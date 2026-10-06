# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What SOAP channels tell the shared scenarios about themselves.

# stdlib
import os

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.audit_log.api import AuditSource
from zato.common.pubsub.outgoing import InboundType
from zato.common.soap.common import Content_Type, SOAP_Action_Header, SOAPVersion
from zato.common.soap.envelope import attach_body, build_envelope, parse_body, parse_envelope, to_bytes
from zato.common.soap.message import SOAPMessage

# Test support
from queue_delivery.channel.client import channel_url, post
from queue_delivery.channel.type_under_test import Channel_Static, Channel_Static_Text, Channel_Static_XML, \
    ChannelTypeUnderTest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strdict
    from queue_delivery.channel.client import ChannelResponse

# ################################################################################################################################
# ################################################################################################################################

_directory = os.path.dirname(__file__)
_queue = HTTP_SOAP.Queue

# The channels of the enmasse template, by key
Channels = {
    'plain':         'test.queue-delivery.channel.plain',
    'orders':        'test.queue-delivery.channel.orders',
    'no_retries':    'test.queue-delivery.channel.no-retries',
    'dlq_keep':      'test.queue-delivery.channel.dlq-keep',
    'no_dlq':        'test.queue-delivery.channel.no-dlq',
    'dlq_retry':     'test.queue-delivery.channel.dlq-retry',
    'dlq_forward':   'test.queue-delivery.channel.dlq-forward',
    'dlq_discard':   'test.queue-delivery.channel.dlq-discard',
    'static':        'test.queue-delivery.channel.static',
    'static_xml':    'test.queue-delivery.channel.static-xml',
    'static_text':   'test.queue-delivery.channel.static-text',
    'hooked':        'test.queue-delivery.channel.hooked',
    'hooked_static': 'test.queue-delivery.channel.hooked-static',
    'slow_hook':     'test.queue-delivery.channel.slow-hook',
    'counting':      'test.queue-delivery.channel.counting',
}

# The URL path of each channel, as the template declares them
URL_Paths = {
    'plain':         '/soap/channel/plain',
    'orders':        '/soap/channel/orders',
    'no_retries':    '/soap/channel/no-retries',
    'dlq_keep':      '/soap/channel/dlq-keep',
    'no_dlq':        '/soap/channel/no-dlq',
    'dlq_retry':     '/soap/channel/dlq-retry',
    'dlq_forward':   '/soap/channel/dlq-forward',
    'dlq_discard':   '/soap/channel/dlq-discard',
    'static':        '/soap/channel/static',
    'static_xml':    '/soap/channel/static-xml',
    'static_text':   '/soap/channel/static-text',
    'hooked':        '/soap/channel/hooked',
    'hooked_static': '/soap/channel/hooked-static',
    'slow_hook':     '/soap/channel/slow-hook',
    'counting':      '/soap/channel/counting',
}

# The service each channel's queued requests go to, as the delivery page shows it
_target_service = 'test.queue-delivery.channel.target'
_hooked_service = 'test.queue-delivery.channel.hooked'

Services = {
    'plain':         _target_service,
    'orders':        _target_service,
    'no_retries':    _target_service,
    'dlq_keep':      _target_service,
    'no_dlq':        _target_service,
    'dlq_retry':     _target_service,
    'dlq_forward':   _target_service,
    'dlq_discard':   _target_service,
    'static':        _target_service,
    'static_xml':    _target_service,
    'static_text':   _target_service,
    'hooked':        _hooked_service,
    'hooked_static': _hooked_service,
    'slow_hook':     'test.queue-delivery.channel.slow-hook',
    'counting':      'test.queue-delivery.channel.counting',
}

Request_Method = 'POST'

# The operation every call invokes and the action the template declares for every channel
Request_Operation = 'SubmitOrder'
Request_SOAP_Action = 'urn:test:queue-delivery:submit'

# Every channel of the template speaks this version
Request_SOAP_Version = SOAPVersion.V11

_response_suffix = 'Response'
_content_type_soap = Content_Type[Request_SOAP_Version]

# A SOAP channel answers every static response in XML
_content_type_xml = 'text/xml'

# The element only a hooked service's response carries
_hook_text_key = 'text'

# How the text of an element reads back as the value that was serialized into it
_bool_texts = {
    'true': True,
    'false': False,
}

# ################################################################################################################################
# ################################################################################################################################

def value_from_text(text:'any_') -> 'any_':
    """ The value an element's text was serialized from - a boolean, an integer or the text itself.
    """
    if text in _bool_texts:
        return _bool_texts[text]

    if isinstance(text, str) and text.isdigit():
        return int(text)

    return text

# ################################################################################################################################

def document_from_message(message:'SOAPMessage') -> 'anydict':
    """ The children of a message as the flat document they were serialized from.
    """
    out = {}

    for name, value in message.to_dict().items():
        out[name] = value_from_text(value)

    return out

# ################################################################################################################################

def build_request(document:'anydict') -> 'bytes':
    """ A flat document as the envelope of a call - the operation element with one child per field.
    """
    message = SOAPMessage()

    for name, value in document.items():
        setattr(message, name, value)

    envelope = build_envelope(Request_SOAP_Version)
    _ = attach_body(envelope, message, Request_Operation)

    out = to_bytes(envelope)
    return out

# ################################################################################################################################

def read_operation_response(response:'ChannelResponse') -> 'SOAPMessage':
    """ The operation's response element of a response envelope.
    """
    envelope = parse_envelope(response.text.encode('utf-8'))
    body = parse_body(envelope)

    out = getattr(body, Request_Operation + _response_suffix)
    return out

# ################################################################################################################################
# ################################################################################################################################

class SOAPChannelType(ChannelTypeUnderTest):
    """ SOAP channels under test.
    """

    conn_type = InboundType.SOAP
    audit_source = AuditSource.SOAP_Channel
    suite_name = 'channel_soap'

    connections = Channels
    url_paths = URL_Paths

    template_path = os.path.join(_directory, '_enmasse_template.yaml')
    services_source = os.path.join(_directory, '_services.py')

    static_content_types = {
        Channel_Static: _content_type_xml,
        Channel_Static_XML: _content_type_xml,
        Channel_Static_Text: _content_type_xml,
    }

    ack_content_type = _content_type_xml
    request_method = Request_Method
    services = Services
    enmasse_section = 'channel_soap'

# ################################################################################################################################

    def path_params_of(self, order_id:'str') -> 'anydict':

        # The paths of SOAP channels carry no parameters
        out = {}
        return out

# ################################################################################################################################

    def call(self, key:'str', document:'anydict', headers:'strdict | None'=None, params:'strdict | None'=None) -> 'ChannelResponse':

        request_headers = {
            'Content-Type': _content_type_soap,
            SOAP_Action_Header: Request_SOAP_Action,
        }

        if headers:
            request_headers.update(headers)

        out = post(channel_url(key, params), build_request(document), request_headers)
        return out

# ################################################################################################################################

    def read_ack(self, response:'ChannelResponse') -> 'anydict':
        message = read_operation_response(response)
        document = document_from_message(message)

        out = {
            'is_ok': document[_queue.Ack_Is_OK],
            'cid': document[_queue.Ack_CID],
        }

        return out

# ################################################################################################################################

    def read_hook_response(self, response:'ChannelResponse') -> 'str':
        message = read_operation_response(response)
        document = document_from_message(message)

        out = document[_hook_text_key]
        return out

# ################################################################################################################################

    def read_plain_response(self, response:'ChannelResponse') -> 'anydict':
        message = read_operation_response(response)

        out = document_from_message(message)
        return out

# ################################################################################################################################

    def body_of_envelope_data(self, data:'any_') -> 'anydict':

        # The queue stores the envelope as it arrived, so the document is read out of its body
        envelope = parse_envelope(data.encode('utf-8'))
        body = parse_body(envelope)
        message = getattr(body, Request_Operation)

        out = document_from_message(message)
        return out

# ################################################################################################################################

    def check_received_request(self, received:'anydict', key:'str', document:'anydict') -> 'None':

        payload = {}
        for name, value in received['payload'].items():
            payload[name] = value_from_text(value)

        assert payload == document, received
        assert received['operation'] == Request_Operation, received
        assert received['soap_version'] == Request_SOAP_Version, received
        assert received['headers']['soapaction'] == Request_SOAP_Action, received
        assert received['content_type'] == _content_type_soap, received

# ################################################################################################################################

    def check_destination(self, key:'str', destination:'str') -> 'None':
        assert destination == f'{Request_Method} {URL_Paths[key]} -> {Services[key]}', destination

# ################################################################################################################################
# ################################################################################################################################

soap_channel_type = SOAPChannelType()

# ################################################################################################################################
# ################################################################################################################################
