# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The start of a server as an arbiter with the config process and the worker. The arbiter reads the name of the server
# from the configuration database, creates the schemas of the Zato database, removes the MCP sessions of the previous start,
# takes over the Zato database on PostgreSQL, creates the shared region with the queue of the SQLite file
# of the Zato database, imports the modules of the internal services, which both forked processes inherit,
# confirms that nothing that a fork would duplicate is open, and forks the config process and the worker.

# stdlib
import os
from importlib import import_module
from tempfile import gettempdir
from time import monotonic

# gevent
from gevent import get_hub, sleep

# SQLAlchemy
from sqlalchemy.util.langhelpers import save_generated_code

# Zato
from zato.common.db_env.common import Type_PostgreSQL
from zato.common.db_env.database import database_config, get_database_sqlite_path, get_database_type, \
    new_unshared_database_engine
from zato.common.db_env.engine import create_schemas, get_cached_engine_count, get_queue_by_path
from zato.common.db_env.outage import call_until_available
from zato.common.db_env.sqlite_identity import record_identity
from zato.common.odb.model import Server
from zato.common.pubsub.sql.generation import take_over_before_fork
from zato.common.util.api import find_internal_modules, get_odb_session_from_server_config
from zato.common.version import get_version
from zato.server.arbiter import Arbiter
from zato.server.arbiter_config import ArbiterConfig, ArbiterError
from zato.server.server_region import new_server_region
from zato.server.config_runtime import ConfigRuntime
from zato.server.service import internal
from zato.server.worker_runtime import WorkerRuntime

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import strintdict, strlist
    from zato.server.arbiter_config import WorkerContext
    from zato.server.main import ZatoApplication
    from zato_ipc_core.zato_ipc_core import SharedRegion

    strintdict = strintdict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The directory of the threads of the calling process, one entry each
    Task_Dir = '/proc/self/task'

    # The file of each thread that holds its name
    Task_Name_File = 'comm'

    # How long the arbiter waits for the threads of the gevent thread pool to exit, and how often it checks, in seconds
    Thread_Stop_Timeout  = 5.0
    Thread_Stop_Interval = 0.01

# ################################################################################################################################
# ################################################################################################################################

def get_sqlite_paths() -> 'strlist':
    """ Returns the paths of the SQLite files to which both the worker and the config process write,
    which is the file of the Zato database, or none on PostgreSQL.
    """
    out:'strlist' = []

    if db_path := get_database_sqlite_path():
        out.append(db_path)

    return out

# ################################################################################################################################

def get_server_name(server_config:'Bunch') -> 'str':
    """ Returns the name of the server, which the configuration database holds under the token of the server
    and which the server itself loads only after the fork, through a session whose engine is disposed before the fork.
    """
    token = server_config.main.token.decode('utf8')

    session = get_odb_session_from_server_config(server_config)
    engine = session.get_bind()

    try:
        query = session.query(Server.name)
        query = query.filter(Server.token == token)
        row = query.one()
        out = row.name
    finally:
        session.close()
        engine.dispose()

    return out

# ################################################################################################################################

def _create_database_schemas() -> 'None':
    """ Creates the schemas of the Zato database through an engine of its own, which is disposed whether or not they were created,
    and records the identity of its SQLite file, which the config process and the worker inherit.
    """
    engine = new_unshared_database_engine()

    try:
        create_schemas(engine, database_config.metadata_tuple)

        if db_path := get_database_sqlite_path():
            record_identity(db_path)

    finally:
        engine.dispose()

# ################################################################################################################################

def prepare_databases(server_name:'str') -> 'None':
    """ Creates the schemas of the Zato database and, on PostgreSQL, makes the server the active one,
    each waiting for the database to become available if it is not, all through engines that are disposed before the fork,
    so that neither the worker nor the config process runs DDL concurrently with the other or raises the generation itself.
    """
    _ = call_until_available('Zato database schemas', _create_database_schemas)

    if get_database_type() == Type_PostgreSQL:
        _ = take_over_before_fork(new_unshared_database_engine, server_name)

# ################################################################################################################################

def import_internal_service_modules() -> 'None':
    """ Imports each module of the internal services, so that the config process and the worker find them imported
    and each only registers their classes when it deploys them.
    """
    module_names = find_internal_modules(internal)

    for module_name in module_names:
        _ = import_module(module_name)

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

def stop_threadpool() -> 'None':
    """ Stops the threads of the gevent thread pool, in which the patched resolver looked up host names
    during the imports of the arbiter, and waits until they exit, because a fork copies none of them.
    The hub of each forked process creates a pool of its own when it needs one.
    """
    hub = get_hub()

    # The pool ends its threads ..
    hub.threadpool.kill()
    del hub.threadpool

    # .. which leave the process shortly after their greenlets did.
    deadline = monotonic() + ModuleCtx.Thread_Stop_Timeout

    # Only the count is read here, because a thread that exits between the listing of the tasks and the reading
    # of their names leaves no name to read.
    while len(os.listdir(ModuleCtx.Task_Dir)) > 1:
        if monotonic() >= deadline:
            break
        sleep(ModuleCtx.Thread_Stop_Interval)

# ################################################################################################################################

def check_fork_ready() -> 'None':
    """ Raises ArbiterError if the arbiter runs a thread other than its main one, which a fork does not copy,
    or holds a database engine, whose pooled connections the forked processes would use at once.
    """
    thread_names = _get_thread_names()

    if len(thread_names) > 1:
        raise ArbiterError(f'The arbiter runs other threads before the fork -> {thread_names}')

    if engine_count := get_cached_engine_count():
        raise ArbiterError(f'The arbiter holds {engine_count} database engines before the fork')

# ################################################################################################################################
# ################################################################################################################################

class ServerProcesses:
    """ The main functions of the worker and of the config process of one server.
    """

    def __init__(self, zato_app:'ZatoApplication', region:'SharedRegion', queue_by_path:'strintdict') -> 'None':
        self.zato_app = zato_app
        self.region = region
        self.queue_by_path = queue_by_path

    def worker_main(self, ctx:'WorkerContext') -> 'None':
        worker = WorkerRuntime(self.region, ctx, self.queue_by_path)
        self.zato_app.run_worker(worker)

    def config_main(self, ctx:'WorkerContext') -> 'None':
        runtime = ConfigRuntime(self.region, ctx, self.queue_by_path)
        self.zato_app.run_config_process(runtime)

# ################################################################################################################################
# ################################################################################################################################

def run_arbiter(zato_app:'ZatoApplication') -> 'int':
    """ Runs the server as an arbiter that forks the config process and the worker, and returns the exit code of the arbiter.
    """
    server = zato_app.zato_server

    # The shared databases are ready before any process starts, and the takeover is recorded with the name of the server ..
    server_name = get_server_name(server.fs_server_config)
    prepare_databases(server_name)

    # .. each SQLite file receives one queue of the region ..
    sqlite_paths = get_sqlite_paths()
    queue_by_path = get_queue_by_path(sqlite_paths)
    queue_count = len(queue_by_path)

    region = new_server_region(queue_count)
    processes = ServerProcesses(zato_app, region, queue_by_path)

    # .. the arbiter rotates the files of zato_server_core that the worker appends to ..
    config = ArbiterConfig.from_defaults(gettempdir())
    config.native_log_files = server.native_log_files

    # .. the version is read once, and the processes forked below inherit it rather than run git on each start ..
    _ = get_version()

    # .. the modules of the internal services are imported once, and both processes inherit them ..
    import_internal_service_modules()

    # .. the code objects that SQLAlchemy generated so far are kept for the imports of the next start ..
    save_generated_code()

    # .. and nothing that a fork would duplicate is open when the processes are forked.
    stop_threadpool()
    check_fork_ready()

    arbiter = Arbiter(region, processes.worker_main, config, processes.config_main)

    out = arbiter.run()
    return out

# ################################################################################################################################
# ################################################################################################################################
