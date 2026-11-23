# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK, SERVICE_UNAVAILABLE
from json import loads

# Zato
from zato.common.test.client import PublishClient

# Test support
from encoding_support import Delivery_Attempt_Key, EncodingConfig, new_escape_classes, new_payload, Retry_Subscriber, \
    Retry_Topic, wait_for_bodies

# ################################################################################################################################
# ################################################################################################################################

# The size of the payload, above the size of a body that the transport writes together with its head
_payload_size = 256 * 1024

# ################################################################################################################################
# ################################################################################################################################

def test_retry_after_a_failure() -> 'None':

    publisher = PublishClient(EncodingConfig.base_url, EncodingConfig.publisher_username, EncodingConfig.publisher_password)
    receiver = EncodingConfig.receiver_by_subscriber[Retry_Subscriber]

    prefix = new_escape_classes()
    data = new_payload(prefix, 'Invoice "2026-001" for Anna Miller\n', _payload_size)

    # The receiver rejects the first attempt and accepts the next one ..
    receiver.behavior.set_reject_503(auto_recover_after=1)

    result = publisher.publish(Retry_Topic, data)
    msg_id = result['msg_id']

    bodies = wait_for_bodies(receiver, 1)
    accepted = bodies[0]
    accepted = loads(accepted)

    rejected = receiver.behavior.rejected_bodies[0]
    rejected = loads(rejected)

    # .. both attempts have the same payload ..
    assert rejected['msg_id'] == msg_id
    assert accepted['msg_id'] == msg_id
    assert rejected['data'] == data
    assert accepted['data'] == data

    # .. the second one with its attempt incremented ..
    assert rejected[Delivery_Attempt_Key] == 1
    assert accepted[Delivery_Attempt_Key] == 2

    # .. in the body and in the headers alike.
    records = receiver.get_request_records()
    first_record, second_record = records

    assert first_record['status_code'] == SERVICE_UNAVAILABLE
    assert first_record[Delivery_Attempt_Key] == 1
    assert second_record['status_code'] == OK
    assert second_record[Delivery_Attempt_Key] == 2

# ################################################################################################################################
# ################################################################################################################################
