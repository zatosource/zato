# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import BAD_REQUEST, NOT_FOUND, OK
from logging import getLogger
from traceback import format_exc
from typing import NamedTuple

# Zato
from zato.common.api import MCP
from zato.common.json_internal import dumps, loads
from zato.common.util.message_filters.api import apply_filter
from zato.common.util.safeguards.api import apply_safeguards
from zato.common.util.safeguards.config import is_safeguards_active
from zato.common.util.truncate.tokens import apply_token_cap
from zato.server.connection.mcp import stateless
from zato.server.connection.mcp.common import _error_invalid_params, _error_invalid_request, _error_method_not_found, \
    _error_parse, _jsonrpc_version, _message_bad_request, _message_invalid_cursor, _message_invalid_params, \
    _message_invalid_request, _message_missing_jsonrpc_version, _message_missing_method, _message_missing_tool_name, \
    _message_parse_error, _message_prompt_not_found, _method_prompts_get, _method_prompts_list, _method_tools_call, \
    _server_name, _server_version, make_error_response, make_success_response, MCPResponse
from zato.server.connection.mcp.prompts import InvalidCursor
from zato.server.connection.mcp.session import Session_Invalid_Identity, Session_Valid
from zato.server.connection.mcp.validate import validate_arguments

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anydictnone, stranydict, strdictlist, strnone
    from zato.common.util.safeguards.common import SafeguardConfig
    from zato.common.util.truncate.tokens import TokenCapConfig
    from zato.server.connection.mcp.prompts import SkillPrompts
    from zato.server.connection.mcp.registry import ToolRegistry
    from zato.server.connection.mcp.session import MCPSessionManager
    from zato.server.service.store import ServiceStore

    MCPSessionManager = MCPSessionManager
    ServiceStore = ServiceStore
    SkillPrompts = SkillPrompts

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

# MCP protocol version negotiated during initialize
_mcp_protocol_version = MCP.Protocol_Version_Sessions

# The initialize method is the only one that may run without an existing session
_method_initialize = 'initialize'

# Error message returned when protocolVersion is absent from initialize params
_message_missing_protocol_version = 'Missing required parameter: protocolVersion'

# HTTP status code for a genuinely absent session resource on DELETE/GET
_http_not_found = NOT_FOUND

# HTTP status code for a protocol-level rejection (missing, unknown, or expired session on a request that requires one)
_http_bad_request = BAD_REQUEST

# The optional argument through which a client passes a JSONata expression to shape a tool's response,
# available only on gateways whose configuration allows client filters.
_response_filter_key = 'response_filter'

# What the advertised response_filter property says about itself
_response_filter_schema:'stranydict' = {
    'type': 'string',
    'description': 'Optional JSONata expression applied to the response before it is returned',
}

# What the trace records as the rejection kind when the size cap blocks a response
_reject_kind_size = 'size'

# What a request body over the published size bound is refused with
_message_request_too_large = 'Request body exceeds the maximum size'

# ################################################################################################################################
# ################################################################################################################################

class ResponseRejected(Exception):
    """ Raised when a response safeguard or size cap refuses a tool response - the message is returned to the client.
    """

# ################################################################################################################################
# ################################################################################################################################

class FilterInvalid(Exception):
    """ Raised when a client-supplied response filter does not compile or does not evaluate -
    the message becomes a JSON-RPC invalid-params error.
    """

# ################################################################################################################################
# ################################################################################################################################

class DispatchResult(NamedTuple):
    """ Carries a single JSON-RPC response body plus the ID of a session
    created during dispatch (only initialize creates one, all other methods yield None)
    and the trace of what shaping did to a tools/call response (None for all other methods).
    """
    body:       'stranydict'
    session_id: 'strnone'
    trace:      'anydictnone' = None

# ################################################################################################################################
# ################################################################################################################################

class MCPHandler:
    """ Handles MCP JSON-RPC 2.0 dispatch for a single MCP gateway.
    Routes initialize, tools/list, tools/call, prompts/list, prompts/get, and ping methods.
    """

    def __init__(
        self,
        tool_registry:'ToolRegistry',
        invoke_func:'any_',
        session_manager:'MCPSessionManager',
        safeguard_config:'SafeguardConfig',
        token_cap_config:'TokenCapConfig',
        validate_input:'bool',
        skill_prompts:'SkillPrompts',
        allow_client_filters:'bool' = False,
        ) -> 'None':
        self.tool_registry = tool_registry
        self.invoke_func = invoke_func
        self.session_manager = session_manager
        self.safeguard_config = safeguard_config
        self.token_cap_config = token_cap_config
        self.validate_input = validate_input
        self.skill_prompts = skill_prompts
        self.allow_client_filters = allow_client_filters

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
                out.body = make_error_response(None, _error_invalid_request, _message_bad_request)
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
            out.body = make_error_response(None, _error_invalid_request, message)
            out.status_code = _http_bad_request
            return out

        return None

# ################################################################################################################################

    def handle_raw_request(
        self,
        raw_data:'bytes',
        sec_def_id:'int',
        session_id:'strnone' = None,
        remote_address:'str' = '',
        protocol_version_header:'strnone' = None,
        mcp_method_header:'strnone' = None,
        mcp_name_header:'strnone' = None,
        ) -> 'MCPResponse':
        """ Parses raw bytes into JSON and dispatches.
        Requests of the stateless protocol revision are self-contained, while in the
        session-based revision every method other than initialize requires a valid session.
        """

        # Our response to produce
        out = MCPResponse()

        # A request past the published size bound is refused before it is parsed at all ..
        request_size = len(raw_data)

        if request_size > MCP.Max_Request_Size:

            out.body = make_error_response(None, _error_invalid_request, _message_request_too_large)
            out.status_code = OK
            return out

        # .. try to parse the incoming data as JSON ..
        try:
            parsed = loads(raw_data)
        except Exception:
            logger.info('MCP: Could not parse the JSON body:\n%s', format_exc())

            out.body = make_error_response(None, _error_parse, _message_parse_error)
            out.status_code = OK
            return out

        # .. an array body is an invalid request - batching is not part of any supported revision ..
        if isinstance(parsed, list):

            out.body = make_error_response(None, _error_invalid_request, _message_invalid_request)
            out.status_code = OK
            return out

        if isinstance(parsed, dict):

            method = parsed.get('method')

            # .. record what is being dispatched for the audit log - the method for every
            # request and, for tool calls and prompt reads, the name being asked for ..
            if isinstance(method, str):
                out.method = method

                if method in (_method_tools_call, _method_prompts_get):
                    params = parsed.get('params')

                    if isinstance(params, dict):
                        tool_name = params.get('name')

                        if isinstance(tool_name, str):
                            out.tool_name = tool_name

            # .. resolve the protocol version this request asks for, out of the header or _meta ..
            requested_version = stateless.resolve_protocol_version(protocol_version_header, parsed)

            # .. requests of the stateless revision are self-contained ..
            is_stateless = requested_version == stateless._protocol_version

            # .. and so are server/discover probes, whatever version they carry ..
            if method == stateless._method_discover:
                is_stateless = True

            # .. both dispatch with no session at all ..
            if is_stateless:
                out = stateless.dispatch(self, parsed, mcp_method_header, mcp_name_header)
                return out

            # .. a version this gateway does not speak is rejected outright, unless a session exists,
            # in which case the session's own version consistency check below reports the mismatch ..
            if requested_version:
                if requested_version != _mcp_protocol_version:
                    if not session_id:

                        request_id = parsed.get('id')
                        error_message = f'Unsupported protocol version: `{requested_version}`'
                        code = stateless._error_unsupported_protocol_version

                        out.body = make_error_response(request_id, code, error_message)
                        out.status_code = OK
                        return out

            # .. validate session and protocol version ..
            validation_error = self._validate_session(session_id, protocol_version_header, sec_def_id)

            if validation_error:
                return validation_error

            # .. if validation passed and a session_id was provided, the session is valid
            # (otherwise _validate_session would have returned an error) ..
            session_is_valid = bool(session_id)

            # .. a gated method without a valid session is a protocol error and must carry HTTP 400 ..
            if method != _method_initialize:
                if not session_is_valid:

                    logger.info('MCP: Session required but not provided')
                    request_id = parsed.get('id')
                    out.body = make_error_response(request_id, _error_invalid_request, _message_bad_request)
                    out.status_code = _http_bad_request
                    out.session_id = None
                    return out

            # .. dispatch the request, receiving both the body and the ID of any session
            # that initialize may have created, keeping all state local to this call ..
            dispatch_result = self._dispatch_single(parsed, session_is_valid, sec_def_id, remote_address)

            out.body = dispatch_result.body
            out.status_code = OK
            out.session_id = dispatch_result.session_id
            out.trace = dispatch_result.trace
            return out

        # .. anything else is an invalid request.
        out.body = make_error_response(None, _error_invalid_request, _message_invalid_request)
        out.status_code = OK
        return out

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

            body = make_error_response(request_id, _error_invalid_request, _message_missing_jsonrpc_version)
            out = DispatchResult(body, None)
            return out

        method = message.get('method')

        if not method:

            body = make_error_response(request_id, _error_invalid_request, _message_missing_method)
            out = DispatchResult(body, None)
            return out

        # .. only initialize may run without an established session, every other method is gated ..
        if method != _method_initialize:
            if not session_is_valid:

                body = make_error_response(request_id, _error_invalid_request, _message_bad_request)
                out = DispatchResult(body, None)
                return out

        # Params is optional per JSON-RPC 2.0 spec - a client may omit it entirely
        params = message.get('params', {})

        # .. but when present, it must be an object, otherwise the handlers cannot read it ..
        if not isinstance(params, dict):

            body = make_error_response(request_id, _error_invalid_params, _message_invalid_params)
            out = DispatchResult(body, None)
            return out

        # .. route to the handler for this method.
        if method == _method_initialize:

            out = self._handle_initialize(request_id, params, sec_def_id, remote_address)
            return out

        if method == 'tools/list':

            body = self._handle_tools_list(request_id, params)
            out = DispatchResult(body, None)
            return out

        if method == _method_tools_call:

            body, trace = self._handle_tools_call(request_id, params)
            out = DispatchResult(body, None, trace)
            return out

        if method == _method_prompts_list:

            body = self._handle_prompts_list(request_id, params)
            out = DispatchResult(body, None)
            return out

        if method == _method_prompts_get:

            body = self._handle_prompts_get(request_id, params)
            out = DispatchResult(body, None)
            return out

        if method == 'ping':

            body = self._handle_ping(request_id)
            out = DispatchResult(body, None)
            return out

        # .. anything else is an unknown method.
        error_message = f'Method not found: `{method}`'
        body = make_error_response(request_id, _error_method_not_found, error_message)

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

            body = make_error_response(request_id, _error_invalid_request, _message_missing_protocol_version)
            out = DispatchResult(body, None)
            return out

        # .. create a new session for this client, recording the version it is bound to,
        # rejecting if the per-identity cap has been reached ..
        try:
            new_session_id = self.session_manager.create(_mcp_protocol_version, sec_def_id, remote_address)
        except ValueError as e:
            logger.info('MCP: %s', e)
            body = make_error_response(request_id, _error_invalid_request, _message_bad_request)
            out = DispatchResult(body, None)
            return out

        capabilities:'stranydict' = {
            'tools': {},
        }

        # The prompts capability is only advertised when there is a prompt to serve at all
        if self.skill_prompts.has_prompts():
            capabilities['prompts'] = {}

        result:'stranydict' = {
            'protocolVersion': _mcp_protocol_version,
            'capabilities': capabilities,
            'serverInfo': {
                'name': _server_name,
                'version': _server_version,
            },
        }

        body = make_success_response(request_id, result)

        out = DispatchResult(body, new_session_id)
        return out

# ################################################################################################################################

    def _add_response_filter_property(self, tools:'strdictlist') -> 'strdictlist':
        """ Returns a copy of a tools page whose every input schema additionally advertises
        the optional response_filter property - the cached originals are never touched,
        so validation keeps seeing the schemas without it.
        """

        out:'strdictlist' = []

        for tool in tools:

            tool = dict(tool)
            input_schema = dict(tool['inputSchema'])

            # A schema with no properties of its own still advertises the filter
            properties = input_schema.get('properties')

            if properties is None:
                properties = {}

            properties = dict(properties)
            properties[_response_filter_key] = _response_filter_schema

            input_schema['properties'] = properties
            tool['inputSchema'] = input_schema

            out.append(tool)

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
            out = make_error_response(request_id, _error_invalid_params, _message_invalid_cursor)
            return out

        # When the gateway allows client filters, every tool advertises the optional
        # response_filter argument so callers can discover it from the schema alone.
        if self.allow_client_filters:
            tools = self._add_response_filter_property(tools)

        result:'stranydict' = {
            'tools': tools,
        }

        if next_cursor:
            result['nextCursor'] = next_cursor

        out = make_success_response(request_id, result)
        return out

# ################################################################################################################################

    def _handle_prompts_list(self, request_id:'any_', params:'anydict') -> 'stranydict':
        """ Handles the MCP prompts/list request.
        Answers with the names and descriptions of the skills this gateway serves,
        cursor-paginated the way tools/list is - the instructions do not travel here.
        """

        cursor = params.get('cursor')

        try:
            prompts, next_cursor = self.skill_prompts.get_prompts_page(cursor)
        except InvalidCursor:
            out = make_error_response(request_id, _error_invalid_params, _message_invalid_cursor)
            return out

        result:'stranydict' = {
            'prompts': prompts,
        }

        if next_cursor:
            result['nextCursor'] = next_cursor

        out = make_success_response(request_id, result)
        return out

# ################################################################################################################################

    def _handle_prompts_get(self, request_id:'any_', params:'anydict') -> 'stranydict':
        """ Handles the MCP prompts/get request.
        Answers with the named skill's instructions in the MCP prompt result shape.
        A name outside the gateway's allow list, or whose file is gone, is invalid params.
        """

        # Extract the prompt name from the params ..
        prompt_name = params.get('name')

        if not prompt_name:

            out = make_error_response(request_id, _error_invalid_params, _message_missing_tool_name)
            return out

        # .. the skill has to be on this gateway's allow list and its file has to be on disk ..
        document = self.skill_prompts.get_prompt(prompt_name)

        if document is None:

            logger.info('MCP: Prompt not found `%s`', prompt_name)
            out = make_error_response(request_id, _error_invalid_params, _message_prompt_not_found)
            return out

        # .. and its instructions go out as the one message of the prompt.
        result:'stranydict' = {
            'description': document.description,
            'messages': [
                {
                    'role': 'user',
                    'content': {
                        'type': 'text',
                        'text': document.instructions,
                    },
                },
            ],
        }

        out = make_success_response(request_id, result)
        return out

# ################################################################################################################################

    def _handle_tools_call(self, request_id:'any_', params:'anydict') -> 'tuple[stranydict, anydictnone]':
        """ Handles the MCP tools/call request.
        Validates the tool name against the allow list, invokes the service,
        and wraps the response in MCP content format. Returns the response body
        together with the trace of what shaping did to it - None when nothing did anything.
        """

        # Extract tool name from the params ..
        tool_name = params.get('name')

        if not tool_name:

            out = make_error_response(request_id, _error_invalid_params, _message_missing_tool_name)
            return out, None

        # .. check if the tool is allowed on this gateway ..
        if not self.tool_registry.is_tool_allowed(tool_name):

            message = f'Tool not found: `{tool_name}`'
            out = make_error_response(request_id, _error_method_not_found, message)
            return out, None

        # .. extract arguments - optional per the MCP spec, defaults to empty dict ..
        arguments = params.get('arguments', {})

        # .. on a gateway that allows client filters, the response_filter argument belongs
        # to the gateway, not to the service - it is taken out before validation ever sees it ..
        response_filter = None

        if self.allow_client_filters:
            if isinstance(arguments, dict):
                response_filter = arguments.pop(_response_filter_key, None)

        # .. when the gateway has input validation on, the arguments must match the tool's
        # input schema, the same one tools/list advertises - the error names the offending field ..
        if self.validate_input:
            schema = self.tool_registry.get_tool_schema(tool_name)

            if error_message := validate_arguments(arguments, schema):
                logger.info('MCP: Invalid arguments for `%s`: %s', tool_name, error_message)
                out = make_error_response(request_id, _error_invalid_params, error_message)
                return out, None

        # The trace of everything shaping does to this response, filled in along the way
        trace:'stranydict' = {}

        # .. invoke the service and serialize its response, treating a serialization
        # failure (e.g. bytes that do not decode or objects that do not dump to JSON)
        # the same way as a service exception ..
        try:
            service_response = self.invoke_func(tool_name, arguments)
            response_text = self._serialize_service_response(service_response, trace, response_filter)

        # .. a safeguard or size cap refused the response - the message names the reason,
        # unlike a service exception, which is never revealed to the client ..
        except ResponseRejected as e:
            logger.info('MCP: Response of `%s` was refused: %s', tool_name, e)

            refused_result:'stranydict' = {
                'content': [
                    {
                        'type': 'text',
                        'text': str(e),
                    },
                ],
                'isError': True,
            }

            out = make_success_response(request_id, refused_result)
            return out, self._trace_or_none(trace)

        # .. an invalid client filter is the caller's own mistake and is reported as invalid params ..
        except FilterInvalid as e:
            logger.info('MCP: Invalid response filter for `%s`: %s', tool_name, e)

            out = make_error_response(request_id, _error_invalid_params, str(e))
            return out, self._trace_or_none(trace)

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

            out = make_success_response(request_id, error_result)
            return out, None

        # .. wrap the successful response in MCP content format.

        success_result:'stranydict' = {
            'content': [
                {
                    'type': 'text',
                    'text': response_text,
                },
            ],
        }

        out = make_success_response(request_id, success_result)
        return out, self._trace_or_none(trace)

# ################################################################################################################################

    def _trace_or_none(self, trace:'stranydict') -> 'anydictnone':
        """ An empty trace travels as None so the audit log never records an empty document.
        """

        if trace:
            out = trace
        else:
            out = None

        return out

# ################################################################################################################################

    def _record_safeguard_trace(self, result:'any_', trace:'stranydict') -> 'None':
        """ Copies what the safeguards did into the trace - only the counters
        that actually counted something are recorded.
        """

        if result.pii_removed:
            trace['pii_removed'] = result.pii_removed

        if result.nulls_removed:
            trace['nulls_removed'] = result.nulls_removed

        if result.whitespace_chars_removed:
            trace['whitespace_chars_removed'] = result.whitespace_chars_removed

        if result.base64_blobs_removed:
            trace['base64_blobs_removed'] = result.base64_blobs_removed

        if result.unicode_chars_removed:
            trace['unicode_chars_removed'] = result.unicode_chars_removed

        if result.markup_items_removed:
            trace['markup_items_removed'] = result.markup_items_removed

        if result.urls_flagged:
            trace['urls_flagged'] = result.urls_flagged

        if result.was_rejected:
            trace['reject_kind'] = result.reject_kind

# ################################################################################################################################

    def _serialize_service_response(
        self,
        response:'any_',
        trace:'stranydict',
        response_filter:'any_' = None,
        ) -> 'str':
        """ Converts a service response to a text string suitable for MCP content,
        applying the gateway's response safeguards, the client's response filter
        and the token cap on the way, recording everything they did in the trace.
        Raises ResponseRejected when a safeguard or the cap refuses the response
        and FilterInvalid when the client's filter cannot be applied.
        """

        # Bytes are decoded up front so every later stage sees a JSON-serializable value ..
        if isinstance(response, bytes):
            response = response.decode('utf8')

        # .. safeguards run on the structured value, before any serialization,
        # and only when at least one stage is enabled, to skip the deep copy otherwise ..
        if is_safeguards_active(self.safeguard_config):
            safeguard_result = apply_safeguards(response, self.safeguard_config)
            self._record_safeguard_trace(safeguard_result, trace)

            # .. a rejection refuses the whole response, naming the kind of finding that caused it ..
            if safeguard_result.was_rejected:
                raise ResponseRejected(f'Response rejected: {safeguard_result.reject_kind}')

            response = safeguard_result.value

        # .. the client's filter runs after the safeguards, so it only ever sees cleaned data,
        # and before the token cap, so the cap enforces the size of what actually goes out ..
        if response_filter is not None:

            # A filter that is not a string at all is refused the same way a broken one is
            if not isinstance(response_filter, str):
                raise FilterInvalid(f'Invalid {_response_filter_key}: expected a string')

            filter_result = apply_filter(response_filter, response)

            if filter_result.error:
                raise FilterInvalid(f'Invalid {_response_filter_key}: {filter_result.error}')

            trace['client_filter'] = response_filter
            response = filter_result.value

        # .. the token cap runs on the possibly cleaned and filtered value, only when a cap is set at all ..
        if self.token_cap_config.max_response_tokens:
            cap_result = apply_token_cap(response, self.token_cap_config)

            # .. block mode refuses an oversized response outright, naming the size and the cap -
            # the trace records what was measured and that size was the reason ..
            if cap_result.was_blocked:
                trace['tokens_before'] = cap_result.tokens_before
                trace['reject_kind'] = _reject_kind_size

                cap = self.token_cap_config.max_response_tokens
                raise ResponseRejected(f'Response too large: {cap_result.tokens_before} tokens, cap is {cap}')

            # .. a truncation records both sides of the cut - an untouched response records nothing ..
            if cap_result.was_truncated:
                trace['tokens_before'] = cap_result.tokens_before
                trace['tokens_after'] = cap_result.tokens_after
                trace['was_truncated'] = True

            response = cap_result.value

        # .. a string result is returned as it is ..
        if isinstance(response, str):

            out = response
            return out

        # .. and everything else serializes to JSON.
        out = dumps(response)
        return out

# ################################################################################################################################

    def _handle_ping(self, request_id:'any_') -> 'stranydict':
        """ Handles the MCP ping request.
        """

        out = make_success_response(request_id, {})
        return out

# ################################################################################################################################

    def handle_delete_session(
        self,
        session_id:'strnone',
        sec_def_id:'int',
        protocol_version_header:'strnone' = None,
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
        # An identity mismatch returns 400 to reject without confirming whether the session exists ..
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
