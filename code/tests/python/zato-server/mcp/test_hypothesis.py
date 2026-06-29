# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import BAD_REQUEST, NO_CONTENT, NOT_FOUND, OK
from unittest import TestCase

# Hypothesis
from hypothesis import given, settings, assume
from hypothesis import strategies as st

# Zato
from zato.common.json_internal import dumps
from zato.server.connection.mcp.handler import MCPHandler, _error_invalid_request, _error_method_not_found, \
    _error_parse, _jsonrpc_version, _mcp_protocol_version
from zato.server.connection.mcp.registry import ToolRegistry, _internal_prefix
from zato.server.connection.mcp.session import MCPSessionManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

def _filter_non_internal(service_name:'str') -> 'bool':
    """ Returns True if the service name does not start with the internal prefix.
    """
    return not service_name.startswith('zato.')

# ################################################################################################################################

def _prepend_zato_prefix(service_name:'str') -> 'str':
    """ Prepends the zato. prefix to a service name for test generation.
    """
    return 'zato.' + service_name

# ################################################################################################################################
# ################################################################################################################################

class _MockToolRegistry:

    def __init__(self, tools:'any_' = None, allowed_tools:'any_' = None) -> 'None':
        self.tools = tools if tools is not None else []
        self.allowed_tools = allowed_tools if allowed_tools is not None else set()

    def get_tools(self) -> 'any_':
        return self.tools

    def get_tools_page(self, cursor:'any_' = None) -> 'any_':
        return self.tools, None

    def is_tool_allowed(self, service_name:'str') -> 'bool':
        return service_name in self.allowed_tools

    def rebuild(self) -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

def _make_handler(allowed_tools:'any_' = None) -> 'any_':

    if allowed_tools is None:
        allowed_tools = set()

    registry = _MockToolRegistry(allowed_tools=allowed_tools)
    session_manager = MCPSessionManager()

    def invoke_func(name:'str', payload:'any_') -> 'anydict':
        return {'echoed': payload}

    handler = MCPHandler(registry, invoke_func, session_manager) # pyright: ignore[reportArgumentType]
    return handler

# ################################################################################################################################
# ################################################################################################################################

def _make_session(handler:'any_') -> 'str':
    """ Creates a valid session on the handler's manager and returns its ID.
    Every method other than initialize requires one.
    """

    out = handler.session_manager.create(_mcp_protocol_version)
    return out

# ################################################################################################################################
# ################################################################################################################################

class JSONRPCEnvelopeFuzzing(TestCase):
    """ Hypothesis tests that fuzz the JSON-RPC envelope structure.
    The handler must never crash regardless of input shape.
    """

# ################################################################################################################################

    @given(st.binary())
    @settings(max_examples=200)
    def test_arbitrary_bytes_never_crash(self, raw_data:'bytes') -> 'None':
        """ Any byte sequence must produce a valid MCPResponse, never an unhandled exception.
        """
        """ Any byte sequence must produce a valid MCPResponse, never an unhandled exception.
        """

        handler = _make_handler()
        response = handler.handle_raw_request(raw_data)

        self.assertIsNotNone(response)
        self.assertIsNotNone(response.status_code)

# ################################################################################################################################

    @given(st.text())
    @settings(max_examples=200)
    def test_arbitrary_text_never_crash(self, text:'str') -> 'None':
        """ Any text string must produce a valid MCPResponse.
        """

        handler = _make_handler()
        encoded_text = text.encode('utf8')
        response = handler.handle_raw_request(encoded_text)

        self.assertIsNotNone(response)
        self.assertIsNotNone(response.status_code)

# ################################################################################################################################

    @given(st.text())
    @settings(max_examples=200)
    def test_non_json_returns_error(self, text:'str') -> 'None':
        """ Non-JSON or non-object/array JSON text must return an error, never a success result.
        """

        stripped = text.strip()
        _ = assume(not stripped.startswith('{'))
        _ = assume(not stripped.startswith('['))

        handler = _make_handler()
        encoded_text = text.encode('utf8')
        response = handler.handle_raw_request(encoded_text)

        self.assertEqual(response.status_code, OK)

        # Either parse error (-32700) or invalid request (-32600) is acceptable
        # because some scalars like '0' or 'true' parse as valid JSON but are not objects/arrays
        if response.body:
            body = response.body
            error = body['error']
            error_code = error['code']
            self.assertIn(error_code, (_error_parse, _error_invalid_request))

# ################################################################################################################################

    @given(st.dictionaries(
        keys=st.text(min_size=1, max_size=20),
        values=st.one_of(st.none(), st.booleans(), st.integers(), st.text(max_size=50)),
        max_size=10,
    ))
    @settings(max_examples=200)
    def test_arbitrary_json_object_never_crash(self, obj:'anydict') -> 'None':
        """ Any JSON object must produce a response without crashing.
        """

        handler = _make_handler()
        session_id = _make_session(handler)
        serialized = dumps(obj)
        raw = serialized.encode('utf8')
        response = handler.handle_raw_request(raw, session_id=session_id)

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
    def test_arbitrary_json_array_never_crash(self, arr:'anylist') -> 'None':
        """ Any JSON array (batch) must produce a response without crashing.
        """

        handler = _make_handler()
        serialized = dumps(arr)
        raw = serialized.encode('utf8')
        response = handler.handle_raw_request(raw)

        self.assertIsNotNone(response)

# ################################################################################################################################

    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=200)
    def test_unknown_method_returns_method_not_found(self, method:'str') -> 'None':
        """ Any method name not in the known set must return -32601.
        """

        known_methods = {'initialize', 'tools/list', 'tools/call', 'ping'}
        _ = assume(method not in known_methods)

        handler = _make_handler()
        session_id = _make_session(handler)
        msg = {'jsonrpc': _jsonrpc_version, 'method': method, 'id': 1}
        serialized = dumps(msg)
        raw = serialized.encode('utf8')
        response = handler.handle_raw_request(raw, session_id=session_id)

        self.assertEqual(response.status_code, OK)

        body = response.body
        error = body['error']
        self.assertEqual(error['code'], _error_method_not_found)

# ################################################################################################################################

    @given(st.one_of(st.none(), st.text(max_size=50), st.integers(), st.booleans()))
    @settings(max_examples=100)
    def test_wrong_jsonrpc_version_returns_invalid_request(self, version:'any_') -> 'None':
        """ Any jsonrpc value other than "2.0" must return -32600.
        """

        _ = assume(version != '2.0')

        handler = _make_handler()
        session_id = _make_session(handler)
        msg = {'jsonrpc': version, 'method': 'ping', 'id': 1}
        serialized = dumps(msg)
        raw = serialized.encode('utf8')
        response = handler.handle_raw_request(raw, session_id=session_id)

        self.assertEqual(response.status_code, OK)

        body = response.body
        error = body['error']
        self.assertEqual(error['code'], _error_invalid_request)

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
    def test_batch_of_valid_requests_returns_same_count(self, messages:'anylist') -> 'None':
        """ A batch of N valid requests must return exactly N responses.
        """

        handler = _make_handler()
        serialized = dumps(messages)
        raw = serialized.encode('utf8')
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
    def test_batch_of_only_notifications_returns_204(self, messages:'anylist') -> 'None':
        """ A batch containing only notifications (no id) must return 204 No Content.
        """

        handler = _make_handler()
        serialized = dumps(messages)
        raw = serialized.encode('utf8')
        response = handler.handle_raw_request(raw)

        self.assertEqual(response.status_code, NO_CONTENT)
        self.assertIsNone(response.body)

# ################################################################################################################################
# ################################################################################################################################

class AllowlistEnforcement(TestCase):
    """ Hypothesis tests that verify service allow list is always enforced.
    """

# ################################################################################################################################

    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=200)
    def test_unlisted_service_always_rejected(self, service_name:'str') -> 'None':
        """ Any service not in the allow list must be rejected by tools/call.
        """

        handler = _make_handler(allowed_tools=set())
        session_id = _make_session(handler)

        msg = {
            'jsonrpc': _jsonrpc_version,
            'method': 'tools/call',
            'id': 1,
            'params': {'name': service_name},
        }
        serialized = dumps(msg)
        raw = serialized.encode('utf8')
        response = handler.handle_raw_request(raw, session_id=session_id)

        self.assertEqual(response.status_code, OK)

        body = response.body
        error = body['error']
        self.assertEqual(error['code'], _error_method_not_found)

# ################################################################################################################################

    @given(st.text(min_size=1, max_size=100).map(_prepend_zato_prefix))
    @settings(max_examples=100)
    def test_internal_service_always_rejected_by_registry(self, service_name:'str') -> 'None':
        """ Any service starting with zato. must be rejected by is_tool_allowed,
        even if it were somehow in the allow list.
        """

        store = _MockServiceStore({})
        registry = ToolRegistry(store, [service_name]) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        is_allowed = registry.is_tool_allowed(service_name)
        self.assertFalse(is_allowed)

# ################################################################################################################################

    @given(st.text(min_size=1, max_size=100).filter(_filter_non_internal))
    @settings(max_examples=200)
    def test_non_internal_unlisted_service_rejected_by_registry(self, service_name:'str') -> 'None':
        """ Any non-internal service not in the allow list must be rejected.
        """

        store = _MockServiceStore({})
        registry = ToolRegistry(store, []) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        is_allowed = registry.is_tool_allowed(service_name)
        self.assertFalse(is_allowed)

# ################################################################################################################################

    @given(st.text(min_size=1, max_size=100).filter(_filter_non_internal))
    @settings(max_examples=200)
    def test_listed_non_internal_service_accepted_by_registry(self, service_name:'str') -> 'None':
        """ A non-internal service in the allow list must be accepted.
        """

        store = _MockServiceStore({service_name: _MockServiceClass(service_name)})
        registry = ToolRegistry(store, [service_name]) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        is_allowed = registry.is_tool_allowed(service_name)
        self.assertTrue(is_allowed)

# ################################################################################################################################
# ################################################################################################################################

class SchemaExtractionProperties(TestCase):
    """ Hypothesis tests for schema extraction invariants.
    """

# ################################################################################################################################

    @given(st.lists(st.text(min_size=1, max_size=50).filter(_filter_non_internal), min_size=0, max_size=20, unique=True))
    @settings(max_examples=100)
    def test_rebuild_produces_at_most_allow_list_count(self, service_names:'strlist') -> 'None':
        """ The number of tools after rebuild is at most the number of allowed services.
        """

        service_dict = {}
        for name in service_names:
            service_dict[name] = _MockServiceClass(name)

        store = _MockServiceStore(service_dict)
        registry = ToolRegistry(store, service_names) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        tools = registry.get_tools()
        self.assertLessEqual(len(tools), len(service_names))

# ################################################################################################################################

    @given(st.lists(st.text(min_size=1, max_size=50).filter(_filter_non_internal), min_size=1, max_size=20, unique=True))
    @settings(max_examples=100)
    def test_all_tools_have_required_fields(self, service_names:'strlist') -> 'None':
        """ Every tool in the list must have name, description, and inputSchema.
        """

        service_dict = {}
        for name in service_names:
            service_dict[name] = _MockServiceClass(name)

        store = _MockServiceStore(service_dict)
        registry = ToolRegistry(store, service_names) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        for tool in registry.get_tools():
            self.assertIn('name', tool)
            self.assertIn('description', tool)
            self.assertIn('inputSchema', tool)

# ################################################################################################################################

    @given(st.lists(st.text(min_size=1, max_size=50).filter(_filter_non_internal), min_size=1, max_size=20, unique=True))
    @settings(max_examples=100)
    def test_tool_names_match_service_names(self, service_names:'strlist') -> 'None':
        """ Every tool name must be one of the allowed service names.
        """

        service_dict = {}
        for name in service_names:
            service_dict[name] = _MockServiceClass(name)

        store = _MockServiceStore(service_dict)
        registry = ToolRegistry(store, service_names) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        tool_names = set()
        for tool in registry.get_tools():
            tool_names.add(tool['name'])

        service_name_set = set(service_names)
        is_subset = tool_names.issubset(service_name_set)
        self.assertTrue(is_subset)

# ################################################################################################################################

    @given(st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=20, unique=True))
    @settings(max_examples=100)
    def test_no_internal_services_in_tools(self, service_names:'strlist') -> 'None':
        """ No tool returned by the registry must start with the internal prefix.
        """

        service_dict = {}
        for name in service_names:
            service_dict[name] = _MockServiceClass(name)

        store = _MockServiceStore(service_dict)
        registry = ToolRegistry(store, service_names) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        for tool in registry.get_tools():
            tool_name = tool['name']
            starts_with_internal = tool_name.startswith(_internal_prefix)
            self.assertFalse(starts_with_internal)

# ################################################################################################################################
# ################################################################################################################################

class SessionFuzzing(TestCase):
    """ Hypothesis tests for session ID validation.
    """

# ################################################################################################################################

    @given(st.text(min_size=1, max_size=200))
    @settings(max_examples=200)
    def test_random_session_id_rejected(self, session_id:'str') -> 'None':
        """ A random string as session ID must be rejected.
        """

        handler = _make_handler()
        msg = {'jsonrpc': _jsonrpc_version, 'method': 'ping', 'id': 1}
        serialized = dumps(msg)
        raw = serialized.encode('utf8')

        response = handler.handle_raw_request(raw, session_id=session_id)

        self.assertEqual(response.status_code, BAD_REQUEST)

# ################################################################################################################################

    @given(st.text(min_size=1, max_size=200))
    @settings(max_examples=100)
    def test_random_session_id_delete_rejected(self, session_id:'str') -> 'None':
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
    def __init__(self, name:'str') -> 'None':
        self.__doc__ = 'Mock service: ' + name
        self._io = None

class _MockServiceStore:
    """ A minimal mock of ServiceStore with name_to_impl_name and services dicts.
    """
    def __init__(self, services_by_name:'anydict') -> 'None':
        self.name_to_impl_name = {}
        self.services = {}

        for name, service_class in services_by_name.items():
            impl_name = 'impl.' + name
            self.name_to_impl_name[name] = impl_name
            self.services[impl_name] = {'service_class': service_class}

# ################################################################################################################################
# ################################################################################################################################
