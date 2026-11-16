# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import threading
import time
from multiprocessing import get_context

# pytest
import pytest

# Zato
from zato.common.db_env.process_queue import get_deadline_seconds, ProcessQueue, ProcessQueueTimeout
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.connection import Connection
    from multiprocessing.sharedctypes import Synchronized

    Connection = Connection
    intsync = Synchronized[int]

# ################################################################################################################################
# ################################################################################################################################

# The processes are forked, as the arbiter forks them, so that they inherit the mapping and the descriptors
_context = get_context('fork')

_region_config = {
    'queue_count': 2,
    'lock_capacity': 0,
}

# The places of the worker and of the config process
_worker_place = 0
_config_place = 1
_places = (_worker_place, _config_place)

# The queues of two SQLite files
_first_queue = 0
_second_queue = 1

# How long a test waits for a write at most, in seconds
_long_deadline = 20.0

# The deadline of a write that is expected to run out, in seconds
_short_deadline = 0.3

# How many writes each process of the overlap test makes
_writes_per_process = 50

# How long a write of the overlap test holds the turn, in seconds
_write_time = 0.001

# How long a test waits for a process to report, in seconds
_report_timeout = 20

# A wake-up arrives well within this period when the turn is released, in seconds
_prompt_wake_up = 2.0

# How often a test reads the record of a place while it waits for its process to take it, in seconds
_place_check_interval = 0.01

# ################################################################################################################################
# ################################################################################################################################

def _new_region() -> 'SharedRegion':
    out = SharedRegion(_region_config)
    return out

# ################################################################################################################################

def _hold_until_told(conn:'Connection') -> 'None':
    """ A write that reports that it holds the turn and keeps it until the parent says otherwise.
    """
    conn.send('holding')
    _ = conn.recv()

# ################################################################################################################################

def _run_holder(region:'SharedRegion', queue:'int', place:'int', conn:'Connection') -> 'None':
    process_queue = ProcessQueue(region, queue, place, _long_deadline)
    _ = process_queue.run(_hold_until_told, (conn,))

# ################################################################################################################################

def _report_write(conn:'Connection', place:'int', sequence:'intsync') -> 'None':
    """ A write that takes the next position of a sequence the writers of a test share, and reports it.
    """
    with sequence.get_lock():
        sequence.value += 1
        position = sequence.value

    conn.send(f'wrote {place} at {position}')

# ################################################################################################################################

def _run_one_write(
    region:'SharedRegion',
    queue:'int',
    place:'int',
    deadline:'float',
    sequence:'intsync',
    conn:'Connection',
    ) -> 'None':
    """ Makes one write, reporting the moment of entry and then the outcome.
    """
    process_queue = ProcessQueue(region, queue, place, deadline)
    conn.send('entering')

    try:
        _ = process_queue.run(_report_write, (conn, place, sequence))
    except ProcessQueueTimeout:
        conn.send(f'timeout {place}')

# ################################################################################################################################

def _wait_for_ticket(region:'SharedRegion', queue:'int', place:'int', conn:'Connection') -> 'None':
    """ Waits until the child behind a connection has taken its place, which its record of the queue shows.
    """
    assert conn.poll(_report_timeout)
    assert conn.recv() == 'entering'

    _wait_for_place(region, queue, place)

# ################################################################################################################################

def _wait_for_place(region:'SharedRegion', queue:'int', place:'int') -> 'None':
    """ Waits until a place in a queue is taken, which the child of the place takes right after it reports.
    """
    now = time.monotonic()
    deadline = now + _report_timeout

    while not region.queue_has_place(queue, place):
        assert time.monotonic() < deadline
        time.sleep(_place_check_interval)

# ################################################################################################################################

def _overlap_writer(
    region:'SharedRegion',
    place:'int',
    inside:'intsync',
    max_inside:'intsync',
    total:'intsync',
    ) -> 'None':
    """ Makes its writes in the queue, counting how many writers are inside at once.
    """
    process_queue = ProcessQueue(region, _first_queue, place, _long_deadline)

    def write() -> 'None':
        with inside.get_lock():
            inside.value += 1
            max_inside.value = max(max_inside.value, inside.value)

        time.sleep(_write_time)

        with inside.get_lock():
            inside.value -= 1
            total.value += 1

    for _ in range(_writes_per_process):
        _ = process_queue.run(write, ())

# ################################################################################################################################
# ################################################################################################################################

def test_the_deadline_is_a_number_of_busy_timeouts() -> 'None':
    assert get_deadline_seconds(5000) == 10.0

# ################################################################################################################################

def test_writes_of_the_worker_and_the_config_process_never_overlap() -> 'None':
    region = _new_region()

    inside = _context.Value('i', 0)
    max_inside = _context.Value('i', 0)
    total = _context.Value('i', 0)

    processes = []

    for place in _places:
        args = (region, place, inside, max_inside, total)
        process = _context.Process(target=_overlap_writer, args=args)
        processes.append(process)

    for process in processes:
        process.start()

    join_timeout = _report_timeout * len(_places)

    for process in processes:
        process.join(join_timeout)
        assert process.exitcode == 0

    expected_total = _writes_per_process * len(_places)

    assert max_inside.value == 1
    assert total.value == expected_total

# ################################################################################################################################

def test_a_write_withdraws_its_place_after_the_deadline() -> 'None':
    region = _new_region()

    # The worker holds the turn ..
    holder_conn, holder_child = _context.Pipe()
    holder = _context.Process(target=_run_holder, args=(region, _first_queue, _worker_place, holder_child))
    holder.start()
    assert holder_conn.poll(_report_timeout)
    assert holder_conn.recv() == 'holding'

    # .. a write of the config process waits past its deadline, which withdraws its place ..
    sequence = _context.Value('i', 0)

    conn, child = _context.Pipe()
    args = (region, _first_queue, _config_place, _short_deadline, sequence, child)
    writer = _context.Process(target=_run_one_write, args=args)
    writer.start()

    assert conn.poll(_report_timeout)
    assert conn.recv() == 'entering'
    assert conn.poll(_report_timeout)
    assert conn.recv() == f'timeout {_config_place}'
    writer.join(_report_timeout)

    assert not region.queue_has_place(_first_queue, _config_place)

    # .. its next write enters again ..
    conn, child = _context.Pipe()
    args = (region, _first_queue, _config_place, _long_deadline, sequence, child)
    writer = _context.Process(target=_run_one_write, args=args)
    writer.start()
    _wait_for_ticket(region, _first_queue, _config_place, conn)

    # .. and it runs promptly once the holder releases the turn.
    holder_conn.send('release')
    holder.join(_report_timeout)

    assert conn.poll(_prompt_wake_up)
    assert conn.recv() == f'wrote {_config_place} at 1'
    writer.join(_report_timeout)

# ################################################################################################################################

def test_a_terminated_holder_is_removed_by_the_arbiter() -> 'None':
    region = _new_region()

    # The worker holds the turn ..
    holder_conn, holder_child = _context.Pipe()
    holder = _context.Process(target=_run_holder, args=(region, _first_queue, _worker_place, holder_child))
    holder.start()
    assert holder_conn.poll(_report_timeout)
    assert holder_conn.recv() == 'holding'

    # .. a write of the config process waits ..
    sequence = _context.Value('i', 0)

    conn, child = _context.Pipe()
    args = (region, _first_queue, _config_place, _long_deadline, sequence, child)
    writer = _context.Process(target=_run_one_write, args=args)
    writer.start()
    _wait_for_ticket(region, _first_queue, _config_place, conn)

    # .. the holder is terminated with SIGKILL while it holds the turn ..
    holder.kill()
    holder.join(_report_timeout)

    # .. the arbiter withdraws its place ..
    region.queue_abandon(_first_queue, _worker_place)

    # .. and the write of the config process runs promptly.
    assert conn.poll(_prompt_wake_up)
    assert conn.recv() == f'wrote {_config_place} at 1'
    writer.join(_report_timeout)

# ################################################################################################################################

def _wait_in_both_queues(region:'SharedRegion', conn:'Connection') -> 'None':
    """ Waits in two queues at once from two threads of the config process, as the writes to two SQLite files do.
    """
    results = []
    threads = []

    def write(queue:'int') -> 'None':
        process_queue = ProcessQueue(region, queue, _config_place, _long_deadline)
        result = process_queue.run(time.monotonic, ())
        results.append(result)

    for queue in (_first_queue, _second_queue):
        thread = threading.Thread(target=write, args=(queue,))
        threads.append(thread)

    for thread in threads:
        thread.start()

    conn.send('entering')

    for thread in threads:
        thread.join()

    conn.send(len(results))

# ################################################################################################################################

def _hold_both_queues(region:'SharedRegion', conn:'Connection') -> 'None':
    first = ProcessQueue(region, _first_queue, _worker_place, _long_deadline)
    second = ProcessQueue(region, _second_queue, _worker_place, _long_deadline)

    def hold_second() -> 'None':
        _ = second.run(_hold_until_told, (conn,))

    _ = first.run(hold_second, ())

# ################################################################################################################################

def test_two_queues_of_one_process_keep_their_own_wake_ups() -> 'None':
    region = _new_region()

    # The worker holds the turns of both queues ..
    holder_conn, holder_child = _context.Pipe()
    holder = _context.Process(target=_hold_both_queues, args=(region, holder_child))
    holder.start()
    assert holder_conn.poll(_report_timeout)
    assert holder_conn.recv() == 'holding'

    # .. the config process waits in both, from two threads ..
    conn, child = _context.Pipe()
    waiter = _context.Process(target=_wait_in_both_queues, args=(region, child))
    waiter.start()
    assert conn.poll(_report_timeout)
    assert conn.recv() == 'entering'

    for queue in (_first_queue, _second_queue):
        _wait_for_place(region, queue, _config_place)

    # .. both turns are released ..
    holder_conn.send('release')
    holder.join(_report_timeout)

    # .. and each waiting thread receives the wake-up of its own queue.
    assert conn.poll(_prompt_wake_up)
    assert conn.recv() == 2
    waiter.join(_report_timeout)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = pytest.main([__file__])

# ################################################################################################################################
# ################################################################################################################################
