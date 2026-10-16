# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http import HTTPStatus
from http.client import INTERNAL_SERVER_ERROR
from json import dumps as json_dumps, loads as json_loads
from traceback import format_exc
from urllib.parse import parse_qsl

# Zato
from zato.common.api import HTTP_SOAP, URL_TYPE
from zato.common.exception import BackendInvocationError, BadRequest, ClientHTTPError
from zato.common.marshal_.api import Model, ModelValidationError
from zato.common.util.api import make_cid_public, new_cid_server
from zato.server.connection.http_soap.channel import get_deprecation_headers
from zato.server.openapi_console.spec import is_channel_visible, resolve_caller

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, stranydict, tuple_
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

# Relayed responses are JSON documents and error messages are plain text
_content_type = 'application/json'
_error_content_type = 'text/plain'

# The exceptions that services raise to reject a request, each with an HTTP status and a message of its own
_client_error_types = (ClientHTTPError, ModelValidationError)

# Of these, the ones whose message reaches the caller only when it was raised to be shown
_bad_request_types = (BadRequest, ModelValidationError, BackendInvocationError)

# The response headers of REST channels, named the way the channels and the HTTP layer name them
_header_cid            = 'X-Zato-CID'
_header_content_type   = 'Content-Type'
_header_content_length = 'content-length'
_header_connection     = 'connection'
_connection_keep_alive = 'keep-alive'

# Request headers are WSGI keys with this prefix, e.g. HTTP_X_CORRELATION_ID for X-Correlation-ID
_header_key_prefix = 'HTTP_'

# What a bad request raised without a message to show is reported as
_bad_request_message = 'Bad request'

# ################################################################################################################################
# ################################################################################################################################

def _find_channel(server:'ParallelServer', http_method:'str', url_path:'str') -> 'any_':
    """ Matches the method and path against REST channels, returning the path parameters and the channel,
    or a pair of Nones if there is no match or the matched channel is not one the console documents.
    """
    url_data = server.url_data
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

def _build_request_ctx(fields:'anydict') -> 'anydict':
    """ Builds the request context of the target service - the HTTP method and the caller's own headers,
    under the WSGI keys that the service's request object reads them from.
    """
    # Our response to produce
    out = {'REQUEST_METHOD': fields['http_method']}

    headers = json_loads(fields['headers'])

    for name, value in headers.items():
        key = _header_key_prefix + name.upper().replace('-', '_')
        out[key] = value

    return out

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

def _build_response_headers(
    server:'ParallelServer',
    cid:'str',
    channel_item:'anydict',
    content_type:'str',
    service_headers:'stranydict',
    data:'str',
    ) -> 'str':
    """ Returns, as a JSON list of name and value pairs, the response headers that the REST channel itself
    would send for this response, in the same order.
    """
    headers:'stranydict' = {}

    # The correlation ID comes first, if the server is configured to return it ..
    if server.needs_x_zato_cid:
        headers[_header_cid] = make_cid_public(cid)

    # .. deprecated channels announce their status on every response ..
    if channel_item.get('is_deprecated'):
        deprecation_headers = get_deprecation_headers(channel_item)
        headers.update(deprecation_headers)

    # .. followed by the content type and the service's own headers, which can replace it ..
    headers[_header_content_type] = content_type
    headers.update(service_headers)

    # .. and the HTTP layer adds the length of the body and the connection's state if the service did not.
    content_length = len(data.encode('utf8'))
    pairs:'anylist' = []

    for name, value in headers.items():
        pairs.append([name, value])

    pairs.append([_header_content_length, str(content_length)])
    pairs.append([_header_connection, _connection_keep_alive])

    out = json_dumps(pairs)
    return out

# ################################################################################################################################

def _describe_error(server:'ParallelServer', e:'Exception') -> 'tuple_[int, str]':
    """ Returns the HTTP status and the message that the service's REST channel would respond with for this exception.
    """
    # Errors raised for the caller have a status and a message of their own ..
    if isinstance(e, _client_error_types):
        http_status = e.status
        message = e.msg

        # .. though a bad request reveals its message only when it was raised with one ..
        if isinstance(e, _bad_request_types):
            if not e.needs_msg:
                message = _bad_request_message

    # .. while any other error is a server error, described only if the server returns tracebacks.
    else:
        http_status = INTERNAL_SERVER_ERROR

        if server.return_tracebacks:
            message = str(e)
        else:
            message = server.default_error_message

    # Statuses arrive as plain ints or as HTTPStatus members, e.g. from http.client,
    # and the reply goes onto a Redis stream, whose client library accepts plain ints only.
    status_code = HTTPStatus(http_status).value

    return status_code, message

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

    # .. build the payload and invoke the target service - the method travels in the request context
    # so that services with per-verb handlers, e.g. handle_GET, dispatch the same way they do over HTTP ..
    payload = _build_payload(fields, path_params)
    request_ctx = _build_request_ctx(fields)
    service_name = channel_item['service_name']

    out['status'] = 'ok'

    # .. the service fills this in with the response headers of its own ..
    cid = new_cid_server()
    service_headers:'stranydict' = {}

    # .. a service that raises is reported the way its REST channel reports it ..
    try:
        response = server.invoke(
            service_name, payload, request_ctx=request_ctx, cid=cid, zato_response_headers_container=service_headers)
    except Exception as e:
        logger.warning('OpenAPI console invocation of `%s` failed: %s', service_name, format_exc())
        http_status, message = _describe_error(server, e)
        out['http_status'] = http_status
        out['content_type'] = _error_content_type
        out['data'] = message
        out['headers'] = _build_response_headers(server, cid, channel_item, _error_content_type, service_headers, message)
        return out

    # .. and relay the response back to the console.
    data = _serialize_response(response)

    # The reply goes onto a Redis stream, whose client library accepts plain ints only,
    # so the enum member cannot be sent as it is.
    out['http_status'] = HTTPStatus.OK.value

    out['content_type'] = _content_type
    out['data'] = data
    out['headers'] = _build_response_headers(server, cid, channel_item, _content_type, service_headers, data)

    return out

# ################################################################################################################################
# ################################################################################################################################
