# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from multiprocessing import get_context

# gevent
import gevent

# SQLAlchemy
from sqlalchemy import event

# Zato
from zato.common.pubsub.sql.payload_cache import get_payload_cache_size, LocalPayloadEpoch, Max_Payload_Cache_Size, \
     PayloadCache, SharedPayloadEpoch
from zato.common.pubsub.sql.pull import payload_query
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.connection import Connection
    from zato.common.typing_ import any_, callable_

    any_ = any_
    callable_ = callable_
    Connection = Connection

# ################################################################################################################################
# ################################################################################################################################

# The workers of another process are forked, so that they inherit the region
_context = get_context('fork')

_region_config = {
    'slot_count': 2,
    'wake_capacity': 8,
    'cell_capacity': 0,
    'queue_count': 0,
    'metric_count': 0,
    'series_capacity': 0,
    'series_key_bytes': 0,
    'dedup_capacity': 0,
    'breaker_capacity': 0,
    'lock_capacity': 0,
    'start_id': 1,
}

_cache_size = 100

_first_msg_id = 'msg-1'
_second_msg_id = 'msg-2'

_topic_name = 'payload.cache.topic'
_sub_key = 'zpsk.payload-cache.1'
_payload_before = 'payload-before-the-edit'
_payload_after = 'payload-after-the-edit'
_max_messages = 10

# How long a test waits for a forked process, in seconds
_timeout = 30.0

# ################################################################################################################################
# ################################################################################################################################

def _run_forked(target:'callable_', *args:'any_') -> 'None':
    """ Runs a test body in a forked process, so that the threads which a backend starts remain in that process.
    """
    process = _context.Process(target=target, args=args)
    process.start()
    process.join(_timeout)

    assert process.exitcode == 0

# ################################################################################################################################

def _fetch_payload(backend:'any_', msg_id:'str') -> 'str':
    _, payloads = backend._fetch_rows(_sub_key, _max_messages)
    out = payloads[msg_id]
    return out

# ################################################################################################################################

def _new_backend(db_path:'str', region:'SharedRegion | None') -> 'any_':
    gevent.reinit()
    os.environ['Zato_PubSub_DB_Path'] = db_path

    from zato.common.pubsub.sql.backend import SQLPubSubBackend

    out = SQLPubSubBackend()

    if region:
        out.share_payload_cache(region)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_each_worker_keeps_its_share_of_the_payloads() -> 'None':
    assert get_payload_cache_size(1) == Max_Payload_Cache_Size
    assert get_payload_cache_size(4) == Max_Payload_Cache_Size // 4

# ################################################################################################################################

def test_the_payloads_used_least_recently_are_evicted() -> 'None':
    cache = PayloadCache(_cache_size, LocalPayloadEpoch())
    read_epoch = cache.get_epoch()

    cache.put(_first_msg_id, 'first', 60, read_epoch)
    cache.put(_second_msg_id, 'second', 30, read_epoch)

    # The first payload is used more recently than the second one ..
    assert cache.get(_first_msg_id) == 'first'

    # .. so the second one leaves once a third one exceeds the size ..
    cache.put('msg-3', 'third', 30, read_epoch)

    assert cache.get(_second_msg_id) is None
    assert cache.get(_first_msg_id) == 'first'
    assert cache.size == 90

    # .. and one larger than the whole cache is not kept.
    cache.put('msg-4', 'fourth', _cache_size + 1, read_epoch)

    assert cache.get('msg-4') is None

# ################################################################################################################################

def test_an_edit_drops_every_payload_kept() -> 'None':
    cache = PayloadCache(_cache_size, LocalPayloadEpoch())
    read_epoch = cache.get_epoch()

    cache.put(_first_msg_id, 'first', 10, read_epoch)
    cache.put(_second_msg_id, 'second', 10, read_epoch)

    cache.invalidate()

    assert cache.get(_first_msg_id) is None
    assert cache.get(_second_msg_id) is None
    assert cache.size == 0

# ################################################################################################################################

def test_a_payload_read_before_an_edit_is_not_kept() -> 'None':
    cache = PayloadCache(_cache_size, LocalPayloadEpoch())

    # The delivery reads the epoch before its queries, the edit commits and returns, and another delivery looks
    # the message up before the first one keeps the payload ..
    read_epoch = cache.get_epoch()
    cache.invalidate()

    assert cache.get(_first_msg_id) is None

    cache.put(_first_msg_id, 'first', 10, read_epoch)

    assert cache.get(_first_msg_id) is None

    # .. whereas a payload read after the edit is kept.
    read_epoch = cache.get_epoch()
    cache.put(_first_msg_id, 'first', 10, read_epoch)

    assert cache.get(_first_msg_id) == 'first'

# ################################################################################################################################

def test_an_edit_in_another_worker_drops_the_payload() -> 'None':
    region = SharedRegion(_region_config)

    delivering = PayloadCache(_cache_size, SharedPayloadEpoch(region))
    editing = PayloadCache(_cache_size, SharedPayloadEpoch(region))

    delivering.put(_first_msg_id, 'first', 10, delivering.get_epoch())
    assert delivering.get(_first_msg_id) == 'first'

    editing.invalidate()

    assert delivering.get(_first_msg_id) is None

# ################################################################################################################################

def _invalidate_in_forked_worker(region:'SharedRegion') -> 'None':
    cache = PayloadCache(_cache_size, SharedPayloadEpoch(region))
    cache.invalidate()

# ################################################################################################################################

def test_an_edit_in_another_process_drops_the_payload() -> 'None':
    region = SharedRegion(_region_config)

    cache = PayloadCache(_cache_size, SharedPayloadEpoch(region))
    cache.put(_first_msg_id, 'first', 10, cache.get_epoch())

    _run_forked(_invalidate_in_forked_worker, region)

    assert cache.get(_first_msg_id) is None

# ################################################################################################################################

def _check_the_share_of_a_backend(db_path:'str', region:'SharedRegion') -> 'None':
    backend = _new_backend(db_path, region)

    assert backend.payload_cache.max_size == Max_Payload_Cache_Size // _region_config['slot_count']
    assert isinstance(backend.payload_cache.epoch, SharedPayloadEpoch)

# ################################################################################################################################

def test_a_backend_takes_its_share_under_the_shared_epoch(tmp_path:'any_') -> 'None':
    region = SharedRegion(_region_config)
    db_path = os.path.join(tmp_path, 'pubsub.db')

    _run_forked(_check_the_share_of_a_backend, db_path, region)

# ################################################################################################################################

def _deliver_in_forked_worker(db_path:'str', region:'SharedRegion', conn:'Connection') -> 'None':
    backend = _new_backend(db_path, region)

    backend.subscribe(_sub_key, _topic_name)
    msg_id = backend.publish(_topic_name, _payload_before).msg_id

    assert _fetch_payload(backend, msg_id) == _payload_before

    conn.send(msg_id)
    _ = conn.recv()

    assert _fetch_payload(backend, msg_id) == _payload_after

# ################################################################################################################################

def _edit_in_forked_worker(db_path:'str', region:'SharedRegion', conn:'Connection') -> 'None':
    msg_id = conn.recv()

    backend = _new_backend(db_path, region)
    assert backend.update_message(_topic_name, msg_id, _payload_after)

    conn.send(None)

# ################################################################################################################################

def test_the_next_delivery_in_another_worker_sends_the_edited_payload(tmp_path:'any_') -> 'None':
    region = SharedRegion(_region_config)
    db_path = os.path.join(tmp_path, 'pubsub.db')

    delivering_conn, delivering_child = _context.Pipe()
    editing_conn, editing_child = _context.Pipe()

    delivering = _context.Process(target=_deliver_in_forked_worker, args=(db_path, region, delivering_child))
    editing = _context.Process(target=_edit_in_forked_worker, args=(db_path, region, editing_child))

    delivering.start()
    editing.start()

    # The payload is kept by the delivering worker before the other one edits it ..
    msg_id = delivering_conn.recv()
    editing_conn.send(msg_id)

    # .. and the delivering worker delivers it again once update_message returned.
    _ = editing_conn.recv()
    delivering_conn.send(None)

    delivering.join(_timeout)
    editing.join(_timeout)

    assert delivering.exitcode == 0
    assert editing.exitcode == 0

# ################################################################################################################################

def _edit_during_a_delivery(db_path:'str') -> 'None':
    backend = _new_backend(db_path, None)

    backend.subscribe(_sub_key, _topic_name)
    msg_id = backend.publish(_topic_name, _payload_before).msg_id

    state = {'is_armed': False}

    def on_execute(conn:'any_', cursor:'any_', statement:'str', parameters:'any_', context:'any_', executemany:'bool') -> 'None':
        if context.invoked_statement is payload_query:
            state['is_armed'] = True

    # The edit commits and returns after the delivery read the payload and before it keeps it
    def on_checkin(*_:'any_') -> 'None':
        if state['is_armed']:
            state['is_armed'] = False
            state['is_edited'] = backend.update_message(_topic_name, msg_id, _payload_after)

    event.listen(backend.engine, 'after_cursor_execute', on_execute)
    event.listen(backend.engine.pool, 'checkin', on_checkin)

    assert _fetch_payload(backend, msg_id) == _payload_before
    assert state['is_edited']

    assert _fetch_payload(backend, msg_id) == _payload_after

# ################################################################################################################################

def test_a_payload_read_before_an_edit_is_not_sent_after_it(tmp_path:'any_') -> 'None':
    db_path = os.path.join(tmp_path, 'pubsub.db')

    _run_forked(_edit_during_a_delivery, db_path)

# ################################################################################################################################
# ################################################################################################################################
