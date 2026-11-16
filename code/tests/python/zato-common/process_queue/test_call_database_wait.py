# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time
import traceback
from multiprocessing import get_context

# Zato
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.connection import Connection
    from pathlib import Path
    from zato.common.typing_ import any_

    any_ = any_
    Connection = Connection
    Path = Path

# ################################################################################################################################
# ################################################################################################################################

# The processes are forked, as the arbiter forks them, so that they inherit the mapping and the descriptors
_context = get_context('fork')

_region_config = {
    'queue_count': 1,
    'lock_capacity': 0,
}

_queue = 0

# The config process holds the turn and the worker writes
_holder_place = 1
_writer_place = 0

# How long the holder keeps the turn before it releases it, in seconds
_hold_time = 0.5

# The deadline of a write that receives its turn, and of one that does not, in seconds
_long_deadline = 20.0
_short_deadline = 0.3

# How often the other greenlet of the writer counts, in seconds, and how many counts a wait must allow at least
_tick_interval = 0.01
_ticks_min = 10

# What the write returns
_write_result = 'written'

# How long the test waits for a process to report or to exit, in seconds
_report_timeout = 20.0

# ################################################################################################################################
# ################################################################################################################################

def _hold_turn(region:'SharedRegion', conn:'Connection') -> 'None':
    """ Takes the turn of the queue and keeps it until the test asks for its release, then reports when it released it.
    """
    _ = region.queue_enter(_queue, _holder_place)

    while not region.queue_poll(_queue, _holder_place):
        time.sleep(_tick_interval)

    conn.send('holding')

    _ = conn.recv()
    released_at = time.monotonic()
    region.queue_release(_queue, _holder_place)

    conn.send(released_at)

# ################################################################################################################################

def _write_while_counting(region:'SharedRegion', db_path:'str', deadline:'float', conn:'Connection') -> 'None':
    """ Writes once through call_database while another greenlet of the worker counts at a fixed interval,
    and reports when the write ran, or the exception, with the counts made during the call.
    """
    exit_code = 1

    try:

        # The worker runs under gevent, as a server does, so call_database runs the write in the pool of the hub,
        # whose loop and threads are its own, as the arbiter makes them for each process that it forks ..
        from gevent import monkey, reinit, sleep, spawn
        reinit()
        _ = monkey.patch_all()

        from sqlalchemy import create_engine
        from zato.common.db_env.engine import call_database, set_process_queue
        from zato.common.db_env.process_queue import ProcessQueue

        engine = create_engine(f'sqlite:///{db_path}')
        process_queue = ProcessQueue(region, _queue, _writer_place, deadline)
        set_process_queue(engine, process_queue)

        # .. another greenlet counts while the write waits for its turn ..
        ticks = [0]

        def count() -> 'None':
            while True:
                sleep(_tick_interval)
                ticks[0] += 1

        _ = spawn(count)

        written_at = [0.0]

        def write() -> 'str':
            written_at[0] = time.monotonic()
            return _write_result

        # .. the call starts once the test knows the worker is about to wait ..
        conn.send('waiting')
        started_at = time.monotonic()
        ticks_before = ticks[0]

        try:
            result = call_database(engine, write)
        except Exception as exception:
            outcome = type(exception).__name__
        else:
            outcome = result

        # .. and the worker reports what the call returned, when the write ran, how long it took and the counts made.
        elapsed = time.monotonic() - started_at
        ticks_during = ticks[0] - ticks_before

        conn.send((outcome, written_at[0], elapsed, ticks_during))
        exit_code = 0

    # The exception reaches the output of the test, since the worker exits without unwinding
    except BaseException:
        traceback.print_exc()

    finally:
        os._exit(exit_code)

# ################################################################################################################################

def _start(target:'any_', args:'any_') -> 'Connection':
    parent_conn, child_conn = _context.Pipe()

    process = _context.Process(target=target, args=(*args, child_conn))
    process.daemon = True
    process.start()

    return parent_conn

# ################################################################################################################################

def _receive(conn:'Connection') -> 'any_':
    assert conn.poll(_report_timeout)
    out = conn.recv()
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_a_write_waits_for_the_turn_of_the_config_process_without_blocking_its_greenlets(tmp_path:'Path') -> 'None':
    region = SharedRegion(_region_config)
    db_path = str(tmp_path / 'waited.db')

    # The config process holds the turn of the file ..
    holder_conn = _start(_hold_turn, (region,))
    assert _receive(holder_conn) == 'holding'

    # .. the worker begins its write ..
    writer_conn = _start(_write_while_counting, (region, db_path, _long_deadline))
    assert _receive(writer_conn) == 'waiting'

    # .. the config process releases the turn after a while ..
    time.sleep(_hold_time)
    holder_conn.send('release')
    released_at = _receive(holder_conn)

    # .. the write runs only after the release ..
    outcome, written_at, _, ticks_during = _receive(writer_conn)

    assert outcome == _write_result
    assert written_at >= released_at

    # .. and the other greenlet of the worker kept running while the write waited.
    assert ticks_during >= _ticks_min

# ################################################################################################################################

def test_a_write_that_receives_no_turn_raises_at_its_deadline_without_blocking_its_greenlets(tmp_path:'Path') -> 'None':
    region = SharedRegion(_region_config)
    db_path = str(tmp_path / 'refused.db')

    # The config process holds the turn of the file throughout ..
    holder_conn = _start(_hold_turn, (region,))
    assert _receive(holder_conn) == 'holding'

    # .. so the write of the worker raises once its deadline passes, without running ..
    writer_conn = _start(_write_while_counting, (region, db_path, _short_deadline))
    assert _receive(writer_conn) == 'waiting'

    outcome, written_at, elapsed, ticks_during = _receive(writer_conn)

    assert outcome == 'ProcessQueueTimeout'
    assert written_at == 0.0
    assert elapsed >= _short_deadline

    # .. the other greenlet kept running while it waited ..
    assert ticks_during >= _ticks_min

    # .. and the write withdrew its place, so the holder's release wakes no one.
    assert not region.queue_has_place(_queue, _writer_place)

    holder_conn.send('release')
    _ = _receive(holder_conn)

# ################################################################################################################################
# ################################################################################################################################
