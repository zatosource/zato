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
from contextlib import contextmanager, ExitStack

_here = os.path.dirname(__file__)
_faults_dir = os.path.abspath(os.path.join(_here, '..', 'pubsub_faults'))
_stability_dir = os.path.abspath(os.path.join(_here, '..', 'pubsub_stability'))
_perf_dir = os.path.abspath(os.path.join(_here, '..', 'pubsub_backend_perf'))
_lib_dir = os.path.abspath(os.path.join(_here, '..', 'lib'))

sys.path.insert(0, _lib_dir)
sys.path.insert(0, _perf_dir)
sys.path.insert(0, _stability_dir)
sys.path.insert(0, _faults_dir)
sys.path.insert(0, _here)

# pytest
import pytest

# Zato
from capture import limit_captured_logs
from container import Container, get_disk_device
from profiles import get_profile_limits
from zato.common.pubsub.sql.config import get_pubsub_engine, ModuleCtx
from zato.common.test.pubsub_database import get_db_mode, get_runtime_dir, is_managed_mode, PubSubDatabase, \
    pubsub_db_env, start_pubsub_database, stop_pubsub_database
from zato.common.test.pubsub_replication import ReplicatedDatabase, start_replicated_database, stop_replicated_database

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Generator, Iterator

    from zato.common.typing_ import callable_, strstrdict

    nonegen       = Generator[None, None, None]
    databasegen   = Generator['ManagedDatabase', None, None]
    factorygen    = Generator[callable_, None, None]
    replicatedgen = Generator[ReplicatedDatabase, None, None]

# ################################################################################################################################
# ################################################################################################################################

# How many fully delivered messages each topic keeps during the runs, which bounds the tables.
_delivered_max_messages = '10000'

# The parameters that each managed mode gives its own values to.
_profile_parameters = ['storage_tier', 'failover_delay', 'round_trip_ms']

# ################################################################################################################################
# ################################################################################################################################

class ManagedDatabase:
    """ The PostgreSQL container of a managed mode that the conditions of one test apply to, with the disk
    that holds its data and the directory of the run.
    """

    def __init__(self, database:'PubSubDatabase', work_dir:'str') -> 'None':
        self.database = database
        self.work_dir = work_dir
        self.container = Container(database.container_name)
        self.device = get_disk_device(database.work_dir)

# ################################################################################################################################
# ################################################################################################################################

def pytest_generate_tests(metafunc:'pytest.Metafunc') -> 'None':
    """ Gives the parameters of the tests the values of the managed mode that the session runs in.
    """
    names = metafunc.fixturenames

    for name in _profile_parameters:
        if name in names:
            limits = get_profile_limits()

            if name == 'storage_tier':
                values = limits.storage_tiers
                ids = []
                for tier in values:
                    ids.append(tier.name)
                metafunc.parametrize(name, values, ids=ids)

            elif name == 'failover_delay':
                metafunc.parametrize(name, limits.failover_delays)

            else:
                metafunc.parametrize(name, limits.round_trip_ms)

# ################################################################################################################################

def _get_run_env(work_dir:'str', database_env:'strstrdict') -> 'strstrdict':
    out = {
        ModuleCtx.Env_Generation_File: os.path.join(work_dir, 'pubsub-generation'),
        ModuleCtx.Env_Delivered_Max_Messages: _delivered_max_messages,
    }
    out.update(database_env)
    return out

# ################################################################################################################################

@contextmanager
def _managed_database(label:'str', image:'str'='', env:'strstrdict | None'=None) -> 'Iterator[ManagedDatabase]':
    """ Starts the database of the managed mode that Zato_Test_PubSub_DB_Mode selects and points the environment
    of the test at it, together with the variables of the test.
    """
    mode = get_db_mode()
    assert is_managed_mode(mode), f'The managed suites run in a managed mode and the mode is `{mode}`'

    work_dir = tempfile.mkdtemp(prefix=f'zato-pubsub-{label}-', dir=get_runtime_dir())
    database = start_pubsub_database(label, mode, image=image)

    run_env = _get_run_env(work_dir, database.env)

    if env:
        run_env.update(env)

    try:
        with pubsub_db_env(run_env):
            yield ManagedDatabase(database, work_dir)
            get_pubsub_engine().dispose()
    finally:
        stop_pubsub_database(database)
        shutil.rmtree(work_dir, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def captured_log_level(request:'pytest.FixtureRequest', caplog:'pytest.LogCaptureFixture') -> 'nonegen':
    """ Keeps the warnings and errors only in the logs that pytest captures for the report of each test.
    """
    yield from limit_captured_logs(request, caplog)

# ################################################################################################################################

@pytest.fixture(scope='module')
def managed_database() -> 'databasegen':
    """ The database of one module of the managed suites.
    """
    with _managed_database('managed') as database:
        yield database

# ################################################################################################################################

@pytest.fixture
def start_managed() -> 'factorygen':
    """ Starts a database of its own for one test, from the image and with the variables that the test gives,
    and removes it once the test ends.
    """
    with ExitStack() as stack:

        def _start(label:'str', image:'str'='', env:'strstrdict | None'=None) -> 'ManagedDatabase':
            context = _managed_database(label, image, env)
            out = stack.enter_context(context)
            return out

        yield _start

# ################################################################################################################################

@pytest.fixture
def failover_database() -> 'replicatedgen':
    """ A primary with a synchronous standby for one failover, after which the standby is the only database left.
    """
    mode = get_db_mode()
    assert is_managed_mode(mode), f'The managed suites run in a managed mode and the mode is `{mode}`'

    work_dir = tempfile.mkdtemp(prefix='zato-pubsub-managed-failover-', dir=get_runtime_dir())
    replicated = start_replicated_database('managed-failover', mode, is_sync=True)

    run_env = _get_run_env(work_dir, replicated.env)

    try:
        with pubsub_db_env(run_env):
            yield replicated
            get_pubsub_engine().dispose()
    finally:
        stop_replicated_database(replicated)
        shutil.rmtree(work_dir, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################
