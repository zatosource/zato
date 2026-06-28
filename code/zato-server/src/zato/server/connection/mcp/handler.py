# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import dataclasses
from http.client import BAD_REQUEST, NO_CONTENT, NOT_FOUND, OK
from logging import getLogger

# Zato
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strdictlist, stranydict, strnone
    from zato.server.connection.mcp.registry import ToolRegistry
    from zato.server.connection.mcp.session import MCPSessionManager
    from zato.server.service.store import ServiceStore

    MCPSessionManager = MCPSessionManager
    ServiceStore = ServiceStore
    strdictlist = strdictlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

# JSON-RPC 2.0 error codes
_error_parse            = -32700
_error_invalid_request  = -32600
_error_method_not_found = -32601
_error_invalid_params   = -32602

# JSON-RPC 2.0 version string
_jsonrpc_version = '2.0'

# MCP protocol version negotiated during initialize
_mcp_protocol_version = '2025-11-05'

# Protocol versions this server is willing to negotiate during initialize
_supported_protocol_versions = frozenset({_mcp_protocol_version})

# The initialize method is the only one that may run without an existing session
_method_initialize = 'initialize'

# Error message returned when a gated method is called without a valid session
_session_required_message = 'Session required: call initialize first'

# Error message returned when a supplied session id is invalid or expired
_message_invalid_session = 'Invalid or expired session'

# Error message returned when parse fails
_message_parse_error = 'Parse error'

# Error message returned when the top-level request is structurally invalid
_message_invalid_request = 'Invalid request'

# Error message returned when the batch array is empty
_message_empty_batch = 'Invalid request: empty batch'

# Error message returned when the jsonrpc version field is missing or wrong
_message_missing_jsonrpc_version = 'Invalid request: missing or wrong jsonrpc version'

# Error message returned when the method field is missing
_message_missing_method = 'Invalid request: missing method'

# Error message returned when the required tool name parameter is absent
_message_missing_tool_name = 'Missing required parameter: name'

# Server metadata returned in the initialize response
_server_name    = 'Apache'
_server_version = '2.4'

# HTTP status code for a genuinely absent session resource on DELETE/GET
_http_not_found = NOT_FOUND

# HTTP status code for a protocol-level rejection (missing, unknown, or expired session on a request that requires one)
_http_bad_request = BAD_REQUEST

# ################################################################################################################################
# ################################################################################################################################

@dataclasses.dataclass(init=False)
class MCPResponse:
    """ Wraps a JSON-RPC response body, HTTP status code, and optional session ID.
    """
    body:         'any_'
    status_code:  'int'
    session_id:   'strnone'  = None

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

    def handle_raw_request(
        self,
        raw_data:'bytes',
        session_id:'strnone' = None,
        remote_address:'str' = '',
        protocol_version_header:'strnone' = None,
        ) -> 'MCPResponse':
        """ Parses raw bytes into JSON and dispatches.
        Every method other than initialize requires a valid session.
        """

        # Our response to produce
        out = MCPResponse()

        # Try to parse the incoming data as JSON ..
        try:
            parsed = loads(raw_data)
        except Exception:
            logger.debug('MCP: Failed to parse JSON body', exc_info=True)

            out.body = _make_error_response(None, _error_parse, _message_parse_error)
            out.status_code = OK
            return out

        # .. resolve whether the caller holds a valid session up front, since the session
        # gate below and the per-method dispatch both depend on it ..
        session_is_valid = False

        if session_id:
            session_is_valid = self.session_manager.validate(session_id)

        # .. a session id that was supplied but does not validate is a protocol error,
        # so reject it before doing any work (400, never 404, since auth is the HTTP layer's job) ..
        if session_id:
            if not session_is_valid:

                out.body = _make_error_response(None, _error_invalid_request, _message_invalid_session)
                out.status_code = _http_bad_request
                return out

        # .. when the caller holds a valid session and sent an MCP-Protocol-Version header,
        # it must match the version negotiated for that session, otherwise reject ..
        if session_is_valid:
            if protocol_version_header is not None:

                negotiated_version = self.session_manager.get_protocol_version(session_id)

                if protocol_version_header != negotiated_version:

                    message = f'Protocol version mismatch: header `{protocol_version_header}` does not match session `{negotiated_version}`'
                    out.body = _make_error_response(None, _error_invalid_request, message)
                    out.status_code = _http_bad_request
                    return out

        # .. clear any pending session ID from a previous request
        # and store the remote address for session creation logging ..
        self._pending_session_id = None
        self._remote_address = remote_address

        # .. handle batch (array) vs single (object) ..
        if isinstance(parsed, list):

            out = self._handle_batch(parsed, session_is_valid)
            out.session_id = self._pending_session_id
            return out

        if isinstance(parsed, dict):

            # .. a single gated method without a valid session is a protocol error and must
            # carry HTTP 400, unlike a batch where each element reports its own JSON-RPC error ..
            method = parsed.get('method')

            if method != _method_initialize:
                if not session_is_valid:

                    request_id = parsed.get('id')
                    out.body = _make_error_response(request_id, _error_invalid_request, _session_required_message)
                    out.status_code = _http_bad_request
                    out.session_id = None
                    return out

            out.body = self._dispatch_single(parsed, session_is_valid)
            out.status_code = OK
            out.session_id = self._pending_session_id
            return out

        # .. anything else is an invalid request.
        out.body = _make_error_response(None, _error_invalid_request, _message_invalid_request)
        out.status_code = OK
        return out

# ################################################################################################################################

    def _handle_batch(self, messages:'list', session_is_valid:'bool') -> 'MCPResponse':
        """ Handles a JSON-RPC batch request (array of messages).
        """

        # Our response to produce
        out = MCPResponse()

        # Empty array is an invalid request per the JSON-RPC spec ..
        if not messages:

            out.body = _make_error_response(None, _error_invalid_request, _message_empty_batch)
            out.status_code = OK
            return out

        # .. dispatch each message independently and collect responses for requests (not notifications).
        responses:'strdictlist' = []

        for message in messages:

            # Notifications have no 'id' field and produce no response ..
            if 'id' not in message:
                self._handle_notification(message)
                continue

            # .. requests produce a response, gated on the same session validity as the outer request.
            response = self._dispatch_single(message, session_is_valid)
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
            return

        # notifications/initialized is a no-op acknowledgment
        if method == 'notifications/initialized':
            logger.info('MCP: Received initialized notification')

        # .. log unknown notifications but do not error.
        else:
            logger.info('MCP: Received notification `%s`', method)

# ################################################################################################################################

    def _dispatch_single(self, message:'anydict', session_is_valid:'bool') -> 'stranydict':
        """ Routes a single JSON-RPC request to the appropriate handler method.
        Every method other than initialize requires a valid session.
        """

        # Validate basic JSON-RPC structure ..
        jsonrpc = message.get('jsonrpc')
        request_id = message.get('id')

        if jsonrpc != _jsonrpc_version:

            out = _make_error_response(request_id, _error_invalid_request, _message_missing_jsonrpc_version)
            return out

        method = message.get('method')

        if not method:

            out = _make_error_response(request_id, _error_invalid_request, _message_missing_method)
            return out

        # .. only initialize may run without an established session, every other method is gated ..
        if method != _method_initialize:
            if not session_is_valid:

                out = _make_error_response(request_id, _error_invalid_request, _session_required_message)
                return out

        # Params is optional per JSON-RPC 2.0 spec - a client may omit it entirely
        params = message.get('params', {})

        # .. route to the handler for this method.
        if method == _method_initialize:

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
        message = f'Method not found: `{method}`'
        out = _make_error_response(request_id, _error_method_not_found, message)
        return out

# ################################################################################################################################

    def _handle_initialize(self, request_id:'any_', params:'anydict') -> 'stranydict':
        """ Handles the MCP initialize request.
        Returns server capabilities and negotiated protocol version.
        Creates a new session and stores its ID on _pending_session_id
        for handle_raw_request to pick up and set as a response header.
        """

        # The client states the protocol version it wants, reject anything we do not support ..
        requested_version = params.get('protocolVersion')

        if requested_version is not None:
            if requested_version not in _supported_protocol_versions:

                message = f'Unsupported protocol version: `{requested_version}`'
                out = _make_error_response(request_id, _error_invalid_request, message)
                return out

        # .. create a new session for this client, recording the version it is bound to ..
        self._pending_session_id = self.session_manager.create(_mcp_protocol_version, self._remote_address)

        result:'stranydict' = {
            'protocolVersion': _mcp_protocol_version,
            'capabilities': {
                'tools': {},
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
        Validates the tool name against the allow list, invokes the service,
        and wraps the response in MCP content format.
        """

        # Extract tool name from the params ..
        tool_name = params.get('name')

        if not tool_name:

            out = _make_error_response(request_id, _error_invalid_params, _message_missing_tool_name)
            return out

        # .. check if the tool is allowed on this channel ..
        if not self.tool_registry.is_tool_allowed(tool_name):

            message = f'Tool not found: `{tool_name}`'
            out = _make_error_response(request_id, _error_method_not_found, message)
            return out

        # .. extract arguments - optional per the MCP spec, defaults to empty dict ..
        arguments = params.get('arguments', {})

        # .. invoke the service ..
        try:
            service_response = self.invoke_func(tool_name, arguments)
        except Exception as e:
            logger.debug('MCP: Service `%s` raised an exception', tool_name, exc_info=True)

            error_result:'stranydict' = {
                'content': [
                    {
                        'type': 'text',
                        'text': str(e),
                    },
                ],
                'isError': True,
            }

            out = _make_success_response(request_id, error_result)
            return out

        # .. wrap the successful response in MCP content format.
        response_text = self._serialize_service_response(service_response)

        success_result:'stranydict' = {
            'content': [
                {
                    'type': 'text',
                    'text': response_text,
                },
            ],
        }

        out = _make_success_response(request_id, success_result)
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

    def _make_session_rejected_response(self) -> 'stranydict':
        """ Builds the JSON-RPC error body for an invalid or expired session.
        Used by the endpoint layer for pre-dispatch validation on DELETE.
        """

        out = _make_error_response(None, _error_invalid_request, _message_invalid_session)
        return out

# ################################################################################################################################

    def _make_version_mismatch_response(self, header_version:'str', negotiated_version:'strnone') -> 'stranydict':
        """ Builds the JSON-RPC error body for a protocol version mismatch.
        Used by the endpoint layer for pre-dispatch validation on DELETE.
        """

        message = f'Protocol version mismatch: header `{header_version}` does not match session `{negotiated_version}`'
        out = _make_error_response(None, _error_invalid_request, message)
        return out

# ################################################################################################################################
# ################################################################################################################################
