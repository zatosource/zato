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
    from multiprocessing.sharedctypes import Synchronized
    from pathlib import Path

    intsync = Synchronized[int]
    Path = Path

# ################################################################################################################################
# ################################################################################################################################

# Workers are forked, as the arbiter forks them, so that they inherit the mapping and the descriptors
_context = get_context('fork')

_region_config = {
    'slot_count': 3,
    'wake_capacity': 8,
    'cell_capacity': 8,
    'queue_count': 1,
    'metric_count': 1,
    'series_capacity': 0,
    'series_key_bytes': 0,
    'dedup_capacity': 0,
    'breaker_capacity': 0,
    'lock_capacity': 0,
    'start_id': 1,
}

_queue = 0

# How many greenlets of each worker write, and how many writes each of them makes
_greenlets_per_worker = 4
_writes_per_greenlet = 10

# How long a write holds the file, in seconds
_write_time = 0.001

# How long a write waits for its turn at most, and how long the test waits for a worker, in seconds
_deadline = 20.0
_join_timeout = 60.0

# ################################################################################################################################
# ################################################################################################################################

def _write_through_call_database(
    region:'SharedRegion',
    slot:'int',
    db_path:'str',
    inside:'intsync',
    max_inside:'intsync',
    total:'intsync',
    ) -> 'None':
    """ Writes from several greenlets of one worker through call_database, counting how many writes run at once
    across all the workers.
    """
    exit_code = 1

    try:

        # The worker runs under gevent, as a server does, so call_database runs the writes in the pool of the hub,
        # whose loop and threads are its own, as the arbiter makes them for each worker that it forks ..
        from gevent import joinall, monkey, reinit, spawn
        reinit()
        _ = monkey.patch_all()

        from sqlalchemy import create_engine
        from zato.common.db_env.engine import call_database, set_process_queue
        from zato.common.db_env.process_queue import ProcessQueue

        engine = create_engine(f'sqlite:///{db_path}')

        # .. and takes turns with the other workers in the queue of the file.
        process_queue = ProcessQueue(region, _queue, slot, _deadline)
        set_process_queue(engine, process_queue)

        def write() -> 'None':
            with inside.get_lock():
                inside.value += 1
                max_inside.value = max(max_inside.value, inside.value)

            time.sleep(_write_time)

            with inside.get_lock():
                inside.value -= 1
                total.value += 1

        def write_many() -> 'None':
            for _ in range(_writes_per_greenlet):
                _ = call_database(engine, write)

        greenlets = []

        for _ in range(_greenlets_per_worker):
            greenlet = spawn(write_many)
            greenlets.append(greenlet)

        _ = joinall(greenlets, raise_error=True)
        exit_code = 0

    # The exception reaches the output of the test, since the worker exits without unwinding
    except BaseException:
        traceback.print_exc()

    finally:
        os._exit(exit_code)

# ################################################################################################################################
# ################################################################################################################################

def test_the_writes_of_call_database_take_turns_across_workers(tmp_path:'Path') -> 'None':
    region = SharedRegion(_region_config)
    slot_count = _region_config['slot_count']
    db_path = str(tmp_path / 'queued.db')

    inside = _context.Value('i', 0)
    max_inside = _context.Value('i', 0)
    total = _context.Value('i', 0)

    processes = []

    for slot in range(slot_count):
        args = (region, slot, db_path, inside, max_inside, total)
        process = _context.Process(target=_write_through_call_database, args=args)
        processes.append(process)

    for process in processes:
        process.start()

    for process in processes:
        process.join(_join_timeout)
        assert process.exitcode == 0

    expected_total = slot_count * _greenlets_per_worker * _writes_per_greenlet

    # Each write ran alone, although each worker had several greenlets writing at once
    assert max_inside.value == 1
    assert total.value == expected_total

# ################################################################################################################################
# ################################################################################################################################
