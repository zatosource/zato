# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
from gevent.event import Event

# Zato
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

    # The consumer name of the worker
    Consumer_Name = 'server-fire-worker'

    # How many entries the terminated worker read, how many of them it acknowledged before it terminated,
    # and how many entries were added after it terminated
    Replaced_Read = 5
    Replaced_Acked = 1
    Unread = 3

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
    """ Reads new entries of the stream as the worker does.
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

def test_the_worker_reads_under_one_consumer_name() -> 'None':
    assert get_consumer_name(ModuleCtx.Group_Name) == ModuleCtx.Consumer_Name

# ################################################################################################################################

def test_a_replacement_claims_what_its_predecessor_left_pending(redis_conn:'Redis', monkeypatch:'MonkeyPatch') -> 'None':

    monkeypatch.setattr(ConsumerCtx, 'Pending_Batch_Size', ModuleCtx.Pending_Batch_Size)

    _ = redis_conn.xgroup_create(ModuleCtx.Stream, ModuleCtx.Group_Name, id='0', mkstream=True)
    _ = _add_entries(redis_conn, ModuleCtx.Replaced_Read + ModuleCtx.Unread)

    # The worker reads its entries and acknowledges the first of them before it terminates ..
    replaced_entries = _read(redis_conn, ModuleCtx.Consumer_Name, ModuleCtx.Replaced_Read)

    for msg_id, _fields in replaced_entries[:ModuleCtx.Replaced_Acked]:
        _ = redis_conn.xack(ModuleCtx.Stream, ModuleCtx.Group_Name, msg_id)

    # .. its replacement claims every entry that it left unacknowledged, with their fields, across several batches ..
    claimed = claim_own_pending(redis_conn, ModuleCtx.Stream, ModuleCtx.Group_Name, ModuleCtx.Consumer_Name)
    expected = replaced_entries[ModuleCtx.Replaced_Acked:]

    assert [(msg_id, fields) for msg_id, fields in claimed] == [(msg_id, fields) for msg_id, fields in expected]

    # .. and the entries that no worker read remain to be read.
    unread = _read(redis_conn, ModuleCtx.Consumer_Name, ModuleCtx.Unread)
    assert len(unread) == ModuleCtx.Unread

# ################################################################################################################################

def test_an_entry_remains_pending_until_its_handler_returns(redis_conn:'Redis') -> 'None':

    consumer_name = ModuleCtx.Consumer_Name

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
