# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# gevent
from gevent import Timeout as GeventTimeout

# Zato
from zato.common.json_internal import dumps
from zato.common.util.message_filters.api import apply_filter
from zato.common.util.safeguards.api import apply_safeguards
from zato.common.util.safeguards.config import is_safeguards_active
from zato.common.util.truncate.tokens import apply_token_cap
from zato.server.connection.mcp.common import _error_invalid_params, _error_method_not_found, _message_bad_request, \
    _message_missing_tool_name, _message_response_too_large, make_error_response, make_success_response, printable
from zato.server.connection.mcp.validate import _message_not_an_object, validate_arguments

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anydictnone, stranydict
    from zato.server.connection.mcp.handler import MCPHandler

    MCPHandler = MCPHandler

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

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

def handle_tools_call(handler:'MCPHandler', request_id:'any_', params:'anydict') -> 'tuple[stranydict, anydictnone]':
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
    if not handler.tool_registry.is_tool_allowed(tool_name):

        message = f'Tool not found: `{printable(tool_name)}`'
        out = make_error_response(request_id, _error_method_not_found, message)
        return out, None

    # .. extract arguments - optional per the MCP spec, defaults to empty dict ..
    arguments = params.get('arguments', {})

    # .. whatever validation is configured, the arguments element must be an object ..
    if not isinstance(arguments, dict):

        out = make_error_response(request_id, _error_invalid_params, _message_not_an_object)
        return out, None

    # .. on a gateway that allows client filters, the response_filter argument belongs
    # to the gateway, not to the service - it is taken out before validation ever sees it ..
    response_filter = None

    if handler.allow_client_filters:
        response_filter = arguments.pop(_response_filter_key, None)

    # .. when the gateway has input validation on, the arguments must match the tool's
    # input schema, the same one tools/list advertises - the error names the offending field ..
    if handler.validate_input:
        schema = handler.tool_registry.get_tool_schema(tool_name)

        if error_message := validate_arguments(arguments, schema):
            logger.info('MCP: Invalid arguments for `%s`: %s', tool_name, error_message)
            out = make_error_response(request_id, _error_invalid_params, error_message)
            return out, None

    # The trace of everything shaping does to this response, filled in along the way
    trace:'stranydict' = {}

    # .. invoke the service under the gateway's timeout and serialize its response,
    # treating a serialization failure (e.g. bytes that do not decode or objects
    # that do not dump to JSON) the same way as a service exception ..
    try:
        with GeventTimeout(handler.invoke_timeout):
            service_response = handler.invoke_func(tool_name, arguments)

        response_text = serialize_service_response(handler, service_response, trace, response_filter)

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
        return out, _trace_or_none(trace)

    # .. an invalid client filter is the caller's own mistake and is reported as invalid params ..
    except FilterInvalid as e:
        logger.info('MCP: Invalid response filter for `%s`: %s', tool_name, printable(e))

        out = make_error_response(request_id, _error_invalid_params, str(e))
        return out, _trace_or_none(trace)

    # .. a service that ran past the gateway's timeout is cut off - gevent's Timeout
    # is a BaseException, so the branch below would never see it. The bound goes
    # to the log and the trace only, the client gets the generic refusal ..
    except GeventTimeout:
        timeout_message = f'Tool call timed out after {handler.invoke_timeout} seconds'
        logger.warning('MCP: Service `%s` timed out after %s seconds', tool_name, handler.invoke_timeout)

        timeout_result:'stranydict' = {
            'content': [
                {
                    'type': 'text',
                    'text': _message_bad_request,
                },
            ],
            'isError': True,
        }

        trace['error_message'] = timeout_message

        out = make_success_response(request_id, timeout_result)
        return out, _trace_or_none(trace)

    # .. a service exception goes to the log and the trace only too ..
    except Exception as e:
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

        trace['error_message'] = str(e)

        out = make_success_response(request_id, error_result)
        return out, _trace_or_none(trace)

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
    return out, _trace_or_none(trace)

# ################################################################################################################################
# ################################################################################################################################

def _trace_or_none(trace:'stranydict') -> 'anydictnone':
    """ An empty trace travels as None so the audit log never records an empty document.
    """

    if trace:
        out = trace
    else:
        out = None

    return out

# ################################################################################################################################
# ################################################################################################################################

def _record_safeguard_trace(result:'any_', trace:'stranydict') -> 'None':
    """ Copies what the safeguards did into the trace - only the counters
    that actually counted something are recorded.
    """

    if result.pii_removed:
        trace['pii_removed'] = result.pii_removed

    if result.secrets_removed:
        trace['secrets_removed'] = result.secrets_removed

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
# ################################################################################################################################

def serialize_service_response(
    handler:'MCPHandler',
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
    if is_safeguards_active(handler.safeguard_config):
        safeguard_result = apply_safeguards(response, handler.safeguard_config)
        _record_safeguard_trace(safeguard_result, trace)

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
    if handler.token_cap_config.max_response_tokens:
        cap_result = apply_token_cap(response, handler.token_cap_config)

        # .. block mode refuses an oversized response outright - the measured size
        # and the reason go to the trace, never to the client ..
        if cap_result.was_blocked:
            trace['tokens_before'] = cap_result.tokens_before
            trace['reject_kind'] = _reject_kind_size

            raise ResponseRejected(_message_response_too_large)

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
# ################################################################################################################################
