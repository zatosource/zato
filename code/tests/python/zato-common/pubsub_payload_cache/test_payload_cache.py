# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from multiprocessing import get_context

# gevent
import gevent

# SQLAlchemy
from sqlalchemy import event

# Zato
from zato.common.pubsub.sql.payload_cache import PayloadCache, PayloadEpoch
from zato.common.pubsub.sql.pull import payload_query
from zato.common.test.zato_database import isolated_database_env

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_

    any_ = any_
    callable_ = callable_

# ################################################################################################################################
# ################################################################################################################################

# The body of a test that starts a backend runs in a forked process
_context = get_context('fork')

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

def _new_backend() -> 'any_':
    gevent.reinit()

    from zato.common.pubsub.sql.backend import SQLPubSubBackend
    from zato.common.test.audit_log_ import new_test_audit_log

    out = SQLPubSubBackend(audit_log=new_test_audit_log())
    return out

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################

def test_the_payloads_used_least_recently_are_evicted() -> 'None':
    cache = PayloadCache(_cache_size, PayloadEpoch())
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
    cache = PayloadCache(_cache_size, PayloadEpoch())
    read_epoch = cache.get_epoch()

    cache.put(_first_msg_id, 'first', 10, read_epoch)
    cache.put(_second_msg_id, 'second', 10, read_epoch)

    cache.invalidate()

    assert cache.get(_first_msg_id) is None
    assert cache.get(_second_msg_id) is None
    assert cache.size == 0

# ################################################################################################################################

def test_a_payload_read_before_an_edit_is_not_kept() -> 'None':
    cache = PayloadCache(_cache_size, PayloadEpoch())

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

def _edit_during_a_delivery() -> 'None':
    backend = _new_backend()

    backend.subscribe(_sub_key, _topic_name)
    msg_id = backend.publish(_topic_name, _payload_before).msg_id

    state = {'is_armed': False}

    def on_execute(conn:'any_', cursor:'any_', statement:'str', parameters:'any_', context:'any_', executemany:'bool') -> 'None':
        payload_sql = payload_query.compile(dialect=conn.dialect).string
        if statement == payload_sql:
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

def test_a_payload_read_before_an_edit_is_not_sent_after_it() -> 'None':

    # The forked process inherits the variables that select the new database
    with isolated_database_env():
        _run_forked(_edit_during_a_delivery)

# ################################################################################################################################
# ################################################################################################################################
