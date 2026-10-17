# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from base64 import b64encode
from json import dumps as json_dumps, loads as json_loads

# Zato
from zato.common.bearer_token_identity import Identity_Key
from zato.common.util.auth import enrich_with_sec_data
from zato.common.util.url_dispatcher import normalize_path_info, to_internal_accept
from zato.common.webapp.auth.auth_type import ConsoleAuthType
from zato.server.connection.http_soap.channel import Console_Caller_Key
from zato.server.openapi_console.caller import resolve_session
from zato.server.openapi_console.spec import get_accepted_security_id, is_channel_documented

# Zato - Rust
from zato_server_core.zato_server_core import build_response_head

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, stranydict, strlist
    from zato.server.base.parallel import ParallelServer
    from zato.server.openapi_console.caller import ConsoleCaller

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Request headers are WSGI keys with this prefix, e.g. HTTP_X_CORRELATION_ID for X-Correlation-ID
_header_key_prefix = 'HTTP_'

# The two request headers that WSGI names without the prefix
_content_length_key = 'CONTENT_LENGTH'
_unprefixed_header_keys = {'CONTENT_TYPE', _content_length_key}

# Request headers as the request context spells them
_accept_key = 'HTTP_ACCEPT'
_authorization_key = 'HTTP_AUTHORIZATION'
_connection_key = 'HTTP_CONNECTION'

# How the Authorization header introduces each kind of credentials
_basic_auth_prefix = 'Basic '
_bearer_token_prefix = 'Bearer '

# What a relayed request reports as its protocol and as the port of the browser, which the console does not receive
_server_protocol = 'HTTP/1.1'
_remote_port = 0

# Where the dispatcher records that the channel's rules disallow the caller's address
_dropped_key = 'zato.http.rate_limit.dropped'

# How the HTTP server writes the lines of a response's header block and each name and value in it
_head_encoding = 'latin-1'
_head_line_separator = '\r\n'
_head_header_separator = ': '

# The response header that names the content type, as the HTTP layer writes it
_header_content_type = 'content-type'

# ################################################################################################################################
# ################################################################################################################################

def _build_request_ctx(server:'ParallelServer', fields:'anydict') -> 'stranydict':
    """ Builds the request context of a relayed request, with the same keys that the HTTP server
    builds the request context of a request it receives with.
    """
    url_path = fields['url_path']
    query_string = fields['query_string']
    remote_addr = fields['remote_addr']
    body = fields['body'].encode('utf8')

    if query_string:
        raw_uri = f'{url_path}?{query_string}'
    else:
        raw_uri = url_path

    # Our response to produce
    out:'stranydict' = {
        'REQUEST_METHOD': fields['http_method'],
        'PATH_INFO': url_path,
        'QUERY_STRING': query_string,
        'RAW_URI': raw_uri,
        'SERVER_PROTOCOL': _server_protocol,
        'REMOTE_ADDR': remote_addr,
        'REMOTE_PORT': _remote_port,
        'zato.http.raw_request': body,
    }

    headers = json_loads(fields['headers'])

    for name, value in headers.items():
        key = name.upper().replace('-', '_')

        # WSGI names every header with a prefix except the content type and the content length ..
        if key not in _unprefixed_header_keys:
            key = _header_key_prefix + key

        out[key] = value

    # .. the length is that of the body itself, as the HTTP layer reports it ..
    if body:
        out[_content_length_key] = str(len(body))

    # .. and the address that the channel's rate limits and address rules apply to is that of the browser,
    # under each key that the server reads a client's address from.
    for key in server.client_address_headers:
        out[key] = remote_addr

    return out

# ################################################################################################################################

def _find_channel(server:'ParallelServer', request_ctx:'stranydict') -> 'any_':
    """ Returns the REST channel that the request reaches, matched the same way the HTTP dispatcher matches it,
    or None if there is no such channel or the console does not document it.
    """
    path_info = normalize_path_info(request_ctx['PATH_INFO'])

    # A request may carry no Accept header at all
    http_accept = to_internal_accept(request_ctx.get(_accept_key))

    _, channel_item = server.url_data.match(path_info, request_ctx['REQUEST_METHOD'], http_accept)

    # No channel responds to this request at all ..
    if channel_item is None:
        return None

    # .. and only the channels that documents describe can be invoked through the relay.
    if not is_channel_documented(channel_item):
        return None

    return channel_item

# ################################################################################################################################

def _get_apikey_header_keys(server:'ParallelServer', channel_item:'anydict') -> 'strlist':
    """ Returns the request context keys under which the channel's own API key definition and its security groups
    read an API key, each one under its own header.
    """
    out:'strlist' = []

    if channel_security_id := channel_item.get('security_id'):
        sec_def = server.url_data.apikey_get_by_id(channel_security_id)
        out.append(sec_def['header'])

    # Groups name their header only when they have API key members
    if security_groups_ctx := channel_item.get('security_groups_ctx'):
        if security_groups_ctx.apikey_header:
            out.append(security_groups_ctx.apikey_header)

    return out

# ################################################################################################################################

def _set_caller_credentials(
    server:'ParallelServer',
    request_ctx:'stranydict',
    channel_item:'anydict',
    caller:'ConsoleCaller',
    security_id:'int',
    ) -> 'None':
    """ Gives a relayed request the credentials of the signed-in caller, in the form in which the channel reads them,
    so that the channel's own security checks the request as it checks the request of a direct call.
    """
    url_data = server.url_data

    # An API key is sent in the header that the channel reads it from ..
    if caller.auth_type == ConsoleAuthType.API_Key:
        for key in _get_apikey_header_keys(server, channel_item):
            request_ctx[key] = caller.secret

    # .. a bearer token in the Authorization header ..
    elif caller.auth_type == ConsoleAuthType.Bearer_Token:
        request_ctx[_authorization_key] = _bearer_token_prefix + caller.secret

    # .. and so are the username and password of a Basic Auth definition ..
    elif url_data.basic_auth_get_by_id(security_id):
        credentials = f'{caller.username}:{caller.secret}'.encode('utf8')
        request_ctx[_authorization_key] = _basic_auth_prefix + b64encode(credentials).decode('ascii')

    # .. whereas the client ID and secret of a Bearer token definition are credentials that channels do not accept,
    # so the console's own check stands in for the channel's, and the request context receives what the channel's
    # security gives it - the definition, and its name as the identity when the channel's groups have members.
    else:
        sec_def = url_data.oauth_get_by_id(security_id)
        request_ctx[Console_Caller_Key] = True

        if security_groups_ctx := channel_item.get('security_groups_ctx'):
            if security_groups_ctx.has_members():
                request_ctx[Identity_Key] = sec_def['name']

        enrich_with_sec_data(request_ctx, sec_def, sec_def['sec_type'])

# ################################################################################################################################

def _parse_response_head(head:'bytes') -> 'str':
    """ Returns, as a JSON list of name and value pairs, the headers of a header block that the HTTP server writes,
    without its status line.
    """
    pairs:'anylist' = []

    lines = head.decode(_head_encoding).split(_head_line_separator)

    # The status line comes first and the blank line that ends the header block comes last
    for line in lines[1:]:
        if line:
            name, value = line.split(_head_header_separator, 1)
            pairs.append([name, value])

    out = json_dumps(pairs)
    return out

# ################################################################################################################################

def handle_invoke(server:'ParallelServer', fields:'anydict') -> 'anydict':
    """ Builds a reply to an invoke command - a try-it request relayed by the console.
    The request goes through the server's HTTP request handler only if the caller is identified and has access to the channel.
    """
    # Our response to produce
    out = {'correlation_id': fields['correlation_id']}

    # Reject the request outright if the caller cannot be identified ..
    caller = resolve_session(server, fields['session_token'])

    if caller is None:
        out['status'] = 'unauthorized'
        out['data'] = ''
        return out

    # .. find the channel that the request reaches ..
    request_ctx = _build_request_ctx(server, fields)
    channel_item = _find_channel(server, request_ctx)

    # .. an unknown path is reported as not found ..
    if channel_item is None:
        out['status'] = 'not_found'
        out['data'] = ''
        return out

    # .. admin callers can invoke every endpoint, which the channel's own security is not told about ..
    if caller.is_admin:
        request_ctx[Console_Caller_Key] = True

    # .. other callers only what their credentials give access to, and a channel the caller cannot see
    # produces the same reply as an unknown path, so that callers cannot probe for endpoints that are not theirs ..
    else:
        security_id = get_accepted_security_id(channel_item, caller.security_ids)

        if security_id is None:
            out['status'] = 'not_found'
            out['data'] = ''
            return out

        _set_caller_credentials(server, request_ctx, channel_item, caller, security_id)

    # .. the request goes through the same handler as each request that the server receives over HTTP ..
    status, headers, body = server.http_request_handler(request_ctx)

    # .. apart from a request from an address that the channel's rules disallow, which has no connection
    # for the dispatcher to drop, so the console reports it as no server having replied ..
    if _dropped_key in request_ctx:
        out['status'] = 'dropped'
        out['data'] = ''
        return out

    # .. a streaming response arrives in chunks, which the console receives as one body ..
    is_streaming = not isinstance(body, bytes)

    if is_streaming:
        body = b''.join(body)

    # .. with the headers that the HTTP server writes for the response on a connection.
    connection_header = request_ctx.get(_connection_key)
    head = build_response_head(status, headers, body, is_streaming, connection_header)

    status_code, _ = status.split(' ', 1)

    # Responses to requests that match no channel, among others, have no content type
    content_type = ''

    for name, value in headers.items():
        if name.lower() == _header_content_type:
            content_type = value

    out['status'] = 'ok'
    out['http_status'] = int(status_code)
    out['content_type'] = content_type

    # The reply stream carries text, so the body travels in Base64, which keeps each of its bytes as it is
    out['data'] = b64encode(body).decode('ascii')
    out['headers'] = _parse_response_head(head)

    return out

# ################################################################################################################################
# ################################################################################################################################
