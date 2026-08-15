# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK
from unittest import TestCase

# gevent
from gevent import sleep as gevent_sleep

# Zato
from zato.common.api import MCP
from zato.common.json_internal import dumps
from zato.common.test import _test_sec_def_id
from zato.common.util.safeguards.config import build_safeguard_config
from zato.common.util.truncate.tokens import build_token_cap_config
from zato.server.connection.mcp.handler import MCPHandler, _error_invalid_params, _error_method_not_found, \
    _mcp_protocol_version, _message_bad_request
from zato.server.connection.mcp.prompts import SkillPrompts
from zato.server.connection.mcp.session import MCPSessionManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anydictnone, anylist, anylistnone, callable_, strnone

# ################################################################################################################################
# ################################################################################################################################

class _MockToolRegistry:
    """ Mock tool registry that returns a fixed list of tools.
    """
    def __init__(self, tools:'anylistnone' = None, allowed_tools:'set | None' = None) -> 'None':
        self.tools = tools if tools is not None else []
        self.allowed_tools = allowed_tools if allowed_tools is not None else set()

# ################################################################################################################################

    def get_tools(self) -> 'anylist':
        return self.tools

# ################################################################################################################################

    def get_tools_page(self, cursor:'strnone' = None) -> 'tuple':
        return self.tools, None

# ################################################################################################################################

    def is_tool_allowed(self, service_name:'str') -> 'bool':
        return service_name in self.allowed_tools

# ################################################################################################################################
# ################################################################################################################################

def _make_request(method:'str', params:'anydictnone' = None, request_id:'any_' = 1) -> 'anydict':

    out = {
        'jsonrpc': '2.0',
        'method': method,
        'id': request_id,
    }

    if params is not None:
        out['params'] = params

    return out

# ################################################################################################################################

# Standard params for initialize requests in tests
_initialize_params = {
    'protocolVersion': _mcp_protocol_version,
    'capabilities': {},
    'clientInfo': {'name': 'test', 'version': '1.0'},
}

# ################################################################################################################################
# ################################################################################################################################

def _invoke_success(service_name:'str', payload:'anydict') -> 'anydict':
    """ Mock invoke function that returns a simple dict.
    """

    return {'service': service_name, 'input': payload}

# ################################################################################################################################
# ################################################################################################################################

_test_service_error_message = 'Test service error'

def _invoke_raises(service_name:'str', payload:'anydict') -> 'None':
    """ Mock invoke function that raises an exception.
    """

    raise Exception(_test_service_error_message)

# ################################################################################################################################
# ################################################################################################################################

def _make_handler(
    registry:'any_'=None,
    invoke_func:'callable_'=None,
    invoke_timeout:'int'=MCP.Default_Invoke_Timeout,
    ) -> 'MCPHandler':
    """ Creates an MCPHandler with defaults for tests.
    """

    if registry is None:
        registry = _MockToolRegistry()

    if invoke_func is None:
        invoke_func = _invoke_success

    session_manager = MCPSessionManager()

    # Response shaping and input validation stay off in these tests - empty configs keep every stage disabled.
    safeguard_config = build_safeguard_config({})
    token_cap_config = build_token_cap_config({})

    out = MCPHandler(registry, invoke_func, session_manager, safeguard_config, token_cap_config, False, SkillPrompts('', []), invoke_timeout=invoke_timeout) # pyright: ignore[reportArgumentType]
    return out

# ################################################################################################################################
# ################################################################################################################################

def _make_session(handler:'MCPHandler') -> 'str':
    """ Creates a valid session on the handler's manager and returns its ID.
    Every method other than initialize requires one.
    """

    session_manager = handler.session_manager
    out = session_manager.create(_mcp_protocol_version, _test_sec_def_id)
    return out

# ################################################################################################################################
# ################################################################################################################################

class HandleToolsCall(TestCase):

    def test_successful_invocation(self) -> 'None':
        """ Verifies that tools/call invokes the service and returns content.
        """

        registry = _MockToolRegistry(allowed_tools={'crm.get-customer'})
        handler = _make_handler(registry=registry)
        session_id = _make_session(handler)

        params = {'name': 'crm.get-customer', 'arguments': {'customer_id': '123'}}
        request = _make_request('tools/call', params)
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        result = body['result']
        self.assertNotIn('isError', result)

        content = result['content']
        self.assertEqual(len(content), 1)

        first_content = content[0]
        self.assertEqual(first_content['type'], 'text')

    def test_missing_tool_name(self) -> 'None':
        """ Verifies that tools/call without a name returns invalid params error.
        """

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)
        session_id = _make_session(handler)

        request = _make_request('tools/call', {})
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        error = body['error']
        self.assertEqual(error['code'], _error_invalid_params)

    def test_disallowed_tool(self) -> 'None':
        """ Verifies that calling a disallowed tool returns method not found.
        """

        registry = _MockToolRegistry(allowed_tools=set())
        handler = _make_handler(registry=registry)
        session_id = _make_session(handler)

        params = {'name': 'secret.internal-service'}
        request = _make_request('tools/call', params)
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        error = body['error']
        self.assertEqual(error['code'], _error_method_not_found)

    def test_service_exception_returns_is_error(self) -> 'None':
        """ Verifies that a service exception produces isError with the error message.
        """

        registry = _MockToolRegistry(allowed_tools={'crm.get-customer'})
        handler = _make_handler(registry=registry, invoke_func=_invoke_raises)
        session_id = _make_session(handler)

        params = {'name': 'crm.get-customer', 'arguments': {}}
        request = _make_request('tools/call', params)
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        result = body['result']
        self.assertTrue(result['isError'])

        content = result['content']
        first_content = content[0]
        text = first_content['text']
        self.assertEqual(text, _message_bad_request)

        # The exception's own message goes to the audit trace, never to the client
        self.assertEqual(mcp_response.trace, {'error_message': _test_service_error_message})

    def test_service_timeout_returns_is_error(self) -> 'None':
        """ Verifies that a service running past the gateway's invoke timeout
        is cut off with the generic error, the bound named in the trace only.
        """

        def invoke_slow(service_name:'str', payload:'anydict') -> 'None':
            gevent_sleep(2)

        registry = _MockToolRegistry(allowed_tools={'crm.get-customer'})
        handler = _make_handler(registry=registry, invoke_func=invoke_slow, invoke_timeout=1)
        session_id = _make_session(handler)

        params = {'name': 'crm.get-customer', 'arguments': {}}
        request = _make_request('tools/call', params)
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

        self.assertEqual(mcp_response.status_code, OK)

        result = mcp_response.body['result']
        self.assertTrue(result['isError'])

        # The client sees the generic refusal, not the bound
        text = result['content'][0]['text']
        self.assertEqual(text, _message_bad_request)

        # The audit trace records the bound
        self.assertEqual(mcp_response.trace, {'error_message': 'Tool call timed out after 1 seconds'})

    def test_string_response_serialized(self) -> 'None':
        """ Verifies that a string service response is serialized as text content.
        """

        def invoke_string(service_name:'str', payload:'anydict') -> 'str':
            return 'plain text response'

        registry = _MockToolRegistry(allowed_tools={'test.service'})
        handler = _make_handler(registry=registry, invoke_func=invoke_string)
        session_id = _make_session(handler)

        params = {'name': 'test.service', 'arguments': {}}
        request = _make_request('tools/call', params)
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

        body = mcp_response.body
        result = body['result']
        content = result['content']
        first_content = content[0]
        text = first_content['text']
        self.assertEqual(text, 'plain text response')

    def test_dict_response_serialized_as_json(self) -> 'None':
        """ Verifies that a dict service response is serialized as JSON text.
        """

        def invoke_dict(service_name:'str', payload:'anydict') -> 'anydict':
            return {'key': 'value'}

        registry = _MockToolRegistry(allowed_tools={'test.service'})
        handler = _make_handler(registry=registry, invoke_func=invoke_dict)
        session_id = _make_session(handler)

        params = {'name': 'test.service', 'arguments': {}}
        request = _make_request('tools/call', params)
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

        body = mcp_response.body
        result = body['result']
        content = result['content']
        first_content = content[0]
        text = first_content['text']
        self.assertIn('key', text)
        self.assertIn('value', text)

    def test_no_arguments_defaults_to_empty_dict(self) -> 'None':
        """ Verifies that omitting arguments defaults to an empty dict payload.
        """

        received_payloads = []

        def invoke_capture(service_name:'str', payload:'anydict') -> 'str':
            received_payloads.append(payload)
            return 'ok'

        registry = _MockToolRegistry(allowed_tools={'test.service'})
        handler = _make_handler(registry=registry, invoke_func=invoke_capture)
        session_id = _make_session(handler)

        params = {'name': 'test.service'}
        request = _make_request('tools/call', params)
        raw = dumps(request)

        _ = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

        first_payload = received_payloads[0]
        self.assertEqual(first_payload, {})

# ################################################################################################################################
# ################################################################################################################################

class HandleConcurrentDispatch(TestCase):
    """ Tests dispatch behavior when requests sharing one handler instance interleave.
    """

    def test_tools_call_response_carries_no_session_id(self) -> 'None':
        """ A tools/call response carries no session ID even when another
        request runs on the same handler during its service invocation.
        """

        registry = _MockToolRegistry(allowed_tools={'crm.get-customer'})

        # Shared slots so the invoke function can reach the handler after it is built
        # and so the test can inspect the interleaved response afterwards
        handler_holder:'anylist' = []
        interleaved_responses:'anylist' = []

        def invoke_with_interleaved_initialize(service_name:'str', payload:'anydict') -> 'str':
            """ Runs a full initialize on the same handler mid-call,
            the way concurrent requests interleave at runtime.
            """

            handler = handler_holder[0]

            initialize_request = _make_request('initialize', params=_initialize_params, request_id=99)
            raw = dumps(initialize_request)

            interleaved_response = handler.handle_raw_request(raw, _test_sec_def_id)
            interleaved_responses.append(interleaved_response)

            return 'Customer details'

        handler = _make_handler(registry=registry, invoke_func=invoke_with_interleaved_initialize)
        handler_holder.append(handler)
        session_id = _make_session(handler)

        # Run a tools/call whose service invocation triggers the interleaved initialize ..
        params = {'name': 'crm.get-customer', 'arguments': {'customer_id': '123'}}
        request = _make_request('tools/call', params)
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

        # .. the interleaved initialize must have created its own session ..
        interleaved_response = interleaved_responses[0]
        self.assertIsNotNone(interleaved_response.session_id)

        # .. the outer tools/call must have succeeded ..
        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        self.assertIn('result', body)

        # .. and per the spec only initialize responses carry a session ID.
        self.assertIsNone(mcp_response.session_id)

    def test_interleaved_initialize_responses_carry_their_own_session_ids(self) -> 'None':
        """ Two initialize calls where the second one runs while the first one
        is still being dispatched must each report their own session ID.
        """

        registry = _MockToolRegistry(allowed_tools={'crm.get-customer'})

        # Shared slots so the invoke function can reach the handler after it is built
        # and so the test can inspect the interleaved response afterwards
        handler_holder:'anylist' = []
        interleaved_responses:'anylist' = []

        def invoke_with_interleaved_initialize(service_name:'str', payload:'anydict') -> 'str':
            """ Runs an initialize on the same handler mid-call.
            """

            handler = handler_holder[0]

            initialize_request = _make_request('initialize', params=_initialize_params, request_id=99)
            raw = dumps(initialize_request)

            interleaved_response = handler.handle_raw_request(raw, _test_sec_def_id)
            interleaved_responses.append(interleaved_response)

            return 'Customer details'

        handler = _make_handler(registry=registry, invoke_func=invoke_with_interleaved_initialize)
        handler_holder.append(handler)
        session_id = _make_session(handler)

        # Run a tools/call that interleaves an initialize, then a plain initialize afterwards ..
        params = {'name': 'crm.get-customer', 'arguments': {'customer_id': '123'}}
        tools_call_request = _make_request('tools/call', params)
        raw = dumps(tools_call_request)
        _ = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

        initialize_request = _make_request('initialize', params=_initialize_params, request_id=2)
        raw = dumps(initialize_request)
        initialize_response = handler.handle_raw_request(raw, _test_sec_def_id)

        # .. both initialize responses must carry session IDs ..
        interleaved_response = interleaved_responses[0]
        self.assertIsNotNone(interleaved_response.session_id)
        self.assertIsNotNone(initialize_response.session_id)

        # .. and the two session IDs must differ.
        self.assertNotEqual(interleaved_response.session_id, initialize_response.session_id)

# ################################################################################################################################
# ################################################################################################################################
