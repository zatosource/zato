# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import dataclasses

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydictnone, stranydict, strnone

# ################################################################################################################################
# ################################################################################################################################

# JSON-RPC 2.0 error codes
_error_parse            = -32700
_error_invalid_request  = -32600
_error_method_not_found = -32601
_error_invalid_params   = -32602

# JSON-RPC 2.0 version string
_jsonrpc_version = '2.0'

# The tools/call method is the only tool method that carries a tool name
_method_tools_call = 'tools/call'

# The prompts methods, of which prompts/get carries a prompt name
# the way tools/call carries a tool name
_method_prompts_list = 'prompts/list'
_method_prompts_get  = 'prompts/get'

# Generic error message returned to clients for all session-related rejections
_message_bad_request = 'Bad request'

# Error message returned when parse fails
_message_parse_error = 'Parse error'

# Error message returned when the top-level request is structurally invalid
_message_invalid_request = 'Invalid request'

# Error message returned when the jsonrpc version field is missing or wrong
_message_missing_jsonrpc_version = 'Invalid request: missing or wrong jsonrpc version'

# Error message returned when the method field is missing
_message_missing_method = 'Invalid request: missing method'

# Error message returned when the required tool name parameter is absent
_message_missing_tool_name = 'Missing required parameter: name'

# Error message returned when the prompt name does not point to a skill this gateway serves
_message_prompt_not_found = 'Prompt not found'

# Error message returned when the cursor parameter is not one the gateway issued
_message_invalid_cursor = 'Invalid cursor value'

# Error message returned when the size cap blocks a response
_message_response_too_large = 'Response too large'

# Error message returned when params is present but is not an object
_message_invalid_params = 'Invalid params: expected an object'

# Server metadata returned to clients
_server_name    = 'Apache'
_server_version = '2.4'

# ################################################################################################################################
# ################################################################################################################################

class InvalidCursor(Exception):
    """ Raised when a tools/list or prompts/list cursor is not one the gateway issued.
    """

# ################################################################################################################################
# ################################################################################################################################

@dataclasses.dataclass(init=False)
class MCPResponse:
    """ Wraps a JSON-RPC response body, HTTP status code, and optional session ID.
    The method and tool name are recorded during dispatch for the audit log,
    so the endpoint never has to re-parse the raw body to learn them.
    The trace carries what the response safeguards, the token cap and the client filter
    did to a tools/call response - only tool calls that changed or refused anything have one.
    """
    body:         'any_'
    status_code:  'int'
    session_id:   'strnone'    = None
    method:       'strnone'    = None
    tool_name:    'strnone'    = None
    trace:        'anydictnone' = None

# ################################################################################################################################
# ################################################################################################################################

def make_error_response(request_id:'any_', code:'int', message:'str') -> 'stranydict':
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

def make_success_response(request_id:'any_', result:'any_') -> 'stranydict':
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
