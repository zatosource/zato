# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What REST channels tell the shared scenarios about themselves.

# stdlib
import os
from json import dumps, loads

# Zato
from zato.common.api import CONTENT_TYPE, HTTP_SOAP
from zato.common.audit_log.api import AuditSource
from zato.common.pubsub.outgoing import InboundType

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

# The URL path of each channel as a client calls it - the template declares each with an order_id path parameter,
# which every call fills in with the same value
Order_ID = 'ord-7'

URL_Paths = {
    'plain':         '/api/channel/plain/' + Order_ID,
    'orders':        '/api/channel/orders/' + Order_ID,
    'no_retries':    '/api/channel/no-retries/' + Order_ID,
    'dlq_keep':      '/api/channel/dlq-keep/' + Order_ID,
    'no_dlq':        '/api/channel/no-dlq/' + Order_ID,
    'dlq_retry':     '/api/channel/dlq-retry/' + Order_ID,
    'dlq_forward':   '/api/channel/dlq-forward/' + Order_ID,
    'dlq_discard':   '/api/channel/dlq-discard/' + Order_ID,
    'static':        '/api/channel/static/' + Order_ID,
    'static_xml':    '/api/channel/static-xml/' + Order_ID,
    'static_text':   '/api/channel/static-text/' + Order_ID,
    'hooked':        '/api/channel/hooked/' + Order_ID,
    'hooked_static': '/api/channel/hooked-static/' + Order_ID,
    'slow_hook':     '/api/channel/slow-hook/' + Order_ID,
    'counting':      '/api/channel/counting/' + Order_ID,
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

_content_type_json = CONTENT_TYPE['JSON']

# The element only a hooked service's response carries
_hook_text_key = 'text'

# ################################################################################################################################
# ################################################################################################################################

class RESTChannelType(ChannelTypeUnderTest):
    """ REST channels under test.
    """

    conn_type = InboundType.REST
    audit_source = AuditSource.REST_Channel
    suite_name = 'channel_rest'

    connections = Channels
    url_paths = URL_Paths

    template_path = os.path.join(_directory, '_enmasse_template.yaml')
    services_source = os.path.join(_directory, '_services.py')

    static_content_types = {
        Channel_Static: _content_type_json,
        Channel_Static_XML: CONTENT_TYPE['PLAIN_XML'],
        Channel_Static_Text: 'text/plain',
    }

    ack_content_type = _content_type_json
    request_method = Request_Method
    services = Services
    enmasse_section = 'channel_rest'

# ################################################################################################################################

    def path_params_of(self, order_id:'str') -> 'anydict':
        out = {'order_id': order_id}
        return out

# ################################################################################################################################

    def call(self, key:'str', document:'anydict', headers:'strdict | None'=None, params:'strdict | None'=None) -> 'ChannelResponse':

        request_headers = {'Content-Type': _content_type_json}

        if headers:
            request_headers.update(headers)

        body = dumps(document).encode('utf-8')

        out = post(channel_url(key, params), body, request_headers)
        return out

# ################################################################################################################################

    def read_ack(self, response:'ChannelResponse') -> 'anydict':
        document = loads(response.text)

        out = {
            'is_ok': document[_queue.Ack_Is_OK],
            'cid': document[_queue.Ack_CID],
        }

        return out

# ################################################################################################################################

    def read_hook_response(self, response:'ChannelResponse') -> 'str':
        document = loads(response.text)

        out = document['text']
        return out

# ################################################################################################################################

    def read_plain_response(self, response:'ChannelResponse') -> 'anydict':
        out = loads(response.text)
        return out

# ################################################################################################################################

    def body_of_envelope_data(self, data:'any_') -> 'anydict':
        out = loads(data)
        return out

# ################################################################################################################################

    def check_received_request(self, received:'anydict', key:'str', document:'anydict') -> 'None':
        assert received['payload'] == document, received
        assert received['content_type'] == _content_type_json, received

# ################################################################################################################################

    def check_destination(self, key:'str', destination:'str') -> 'None':
        assert destination == f'{Request_Method} {URL_Paths[key]} -> {Services[key]}', destination

# ################################################################################################################################
# ################################################################################################################################

rest_channel_type = RESTChannelType()

# ################################################################################################################################
# ################################################################################################################################
