# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import NO_CONTENT, OK
from logging import getLogger

# Zato
from zato.common.api import MCP
from zato.server.connection.mcp.common import _error_invalid_params, _error_invalid_request, _error_method_not_found, \
    _jsonrpc_version, _message_invalid_params, _message_missing_jsonrpc_version, _message_missing_method, \
    _method_tools_call, _server_name, _server_version, make_error_response, make_success_response, MCPResponse

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, stranydict, strnone
    from zato.server.connection.mcp.handler import MCPHandler

    MCPHandler = MCPHandler

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

# The protocol revision this module implements - each request is self-contained
_protocol_version = MCP.Protocol_Version_Stateless

# JSON-RPC error code returned when an Mcp-* header does not agree with the request body
_error_header_mismatch = -32020

# JSON-RPC error code returned when a request asks for a protocol version this gateway does not speak
_error_unsupported_protocol_version = -32022

# The method that advertises supported protocol versions, capabilities and identity
_method_discover = 'server/discover'

# The method that lists the tools a gateway exposes
_method_tools_list = 'tools/list'

# The _meta key carrying the protocol version of a request
_meta_key_protocol_version = 'io.modelcontextprotocol/protocolVersion'

# The _meta key naming the server in each result
_meta_key_server_info = 'io.modelcontextprotocol/serverInfo'

# The resultType marker every ordinary result carries
_result_type_complete = 'complete'

# How long clients may cache a tools/list response for, in milliseconds
_tools_list_ttl_ms = 60_000

# Only the caller itself may cache a tools/list response, never a shared intermediary
_tools_list_cache_scope = 'private'

# ################################################################################################################################
# ################################################################################################################################

def resolve_protocol_version(protocol_version_header:'strnone', message:'anydict') -> 'strnone':
    """ Returns the protocol version a request asks for.
    The MCP-Protocol-Version header speaks for the whole HTTP request and takes precedence,
    otherwise the version may travel in the _meta object of the request's params.
    """

    # The header takes precedence when it is present ..
    if protocol_version_header:
        out = protocol_version_header
        return out

    # .. otherwise, look for the version in the params _meta object.
    params = message.get('params')

    if isinstance(params, dict):
        if meta := params.get('_meta'):
            if isinstance(meta, dict):
                out = meta.get(_meta_key_protocol_version)
                return out

    return None

# ################################################################################################################################
# ################################################################################################################################

def _decorate_result(body:'stranydict') -> 'None':
    """ Adds the fields every result of this protocol revision carries -
    the resultType marker and the server identity in _meta.
    Error responses have no result and are returned as they are.
    """

    if result := body.get('result'):
        result['resultType'] = _result_type_complete
        result['_meta'] = {
            _meta_key_server_info: {
                'name': _server_name,
                'version': _server_version,
            },
        }

# ################################################################################################################################
# ################################################################################################################################

def _handle_discover(request_id:'any_') -> 'stranydict':
    """ Handles the server/discover request - advertises the protocol versions
    this gateway speaks, its capabilities and its identity.
    """

    result:'stranydict' = {
        'protocolVersions': MCP.Protocol_Versions_Supported,
        'capabilities': {
            'tools': {},
        },
        'serverInfo': {
            'name': _server_name,
            'version': _server_version,
        },
    }

    out = make_success_response(request_id, result)
    return out

# ################################################################################################################################
# ################################################################################################################################

def dispatch(
    handler:'MCPHandler',
    message:'anydict',
    mcp_method_header:'strnone',
    mcp_name_header:'strnone',
    ) -> 'MCPResponse':
    """ Routes a single request of the stateless protocol revision to its handler.
    There are no sessions here - each request is self-contained - and the Mcp-Method
    and Mcp-Name headers must agree with what the request body says.
    """

    # Our response to produce
    out = MCPResponse()
    out.session_id = None

    request_id = message.get('id')

    # Validate basic JSON-RPC structure ..
    jsonrpc = message.get('jsonrpc')

    if jsonrpc != _jsonrpc_version:

        out.body = make_error_response(request_id, _error_invalid_request, _message_missing_jsonrpc_version)
        out.status_code = OK
        return out

    # .. the method is always required ..
    method = message.get('method')

    if not method:

        out.body = make_error_response(request_id, _error_invalid_request, _message_missing_method)
        out.status_code = OK
        return out

    # .. record what is being dispatched for the audit log ..
    out.method = method

    # .. the Mcp-Method header must agree with the method in the body ..
    if mcp_method_header != method:

        error_message = f'Header mismatch: Mcp-Method `{mcp_method_header}` does not match method `{method}`'
        out.body = make_error_response(request_id, _error_header_mismatch, error_message)
        out.status_code = OK
        return out

    # .. params are optional but must be an object when present ..
    params = message.get('params', {})

    if not isinstance(params, dict):

        out.body = make_error_response(request_id, _error_invalid_params, _message_invalid_params)
        out.status_code = OK
        return out

    # .. a message without an ID is a notification and produces no response ..
    if 'id' not in message:

        logger.info('MCP: Received notification `%s`', method)
        out.body = None
        out.status_code = NO_CONTENT
        return out

    # .. tools/call additionally needs its Mcp-Name header to agree with the tool name ..
    if method == _method_tools_call:

        tool_name = params.get('name')

        if isinstance(tool_name, str):
            out.tool_name = tool_name

        if mcp_name_header != tool_name:

            error_message = f'Header mismatch: Mcp-Name `{mcp_name_header}` does not match tool `{tool_name}`'
            out.body = make_error_response(request_id, _error_header_mismatch, error_message)
            out.status_code = OK
            return out

        body = handler._handle_tools_call(request_id, params)

    # .. server/discover advertises versions, capabilities and identity ..
    elif method == _method_discover:
        body = _handle_discover(request_id)

    # .. tools/list results carry their cache hints ..
    elif method == _method_tools_list:

        body = handler._handle_tools_list(request_id, params)

        if result := body.get('result'):
            result['ttlMs'] = _tools_list_ttl_ms
            result['cacheScope'] = _tools_list_cache_scope

    # .. anything else, including the initialize and ping of the session-based revision, is unknown here.
    else:
        error_message = f'Method not found: `{method}`'
        body = make_error_response(request_id, _error_method_not_found, error_message)

    # .. every result carries the resultType marker and the server identity.
    _decorate_result(body)

    out.body = body
    out.status_code = OK
    return out

# ################################################################################################################################
# ################################################################################################################################
