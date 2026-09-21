# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What outgoing SOAP connections tell the shared harness about themselves.

# stdlib
import os

# lxml
from lxml import etree

# Zato
from zato.common.audit_log.api import AuditSource
from zato.common.pubsub.outgoing import Key_Data, Key_Headers, Key_Operation, OutgoingType
from zato.common.soap.common import FaultCode
from zato.common.soap.message import serialize as serialize_soap_message, SOAPMessage
from zato.common.util.xml_.core import parse_xml

# Test support
from queue_delivery.type_under_test import TypeUnderTest
from _receiver import Fault_Reason, SOAPRecordingReceiver

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
    'plain':       '/services/plain',
    'orders':      '/services/orders',
    'no_retries':  '/services/no-retries',
    'dlq_keep':    '/services/dlq-keep',
    'no_dlq':      '/services/no-dlq',
    'dlq_retry':   '/services/dlq-retry',
    'dlq_forward': '/services/dlq-forward',
    'dlq_discard': '/services/dlq-discard',
}

# The operation every send of the suite invokes - the test services spell it the same way
Request_Operation = 'ProcessOrder'

# The version every connection of the template speaks
Request_SOAP_Version = '1.2'

# A queued message is the XML of its operation element
_xml_encoding = 'unicode'

# How the text of an element reads back as the value that was serialized into it
_bool_texts = {
    'true': True,
    'false': False,
}

# ################################################################################################################################
# ################################################################################################################################

def value_from_text(text:'str') -> 'any_':
    """ The value an element's text was serialized from - a boolean, an integer or the text itself.
    """
    if text in _bool_texts:
        return _bool_texts[text]

    if text.isdigit():
        return int(text)

    return text

# ################################################################################################################################

def document_from_xml(xml:'str') -> 'anydict':
    """ The children of an operation element as the flat document a scenario sent.
    """
    root = parse_xml(xml.encode('utf-8'))

    out = {}

    for child in root:
        name = etree.QName(child).localname
        out[name] = value_from_text(child.text)

    return out

# ################################################################################################################################

def xml_from_document(document:'anydict', operation:'str') -> 'str':
    """ A flat document as the XML of its operation element.
    """
    message = SOAPMessage()

    for name, value in document.items():
        setattr(message, name, value)

    element = serialize_soap_message(message, operation)

    out = etree.tostring(element, encoding=_xml_encoding)
    return out

# ################################################################################################################################
# ################################################################################################################################

class SOAPType(TypeUnderTest):
    """ Outgoing SOAP connections under test.
    """

    conn_type = OutgoingType.SOAP
    audit_source = AuditSource.SOAP_Outgoing
    suite_name = 'soap'

    connections = Connections

    template_path = os.path.join(_directory, '_enmasse_template.yaml')
    services_source = os.path.join(_directory, '_services.py')

    receiver_class = SOAPRecordingReceiver

    # A refused invocation comes back as a fault, which reads as its code and its reason
    refused_error_prefix = f'{FaultCode.Receiver} {Fault_Reason}'
    down_error_text = 'Connection refused'

# ################################################################################################################################

    def body_of(self, request:'any_') -> 'any_':
        out = document_from_xml(request.body)
        return out

# ################################################################################################################################

    def body_of_envelope_data(self, data:'any_') -> 'any_':
        out = document_from_xml(data)
        return out

# ################################################################################################################################

    def envelope_data_of(self, document:'any_') -> 'str':
        out = xml_from_document(document, Request_Operation)
        return out

# ################################################################################################################################

    def check_envelope_request(self, request_part:'anydict', data:'any_') -> 'None':
        assert request_part[Key_Operation] == Request_Operation
        assert document_from_xml(request_part[Key_Data]) == data
        assert request_part[Key_Headers] == {}

# ################################################################################################################################

    def check_destination(self, conn_key:'str', destination:'str') -> 'None':
        assert destination.startswith(Request_Operation + ' http://127.0.0.1:'), destination
        assert URL_Paths[conn_key] in destination, destination

# ################################################################################################################################
# ################################################################################################################################

soap_type = SOAPType()

# ################################################################################################################################
# ################################################################################################################################
