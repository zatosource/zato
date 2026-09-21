# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What outgoing MLLP connections tell the shared harness about themselves.

# stdlib
import os

# Zato
from zato.common.audit_log.api import AuditEvent
from zato.common.pubsub.outgoing import Key_Data, OutgoingType

# Test support
from queue_delivery.type_under_test import TypeUnderTest
from _receiver import MLLPRecordingReceiver, Refuse_Code
from _services import build_message, document_of_message

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

# What the delivery page opens a message's destination with
Destination_Prefix = 'MLLP'

# ################################################################################################################################
# ################################################################################################################################

class MLLPType(TypeUnderTest):
    """ Outgoing MLLP connections under test.
    """

    conn_type = OutgoingType.MLLP
    suite_name = 'mllp'

    connections = Connections

    template_path = os.path.join(_directory, '_enmasse_template.yaml')
    services_source = os.path.join(_directory, '_services.py')

    receiver_class = MLLPRecordingReceiver

    # A refused message comes back as the code of its acknowledgment and what the connection makes of the code
    refused_error_prefix = f'{Refuse_Code} Application error ({Refuse_Code})'
    down_error_text = 'Connection refused'

    # A ping is a connection opened and closed again - nothing the endpoint can turn down
    read_can_be_refused = False

    audit_sent_event = AuditEvent.Message_Sent
    audit_received_event = AuditEvent.Ack_Received

# ################################################################################################################################

    def body_of(self, request:'any_') -> 'any_':
        out = document_of_message(request.body)
        return out

# ################################################################################################################################

    def body_of_envelope_data(self, data:'any_') -> 'any_':
        out = document_of_message(data)
        return out

# ################################################################################################################################

    def envelope_data_of(self, document:'any_') -> 'str':
        out = build_message(document)
        return out

# ################################################################################################################################

    def check_envelope_request(self, request_part:'anydict', data:'any_') -> 'None':
        assert list(request_part) == [Key_Data]
        assert document_of_message(request_part[Key_Data]) == data

# ################################################################################################################################

    def check_destination(self, conn_key:'str', destination:'str') -> 'None':
        assert destination.startswith(Destination_Prefix + ' 127.0.0.1:'), destination

# ################################################################################################################################
# ################################################################################################################################

mllp_type = MLLPType()

# ################################################################################################################################
# ################################################################################################################################
