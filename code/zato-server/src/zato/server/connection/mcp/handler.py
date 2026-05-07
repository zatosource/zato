# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import dataclasses
from http.client import NO_CONTENT, NOT_FOUND, OK
from logging import getLogger

# Zato
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Generator
    from zato.common.typing_ import any_, anydict, strdictlist, stranydict, strnone
    from zato.server.connection.mcp.registry import ToolRegistry
    from zato.server.connection.mcp.session import MCPSessionManager
    from zato.server.service.store import ServiceStore

    Generator = Generator
    MCPSessionManager = MCPSessionManager
    ServiceStore = ServiceStore
    strdictlist = strdictlist

# Type alias for the SSE bytes generator
sse_bytes_gen = 'Generator[bytes, None, None]'

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

# HTTP status code for invalid/unknown session
_http_not_found = NOT_FOUND

# SSE data line prefix
_sse_data_prefix = b'data: '

# SSE line terminator
_sse_line_end = b'\n\n'

# ################################################################################################################################
# ################################################################################################################################

@dataclasses.dataclass(init=False)
class MCPResponse:
    """ Wraps a JSON-RPC response body, HTTP status code, and optional session ID.
    """
    body:         'any_'
    status_code:  'int'
    session_id:   'strnone'  = None
    is_streaming: 'bool'     = False

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
    def __init__(self, tool_registry:'ToolRegistry', invoke_func:'any_', session_manager:'MCPSessionManager') -> 'None':
        self.tool_registry = tool_registry
        self.invoke_func = invoke_func
        self.session_manager = session_manager
        self._pending_session_id:'strnone' = None

# ################################################################################################################################

    def handle_raw_request(self, raw_data:'bytes', session_id:'strnone'=None, remote_address:'str'='') -> 'MCPResponse':
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

        # .. if a session ID was provided, validate it ..
        if session_id:
            if not self.session_manager.validate(session_id):

                out.body = _make_error_response(None, _error_invalid_req, 'Invalid or expired session')
                out.status_code = _http_not_found
                return out

        # .. clear any pending session ID from a previous request
        # and store the remote address for session creation logging ..
        self._pending_session_id = None
        self._remote_address = remote_address

        # .. handle batch (array) vs single (object) ..
        if isinstance(parsed, list):

            out = self._handle_batch(parsed)
            out.session_id = self._pending_session_id
            return out

        if isinstance(parsed, dict):

            out.body = self._dispatch_single(parsed)
            out.status_code = OK
            out.session_id = self._pending_session_id
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

        method = message.get('method')

        if not method:
            logger.info('MCP: Received notification without a method, ignoring')
            return

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

            out = self._handle_tools_list(request_id, params)
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
        Creates a new session and stores its ID on _pending_session_id
        for handle_raw_request to pick up and set as a response header.
        """

        # Create a new session for this client ..
        self._pending_session_id = self.session_manager.create(_mcp_protocol_version, self._remote_address)

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

    def _handle_tools_list(self, request_id:'any_', params:'anydict') -> 'stranydict':
        """ Handles the MCP tools/list request.
        Supports cursor-based pagination - the client may pass a `cursor` in params
        to continue listing from a previous position.
        """

        cursor = params.get('cursor')
        tools, next_cursor = self.tool_registry.get_tools_page(cursor)

        result:'stranydict' = {
            'tools': tools,
        }

        if next_cursor:
            result['nextCursor'] = next_cursor

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

    def _handle_tools_call_streaming(self, request_id:'any_', params:'anydict') -> sse_bytes_gen:
        """ Handles tools/call as an SSE stream, yielding bytes chunks.
        Each yielded value is a complete SSE data frame containing a JSON-RPC message.
        The final frame contains the tools/call result.
        """

        # Extract tool name from the params ..
        tool_name = params.get('name')

        if not tool_name:
            error_response = _make_error_response(request_id, _error_invalid_params, 'Missing required parameter: name')
            yield _sse_data_prefix + dumps(error_response).encode('utf8') + _sse_line_end
            return

        # .. check if the tool is allowed on this channel ..
        if not self.tool_registry.is_tool_allowed(tool_name):
            error_response = _make_error_response(request_id, _error_method_not_found, f'Tool not found: `{tool_name}`')
            yield _sse_data_prefix + dumps(error_response).encode('utf8') + _sse_line_end
            return

        # .. extract arguments ..
        arguments = params.get('arguments', {})

        # .. invoke the service ..
        try:
            service_response = self.invoke_func(tool_name, arguments)
        except Exception as error:
            logger.warning('MCP: Service `%s` raised an exception during streaming', tool_name, exc_info=True)
            result:'stranydict' = {
                'content': [{'type': 'text', 'text': str(error)}],
                'isError': True,
            }
            final_response = _make_success_response(request_id, result)
            yield _sse_data_prefix + dumps(final_response).encode('utf8') + _sse_line_end
            return

        # .. wrap the successful response in MCP content format and yield the final SSE frame.
        response_text = self._serialize_service_response(service_response)
        result:'stranydict' = { # pyright: ignore[reportRedefinedVariable]
            'content': [{'type': 'text', 'text': response_text}],
        }
        final_response = _make_success_response(request_id, result)

        yield _sse_data_prefix + dumps(final_response).encode('utf8') + _sse_line_end

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

    def notify_tools_changed(self) -> 'int':
        """ Rebuilds the tool registry and queues a notifications/tools/list_changed
        notification to all active sessions.
        Returns the number of sessions notified.
        """

        # Rebuild the registry so new or removed services are reflected ..
        self.tool_registry.rebuild()

        # .. build the notification message ..
        notification:'stranydict' = {
            'jsonrpc': _jsonrpc_version,
            'method': 'notifications/tools/list_changed',
        }

        # .. and queue it for every active session.
        out = self.session_manager.queue_notification_for_all(notification)
        return out

# ################################################################################################################################

    def get_pending_notifications(self, session_id:'strnone') -> 'MCPResponse':
        """ Returns pending notifications for a session as a JSON-RPC batch.
        Used by GET requests for server-to-client notifications.
        """

        # Our response to produce
        out = MCPResponse()
        out.session_id = None

        # A session ID is required for notification polling ..
        if not session_id:
            out.body = None
            out.status_code = _http_not_found
            return out

        # .. the session must exist and be valid ..
        if not self.session_manager.validate(session_id):
            out.body = None
            out.status_code = _http_not_found
            return out

        # .. drain all pending notifications for this session ..
        notifications = self.session_manager.drain_notifications(session_id)

        # .. if there are none, return 204 No Content ..
        if not notifications:
            out.body = None
            out.status_code = NO_CONTENT
            return out

        # .. otherwise return them as a JSON-RPC batch.
        out.body = notifications
        out.status_code = OK
        return out

# ################################################################################################################################

    def handle_delete_session(self, session_id:'strnone') -> 'MCPResponse':
        """ Handles an HTTP DELETE request to terminate an MCP session.
        """

        # Our response to produce
        out = MCPResponse()
        out.session_id = None

        # A session ID is required for deletion ..
        if not session_id:
            out.body = None
            out.status_code = _http_not_found
            return out

        # .. try to delete it ..
        was_deleted = self.session_manager.delete(session_id)

        # .. if it existed, confirm with 200 ..
        if was_deleted:
            out.body = None
            out.status_code = OK
            return out

        # .. otherwise the session was not found.
        out.body = None
        out.status_code = _http_not_found
        return out

# ################################################################################################################################
# ################################################################################################################################
