# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import NO_CONTENT, OK
from unittest import TestCase

# Zato
from zato.common.json_internal import dumps
from zato.server.connection.mcp.handler import MCPHandler, _error_invalid_params, _error_invalid_req, \
    _error_method_not_found, _error_parse, _jsonrpc_version, _mcp_protocol_version, _server_name, _server_version
from zato.server.connection.mcp.session import MCPSessionManager

# ################################################################################################################################
# ################################################################################################################################

class _MockToolRegistry:
    """ Mock tool registry that returns a fixed list of tools.
    """
    def __init__(self, tools=None, allowed_tools=None): # type: ignore
        self.tools = tools if tools is not None else []
        self.allowed_tools = allowed_tools if allowed_tools is not None else set()
        self.get_tools_call_count = 0

# ################################################################################################################################

    def get_tools(self): # type: ignore
        self.get_tools_call_count += 1
        return self.tools

# ################################################################################################################################

    def get_tools_page(self, cursor=None): # type: ignore
        self.get_tools_call_count += 1
        return self.tools, None

# ################################################################################################################################

    def is_tool_allowed(self, service_name): # type: ignore
        return service_name in self.allowed_tools

# ################################################################################################################################
# ################################################################################################################################

def _make_request(method, params=None, request_id=1): # type: ignore

    out = {
        'jsonrpc': '2.0',
        'method': method,
        'id': request_id,
    }

    if params is not None:
        out['params'] = params

    return out

# ################################################################################################################################
# ################################################################################################################################

def _invoke_success(service_name, payload): # type: ignore
    """ Mock invoke function that returns a simple dict.
    """
    return {'service': service_name, 'input': payload}

# ################################################################################################################################
# ################################################################################################################################

_test_service_error_message = 'Test service error'

def _invoke_raises(service_name, payload): # type: ignore
    """ Mock invoke function that raises an exception.
    """
    raise Exception(_test_service_error_message)

# ################################################################################################################################
# ################################################################################################################################

def _make_handler(registry=None, invoke_func=None): # type: ignore
    """ Creates an MCPHandler with defaults for tests.
    """
    if registry is None:
        registry = _MockToolRegistry()

    if invoke_func is None:
        invoke_func = _invoke_success

    session_manager = MCPSessionManager()

    out = MCPHandler(registry, invoke_func, session_manager)
    return out

# ################################################################################################################################
# ################################################################################################################################

class HandleInitialize(TestCase):

    def test_initialize_returns_capabilities(self): # type: ignore

        handler = _make_handler()

        request = _make_request('initialize')
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.status_code, OK)
        self.assertEqual(mcp_response.body['jsonrpc'], _jsonrpc_version)
        self.assertEqual(mcp_response.body['id'], 1)

        result = mcp_response.body['result']
        self.assertEqual(result['protocolVersion'], _mcp_protocol_version)
        self.assertTrue(result['capabilities']['tools']['listChanged'])
        self.assertEqual(result['serverInfo']['name'], _server_name)
        self.assertEqual(result['serverInfo']['version'], _server_version)

        # Session ID should be set on the response
        self.assertIsNotNone(mcp_response.session_id)

# ################################################################################################################################
# ################################################################################################################################

class HandleToolsList(TestCase):

    def test_tools_list_returns_tools(self): # type: ignore

        tools = [
            {'name': 'crm.get-customer', 'description': 'Get customer', 'inputSchema': {'type': 'object'}},
        ]
        registry = _MockToolRegistry(tools=tools)
        handler = _make_handler(registry=registry)

        request = _make_request('tools/list')
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.status_code, OK)
        self.assertEqual(mcp_response.body['result']['tools'], tools)

    def test_tools_list_empty(self): # type: ignore

        registry = _MockToolRegistry(tools=[])
        handler = _make_handler(registry=registry)

        request = _make_request('tools/list')
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.status_code, OK)
        self.assertEqual(mcp_response.body['result']['tools'], [])

# ################################################################################################################################
# ################################################################################################################################

class HandleToolsListPagination(TestCase):

    def test_tools_list_with_cursor(self): # type: ignore

        page1 = [{'name': 'svc.a', 'description': '', 'inputSchema': {'type': 'object'}}]

        class _PaginatingRegistry(_MockToolRegistry):
            def get_tools_page(self, cursor=None): # type: ignore
                if cursor is None:
                    return page1, '1'
                return [], None

        registry = _PaginatingRegistry()
        handler = _make_handler(registry=registry)

        # First page (no cursor)
        request = _make_request('tools/list')
        raw = dumps(request)
        mcp_response = handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.body['result']['tools'], page1)
        self.assertEqual(mcp_response.body['result']['nextCursor'], '1')

    def test_tools_list_last_page_no_next_cursor(self): # type: ignore

        tools = [{'name': 'svc.a', 'description': '', 'inputSchema': {'type': 'object'}}]

        class _NoPaginationRegistry(_MockToolRegistry):
            def get_tools_page(self, cursor=None): # type: ignore
                return tools, None

        registry = _NoPaginationRegistry()
        handler = _make_handler(registry=registry)

        request = _make_request('tools/list')
        raw = dumps(request)
        mcp_response = handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.body['result']['tools'], tools)
        self.assertNotIn('nextCursor', mcp_response.body['result'])

    def test_tools_list_passes_cursor_from_params(self): # type: ignore

        captured_cursors = []

        class _CapturingRegistry(_MockToolRegistry):
            def get_tools_page(self, cursor=None): # type: ignore
                captured_cursors.append(cursor)
                return [], None

        registry = _CapturingRegistry()
        handler = _make_handler(registry=registry)

        request = _make_request('tools/list', params={'cursor': '42'})
        raw = dumps(request)
        handler.handle_raw_request(raw)

        self.assertEqual(captured_cursors, ['42'])

# ################################################################################################################################
# ################################################################################################################################

class HandleToolsCall(TestCase):

    def test_successful_invocation(self): # type: ignore

        registry = _MockToolRegistry(allowed_tools={'crm.get-customer'})
        handler = _make_handler(registry=registry)

        params = {'name': 'crm.get-customer', 'arguments': {'customer_id': '123'}}
        request = _make_request('tools/call', params)
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.status_code, OK)

        result = mcp_response.body['result']
        self.assertNotIn('isError', result)
        self.assertEqual(len(result['content']), 1)
        self.assertEqual(result['content'][0]['type'], 'text')

    def test_missing_tool_name(self): # type: ignore

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)

        request = _make_request('tools/call', {})
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.status_code, OK)
        self.assertEqual(mcp_response.body['error']['code'], _error_invalid_params)

    def test_disallowed_tool(self): # type: ignore

        registry = _MockToolRegistry(allowed_tools=set())
        handler = _make_handler(registry=registry)

        params = {'name': 'secret.internal-service'}
        request = _make_request('tools/call', params)
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.status_code, OK)
        self.assertEqual(mcp_response.body['error']['code'], _error_method_not_found)

    def test_service_exception_returns_is_error(self): # type: ignore

        registry = _MockToolRegistry(allowed_tools={'crm.get-customer'})
        handler = _make_handler(registry=registry, invoke_func=_invoke_raises)

        params = {'name': 'crm.get-customer', 'arguments': {}}
        request = _make_request('tools/call', params)
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.status_code, OK)

        result = mcp_response.body['result']
        self.assertTrue(result['isError'])
        self.assertEqual(result['content'][0]['text'], _test_service_error_message)

    def test_string_response_serialized(self): # type: ignore

        def invoke_string(service_name, payload): # type: ignore
            return 'plain text response'

        registry = _MockToolRegistry(allowed_tools={'test.service'})
        handler = _make_handler(registry=registry, invoke_func=invoke_string)

        params = {'name': 'test.service', 'arguments': {}}
        request = _make_request('tools/call', params)
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.body['result']['content'][0]['text'], 'plain text response')

    def test_dict_response_serialized_as_json(self): # type: ignore

        def invoke_dict(service_name, payload): # type: ignore
            return {'key': 'value'}

        registry = _MockToolRegistry(allowed_tools={'test.service'})
        handler = _make_handler(registry=registry, invoke_func=invoke_dict)

        params = {'name': 'test.service', 'arguments': {}}
        request = _make_request('tools/call', params)
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw)

        text = mcp_response.body['result']['content'][0]['text']
        self.assertIn('key', text)
        self.assertIn('value', text)

    def test_no_arguments_defaults_to_empty_dict(self): # type: ignore

        received_payloads = []

        def invoke_capture(service_name, payload): # type: ignore
            received_payloads.append(payload)
            return 'ok'

        registry = _MockToolRegistry(allowed_tools={'test.service'})
        handler = _make_handler(registry=registry, invoke_func=invoke_capture)

        params = {'name': 'test.service'}
        request = _make_request('tools/call', params)
        raw = dumps(request)

        handler.handle_raw_request(raw)

        self.assertEqual(received_payloads[0], {})

# ################################################################################################################################
# ################################################################################################################################

class HandlePing(TestCase):

    def test_ping_returns_empty_result(self): # type: ignore

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)

        request = _make_request('ping')
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.status_code, OK)
        self.assertEqual(mcp_response.body['result'], {})

# ################################################################################################################################
# ################################################################################################################################

class HandleParseError(TestCase):

    def test_malformed_json(self): # type: ignore

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)

        mcp_response = handler.handle_raw_request(b'not json at all')

        self.assertEqual(mcp_response.status_code, OK)
        self.assertEqual(mcp_response.body['error']['code'], _error_parse)

    def test_non_object_non_array(self): # type: ignore

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)

        mcp_response = handler.handle_raw_request(b'"just a string"')

        self.assertEqual(mcp_response.status_code, OK)
        self.assertEqual(mcp_response.body['error']['code'], _error_invalid_req)

# ################################################################################################################################
# ################################################################################################################################

class HandleInvalidRequest(TestCase):

    def test_missing_jsonrpc_field(self): # type: ignore

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)

        request = {'method': 'ping', 'id': 1}
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.status_code, OK)
        self.assertEqual(mcp_response.body['error']['code'], _error_invalid_req)

    def test_wrong_jsonrpc_version(self): # type: ignore

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)

        request = {'jsonrpc': '1.0', 'method': 'ping', 'id': 1}
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.status_code, OK)
        self.assertEqual(mcp_response.body['error']['code'], _error_invalid_req)

    def test_missing_method(self): # type: ignore

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)

        request = {'jsonrpc': '2.0', 'id': 1}
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.status_code, OK)
        self.assertEqual(mcp_response.body['error']['code'], _error_invalid_req)

    def test_unknown_method(self): # type: ignore

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)

        request = _make_request('nonexistent/method')
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.status_code, OK)
        self.assertEqual(mcp_response.body['error']['code'], _error_method_not_found)

# ################################################################################################################################
# ################################################################################################################################

class HandleBatch(TestCase):

    def test_batch_with_two_requests(self): # type: ignore

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)

        batch = [
            _make_request('ping', request_id=1),
            _make_request('ping', request_id=2),
        ]
        raw = dumps(batch)

        mcp_response = handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.status_code, OK)
        self.assertIsInstance(mcp_response.body, list)
        self.assertEqual(len(mcp_response.body), 2)
        self.assertEqual(mcp_response.body[0]['id'], 1)
        self.assertEqual(mcp_response.body[1]['id'], 2)

    def test_batch_notifications_produce_no_response(self): # type: ignore

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)

        batch = [
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
        ]
        raw = dumps(batch)

        mcp_response = handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.status_code, NO_CONTENT)
        self.assertIsNone(mcp_response.body)

    def test_batch_mixed_requests_and_notifications(self): # type: ignore

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)

        batch = [
            _make_request('initialize', request_id=1),
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
        ]
        raw = dumps(batch)

        mcp_response = handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.status_code, OK)
        self.assertIsInstance(mcp_response.body, list)
        self.assertEqual(len(mcp_response.body), 1)
        self.assertEqual(mcp_response.body[0]['id'], 1)

    def test_empty_batch_is_invalid(self): # type: ignore

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)

        raw = dumps([])

        mcp_response = handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.status_code, OK)
        self.assertEqual(mcp_response.body['error']['code'], _error_invalid_req)

    def test_batch_individual_errors_do_not_affect_others(self): # type: ignore

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)

        batch = [
            _make_request('ping', request_id=1),
            _make_request('nonexistent/method', request_id=2),
            _make_request('ping', request_id=3),
        ]
        raw = dumps(batch)

        mcp_response = handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.status_code, OK)
        self.assertEqual(len(mcp_response.body), 3)

        # First and third should succeed
        self.assertIn('result', mcp_response.body[0])
        self.assertIn('result', mcp_response.body[2])

        # Second should be an error
        self.assertIn('error', mcp_response.body[1])
        self.assertEqual(mcp_response.body[1]['error']['code'], _error_method_not_found)

# ################################################################################################################################
# ################################################################################################################################

class HandleInitializeBatch(TestCase):
    """ Tests the typical real-world batch: [initialize, notifications/initialized].
    """

    def test_initialize_plus_notification(self): # type: ignore

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)

        batch = [
            _make_request('initialize', request_id=1),
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
        ]
        raw = dumps(batch)

        mcp_response = handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.status_code, OK)
        self.assertIsInstance(mcp_response.body, list)
        self.assertEqual(len(mcp_response.body), 1)

        init_response = mcp_response.body[0]
        self.assertEqual(init_response['id'], 1)
        self.assertEqual(init_response['result']['protocolVersion'], _mcp_protocol_version)

# ################################################################################################################################
# ################################################################################################################################
