# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import socket
import time
import traceback
from http.client import HTTPConnection
from multiprocessing import get_context

# Zato
from zato.common.rate_limiting.common import Microseconds_Per_Second
from zato.common.rate_limiting.region import RegionTokenBucketRegistry
from zato.common.rate_limiting.token_bucket import TokenBucketConfig
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.connection import Connection
    from multiprocessing.process import BaseProcess
    from multiprocessing.synchronize import Event
    from zato.common.typing_ import anydict, anytuple, list_

    anydict = anydict
    anytuple = anytuple
    BaseProcess = BaseProcess
    Connection = Connection
    Event = Event

    connectionlist = list_[Connection]
    processlist    = list_[BaseProcess]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Host = '127.0.0.1'

    # The worker count at which the target of the scaling measurement applies
    Worker_Count = 8

    # How many checks each worker makes and how many requests the client sends
    Checks_Per_Worker = 500_000
    Request_Count = 500

    # The largest share of the processing of one request that one contended check may take
    Max_Check_Share = 0.1

    # A key and its group, as SlottedCIDRMatcher.check builds them for the first time range of a rule
    Key   = 'rest.orders:10.0.0.0/8:0'
    Group = 'rest.orders:10.0.0.0/8:'

    # A burst that no test spends, so that every check takes one token and writes the state of the cell
    Rate  = 1
    Burst = 1_000_000_000

    # A clock reading that every check shares
    Now_us = 1_800_000_000 * Microseconds_Per_Second

    # The metric that counts the requests refused because the table is at capacity
    Table_Full_Metric = 0

    # The largest request that the server of the test accepts, in bytes
    Max_Msg_Size = 1_000_000

    # How long the client waits for the server to listen and for each response, in seconds
    Connect_Timeout = 20.0
    Response_Timeout = 10.0
    Connect_Interval = 0.05

    # How long the test waits for a worker to report and for a process to exit, in seconds
    Report_Timeout = 120.0
    Join_Timeout = 20.0

# ################################################################################################################################
# ################################################################################################################################

# Workers are forked, as the arbiter forks them, so that they inherit the mapping
_context = get_context('fork')

# ################################################################################################################################

def _new_region() -> 'SharedRegion':
    config = {
        'slot_count': ModuleCtx.Worker_Count,
        'wake_capacity': 8,
        'cell_capacity': 64,
        'queue_count': 1,
        'metric_count': 1,
        'series_capacity': 0,
        'series_key_bytes': 0,
        'dedup_capacity': 0,
        'breaker_capacity': 0,
        'lock_capacity': 0,
        'start_id': 1,
    }
    out = SharedRegion(config)
    return out

# ################################################################################################################################

def _check_many(region:'SharedRegion', slot:'int', start:'Event', conn:'Connection') -> 'None':
    """ Makes the checks of one worker against the cell that every worker shares and reports the time of one check.
    """
    token_buckets = RegionTokenBucketRegistry(region, slot, ModuleCtx.Table_Full_Metric)
    config = TokenBucketConfig.from_parts(ModuleCtx.Rate, ModuleCtx.Burst)

    # Every worker starts at once, so that their checks overlap ..
    _ = start.wait(ModuleCtx.Report_Timeout)

    started = time.perf_counter()

    for _ in range(ModuleCtx.Checks_Per_Worker):
        _ = token_buckets.check_in_group(ModuleCtx.Key, ModuleCtx.Group, config, ModuleCtx.Now_us)

    # .. and each one reports the mean time of its checks.
    elapsed = time.perf_counter() - started
    conn.send(elapsed / ModuleCtx.Checks_Per_Worker)

# ################################################################################################################################

def _get_contended_check_time() -> 'float':
    """ Returns the mean time of one check, in seconds, in the slowest of the workers that check one cell at once.
    """
    region = _new_region()
    start = _context.Event()

    connections:'connectionlist' = []
    processes:'processlist' = []

    for slot in range(ModuleCtx.Worker_Count):
        parent_conn, child_conn = _context.Pipe()
        process = _context.Process(target=_check_many, args=(region, slot, start, child_conn))
        process.start()

        connections.append(parent_conn)
        processes.append(process)

    start.set()

    check_times:'list_[float]' = []

    for parent_conn in connections:
        assert parent_conn.poll(ModuleCtx.Report_Timeout)
        check_times.append(parent_conn.recv())

    for process in processes:
        process.join(ModuleCtx.Join_Timeout)
        assert process.exitcode == 0

    # Every check took one token, so the cell received every write of every worker
    token_buckets = RegionTokenBucketRegistry(region, 0, ModuleCtx.Table_Full_Metric)
    config = TokenBucketConfig.from_parts(ModuleCtx.Rate, ModuleCtx.Burst)
    result = token_buckets.check_in_group(ModuleCtx.Key, ModuleCtx.Group, config, ModuleCtx.Now_us)

    check_count = ModuleCtx.Worker_Count * ModuleCtx.Checks_Per_Worker
    assert result.tokens_remaining == ModuleCtx.Burst - check_count - 1

    out = max(check_times)
    return out

# ################################################################################################################################

def _get_free_port() -> 'int':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((ModuleCtx.Host, 0))
        out = sock.getsockname()[1]

    return out

# ################################################################################################################################

def _serve(port:'int') -> 'None':
    """ Runs the HTTP server of zato_server_core in a process of its own, with a handler that answers every request.
    """
    exit_code = 1

    try:
        from zato_server_core.zato_server_core import HTTPServer

        def handle(request_ctx:'anydict') -> 'anytuple':
            out = ('200 OK', {'Content-Type': 'text/plain'}, b'OK')
            return out

        server = HTTPServer(ModuleCtx.Host, port, handle, 'zato-test', ModuleCtx.Max_Msg_Size)
        _ = server.serve_forever()
        exit_code = 0

    except BaseException:
        traceback.print_exc()

    finally:
        os._exit(exit_code)

# ################################################################################################################################

def _connect(port:'int') -> 'HTTPConnection':
    """ Returns a connection to the server, which may not be listening yet.
    """
    deadline = time.monotonic() + ModuleCtx.Connect_Timeout

    while True:
        connection = HTTPConnection(ModuleCtx.Host, port, timeout=ModuleCtx.Response_Timeout)

        try:
            connection.connect()
            return connection

        except ConnectionRefusedError:
            if time.monotonic() > deadline:
                raise
            time.sleep(ModuleCtx.Connect_Interval)

# ################################################################################################################################

def _get_request_time() -> 'float':
    """ Returns the mean time of one request, in seconds, to a server whose handler does no work of its own.
    """
    port = _get_free_port()

    process = _context.Process(target=_serve, args=(port,))
    process.start()

    try:
        connection = _connect(port)
        started = time.perf_counter()

        for _ in range(ModuleCtx.Request_Count):
            connection.request('GET', '/')
            response = connection.getresponse()
            assert response.read() == b'OK'

        elapsed = time.perf_counter() - started
        connection.close()

    finally:
        process.terminate()
        process.join(ModuleCtx.Join_Timeout)

    out = elapsed / ModuleCtx.Request_Count
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_a_cell_checked_by_every_worker_costs_a_fraction_of_one_request() -> 'None':

    # A request to a handler that does no work is the least that any request costs ..
    request_time = _get_request_time()

    # .. and a check of a cell that every worker writes at once costs no more than a share of it.
    check_time = _get_contended_check_time()

    assert check_time < ModuleCtx.Max_Check_Share * request_time, (check_time, request_time)

# ################################################################################################################################
# ################################################################################################################################
