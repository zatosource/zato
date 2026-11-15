# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import signal
import time
from multiprocessing import get_context

# Zato
from zato_ipc_core.zato_ipc_core import RateLimitKey, SharedRegion, SharedRegionFull

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.context import ForkProcess
    from multiprocessing.synchronize import Event
    from zato.common.typing_ import callable_, list_
    from zato_ipc_core.zato_ipc_core import CellCheckResult

    callable_ = callable_
    CellCheckResult = CellCheckResult
    Event = Event
    ForkProcess = ForkProcess

    processlist = list_[ForkProcess]

# ################################################################################################################################
# ################################################################################################################################

# Workers are forked, as the arbiter forks them, so that they inherit the mapping
_context = get_context('fork')

_slot_count = 4

# The metrics through which the workers report what was allowed
_token_metric  = 0
_window_metric = 1

# The key that every worker of a test checks
_key   = 'rest.orders:10.0.0.0/8:0'
_group = 'rest.orders:10.0.0.0/8:'

# A clock reading that every request of a test shares, so that no bucket refills during the test
_now_us = 1_800_000_000_000_000

# A window that ends long after any test
_window_end_us = _now_us + 86_400_000_000

# The requests of each worker, and the burst and the limit that the workers together exhaust
_requests_per_worker = 10_000
_contended_burst     = 15_000
_contended_limit     = 25_000

# The rate of a bucket that does not refill within a test, in tokens per second
_slow_rate = 1

# The rate and the burst of the bucket that refills during a test, and how long its workers make requests, in seconds
_refill_rate  = 2_000
_refill_burst = 50
_refill_duration = 1.0

# A window limit that no worker reaches before it is terminated
_unreached_limit = 1 << 30

# When each worker is terminated after the start, in seconds
_kill_delays = [0.05, 0.08, 0.11, 0.14]

# The cells of the claim test, and the pause of its workers between two claims, in seconds
_claim_capacity = 1 << 16
_claim_pause = 0.0001

# How long a test waits for a worker to exit, in seconds
_join_timeout = 20

# Microseconds and nanoseconds in one second
_micros_per_second = 1_000_000
_nanos_per_micro = 1_000

# ################################################################################################################################
# ################################################################################################################################

def _new_region(cell_capacity:'int'=64) -> 'SharedRegion':
    config = {
        'slot_count': _slot_count,
        'wake_capacity': 8,
        'cell_capacity': cell_capacity,
        'queue_count': 1,
        'metric_count': _slot_count,
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

def _start_workers(region:'SharedRegion', target:'callable_', start:'Event') -> 'processlist':
    """ Forks one worker per slot, each of which waits for the start event before its first request.
    """
    out:'processlist' = []

    for slot in range(_slot_count):
        process = _context.Process(target=target, args=(region, slot, start))
        process.start()
        out.append(process)

    return out

# ################################################################################################################################

def _join_workers(processes:'processlist', exit_code:'int') -> 'None':
    for process in processes:
        process.join(_join_timeout)
        assert process.exitcode == exit_code

# ################################################################################################################################

def _kill_workers(processes:'processlist') -> 'None':
    """ Terminates each worker with SIGKILL at its own delay after the start.
    """
    started_at = time.monotonic()

    for process, delay in zip(processes, _kill_delays):
        kill_at = started_at + delay
        wait = kill_at - time.monotonic()

        if wait > 0:
            time.sleep(wait)

        process.kill()

    _join_workers(processes, -signal.SIGKILL)

# ################################################################################################################################

def _get_now_us() -> 'int':
    out = time.time_ns() // _nanos_per_micro
    return out

# ################################################################################################################################
# ################################################################################################################################

def _check_at_one_instant(region:'SharedRegion', slot:'int', start:'Event') -> 'None':
    """ Makes the requests of one worker against a bucket and a window, all with the same clock reading.
    """
    key = RateLimitKey(_key, _group)
    _ = start.wait()

    for _ in range(_requests_per_worker):
        if region.token_bucket_check(key, _slow_rate, _contended_burst, _now_us).is_allowed:
            region.metric_add(slot, _token_metric, 1)

        if region.fixed_window_check(key, _contended_limit, _window_end_us, _now_us).is_allowed:
            region.metric_add(slot, _window_metric, 1)

# ################################################################################################################################

def _check_while_refilling(region:'SharedRegion', slot:'int', start:'Event') -> 'None':
    """ Makes requests against a bucket that refills, with the clock of the moment of each request.
    """
    key = RateLimitKey(_key, _group)
    _ = start.wait()

    deadline = time.monotonic() + _refill_duration

    while time.monotonic() < deadline:
        now_us = _get_now_us()

        if region.token_bucket_check(key, _refill_rate, _refill_burst, now_us).is_allowed:
            region.metric_add(slot, _token_metric, 1)

# ################################################################################################################################

def _check_until_killed(region:'SharedRegion', slot:'int', start:'Event') -> 'None':
    """ Counts requests in one window and reports each allowed one, until the worker is terminated.
    """
    key = RateLimitKey(_key, _group)
    _ = start.wait()

    while True:
        if region.fixed_window_check(key, _unreached_limit, _window_end_us, _now_us).is_allowed:
            region.metric_add(slot, _window_metric, 1)

# ################################################################################################################################

def _claim_until_killed(region:'SharedRegion', slot:'int', start:'Event') -> 'None':
    """ Claims a cell for one new key after another and reports each claim, until the worker is terminated.
    """
    _ = start.wait()
    index = 0

    while True:
        key = RateLimitKey(f'{slot}.{index}', f'{slot}.')
        _ = region.fixed_window_check(key, _unreached_limit, _window_end_us, _now_us)

        # Each worker reports its claims through the metric of its own slot.
        region.metric_add(slot, slot, 1)
        index += 1

        time.sleep(_claim_pause)

# ################################################################################################################################

def _check_claimed_key(region:'SharedRegion', slot:'int', index:'int') -> 'CellCheckResult':
    key = RateLimitKey(f'{slot}.{index}', f'{slot}.')
    out = region.fixed_window_check(key, _unreached_limit, _window_end_us, _now_us)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_forked_workers_take_each_token_and_each_request_of_a_window_once() -> 'None':
    region = _new_region()
    start = _context.Event()

    # Every worker makes its requests at the same moment ..
    processes = _start_workers(region, _check_at_one_instant, start)
    start.set()

    _join_workers(processes, 0)

    # .. and together they are allowed the burst and the limit exactly.
    assert region.metric_sum(_token_metric) == _contended_burst
    assert region.metric_sum(_window_metric) == _contended_limit

# ################################################################################################################################

def test_forked_workers_are_allowed_no_more_than_the_burst_and_the_refill() -> 'None':
    region = _new_region()
    start = _context.Event()

    processes = _start_workers(region, _check_while_refilling, start)

    # Every request is made between these two clock readings ..
    started_us = _get_now_us()
    start.set()

    _join_workers(processes, 0)
    ended_us = _get_now_us()

    # .. so the workers together are allowed at most the burst and the tokens refilled in between ..
    elapsed_us = ended_us - started_us
    refilled = _refill_rate * elapsed_us // _micros_per_second
    allowed = region.metric_sum(_token_metric)

    assert allowed <= _refill_burst + refilled

    # .. and the refill is counted.
    assert allowed > _refill_burst

# ################################################################################################################################

def test_workers_killed_during_their_checks_leave_the_count_of_a_window_consistent() -> 'None':
    region = _new_region()
    start = _context.Event()

    # Each worker is terminated at an arbitrary instruction of a check or of its report ..
    processes = _start_workers(region, _check_until_killed, start)
    start.set()

    _kill_workers(processes)

    # .. the window counted each reported request, and at most one more for each terminated worker ..
    key = RateLimitKey(_key, _group)
    check = region.fixed_window_check(key, _unreached_limit, _window_end_us, _now_us)

    counted = _unreached_limit - check.remaining - 1
    reported = region.metric_sum(_window_metric)

    assert reported <= counted <= reported + _slot_count

    # .. and the region keeps its header.
    region.verify()

# ################################################################################################################################

def test_workers_killed_while_they_claim_cells_lose_no_cell() -> 'None':
    region = _new_region(_claim_capacity)
    start = _context.Event()

    # Each worker is terminated while it claims cells for new keys ..
    processes = _start_workers(region, _claim_until_killed, start)
    start.set()

    _kill_workers(processes)

    # .. every reported key keeps the request its worker counted, and the key after the last reported one
    # has a cell with no request or with the one request of a worker terminated before its report ..
    claimed = 0

    for slot in range(_slot_count):
        reported = region.metric_sum(slot)

        for index in range(reported):
            check = _check_claimed_key(region, slot, index)
            assert check.remaining == _unreached_limit - 2

        check = _check_claimed_key(region, slot, reported)
        assert check.remaining in (_unreached_limit - 1, _unreached_limit - 2)

        claimed += reported + 1

    # .. and every other cell is free for a new key, so no claim took a cell without a key or a second cell.
    free = 0

    while True:
        key = RateLimitKey(f'free.{free}', 'free.')

        try:
            _ = region.fixed_window_check(key, _unreached_limit, _window_end_us, _now_us)
        except SharedRegionFull:
            break

        free += 1

    assert claimed + free == _claim_capacity

# ################################################################################################################################
# ################################################################################################################################
