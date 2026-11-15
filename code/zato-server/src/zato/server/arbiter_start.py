# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The start of a server as an arbiter with worker processes. The arbiter resolves the worker count, creates the schemas
# of the shared databases, removes the MCP sessions of the previous start, takes over the pub/sub database on PostgreSQL
# once for every worker, creates the shared region with one queue for each SQLite file of the server, confirms that
# nothing that a fork would duplicate is open, and forks the workers and, on SQLite with several workers,
# the pub/sub writer process.

# stdlib
import os
from tempfile import gettempdir

# Zato
from zato.common.analytics.api import get_analytics_db_path
from zato.common.audit_log.api import new_unshared_audit_engine
from zato.common.audit_log.sqlite_writes import env_config as audit_env_config
from zato.common.common_db.config import get_common_sqlite_path
from zato.common.db_env.common import get_env_sqlite_path, Type_PostgreSQL, Type_SQLite
from zato.common.db_env.connection import SQLite_Busy_Timeout_Ms
from zato.common.db_env.engine import bind_process_queues, create_schema, get_cached_engine_count, get_queue_by_path, \
    set_pool_worker_count
from zato.common.db_env.process_queue import get_deadline_seconds
from zato.common.pubsub.sql.config import get_pubsub_db_path, get_pubsub_db_type, new_unshared_pubsub_engine
from zato.common.pubsub.sql.generation import take_over_before_fork
from zato.common.pubsub.sql.schema import metadata as pubsub_metadata
from zato.common.pubsub.writer_process.handlers import run_writer
from zato.common.worker_count import get_affinity_count, resolve_worker_count, ServerWorkers
from zato.server.arbiter import Arbiter
from zato.server.arbiter_config import ArbiterConfig, ArbiterError
from zato.server.connection.mcp.session import remove_all_sessions
from zato.server.server_region import new_server_region
from zato.server.worker_runtime import WorkerRuntime

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import strintdict, strlist, strnone
    from zato.server.arbiter_config import WorkerContext
    from zato.server.main import ZatoApplication
    from zato_ipc_core.zato_ipc_core import SharedRegion

    Bunch = Bunch
    SharedRegion = SharedRegion
    strintdict = strintdict
    strlist = strlist
    strnone = strnone
    WorkerContext = WorkerContext
    ZatoApplication = ZatoApplication

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The directory of the threads of the calling process, one entry each
    Task_Dir = '/proc/self/task'

    # The file of each thread that holds its name
    Task_Name_File = 'comm'

    # The files of zato_server_core that every worker appends to
    REST_Log_Name   = 'rest.log'
    Access_Log_Name = 'access.log'

# ################################################################################################################################
# ################################################################################################################################

def get_worker_count(server_config:'Bunch') -> 'int':
    """ Returns the number of workers that server.conf and the environment configure.
    """
    # A server.conf written before the key existed has no such key ..
    if ServerWorkers.Config_Key in server_config.main:
        config_value:'strnone' = server_config.main[ServerWorkers.Config_Key]
    else:
        config_value = None

    # .. and the environment variable overrides whatever server.conf configures.
    env_value = os.environ.get(ServerWorkers.Env_Key)
    affinity_count = get_affinity_count()

    out = resolve_worker_count(config_value, env_value, affinity_count, ServerWorkers.CPU_Max_Path)
    return out

# ################################################################################################################################

def get_sqlite_paths() -> 'strlist':
    """ Returns the paths of the SQLite files to which every worker of the server writes.
    """
    out:'strlist' = []

    if get_pubsub_db_type() == Type_SQLite:
        pubsub_path = get_pubsub_db_path()
        out.append(pubsub_path)

    if audit_path := get_env_sqlite_path(audit_env_config):
        out.append(audit_path)

    if common_path := get_common_sqlite_path():
        out.append(common_path)

    analytics_path = get_analytics_db_path()
    out.append(analytics_path)

    return out

# ################################################################################################################################

def prepare_databases() -> 'None':
    """ Creates the schemas of the pub/sub and audit databases, removes the MCP sessions of the previous start
    and, on PostgreSQL, makes the server the active one, all through engines that are disposed before the fork,
    so that no worker runs DDL concurrently with another and no worker raises the generation itself.
    """
    pubsub_engine = new_unshared_pubsub_engine()
    create_schema(pubsub_engine, pubsub_metadata)
    remove_all_sessions(pubsub_engine)
    pubsub_engine.dispose()

    audit_engine = new_unshared_audit_engine()
    create_schema(audit_engine, audit_env_config.metadata)
    audit_engine.dispose()

    if get_pubsub_db_type() == Type_PostgreSQL:
        _ = take_over_before_fork(new_unshared_pubsub_engine)

# ################################################################################################################################

def _get_thread_names() -> 'strlist':
    out:'strlist' = []

    for task_id in sorted(os.listdir(ModuleCtx.Task_Dir)):
        name_path = os.path.join(ModuleCtx.Task_Dir, task_id, ModuleCtx.Task_Name_File)

        with open(name_path) as name_file:
            name = name_file.read()

        name = name.strip()
        out.append(name)

    return out

# ################################################################################################################################

def check_fork_ready() -> 'None':
    """ Raises ArbiterError if the arbiter runs a thread other than its main one, which a fork does not copy,
    or holds a database engine, whose pooled connections every worker would use at once.
    """
    thread_names = _get_thread_names()

    if len(thread_names) > 1:
        raise ArbiterError(f'The arbiter runs other threads before the fork -> {thread_names}')

    if engine_count := get_cached_engine_count():
        raise ArbiterError(f'The arbiter holds {engine_count} database engines before the fork')

# ################################################################################################################################
# ################################################################################################################################

class ServerProcesses:
    """ The main functions of the worker processes and of the pub/sub writer process of one server.
    """

    def __init__(self, zato_app:'ZatoApplication', region:'SharedRegion', queue_by_path:'strintdict') -> 'None':
        self.zato_app = zato_app
        self.region = region
        self.queue_by_path = queue_by_path

    def worker_main(self, ctx:'WorkerContext') -> 'None':
        worker = WorkerRuntime(self.region, ctx, self.queue_by_path)
        self.zato_app.run_worker(worker)

    def writer_main(self, listen_fd:'int') -> 'None':
        """ Serves the workers, taking the turns of the writer process in the queues of the pub/sub and audit files.
        """
        deadline_seconds = get_deadline_seconds(SQLite_Busy_Timeout_Ms, self.region.slot_count)

        bind_process_queues(self.region, self.region.writer_place, deadline_seconds, self.queue_by_path)
        run_writer(listen_fd)

# ################################################################################################################################
# ################################################################################################################################

def run_arbiter(zato_app:'ZatoApplication') -> 'int':
    """ Runs the server as an arbiter that forks its workers, and returns the exit code of the arbiter.
    """
    server = zato_app.zato_server

    # The pools of the network databases are divided among the workers ..
    worker_count = get_worker_count(server.fs_server_config)
    set_pool_worker_count(worker_count)

    # .. the shared databases are ready before any worker starts ..
    prepare_databases()

    # .. each SQLite file receives one queue of the region ..
    sqlite_paths = get_sqlite_paths()
    queue_by_path = get_queue_by_path(sqlite_paths)
    queue_count = len(queue_by_path)

    region = new_server_region(worker_count, queue_count)
    processes = ServerProcesses(zato_app, region, queue_by_path)

    # .. the arbiter rotates the files of zato_server_core that every worker appends to ..
    config = ArbiterConfig.from_defaults(gettempdir())
    config.native_log_files = [
        os.path.join(server.logs_dir, ModuleCtx.REST_Log_Name),
        os.path.join(server.logs_dir, ModuleCtx.Access_Log_Name),
    ]

    # .. on SQLite with several workers, one writer process writes the publications of all of them ..
    if worker_count > 1 and get_pubsub_db_type() == Type_SQLite:
        writer_main = processes.writer_main
    else:
        writer_main = None

    # .. and nothing that a fork would duplicate is open when the workers are forked.
    check_fork_ready()

    arbiter = Arbiter(region, processes.worker_main, config, writer_main)

    out = arbiter.run()
    return out

# ################################################################################################################################
# ################################################################################################################################
