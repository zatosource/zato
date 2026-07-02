# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import dataclasses
from http.client import BAD_REQUEST, NO_CONTENT, NOT_FOUND, OK
from logging import getLogger
from traceback import format_exc
from typing import NamedTuple

# Zato
from zato.common.json_internal import dumps, loads
from zato.server.connection.mcp.session import Session_Invalid_Identity, Session_Valid

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strdictlist, stranydict, strnone
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

# The initialize method is the only one that may run without an existing session
_method_initialize = 'initialize'

# Generic error message returned to clients for all session-related rejections
_message_bad_request = 'Bad request'

# Error message returned when parse fails
_message_parse_error = 'Parse error'

# Error message returned when the top-level request is structurally invalid
_message_invalid_request = 'Invalid request'

# Error message returned when the batch array is empty
_message_empty_batch = 'Invalid request: empty batch'

# Error message returned when initialize appears inside a batch
_message_initialize_in_batch = 'Invalid request: initialize MUST NOT appear in a batch'

# Error message returned when the jsonrpc version field is missing or wrong
_message_missing_jsonrpc_version = 'Invalid request: missing or wrong jsonrpc version'

# Error message returned when the method field is missing
_message_missing_method = 'Invalid request: missing method'

# Error message returned when the required tool name parameter is absent
_message_missing_tool_name = 'Missing required parameter: name'

# Error message returned when the cursor parameter is not a valid integer
_message_invalid_cursor = 'Invalid cursor value'

# Error message returned when protocolVersion is absent from initialize params
_message_missing_protocol_version = 'Missing required parameter: protocolVersion'

# Server metadata returned in the initialize response
_server_name    = 'Apache'
_server_version = '2.4'

# HTTP status code for a genuinely absent session resource on DELETE/GET
_http_not_found = NOT_FOUND

# HTTP status code for a protocol-level rejection (missing, unknown, or expired session on a request that requires one)
_http_bad_request = BAD_REQUEST

# Default sec_def_id when none is provided (e.g. in tests)
_no_sec_def_id = 0

# Maximum number of messages allowed in a single JSON-RPC batch request
_max_batch_size = 20

# Error message returned when a batch exceeds the maximum allowed size
_message_batch_too_large = 'Invalid request: batch too large'

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

class DispatchResult(NamedTuple):
    """ Carries a single JSON-RPC response body plus the ID of a session
    created during dispatch (only initialize creates one, all other methods yield None).
    """
    body:       'stranydict'
    session_id: 'strnone'

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

# ################################################################################################################################

    def _validate_session(
        self,
        session_id:'strnone',
        protocol_version_header:'strnone',
        sec_def_id:'int',
        ) -> 'MCPResponse | None':
        """ Validates session existence, identity, and protocol version match.
        Returns an MCPResponse with a 400 error if the session is invalid, or None if everything is fine.
        Called by handle_raw_request where an invalid session means it was terminated, never existed,
        or belongs to a different identity.
        """

        # If a session id was supplied, it must be valid ..
        if session_id:

            validation_result = self.session_manager.validate(session_id, sec_def_id)

            if validation_result != Session_Valid:
                logger.info('MCP: Invalid or expired session `%s`', session_id)
                out = MCPResponse()
                out.body = _make_error_response(None, _error_invalid_request, _message_bad_request)
                out.status_code = _http_bad_request
                return out

            # .. when the session is valid, check the protocol version header ..
            return self._validate_protocol_version(session_id, protocol_version_header)

        # .. validation passed.
        return None

# ################################################################################################################################

    def _validate_protocol_version(self, session_id:'str', protocol_version_header:'strnone') -> 'MCPResponse | None':
        """ Checks that the MCP-Protocol-Version header matches the negotiated version.
        Returns an MCPResponse with a 400 error on mismatch, or None if fine.
        """

        if protocol_version_header is None:
            return None

        negotiated_version = self.session_manager.get_protocol_version(session_id)

        if protocol_version_header != negotiated_version:
            message = f'Protocol version mismatch: header `{protocol_version_header}` does not match session `{negotiated_version}`'
            out = MCPResponse()
            out.body = _make_error_response(None, _error_invalid_request, message)
            out.status_code = _http_bad_request
            return out

        return None

# ################################################################################################################################

    def handle_raw_request(
        self,
        raw_data:'bytes',
        session_id:'strnone' = None,
        remote_address:'str' = '',
        protocol_version_header:'strnone' = None,
        sec_def_id:'int' = _no_sec_def_id,
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
            logger.info('MCP: Could not parse the JSON body:\n%s', format_exc())

            out.body = _make_error_response(None, _error_parse, _message_parse_error)
            out.status_code = OK
            return out

        # .. validate session and protocol version up front ..
        validation_error = self._validate_session(session_id, protocol_version_header, sec_def_id)

        if validation_error:
            return validation_error

        # .. if validation passed and a session_id was provided, the session is valid
        # (otherwise _validate_session would have returned an error) ..
        session_is_valid = bool(session_id)

        # .. handle batch (array) vs single (object) ..
        if isinstance(parsed, list):

            out = self._handle_batch(parsed, session_is_valid, sec_def_id, remote_address)
            return out

        if isinstance(parsed, dict):

            # .. a single gated method without a valid session is a protocol error and must
            # carry HTTP 400, unlike a batch where each element reports its own JSON-RPC error ..
            method = parsed.get('method')

            if method != _method_initialize:
                if not session_is_valid:

                    logger.info('MCP: Session required but not provided')
                    request_id = parsed.get('id')
                    out.body = _make_error_response(request_id, _error_invalid_request, _message_bad_request)
                    out.status_code = _http_bad_request
                    out.session_id = None
                    return out

            # .. dispatch the request, receiving both the body and the ID of any session
            # that initialize may have created, keeping all state local to this call ..
            dispatch_result = self._dispatch_single(parsed, session_is_valid, sec_def_id, remote_address)

            out.body = dispatch_result.body
            out.status_code = OK
            out.session_id = dispatch_result.session_id
            return out

        # .. anything else is an invalid request.
        out.body = _make_error_response(None, _error_invalid_request, _message_invalid_request)
        out.status_code = OK
        return out

# ################################################################################################################################

    def _handle_batch(
        self,
        messages:'anylist',
        session_is_valid:'bool',
        sec_def_id:'int',
        remote_address:'str',
        ) -> 'MCPResponse':
        """ Handles a JSON-RPC batch request (array of messages).
        Initialize is forbidden inside a batch, so no batch element can ever create a session.
        """

        # Our response to produce
        out = MCPResponse()

        # Empty array is an invalid request per the JSON-RPC spec ..
        if not messages:

            out.body = _make_error_response(None, _error_invalid_request, _message_empty_batch)
            out.status_code = OK
            return out

        # .. reject batches that exceed the configured maximum size ..
        batch_size = len(messages)

        if batch_size > _max_batch_size:
            logger.info('MCP: Batch rejected, size %d exceeds cap %d', batch_size, _max_batch_size)
            out.body = _make_error_response(None, _error_invalid_request, _message_batch_too_large)
            out.status_code = OK
            return out

        # .. the MCP spec forbids initialize inside a batch, reject the entire
        # batch if any element attempts it ..
        for message in messages:
            if isinstance(message, dict):
                method = message.get('method')
                if method == _method_initialize:
                    request_id = message.get('id')
                    out.body = _make_error_response(request_id, _error_invalid_request, _message_initialize_in_batch)
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
            # Initialize was already rejected above, so dispatch_result.session_id is always None here.
            dispatch_result = self._dispatch_single(message, session_is_valid, sec_def_id, remote_address)
            responses.append(dispatch_result.body)

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

    def _dispatch_single(
        self,
        message:'anydict',
        session_is_valid:'bool',
        sec_def_id:'int',
        remote_address:'str',
        ) -> 'DispatchResult':
        """ Routes a single JSON-RPC request to the appropriate handler method.
        Every method other than initialize requires a valid session.
        Returns the response body plus the ID of any session that initialize created.
        """

        # Validate basic JSON-RPC structure ..
        jsonrpc = message.get('jsonrpc')
        request_id = message.get('id')

        if jsonrpc != _jsonrpc_version:

            body = _make_error_response(request_id, _error_invalid_request, _message_missing_jsonrpc_version)
            out = DispatchResult(body, None)
            return out

        method = message.get('method')

        if not method:

            body = _make_error_response(request_id, _error_invalid_request, _message_missing_method)
            out = DispatchResult(body, None)
            return out

        # .. only initialize may run without an established session, every other method is gated ..
        if method != _method_initialize:
            if not session_is_valid:

                body = _make_error_response(request_id, _error_invalid_request, _message_bad_request)
                out = DispatchResult(body, None)
                return out

        # Params is optional per JSON-RPC 2.0 spec - a client may omit it entirely
        params = message.get('params', {})

        # .. route to the handler for this method.
        if method == _method_initialize:

            out = self._handle_initialize(request_id, params, sec_def_id, remote_address)
            return out

        if method == 'tools/list':

            body = self._handle_tools_list(request_id, params)
            out = DispatchResult(body, None)
            return out

        if method == 'tools/call':

            body = self._handle_tools_call(request_id, params)
            out = DispatchResult(body, None)
            return out

        if method == 'ping':

            body = self._handle_ping(request_id)
            out = DispatchResult(body, None)
            return out

        # .. anything else is an unknown method.
        error_message = f'Method not found: `{method}`'
        body = _make_error_response(request_id, _error_method_not_found, error_message)

        out = DispatchResult(body, None)
        return out

# ################################################################################################################################

    def _handle_initialize(
        self,
        request_id:'any_',
        params:'anydict',
        sec_def_id:'int',
        remote_address:'str',
        ) -> 'DispatchResult':
        """ Handles the MCP initialize request.
        Returns server capabilities and negotiated protocol version,
        together with the ID of the newly created session so the caller
        can set it as a response header.
        """

        # The client must state the protocol version it wants ..
        if params.get('protocolVersion') is None:

            body = _make_error_response(request_id, _error_invalid_request, _message_missing_protocol_version)
            out = DispatchResult(body, None)
            return out

        # .. create a new session for this client, recording the version it is bound to,
        # rejecting if the per-identity cap has been reached ..
        try:
            new_session_id = self.session_manager.create(_mcp_protocol_version, sec_def_id, remote_address)
        except ValueError as e:
            logger.info('MCP: %s', e)
            body = _make_error_response(request_id, _error_invalid_request, _message_bad_request)
            out = DispatchResult(body, None)
            return out

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

        body = _make_success_response(request_id, result)

        out = DispatchResult(body, new_session_id)
        return out

# ################################################################################################################################

    def _handle_tools_list(self, request_id:'any_', params:'anydict') -> 'stranydict':
        """ Handles the MCP tools/list request.
        Supports cursor-based pagination - the client may pass a `cursor` in params
        to continue listing from a previous position.
        """

        cursor = params.get('cursor')

        try:
            tools, next_cursor = self.tool_registry.get_tools_page(cursor)
        except ValueError:
            out = _make_error_response(request_id, _error_invalid_params, _message_invalid_cursor)
            return out

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
        except Exception:
            exception_detail = format_exc()
            logger.warning('MCP: Service `%s` raised an exception:\n%s', tool_name, exception_detail)

            error_result:'stranydict' = {
                'content': [
                    {
                        'type': 'text',
                        'text': _message_bad_request,
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

    def handle_delete_session(
        self,
        session_id:'strnone',
        protocol_version_header:'strnone' = None,
        sec_def_id:'int' = _no_sec_def_id,
        ) -> 'MCPResponse':
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

        # .. check if the session exists and belongs to the caller.
        # For DELETE, an unknown or expired session is 404 (resource not found).
        # An identity mismatch returns 400 to reject without leaking session existence ..
        validation_result = self.session_manager.validate(session_id, sec_def_id)

        if validation_result == Session_Invalid_Identity:
            out.body = None
            out.status_code = _http_bad_request
            return out

        if validation_result != Session_Valid:
            out.body = None
            out.status_code = _http_not_found
            return out

        # .. the session exists, so check protocol version consistency ..
        version_error = self._validate_protocol_version(session_id, protocol_version_header)

        if version_error:
            return version_error

        # .. delete it.
        _ = self.session_manager.delete(session_id)
        out.body = None
        out.status_code = OK
        return out

# ################################################################################################################################
# ################################################################################################################################
