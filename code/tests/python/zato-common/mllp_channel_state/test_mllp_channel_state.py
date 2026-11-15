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
from zato.common.alerting.collectors.backlogs import collect_feed_silent_facts
from zato.common.hl7.mllp import state as mllp_state
from zato.common.hl7.mllp.region import _state as mllp_binding_state, bind_mllp
from zato.common.hl7.mllp.state import ChannelState
from zato.server.metrics_region import bind_metrics
from zato_ipc_core.zato_ipc_core import SharedRegion, STATE_READY

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.queues import SimpleQueue
    from zato.common.typing_ import any_, anydict, anylist, anytuple, callable_, generator_

    any_ = any_
    anydict = anydict
    anylist = anylist
    anytuple = anytuple
    callable_ = callable_
    generator_ = generator_
    SimpleQueue = SimpleQueue

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Slot_Count = 4

    Series_Capacity = 64

    # How long the test waits for a process, in seconds
    Join_Timeout = 60.0

    Channel_Name = 'hl7.orders'
    Other_Channel_Name = 'hl7.results'

    # The times of the arrivals of the tests, in seconds since the epoch
    Earlier_Arrival = 1_800_000_000.0
    Later_Arrival = 1_800_000_060.0

    # How long after the later arrival the sweep runs, in seconds
    Sweep_Delay = 1.0

_context = get_context('fork')

# ################################################################################################################################
# ################################################################################################################################

def _new_region(series_capacity:'int'=ModuleCtx.Series_Capacity) -> 'SharedRegion':
    """ Returns the region of a server whose every slot has a worker that is ready.
    """
    region = SharedRegion({
        'slot_count': ModuleCtx.Slot_Count,
        'wake_capacity': 0,
        'cell_capacity': 0,
        'queue_count': 0,
        'metric_count': 0,
        'series_capacity': series_capacity,
        'series_key_bytes': ModuleCtx.Series_Capacity * 256,
        'dedup_capacity': 0,
        'breaker_capacity': 0,
        'lock_capacity': 0,
        'start_id': 1,
    })

    for slot in range(ModuleCtx.Slot_Count):
        _ = region.next_slot_generation(slot)
        region.set_slot_state(slot, STATE_READY)

    return region

# ################################################################################################################################

def _bind(region:'SharedRegion', slot:'int') -> 'None':
    bind_mllp(region, slot, region.slot_generation(slot))

# ################################################################################################################################

@pytest.fixture(autouse=True)
def unbound() -> 'generator_[None, None, None]':
    """ Leaves this process without a binding after every test, as the tests bind it to the slots of their regions.
    """
    yield
    mllp_binding_state.binding = None

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

def _set_arrival_time(arrival:'float') -> 'None':
    mllp_state.time = lambda: arrival # type: ignore[assignment]

# ################################################################################################################################
# ################################################################################################################################

def _handle(
    results:'SimpleQueue',
    region:'SharedRegion',
    slot:'int',
    channel_name:'str',
    outcomes:'anytuple',
    arrival:'float',
    ) -> 'None':
    """ Handles one message for each outcome on a channel, in a worker bound to its slot.
    """
    _bind(region, slot)
    _set_arrival_time(arrival)

    channel_state = ChannelState(channel_name)

    for outcome in outcomes:
        channel_state.on_message_received()

        if outcome == 'ack':
            channel_state.on_ack_sent()
        elif outcome == 'nack':
            channel_state.on_nack_sent()
        else:
            channel_state.on_error()

    results.put(channel_state.received)

# ################################################################################################################################

def _query(results:'SimpleQueue', region:'SharedRegion', slot:'int', channel_name:'str', now:'float') -> 'None':
    """ Reports the state of a channel and its endpoint metrics, in a worker bound to its slot.
    """
    _bind(region, slot)

    channel_state = ChannelState(channel_name)

    contract = channel_state.get_state(now)
    metrics = channel_state.get_metrics(now)

    results.put((contract, metrics.silence_seconds))

# ################################################################################################################################
# ################################################################################################################################


# ################################################################################################################################

def test_a_query_through_one_worker_reports_the_messages_of_every_worker() -> 'None':
    region = _new_region()
    now = ModuleCtx.Later_Arrival + ModuleCtx.Sweep_Delay

    # Two workers handle the messages of one channel, and a third worker handles one of another channel ..
    assert _run_in_child(_handle, (region, 1, ModuleCtx.Channel_Name, ('ack', 'nack'), ModuleCtx.Earlier_Arrival)) == [2]
    assert _run_in_child(_handle, (region, 2, ModuleCtx.Channel_Name, ('ack', 'error'), ModuleCtx.Earlier_Arrival)) == [4]
    assert _run_in_child(_handle, (region, 3, ModuleCtx.Other_Channel_Name, ('ack',), ModuleCtx.Later_Arrival)) == [1]

    # .. and a worker that handled none of them reports the totals of each channel.
    [(contract, _)] = _run_in_child(_query, (region, 0, ModuleCtx.Channel_Name, now))

    assert contract['received'] == 4
    assert contract['acked'] == 2
    assert contract['nacked'] == 1
    assert contract['errored'] == 1

    [(other_contract, _)] = _run_in_child(_query, (region, 0, ModuleCtx.Other_Channel_Name, now))

    assert other_contract['received'] == 1
    assert other_contract['acked'] == 1

# ################################################################################################################################

def test_the_silence_of_a_channel_is_measured_from_the_latest_message_of_any_worker() -> 'None':
    region = _new_region()
    now = ModuleCtx.Later_Arrival + ModuleCtx.Sweep_Delay

    # A worker of a higher slot receives a message first, and a worker of a lower slot receives one later ..
    _ = _run_in_child(_handle, (region, 3, ModuleCtx.Channel_Name, ('ack',), ModuleCtx.Earlier_Arrival))
    _ = _run_in_child(_handle, (region, 1, ModuleCtx.Channel_Name, ('ack',), ModuleCtx.Later_Arrival))

    # .. and the sweep in a third worker measures the silence from the later message.
    [(contract, silence_seconds)] = _run_in_child(_query, (region, 2, ModuleCtx.Channel_Name, now))

    assert silence_seconds == ModuleCtx.Sweep_Delay
    assert contract['silence_seconds'] == ModuleCtx.Sweep_Delay
    assert contract['last_message_time_iso'] == '2027-01-15T08:01:00+00:00'

# ################################################################################################################################

def test_the_feed_silent_collector_reports_the_silence_across_workers() -> 'None':
    region = _new_region()
    now = ModuleCtx.Later_Arrival + ModuleCtx.Sweep_Delay

    _ = _run_in_child(_handle, (region, 1, ModuleCtx.Channel_Name, ('ack',), ModuleCtx.Later_Arrival))

    _bind(region, 2)
    metrics = ChannelState(ModuleCtx.Channel_Name).get_metrics(now)

    facts = collect_feed_silent_facts({ModuleCtx.Channel_Name: metrics}, 'hl7')

    assert len(facts) == 1
    assert facts[0]['silent_seconds'] == round(ModuleCtx.Sweep_Delay)

# ################################################################################################################################

def test_a_channel_that_no_worker_heard_reports_no_message() -> 'None':
    region = _new_region()

    _bind(region, 1)
    channel_state = ChannelState(ModuleCtx.Channel_Name)

    assert channel_state.received == 0
    assert channel_state.last_message_time is None
    assert channel_state.get_silence_seconds() == 0.0
    assert channel_state.get_last_message_time_iso() == ''

# ################################################################################################################################

def test_the_binding_of_a_new_worker_keeps_the_values_of_its_predecessor() -> 'None':
    region = _new_region()
    now = ModuleCtx.Later_Arrival + ModuleCtx.Sweep_Delay

    _ = _run_in_child(_handle, (region, 1, ModuleCtx.Channel_Name, ('ack',), ModuleCtx.Later_Arrival))

    # The worker that replaces the one of slot 1 binds the metrics of the server to its slot ..
    bind_metrics(region, 1)

    # .. which leaves the time of the last message and the counters of the channel in place.
    [(contract, silence_seconds)] = _run_in_child(_query, (region, 0, ModuleCtx.Channel_Name, now))

    assert contract['received'] == 1
    assert silence_seconds == ModuleCtx.Sweep_Delay

# ################################################################################################################################

def test_with_the_series_table_full_a_channel_counts_in_its_own_worker(caplog:'pytest.LogCaptureFixture') -> 'None':
    region = _new_region(series_capacity=0)

    _bind(region, 1)

    with caplog.at_level(logging.ERROR):
        channel_state = ChannelState(ModuleCtx.Channel_Name)

    channel_state.on_message_received()
    channel_state.on_ack_sent()

    assert channel_state.received == 1
    assert channel_state.acked == 1
    assert channel_state.last_message_time is not None
    assert 'the series table is full' in caplog.text

# ################################################################################################################################

def test_processes_without_an_arbiter_keep_the_values_of_each_state() -> 'None':
    first = ChannelState(ModuleCtx.Channel_Name)
    second = ChannelState(ModuleCtx.Channel_Name)

    first.on_message_received()

    assert first.received == 1
    assert second.received == 0
    assert second.last_message_time is None

# ################################################################################################################################
# ################################################################################################################################
