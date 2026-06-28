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
from zato.server.connection.mcp.handler import MCPHandler, _error_invalid_params, _error_invalid_request, \
    _error_method_not_found, _error_parse, _jsonrpc_version, _mcp_protocol_version, _server_name, _server_version
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

def _make_handler(registry:'any_'=None, invoke_func:'callable_'=None) -> 'MCPHandler':
    """ Creates an MCPHandler with defaults for tests.
    """

    if registry is None:
        registry = _MockToolRegistry()

    if invoke_func is None:
        invoke_func = _invoke_success

    session_manager = MCPSessionManager()

    out = MCPHandler(registry, invoke_func, session_manager) # pyright: ignore[reportArgumentType]
    return out

# ################################################################################################################################
# ################################################################################################################################

def _make_session(handler:'MCPHandler') -> 'str':
    """ Creates a valid session on the handler's manager and returns its ID.
    Every method other than initialize requires one.
    """

    out = handler.session_manager.create(_mcp_protocol_version)
    return out

# ################################################################################################################################
# ################################################################################################################################

class HandleInitialize(TestCase):

    def test_initialize_returns_capabilities(self) -> 'None':
        """ Verifies that initialize returns protocol version, capabilities and server info.
        """

        handler = _make_handler()

        request = _make_request('initialize')
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        self.assertEqual(body['jsonrpc'], _jsonrpc_version)
        self.assertEqual(body['id'], 1)

        result = body['result']
        self.assertEqual(result['protocolVersion'], _mcp_protocol_version)

        capabilities = result['capabilities']
        tools_capability = capabilities['tools']
        list_changed = tools_capability['listChanged']
        self.assertTrue(list_changed)

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

        mcp_response = handler.handle_raw_request(raw, session_id=session_id)

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

        mcp_response = handler.handle_raw_request(raw, session_id=session_id)

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
        mcp_response = handler.handle_raw_request(raw, session_id=session_id)

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
        mcp_response = handler.handle_raw_request(raw, session_id=session_id)

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
        _ = handler.handle_raw_request(raw, session_id=session_id)

        self.assertEqual(captured_cursors, ['42'])

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

        mcp_response = handler.handle_raw_request(raw, session_id=session_id)

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

        mcp_response = handler.handle_raw_request(raw, session_id=session_id)

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

        mcp_response = handler.handle_raw_request(raw, session_id=session_id)

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

        mcp_response = handler.handle_raw_request(raw, session_id=session_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        result = body['result']
        self.assertTrue(result['isError'])

        content = result['content']
        first_content = content[0]
        text = first_content['text']
        self.assertEqual(text, _test_service_error_message)

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

        mcp_response = handler.handle_raw_request(raw, session_id=session_id)

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

        mcp_response = handler.handle_raw_request(raw, session_id=session_id)

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

        _ = handler.handle_raw_request(raw, session_id=session_id)

        first_payload = received_payloads[0]
        self.assertEqual(first_payload, {})

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

        mcp_response = handler.handle_raw_request(raw, session_id=session_id)

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

        mcp_response = handler.handle_raw_request(b'not json at all')

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        error = body['error']
        self.assertEqual(error['code'], _error_parse)

    def test_non_object_non_array(self) -> 'None':
        """ Verifies that a non-object non-array JSON value produces an invalid request error.
        """

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)

        mcp_response = handler.handle_raw_request(b'"just a string"')

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

        mcp_response = handler.handle_raw_request(raw, session_id=session_id)

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

        mcp_response = handler.handle_raw_request(raw, session_id=session_id)

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

        mcp_response = handler.handle_raw_request(raw, session_id=session_id)

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

        mcp_response = handler.handle_raw_request(raw, session_id=session_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        error = body['error']
        self.assertEqual(error['code'], _error_method_not_found)

# ################################################################################################################################
# ################################################################################################################################

class HandleBatch(TestCase):

    def test_batch_with_two_requests(self) -> 'None':
        """ Verifies that a batch of two requests returns two responses.
        """

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)

        batch = [
            _make_request('ping', request_id=1),
            _make_request('ping', request_id=2),
        ]
        raw = dumps(batch)

        session_id = _make_session(handler)
        mcp_response = handler.handle_raw_request(raw, session_id=session_id)

        self.assertEqual(mcp_response.status_code, OK)
        self.assertIsInstance(mcp_response.body, list)
        self.assertEqual(len(mcp_response.body), 2)

        first_response = mcp_response.body[0]
        second_response = mcp_response.body[1]
        self.assertEqual(first_response['id'], 1)
        self.assertEqual(second_response['id'], 2)

    def test_batch_notifications_produce_no_response(self) -> 'None':
        """ Verifies that a batch of only notifications returns 204 No Content.
        """

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)

        batch = [
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
        ]
        raw = dumps(batch)

        mcp_response = handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.status_code, NO_CONTENT)
        self.assertIsNone(mcp_response.body)

    def test_batch_mixed_requests_and_notifications(self) -> 'None':
        """ Verifies that a batch with mixed requests and notifications returns only request responses.
        """

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

        first_response = mcp_response.body[0]
        self.assertEqual(first_response['id'], 1)

    def test_empty_batch_is_invalid(self) -> 'None':
        """ Verifies that an empty batch returns an invalid request error.
        """

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)

        raw = dumps([])

        mcp_response = handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        error = body['error']
        self.assertEqual(error['code'], _error_invalid_request)

    def test_batch_individual_errors_do_not_affect_others(self) -> 'None':
        """ Verifies that individual errors in a batch do not affect other requests.
        """

        registry = _MockToolRegistry()
        handler = _make_handler(registry=registry)

        batch = [
            _make_request('ping', request_id=1),
            _make_request('nonexistent/method', request_id=2),
            _make_request('ping', request_id=3),
        ]
        raw = dumps(batch)

        session_id = _make_session(handler)
        mcp_response = handler.handle_raw_request(raw, session_id=session_id)

        self.assertEqual(mcp_response.status_code, OK)
        self.assertEqual(len(mcp_response.body), 3)

        # First and third should succeed
        first_response = mcp_response.body[0]
        third_response = mcp_response.body[2]
        self.assertIn('result', first_response)
        self.assertIn('result', third_response)

        # Second should be an error
        second_response = mcp_response.body[1]
        self.assertIn('error', second_response)

        error = second_response['error']
        self.assertEqual(error['code'], _error_method_not_found)

# ################################################################################################################################
# ################################################################################################################################

class HandleInitializeBatch(TestCase):
    """ Tests the typical real-world batch: [initialize, notifications/initialized].
    """

    def test_initialize_plus_notification(self) -> 'None':
        """ Verifies that a batch with initialize and notification returns one response.
        """

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

        initialize_response = mcp_response.body[0]
        self.assertEqual(initialize_response['id'], 1)

        result = initialize_response['result']
        self.assertEqual(result['protocolVersion'], _mcp_protocol_version)

# ################################################################################################################################
# ################################################################################################################################
