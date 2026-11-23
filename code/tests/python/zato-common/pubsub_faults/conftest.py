# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
from gevent import monkey
_ = monkey.patch_all()

# stdlib
import os
import shutil
import subprocess
import sys
import tempfile

_here = os.path.dirname(__file__)
sys.path.insert(0, _here)

# pytest
import pytest

# Zato
from container import Container, get_disk_device
from fault_server import get_fault_fixture_arguments, Server_Config
from process import get_process_env, new_scope, ProcessEnvironment
from pubsub_rest.capture import limit_captured_logs
from pubsub_rest.server import PubSubServer
from tools import get_fsfault_docker_args
from toxiproxy import Database_Proxy, Toxiproxy, Toxiproxy_Host
from zato.common.test.conftest_base_pubsub import create_zato_server_fixture
from zato.common.db_env.database import get_database_engine
from zato.common.db_env.database_env import DatabaseEnv
from zato.common.db_env.fence import ModuleCtx as FenceCtx
from zato.common.pubsub.sql.config import ModuleCtx
from zato.common.test.pubsub_database import get_database_address, get_db_mode, get_runtime_dir, is_postgresql_mode, \
    PubSubDatabase, pubsub_db_env, start_pubsub_database, stop_pubsub_database
from zato.common.test.pubsub_profile import session_dns
from zato.common.test.pubsub_replication import ReplicatedDatabase, start_replicated_database, stop_replicated_database

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Generator

    from process_faults import Scope
    from zato.common.typing_ import strstrdict

    nonegen        = Generator[None, None, None]
    scopegen       = Generator['Scope', None, None]
    databasegen    = Generator['FaultDatabase', None, None]
    environmentgen = Generator[ProcessEnvironment, None, None]
    streamgen      = Generator[Toxiproxy, None, None]
    strgen         = Generator[str, None, None]
    replicatedgen  = Generator[ReplicatedDatabase, None, None]

# ################################################################################################################################
# ################################################################################################################################

# How many fully delivered messages each topic keeps during the runs, which bounds the tables.
_delivered_max_messages = '10000'

# The server of each test.
_server = PubSubServer('pubsub-faults')

# The name of the control file of the faults of the PostgreSQL container.
_database_control_name = 'postgresql'

# The name of the copy of the log of each container of the failover, which outlives the container.
_failover_log_copy_name = 'pubsub-faults-failover-{}.txt'

# ################################################################################################################################
# ################################################################################################################################

class FaultDatabase:
    """ The PostgreSQL container that the faults of one module apply to, with the disk that holds its data.
    """

    def __init__(self, database:'PubSubDatabase') -> 'None':
        self.database = database
        self.container = Container(database.container_name)
        self.device = get_disk_device(database.work_dir)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def captured_log_level(request:'pytest.FixtureRequest', caplog:'pytest.LogCaptureFixture') -> 'nonegen':
    """ Keeps the warnings and errors only in the logs that pytest captures for the report of each test.
    """
    yield from limit_captured_logs(request, caplog)

# ################################################################################################################################

@pytest.fixture(scope='module')
def fault_database() -> 'databasegen':
    """ The PostgreSQL container of one fault suite in the mode that Zato_Test_PubSub_DB_Mode selects,
    with the generation file and the retention of the run.
    """
    mode = get_db_mode()
    assert is_postgresql_mode(mode), f'The faults apply to a PostgreSQL container and the mode is `{mode}`'

    work_dir = tempfile.mkdtemp(prefix='zato-pubsub-faults-', dir=get_runtime_dir())
    database = start_pubsub_database('faults', mode)

    env = {
        FenceCtx.Env_Generation_File: os.path.join(work_dir, 'database-generation'),
        ModuleCtx.Env_Delivered_Max_Messages: _delivered_max_messages,
    }
    env.update(database.env)

    try:
        with pubsub_db_env(env):
            yield FaultDatabase(database)
            get_database_engine().dispose()
    finally:
        stop_pubsub_database(database)
        shutil.rmtree(work_dir, ignore_errors=True)

# ################################################################################################################################

@pytest.fixture(scope='module')
def standby_database() -> 'databasegen':
    """ A primary with a synchronous standby, whose container and disk the faults apply to, so that every commit
    waits for the standby. The server reaches the primary through the proxy of the replication.
    """
    mode = get_db_mode()
    assert is_postgresql_mode(mode), f'The synchronous standby is a PostgreSQL container and the mode is `{mode}`'

    work_dir = tempfile.mkdtemp(prefix='zato-pubsub-standby-faults-', dir=get_runtime_dir())
    replicated = start_replicated_database('faults-standby', mode, is_sync=True)

    env = {
        FenceCtx.Env_Generation_File: os.path.join(work_dir, 'database-generation'),
        ModuleCtx.Env_Delivered_Max_Messages: _delivered_max_messages,
    }
    env.update(replicated.env)

    standby = FaultDatabase(replicated.primary)
    standby.container = Container(replicated.standby_container)
    standby.device = get_disk_device(replicated.standby_dir)

    try:
        with pubsub_db_env(env):
            yield standby
            get_database_engine().dispose()
    finally:
        stop_replicated_database(replicated)
        shutil.rmtree(work_dir, ignore_errors=True)

# ################################################################################################################################

@pytest.fixture
def failover_database() -> 'replicatedgen':
    """ A primary with a synchronous standby for one failover, after which the standby is the only database left.
    """
    mode = get_db_mode()
    assert is_postgresql_mode(mode), f'The failover is between PostgreSQL containers and the mode is `{mode}`'

    work_dir = tempfile.mkdtemp(prefix='zato-pubsub-failover-faults-', dir=get_runtime_dir())
    replicated = start_replicated_database('faults-failover', mode, is_sync=True)

    env = {
        FenceCtx.Env_Generation_File: os.path.join(work_dir, 'database-generation'),
        ModuleCtx.Env_Delivered_Max_Messages: _delivered_max_messages,
    }
    env.update(replicated.env)

    try:
        with pubsub_db_env(env):
            yield replicated
            get_database_engine().dispose()
    finally:
        _copy_container_log(replicated.primary.container_name, 'primary')
        _copy_container_log(replicated.standby_container, 'standby')
        stop_replicated_database(replicated)
        shutil.rmtree(work_dir, ignore_errors=True)

# ################################################################################################################################

def _copy_container_log(container_name:'str', role:'str') -> 'None':
    """ Copies the log of a database container of the failover, with its slow statements, checkpoints and autovacuum runs,
    to the temporary directory, where it remains after the container is removed.
    """
    path = os.path.join(tempfile.gettempdir(), _failover_log_copy_name.format(role))

    with open(path, 'wb') as log_file:
        _ = subprocess.run(['docker', 'logs', container_name], stdout=log_file, stderr=subprocess.STDOUT, check=True)

# ################################################################################################################################

@pytest.fixture(scope='module')
def endpoint_work_dir() -> 'strgen':
    """ The pub/sub database of the push endpoints in the mode that Zato_Test_PubSub_DB_Mode selects,
    a SQLite file or a PostgreSQL container, and the directory of the run.
    """
    mode = get_db_mode()
    work_dir = tempfile.mkdtemp(prefix='zato-pubsub-endpoints-', dir=get_runtime_dir())

    env:'strstrdict' = {
        FenceCtx.Env_Generation_File: os.path.join(work_dir, 'database-generation'),
        ModuleCtx.Env_Delivered_Max_Messages: _delivered_max_messages,
    }

    database = None

    if is_postgresql_mode(mode):
        database = start_pubsub_database('endpoints', mode)
        env.update(database.env)
    else:
        env[DatabaseEnv.Env_Type] = DatabaseEnv.Type_SQLite
        env[DatabaseEnv.Env_Path] = os.path.join(work_dir, 'zato.db')

    try:
        with pubsub_db_env(env):
            yield work_dir
            get_database_engine().dispose()
    finally:
        if database:
            stop_pubsub_database(database)
        shutil.rmtree(work_dir, ignore_errors=True)

# ################################################################################################################################

@pytest.fixture(scope='module')
def stream_database() -> 'streamgen':
    """ The PostgreSQL container of the stream faults, which the server reaches through a proxy of Toxiproxy.
    """
    mode = get_db_mode()
    assert is_postgresql_mode(mode), f'The stream faults apply to the link to PostgreSQL and the mode is `{mode}`'

    work_dir = tempfile.mkdtemp(prefix='zato-pubsub-stream-faults-', dir=get_runtime_dir())
    database = start_pubsub_database('stream-faults', mode)

    toxiproxy = Toxiproxy('database')
    toxiproxy.start()

    try:
        upstream_host = get_database_address(database)
        listen_port = toxiproxy.add_proxy(Database_Proxy, database.port, upstream_host)

        # The endpoint name of a managed mode resolves to the proxy ..
        if database.profile_name:
            runtime_dir = get_runtime_dir()
            session_dns.register(runtime_dir, database.endpoint, Toxiproxy_Host)

        env = {
            FenceCtx.Env_Generation_File: os.path.join(work_dir, 'database-generation'),
            ModuleCtx.Env_Delivered_Max_Messages: _delivered_max_messages,
        }
        env.update(database.env)
        env['Zato_Database_Port'] = f'{listen_port}'

        with pubsub_db_env(env):
            yield toxiproxy
            get_database_engine().dispose()

    finally:
        toxiproxy.stop()
        stop_pubsub_database(database)
        shutil.rmtree(work_dir, ignore_errors=True)

# ################################################################################################################################

@pytest.fixture(scope='module')
def process_environment() -> 'environmentgen':
    """ The database of the faults of single processes in the mode that Zato_Test_PubSub_DB_Mode selects -
    a SQLite file or a PostgreSQL container whose processes preload the library of the file system faults.
    """
    mode = get_db_mode()
    work_dir = tempfile.mkdtemp(prefix='zato-pubsub-process-faults-', dir=get_runtime_dir())

    env:'strstrdict' = {
        FenceCtx.Env_Generation_File: os.path.join(work_dir, 'database-generation'),
        ModuleCtx.Env_Delivered_Max_Messages: _delivered_max_messages,
    }

    database = None

    if is_postgresql_mode(mode):
        control_dir = os.path.join(work_dir, 'fsfault-control')
        os.makedirs(control_dir)

        docker_args = get_fsfault_docker_args(work_dir, control_dir, _database_control_name)

        database = start_pubsub_database('process-faults', mode, extra_docker_args=docker_args)
        env.update(database.env)

    else:
        env[DatabaseEnv.Env_Type] = DatabaseEnv.Type_SQLite
        env[DatabaseEnv.Env_Path] = os.path.join(work_dir, 'zato.db')

    try:
        with pubsub_db_env(env):
            yield ProcessEnvironment(work_dir, database)
    finally:
        if database:
            stop_pubsub_database(database)
        shutil.rmtree(work_dir, ignore_errors=True)

# ################################################################################################################################

@pytest.fixture
def server_scope(process_environment:'ProcessEnvironment') -> 'scopegen':
    """ The transient scope that the server of one test of a single server runs in, together with its cleanup process,
    both of them with the libraries of the faults preloaded.
    """
    scope = new_scope()

    Server_Config.server_env = get_process_env(process_environment)
    Server_Config.command_prefix = scope.get_command_prefix()
    Server_Config.scope = scope

    try:
        yield scope
    finally:
        Server_Config.reset()
        scope.stop()

# ################################################################################################################################

# The server of one test, against the database that the fixtures requested before it select.
zato_server = create_zato_server_fixture(**get_fault_fixture_arguments(_server, Server_Config))

# ################################################################################################################################

@pytest.fixture
def server(zato_server:'None') -> 'PubSubServer':
    return _server

# ################################################################################################################################
# ################################################################################################################################
