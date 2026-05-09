# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import NOT_FOUND, OK
from unittest import TestCase, main

# Hypothesis
from hypothesis import given, settings, assume
from hypothesis import strategies as st

# Zato
from zato.common.json_internal import dumps
from zato.server.connection.mcp.handler import MCPHandler, _error_invalid_req, _error_method_not_found, \
    _error_parse, _jsonrpc_version
from zato.server.connection.mcp.registry import ToolRegistry, _internal_prefix
from zato.server.connection.mcp.session import MCPSessionManager

# ################################################################################################################################
# ################################################################################################################################

class _MockToolRegistry:

    def __init__(self, tools=None, allowed_tools=None): # type: ignore
        self.tools = tools if tools is not None else []
        self.allowed_tools = allowed_tools if allowed_tools is not None else set()

    def get_tools(self): # type: ignore
        return self.tools

    def get_tools_page(self, cursor=None): # type: ignore
        return self.tools, None

    def is_tool_allowed(self, service_name): # type: ignore
        return service_name in self.allowed_tools

    def rebuild(self): # type: ignore
        pass

# ################################################################################################################################
# ################################################################################################################################

def _make_handler(allowed_tools=None): # type: ignore
    registry = _MockToolRegistry(allowed_tools=allowed_tools or set())
    session_manager = MCPSessionManager()
    invoke_func = lambda name, payload: {'echoed': payload}
    handler = MCPHandler(registry, invoke_func, session_manager)
    return handler

# ################################################################################################################################
# ################################################################################################################################

class JSONRPCEnvelopeFuzzing(TestCase):
    """ Hypothesis tests that fuzz the JSON-RPC envelope structure.
    The handler must never crash regardless of input shape.
    """

# ################################################################################################################################

    @given(st.binary())
    @settings(max_examples=200)
    def test_arbitrary_bytes_never_crash(self, raw_data):
        """ Any byte sequence must produce a valid MCPResponse, never an unhandled exception.
        """
        handler = _make_handler()
        response = handler.handle_raw_request(raw_data)

        self.assertIsNotNone(response)
        self.assertIsNotNone(response.status_code)

# ################################################################################################################################

    @given(st.text())
    @settings(max_examples=200)
    def test_arbitrary_text_never_crash(self, text):
        """ Any text string must produce a valid MCPResponse.
        """
        handler = _make_handler()
        response = handler.handle_raw_request(text.encode('utf8'))

        self.assertIsNotNone(response)
        self.assertIsNotNone(response.status_code)

# ################################################################################################################################

    @given(st.text())
    @settings(max_examples=200)
    def test_non_json_returns_error(self, text):
        """ Non-JSON or non-object/array JSON text must return an error, never a success result.
        """
        assume(not text.strip().startswith('{'))
        assume(not text.strip().startswith('['))

        handler = _make_handler()
        response = handler.handle_raw_request(text.encode('utf8'))

        self.assertEqual(response.status_code, OK)

        # Either parse error (-32700) or invalid request (-32600) is acceptable
        # because some scalars like '0' or 'true' parse as valid JSON but are not objects/arrays
        if response.body:
            error_code = response.body['error']['code']
            self.assertIn(error_code, (_error_parse, _error_invalid_req))

# ################################################################################################################################

    @given(st.dictionaries(
        keys=st.text(min_size=1, max_size=20),
        values=st.one_of(st.none(), st.booleans(), st.integers(), st.text(max_size=50)),
        max_size=10,
    ))
    @settings(max_examples=200)
    def test_arbitrary_json_object_never_crash(self, obj):
        """ Any JSON object must produce a response without crashing.
        """
        handler = _make_handler()
        raw = dumps(obj).encode('utf8')
        response = handler.handle_raw_request(raw)

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, OK)

# ################################################################################################################################

    @given(st.lists(
        st.dictionaries(
            keys=st.text(min_size=1, max_size=20),
            values=st.one_of(st.none(), st.booleans(), st.integers(), st.text(max_size=50)),
            max_size=5,
        ),
        max_size=5,
    ))
    @settings(max_examples=200)
    def test_arbitrary_json_array_never_crash(self, arr):
        """ Any JSON array (batch) must produce a response without crashing.
        """
        handler = _make_handler()
        raw = dumps(arr).encode('utf8')
        response = handler.handle_raw_request(raw)

        self.assertIsNotNone(response)

# ################################################################################################################################

    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=200)
    def test_unknown_method_returns_method_not_found(self, method):
        """ Any method name not in the known set must return -32601.
        """
        known_methods = {'initialize', 'tools/list', 'tools/call', 'ping'}
        assume(method not in known_methods)

        handler = _make_handler()
        msg = {'jsonrpc': _jsonrpc_version, 'method': method, 'id': 1}
        raw = dumps(msg).encode('utf8')
        response = handler.handle_raw_request(raw)

        self.assertEqual(response.status_code, OK)
        self.assertEqual(response.body['error']['code'], _error_method_not_found)

# ################################################################################################################################

    @given(st.one_of(st.none(), st.text(max_size=50), st.integers(), st.booleans()))
    @settings(max_examples=100)
    def test_wrong_jsonrpc_version_returns_invalid_request(self, version):
        """ Any jsonrpc value other than "2.0" must return -32600.
        """
        assume(version != '2.0')

        handler = _make_handler()
        msg = {'jsonrpc': version, 'method': 'ping', 'id': 1}
        raw = dumps(msg).encode('utf8')
        response = handler.handle_raw_request(raw)

        self.assertEqual(response.status_code, OK)
        self.assertEqual(response.body['error']['code'], _error_invalid_req)

# ################################################################################################################################
# ################################################################################################################################

class BatchFuzzing(TestCase):
    """ Hypothesis tests that fuzz batch (array) requests.
    """

# ################################################################################################################################

    @given(st.lists(
        st.fixed_dictionaries({
            'jsonrpc': st.just('2.0'),
            'method': st.sampled_from(['ping', 'tools/list', 'initialize']),
            'id': st.integers(min_value=1, max_value=10000),
        }),
        min_size=1,
        max_size=20,
    ))
    @settings(max_examples=100)
    def test_batch_of_valid_requests_returns_same_count(self, messages):
        """ A batch of N valid requests must return exactly N responses.
        """
        handler = _make_handler()
        raw = dumps(messages).encode('utf8')
        response = handler.handle_raw_request(raw)

        self.assertEqual(response.status_code, OK)
        self.assertIsInstance(response.body, list)
        self.assertEqual(len(response.body), len(messages))

# ################################################################################################################################

    @given(st.lists(
        st.fixed_dictionaries({
            'jsonrpc': st.just('2.0'),
            'method': st.sampled_from(['notifications/initialized', 'notifications/cancelled']),
        }),
        min_size=1,
        max_size=10,
    ))
    @settings(max_examples=50)
    def test_batch_of_only_notifications_returns_204(self, messages):
        """ A batch containing only notifications (no id) must return 204 No Content.
        """
        from http.client import NO_CONTENT

        handler = _make_handler()
        raw = dumps(messages).encode('utf8')
        response = handler.handle_raw_request(raw)

        self.assertEqual(response.status_code, NO_CONTENT)
        self.assertIsNone(response.body)

# ################################################################################################################################
# ################################################################################################################################

class AllowlistEnforcement(TestCase):
    """ Hypothesis tests that verify service allowlist is always enforced.
    """

# ################################################################################################################################

    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=200)
    def test_unlisted_service_always_rejected(self, service_name):
        """ Any service not in the allowlist must be rejected by tools/call.
        """
        handler = _make_handler(allowed_tools=set())

        msg = {
            'jsonrpc': _jsonrpc_version,
            'method': 'tools/call',
            'id': 1,
            'params': {'name': service_name},
        }
        raw = dumps(msg).encode('utf8')
        response = handler.handle_raw_request(raw)

        self.assertEqual(response.status_code, OK)
        self.assertEqual(response.body['error']['code'], _error_method_not_found)

# ################################################################################################################################

    @given(st.text(min_size=1, max_size=100).map(lambda s: 'zato.' + s))
    @settings(max_examples=100)
    def test_internal_service_always_rejected_by_registry(self, service_name):
        """ Any service starting with zato. must be rejected by is_tool_allowed,
        even if it were somehow in the allowlist.
        """
        store = _MockServiceStore({})
        registry = ToolRegistry(store, [service_name])
        registry.rebuild()

        self.assertFalse(registry.is_tool_allowed(service_name))

# ################################################################################################################################

    @given(st.text(min_size=1, max_size=100).filter(lambda s: not s.startswith('zato.')))
    @settings(max_examples=200)
    def test_non_internal_unlisted_service_rejected_by_registry(self, service_name):
        """ Any non-internal service not in the allowlist must be rejected.
        """
        store = _MockServiceStore({})
        registry = ToolRegistry(store, [])
        registry.rebuild()

        self.assertFalse(registry.is_tool_allowed(service_name))

# ################################################################################################################################

    @given(st.text(min_size=1, max_size=100).filter(lambda s: not s.startswith('zato.')))
    @settings(max_examples=200)
    def test_listed_non_internal_service_accepted_by_registry(self, service_name):
        """ A non-internal service in the allowlist must be accepted.
        """
        store = _MockServiceStore({})
        registry = ToolRegistry(store, [service_name])
        registry.rebuild()

        self.assertTrue(registry.is_tool_allowed(service_name))

# ################################################################################################################################
# ################################################################################################################################

class SchemaExtractionProperties(TestCase):
    """ Hypothesis tests for schema extraction invariants.
    """

# ################################################################################################################################

    @given(st.lists(st.text(min_size=1, max_size=50).filter(lambda s: not s.startswith('zato.')), min_size=0, max_size=20, unique=True))
    @settings(max_examples=100)
    def test_rebuild_produces_at_most_allowlist_count(self, service_names):
        """ The number of tools after rebuild is at most the number of allowed services.
        """
        service_dict = {}
        for name in service_names:
            service_dict[name] = _MockServiceClass(name)

        store = _MockServiceStore(service_dict)
        registry = ToolRegistry(store, service_names)
        registry.rebuild()

        tools = registry.get_tools()
        self.assertLessEqual(len(tools), len(service_names))

# ################################################################################################################################

    @given(st.lists(st.text(min_size=1, max_size=50).filter(lambda s: not s.startswith('zato.')), min_size=1, max_size=20, unique=True))
    @settings(max_examples=100)
    def test_all_tools_have_required_fields(self, service_names):
        """ Every tool in the list must have name, description, and inputSchema.
        """
        service_dict = {}
        for name in service_names:
            service_dict[name] = _MockServiceClass(name)

        store = _MockServiceStore(service_dict)
        registry = ToolRegistry(store, service_names)
        registry.rebuild()

        for tool in registry.get_tools():
            self.assertIn('name', tool)
            self.assertIn('description', tool)
            self.assertIn('inputSchema', tool)

# ################################################################################################################################

    @given(st.lists(st.text(min_size=1, max_size=50).filter(lambda s: not s.startswith('zato.')), min_size=1, max_size=20, unique=True))
    @settings(max_examples=100)
    def test_tool_names_match_service_names(self, service_names):
        """ Every tool name must be one of the allowed service names.
        """
        service_dict = {}
        for name in service_names:
            service_dict[name] = _MockServiceClass(name)

        store = _MockServiceStore(service_dict)
        registry = ToolRegistry(store, service_names)
        registry.rebuild()

        tool_names = {tool['name'] for tool in registry.get_tools()}
        self.assertTrue(tool_names.issubset(set(service_names)))

# ################################################################################################################################

    @given(st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=20, unique=True))
    @settings(max_examples=100)
    def test_no_internal_services_in_tools(self, service_names):
        """ No tool returned by the registry must start with the internal prefix.
        """
        service_dict = {}
        for name in service_names:
            service_dict[name] = _MockServiceClass(name)

        store = _MockServiceStore(service_dict)
        registry = ToolRegistry(store, service_names)
        registry.rebuild()

        for tool in registry.get_tools():
            self.assertFalse(tool['name'].startswith(_internal_prefix))

# ################################################################################################################################
# ################################################################################################################################

class SessionFuzzing(TestCase):
    """ Hypothesis tests for session ID validation.
    """

# ################################################################################################################################

    @given(st.text(min_size=1, max_size=200))
    @settings(max_examples=200)
    def test_random_session_id_rejected(self, session_id):
        """ A random string as session ID must be rejected.
        """
        handler = _make_handler()
        msg = {'jsonrpc': _jsonrpc_version, 'method': 'ping', 'id': 1}
        raw = dumps(msg).encode('utf8')

        response = handler.handle_raw_request(raw, session_id=session_id)

        self.assertEqual(response.status_code, NOT_FOUND)

# ################################################################################################################################

    @given(st.text(min_size=1, max_size=200))
    @settings(max_examples=100)
    def test_random_session_id_delete_rejected(self, session_id):
        """ Deleting a random session ID must return not found.
        """
        handler = _make_handler()
        response = handler.handle_delete_session(session_id)

        self.assertEqual(response.status_code, NOT_FOUND)

# ################################################################################################################################
# ################################################################################################################################
# Mock helpers for ToolRegistry tests
# ################################################################################################################################
# ################################################################################################################################

class _MockServiceClass:
    """ A minimal mock of a Zato service class for schema extraction.
    """
    def __init__(self, name):
        self.__doc__ = 'Mock service: ' + name
        self._io = None

class _MockServiceStore:
    """ A minimal mock of ServiceStore with name_to_impl_name and services dicts.
    """
    def __init__(self, services_by_name):
        self.name_to_impl_name = {}
        self.services = {}

        for name, service_class in services_by_name.items():
            impl_name = 'impl.' + name
            self.name_to_impl_name[name] = impl_name
            self.services[impl_name] = {'service_class': service_class}

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()
