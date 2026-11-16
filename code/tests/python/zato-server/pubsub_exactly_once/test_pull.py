# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from http.client import BAD_REQUEST, CONFLICT, FORBIDDEN, OK, UNAUTHORIZED

# Zato
from pubsub_exactly_once.harness import get_engine, new_keys
from pubsub_exactly_once.rest import ack, drain, publish, pull_by_key
from zato.common.test import pubsub_db
from zato.common.test.exactly_once.config import TestConfig
from zato.common.test.exactly_once.verify import count_deliveries

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pubsub_exactly_once.rest import HTTPResult
    from zato.common.typing_ import any_, anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

# The topics of the cycle of a pull client
_orders_topic   = 'orders'
_invoices_topic = 'invoices'
_audit_topic    = 'audit'

# A topic that is not active
_inactive_topic = 'exactly-once.inactive'

# How long a copy waits for the lease of its message to run out, in seconds
_lease_wait_seconds = 3.0

# The largest number of elements that a list of an acknowledgement may have
_max_elements = 1000

# A message ID that does not match the pattern of message IDs, and the longest message ID allowed
_invalid_msg_id = 'order number 1'
_max_msg_id_length = 200

# ################################################################################################################################
# ################################################################################################################################

def _publish_order(key:'str') -> 'str':
    """ Publishes one order with the key and returns its message ID.
    """
    payload:'anydict' = {'data': {'key': key}}
    result = publish(TestConfig.publisher_username, TestConfig.publisher_password, _orders_topic, payload)

    assert result.status_code == OK, result

    out = result.body['msg_id']
    return out

# ################################################################################################################################

def _pull_order(key:'str') -> 'anydict':
    """ Pulls the order with the key as the orders client and returns its meta.
    """
    message = pull_by_key(TestConfig.orders_username, TestConfig.orders_password, key)

    out = message['meta']
    return out

# ################################################################################################################################

def _ack_order(meta:'anydict', publications:'anylist') -> 'anydict':
    """ Builds the acknowledgement of one pulled order with the given publications.
    """
    consumed = {
        'msg_id': meta['msg_id'],
        'delivery_attempt': meta['delivery_attempt'],
    }

    out:'anydict' = {
        'consumed': [consumed],
        'publish': publications,
    }

    return out

# ################################################################################################################################

def _send_ack(payload:'anydict') -> 'HTTPResult':
    """ Sends an acknowledgement as the orders client and returns the response.
    """
    out = ack(TestConfig.orders_username, TestConfig.orders_password, payload)
    return out

# ################################################################################################################################

def _drain_verifier() -> 'strlist':
    """ Pulls and acknowledges everything that the verifier received, and returns the message ID of each message.
    """
    messages = drain(TestConfig.verifier_username, TestConfig.verifier_password)

    out:'strlist' = []

    for message in messages:
        meta = message['meta']
        out.append(meta['msg_id'])

    return out

# ################################################################################################################################

def _drain_queues() -> 'None':
    """ Removes what the earlier tests left in the queues of the orders client and of the verifier.
    """
    _ = drain(TestConfig.orders_username, TestConfig.orders_password)
    _ = _drain_verifier()

# ################################################################################################################################
# ################################################################################################################################

def test_publication_conflict(zato_server:'any_') -> 'None':
    """ A publication that reuses a message ID with different data is a conflict, and only the original is received.
    """
    _drain_queues()

    _, keys = new_keys(1)
    key = keys[0]
    msg_id = f'{key}.order'

    original:'anydict' = {'data': {'key': key, 'order': 'original'}, 'msg_id': msg_id}
    different:'anydict' = {'data': {'key': key, 'order': 'different'}, 'msg_id': msg_id}

    first = publish(TestConfig.publisher_username, TestConfig.publisher_password, _orders_topic, original)
    second = publish(TestConfig.publisher_username, TestConfig.publisher_password, _orders_topic, different)

    assert first.status_code == OK, first
    assert second.status_code == CONFLICT, second

    # The orders client receives the original alone.
    messages = drain(TestConfig.orders_username, TestConfig.orders_password)
    message_count = len(messages)

    assert message_count == 1, messages

    message = messages[0]
    data = message['data']

    assert data['order'] == 'original'

# ################################################################################################################################

def test_publication_input_checks(zato_server:'any_') -> 'None':
    """ A publication with a message ID that does not match the pattern of message IDs is rejected and nothing is stored.
    """
    _, keys = new_keys(1)
    key = keys[0]

    too_long_msg_id = 'm' * (_max_msg_id_length + 1)

    for msg_id in (_invalid_msg_id, too_long_msg_id):

        payload:'anydict' = {'data': {'key': key}, 'msg_id': msg_id}
        result = publish(TestConfig.publisher_username, TestConfig.publisher_password, _orders_topic, payload)

        assert result.status_code == BAD_REQUEST, result

    msg_ids = [_invalid_msg_id, too_long_msg_id]
    assert pubsub_db.count_message_rows(msg_ids) == 0

# ################################################################################################################################

def test_full_cycle(zato_server:'any_') -> 'None':
    """ A pull client acknowledges an order and publishes an invoice and an audit record in one call,
    and the verifier receives each publication once.
    """
    _drain_queues()

    _, keys = new_keys(1)
    key = keys[0]

    order_msg_id = _publish_order(key)
    meta = _pull_order(key)

    publications:'anylist' = [
        {'topic_name': _invoices_topic, 'data': {'key': key, 'invoice': 1}},
        {'topic_name': _audit_topic, 'data': {'key': key, 'audit': 'order invoiced'}},
    ]

    payload = _ack_order(meta, publications)
    response = _send_ack(payload)

    # The order is acknowledged and both publications are committed ..
    assert response.status_code == OK, response
    assert response.body['ack_count'] == 1, response

    published = response.body['published']
    published_count = len(published)

    assert published_count == 2, response

    # .. the orders queue has nothing left of the order ..
    engine = get_engine()
    assert count_deliveries(engine, order_msg_id) == 0

    # .. and the verifier receives each publication once.
    received = _drain_verifier()
    assert sorted(received) == sorted(published), received

# ################################################################################################################################

def test_stale_copy(zato_server:'any_') -> 'None':
    """ A copy whose lease ran out and whose message was handed out again cannot commit, while the later copy can,
    and the verifier receives only the publications of the later copy.
    """
    _drain_queues()

    _, keys = new_keys(1)
    key = keys[0]

    _ = _publish_order(key)

    # The first copy pulls the order and is held up past its lease ..
    stale_meta = _pull_order(key)
    time.sleep(_lease_wait_seconds)

    # .. so the second copy pulls it again ..
    current_meta = _pull_order(key)

    assert current_meta['delivery_attempt'] == stale_meta['delivery_attempt'] + 1

    stale_publications:'anylist' = [{'topic_name': _invoices_topic, 'data': {'key': key, 'copy': 'stale'}}]
    current_publications:'anylist' = [{'topic_name': _invoices_topic, 'data': {'key': key, 'copy': 'current'}}]

    # .. the first copy cannot commit ..
    stale_payload = _ack_order(stale_meta, stale_publications)
    stale_response = _send_ack(stale_payload)

    assert stale_response.status_code == CONFLICT, stale_response

    # .. while the second one can ..
    current_payload = _ack_order(current_meta, current_publications)
    current_response = _send_ack(current_payload)

    assert current_response.status_code == OK, current_response

    # .. and the verifier receives what the second copy published alone.
    received = _drain_verifier()
    assert received == current_response.body['published'], received

# ################################################################################################################################

def test_lost_reply(zato_server:'any_') -> 'None':
    """ An acknowledgement sent again after its reply was lost succeeds, and each publication is received once.
    """
    _drain_queues()

    _, keys = new_keys(1)
    key = keys[0]

    order_msg_id = _publish_order(key)
    meta = _pull_order(key)

    # The publications have message IDs derived from the order, so that a repeated call repeats them ..
    invoice_msg_id = f'{order_msg_id}.invoice'
    audit_msg_id = f'{order_msg_id}.audit'

    publications:'anylist' = [
        {'topic_name': _invoices_topic, 'data': {'key': key, 'invoice': 1}, 'msg_id': invoice_msg_id},
        {'topic_name': _audit_topic, 'data': {'key': key, 'audit': 'order invoiced'}, 'msg_id': audit_msg_id},
    ]

    payload = _ack_order(meta, publications)

    # .. both calls succeed with the same message IDs ..
    first = _send_ack(payload)
    second = _send_ack(payload)

    expected = [invoice_msg_id, audit_msg_id]

    for response in (first, second):
        assert response.status_code == OK, response
        assert response.body['published'] == expected, response

    # .. and the verifier receives each publication once.
    received = _drain_verifier()
    assert sorted(received) == sorted(expected), received

# ################################################################################################################################

def test_ack_input_checks(zato_server:'any_') -> 'None':
    """ An acknowledgement with invalid input, or with a publication that the client may not make, is rejected
    and the consumed message remains in the queue.
    """
    _drain_queues()

    _, keys = new_keys(1)
    key = keys[0]

    order_msg_id = _publish_order(key)
    meta = _pull_order(key)

    consumed = {
        'msg_id': meta['msg_id'],
        'delivery_attempt': meta['delivery_attempt'],
    }

    invoice:'anydict' = {'topic_name': _invoices_topic, 'data': {'key': key}}

    too_many:'anylist' = []

    for _ in range(_max_elements + 1):
        too_many.append(consumed)

    non_integer_attempt = {'msg_id': meta['msg_id'], 'delivery_attempt': '1'}

    # Each request with the status that it is rejected with
    requests:'anylist' = [
        ({'msg_ids': [order_msg_id], 'consumed': [consumed]}, BAD_REQUEST),
        ({}, BAD_REQUEST),
        ({'consumed': too_many}, BAD_REQUEST),
        ({'consumed': [non_integer_attempt]}, BAD_REQUEST),
        ({'consumed': [consumed], 'publish': [{'topic_name': _orders_topic, 'data': {'key': key}}]}, UNAUTHORIZED),
        ({'consumed': [consumed], 'publish': [{'topic_name': _inactive_topic, 'data': {'key': key}}]}, FORBIDDEN),
        ({'consumed': [consumed], 'publish': [{'topic_name': _invoices_topic}]}, BAD_REQUEST),
        ({'consumed': [consumed], 'publish': [invoice, {'topic_name': _invoices_topic}]}, BAD_REQUEST),
    ]

    engine = get_engine()

    for payload, status_code in requests:
        response = _send_ack(payload)

        assert response.status_code == status_code, (payload, response)
        assert count_deliveries(engine, order_msg_id) == 1, payload

    # Nothing was published by any of the requests ..
    received = _drain_verifier()
    assert received == [], received

    # .. and the order is acknowledged now, so that it does not remain for the other tests.
    final_payload = {'msg_ids': [order_msg_id]}
    final_response = ack(TestConfig.orders_username, TestConfig.orders_password, final_payload)

    assert final_response.status_code == OK, final_response

# ################################################################################################################################
# ################################################################################################################################
