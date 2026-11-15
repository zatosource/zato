# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import traceback
from multiprocessing import get_context

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.pool import NullPool

# Zato
from zato.common.db_env.common import EnvDBConfig
from zato.common.db_env.engine import dispose_env_engine, get_env_engine, get_worker_pool_size, set_pool_worker_count
from zato.common.pubsub.sql.config import pubsub_db_config
from zato.common.typing_ import cast_
from zato.server.base.parallel.delivery import PushDelivery

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from live_sql.containers import DatabaseServer
    from multiprocessing.context import ForkProcess
    from multiprocessing.synchronize import Event as EventType
    from zato.common.typing_ import list_, stranydict
    from zato.common.pubsub.fence import DeliveryFence
    from zato.common.pubsub.sql.backend import SQLPubSubBackend
    from zato.server.base.parallel import ParallelServer

    DatabaseServer = DatabaseServer
    DeliveryFence = DeliveryFence
    EventType = EventType
    ForkProcess = ForkProcess
    stranydict = stranydict
    nonegen = Iterator[None]
    workerlist = list_[tuple[ForkProcess, EventType]]
    ParallelServer = ParallelServer
    SQLPubSubBackend = SQLPubSubBackend

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The pool size that the environment configures, and the workers among which it is divided
    Pool_Size = 80
    Worker_Count = 4

    # The environment variables of the database whose pools the tests create
    Env_Prefix = 'Zato_Test_Worker_Pools_DB_'

    # How long the test waits for the processes of the workers, in seconds
    Join_Timeout = 60.0

# ################################################################################################################################
# ################################################################################################################################

_config = EnvDBConfig(
    env_prefix=ModuleCtx.Env_Prefix,
    sqlite_file_name='zato-test-worker-pools.db',
    metadata=MetaData(),
    needs_pool=True,
)

# The workers of the tests are forked, so that each creates its own engine
_context = get_context('fork')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def worker_count() -> 'nonegen':
    """ Divides the pools among the workers of a test, after which a process has one worker again.
    """
    set_pool_worker_count(ModuleCtx.Worker_Count)
    yield
    set_pool_worker_count(1)

# ################################################################################################################################

def _set_env(monkeypatch:'pytest.MonkeyPatch', details:'stranydict') -> 'None':
    monkeypatch.setenv(_config.env_type, details['type'])
    monkeypatch.setenv(_config.env_host, details['host'])
    monkeypatch.setenv(_config.env_port, details['port'])
    monkeypatch.setenv(_config.env_username, details['username'])
    monkeypatch.setenv(_config.env_password, details['password'])
    monkeypatch.setenv(_config.env_name, details['name'])
    monkeypatch.setenv(_config.env_pool_size, str(ModuleCtx.Pool_Size))

# ################################################################################################################################

def _get_connection_count(details:'stranydict') -> 'int':
    """ Returns how many connections other than its own the database holds for the user of the tests.
    """
    username = details['username']
    url = f'postgresql+pg8000://{username}:{details["password"]}@{details["host"]}:{details["port"]}/{details["name"]}'

    engine = create_engine(url, poolclass=NullPool)

    # The user of the tests is the superuser of the container, under whose name its background processes run as well
    query = text("""
        select count(*) from pg_stat_activity
        where usename = :username and backend_type = 'client backend' and pid != pg_backend_pid()
    """)

    with engine.connect() as connection:
        out = connection.execute(query, {'username': username}).scalar_one()

    engine.dispose()
    return out

# ################################################################################################################################

def _hold_every_connection(held:'EventType', release:'EventType') -> 'None':
    """ Checks out every connection of the pool of this worker and holds them until the test releases them.
    """
    exit_code = 1

    try:
        engine = get_env_engine(_config)
        connections = [engine.connect() for _ in range(engine.pool.size())]

        held.set()
        _ = release.wait(ModuleCtx.Join_Timeout)

        for connection in connections:
            connection.close()

        engine.dispose()
        exit_code = 0

    except BaseException:
        traceback.print_exc()

    finally:
        os._exit(exit_code)

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize(('pool_size', 'worker_count', 'expected'), [
    (80, 1, 80),
    (3, 1, 3),
    (80, 4, 20),
    (81, 4, 20),
    (80, 32, 4),
    (2, 4, 2),
])
def test_a_worker_receives_its_share_of_the_configured_pool(pool_size:'int', worker_count:'int', expected:'int') -> 'None':
    set_pool_worker_count(worker_count)

    try:
        assert get_worker_pool_size(pool_size) == expected
    finally:
        set_pool_worker_count(1)

# ################################################################################################################################

@pytest.mark.usefixtures('worker_count')
def test_the_push_deliveries_of_a_worker_use_the_share_of_its_pool(monkeypatch:'pytest.MonkeyPatch') -> 'None':
    monkeypatch.setenv(pubsub_db_config.env_pool_size, str(ModuleCtx.Pool_Size))

    server = cast_('ParallelServer', None)
    backend = cast_('SQLPubSubBackend', None)
    fence = cast_('DeliveryFence', None)

    delivery = PushDelivery(server, backend, fence)

    # Three quarters of the twenty connections of the worker
    assert delivery._database_slots.counter == 15

# ################################################################################################################################

@pytest.mark.usefixtures('worker_count')
def test_the_workers_together_hold_the_configured_connections(
    monkeypatch:'pytest.MonkeyPatch',
    postgresql_server:'DatabaseServer',
    ) -> 'None':

    _set_env(monkeypatch, postgresql_server.details)

    release = _context.Event()
    workers:'workerlist' = []

    # Each worker checks out every connection of its pool ..
    for _ in range(ModuleCtx.Worker_Count):
        held = _context.Event()
        process = _context.Process(target=_hold_every_connection, args=(held, release))
        process.start()
        workers.append((process, held))

    for _, held in workers:
        assert held.wait(ModuleCtx.Join_Timeout)

    # .. and the database holds as many connections as configured for the server as a whole.
    try:
        assert _get_connection_count(postgresql_server.details) == ModuleCtx.Pool_Size

    finally:
        release.set()

        for process, _ in workers:
            process.join(ModuleCtx.Join_Timeout)

    for process, _ in workers:
        assert process.exitcode == 0

# ################################################################################################################################

def test_a_single_process_holds_the_configured_pool(
    monkeypatch:'pytest.MonkeyPatch',
    postgresql_server:'DatabaseServer',
    ) -> 'None':

    _set_env(monkeypatch, postgresql_server.details)

    engine = get_env_engine(_config)

    try:
        assert engine.pool.size() == ModuleCtx.Pool_Size
    finally:
        dispose_env_engine(_config)

# ################################################################################################################################
# ################################################################################################################################
