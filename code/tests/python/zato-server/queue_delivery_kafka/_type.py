# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What outgoing Kafka connections tell the shared harness about themselves.

# stdlib
import os
from json import dumps, loads

# Zato
from zato.common.audit_log.api import AuditSource
from zato.common.pubsub.outgoing import Key_Data, Key_Headers, Key_Is_Tombstone, Key_Key, Key_Partition, OutgoingType

# Test support
from queue_delivery.type_under_test import TypeUnderTest
from _receiver import KafkaRecordingReceiver

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

_directory = os.path.dirname(__file__)

# The connections of the enmasse template, by key
Connections = {
    'plain':       'test.queue-delivery.plain',
    'orders':      'test.queue-delivery.orders',
    'no_retries':  'test.queue-delivery.no-retries',
    'dlq_keep':    'test.queue-delivery.dlq-keep',
    'no_dlq':      'test.queue-delivery.no-dlq',
    'dlq_retry':   'test.queue-delivery.dlq-retry',
    'dlq_forward': 'test.queue-delivery.dlq-forward',
    'dlq_discard': 'test.queue-delivery.dlq-discard',
}

# The topic each connection writes to - one per connection, named after it
Topics = {key: name for key, name in Connections.items()}

# What the delivery page opens a message's destination with
Destination_Prefix = 'Kafka'

# What a send's error opens with when Kafka turned the message down - the connection's name follows
Refused_Error_Prefix = 'Kafka send through `test.queue-delivery.'

# What a send's error carries when nothing answered within the send's timeout - whether the connection or the bridge
# behind it is what gave up waiting
Down_Error_Text = 'timed out'

# The fields the request part of a queued envelope always holds
Envelope_Request_Keys = {Key_Data, Key_Key, Key_Headers, Key_Partition, Key_Is_Tombstone}

# ################################################################################################################################
# ################################################################################################################################

class KafkaType(TypeUnderTest):
    """ Outgoing Kafka connections under test.
    """

    conn_type = OutgoingType.KAFKA
    audit_source = AuditSource.Kafka_Outgoing
    suite_name = 'kafka'

    connections = Connections

    template_path = os.path.join(_directory, '_enmasse_template.yaml')
    services_source = os.path.join(_directory, '_services.py')

    receiver_class = KafkaRecordingReceiver

    refused_error_prefix = Refused_Error_Prefix
    down_error_text = Down_Error_Text

    # A ping is a look at the metadata of the instances - nothing the endpoint turns down
    read_can_be_refused = False

# ################################################################################################################################

    def body_of(self, request:'any_') -> 'any_':
        out = loads(request.body)
        return out

# ################################################################################################################################

    def body_of_envelope_data(self, data:'any_') -> 'any_':
        out = loads(data)
        return out

# ################################################################################################################################

    def envelope_data_of(self, document:'any_') -> 'str':
        out = dumps(document)
        return out

# ################################################################################################################################

    def check_envelope_request(self, request_part:'anydict', data:'any_') -> 'None':
        assert set(request_part) == Envelope_Request_Keys, request_part
        assert loads(request_part[Key_Data]) == data
        assert request_part[Key_Is_Tombstone] is False

# ################################################################################################################################

    def check_destination(self, conn_key:'str', destination:'str') -> 'None':
        assert destination == f'{Destination_Prefix} {Topics[conn_key]}', destination

# ################################################################################################################################
# ################################################################################################################################

kafka_type = KafkaType()

# ################################################################################################################################
# ################################################################################################################################
