# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What outgoing REST connections tell the shared harness about themselves.

# stdlib
import os
from http.client import SERVICE_UNAVAILABLE
from json import loads

# Zato
from zato.common.audit_log.api import AuditSource
from zato.common.pubsub.outgoing import Key_Data, Key_Method, Key_Params, OutgoingType

# Test support
from queue_delivery.type_under_test import TypeUnderTest
from _receiver import HTTPRecordingReceiver

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

# The URL path of each connection, as the template declares them
URL_Paths = {
    'plain':       '/api/plain',
    'orders':      '/api/orders',
    'no_retries':  '/api/no-retries',
    'dlq_keep':    '/api/dlq-keep',
    'no_dlq':      '/api/no-dlq',
    'dlq_retry':   '/api/dlq-retry',
    'dlq_forward': '/api/dlq-forward',
    'dlq_discard': '/api/dlq-discard',
}

# Every connection of the template sends with this method
Request_Method = 'POST'

# ################################################################################################################################
# ################################################################################################################################

class RESTType(TypeUnderTest):
    """ Outgoing REST connections under test.
    """

    conn_type = OutgoingType.REST
    audit_source = AuditSource.REST_Outgoing
    suite_name = 'rest'

    connections = Connections

    template_path = os.path.join(_directory, '_enmasse_template.yaml')
    services_source = os.path.join(_directory, '_services.py')

    receiver_class = HTTPRecordingReceiver

    refused_error_prefix = f'HTTP {SERVICE_UNAVAILABLE}'
    down_error_text = 'Connection error'

# ################################################################################################################################

    def check_envelope_request(self, request_part:'anydict', data:'any_') -> 'None':
        assert request_part[Key_Method] == Request_Method
        assert loads(request_part[Key_Data]) == data
        assert request_part[Key_Params] == {}

# ################################################################################################################################

    def check_destination(self, conn_key:'str', destination:'str') -> 'None':
        assert destination.startswith(Request_Method + ' http://127.0.0.1:'), destination
        assert URL_Paths[conn_key] in destination, destination

# ################################################################################################################################
# ################################################################################################################################

rest_type = RESTType()

# ################################################################################################################################
# ################################################################################################################################
