# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import dataclasses
from http.client import NO_CONTENT, OK
from logging import getLogger

# Zato
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strdictlist, stranydict
    from zato.server.connection.mcp.registry import ToolRegistry
    from zato.server.service.store import ServiceStore

    ServiceStore = ServiceStore
    strdictlist = strdictlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

# JSON-RPC 2.0 error codes
_error_parse       = -32700
_error_invalid_req = -32600
_error_method_not_found = -32601
_error_invalid_params   = -32602

# JSON-RPC 2.0 version string
_jsonrpc_version = '2.0'

# MCP protocol version negotiated during initialize
_mcp_protocol_version = '2025-11-05'

# Server metadata returned in the initialize response
_server_name = 'Apache'
_server_version = '2.4'

# ################################################################################################################################
# ################################################################################################################################

@dataclasses.dataclass(init=False)
class MCPResponse:
    """ Wraps a JSON-RPC response body and its HTTP status code.
    """
    body: 'any_'
    status_code: 'int'

# ################################################################################################################################
# ################################################################################################################################

def _make_error_response(request_id:'any_', code:'int', message:'str') -> 'stranydict':
    """ Builds a JSON-RPC 2.0 error response.
    """

    out:'stranydict' = {
        'jsonrpc': _jsonrpc_version,
        'id': request_id,
        'error': {
            'code': code,
            'message': message,
        },
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

def _make_success_response(request_id:'any_', result:'any_') -> 'stranydict':
    """ Builds a JSON-RPC 2.0 success response.
    """

    out:'stranydict' = {
        'jsonrpc': _jsonrpc_version,
        'id': request_id,
        'result': result,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class MCPHandler:
    """ Handles MCP JSON-RPC 2.0 dispatch for a single MCP channel.
    Routes initialize, tools/list, tools/call, and ping methods.
    """
    def __init__(self, tool_registry:'ToolRegistry', invoke_func:'any_') -> 'None':
        self.tool_registry = tool_registry
        self.invoke_func = invoke_func

# ################################################################################################################################

    def handle_raw_request(self, raw_data:'bytes') -> 'MCPResponse':
        """ Parses raw bytes into JSON and dispatches.
        """

        # Our response to produce
        out = MCPResponse()

        # Try to parse the incoming data as JSON ..
        try:
            parsed = loads(raw_data)
        except Exception:
            logger.warning('MCP: Failed to parse JSON body', exc_info=True)

            out.body = _make_error_response(None, _error_parse, 'Parse error')
            out.status_code = OK
            return out

        # .. handle batch (array) vs single (object) ..
        if isinstance(parsed, list):

            out = self._handle_batch(parsed)
            return out

        if isinstance(parsed, dict):

            out.body = self._dispatch_single(parsed)
            out.status_code = OK
            return out

        # .. anything else is an invalid request.
        out.body = _make_error_response(None, _error_invalid_req, 'Invalid request')
        out.status_code = OK
        return out

# ################################################################################################################################

    def _handle_batch(self, messages:'list') -> 'MCPResponse':
        """ Handles a JSON-RPC batch request (array of messages).
        """

        # Our response to produce
        out = MCPResponse()

        # Empty array is an invalid request per the JSON-RPC spec ..
        if not messages:

            out.body = _make_error_response(None, _error_invalid_req, 'Invalid request: empty batch')
            out.status_code = OK
            return out

        # .. dispatch each message independently and collect responses for requests (not notifications).
        responses:'strdictlist' = []

        for message in messages:

            # Notifications have no 'id' field and produce no response ..
            if 'id' not in message:
                self._handle_notification(message)
                continue

            # .. requests produce a response.
            response = self._dispatch_single(message)
            responses.append(response)

        # If every message was a notification, return 204 ..
        if not responses:

            out.body = None
            out.status_code = NO_CONTENT
            return out

        # .. otherwise return the batch response array.
        out.body = responses
        out.status_code = OK
        return out

# ################################################################################################################################

    def _handle_notification(self, message:'anydict') -> 'None':
        """ Processes a JSON-RPC notification (no response expected).
        """

        method = message['method']

        # notifications/initialized is a no-op acknowledgment
        if method == 'notifications/initialized':
            logger.info('MCP: Received initialized notification')

        # .. log unknown notifications but do not error.
        else:
            logger.info('MCP: Received notification `%s`', method)

# ################################################################################################################################

    def _dispatch_single(self, message:'anydict') -> 'stranydict':
        """ Routes a single JSON-RPC request to the appropriate handler method.
        """

        # Validate basic JSON-RPC structure ..
        jsonrpc = message.get('jsonrpc')
        request_id = message.get('id')

        if jsonrpc != _jsonrpc_version:

            out = _make_error_response(request_id, _error_invalid_req, 'Invalid request: missing or wrong jsonrpc version')
            return out

        method = message.get('method')

        if not method:

            out = _make_error_response(request_id, _error_invalid_req, 'Invalid request: missing method')
            return out

        # Params is optional per JSON-RPC 2.0 spec - a client may omit it entirely
        params = message.get('params', {})

        # .. route to the handler for this method.
        if method == 'initialize':

            out = self._handle_initialize(request_id, params)
            return out

        if method == 'tools/list':

            out = self._handle_tools_list(request_id)
            return out

        if method == 'tools/call':

            out = self._handle_tools_call(request_id, params)
            return out

        if method == 'ping':

            out = self._handle_ping(request_id)
            return out

        # .. anything else is an unknown method.
        out = _make_error_response(request_id, _error_method_not_found, f'Method not found: `{method}`')
        return out

# ################################################################################################################################

    def _handle_initialize(self, request_id:'any_', params:'anydict') -> 'stranydict':
        """ Handles the MCP initialize request.
        Returns server capabilities and negotiated protocol version.
        """

        _ = params

        result:'stranydict' = {
            'protocolVersion': _mcp_protocol_version,
            'capabilities': {
                'tools': {
                    'listChanged': True,
                },
            },
            'serverInfo': {
                'name': _server_name,
                'version': _server_version,
            },
        }

        out = _make_success_response(request_id, result)
        return out

# ################################################################################################################################

    def _handle_tools_list(self, request_id:'any_') -> 'stranydict':
        """ Handles the MCP tools/list request.
        Returns the list of available tools from the tool registry.
        """

        tools = self.tool_registry.get_tools()

        result:'stranydict' = {
            'tools': tools,
        }

        out = _make_success_response(request_id, result)
        return out

# ################################################################################################################################

    def _handle_tools_call(self, request_id:'any_', params:'anydict') -> 'stranydict':
        """ Handles the MCP tools/call request.
        Validates the tool name against the allowlist, invokes the service,
        and wraps the response in MCP content format.
        """

        # Extract tool name from the params ..
        tool_name = params.get('name')

        if not tool_name:

            out = _make_error_response(request_id, _error_invalid_params, 'Missing required parameter: name')
            return out

        # .. check if the tool is allowed on this channel ..
        if not self.tool_registry.is_tool_allowed(tool_name):

            out = _make_error_response(request_id, _error_method_not_found, f'Tool not found: `{tool_name}`')
            return out

        # .. extract arguments - optional per the MCP spec, defaults to empty dict ..
        arguments = params.get('arguments', {})

        # .. invoke the service ..
        try:
            service_response = self.invoke_func(tool_name, arguments)
        except Exception as error:
            logger.warning('MCP: Service `%s` raised an exception', tool_name, exc_info=True)

            result:'stranydict' = {
                'content': [
                    {
                        'type': 'text',
                        'text': str(error),
                    },
                ],
                'isError': True,
            }

            out = _make_success_response(request_id, result)
            return out

        # .. wrap the successful response in MCP content format.
        response_text = self._serialize_service_response(service_response)

        result:'stranydict' = { # pyright: ignore[reportRedefinedVariable]
            'content': [
                {
                    'type': 'text',
                    'text': response_text,
                },
            ],
        }

        out = _make_success_response(request_id, result)
        return out

# ################################################################################################################################

    def _serialize_service_response(self, response:'any_') -> 'str':
        """ Converts a service response to a text string suitable for MCP content.
        """

        # If the response is already a string, return it directly ..
        if isinstance(response, str):

            out = response
            return out

        # .. if it is bytes, decode it ..
        if isinstance(response, bytes):

            out = response.decode('utf8')
            return out

        # .. otherwise serialize it to JSON.
        out = dumps(response)
        return out

# ################################################################################################################################

    def _handle_ping(self, request_id:'any_') -> 'stranydict':
        """ Handles the MCP ping request.
        """

        out = _make_success_response(request_id, {})
        return out

# ################################################################################################################################
# ################################################################################################################################
