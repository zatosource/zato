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
import sys
import tempfile

_here = os.path.dirname(__file__)
_stability_dir = os.path.abspath(os.path.join(_here, '..', 'pubsub_stability'))
_perf_dir = os.path.abspath(os.path.join(_here, '..', 'pubsub_backend_perf'))
_lib_dir = os.path.abspath(os.path.join(_here, '..', 'lib'))

sys.path.insert(0, _lib_dir)
sys.path.insert(0, _perf_dir)
sys.path.insert(0, _stability_dir)
sys.path.insert(0, _here)

# pytest
import pytest

# Zato
from capture import limit_captured_logs
from container import Container, get_disk_device
from process import ProcessEnvironment
from tools import build_fsfault
from toxiproxy import Toxiproxy, Toxiproxy_Host
from zato.common.pubsub.sql.config import get_pubsub_engine, ModuleCtx
from zato.common.test.pubsub_database import get_database_address, get_db_mode, get_runtime_dir, is_postgresql_mode, \
    PubSubDatabase, pubsub_db_env, start_pubsub_database, stop_pubsub_database
from zato.common.test.pubsub_profile import session_dns
from zato.common.test.pubsub_replication import ReplicatedDatabase, start_replicated_database, stop_replicated_database

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Generator

    from zato.common.typing_ import strstrdict

    nonegen        = Generator[None, None, None]
    databasegen    = Generator['FaultDatabase', None, None]
    environmentgen = Generator[ProcessEnvironment, None, None]
    streamgen      = Generator[Toxiproxy, None, None]
    strgen         = Generator[str, None, None]
    replicatedgen  = Generator[ReplicatedDatabase, None, None]

# ################################################################################################################################
# ################################################################################################################################

# How many fully delivered messages each topic keeps during the runs, which bounds the tables.
_delivered_max_messages = '10000'

# Where the container of PostgreSQL sees the library of the file system faults and the directory of its control file.
_container_fsfault_path = '/zato-fault/fsfault.so'
_container_control_dir = '/zato-fault/control'

# The proxy of Toxiproxy on the link from the server to PostgreSQL.
Database_Proxy = 'postgresql'

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
        ModuleCtx.Env_Generation_File: os.path.join(work_dir, 'pubsub-generation'),
        ModuleCtx.Env_Delivered_Max_Messages: _delivered_max_messages,
    }
    env.update(database.env)

    try:
        with pubsub_db_env(env):
            yield FaultDatabase(database)
            get_pubsub_engine().dispose()
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
        ModuleCtx.Env_Generation_File: os.path.join(work_dir, 'pubsub-generation'),
        ModuleCtx.Env_Delivered_Max_Messages: _delivered_max_messages,
    }
    env.update(replicated.env)

    standby = FaultDatabase(replicated.primary)
    standby.container = Container(replicated.standby_container)
    standby.device = get_disk_device(replicated.standby_dir)

    try:
        with pubsub_db_env(env):
            yield standby
            get_pubsub_engine().dispose()
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
        ModuleCtx.Env_Generation_File: os.path.join(work_dir, 'pubsub-generation'),
        ModuleCtx.Env_Delivered_Max_Messages: _delivered_max_messages,
    }
    env.update(replicated.env)

    try:
        with pubsub_db_env(env):
            yield replicated
            get_pubsub_engine().dispose()
    finally:
        stop_replicated_database(replicated)
        shutil.rmtree(work_dir, ignore_errors=True)

# ################################################################################################################################

@pytest.fixture(scope='module')
def endpoint_work_dir() -> 'strgen':
    """ The pub/sub database of the push endpoints in the mode that Zato_Test_PubSub_DB_Mode selects,
    a SQLite file or a PostgreSQL container, and the directory of the run.
    """
    mode = get_db_mode()
    work_dir = tempfile.mkdtemp(prefix='zato-pubsub-endpoints-', dir=get_runtime_dir())

    env:'strstrdict' = {
        ModuleCtx.Env_Generation_File: os.path.join(work_dir, 'pubsub-generation'),
        ModuleCtx.Env_Delivered_Max_Messages: _delivered_max_messages,
    }

    database = None

    if is_postgresql_mode(mode):
        database = start_pubsub_database('endpoints', mode)
        env.update(database.env)
    else:
        env[ModuleCtx.Env_Path] = os.path.join(work_dir, 'pubsub.db')

    try:
        with pubsub_db_env(env):
            yield work_dir
            get_pubsub_engine().dispose()
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
            ModuleCtx.Env_Generation_File: os.path.join(work_dir, 'pubsub-generation'),
            ModuleCtx.Env_Delivered_Max_Messages: _delivered_max_messages,
        }
        env.update(database.env)
        env['Zato_PubSub_DB_Port'] = f'{listen_port}'

        with pubsub_db_env(env):
            yield toxiproxy
            get_pubsub_engine().dispose()

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
        ModuleCtx.Env_Generation_File: os.path.join(work_dir, 'pubsub-generation'),
        ModuleCtx.Env_Delivered_Max_Messages: _delivered_max_messages,
    }

    database = None

    if is_postgresql_mode(mode):
        control_dir = os.path.join(work_dir, 'fsfault-control')
        os.makedirs(control_dir)

        fsfault_path = build_fsfault()

        docker_args = [
            '-v', f'{fsfault_path}:{_container_fsfault_path}:ro',
            '-v', f'{control_dir}:{_container_control_dir}:ro',
            '-e', f'LD_PRELOAD={_container_fsfault_path}',
            '-e', f'ZATO_FSFAULT_CONTROL={_container_control_dir}/postgresql',
        ]

        database = start_pubsub_database('process-faults', mode, extra_docker_args=docker_args)
        env.update(database.env)

    else:
        env[ModuleCtx.Env_Path] = os.path.join(work_dir, 'pubsub.db')

    try:
        with pubsub_db_env(env):
            yield ProcessEnvironment(work_dir, database)
    finally:
        if database:
            stop_pubsub_database(database)
        shutil.rmtree(work_dir, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################
