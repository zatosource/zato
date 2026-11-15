# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ssl
import time
from multiprocessing import get_context
from threading import Thread

# pytest
import pytest

# Redis
from redis import SSLConnection
from redis.exceptions import ConnectionError as RedisConnectionError

# Zato
from zato.common.redis_env import Default_Pool_Size, Default_Pool_Timeout, get_redis_conn_from_values, \
    get_redis_values_from_section

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.queues import SimpleQueue
    from redis import BlockingConnectionPool, Redis
    from zato.common.typing_ import any_, anylist, stranydict, strlist
    from .conftest import RedisServer

    any_ = any_
    anylist = anylist
    BlockingConnectionPool = BlockingConnectionPool
    Redis = Redis
    RedisServer = RedisServer
    SimpleQueue = SimpleQueue
    stranydict = stranydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Host = '127.0.0.1'

    Pool_Size = 4

    # Three callers for each connection of the pool
    Caller_Count = 12

    Worker_Count = 2

    # How long each caller blocks on its connection, in seconds
    Block_Seconds = 1

    # How long a caller waits for a connection in the test of the timeout, in seconds
    Short_Pool_Timeout = 0.2

    # How long the test waits for a caller to hold its connection, in seconds
    Hold_Timeout = 10.0

    # How long to wait between two checks of the connections that the server holds, in seconds
    Hold_Sleep = 0.02

    # How long the test waits for a process or a thread, in seconds
    Join_Timeout = 60.0

    Absent_Key = 'zato.test.redis_pool.absent'

    Key = 'zato.test.redis_pool.key'
    Value = 'zato.test.redis_pool.value'

    Pool_Size_Text = '7'
    Pool_Timeout_Text = '2.5'

    Password = 'zato.test.redis_pool.password'
    CA_File = '/opt/zato/test/ca.pem'

_context = get_context('fork')

# ################################################################################################################################
# ################################################################################################################################

def _new_client(port:'int', pool_size:'int'=ModuleCtx.Pool_Size, pool_timeout:'float'=Default_Pool_Timeout) -> 'Redis':
    """ Returns a client that the server would build from its [redis] section.
    """
    section = {
        'host': ModuleCtx.Host,
        'port': port,
        'pool_size': pool_size,
        'pool_timeout': pool_timeout,
    }
    values = get_redis_values_from_section(section)

    out = get_redis_conn_from_values(values, decode_responses=True)
    return out

# ################################################################################################################################

def _get_pool(client:'Redis') -> 'BlockingConnectionPool':
    out:'any_' = client.connection_pool
    return out

# ################################################################################################################################

def _block(client:'Redis', errors:'strlist') -> 'None':
    """ Holds a connection of the client for the time of a blocking pop of a key that no one pushes to.
    """
    try:
        _ = client.blpop([ModuleCtx.Absent_Key], timeout=ModuleCtx.Block_Seconds)
    except Exception as e:
        errors.append(type(e).__name__)

# ################################################################################################################################

def _block_concurrently(client:'Redis', caller_count:'int') -> 'strlist':
    """ Runs blocking pops in several threads at once and returns the names of the errors they raised.
    """
    errors:'strlist' = []
    threads = [Thread(target=_block, args=(client, errors)) for _ in range(caller_count)]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join(ModuleCtx.Join_Timeout)

    return errors

# ################################################################################################################################

def _wait_for_clients(redis_server:'RedisServer', expected:'int') -> 'None':
    """ Waits until the server holds the expected number of connections other than the probe.
    """
    deadline = time.monotonic() + ModuleCtx.Hold_Timeout

    while redis_server.get_client_count() != expected:
        assert time.monotonic() < deadline
        time.sleep(ModuleCtx.Hold_Sleep)

# ################################################################################################################################
# ################################################################################################################################

def test_callers_beyond_the_pool_wait_for_a_connection(redis_server:'RedisServer') -> 'None':
    """ Three times as many concurrent callers as the pool has connections all complete, through the connections of the pool.
    """
    client = _new_client(redis_server.port)

    errors = _block_concurrently(client, ModuleCtx.Caller_Count)

    assert errors == []
    assert redis_server.get_client_count() == ModuleCtx.Pool_Size

# ################################################################################################################################

def test_a_caller_waits_no_longer_than_the_pool_timeout(redis_server:'RedisServer') -> 'None':
    """ A caller that finds every connection in use for longer than the timeout of the pool fails at that timeout.
    """
    client = _new_client(redis_server.port, pool_size=1, pool_timeout=ModuleCtx.Short_Pool_Timeout)

    errors:'strlist' = []
    holder = Thread(target=_block, args=(client, errors))
    holder.start()

    _wait_for_clients(redis_server, 1)

    started = time.monotonic()

    with pytest.raises(RedisConnectionError):
        _ = client.get(ModuleCtx.Key)

    elapsed = time.monotonic() - started

    holder.join(ModuleCtx.Join_Timeout)

    assert errors == []
    assert ModuleCtx.Short_Pool_Timeout <= elapsed < ModuleCtx.Block_Seconds

# ################################################################################################################################

def _run_worker(results:'SimpleQueue', client:'Redis') -> 'None':
    """ Uses in a forked process the client that its parent built and used.
    """
    errors = _block_concurrently(client, ModuleCtx.Caller_Count)

    client_id = client.client_id()
    results.put((client_id, errors))

# ################################################################################################################################

def test_each_forked_worker_opens_connections_of_its_own(redis_server:'RedisServer') -> 'None':
    """ Workers forked from a process whose client holds a connection open their own connections,
    and the connection of the parent stays usable after they exit.
    """
    client = _new_client(redis_server.port)
    parent_id = client.client_id()

    results:'SimpleQueue' = _context.SimpleQueue()
    processes = [_context.Process(target=_run_worker, args=(results, client)) for _ in range(ModuleCtx.Worker_Count)]

    for process in processes:
        process.start()

    for process in processes:
        process.join(ModuleCtx.Join_Timeout)
        assert process.exitcode == 0

    worker_ids:'anylist' = []

    while not results.empty():
        worker_id, errors = results.get()
        assert errors == []
        worker_ids.append(worker_id)

    assert len(worker_ids) == ModuleCtx.Worker_Count
    assert len(set(worker_ids)) == ModuleCtx.Worker_Count
    assert parent_id not in worker_ids

    assert client.client_id() == parent_id

# ################################################################################################################################

def test_the_pool_values_are_read_from_the_section() -> 'None':
    """ The size and the timeout of the pool arrive as text from server.conf, and a section without them,
    or with them empty, receives the defaults.
    """
    values = get_redis_values_from_section({'pool_size': ModuleCtx.Pool_Size_Text, 'pool_timeout': ModuleCtx.Pool_Timeout_Text})

    assert values['pool_size'] == 7
    assert values['pool_timeout'] == 2.5

    pool = _get_pool(get_redis_conn_from_values(values))

    assert pool.max_connections == 7
    assert pool.timeout == 2.5

    for section in ({}, {'pool_size': '', 'pool_timeout': ''}):
        values = get_redis_values_from_section(section)

        assert values['pool_size'] == Default_Pool_Size
        assert values['pool_timeout'] == Default_Pool_Timeout

# ################################################################################################################################

def test_the_pool_keeps_the_connection_arguments(redis_server:'RedisServer') -> 'None':
    """ The pool opens its connections with the credentials, the SSL configuration and the decoding of the section.
    """
    section:'stranydict' = {
        'password': ModuleCtx.Password,
        'ssl': 'True',
        'ssl_verify': 'False',
        'ssl_ca_file': ModuleCtx.CA_File,
    }
    values = get_redis_values_from_section(section)

    pool = _get_pool(get_redis_conn_from_values(values, decode_responses=True))
    kwargs = pool.connection_kwargs

    assert pool.connection_class is SSLConnection
    assert kwargs['password'] == ModuleCtx.Password
    assert kwargs['ssl_ca_certs'] == ModuleCtx.CA_File
    assert kwargs['ssl_cert_reqs'] == ssl.CERT_NONE
    assert kwargs['ssl_check_hostname'] is False
    assert kwargs['decode_responses'] is True

    client = _new_client(redis_server.port)
    _ = client.set(ModuleCtx.Key, ModuleCtx.Value)

    assert client.get(ModuleCtx.Key) == ModuleCtx.Value

# ################################################################################################################################
# ################################################################################################################################
