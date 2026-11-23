# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.receiver import WebhookReceiver
    from zato.common.typing_ import byteslist, strlist

    receiver_list       = list[WebhookReceiver]
    strreceiverdict     = dict[str, WebhookReceiver]
    strreceiverlistdict = dict[str, receiver_list]

# ################################################################################################################################
# ################################################################################################################################

# The topics of the suite
Broadcast_Topic = 'encoding.broadcast'
Sizes_Topic     = 'encoding.sizes'
Edit_Topic      = 'encoding.edit'
Retry_Topic     = 'encoding.retry'

# How many REST push subscribers the broadcast topic has
Broadcast_Subscriber_Count = 50

# The subscribers of the topics other than the broadcast one, in the order of their receivers
Sizes_Subscriber   = 'encoding.sizes.receiver'
Held_Subscriber    = 'encoding.edit.held'
Retried_Subscriber = 'encoding.edit.retried'
Retry_Subscriber   = 'encoding.retry.receiver'

# The largest body the transport writes in the same buffer as the head of its request
Max_Inline_Body_Len = 64 * 1024

# The keys of a push envelope that precede its optional fields, in their order
Envelope_Leading_Keys = [
    'msg_id',
    'sequence_id',
    'topic_name',
    'data',
    'data_class',
    'data_size',
    'data_preview',
    'priority',
    'expiration',
    'pub_time_iso',
    'recv_time_iso',
    'expiration_time_iso',
]

# The header of a push request and the field of its envelope that hold the number of the attempt
Delivery_Attempt_Key = 'delivery_attempt'

# The field of a message that push delivery keeps out of the envelope
Delivery_ID_Key = 'delivery_id'

# How long a test waits for its deliveries, in seconds
Delivery_Timeout = 120.0

# How often a test checks for new deliveries, in seconds
_poll_interval = 0.2

# The control characters, which JSON strings escape
_control_characters_end = 0x20

# ################################################################################################################################
# ################################################################################################################################

class EncodingConfig:
    """ The server of the suite and its receivers, set once the server is ready.
    """
    base_url:'str' = ''
    invoke_password:'str' = ''

    publisher_username:'str' = ''
    publisher_password:'str' = ''

    # The receivers of each topic, in the order of their subscribers
    receivers:'strreceiverlistdict' = {}

    # The receiver of each subscriber
    receiver_by_subscriber:'strreceiverdict' = {}

# ################################################################################################################################
# ################################################################################################################################

def get_broadcast_subscribers() -> 'strlist':
    """ Returns the names of the subscribers of the broadcast topic.
    """
    out:'strlist' = []

    for index in range(1, Broadcast_Subscriber_Count + 1):
        name = f'{Broadcast_Topic}.{index:02d}'
        out.append(name)

    return out

# ################################################################################################################################

def new_escape_classes() -> 'str':
    """ Returns text with every class of characters that JSON escapes and with characters that it writes as they are.
    """
    out = 'Order "12345" for C:\\customers\\john.smith - '

    for code_point in range(_control_characters_end):
        out += chr(code_point)

    out += '\u2028\U0001F680 naïve café /path'
    return out

# ################################################################################################################################

def new_payload(prefix:'str', filler:'str', size:'int') -> 'str':
    """ Returns a payload of the given number of characters that starts with the prefix and repeats the filler after it.
    """
    filler_size = size - len(prefix)
    repeat_count = filler_size // len(filler) + 1
    filler = filler * repeat_count
    filler = filler[:filler_size]

    out = prefix + filler
    return out

# ################################################################################################################################

def read_raw_bodies(receiver:'WebhookReceiver') -> 'byteslist':
    """ Returns the raw body of each request that the receiver accepted, in the order of their arrival.
    """
    out:'byteslist' = []

    file_names = sorted(os.listdir(receiver.output_directory))

    for file_name in file_names:
        if not file_name.endswith('.json'):
            continue

        file_path = os.path.join(receiver.output_directory, file_name)

        with open(file_path, 'rb') as input_file:
            body = input_file.read()

        out.append(body)

    return out

# ################################################################################################################################

def wait_for_bodies(receiver:'WebhookReceiver', expected_count:'int', timeout:'float'=Delivery_Timeout) -> 'byteslist':
    """ Waits until the receiver accepted at least the given number of requests and returns their raw bodies.
    """
    deadline = time.monotonic() + timeout

    while True:
        out = read_raw_bodies(receiver)
        body_count = len(out)

        if body_count >= expected_count:
            break

        if time.monotonic() > deadline:
            break

        time.sleep(_poll_interval)

    return out

# ################################################################################################################################
# ################################################################################################################################
