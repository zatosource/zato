# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
from gevent.event import Event

# Zato
from zato.common import worker_slot as worker_slot_module
from zato.server.base.parallel.stream_consumer import claim_own_pending, get_consumer_name, ModuleCtx as ConsumerCtx, \
    spawn_then_ack

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pytest import MonkeyPatch
    from redis import Redis
    from zato.common.typing_ import anydict, anylist, strlist

    anydict = anydict
    MonkeyPatch = MonkeyPatch
    Redis = Redis

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Stream = 'zato:scheduler:stream:fire'
    Group_Name = 'server-fire'

    # The slot of the terminated worker whose replacement claims its entries, and the slot of a live worker
    Replaced_Slot = 1
    Live_Slot = 2

    # How many entries each worker reads, and how many of them the terminated one acknowledged before it terminated
    Replaced_Read = 5
    Replaced_Acked = 1
    Live_Read = 3

    # The batch size of XPENDING in the test, smaller than the number of entries that the replacement claims
    Pending_Batch_Size = 2

    # How long the test waits for a handler, in seconds
    Handler_Timeout = 10.0

# ################################################################################################################################
# ################################################################################################################################

def _add_entries(redis_conn:'Redis', count:'int') -> 'strlist':
    out:'strlist' = []

    for idx in range(count):
        msg_id = redis_conn.xadd(ModuleCtx.Stream, {'job': str(idx)})
        out.append(msg_id)

    return out

# ################################################################################################################################

def _read(redis_conn:'Redis', consumer_name:'str', count:'int') -> 'anylist':
    """ Reads new entries of the stream as a worker of one consumer name does.
    """
    result = redis_conn.xreadgroup(ModuleCtx.Group_Name, consumer_name, {ModuleCtx.Stream: '>'}, count=count)
    out = result[0][1]

    return out

# ################################################################################################################################

def _get_pending_ids(redis_conn:'Redis', consumer_name:'str') -> 'strlist':
    pending = redis_conn.xpending_range(ModuleCtx.Stream, ModuleCtx.Group_Name, '-', '+', 1000, consumername=consumer_name)
    out = [item['message_id'] for item in pending]

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_the_consumer_name_names_the_slot_of_the_worker(monkeypatch:'MonkeyPatch') -> 'None':

    # A server with one process reads under the name of the first slot ..
    assert get_consumer_name(ModuleCtx.Group_Name) == 'server-fire-0'

    # .. and each worker under the name of its own slot.
    monkeypatch.setattr(worker_slot_module, '_worker_slot', ModuleCtx.Live_Slot)
    assert get_consumer_name(ModuleCtx.Group_Name) == 'server-fire-2'

# ################################################################################################################################

def test_a_replacement_claims_what_its_slot_left_pending_and_nothing_else(
    redis_conn:'Redis',
    monkeypatch:'MonkeyPatch',
    ) -> 'None':

    monkeypatch.setattr(ConsumerCtx, 'Pending_Batch_Size', ModuleCtx.Pending_Batch_Size)

    replaced_name = f'{ModuleCtx.Group_Name}-{ModuleCtx.Replaced_Slot}'
    live_name = f'{ModuleCtx.Group_Name}-{ModuleCtx.Live_Slot}'

    _ = redis_conn.xgroup_create(ModuleCtx.Stream, ModuleCtx.Group_Name, id='0', mkstream=True)
    _ = _add_entries(redis_conn, ModuleCtx.Replaced_Read + ModuleCtx.Live_Read)

    # The worker of one slot reads its entries and acknowledges the first of them before it terminates ..
    replaced_entries = _read(redis_conn, replaced_name, ModuleCtx.Replaced_Read)

    for msg_id, _fields in replaced_entries[:ModuleCtx.Replaced_Acked]:
        _ = redis_conn.xack(ModuleCtx.Stream, ModuleCtx.Group_Name, msg_id)

    # .. while the worker of another slot reads its own and is still handling them ..
    live_entries = _read(redis_conn, live_name, ModuleCtx.Live_Read)

    # .. the replacement of the terminated worker claims every entry that its slot left unacknowledged,
    # with their fields, across several batches ..
    claimed = claim_own_pending(redis_conn, ModuleCtx.Stream, ModuleCtx.Group_Name, replaced_name)
    expected = replaced_entries[ModuleCtx.Replaced_Acked:]

    assert [(msg_id, fields) for msg_id, fields in claimed] == [(msg_id, fields) for msg_id, fields in expected]

    # .. and the entries of the live worker remain pending for that worker alone.
    live_ids = [msg_id for msg_id, _fields in live_entries]

    assert _get_pending_ids(redis_conn, live_name) == live_ids
    assert _get_pending_ids(redis_conn, replaced_name) == [msg_id for msg_id, _fields in expected]

# ################################################################################################################################

def test_an_entry_remains_pending_until_its_handler_returns(redis_conn:'Redis') -> 'None':

    consumer_name = f'{ModuleCtx.Group_Name}-{ModuleCtx.Live_Slot}'

    _ = redis_conn.xgroup_create(ModuleCtx.Stream, ModuleCtx.Group_Name, id='0', mkstream=True)
    _ = _add_entries(redis_conn, 2)

    entries = _read(redis_conn, consumer_name, 2)
    (first_id, first_fields), (second_id, second_fields) = entries

    release = Event()
    handled:'anylist' = []

    def handle(fields:'anydict') -> 'None':
        _ = release.wait(ModuleCtx.Handler_Timeout)
        handled.append(fields)

    def fail(fields:'anydict') -> 'None':
        raise Exception('Handler failed')

    # The handler of one entry runs, and the handler of the other one raises ..
    first = spawn_then_ack(redis_conn, ModuleCtx.Stream, ModuleCtx.Group_Name, first_id, handle, first_fields)
    second = spawn_then_ack(redis_conn, ModuleCtx.Stream, ModuleCtx.Group_Name, second_id, fail, second_fields)

    _ = second.join(ModuleCtx.Handler_Timeout)

    # .. the entry whose handler raised is acknowledged, while the other one is pending until its handler returns ..
    assert _get_pending_ids(redis_conn, consumer_name) == [first_id]

    release.set()
    _ = first.join(ModuleCtx.Handler_Timeout)

    # .. after which nothing is pending.
    assert handled == [first_fields]
    assert _get_pending_ids(redis_conn, consumer_name) == []

# ################################################################################################################################
# ################################################################################################################################
