# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from multiprocessing import get_context

# pytest
import pytest

# Zato
from zato.common import log_streaming
from zato.common.log_streaming import _state, bind_log_streaming, LogStreamingManager, ModuleCtx as StreamingCtx
from zato_ipc_core.zato_ipc_core import FLAG_LOG_STREAMING, SharedRegion, STATE_READY

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.queues import SimpleQueue
    from zato.common.typing_ import anylist, anytuple, callable_, generator_

    anylist = anylist
    anytuple = anytuple
    callable_ = callable_
    SimpleQueue = SimpleQueue

    nonegen = generator_[None, None, None]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Slot_Count = 2

    # The loggers of the two workers that the tests run in this process
    First_Logger_Name = 'test.log_streaming.first'
    Second_Logger_Name = 'test.log_streaming.second'

    # How long the test waits for a process, in seconds
    Join_Timeout = 60.0

_context = get_context('fork')

_apply_event = {StreamingCtx.Key_Action: StreamingCtx.Action_Apply_Streaming}

# ################################################################################################################################
# ################################################################################################################################

class FakeRedisHandler(logging.Handler):
    """ A handler that discards the records of the logger, in place of the one that writes them to Redis.
    """
    def __init__(self, channel:'str') -> 'None':
        super().__init__()
        self.channel = channel

    def emit(self, record:'logging.LogRecord') -> 'None':
        pass

# ################################################################################################################################

@pytest.fixture(autouse=True)
def streaming(monkeypatch:'pytest.MonkeyPatch') -> 'nonegen':
    """ Replaces the handler that writes to Redis and the loggers that every manager streams,
    and leaves the process unbound after the test.
    """
    monkeypatch.setattr(log_streaming, 'RedisHandler', FakeRedisHandler)
    monkeypatch.setattr(LogStreamingManager, 'loggers_to_stream', set())

    yield

    _state.binding = None

    for logger_name in (ModuleCtx.First_Logger_Name, ModuleCtx.Second_Logger_Name):
        logging.getLogger(logger_name).handlers.clear()

# ################################################################################################################################

def _new_region() -> 'SharedRegion':
    out = SharedRegion({
        'slot_count': ModuleCtx.Slot_Count,
        'wake_capacity': 0,
        'cell_capacity': 0,
        'queue_count': 0,
        'metric_count': 0,
        'series_capacity': 0,
        'series_key_bytes': 0,
        'dedup_capacity': 0,
        'breaker_capacity': 0,
        'lock_capacity': 0,
        'start_id': 1,
    })

    for slot in range(ModuleCtx.Slot_Count):
        _ = out.next_slot_generation(slot)
        out.set_slot_state(slot, STATE_READY)

    return out

# ################################################################################################################################

def _bind(region:'SharedRegion') -> 'anylist':
    """ Binds this process to the region and returns the list to which it publishes its events.
    """
    out:'anylist' = []
    bind_log_streaming(region, out.append)

    return out

# ################################################################################################################################

def _run_in_child(target:'callable_', args:'anytuple') -> 'anylist':
    """ Runs a function in a forked process and returns what it put in its queue.
    """
    results:'SimpleQueue' = _context.SimpleQueue()

    process = _context.Process(target=target, args=(results, *args))
    process.start()
    process.join(ModuleCtx.Join_Timeout)

    assert process.exitcode == 0

    out:'anylist' = []

    while not results.empty():
        out.append(results.get())

    return out

# ################################################################################################################################

def _has_handler(manager:'LogStreamingManager') -> 'bool':
    out = manager.get_redis_handler() in manager.logger.handlers
    return out

# ################################################################################################################################
# ################################################################################################################################


# ################################################################################################################################

def _toggle(results:'SimpleQueue', region:'SharedRegion') -> 'None':
    published = _bind(region)
    manager = LogStreamingManager(ModuleCtx.First_Logger_Name)

    results.put((manager.toggle_streaming(), _has_handler(manager), published))

# ################################################################################################################################

def _start_and_report(results:'SimpleQueue', region:'SharedRegion') -> 'None':
    """ Starts a worker, which applies the flag before it reports ready, and reports the status of log streaming.
    """
    _ = _bind(region)
    manager = LogStreamingManager(ModuleCtx.Second_Logger_Name)

    is_enabled_before_start = manager.is_streaming_enabled()
    manager.apply_streaming()

    results.put((is_enabled_before_start, _has_handler(manager)))

# ################################################################################################################################

def test_a_toggle_in_one_worker_is_the_status_of_every_worker() -> 'None':
    region = _new_region()

    # One worker turns streaming on and tells the other workers to apply it ..
    [(is_enabled, has_handler, published)] = _run_in_child(_toggle, (region,))

    assert is_enabled
    assert has_handler
    assert published == [_apply_event]

    # .. and another worker reports it on, and adds its own handler when it starts.
    assert _run_in_child(_start_and_report, (region,)) == [(True, True)]
    assert region.flag_is_set(FLAG_LOG_STREAMING)

# ################################################################################################################################

def test_the_event_makes_another_worker_follow_the_flag() -> 'None':
    region = _new_region()
    published = _bind(region)

    first = LogStreamingManager(ModuleCtx.First_Logger_Name)
    second = LogStreamingManager(ModuleCtx.Second_Logger_Name)

    # The first worker turns streaming on, and the second one adds its handler once the event reaches it ..
    assert first.toggle_streaming()
    assert not _has_handler(second)
    assert second.is_streaming_enabled()

    second.apply_streaming()
    assert _has_handler(second)

    # .. and the same for turning it off.
    assert not first.toggle_streaming()
    assert _has_handler(second)
    assert not second.is_streaming_enabled()

    second.apply_streaming()
    assert not _has_handler(second)

    assert published == [_apply_event, _apply_event]

# ################################################################################################################################

def test_crossing_toggles_leave_every_worker_as_the_flag_states() -> 'None':
    region = _new_region()
    _ = _bind(region)

    first = LogStreamingManager(ModuleCtx.First_Logger_Name)
    second = LogStreamingManager(ModuleCtx.Second_Logger_Name)

    # The first worker turns streaming on and the second one turns it off before the event of the first one reaches it ..
    assert first.toggle_streaming()
    assert not second.toggle_streaming()

    # .. and once each event reaches the other worker, neither of them streams, as the flag states.
    second.apply_streaming()
    first.apply_streaming()

    assert not region.flag_is_set(FLAG_LOG_STREAMING)
    assert not _has_handler(first)
    assert not _has_handler(second)

# ################################################################################################################################

def test_a_process_that_no_arbiter_started_toggles_its_own_handler() -> 'None':
    manager = LogStreamingManager(ModuleCtx.First_Logger_Name)

    assert manager.toggle_streaming()
    assert manager.is_streaming_enabled()
    assert _has_handler(manager)

    assert not manager.toggle_streaming()
    assert not manager.is_streaming_enabled()

# ################################################################################################################################
# ################################################################################################################################
