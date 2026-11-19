# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import runpy
from contextlib import contextmanager
from datetime import datetime, timezone
from threading import Event, Lock, Semaphore, Thread
from time import monotonic
from traceback import format_exc
from uuid import uuid4

# Zato
from zato.common.api import FileTransfer
from zato.common.audit_log.api import AuditLog
from zato.common.config_db import Env_Audit_Log_Enabled
from zato.common.ext.bunch import Bunch
from zato.common.file_transfer.api import Default_Verify_How
from zato.common.model.file_transfer_ import FileTransferItem
from zato.common.typing_ import cast_
from zato.common.util.file_transfer_scheduler import apply_schedule_defaults
from zato.server.connection.facade import SMBFacade
from zato.server.generic.api.outconn_smb import SMBClient
from zato.server.service import Service
from zato.server.service.internal.outgoing.file_transfer.candidates import get_candidates, get_file_name, \
    keep_stable_entries

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import any_, anydict, anylist, iterator_
    from zato.server.base.parallel import ParallelServer
    from zato.server.base.config_manager import ConfigManager
    from zato.server.connection.smb import SMBConnection

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The audit log is not part of what the peer reproduces
    Audit_Log_Disabled = 'false'

    # The name under which the peer would write to the audit log
    Server_Name = 'smb-windows-peer'

    # How long a schedule or a job may take to end once it is stopped, in seconds
    Join_Timeout = 15

    # The log levels the peer writes, of which only errors fail a test
    Level_Info    = 'INFO'
    Level_Warning = 'WARNING'
    Level_Error   = 'ERROR'

    # A schedule with this value deletes each processed file rather than moving it
    On_Success_Delete = 'delete'

    # The pool size of an SMB connection that enmasse imports without one
    Default_Pool_Size = 1

# ################################################################################################################################
# ################################################################################################################################

class PeerPoolTimeout(Exception):
    """ Raised when no client of a connection becomes free within the time its caller waits for one.
    """

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

# ################################################################################################################################
# ################################################################################################################################

class PeerWrapper:
    """ Stands in for the wrapper of an outgoing SMB connection - one client of Zato that every operation of the connection uses.
    """
    def __init__(self, definition:'anydict', audit_log:'AuditLog') -> 'None':

        self.config = Bunch()
        self.config.id = definition['name']
        self.config.name = definition['name']
        self.config.is_active = True
        self.config.host = definition['host']
        self.config.port = definition['port']
        self.config.username = definition['username']
        self.config.secret = definition['password']

        self.audit_log = audit_log
        self.should_store_content = False
        self.verify_how = Default_Verify_How

        server:'ParallelServer' = cast_('ParallelServer', None)
        self.smb_client = SMBClient(self.config, server)

        # The client connects when the definitions are imported, so that its connection is in place before the tests run
        self.smb_client.connect()

        # The operations of a connection share its pool of clients, as they do in a server
        if 'pool_size' in definition:
            pool_size = definition['pool_size']
        else:
            pool_size = ModuleCtx.Default_Pool_Size

        self.pool = Semaphore(pool_size)

# ################################################################################################################################

    @contextmanager
    def client(self, should_block:'bool'=True, block_timeout:'int'=0) -> 'iterator_':
        """ Checks out the client for the duration of one operation, waiting for it as long as the caller allows.
        """
        if not self.pool.acquire(timeout=block_timeout):
            raise PeerPoolTimeout(f'No client of `{self.config.name}` became free within {block_timeout}s')

        try:
            yield self.smb_client
        finally:
            self.pool.release()

# ################################################################################################################################

    def ping(self) -> 'None':
        self.smb_client.ping()

# ################################################################################################################################

    def close(self) -> 'None':
        self.smb_client.close()

# ################################################################################################################################
# ################################################################################################################################

class _ConfigManager:
    """ The part of the configuration manager of a server that the SMB facade reads.
    """
    def __init__(self) -> 'None':
        self.outconn_smb:'anydict' = {}

# ################################################################################################################################
# ################################################################################################################################

class _ServiceRequest:
    def __init__(self, input:'any_', raw_request:'any_') -> 'None':
        self.input = input
        self.raw_request = raw_request

# ################################################################################################################################

class _ServiceLogger:
    """ The logger of a service, which writes to the log of the peer.
    """
    def __init__(self, peer:'PeerServer') -> 'None':
        self.peer = peer

    def info(self, message:'str', *args:'any_') -> 'None':
        text = message % args
        self.peer.log(ModuleCtx.Level_Info, text)

    def warning(self, message:'str', *args:'any_') -> 'None':
        text = message % args
        self.peer.log(ModuleCtx.Level_Warning, text)

    def error(self, message:'str', *args:'any_') -> 'None':
        text = message % args
        self.peer.log(ModuleCtx.Level_Error, text)

# ################################################################################################################################

class _ServiceContext:
    """ What the handle method of a service reads from its instance - the request, the SMB facade and the logger.
    """
    def __init__(self, cid:'str', request:'_ServiceRequest', smb:'SMBFacade', logger:'_ServiceLogger') -> 'None':
        self.cid = cid
        self.request = request
        self.smb = smb
        self.logger = logger

# ################################################################################################################################
# ################################################################################################################################

class _ScheduleRunner:
    """ Runs one schedule of one connection the way the scheduler of a server does - it lists the directory, keeps
    the candidates that match and stopped changing, claims each one, hands it to its service and moves it out of the way.
    The peer keeps no memory of earlier attempts, so a failed file is quarantined when the schedule allows one attempt
    and released otherwise.
    """
    def __init__(self, peer:'PeerServer', conn_name:'str', schedule:'anydict') -> 'None':
        apply_schedule_defaults(schedule)

        self.peer = peer
        self.conn_name = conn_name
        self.schedule = schedule
        self.name = schedule['name']

        self.stopping = Event()
        self.thread = Thread(target=self._run, daemon=True, name=f'peer-{self.name}-{conn_name}')

# ################################################################################################################################

    def start(self) -> 'None':
        self.thread.start()

    def stop(self) -> 'None':
        self.stopping.set()
        self.thread.join(ModuleCtx.Join_Timeout)

# ################################################################################################################################

    def _run(self) -> 'None':

        interval = self.schedule['run_every']

        while not self.stopping.is_set():

            started = monotonic()

            # A run that fails is logged as an error, the way the server logs a failed job, and the next one follows ..
            try:
                self._run_once()
            except Exception:
                error = format_exc()
                self.peer.log(ModuleCtx.Level_Error, f'Run of schedule `{self.name}` of `{self.conn_name}` failed -> {error}')

            # .. at the interval of the schedule.
            elapsed = monotonic() - started
            wait = max(interval - elapsed, 0)
            _ = self.stopping.wait(wait)

# ################################################################################################################################

    def _run_once(self) -> 'None':

        conn = self.peer.connection(self.conn_name)
        directory = self.schedule['directory'].rstrip('/')

        entries = conn.list(directory)

        if not entries:
            return

        # The candidates are selected by the code of the server ..
        selection = get_candidates(self.schedule, entries)
        candidates = selection.kept

        if not candidates:
            return

        if self.schedule['ready_how'] == _scheduler.ReadyHow.Stability:
            selection = keep_stable_entries(conn, directory, candidates, self.schedule['stability_delay'])
            candidates = selection.kept

        # .. and each one is processed on its own, until the schedule is stopped.
        for entry in candidates:

            if self.stopping.is_set():
                return

            self._process(conn, directory, entry)

# ################################################################################################################################

    def _process(self, conn:'SMBConnection', directory:'str', entry:'any_') -> 'None':

        file_name = get_file_name(entry)
        full_path = f'{directory}/{file_name}'
        current_path = full_path
        service_name = self.schedule['service']

        # A failed rename of a claim means that another consumer claimed the file first ..
        if self.schedule['should_claim']:
            claim_path = full_path + _scheduler.Claim_Suffix
            try:
                conn.move(full_path, claim_path)
            except Exception:
                self.peer.log(ModuleCtx.Level_Info, f'File `{full_path}` already claimed by another consumer, skipping')
                return
            current_path = claim_path

        # .. otherwise the file is read and handed to its service ..
        try:
            spooled = conn.read_to_spool(current_path)

            item = FileTransferItem(FileTransfer.ConnType.SMB, self.conn_name, self.name,
                directory, file_name, full_path, spooled.size, entry.last_modified_iso, spooled.path,
                self.schedule['encoding'])

            try:
                self.peer.invoke(service_name, item, '')
            finally:
                item.close()

        # .. a file the service rejects is quarantined or released ..
        except Exception:
            error = format_exc()
            self.peer.log(ModuleCtx.Level_Warning,
                f'Could not invoke `{service_name}` with file `{full_path}` from `{self.conn_name}` -> {error}')

            if self.schedule['max_attempts'] == 1:
                self._move_away(conn, directory, self.schedule['quarantine_directory'], file_name, current_path)
            elif current_path != full_path:
                conn.move(current_path, full_path)

            return

        # .. and a processed one is deleted or moved out of the way.
        if self.schedule['on_success'] == ModuleCtx.On_Success_Delete:
            conn.delete_file(current_path)
        else:
            self._move_away(conn, directory, self.schedule['move_directory'], file_name, current_path)

# ################################################################################################################################

    def _move_away(self, conn:'SMBConnection', directory:'str', subdirectory:'str', file_name:'str', current_path:'str') -> 'None':
        """ Moves a file into a subdirectory of its directory, under its own name, or with a timestamp if the name is taken.
        """
        if subdirectory.startswith('/'):
            destination_directory = subdirectory
        else:
            destination_directory = f'{directory}/{subdirectory}'

        conn.create_directory(destination_directory, exist_ok=True)

        destination = f'{destination_directory}/{file_name}'

        if conn.exists(destination):
            now = datetime.now(timezone.utc)
            stamp = now.strftime(_scheduler.Collision_Suffix_Format)
            destination = f'{destination}.{stamp}'

        try:
            conn.move(current_path, destination)
        except Exception:
            error = format_exc()
            self.peer.log(ModuleCtx.Level_Warning, f'Could not put file `{current_path}` out of the way -> {error}')

# ################################################################################################################################
# ################################################################################################################################

class _JobRunner:
    """ Runs one interval-based job, which invokes its service with the first element of its extra data.
    """
    def __init__(self, peer:'PeerServer', job:'anydict') -> 'None':
        self.peer = peer
        self.job = job
        self.name = job['name']

        self.stopping = Event()
        self.thread = Thread(target=self._run, daemon=True, name=f'peer-job-{self.name}')

    def start(self) -> 'None':
        self.thread.start()

    def stop(self) -> 'None':
        self.stopping.set()
        self.thread.join(ModuleCtx.Join_Timeout)

    def _run(self) -> 'None':

        interval = self.job['seconds']
        extra = self.job['extra']
        raw_request = extra[0]

        # The first run follows one interval after the start, as with a job that starts now
        while not self.stopping.wait(interval):
            try:
                self.peer.invoke(self.job['service'], None, raw_request)
            except Exception:
                error = format_exc()
                self.peer.log(ModuleCtx.Level_Error, f'Job `{self.name}` with `{raw_request}` failed -> {error}')

# ################################################################################################################################
# ################################################################################################################################

class PeerServer:
    """ Stands in for the file transfer side of a Zato server, in the process of the tests. It reaches the guests through
    the SMB facade and the SMB client of Zato, runs the schedules and the jobs of enmasse definitions with the candidate
    selection of Zato, and hands each file to the handle method of the deployed services. It writes its log in the format
    of the server log, so that a monitor reads it as it reads the log of a server.
    """
    def __init__(self, services_path:'Path', log_path:'str') -> 'None':

        os.environ[Env_Audit_Log_Enabled] = ModuleCtx.Audit_Log_Disabled
        self.audit_log = AuditLog(ModuleCtx.Server_Name)

        self.services = _load_services(services_path)

        self.log_path = log_path
        self.log_lock = Lock()

        # Each set of definitions is kept under its key, e.g. the version of a guest, so that a new import replaces it
        self.definitions:'anydict' = {}
        self.runners:'anydict' = {}
        self.wrappers:'dict[str, PeerWrapper]' = {}

        self.config_manager = _ConfigManager()

        with open(self.log_path, 'a', encoding='utf8'):
            pass

# ################################################################################################################################

    def log(self, level:'str', message:'str') -> 'None':
        now = datetime.now(timezone.utc)
        line = f'{now.isoformat()} - {level} - {message}\n'

        with self.log_lock:
            with open(self.log_path, 'a', encoding='utf8') as log_file:
                _ = log_file.write(line)

# ################################################################################################################################

    def facade(self, cid:'str') -> 'SMBFacade':
        config_manager:'ConfigManager' = cast_('ConfigManager', self.config_manager)

        out = SMBFacade()
        out.init(cid, config_manager)

        return out

# ################################################################################################################################

    def connection(self, name:'str') -> 'SMBConnection':
        """ Returns a connection the way a service obtains it, through self.smb[name].
        """
        cid = uuid4().hex
        facade = self.facade(cid)

        out = facade[name]
        return out

# ################################################################################################################################

    def invoke(self, service_name:'str', input:'any_', raw_request:'any_') -> 'None':
        """ Runs the handle method of a deployed service with the given request.
        """
        cid = uuid4().hex
        request = _ServiceRequest(input, raw_request)
        smb = self.facade(cid)
        logger = _ServiceLogger(self)

        context = _ServiceContext(cid, request, smb, logger)
        service = cast_('Service', context)

        service_class = self.services[service_name]
        service_class.handle(service)

# ################################################################################################################################

    def import_definitions(self, key:'str', definitions:'anydict') -> 'None':
        """ Replaces the connections, schedules and jobs imported under a key with the ones of enmasse definitions.
        """
        self._stop_runners(key)
        self.definitions[key] = definitions
        self._start(key)

# ################################################################################################################################

    def _start(self, key:'str') -> 'None':

        definitions = self.definitions[key]
        runners:'anylist' = []

        # Each connection replaces an earlier one of the same name, as an edit of a connection does ..
        for definition in definitions['smb']:

            name = definition['name']

            if name in self.wrappers:
                self.wrappers[name].close()

            wrapper = PeerWrapper(definition, self.audit_log)
            self.wrappers[name] = wrapper
            self.config_manager.outconn_smb[name] = {'conn': wrapper}

            if 'schedules' in definition:
                for schedule in definition['schedules']:
                    schedule_runner = _ScheduleRunner(self, name, schedule)
                    runners.append(schedule_runner)

        # .. and only the active jobs run.
        for job in definitions['scheduler']:
            if job['is_active']:
                job_runner = _JobRunner(self, job)
                runners.append(job_runner)

        for runner in runners:
            runner.start()

        self.runners[key] = runners

# ################################################################################################################################

    def _stop_runners(self, key:'str') -> 'None':
        if key in self.runners:
            for runner in self.runners[key]:
                runner.stop()
            del self.runners[key]

# ################################################################################################################################

    def restart(self) -> 'None':
        """ Stops everything and starts it again with new connections, as a restart of a server does.
        """
        keys = list(self.definitions)

        for key in keys:
            self._stop_runners(key)

        for wrapper in self.wrappers.values():
            wrapper.close()

        self.wrappers.clear()
        self.config_manager.outconn_smb.clear()

        self.log(ModuleCtx.Level_Info, 'Restarted')

        for key in keys:
            self._start(key)

# ################################################################################################################################

    def stop(self) -> 'None':
        for key in list(self.runners):
            self._stop_runners(key)

        for wrapper in self.wrappers.values():
            wrapper.close()

# ################################################################################################################################
# ################################################################################################################################

def _load_services(path:'Path') -> 'dict[str, type[Service]]':
    """ Returns each service class of a module of services, by its name.
    """
    out:'dict[str, type[Service]]' = {}

    module_globals = runpy.run_path(str(path))

    for value in module_globals.values():

        if not isinstance(value, type):
            continue

        if value is Service:
            continue

        if issubclass(value, Service):
            name = value.__dict__['name']
            out[name] = value

    return out

# ################################################################################################################################
# ################################################################################################################################
