# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What outgoing FHIR connections tell the shared harness about themselves.

# stdlib
import os
from http.client import UNPROCESSABLE_ENTITY
from json import dumps, loads

# Zato
from zato.common.audit_log.api import AuditSource
from zato.common.pubsub.outgoing import Key_Data, Key_Method, Key_Params, Key_Path, OutgoingType

# Test support
from queue_delivery.type_under_test import TypeUnderTest
from _receiver import FHIRRecordingReceiver, Outcome_Diagnostics

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

# The resource type every send of the suite creates - the test services build their resources of it,
# so it is the path a send is posted to and the key a document travels under on top of what a scenario sent
Resource_Type = 'Patient'
Resource_Type_Key = 'resourceType'

# A resource is created by posting it under the path its own type names
Request_Method = 'POST'
Request_Path = Resource_Type

# ################################################################################################################################
# ################################################################################################################################

def document_from_resource(resource:'anydict') -> 'anydict':
    """ The flat document a scenario sent, which is the resource without the type the test service gave it.
    """
    out = dict(resource)
    _ = out.pop(Resource_Type_Key)

    return out

# ################################################################################################################################

def resource_from_document(document:'anydict') -> 'anydict':
    """ A flat document as the resource the test service sends it as.
    """
    out = dict(document)
    out[Resource_Type_Key] = Resource_Type

    return out

# ################################################################################################################################
# ################################################################################################################################

class FHIRType(TypeUnderTest):
    """ Outgoing FHIR connections under test.
    """

    conn_type = OutgoingType.FHIR
    audit_source = AuditSource.FHIR
    suite_name = 'fhir'

    connections = Connections

    template_path = os.path.join(_directory, '_enmasse_template.yaml')
    services_source = os.path.join(_directory, '_services.py')

    receiver_class = FHIRRecordingReceiver

    # A refused write comes back as its status and the diagnostics of the OperationOutcome it was answered with
    refused_error_prefix = f'HTTP {UNPROCESSABLE_ENTITY} {Outcome_Diagnostics}'
    down_error_text = 'Connection refused'

# ################################################################################################################################

    def body_of(self, request:'any_') -> 'any_':
        out = document_from_resource(loads(request.body))
        return out

# ################################################################################################################################

    def body_of_envelope_data(self, data:'any_') -> 'any_':
        out = document_from_resource(loads(data))
        return out

# ################################################################################################################################

    def envelope_data_of(self, document:'any_') -> 'str':
        out = dumps(resource_from_document(document))
        return out

# ################################################################################################################################

    def check_envelope_request(self, request_part:'anydict', data:'any_') -> 'None':
        assert request_part[Key_Method] == Request_Method
        assert request_part[Key_Path] == Request_Path
        assert document_from_resource(loads(request_part[Key_Data])) == data
        assert request_part[Key_Params] == {}

# ################################################################################################################################

    def check_destination(self, conn_key:'str', destination:'str') -> 'None':
        assert destination.startswith(Request_Method + ' http://127.0.0.1:'), destination
        assert destination.endswith('/' + Request_Path), destination

# ################################################################################################################################
# ################################################################################################################################

fhir_type = FHIRType()

# ################################################################################################################################
# ################################################################################################################################
