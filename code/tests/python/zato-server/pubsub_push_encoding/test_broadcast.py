# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads

# Zato
from zato.common.test.client import PublishClient
from zato.common.test.receiver import wait_until_receivers_quiet

# Test support
from encoding_support import Broadcast_Topic, Delivery_Attempt_Key, Delivery_ID_Key, EncodingConfig, Envelope_Leading_Keys, \
    Max_Inline_Body_Len, new_escape_classes, new_payload, read_raw_bodies, Sizes_Subscriber, Sizes_Topic, wait_for_bodies

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.receiver import WebhookReceiver
    from zato.common.typing_ import anydict, intlist, strlist, strstrdict

    strlistlist = list[strlist]

# ################################################################################################################################
# ################################################################################################################################

# The size of the payload of the broadcast, in characters
_large_payload_size = 8 * 1024 * 1024

# The size of the payload that measures how many bytes the envelope adds to its payload
_probe_payload_size = Max_Inline_Body_Len - 1024

# How many bytes the quotes add to a payload written as a JSON string
_quotes_len = 2

# How many messages the burst publishes
_burst_message_count = 200

# The text that the payloads repeat
_large_filler = 'Order "12345" for John Smith\n'
_plain_filler = 'Invoice 2026-001 for Anna Miller '

# ################################################################################################################################
# ################################################################################################################################

def _new_publisher() -> 'PublishClient':
    out = PublishClient(EncodingConfig.base_url, EncodingConfig.publisher_username, EncodingConfig.publisher_password)
    return out

# ################################################################################################################################

def _check_envelope(body:'bytes', msg_id:'str', data:'str') -> 'anydict':
    """ Checks that a push body is the envelope of the given message, with the keys in their order,
    and returns the envelope.
    """
    out = loads(body)
    keys = list(out)

    leading_key_count = len(Envelope_Leading_Keys)
    leading_keys = keys[:leading_key_count]

    assert leading_keys == Envelope_Leading_Keys
    assert Delivery_Attempt_Key in out
    assert Delivery_ID_Key not in out
    assert out['msg_id'] == msg_id
    assert out['data'] == data

    return out

# ################################################################################################################################

def _get_single_body(receiver:'WebhookReceiver') -> 'bytes':
    """ Returns the only body that the receiver accepted.
    """
    bodies = read_raw_bodies(receiver)
    body_count = len(bodies)

    assert body_count == 1

    out = bodies[0]
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_large_payload_reaches_every_subscriber() -> 'None':

    publisher = _new_publisher()
    receivers = EncodingConfig.receivers[Broadcast_Topic]

    prefix = new_escape_classes()
    data = new_payload(prefix, _large_filler, _large_payload_size)

    result = publisher.publish(Broadcast_Topic, data)
    msg_id = result['msg_id']

    # Each subscriber receives the message ..
    for receiver in receivers:
        _ = wait_for_bodies(receiver, 1)

    # .. exactly once ..
    wait_until_receivers_quiet(receivers)

    key_lists:'strlistlist' = []

    for receiver in receivers:
        body = _get_single_body(receiver)
        envelope = _check_envelope(body, msg_id, data)

        # .. with the attempt of the body equal to the one in the headers ..
        records = receiver.get_request_records()
        record_count = len(records)
        assert record_count == 1

        record = records[0]
        assert record[Delivery_Attempt_Key] == envelope[Delivery_Attempt_Key]

        keys = list(envelope)
        key_lists.append(keys)

    # .. and with the same keys in the same order for every subscriber.
    first_keys = key_lists[0]

    for keys in key_lists:
        assert keys == first_keys

# ################################################################################################################################

def test_sizes_around_the_inline_threshold() -> 'None':

    publisher = _new_publisher()
    receiver = EncodingConfig.receiver_by_subscriber[Sizes_Subscriber]

    # The envelope of a payload without characters to escape adds the same number of bytes to payloads of similar sizes ..
    probe = new_payload('', _plain_filler, _probe_payload_size)
    _ = publisher.publish(Sizes_Topic, probe)

    bodies = wait_for_bodies(receiver, 1)
    probe_body = bodies[0]

    envelope_len = len(probe_body) - len(probe) - _quotes_len

    # .. which makes it possible to publish payloads whose bodies are just below, at and just above the threshold.
    body_lens = (Max_Inline_Body_Len - 1, Max_Inline_Body_Len, Max_Inline_Body_Len + 1)
    published:'strstrdict' = {}

    for body_len in body_lens:
        payload_size = body_len - envelope_len - _quotes_len
        data = new_payload(f'Size {body_len} - ', _plain_filler, payload_size)

        result = publisher.publish(Sizes_Topic, data)
        msg_id = result['msg_id']
        published[msg_id] = data

    expected_count = len(body_lens) + 1
    bodies = wait_for_bodies(receiver, expected_count)

    received_lens:'intlist' = []

    for body in bodies[1:]:
        envelope = loads(body)
        msg_id = envelope['msg_id']
        data = published[msg_id]

        _ = _check_envelope(body, msg_id, data)

        body_len = len(body)
        received_lens.append(body_len)

    assert sorted(received_lens) == list(body_lens)

# ################################################################################################################################

def test_burst_of_messages() -> 'None':

    publisher = _new_publisher()
    receivers = EncodingConfig.receivers[Broadcast_Topic]

    prefix = new_escape_classes()
    published:'strstrdict' = {}

    # Each message of the burst has a payload of its own ..
    for index in range(_burst_message_count):
        data = f'{prefix} Order {index} for John Smith'

        result = publisher.publish(Broadcast_Topic, data)
        msg_id = result['msg_id']
        published[msg_id] = data

    # .. every subscriber receives all of them ..
    for receiver in receivers:
        _ = wait_for_bodies(receiver, _burst_message_count)

    wait_until_receivers_quiet(receivers)

    # .. intact and each one once.
    for receiver in receivers:
        bodies = read_raw_bodies(receiver)
        body_count = len(bodies)

        assert body_count == _burst_message_count

        received:'strstrdict' = {}

        for body in bodies:
            envelope = loads(body)
            msg_id = envelope['msg_id']

            _ = _check_envelope(body, msg_id, published[msg_id])
            received[msg_id] = envelope['data']

        assert received == published

# ################################################################################################################################
# ################################################################################################################################
