# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http.client import OK
from json import dumps as json_dumps, loads as json_loads
from urllib.parse import parse_qsl

# Zato
from zato.common.api import HTTP_SOAP, URL_TYPE
from zato.common.marshal_.api import Model
from zato.server.openapi_console.spec import is_channel_visible, resolve_caller

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The Accept value used for channel matching - the relay accepts any content type, and the value
# is transformed the same way the HTTP channel dispatcher transforms incoming Accept headers.
_http_accept = HTTP_SOAP.ACCEPT.ANY.replace('*', HTTP_SOAP.ACCEPT.ANY_INTERNAL)
_http_accept = _http_accept.replace('/', 'HTTP_SEP')

# All relayed responses are JSON documents
_content_type = 'application/json'

# ################################################################################################################################
# ################################################################################################################################

def _find_channel(server:'ParallelServer', http_method:'str', url_path:'str') -> 'any_':
    """ Matches the method and path against REST channels, returning the path parameters and the channel,
    or a pair of Nones if there is no match or the matched channel is not one the console documents.
    """
    url_data = server.config_manager.request_dispatcher.url_data
    path_params, channel_item = url_data.match(url_path, http_method, _http_accept)

    # No channel responds at this path and method at all ..
    if channel_item is None:
        return None, None

    # .. only the kinds of channels the spec documents can be invoked through the relay,
    # which is the same eligibility the spec builder applies.
    if channel_item['connection'] != 'channel':
        return None, None

    if channel_item['transport'] != URL_TYPE.PLAIN_HTTP:
        return None, None

    if not channel_item['is_active']:
        return None, None

    if channel_item['is_internal']:
        return None, None

    if not channel_item['service_name']:
        return None, None

    return path_params, channel_item

# ################################################################################################################################

def _build_payload(fields:'anydict', path_params:'anydict') -> 'any_':
    """ Builds the payload for the target service out of the request body, the query string and the path parameters.
    """
    query_params = dict(parse_qsl(fields['query_string']))
    body = fields['body']

    # The body is JSON whenever possible, otherwise it is passed through as a string ..
    if body:
        try:
            payload = json_loads(body)
        except ValueError:
            payload = body
    else:
        payload = {}

    # .. query string and path parameters are merged into JSON object payloads.
    if isinstance(payload, dict):
        payload.update(query_params)
        payload.update(path_params)

    return payload

# ################################################################################################################################

def _serialize_response(response:'any_') -> 'str':
    """ Converts a service response to the string form carried on the reply stream.
    """
    # No response means an empty body ..
    if response is None:
        out = ''
        return out

    # .. bytes are decoded ..
    if isinstance(response, bytes):
        out = response.decode('utf8')
        return out

    # .. strings are passed through ..
    if isinstance(response, str):
        out = response
        return out

    # .. typed services reply with a dataclass model, which serializes through its own to_dict ..
    if isinstance(response, Model):
        response = response.to_dict()

    # .. and anything else is serialized to JSON.
    out = json_dumps(response)

    return out

# ################################################################################################################################

def handle_invoke(server:'ParallelServer', fields:'anydict') -> 'anydict':
    """ Builds a reply to an invoke command - a try-it request relayed by the console.
    The target service is invoked only if the caller is identified and has access to the matched channel.
    """
    # Our response to produce
    out = {'correlation_id': fields['correlation_id']}

    # Reject the request outright if the caller cannot be identified ..
    security_id, is_admin = resolve_caller(server, fields)

    if not security_id:
        if not is_admin:
            out['status'] = 'unauthorized'
            out['data'] = ''
            return out

    # .. match the method and path against REST channels ..
    path_params, channel_item = _find_channel(server, fields['http_method'], fields['url_path'])

    # .. an unknown path is reported as not found ..
    if channel_item is None:
        out['status'] = 'not_found'
        out['data'] = ''
        return out

    # .. admin callers can invoke every endpoint, other callers only what their identity
    # gives access to, and a channel the caller cannot see produces the same reply as an unknown path,
    # so that callers cannot probe for endpoints that are not theirs ..
    if not is_admin:
        if not is_channel_visible(channel_item, security_id):
            out['status'] = 'not_found'
            out['data'] = ''
            return out

    # .. build the payload and invoke the target service - the method travels in the WSGI environment
    # so that services with per-verb handlers, e.g. handle_GET, dispatch the same way they do over HTTP ..
    payload = _build_payload(fields, path_params)
    wsgi_environ = {'REQUEST_METHOD': fields['http_method']}
    response = server.invoke(channel_item['service_name'], payload, wsgi_environ=wsgi_environ)

    # .. and relay the response back to the console.
    data = _serialize_response(response)

    out['status'] = 'ok'

    # The reply goes onto a Redis stream, whose client library accepts plain ints only,
    # so the enum member cannot be sent as it is.
    out['http_status'] = OK.value

    out['content_type'] = _content_type
    out['data'] = data

    return out

# ################################################################################################################################
# ################################################################################################################################
