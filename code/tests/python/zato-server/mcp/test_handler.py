# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK
from unittest import TestCase

# Zato
from zato.common.api import MCP
from zato.common.json_internal import dumps
from zato.common.test import _test_sec_def_id
from zato.common.util.safeguards.config import build_safeguard_config
from zato.common.util.truncate.tokens import build_token_cap_config
from zato.server.connection.mcp.handler import MCPHandler, _error_invalid_params, _error_invalid_request, \
    _error_method_not_found, _error_parse, _jsonrpc_version, _mcp_protocol_version, _message_bad_request, \
    _message_request_too_deep, _server_name, _server_version
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
        self.get_tools_call_count = 0

# ################################################################################################################################

    def get_tools(self) -> 'anylist':
        self.get_tools_call_count += 1
        return self.tools

# ################################################################################################################################

    def get_tools_page(self, cursor:'strnone' = None) -> 'tuple':
        self.get_tools_call_count += 1
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

class HandleInitialize(TestCase):

    def test_initialize_returns_capabilities(self) -> 'None':
        """ Verifies that initialize returns protocol version, capabilities and server info.
        """

        handler = _make_handler()

        request = _make_request('initialize', params=_initialize_params)
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        self.assertEqual(body['jsonrpc'], _jsonrpc_version)
        self.assertEqual(body['id'], 1)

        result = body['result']
        self.assertEqual(result['protocolVersion'], _mcp_protocol_version)

        capabilities = result['capabilities']
        tools_capability = capabilities['tools']
        self.assertIsInstance(tools_capability, dict)

        server_info = result['serverInfo']
        self.assertEqual(server_info['name'], _server_name)
        self.assertEqual(server_info['version'], _server_version)

        # Session ID should be set on the response
        self.assertIsNotNone(mcp_response.session_id)

# ################################################################################################################################
# ################################################################################################################################

class HandleToolsList(TestCase):

    def test_tools_list_returns_tools(self) -> 'None':
        """ Verifies that tools/list returns the registered tools.
        """

        tools = [
            {'name': 'crm.get-customer', 'description': 'Get customer', 'inputSchema': {'type': 'object'}},
        ]
        registry = _MockToolRegistry(tools=tools)
        handler = _make_handler(registry=registry)
        session_id = _make_session(handler)

        request = _make_request('tools/list')
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        result = body['result']
        self.assertEqual(result['tools'], tools)

    def test_tools_list_empty(self) -> 'None':
        """ Verifies that tools/list returns an empty list when no tools are registered.
        """

        registry = _MockToolRegistry(tools=[])
        handler = _make_handler(registry=registry)
        session_id = _make_session(handler)

        request = _make_request('tools/list')
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        result = body['result']
        self.assertEqual(result['tools'], [])

# ################################################################################################################################
# ################################################################################################################################

class HandleToolsListPagination(TestCase):

    def test_tools_list_with_cursor(self) -> 'None':
        """ Verifies that tools/list returns a next cursor when paginated.
        """

        page1 = [{'name': 'svc.a', 'description': '', 'inputSchema': {'type': 'object'}}]

        class _PaginatingRegistry(_MockToolRegistry):
            def get_tools_page(self, cursor:'strnone'=None) -> 'tuple':
                if cursor is None:
                    return page1, '1'
                return [], None

        registry = _PaginatingRegistry()
        handler = _make_handler(registry=registry)
        session_id = _make_session(handler)

        # First page (no cursor)
        request = _make_request('tools/list')
        raw = dumps(request)
        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

        body = mcp_response.body
        result = body['result']
        self.assertEqual(result['tools'], page1)
        self.assertEqual(result['nextCursor'], '1')

    def test_tools_list_last_page_no_next_cursor(self) -> 'None':
        """ Verifies that the last page does not include a nextCursor field.
        """

        tools = [{'name': 'svc.a', 'description': '', 'inputSchema': {'type': 'object'}}]

        class _NoPaginationRegistry(_MockToolRegistry):
            def get_tools_page(self, cursor:'strnone'=None) -> 'tuple':
                return tools, None

        registry = _NoPaginationRegistry()
        handler = _make_handler(registry=registry)
        session_id = _make_session(handler)

        request = _make_request('tools/list')
        raw = dumps(request)
        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

        body = mcp_response.body
        result = body['result']
        self.assertEqual(result['tools'], tools)
        self.assertNotIn('nextCursor', result)

    def test_tools_list_passes_cursor_from_params(self) -> 'None':
        """ Verifies that the cursor from params is passed to get_tools_page.
        """

        captured_cursors = []

        class _CapturingRegistry(_MockToolRegistry):
            def get_tools_page(self, cursor:'strnone'=None) -> 'tuple':
                captured_cursors.append(cursor)
                return [], None

        registry = _CapturingRegistry()
        handler = _make_handler(registry=registry)
        session_id = _make_session(handler)

        request = _make_request('tools/list', params={'cursor': '42'})
        raw = dumps(request)
        _ = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

        self.assertEqual(captured_cursors, ['42'])

# ################################################################################################################################
# ################################################################################################################################

class HandlePing(TestCase):

    def test_ping_returns_empty_result(self) -> 'None':
        """ Verifies that ping returns an empty result object.
        """

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)
        session_id = _make_session(handler)

        request = _make_request('ping')
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        result = body['result']
        self.assertEqual(result, {})

# ################################################################################################################################
# ################################################################################################################################

class HandleParseError(TestCase):

    def test_malformed_json(self) -> 'None':
        """ Verifies that malformed JSON produces a parse error.
        """

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)

        mcp_response = handler.handle_raw_request(b'not json at all', _test_sec_def_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        error = body['error']
        self.assertEqual(error['code'], _error_parse)

    def test_non_object_non_array(self) -> 'None':
        """ Verifies that a non-object non-array JSON value produces an invalid request error.
        """

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)

        mcp_response = handler.handle_raw_request(b'"just a string"', _test_sec_def_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        error = body['error']
        self.assertEqual(error['code'], _error_invalid_request)

# ################################################################################################################################
# ################################################################################################################################

class HandleInvalidRequest(TestCase):

    def test_missing_jsonrpc_field(self) -> 'None':
        """ Verifies that a missing jsonrpc field produces an invalid request error.
        """

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)
        session_id = _make_session(handler)

        request = {'method': 'ping', 'id': 1}
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        error = body['error']
        self.assertEqual(error['code'], _error_invalid_request)

    def test_wrong_jsonrpc_version(self) -> 'None':
        """ Verifies that a wrong jsonrpc version produces an invalid request error.
        """

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)
        session_id = _make_session(handler)

        request = {'jsonrpc': '1.0', 'method': 'ping', 'id': 1}
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        error = body['error']
        self.assertEqual(error['code'], _error_invalid_request)

    def test_missing_method(self) -> 'None':
        """ Verifies that a missing method field produces an invalid request error.
        """

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)
        session_id = _make_session(handler)

        request = {'jsonrpc': '2.0', 'id': 1}
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        error = body['error']
        self.assertEqual(error['code'], _error_invalid_request)

    def test_unknown_method(self) -> 'None':
        """ Verifies that an unknown method returns method not found.
        """

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)
        session_id = _make_session(handler)

        request = _make_request('nonexistent/method')
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        error = body['error']
        self.assertEqual(error['code'], _error_method_not_found)

# ################################################################################################################################
# ################################################################################################################################

class HandleArrayBody(TestCase):
    """ Tests that array bodies are rejected - batching is not part of any supported protocol revision.
    """

    def test_array_of_requests_is_invalid(self) -> 'None':
        """ An array of otherwise valid requests returns a single invalid request error.
        """

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)
        session_id = _make_session(handler)

        messages = [
            _make_request('ping', request_id=1),
            _make_request('ping', request_id=2),
        ]
        raw = dumps(messages)

        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        error = body['error']
        self.assertEqual(error['code'], _error_invalid_request)

    def test_empty_array_is_invalid(self) -> 'None':
        """ An empty array returns an invalid request error.
        """

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)

        raw = dumps([])

        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        error = body['error']
        self.assertEqual(error['code'], _error_invalid_request)

# ################################################################################################################################
# ################################################################################################################################

class HandleMalformedInput(TestCase):
    """ Tests that structurally invalid input produces JSON-RPC errors, never exceptions.
    """

    def test_params_as_list_rejected(self) -> 'None':
        """ A params field that is a list produces an invalid params error.
        """

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)
        session_id = _make_session(handler)

        request = {'jsonrpc': '2.0', 'method': 'tools/list', 'id': 1, 'params': ['not', 'an', 'object']}
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        error = body['error']
        self.assertEqual(error['code'], _error_invalid_params)

    def test_params_as_string_rejected(self) -> 'None':
        """ A params field that is a string produces an invalid params error.
        """

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)
        session_id = _make_session(handler)

        request = {'jsonrpc': '2.0', 'method': 'tools/call', 'id': 1, 'params': 'name=demo.echo'}
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        error = body['error']
        self.assertEqual(error['code'], _error_invalid_params)

    def test_params_as_number_in_initialize_rejected(self) -> 'None':
        """ Initialize with a numeric params field is rejected and creates no session.
        """

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)
        session_manager = handler.session_manager

        request = {'jsonrpc': '2.0', 'method': 'initialize', 'id': 1, 'params': 123}
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        error = body['error']
        self.assertEqual(error['code'], _error_invalid_params)

        # No session must have been created for the rejected initialize
        self.assertIsNone(mcp_response.session_id)
        self.assertEqual(session_manager.session_count, 0)

    def test_undecodable_bytes_response_returns_is_error(self) -> 'None':
        """ A service response of bytes that do not decode as UTF-8
        produces an isError result, not an exception.
        """

        def invoke_invalid_bytes(service_name:'str', payload:'anydict') -> 'bytes':
            return b'\xff\xfe invalid utf8 \xff'

        registry = _MockToolRegistry(allowed_tools={'test.service'})
        handler = _make_handler(registry=registry, invoke_func=invoke_invalid_bytes)
        session_id = _make_session(handler)

        params = {'name': 'test.service', 'arguments': {}}
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

    def test_unserializable_response_returns_is_error(self) -> 'None':
        """ A service response that cannot be dumped to JSON
        produces an isError result, not an exception.
        """

        def invoke_unserializable(service_name:'str', payload:'anydict') -> 'any_':
            return object()

        registry = _MockToolRegistry(allowed_tools={'test.service'})
        handler = _make_handler(registry=registry, invoke_func=invoke_unserializable)
        session_id = _make_session(handler)

        params = {'name': 'test.service', 'arguments': {}}
        request = _make_request('tools/call', params)
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        result = body['result']
        self.assertTrue(result['isError'])

# ################################################################################################################################
# ################################################################################################################################

def _make_nested_value(levels:'int') -> 'anydict':
    """ Builds a dict-in-dict chain of the given number of levels.
    """

    out:'anydict' = {'level': 'bottom'}

    for _ in range(levels - 1):
        out = {'level': out}

    return out

# ################################################################################################################################
# ################################################################################################################################

class HandleRequestDepth(TestCase):
    """ Tests the bound on how deeply a request body may nest, over and above the byte size bound.
    """

    def test_a_body_past_the_depth_bound_is_invalid(self) -> 'None':
        """ A body nested past the published depth bound is a clean invalid request.
        """

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)
        session_id = _make_session(handler)

        # The body and params levels sit on top of the nested chain,
        # so the chain alone already exceeds the bound.
        nested = _make_nested_value(MCP.Max_Request_Depth + 50)

        request = _make_request('ping', params={'context': nested})
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        error = body['error']
        self.assertEqual(error['code'], _error_invalid_request)
        self.assertEqual(error['message'], _message_request_too_deep)

    def test_a_body_under_the_depth_bound_is_served(self) -> 'None':
        """ A body whose nesting stays under the bound dispatches like any other.
        """

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)
        session_id = _make_session(handler)

        # The body and params levels sit on top of the nested chain, hence the headroom
        nested = _make_nested_value(MCP.Max_Request_Depth - 10)

        request = _make_request('ping', params={'context': nested})
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        result = body['result']
        self.assertEqual(result, {})

# ################################################################################################################################
# ################################################################################################################################
