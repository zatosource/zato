# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from multiprocessing import get_context

# Zato
from zato.common.ext.bunch import Bunch
from zato.common.hl7.mllp.circuit_breaker import CircuitBreaker
from zato.common.hl7.mllp.dedup import Default_Max_Entries, MessageDeduplicator
from zato.common.hl7.mllp.region import bind_mllp, get_worker_pool_size
from zato.common.hl7.mllp.settings import RouteSettings
from zato.common.typing_ import cast_
from zato.server.generic.api.outconn_hl7_mllp import OutconnHL7MLLPWrapper
from zato_ipc_core.zato_ipc_core import BREAKER_CLOSED, BREAKER_HALF_OPEN, BREAKER_OPEN, SharedRegion, STATE_READY

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.queues import SimpleQueue
    from multiprocessing.synchronize import Barrier, Event
    from zato.common.typing_ import any_, anylist, anytuple, callable_
    from zato.server.base.parallel import ParallelServer

    any_ = any_
    anylist = anylist
    Barrier = Barrier
    anytuple = anytuple
    callable_ = callable_
    Event = Event
    ParallelServer = ParallelServer
    SimpleQueue = SimpleQueue

# ################################################################################################################################
# ################################################################################################################################

_context = get_context('fork')

# How long the test waits for a process, in seconds
_join_timeout = 60.0

_slot_count = 4

_channel_name = 'hl7.orders'
_other_channel_name = 'hl7.results'
_control_id = 'MSG-00001'

# The deduplication window of the tests, in seconds
_dedup_ttl_seconds = 3600.0

_connection_key = '101'
_threshold_percent = 50
_window_seconds = 60.0

# The reset period of the breakers of the tests, in seconds
_reset_seconds = 0.2

# ################################################################################################################################
# ################################################################################################################################

def _new_region() -> 'SharedRegion':
    """ Returns the region of a server whose every slot has a worker that is ready.
    """
    region = SharedRegion({
        'slot_count': _slot_count,
        'wake_capacity': 0,
        'cell_capacity': 0,
        'queue_count': 0,
        'metric_count': 0,
        'series_capacity': 0,
        'series_key_bytes': 0,
        'dedup_capacity': 64,
        'breaker_capacity': 8,
        'lock_capacity': 0,
        'start_id': 1,
    })

    for slot in range(_slot_count):
        _ = region.next_slot_generation(slot)
        region.set_slot_state(slot, STATE_READY)

    return region

# ################################################################################################################################

def _bind(region:'SharedRegion', slot:'int') -> 'None':
    bind_mllp(region, slot, region.slot_generation(slot))

# ################################################################################################################################

def _run_in_child(target:'callable_', args:'anytuple') -> 'anylist':
    """ Runs a function in a forked process and returns what it put in its queue.
    """
    results:'SimpleQueue' = _context.SimpleQueue()

    process = _context.Process(target=target, args=(results, *args))
    process.start()
    process.join(_join_timeout)

    assert process.exitcode == 0

    out:'anylist' = []

    while not results.empty():
        out.append(results.get())

    return out

# ################################################################################################################################

def _new_breaker() -> 'CircuitBreaker':
    out = CircuitBreaker(_threshold_percent, _window_seconds, _reset_seconds, _connection_key)
    return out

# ################################################################################################################################
# ################################################################################################################################


# ################################################################################################################################
# ################################################################################################################################

def _receive(results:'SimpleQueue', region:'SharedRegion | None', slot:'int', channel_name:'str') -> 'None':
    """ Receives the control ID on a channel, in a worker bound to its slot or in a process without an arbiter.
    """
    if region:
        _bind(region, slot)

    deduplicator = MessageDeduplicator(_dedup_ttl_seconds, Default_Max_Entries, channel_name)
    results.put(deduplicator.is_duplicate(_control_id))

# ################################################################################################################################

def test_a_retransmission_received_by_another_worker_is_a_duplicate() -> 'None':
    region = _new_region()

    # The first worker receives the message, and the second worker receives its retransmission ..
    assert _run_in_child(_receive, (region, 1, _channel_name)) == [False]
    assert _run_in_child(_receive, (region, 2, _channel_name)) == [True]

    # .. while the same control ID on another channel is a message of its own.
    assert _run_in_child(_receive, (region, 2, _other_channel_name)) == [False]

# ################################################################################################################################

def test_processes_without_an_arbiter_keep_their_own_control_ids() -> 'None':
    assert _run_in_child(_receive, (None, 0, _channel_name)) == [False]
    assert _run_in_child(_receive, (None, 0, _channel_name)) == [False]

# ################################################################################################################################

def _receive_through_route_settings(results:'SimpleQueue', region:'SharedRegion', slot:'int') -> 'None':
    _bind(region, slot)

    route_settings = RouteSettings(dedup_ttl_value=1, dedup_ttl_unit='hours', channel_name=_channel_name)
    deduplicator = route_settings.deduplicator

    assert deduplicator is not None
    results.put(deduplicator.is_duplicate(_control_id))

# ################################################################################################################################

def test_the_settings_of_a_channel_keep_its_control_ids_under_its_name() -> 'None':
    region = _new_region()

    assert _run_in_child(_receive, (region, 1, _channel_name)) == [False]
    assert _run_in_child(_receive_through_route_settings, (region, 2)) == [True]

# ################################################################################################################################

class _BusyRegion:
    """ A region whose table of control IDs another worker holds for the first checks.
    """
    def __init__(self, busy_count:'int') -> 'None':
        self.busy_count = busy_count
        self.check_count = 0

    def dedup_check(self, *_args:'any_') -> 'bool | None':
        self.check_count += 1

        if self.check_count <= self.busy_count:
            return None

        return False

# ################################################################################################################################

def _receive_while_busy(results:'SimpleQueue', busy_count:'int') -> 'None':
    busy_region = _BusyRegion(busy_count)
    bind_mllp(cast_('SharedRegion', busy_region), 0, 1)

    deduplicator = MessageDeduplicator(_dedup_ttl_seconds, Default_Max_Entries, _channel_name)

    results.put(deduplicator.is_duplicate(_control_id))
    results.put(busy_region.check_count)

# ################################################################################################################################

def test_a_check_waits_while_another_worker_holds_the_table() -> 'None':
    busy_count = 3
    assert _run_in_child(_receive_while_busy, (busy_count,)) == [False, busy_count + 1]

# ################################################################################################################################
# ################################################################################################################################

def _fail_sends(results:'SimpleQueue', region:'SharedRegion', slot:'int', outcomes:'str') -> 'None':
    """ Records the outcomes of sends, S for a success and F for a failure, in the order given.
    """
    _bind(region, slot)
    breaker = _new_breaker()

    for outcome in outcomes:
        if outcome == 'S':
            breaker.record_success()
        else:
            breaker.record_failure()

    results.put(region.breaker_state(_connection_key)[0])

# ################################################################################################################################

def _ask_to_send(results:'SimpleQueue', region:'SharedRegion', slot:'int') -> 'None':
    _bind(region, slot)
    breaker = _new_breaker()

    results.put(breaker.can_execute())

# ################################################################################################################################

def _ask_together(results:'SimpleQueue', region:'SharedRegion', slot:'int', asked:'Barrier', trial_outcome:'str') -> 'None':
    """ Asks to send together with the other workers, and concludes the trial message, if this worker sends it,
    once every worker has asked.
    """
    _bind(region, slot)
    breaker = _new_breaker()

    _ = asked.wait(_join_timeout)
    can_execute = breaker.can_execute()
    _ = asked.wait(_join_timeout)

    if can_execute:
        if trial_outcome == 'S':
            breaker.record_success()
        else:
            breaker.record_failure()

    results.put(can_execute)

# ################################################################################################################################

def _send_trial_from_every_worker(region:'SharedRegion', trial_outcome:'str') -> 'int':
    """ Lets every worker ask to send at once after the reset period, returning how many sent the trial message.
    """
    time.sleep(_reset_seconds)

    asked = _context.Barrier(_slot_count)
    results:'SimpleQueue' = _context.SimpleQueue()

    processes = [
        _context.Process(target=_ask_together, args=(results, region, slot, asked, trial_outcome))
        for slot in range(_slot_count)
    ]

    for process in processes:
        process.start()

    for process in processes:
        process.join(_join_timeout)
        assert process.exitcode == 0

    out = 0

    while not results.empty():
        if results.get():
            out += 1

    return out

# ################################################################################################################################

def test_the_breaker_opened_by_one_worker_stops_every_worker_and_one_trial_goes_out() -> 'None':
    region = _new_region()

    # The failures of one worker open the breaker ..
    assert _run_in_child(_fail_sends, (region, 1, 'FF')) == [BREAKER_OPEN]

    # .. which stops another worker before the reset period is over ..
    assert _run_in_child(_ask_to_send, (region, 2)) == [False]

    # .. after which one worker of all sends the trial message, whose success closes the breaker of every worker.
    assert _send_trial_from_every_worker(region, 'S') == 1
    assert region.breaker_state(_connection_key)[0] == BREAKER_CLOSED
    assert _run_in_child(_ask_to_send, (region, 2)) == [True]

# ################################################################################################################################

def test_a_failed_trial_opens_the_breaker_of_every_worker_again() -> 'None':
    region = _new_region()

    assert _run_in_child(_fail_sends, (region, 1, 'FF')) == [BREAKER_OPEN]
    assert _send_trial_from_every_worker(region, 'F') == 1

    assert region.breaker_state(_connection_key)[0] == BREAKER_OPEN
    assert _run_in_child(_ask_to_send, (region, 3)) == [False]

# ################################################################################################################################

def test_the_trial_of_another_worker_stops_this_one() -> 'None':
    region = _new_region()

    assert _run_in_child(_fail_sends, (region, 1, 'FF')) == [BREAKER_OPEN]
    time.sleep(_reset_seconds)

    # The first worker that asks sends the trial message, which has no outcome yet when the next one asks
    assert _run_in_child(_ask_to_send, (region, 1)) == [True]
    assert region.breaker_state(_connection_key)[0] == BREAKER_HALF_OPEN
    assert _run_in_child(_ask_to_send, (region, 2)) == [False]

# ################################################################################################################################

def _fail_after_reopening(results:'SimpleQueue', region:'SharedRegion', start_open:'Event', start_closed:'Event') -> 'None':
    """ A worker whose window holds more successes than failures sees the breaker open and closed by others,
    and then one of its sends fails.
    """
    _bind(region, 2)
    breaker = _new_breaker()

    for _ in range(3):
        breaker.record_success()

    breaker.record_failure()

    _ = start_open.wait(_join_timeout)
    results.put(breaker.can_execute())

    _ = start_closed.wait(_join_timeout)
    results.put(breaker.can_execute())

    breaker.record_failure()
    results.put(region.breaker_state(_connection_key)[0])

# ################################################################################################################################

def test_a_worker_starts_its_window_anew_once_the_trial_of_another_worker_closes_the_breaker() -> 'None':
    region = _new_region()
    start_open = _context.Event()
    start_closed = _context.Event()
    results:'SimpleQueue' = _context.SimpleQueue()

    process = _context.Process(target=_fail_after_reopening, args=(results, region, start_open, start_closed))
    process.start()

    # The window of the worker holds one failure of four sends, below the threshold, when another worker opens the breaker ..
    assert _run_in_child(_fail_sends, (region, 1, 'FF')) == [BREAKER_OPEN]
    start_open.set()

    # .. whose trial message then closes it ..
    assert _send_trial_from_every_worker(region, 'S') == 1
    start_closed.set()

    process.join(_join_timeout)
    assert process.exitcode == 0

    # .. and the next failure of the worker is the only outcome of its window, as after a successful trial in one process.
    assert results.get() is False
    assert results.get() is True
    assert results.get() == BREAKER_OPEN

# ################################################################################################################################
# ################################################################################################################################

def _get_pool_sizes(results:'SimpleQueue', region:'SharedRegion | None') -> 'None':
    if region:
        _bind(region, 0)

    results.put([get_worker_pool_size(pool_size) for pool_size in (10, 4, 3, 1)])

# ################################################################################################################################

def test_each_worker_keeps_its_share_of_the_pool_and_at_least_one_connection() -> 'None':
    region = _new_region()

    assert _run_in_child(_get_pool_sizes, (region,)) == [[2, 1, 1, 1]]
    assert _run_in_child(_get_pool_sizes, (None,)) == [[10, 4, 3, 1]]

# ################################################################################################################################

def _build_wrapper(results:'SimpleQueue', region:'SharedRegion') -> 'None':
    """ Builds the wrapper of an outgoing connection, without connecting, in a worker bound to its slot.
    """
    _bind(region, 0)

    config = Bunch({
        'id': 101,
        'name': 'Lab results',
        'address': '127.0.0.1:2575',
        'username': None,
        'is_active': False,
        'pool_size': 8,
        'queue_build_cap': 30,
        'is_audit_log_active': False,
        'use_queue': False,
        'circuit_breaker_threshold_percent': _threshold_percent,
        'circuit_breaker_window_seconds': _window_seconds,
        'circuit_breaker_reset_seconds': _reset_seconds,
    })

    wrapper = OutconnHL7MLLPWrapper(config, cast_('ParallelServer', None))

    results.put(wrapper.client.queue_max_size)
    results.put(wrapper.breaker.key)

# ################################################################################################################################

def test_the_wrapper_of_an_outgoing_connection_uses_the_share_of_its_worker_and_the_breaker_of_its_id() -> 'None':
    region = _new_region()
    assert _run_in_child(_build_wrapper, (region,)) == [8 // _slot_count, _connection_key]

# ################################################################################################################################
# ################################################################################################################################
