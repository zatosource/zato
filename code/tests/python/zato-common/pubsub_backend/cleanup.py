# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from common import delete_all_rows, get_delivery_rows, get_message_rows
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.cleanup import PubSubCleanup
from zato.common.pubsub.sql.config import get_pubsub_engine, ModuleCtx
from zato.common.pubsub.sql.schema import message_table
from zato.common.util.time_ import datetime_to_ms, utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

# The topics and subscribers all the cleanup assertions share.
_topic_expiry = 'pubsub.backend.test.cleanup.expiry'
_topic_traces = 'pubsub.backend.test.cleanup.traces'

_sub_key_1 = 'zpsk.test.cleanup.1'
_sub_key_2 = 'zpsk.test.cleanup.2'
_sub_key_3 = 'zpsk.test.cleanup.3'

# How many milliseconds one second and one day have.
_ms_per_second = 1000
_ms_per_day = 24 * 60 * 60 * _ms_per_second

# How far in the past an aged trace is placed - well past the default retention of days.
_aged_days = 30

# ################################################################################################################################
# ################################################################################################################################

def _set_expired(msg_ids:'strlist') -> 'None':
    """ Moves the expiration of the given messages into the past, straight in the database.
    """
    engine = get_pubsub_engine()

    now_ms = int(datetime_to_ms(utcnow()))
    expired_ms = now_ms - _ms_per_second

    update_statement = message_table.update()
    update_statement = update_statement.where(message_table.c.msg_id.in_(msg_ids))
    update_statement = update_statement.values(expiration_ms=expired_ms)

    with engine.begin() as connection:
        _ = connection.execute(update_statement)

# ################################################################################################################################

def _set_aged(msg_ids:'strlist') -> 'None':
    """ Moves the publication time of the given messages far into the past,
    straight in the database.
    """
    engine = get_pubsub_engine()

    now_ms = int(datetime_to_ms(utcnow()))
    aged_ms = now_ms - _aged_days * _ms_per_day

    update_statement = message_table.update()
    update_statement = update_statement.where(message_table.c.msg_id.in_(msg_ids))
    update_statement = update_statement.values(pub_time_ms=aged_ms)

    with engine.begin() as connection:
        _ = connection.execute(update_statement)

# ################################################################################################################################

def _get_trace_msg_ids(topic_name:'str') -> 'strlist':
    """ Returns the public identifiers of one topic's delivered-message traces,
    in publication order.
    """
    out:'strlist' = []

    for row in get_message_rows(topic_name):
        if row.payload is None:
            out.append(row.msg_id)

    return out

# ################################################################################################################################

def _fetch_and_ack_all(backend:'SQLPubSubBackend', sub_key:'str') -> 'None':
    """ Drains one subscriber's queue completely, acknowledging everything fetched.
    """
    while True:

        messages = backend.fetch_messages(sub_key)

        if not messages:
            break

        msg_ids:'strlist' = []

        for message in messages:
            msg_ids.append(message['msg_id'])

        _ = backend.ack_messages(sub_key, msg_ids)

# ################################################################################################################################

def run_cleanup_scenario() -> 'None':
    """ The cleanup process - expired messages disappear with their delivery rows,
    delivered-message traces outlive expiry yet fall to the retention sweeps,
    and pending messages are never touched.
    """
    delete_all_rows()

    backend = SQLPubSubBackend()
    cleanup = PubSubCleanup()

    # Two subscribers so expiry can be checked against multi-subscriber deliveries.
    backend.subscribe(_sub_key_1, _topic_expiry)
    backend.subscribe(_sub_key_2, _topic_expiry)

    # Five pending messages, of which the last three expire ..
    kept_msg_ids:'strlist' = []
    expired_msg_ids:'strlist' = []

    for index in range(2):
        result = backend.publish(_topic_expiry, f'cleanup-kept-{index}')
        kept_msg_ids.append(result.msg_id)

    for index in range(3):
        result = backend.publish(_topic_expiry, f'cleanup-expired-{index}')
        expired_msg_ids.append(result.msg_id)

    _set_expired(expired_msg_ids)

    # .. the expiry sweep removes exactly the expired ones, delivery rows included ..
    counts = cleanup.sweep_once()

    assert counts['expired'] == 3, counts
    assert counts['aged'] == 0, counts
    assert counts['over_cap'] == 0, counts

    message_rows = get_message_rows(_topic_expiry)
    assert len(message_rows) == 2, len(message_rows)

    assert len(get_delivery_rows(_sub_key_1)) == 2
    assert len(get_delivery_rows(_sub_key_2)) == 2

    # .. a fully delivered message becomes a trace with a NULL payload,
    # .. and traces are exempt from the expiry sweep even when expired ..
    trace_msg_id = kept_msg_ids[0]

    _ = backend.ack_message(_sub_key_1, trace_msg_id)
    _ = backend.ack_message(_sub_key_2, trace_msg_id)

    _set_expired([trace_msg_id])

    counts = cleanup.sweep_once()
    assert counts['expired'] == 0, counts

    trace_msg_ids = _get_trace_msg_ids(_topic_expiry)
    assert trace_msg_ids == [trace_msg_id], trace_msg_ids

    # .. now a topic whose messages are all delivered, so it holds traces only -
    # .. with its own subscriber so draining it cannot touch the expiry topic ..
    backend.subscribe(_sub_key_3, _topic_traces)

    for index in range(4):
        _ = backend.publish(_topic_traces, f'cleanup-trace-{index}')

    _fetch_and_ack_all(backend, _sub_key_3)

    trace_msg_ids = _get_trace_msg_ids(_topic_traces)
    assert len(trace_msg_ids) == 4, trace_msg_ids

    # .. the two oldest traces age past the retention and the age sweep removes them ..
    _set_aged(trace_msg_ids[:2])

    counts = cleanup.sweep_once()

    assert counts['aged'] == 2, counts

    remaining_trace_msg_ids = _get_trace_msg_ids(_topic_traces)
    assert remaining_trace_msg_ids == trace_msg_ids[2:], remaining_trace_msg_ids

    # .. with the per-topic cap lowered to one, the cap sweep keeps only
    # .. the newest trace of each topic ..
    os.environ[ModuleCtx.Env_Delivered_Max_Messages] = '1'

    try:
        counts = cleanup.sweep_once()
    finally:
        del os.environ[ModuleCtx.Env_Delivered_Max_Messages]

    assert counts['over_cap'] == 1, counts

    remaining_trace_msg_ids = _get_trace_msg_ids(_topic_traces)
    assert remaining_trace_msg_ids == trace_msg_ids[3:], remaining_trace_msg_ids

    # .. and through all of the above, the pending message was never touched.
    pending_msg_id = kept_msg_ids[1]

    pending_rows = []

    for row in get_message_rows(_topic_expiry):
        if row.msg_id == pending_msg_id:
            pending_rows.append(row)

    assert len(pending_rows) == 1, pending_rows
    assert pending_rows[0].payload is not None

    assert len(get_delivery_rows(_sub_key_1)) == 1
    assert len(get_delivery_rows(_sub_key_2)) == 1

# ################################################################################################################################
# ################################################################################################################################
