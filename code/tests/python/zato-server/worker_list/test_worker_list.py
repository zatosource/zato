# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.ext.bunch import Bunch
from zato.common.pubsub.ownership import is_owner
from zato.common.pubsub.subscriptions_store import SubscriptionsStore
from zato.server.control.hub import EntryStatus, new_entry
from zato.server.control.queries import new_query, QueryName, QueryRouter
from zato.server.service.internal.worker import GetList
from zato.server.worker_list import _state as worker_list_state, answer_worker_list, bind_worker_list, build_worker_list
from zato_ipc_core.zato_ipc_core import SharedRegion, STATE_DRAINING, STATE_READY, STATE_STOPPED

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, generator_

    any_ = any_
    anydict = anydict
    anylist = anylist

    nonegenerator = generator_[None, None, None]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Slot_Count = 4

    # The slots of the region of the tests: one answers, one does not answer in time, one awaits its respawn
    # and one never had a worker
    Answered_Slot = 0
    Timed_Out_Slot = 1
    Stopped_Slot = 2
    Empty_Slot = 3

    Answered_Pid = 1001
    Timed_Out_Pid = 1002
    Stopped_Pid = 1003

    # The monotonic time of the tests and the heartbeat of each slot that had a worker, in microseconds
    Now_Us = 50_000_000
    Answered_Heartbeat_Us = 49_900_000
    Timed_Out_Heartbeat_Us = 47_000_000
    Stopped_Heartbeat_Us = 40_000_000

    Answered_Heartbeat_Age_Ms = 100
    Timed_Out_Heartbeat_Age_Ms = 3000
    Stopped_Heartbeat_Age_Ms = 10_000

    # The generation of the worker of the answered slot and the generations of the other slots in the region
    Answered_Generation = 2
    Timed_Out_Generation = 1
    Stopped_Generation = 3

    Answered_Sub_Key_Count = 7

    Sub_Key_Count = 40
    Sub_Key_Pattern = 'zpsk.test.worker-list.{}'

# ################################################################################################################################
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
    return out

# ################################################################################################################################

def _start_slot(region:'SharedRegion', slot:'int', pid:'int', generation:'int', heartbeat_us:'int', state:'int') -> 'None':
    """ Records in the region a worker of a slot, as the arbiter does when it forks one.
    """
    for _ in range(generation):
        _ = region.next_slot_generation(slot)

    region.set_slot_pid(slot, pid)
    region.set_slot_heartbeat(slot, heartbeat_us)
    region.set_slot_state(slot, state)

# ################################################################################################################################

def _new_sub_keys() -> 'list[str]':
    out = [ModuleCtx.Sub_Key_Pattern.format(index) for index in range(ModuleCtx.Sub_Key_Count)]
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def unbind_worker_list() -> 'nonegenerator':
    """ Leaves this process without the binding that a test made.
    """
    yield
    worker_list_state.binding = None

# ################################################################################################################################

@pytest.fixture
def region() -> 'SharedRegion':
    out = _new_region()

    _start_slot(out, ModuleCtx.Answered_Slot, ModuleCtx.Answered_Pid, ModuleCtx.Answered_Generation,
        ModuleCtx.Answered_Heartbeat_Us, STATE_READY)

    _start_slot(out, ModuleCtx.Timed_Out_Slot, ModuleCtx.Timed_Out_Pid, ModuleCtx.Timed_Out_Generation,
        ModuleCtx.Timed_Out_Heartbeat_Us, STATE_DRAINING)

    _start_slot(out, ModuleCtx.Stopped_Slot, ModuleCtx.Stopped_Pid, ModuleCtx.Stopped_Generation,
        ModuleCtx.Stopped_Heartbeat_Us, STATE_STOPPED)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_each_slot_is_described_by_its_answer_or_by_the_region(region:'SharedRegion') -> 'None':

    answer = {
        'pid': ModuleCtx.Answered_Pid,
        'generation': ModuleCtx.Answered_Generation,
        'sub_key_count': ModuleCtx.Answered_Sub_Key_Count,
        'is_singleton_owner': True,
    }

    entries = [
        new_entry(ModuleCtx.Answered_Slot, EntryStatus.OK, answer),
        new_entry(ModuleCtx.Timed_Out_Slot, EntryStatus.Timeout, None),
        new_entry(ModuleCtx.Stopped_Slot, EntryStatus.Unavailable, None),
        new_entry(ModuleCtx.Empty_Slot, EntryStatus.Unavailable, None),
    ]

    rows = build_worker_list(region, entries, ModuleCtx.Now_Us)

    assert rows == [
        {
            'slot': ModuleCtx.Answered_Slot,
            'pid': ModuleCtx.Answered_Pid,
            'generation': ModuleCtx.Answered_Generation,
            'state': 'ready',
            'heartbeat_age_ms': ModuleCtx.Answered_Heartbeat_Age_Ms,
            'sub_key_count': ModuleCtx.Answered_Sub_Key_Count,
            'is_singleton_owner': True,
            'response': EntryStatus.OK,
        },
        {
            'slot': ModuleCtx.Timed_Out_Slot,
            'pid': ModuleCtx.Timed_Out_Pid,
            'generation': ModuleCtx.Timed_Out_Generation,
            'state': 'draining',
            'heartbeat_age_ms': ModuleCtx.Timed_Out_Heartbeat_Age_Ms,
            'sub_key_count': None,
            'is_singleton_owner': None,
            'response': EntryStatus.Timeout,
        },
        {
            'slot': ModuleCtx.Stopped_Slot,
            'pid': ModuleCtx.Stopped_Pid,
            'generation': ModuleCtx.Stopped_Generation,
            'state': 'stopped',
            'heartbeat_age_ms': ModuleCtx.Stopped_Heartbeat_Age_Ms,
            'sub_key_count': None,
            'is_singleton_owner': None,
            'response': EntryStatus.Unavailable,
        },
        {
            'slot': ModuleCtx.Empty_Slot,
            'pid': 0,
            'generation': 0,
            'state': 'empty',
            'heartbeat_age_ms': None,
            'sub_key_count': None,
            'is_singleton_owner': None,
            'response': EntryStatus.Unavailable,
        },
    ]

# ################################################################################################################################

def test_the_answers_of_all_slots_count_every_key_once(region:'SharedRegion') -> 'None':

    store = SubscriptionsStore()
    sub_keys = _new_sub_keys()

    for index, sub_key in enumerate(sub_keys):
        _ = store.register_user(f'user.{index}', f'sec.{index}', sub_key)

    # The worker of each slot answers with the keys that its slot owns, of every key in its store ..
    counts:'anylist' = []

    for slot in range(ModuleCtx.Slot_Count):
        bind_worker_list(region, slot, ModuleCtx.Answered_Generation, None, store.get_sub_keys) # type: ignore[arg-type]
        answer = answer_worker_list(None)

        owned = [sub_key for sub_key in sub_keys if is_owner(sub_key, slot, ModuleCtx.Slot_Count)]
        assert answer['sub_key_count'] == len(owned)
        assert answer['generation'] == ModuleCtx.Answered_Generation

        counts.append(answer['sub_key_count'])

    # .. so the counts of all slots add up to the number of keys.
    assert sum(counts) == ModuleCtx.Sub_Key_Count

# ################################################################################################################################

def test_a_query_is_answered_by_the_handler_of_its_name() -> 'None':

    def answer_list(data:'str') -> 'anydict':
        out = {'received': data}
        return out

    def answer_other(_data:'str') -> 'None':
        return None

    router = QueryRouter()
    router.register(QueryName.Worker_Get_List, answer_list)
    router.register('zato.test.other', answer_other)

    answer = router.on_query(new_query(QueryName.Worker_Get_List, 'my-data'))
    assert answer == {'received': 'my-data'}

# ################################################################################################################################

def test_the_service_returns_a_row_for_every_entry_of_the_query(region:'SharedRegion') -> 'None':

    queries:'anylist' = []

    def query(body:'anydict') -> 'anylist':
        queries.append(body)

        out = [new_entry(slot, EntryStatus.Unavailable, None) for slot in range(ModuleCtx.Slot_Count)]
        return out

    bind_worker_list(region, ModuleCtx.Answered_Slot, ModuleCtx.Answered_Generation, query, list)

    service = Bunch(response=Bunch(payload=None))
    GetList.handle(service) # type: ignore[arg-type]

    assert queries == [new_query(QueryName.Worker_Get_List, None)]

    items = service.response.payload['items']
    assert [item['slot'] for item in items] == list(range(ModuleCtx.Slot_Count))
    assert [item['pid'] for item in items] == [ModuleCtx.Answered_Pid, ModuleCtx.Timed_Out_Pid, ModuleCtx.Stopped_Pid, 0]

# ################################################################################################################################

def test_the_worker_list_requires_a_worker_process() -> 'None':

    with pytest.raises(Exception, match='available only in a worker process'):
        _ = answer_worker_list(None)

# ################################################################################################################################
# ################################################################################################################################
