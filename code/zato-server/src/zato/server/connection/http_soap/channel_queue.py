# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A REST or SOAP channel whose queue is on - the request goes to the channel's queue and the caller gets an acknowledgement.

# stdlib
import logging
from http.client import OK
from urllib.parse import urlencode

# gevent
from gevent import spawn

# Zato
from zato.common.api import CHANNEL, CONTENT_TYPE, HTTP_SOAP, URL_TYPE
from zato.common.json_ import dumps
from zato.common.pubsub.outgoing import Attempts_None, Body_Mode_JSON, Body_Mode_XML, decode_payload, detect_body_mode, \
    http_soap_inbound_types, Key_Data, Key_Data_Format, Key_Headers, Key_Is_Base64, Key_Method, Key_Params, Key_Path, \
    Key_Path_Params, Key_Service, Key_Transport, OutgoingPublisher
from zato.common.soap.message import SOAPMessage
from zato.common.typing_ import cast_
from zato.common.util.api import make_cid_public
from zato.server.connection.http_soap.channel_soap import build_soap_response
from zato.server.reqresp.response import Response
from zato.server.service import Invoke_Mode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, callable_, stranydict, strdict, strstrdict
    from zato.server.base.config_manager import ConfigManager
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato_rest')

_queue = HTTP_SOAP.Queue

_transport_soap = URL_TYPE.SOAP

_content_type_json = CONTENT_TYPE['JSON']
_content_type_xml  = CONTENT_TYPE['PLAIN_XML']
_content_type_text = 'text/plain'

# A SOAP channel always answers in XML
_content_type_soap = 'text/xml'

# The Content-Type of a static response, by what the response opens with
_content_type_by_body_mode = {
    Body_Mode_JSON: _content_type_json,
    Body_Mode_XML: _content_type_xml,
}

# The WSGI keys of the two headers that have no HTTP_ prefix in the request context
_wsgi_content_type   = 'CONTENT_TYPE'
_wsgi_content_length = 'CONTENT_LENGTH'

_header_content_type   = 'content-type'
_header_content_length = 'content-length'

_wsgi_header_prefix = 'HTTP_'

# ################################################################################################################################
# ################################################################################################################################

def extract_request_headers(request_ctx:'stranydict') -> 'strstrdict':
    """ The headers of the request as a service reads them in self.request.http.headers, lower-case and dash-separated,
    with the two content headers WSGI keeps outside the prefixed ones.
    """
    out:'strstrdict' = {}

    for key, value in request_ctx.items():
        if key.startswith(_wsgi_header_prefix):
            header_name = key[len(_wsgi_header_prefix):].replace('_', '-').lower()
            out[header_name] = value

    if _wsgi_content_type in request_ctx:
        out[_header_content_type] = request_ctx[_wsgi_content_type]

    if _wsgi_content_length in request_ctx:
        out[_header_content_length] = request_ctx[_wsgi_content_length]

    return out

# ################################################################################################################################

def headers_to_request_ctx(headers:'strstrdict') -> 'strstrdict':
    """ The reverse of extract_request_headers - the WSGI keys a request context carries the headers under.
    """
    out:'strstrdict' = {}

    for header_name, value in headers.items():

        if header_name == _header_content_type:
            out[_wsgi_content_type] = value

        elif header_name == _header_content_length:
            out[_wsgi_content_length] = value

        else:
            key = _wsgi_header_prefix + header_name.replace('-', '_').upper()
            out[key] = value

    return out

# ################################################################################################################################

def build_channel_request(
    channel_item:'anydict',
    request_ctx:'stranydict',
    payload:'bytes',
    query_params:'anydict',
    url_match:'anydict',
) -> 'stranydict':
    """ The request part of the envelope a channel's queue stores - everything the service needs to run later
    as if the request had just arrived.
    """
    data, is_base64 = decode_payload(payload)

    out = {
        Key_Service: channel_item['service_name'],
        Key_Method: request_ctx['REQUEST_METHOD'],
        Key_Path: request_ctx['PATH_INFO'],
        Key_Path_Params: dict(url_match),
        Key_Params: query_params,
        Key_Headers: extract_request_headers(request_ctx),
        Key_Data: data,
        Key_Is_Base64: is_base64,
        Key_Data_Format: channel_item['data_format'],
        Key_Transport: channel_item['transport'],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

def build_default_ack(cid:'str', channel_item:'anydict', request_ctx:'stranydict') -> 'Response':
    """ The acknowledgement a queued request gets when neither the hook nor a static response shapes it -
    the public cid in JSON on a REST channel and in an envelope of the request's version on a SOAP channel.
    """
    out = Response()
    out.status_code = OK

    pub_cid = make_cid_public(cid)

    if channel_item['transport'] == _transport_soap:

        message = SOAPMessage()
        setattr(message, _queue.Ack_Is_OK, True)
        setattr(message, _queue.Ack_CID, pub_cid)

        soap_context = request_ctx['zato.request.soap']
        body, content_type = build_soap_response(soap_context, message)

        out.payload = body
        out.content_type = content_type

    else:
        ack = {
            _queue.Ack_Is_OK: True,
            _queue.Ack_CID: pub_cid,
        }

        out.payload = dumps(ack)
        out.content_type = _content_type_json

    return out

# ################################################################################################################################

def build_static_response(channel_item:'anydict') -> 'Response':
    """ The static response a channel's queue_response setting gives every queued request, verbatim,
    with a Content-Type by what it opens with - always XML on a SOAP channel.
    """
    out = Response()
    out.status_code = OK

    queue_response = channel_item[_queue.Field_Queue_Response]
    out.payload = queue_response

    if channel_item['transport'] == _transport_soap:
        content_type = _content_type_soap
    else:
        body_mode = detect_body_mode(queue_response)

        if body_mode in _content_type_by_body_mode:
            content_type = _content_type_by_body_mode[body_mode]
        else:
            content_type = _content_type_text

    out.content_type = content_type

    return out

# ################################################################################################################################
# ################################################################################################################################

class QueuedChannelHandler:
    """ Handles one request of a channel whose queue is on - stores it first, then shapes the response.
    """

    def __init__(self, server:'ParallelServer', set_response_func:'callable_', flatten_query_string:'callable_') -> 'None':
        self.server = server

        # What the request handler sets a service's response with, so the hook's response is shaped as any other
        self.set_response_func = set_response_func

        # How the request handler reads a query string into the parameters a service sees
        self.flatten_query_string = flatten_query_string

# ################################################################################################################################

    def _run_hook(
        self,
        cid:'str',
        service:'any_',
        payload:'any_',
        channel_item:'anydict',
        request_ctx:'stranydict',
        config_manager:'ConfigManager',
        url_match:'anydict',
        channel_params:'anydict',
        zato_response_headers_container:'stranydict',
        msg_id:'str',
    ) -> 'Response':
        """ Runs the service's get_queue_response hook alone, with the id of the message the queue has just stored.
        """
        out = service.update_handle(self.set_response_func, service, payload,
            CHANNEL.HTTP_SOAP, channel_item['data_format'], channel_item['transport'], self.server,
            cast_('any_', config_manager.config_dispatcher),
            config_manager, cid, request_ctx=request_ctx,
            url_match=url_match, channel_item=channel_item, channel_params=channel_params,
            merge_channel_params=channel_item['merge_url_params_req'],
            params_priority=channel_item['params_pri'],
            zato_response_headers_container=zato_response_headers_container,
            invoke_mode=Invoke_Mode.Queue_Response_Only,
            queue_msg_id=msg_id)

        return out

# ################################################################################################################################

    def handle(
        self,
        cid:'str',
        service_class:'any_',
        payload:'any_',
        raw_request:'bytes',
        url_match:'anydict',
        channel_item:'anydict',
        request_ctx:'stranydict',
        config_manager:'ConfigManager',
        channel_params:'anydict',
        zato_response_headers_container:'stranydict',
    ) -> 'Response':
        """ Stores the request in the channel's queue and returns what the caller is to receive - what the hook produced
        if the service has one, else the channel's static response if it has one, else the default acknowledgement.
        The service is instantiated only if it has the hook, a service without one costs the channel nothing.
        """
        inbound_type = http_soap_inbound_types[channel_item['transport']]
        channel_id = channel_item['id']

        # The query string as the service would read it in self.request.http.GET
        query_params = self.flatten_query_string(request_ctx.get('QUERY_STRING', ''))

        request = build_channel_request(channel_item, request_ctx, raw_request, query_params, url_match)

        # The message is stored before anything about the response is decided - a publish that raises
        # goes to the caller as a 500 like any other failure, with no acknowledgement.
        publisher = OutgoingPublisher(self.server, inbound_type, channel_id)
        result = publisher.publish_request(cid, Attempts_None, request)
        msg_id = result.msg_id

        logger.info('Request queued -> channel:`%s`, msg_id:`%s`, cid:`%s`', channel_item['name'], msg_id, cid)

        # A service with the hook shapes the response in a greenlet of its own, so the delivery
        # of the message it has just been told about may already be running alongside it ..
        if service_class.has_get_queue_response:

            service, _ = self.server.service_store.new_instance(channel_item['service_impl_name'])

            hook = spawn(self._run_hook, cid, service, payload, channel_item, request_ctx, config_manager,
                url_match, channel_params, zato_response_headers_container, msg_id)

            out = hook.get()

        # .. a channel with a static response returns it verbatim ..
        elif channel_item[_queue.Field_Queue_Response]:
            out = build_static_response(channel_item)

        # .. and otherwise the caller learns that the request is in and what its cid is.
        else:
            out = build_default_ack(cid, channel_item, request_ctx)

        return out

# ################################################################################################################################
# ################################################################################################################################

def build_delivery_request_ctx(channel_item:'anydict', request:'stranydict') -> 'stranydict':
    """ The request context a queued request is delivered with, so the service reads self.request.http,
    self.request.headers and self.channel as it would had the request just arrived.
    """
    headers:'strdict' = request[Key_Headers]
    query_params = request[Key_Params]

    out:'stranydict' = {}
    out.update(headers_to_request_ctx(headers))

    out['REQUEST_METHOD'] = request[Key_Method]
    out['PATH_INFO'] = request[Key_Path]

    # The query string alone is placed here - what the service reads as self.request.http.GET and .POST is built
    # out of it by create_channel_params under the channel's merge switch, the same as for a request that has
    # just arrived, so a channel with the switch off reads neither from the queue either.
    out['QUERY_STRING'] = _build_query_string(query_params)
    out['zato.http.path_params'] = request[Key_Path_Params]
    out['zato.request.headers'] = headers
    out['zato.channel_item'] = channel_item
    out['zato.http.response.headers'] = {}

    return out

# ################################################################################################################################

def _build_query_string(query_params:'anydict') -> 'str':
    """ The query string the flattened parameters came from - a list value is a repeated parameter.
    """
    out = urlencode(query_params, doseq=True)
    return out

# ################################################################################################################################
# ################################################################################################################################
