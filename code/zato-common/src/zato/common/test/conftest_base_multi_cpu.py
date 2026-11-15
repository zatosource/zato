# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The shared fixture of the live suites of a server with several workers. The server is started through
# create_zato_server_fixture with the worker count in Zato_Server_Workers, and WorkerControl reads the slots
# of the server through zato.server.worker.get-list and sends signals to the worker of a chosen slot.

# stdlib
import atexit
import json
import logging
import os
import shutil
import signal
import sqlite3
import subprocess
import sys
import tempfile
from base64 import b64encode
from http.client import HTTPConnection
from threading import Thread
from time import monotonic, sleep
from uuid import uuid4

# PyYAML
import yaml

# Zato
from zato.common.file_transfer import listener as file_listener
from zato.common.test.client import AdminClient
from zato.common.hl7.mllp.haproxy import Env_Port_Name as MLLP_Port_Env
from zato.common.test.conftest_base_pubsub import create_zato_server_fixture, find_free_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, callable_, intlist, strlist

    any_ = any_
    anydict = anydict
    anylist = anylist
    callable_ = callable_
    intlist = intlist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.common.test.conftest_base_multi_cpu')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The environment variable through which the server receives its worker count
    Worker_Count_Env = 'Zato_Server_Workers'

    # The worker count of a suite whose environment does not set one
    Default_Worker_Count = 4

    # The prefix of every directory that a suite creates in the temporary directory,
    # and the label of every container and network that a suite creates
    Directory_Prefix = 'zato_multi_cpu_'
    Docker_Label = 'zato-test-multi-cpu'

    # The directory whose entries are the PIDs of the processes of the host
    Proc_Directory = '/proc'

    # The name of the config process of a server, as the kernel reports it
    Config_Process_Name = 'zato-config'

    # The pickup directories of a server that a file listener watches, the files it deploys from them, the directory
    # of the server whose TLS material a listener of its own reports, the file the output of a listener goes to,
    # and the line it writes once it watches its directory
    Listener_Directories = (
        os.path.join('pickup', 'incoming', 'services'),
        os.path.join('pickup', 'incoming', 'user-conf'),
    )
    Listener_Patterns = ['*.py', '*.zip', '*.yaml', '*.yml', '*.ini', '*.zrules']
    TLS_Material_Directory = 'tls-material'
    Listener_Log_Name = 'file-listener-{}.log'
    Listener_Ready_Marker = 'Watching for changes, press Ctrl+C to stop'

    # How long a file listener may take to watch its directory, in seconds
    Listener_Ready_Deadline = 30.0

    # The name of a file in a pickup directory that matches no pattern of its file listener
    Staging_Name = 'staging-{}.part'

    # The repository of the web-admin of a quickstart environment, which holds the credentials that a file listener uses
    Web_Admin_Repo = os.path.join('web-admin', 'config', 'repo')

    # The service that returns the slots of the server
    Worker_List_Service = 'zato.server.worker.get-list'

    # The service that returns the slot of the worker that served the request, and the file it is deployed from,
    # which a suite lists in the hot_deploy_sources of its configuration
    Worker_Slot_Service = 'test.multi-cpu.worker-slot'
    Worker_Slot_Service_Path = os.path.join(os.path.dirname(__file__), 'multi_cpu_service.py')
    Worker_Slot_Path = '/test/multi-cpu/worker-slot'

    # The state of a slot whose worker serves requests
    State_Ready = 'ready'

    # How long a respawn or a return of every slot to the ready state may take, in seconds
    Respawn_Deadline = 60.0

    # How often the slots are read while waiting, in seconds
    Poll_Interval = 0.25

    # How long a test request waits for its response, which exceeds the duration of test.multi-cpu.worker-sleep, in seconds
    Request_Timeout = 30.0

    Status_OK = 200

    # The variable whose password quickstart assigns to the user of the metrics channel, and that user
    Metrics_Password_Env = 'Zato_Metrics_Password'
    Metrics_Username = 'metrics'

    # The user and the path of the admin channel through which a test invokes a service in a chosen worker
    Admin_Username = 'admin.invoke'
    Admin_Invoke_Path = '/zato/api/invoke/{}'

    # How long an admin request of the helpers waits for its response, which exceeds the timeout of a fan-out query
    # to a stopped worker, in seconds
    Admin_Timeout = 15.0

    # The position of the parent PID among the fields of /proc/<pid>/stat that follow the process name
    Stat_Parent_Field = 1

    # The relative location of the server log and the markers that the server writes to it for each enmasse import it starts
    Log_Path = os.path.join('logs', 'server.log')
    Marker_Started = 'Invoking command'
    Marker_Import  = '--import'

    # The variables that set the size limit and the backup count of the server log in the logging configuration
    # that quickstart writes, and the values that the logging suite uses
    Log_Max_Size_Env     = 'Zato_Server_Log_Max_Size'
    Log_Backup_Count_Env = 'Zato_Server_Log_Backup_Count'
    Log_Max_Size         = 1_000_000
    Log_Backup_Count     = 50

# ################################################################################################################################
# ################################################################################################################################

def get_worker_count() -> 'int':
    """ Returns the worker count of the suite, which the environment of the test run may set.
    """
    if ModuleCtx.Worker_Count_Env in os.environ:
        out = int(os.environ[ModuleCtx.Worker_Count_Env])
    else:
        out = ModuleCtx.Default_Worker_Count

    return out

# ################################################################################################################################
# ################################################################################################################################

class MultiCPUTestConfig:
    """ The address of the server and the credentials that the tests of a suite with several workers use,
    set by the populate callback of the suite once the server is ready.
    """
    host = ''
    port = 0
    server_directory = ''
    zato_bin = ''
    base_url = ''
    invoke_password = ''
    worker_count = 0

    # The port that the MLLP listener of every worker binds to, chosen before the server starts
    mllp_port = find_free_port()

    # The password of the security definitions that a suite creates through its enmasse template
    sec_password = uuid4().hex

    @classmethod
    def populate(
        cls,
        host:'str',
        server_port:'int',
        invoke_password:'str',
        server_directory:'str',
        zato_bin:'str',
    ) -> 'None':
        cls.host = host
        cls.port = server_port
        cls.server_directory = server_directory
        cls.zato_bin = zato_bin
        cls.base_url = f'http://{host}:{server_port}'
        cls.invoke_password = invoke_password
        cls.worker_count = get_worker_count()

        start_file_listeners(server_directory, server_port)

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_listener(process:'subprocess.Popen[bytes]', log_path:'str') -> 'None':
    """ Waits until a file listener reports that it watches its directory.
    """
    deadline = monotonic() + ModuleCtx.Listener_Ready_Deadline

    while monotonic() < deadline:

        if process.poll() is not None:
            with open(log_path) as log_file:
                output = log_file.read()
            raise Exception(f'The file listener exited with {process.returncode} -> {output}')

        with open(log_path) as log_file:
            if ModuleCtx.Listener_Ready_Marker in log_file.read():
                return

        sleep(ModuleCtx.Poll_Interval)

    raise Exception(f'The file listener did not watch its directory within {ModuleCtx.Listener_Ready_Deadline}s, see {log_path}')

# ################################################################################################################################

def start_file_listeners(server_directory:'str', server_port:'int') -> 'None':
    """ Starts a file listener for each pickup directory of the server and one for its TLS material, as a deployment
    of the server does, so that a file placed in one of them reaches the server through a listener.
    The listeners are stopped when the test run exits.
    """
    quickstart_directory = os.path.dirname(server_directory)

    environment = dict(os.environ)
    environment['Zato_Web_Admin_Repo_Dir'] = os.path.join(quickstart_directory, ModuleCtx.Web_Admin_Repo)
    environment['Zato_Config_Bind_Port'] = str(server_port)

    tls_material_directory = os.path.join(server_directory, ModuleCtx.TLS_Material_Directory)
    os.makedirs(tls_material_directory)

    commands:'anylist' = []

    for directory in ModuleCtx.Listener_Directories:
        commands.append([os.path.join(server_directory, directory), '--patterns', *ModuleCtx.Listener_Patterns])

    commands.append([tls_material_directory, '--tls-material'])

    for index, arguments in enumerate(commands):

        log_path = os.path.join(quickstart_directory, ModuleCtx.Listener_Log_Name.format(index))
        command = [sys.executable, file_listener.__file__, *arguments, '--observer', 'inotify']

        with open(log_path, 'w') as log_file:
            process = subprocess.Popen(command, env=environment, stdout=log_file, stderr=subprocess.STDOUT)

        _ = atexit.register(_stop_file_listener, process)

        _wait_for_listener(process, log_path)
        logger.info('File listener %s watches %s', process.pid, arguments[0])

# ################################################################################################################################

def _stop_file_listener(process:'subprocess.Popen[bytes]') -> 'None':
    process.terminate()
    _ = process.wait()

# ################################################################################################################################

def get_staging_path(directory:'str') -> 'str':
    """ Returns a path in a pickup directory from which a complete file is renamed into place, so that its file listener
    never reads a partially written one.
    """
    out = os.path.join(MultiCPUTestConfig.server_directory, directory, ModuleCtx.Staging_Name.format(uuid4().hex))
    return out

# ################################################################################################################################
# ################################################################################################################################

def new_connection() -> 'HTTPConnection':
    """ Opens a connection of its own to the server, which the kernel assigns to one of the workers.
    """
    out = HTTPConnection(MultiCPUTestConfig.host, MultiCPUTestConfig.port, timeout=ModuleCtx.Request_Timeout)
    return out

# ################################################################################################################################

def get_parent_pid(pid:'int') -> 'int':
    """ Returns the PID of the parent of a process, which for a worker is the PID of the arbiter.
    """
    with open(f'/proc/{pid}/stat') as stat_file:
        stat = stat_file.read()

    # .. the name of the process is in parentheses and may contain spaces, so the fields are counted after it ..
    fields = stat[stat.rindex(')') + 2:].split()

    out = int(fields[ModuleCtx.Stat_Parent_Field])
    return out

# ################################################################################################################################

def get_child_pids(parent_pid:'int') -> 'intlist':
    """ Returns the PIDs of every process whose parent is the given one.
    """
    out:'intlist' = []

    for name in os.listdir('/proc'):
        if name.isdigit():
            try:
                parent = get_parent_pid(int(name))
            except FileNotFoundError:
                continue
            if parent == parent_pid:
                out.append(int(name))

    return out

# ################################################################################################################################

def get_json(connection:'HTTPConnection', path:'str') -> 'anydict':
    """ Sends one request over an open connection and returns its JSON response, which must have a status of 200.
    """
    connection.request('GET', path)
    response = connection.getresponse()
    body = response.read()

    if response.status != ModuleCtx.Status_OK:
        raise Exception(f'Status {response.status} from {path} -> {body!r}')

    out = json.loads(body)
    return out

# ################################################################################################################################

def connection_to_slot(slot:'int', other_than:'bool'=False) -> 'HTTPConnection':
    """ Returns a keep-alive connection that the worker of the given slot accepted, or the worker of any other slot,
    using the channel of test.multi-cpu.worker-slot, which every suite defines under the same path.
    """
    while True:
        connection = new_connection()
        response = get_json(connection, ModuleCtx.Worker_Slot_Path)

        if (response['slot'] == slot) != other_than:
            return connection

        connection.close()

# ################################################################################################################################

def basic_auth_header(username:'str', password:'str') -> 'str':
    credentials = f'{username}:{password}'
    out = 'Basic ' + b64encode(credentials.encode()).decode()
    return out

# ################################################################################################################################

def request_on_slot(slot:'int', method:'str', path:'str', body:'str', headers:'anydict') -> 'tuple[int, bytes]':
    """ Sends one request through a connection that the worker of a slot accepted and returns the status and body of the response.
    """
    connection = connection_to_slot(slot)
    connection.request(method, path, body=body, headers=headers)

    response = connection.getresponse()
    response_body = response.read()
    connection.close()

    out = (response.status, response_body)
    return out

# ################################################################################################################################

def invoke_on_slot(slot:'int', service_name:'str', payload:'anydict') -> 'tuple[int, bytes]':
    """ Invokes a service through the admin channel of the worker of a slot and returns the status and body of the response.
    """
    headers = {
        'Authorization': basic_auth_header(ModuleCtx.Admin_Username, MultiCPUTestConfig.invoke_password),
        'Content-Type': 'application/json',
    }

    path = ModuleCtx.Admin_Invoke_Path.format(service_name)

    out = request_on_slot(slot, 'POST', path, json.dumps(payload), headers)
    return out

# ################################################################################################################################

def count_enmasse_imports(file_name:'str') -> 'int':
    """ How many enmasse imports of the file the server log reports.
    """
    path = os.path.join(MultiCPUTestConfig.server_directory, ModuleCtx.Log_Path)

    with open(path) as log_file:
        lines = log_file.read().splitlines()

    out = 0

    for line in lines:
        if ModuleCtx.Marker_Started in line and ModuleCtx.Marker_Import in line and file_name in line:
            out += 1

    return out

# ################################################################################################################################

def enmasse_import(config:'anydict') -> 'None':
    """ Imports the configuration into the server through zato enmasse --import.
    """
    input_path = os.path.join(MultiCPUTestConfig.server_directory, f'multi-cpu-import-{uuid4().hex}.yaml')

    with open(input_path, 'w') as input_file:
        _ = input_file.write(yaml.safe_dump(config, sort_keys=False))

    command = [MultiCPUTestConfig.zato_bin, 'enmasse', MultiCPUTestConfig.server_directory, '--import', '--input', input_path]
    result = subprocess.run(command, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        raise Exception(f'Enmasse import failed -> {result.stdout} {result.stderr}')

# ################################################################################################################################

def wait_for_every_slot(is_done:'callable_', description:'str', deadline:'float') -> 'None':
    """ Waits until the condition holds for every slot of the server, where is_done receives a slot and returns
    whether the worker of that slot satisfies the condition. Raises an exception after the deadline, in seconds.
    """
    pending:'intlist' = list(range(MultiCPUTestConfig.worker_count))
    deadline_at = monotonic() + deadline

    while pending:
        still_pending:'intlist' = []

        for slot in pending:
            if not is_done(slot):
                still_pending.append(slot)

        pending = still_pending

        if pending:
            if monotonic() > deadline_at:
                raise Exception(f'{description} not reached by slots {pending} after {deadline}s')
            sleep(ModuleCtx.Poll_Interval)

    logger.info('%s reached by every slot', description)

# ################################################################################################################################

def post_json(connection:'HTTPConnection', path:'str', payload:'anydict') -> 'anydict':
    """ Sends one JSON request over an open connection and returns its JSON response, which must have a status of 200.
    """
    connection.request('POST', path, body=json.dumps(payload), headers={'Content-Type': 'application/json'})
    response = connection.getresponse()
    body = response.read()

    if response.status != ModuleCtx.Status_OK:
        raise Exception(f'Status {response.status} from {path} -> {body!r}')

    out = json.loads(body)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _remove_docker_objects(list_command:'strlist', remove_command:'strlist') -> 'None':
    """ Removes the Docker objects that the list command returns the IDs of.
    """
    result = subprocess.run(list_command, capture_output=True, text=True, check=True)
    object_ids = result.stdout.split()

    if object_ids:
        _ = subprocess.run(remove_command + object_ids, capture_output=True, check=True)
        logger.info('Removed Docker objects of an interrupted run: %s', object_ids)

# ################################################################################################################################

def _kill_processes_naming(directories:'strlist') -> 'None':
    """ Terminates every process other than the current one whose command line names one of the directories.
    """
    own_pid = os.getpid()

    for name in os.listdir(ModuleCtx.Proc_Directory):

        if not name.isdigit():
            continue

        pid = int(name)

        if pid == own_pid:
            continue

        # A process may exit between the listing and the read of its command line
        try:
            with open(os.path.join(ModuleCtx.Proc_Directory, name, 'cmdline'), 'rb') as cmdline_file:
                cmdline = cmdline_file.read().decode('utf8', 'replace')
        except FileNotFoundError:
            continue

        for directory in directories:
            if directory in cmdline:

                # .. and between the read and the signal.
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                else:
                    logger.info('Terminated process %s of an interrupted run, which names %s', pid, directory)

                break

# ################################################################################################################################

def remove_interrupted_run_state() -> 'None':
    """ Removes what a run interrupted before its teardown left behind - the containers and networks
    of the label of the suites, the processes whose command lines name a directory of the suites, and those directories.
    A suite calls it before it creates anything.
    """
    label_filter = f'label={ModuleCtx.Docker_Label}'

    _remove_docker_objects(['docker', 'container', 'ls', '--all', '--quiet', '--filter', label_filter],
        ['docker', 'container', 'rm', '--force'])

    _remove_docker_objects(['docker', 'network', 'ls', '--quiet', '--filter', label_filter],
        ['docker', 'network', 'rm'])

    temp_directory = tempfile.gettempdir()
    directories:'strlist' = []

    for name in os.listdir(temp_directory):
        if name.startswith(ModuleCtx.Directory_Prefix):
            directories.append(os.path.join(temp_directory, name))

    _kill_processes_naming(directories)

    for directory in directories:
        shutil.rmtree(directory)
        logger.info('Removed directory of an interrupted run: %s', directory)

# ################################################################################################################################

def create_multi_cpu_server_fixture(
    logger_name:'str',
    server_log_copy_name:'str',
    template_path:'str',
    quickstart_prefix:'str',
    worker_count:'int',
    build_config_callback:'callable_',
) -> 'any_':
    """ Returns a session-scoped fixture that starts a server with the given number of workers.
    """
    extra_server_env = {
        ModuleCtx.Worker_Count_Env: str(worker_count),
        MLLP_Port_Env: str(MultiCPUTestConfig.mllp_port),
    }

    out = create_zato_server_fixture(
        logger_name=logger_name,
        server_log_copy_name=server_log_copy_name,
        template_path=template_path,
        quickstart_prefix=quickstart_prefix,
        extra_server_env=extra_server_env,
        patch_server_conf_bind=False,
        build_config_callback=build_config_callback,
    )
    return out

# ################################################################################################################################
# ################################################################################################################################

class WorkerControl:
    """ Reads the slots of a server and sends signals to the worker of a chosen slot.
    """

    def __init__(self, base_url:'str', invoke_password:'str') -> 'None':
        self.client = AdminClient(base_url, invoke_password, ModuleCtx.Admin_Timeout)

# ################################################################################################################################

    def _get_slots_while_waiting(self) -> 'anylist | None':
        """ Returns the slots, or None if the request reached a worker that is stopped or was just terminated,
        which the kernel may still assign connections to.
        """
        try:
            out = self.get_slots()
        except OSError as e:
            logger.info('Slots not read while waiting -> %s', e)
            out = None

        return out

# ################################################################################################################################

    def get_slots(self) -> 'anylist':
        """ Returns one row for each slot, with its PID, generation, state, heartbeat age, owned subscription keys
        and singleton flag.
        """
        response = self.client.invoke(ModuleCtx.Worker_List_Service)
        out = response['items']
        return out

# ################################################################################################################################

    def get_slot(self, slot:'int') -> 'anydict':
        """ Returns the row of one slot.
        """
        for row in self.get_slots():
            if row['slot'] == slot:
                return row

        raise Exception(f'Slot {slot} not found in {ModuleCtx.Worker_List_Service}')

# ################################################################################################################################

    def get_serving_slot(self) -> 'int':
        """ Returns the slot of the worker that served one request, sent over a connection of its own.
        """
        response = self.client.invoke(ModuleCtx.Worker_Slot_Service)
        out = response['slot']
        return out

# ################################################################################################################################

    def send_signal(self, slot:'int', signal_number:'int') -> 'anydict':
        """ Sends a signal to the worker of a slot and returns the row of the slot read before the signal.
        """
        row = self.get_slot(slot)
        os.kill(row['pid'], signal_number)
        return row

# ################################################################################################################################

    def kill(self, slot:'int') -> 'anydict':
        out = self.send_signal(slot, signal.SIGKILL)
        return out

# ################################################################################################################################

    def stop(self, slot:'int') -> 'anydict':
        out = self.send_signal(slot, signal.SIGSTOP)
        return out

# ################################################################################################################################

    def resume(self, slot:'int') -> 'anydict':
        out = self.send_signal(slot, signal.SIGCONT)
        return out

# ################################################################################################################################

    def wait_for_respawn(self, slot:'int', previous_generation:'int') -> 'anydict':
        """ Waits until the slot runs a worker of a generation above the given one and that worker is ready.
        """
        deadline = monotonic() + ModuleCtx.Respawn_Deadline

        while monotonic() < deadline:
            rows = self._get_slots_while_waiting()

            if rows is not None:
                for row in rows:
                    if row['slot'] == slot:
                        if row['generation'] > previous_generation and row['state'] == ModuleCtx.State_Ready:
                            return row

            sleep(ModuleCtx.Poll_Interval)

        raise Exception(f'Slot {slot} was not respawned within {ModuleCtx.Respawn_Deadline}s')

# ################################################################################################################################

    def get_config_process_pid(self) -> 'int':
        """ Returns the PID of the config process, which is the child of the arbiter of that name.
        """
        worker_pid = self.get_slots()[0]['pid']
        arbiter_pid = get_parent_pid(worker_pid)

        for pid in get_child_pids(arbiter_pid):
            with open(f'{ModuleCtx.Proc_Directory}/{pid}/comm') as comm_file:
                name = comm_file.read().strip()

            if name == ModuleCtx.Config_Process_Name:
                return pid

        raise Exception(f'No config process among the children of the arbiter {arbiter_pid}')

# ################################################################################################################################

    def wait_for_config_process(self, previous_pid:'int') -> 'int':
        """ Waits until the arbiter runs a config process other than the given one and returns its PID.
        """
        deadline = monotonic() + ModuleCtx.Respawn_Deadline

        while monotonic() < deadline:
            try:
                pid = self.get_config_process_pid()
            except Exception as e:
                logger.info('Config process not found while waiting -> %s', e)
            else:
                if pid != previous_pid:
                    return pid

            sleep(ModuleCtx.Poll_Interval)

        raise Exception(f'The config process was not respawned within {ModuleCtx.Respawn_Deadline}s')

# ################################################################################################################################

    def wait_for_all_ready(self) -> 'anylist':
        """ Waits until the worker of every slot is ready and returns the slots.
        """
        deadline = monotonic() + ModuleCtx.Respawn_Deadline

        while monotonic() < deadline:
            rows = self._get_slots_while_waiting()

            if rows is not None:
                not_ready:'intlist' = []

                for row in rows:
                    if row['state'] != ModuleCtx.State_Ready:
                        not_ready.append(row['slot'])

                if not not_ready:
                    return rows

            sleep(ModuleCtx.Poll_Interval)

        raise Exception(f'Not every slot was ready within {ModuleCtx.Respawn_Deadline}s')

# ################################################################################################################################
# ################################################################################################################################

class SQLiteWriteLock:
    """ Holds the write lock of an SQLite file from the test process for a given duration.
    """

    def __init__(self, db_path:'str', duration:'float') -> 'None':
        self.db_path = db_path
        self.duration = duration
        self.thread = Thread(target=self._hold, daemon=True)

# ################################################################################################################################

    def _hold(self) -> 'None':

        # The connection begins its transaction explicitly, so that BEGIN IMMEDIATE takes the write lock at once
        connection = sqlite3.connect(self.db_path, isolation_level=None)

        try:
            _ = connection.execute('BEGIN IMMEDIATE')
            sleep(self.duration)
            _ = connection.execute('ROLLBACK')
        finally:
            connection.close()

# ################################################################################################################################

    def start(self) -> 'None':
        self.thread.start()

# ################################################################################################################################

    def wait(self) -> 'None':
        self.thread.join()

# ################################################################################################################################
# ################################################################################################################################
