# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from json import loads

# Zato
from zato.common.test.client import AdminClient, PublishClient

# Test support
from encoding_support import Delivery_Attempt_Key, Delivery_Timeout, Edit_Topic, EncodingConfig, Held_Subscriber, \
    new_escape_classes, new_payload, Retried_Subscriber, wait_for_bodies

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.receiver import WebhookReceiver

# ################################################################################################################################
# ################################################################################################################################

# The size of the payloads, above the size of a body that the transport writes together with its head
_payload_size = 256 * 1024

# The service that replaces the payload of a message
_update_service = 'zato.pubsub.subscription.update-message'

# How often the test checks for a rejected attempt, in seconds
_poll_interval = 0.1

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_rejection(receiver:'WebhookReceiver') -> 'None':
    """ Waits until the receiver rejected at least one attempt.
    """
    deadline = time.monotonic() + Delivery_Timeout

    while receiver.behavior.reject_count == 0:
        assert time.monotonic() < deadline
        time.sleep(_poll_interval)

# ################################################################################################################################
# ################################################################################################################################

def test_edit_during_delivery() -> 'None':

    publisher = PublishClient(EncodingConfig.base_url, EncodingConfig.publisher_username, EncodingConfig.publisher_password)
    admin = AdminClient(EncodingConfig.base_url, EncodingConfig.invoke_password)

    held = EncodingConfig.receiver_by_subscriber[Held_Subscriber]
    retried = EncodingConfig.receiver_by_subscriber[Retried_Subscriber]

    prefix = new_escape_classes()
    original = new_payload(prefix, 'Order "12345" for John Smith\n', _payload_size)
    edited = new_payload(prefix, 'Order "12345" for Maria Johnson\n', _payload_size)

    # One subscriber holds the first push and the other one rejects every attempt ..
    held.behavior.set_gate()
    retried.behavior.set_reject_503()

    result = publisher.publish(Edit_Topic, original)
    msg_id = result['msg_id']

    # .. so the payload is escaped while both pushes of the original are in progress ..
    assert held.behavior.request_arrived.wait(Delivery_Timeout)
    _wait_for_rejection(retried)

    # .. then the message is edited ..
    request = {
        'msg_id': msg_id,
        'topic_name': Edit_Topic,
        'data': edited,
    }
    response = admin.invoke(_update_service, request)
    assert response['status'] == 'ok'

    # .. and both subscribers accept the next request.
    retried.behavior.set_accept()
    held.behavior.gate_released.set()

    # The push held since before the edit has the original ..
    held_bodies = wait_for_bodies(held, 1)
    held_body = held_bodies[0]
    held_envelope = loads(held_body)

    assert held_envelope['data'] == original

    # .. the first rejected attempt had it too ..
    first_rejected = retried.behavior.rejected_bodies[0]
    first_rejected = loads(first_rejected)

    assert first_rejected['data'] == original
    assert first_rejected[Delivery_Attempt_Key] == 1

    # .. and the attempt after the edit has the edited payload, never the escaped bytes of the original.
    retried_bodies = wait_for_bodies(retried, 1)
    retried_body = retried_bodies[0]
    retried_envelope = loads(retried_body)

    assert retried_envelope['msg_id'] == msg_id
    assert retried_envelope['data'] == edited
    assert retried_envelope[Delivery_Attempt_Key] > 1

# ################################################################################################################################
# ################################################################################################################################
