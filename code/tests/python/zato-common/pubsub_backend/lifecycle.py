# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# Zato
from common import delete_all_rows, get_delivery_rows, get_message_rows
from zato.common.pubsub.sql.backend import SQLPubSubBackend

# ################################################################################################################################
# ################################################################################################################################

# The topic and subscribers all the lifecycle assertions share
_topic = 'pubsub.backend.test.lifecycle'
_sub_key_1 = 'zpsk.test.lifecycle.1'
_sub_key_2 = 'zpsk.test.lifecycle.2'

# ################################################################################################################################
# ################################################################################################################################

def _run_publish_fetch_ack_flow(backend:'SQLPubSubBackend') -> 'None':
    """ The core flow - publications reach every subscriber, fetches are ordered
    by priority, acknowledgements are per subscriber and the payload is dropped
    only once the last subscriber has acknowledged.
    """
    delete_all_rows()

    # A message published before anyone subscribes reaches no queue - its row goes
    # straight into the delivered-message trace form, payload already dropped ..
    pre_subscription_result = backend.publish(_topic, 'published-before-any-subscription')

    assert pre_subscription_result.msg_id.startswith('zpsm.')

    # .. now both subscribers arrive - subscribing twice makes no difference ..
    backend.subscribe(_sub_key_1, _topic)
    backend.subscribe(_sub_key_1, _topic)
    backend.subscribe(_sub_key_2, _topic)

    # .. and the pre-subscription message is not deliverable to either of them ..
    assert backend.fetch_messages(_sub_key_1) == []
    assert backend.fetch_messages(_sub_key_2) == []

    trace_rows = get_message_rows(_topic)
    assert len(trace_rows) == 1
    assert trace_rows[0].payload is None

    # .. publish three messages with different priorities and optional metadata ..
    dict_data = {'abc': 123}

    result_1 = backend.publish(_topic, dict_data)
    result_2 = backend.publish(_topic, 'high-priority-data', priority=9)
    result_3 = backend.publish(_topic, 'low-priority-data', priority=1,
        correl_id='correlation-1', in_reply_to='msg-0', ext_client_id='client-1',
        publisher='alice', cid='cid-lifecycle-1')

    # .. the fetch returns them highest-priority first, publication order within a priority ..
    messages = backend.fetch_messages(_sub_key_1)

    assert len(messages) == 3
    assert messages[0]['msg_id'] == result_2.msg_id
    assert messages[1]['msg_id'] == result_1.msg_id
    assert messages[2]['msg_id'] == result_3.msg_id

    # .. non-string payloads were serialized to JSON on publish ..
    assert messages[1]['data'] == json.dumps(dict_data)

    # .. every message carries the full metadata set ..
    high_priority = messages[0]

    assert high_priority['topic_name'] == _topic
    assert high_priority['data'] == 'high-priority-data'
    assert high_priority['data_size'] == len('high-priority-data')
    assert high_priority['data_preview'] == 'high-priority-data'
    assert high_priority['priority'] == 9
    assert high_priority['expiration'] > 0
    assert high_priority['pub_time_iso']
    assert high_priority['recv_time_iso']
    assert high_priority['expiration_time_iso']

    # .. optional fields exist only on the message that was published with them ..
    assert 'correl_id' not in high_priority
    assert 'publisher' not in high_priority

    low_priority = messages[2]

    assert low_priority['correl_id'] == 'correlation-1'
    assert low_priority['in_reply_to'] == 'msg-0'
    assert low_priority['ext_client_id'] == 'client-1'
    assert low_priority['publisher'] == 'alice'
    assert low_priority['cid'] == 'cid-lifecycle-1'

    # .. fetching does not acknowledge - a re-fetch sees the same messages ..
    messages_again = backend.fetch_messages(_sub_key_1)
    assert len(messages_again) == 3

    # .. acknowledging for one subscriber leaves the other's queue intact
    # .. and the payload stays because the other subscriber still needs it ..
    fully_delivered = backend.ack_message(_sub_key_1, result_2.msg_id)
    assert fully_delivered is False

    assert len(backend.fetch_messages(_sub_key_1)) == 2
    assert len(backend.fetch_messages(_sub_key_2)) == 3

    # .. a batch acknowledgement clears the rest of the first subscriber's queue ..
    fully_delivered_count = backend.ack_messages(_sub_key_1, [result_1.msg_id, result_3.msg_id])
    assert fully_delivered_count == 0

    assert backend.fetch_messages(_sub_key_1) == []

    # .. and once the second subscriber acknowledges everything, all three payloads are dropped ..
    msg_ids = [result_1.msg_id, result_2.msg_id, result_3.msg_id]
    fully_delivered_count = backend.ack_messages(_sub_key_2, msg_ids)
    assert fully_delivered_count == 3

    assert backend.fetch_messages(_sub_key_2) == []
    assert get_delivery_rows(_sub_key_1) == []
    assert get_delivery_rows(_sub_key_2) == []

    # .. the rows themselves stay behind as delivered-message traces.
    trace_rows = get_message_rows(_topic)
    assert len(trace_rows) == 4

    for row in trace_rows:
        assert row.payload is None

# ################################################################################################################################

def _run_expiration_flow(backend:'SQLPubSubBackend') -> 'None':
    """ Messages that are already past their expiration time are never fetched.
    """
    delete_all_rows()

    backend.subscribe(_sub_key_1, _topic)

    # A zero expiration means the message expires the moment it is published ..
    _ = backend.publish(_topic, 'expires-immediately', expiration=0)

    # .. while a positive one keeps the message deliverable ..
    live_result = backend.publish(_topic, 'still-alive', expiration=3600)

    # .. so the fetch sees only the live one.
    messages = backend.fetch_messages(_sub_key_1)

    assert len(messages) == 1
    assert messages[0]['msg_id'] == live_result.msg_id

# ################################################################################################################################

def _run_fetch_limits_flow(backend:'SQLPubSubBackend') -> 'None':
    """ Fetches respect both the message count limit and the total size budget.
    """
    delete_all_rows()

    backend.subscribe(_sub_key_1, _topic)

    payload_1 = 'a' * 100
    payload_2 = 'b' * 100
    payload_3 = 'c' * 100

    _ = backend.publish(_topic, payload_1)
    _ = backend.publish(_topic, payload_2)
    _ = backend.publish(_topic, payload_3)

    # The count limit caps how many messages one fetch returns ..
    messages = backend.fetch_messages(_sub_key_1, max_messages=2)
    assert len(messages) == 2

    # .. and the size budget stops the fetch before it would be exceeded ..
    messages = backend.fetch_messages(_sub_key_1, max_len=150)
    assert len(messages) == 1

    messages = backend.fetch_messages(_sub_key_1, max_len=250)
    assert len(messages) == 2

    # .. while a budget that fits everything returns everything.
    messages = backend.fetch_messages(_sub_key_1, max_len=1000)
    assert len(messages) == 3

    # fetch_pending is the startup-recovery entry point and sees the same queue.
    pending = backend.fetch_pending(_sub_key_1)
    assert len(pending) == 3

# ################################################################################################################################

def _run_rest_formatting_flow(backend:'SQLPubSubBackend') -> 'None':
    """ The REST formatting parses JSON payloads, fills in the meta envelope
    and acknowledges each message it hands over.
    """
    delete_all_rows()

    backend.subscribe(_sub_key_1, _topic)

    dict_data = {'invoice_id': 'INV-1', 'amount': 250}
    result = backend.publish(_topic, dict_data, correl_id='correlation-rest-1')

    messages = backend.fetch_messages(_sub_key_1)
    formatted = backend.format_messages_for_rest(messages, _sub_key_1)

    assert len(formatted) == 1
    entry = formatted[0]

    # JSON payloads come back parsed ..
    assert entry['data'] == dict_data

    # .. with the meta envelope fully filled in ..
    meta = entry['meta']

    assert meta['topic_name'] == _topic
    assert meta['msg_id'] == result.msg_id
    assert meta['sub_key'] == _sub_key_1
    assert meta['size'] == len(json.dumps(dict_data))
    assert meta['priority'] == 5
    assert meta['correl_id'] == 'correlation-rest-1'
    assert meta['pub_time_iso']
    assert meta['recv_time_iso']
    assert meta['expiration_time_iso']
    assert meta['time_since_pub']
    assert meta['time_since_recv']

    # .. and the hand-over acknowledged the message.
    assert backend.fetch_messages(_sub_key_1) == []

    # Non-JSON payloads come back as the plain strings they are.
    _ = backend.publish(_topic, 'just plain text')

    messages = backend.fetch_messages(_sub_key_1)
    formatted = backend.format_messages_for_rest(messages, _sub_key_1)

    assert formatted[0]['data'] == 'just plain text'

# ################################################################################################################################

def run_lifecycle_scenario() -> 'None':
    """ The message lifecycle every backend must support - publish, fetch, acknowledge,
    expiration, fetch limits and the REST formatting.
    """
    backend = SQLPubSubBackend()

    _run_publish_fetch_ack_flow(backend)
    _run_expiration_flow(backend)
    _run_fetch_limits_flow(backend)
    _run_rest_formatting_flow(backend)

# ################################################################################################################################
# ################################################################################################################################
