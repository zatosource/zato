# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import NO_CONTENT, OK
from unittest import TestCase

# Zato
from zato.common.json_internal import dumps, loads
from zato.common.test import _test_sec_def_id
from zato.server.connection.mcp.handler import _mcp_protocol_version, MCPHandler
from zato.server.generic.api.channel_mcp import ChannelMCPWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################

class _MockServiceStore:
    """ Mock service store for ToolRegistry.
    """
    def __init__(self) -> 'None':
        self.services = {}
        self.name_to_impl_name = {}

    def add_service(self, name:'str') -> 'None':
        impl_name = 'impl.' + name
        self.name_to_impl_name[name] = impl_name
        self.services[impl_name] = {'service_class': type(name, (), {'__doc__': name, '_io': None})}

# ################################################################################################################################
# ################################################################################################################################

class _MockServer:
    """ Mock server with service_store and invoke method.
    """
    def __init__(self) -> 'None':
        self.service_store = _MockServiceStore()
        self._invoke_responses = {}

    def invoke(self, service_name:'str', payload:'anydict') -> 'anydict':
        return self._invoke_responses[service_name]

# ################################################################################################################################
# ################################################################################################################################

class _MockBunch(dict):
    """ Dict-like object that also supports attribute access.
    """
    def __getattr__(self, name:'str') -> 'str':
        return self[name]

# ################################################################################################################################
# ################################################################################################################################

class ChannelMCPWrapperBuild(TestCase):

    def test_build_wrapper_creates_handler(self) -> 'None':
        """ Verifies that build_wrapper creates an MCPHandler instance.
        """

        server = _MockServer()
        server.service_store.add_service('crm.get-customer')

        config = _MockBunch({
            'name': 'test-mcp-channel',
            'services': ['crm.get-customer'],
        })

        wrapper = ChannelMCPWrapper(config, server) # pyright: ignore[reportArgumentType]
        wrapper.build_wrapper()

        self.assertIsNotNone(wrapper.handler)
        self.assertIsInstance(wrapper.handler, MCPHandler)

    def test_build_wrapper_no_opaque(self) -> 'None':
        """ Verifies that build_wrapper works without an opaque services key.
        """

        server = _MockServer()

        config = _MockBunch({
            'name': 'empty-channel',
        })

        wrapper = ChannelMCPWrapper(config, server) # pyright: ignore[reportArgumentType]
        wrapper.build_wrapper()

        self.assertIsNotNone(wrapper.handler)

    def test_build_wrapper_empty_services(self) -> 'None':
        """ Verifies that build_wrapper with empty services produces no tools.
        """

        server = _MockServer()

        config = _MockBunch({
            'name': 'empty-services-channel',
            'services': [],
        })

        wrapper = ChannelMCPWrapper(config, server) # pyright: ignore[reportArgumentType]
        wrapper.build_wrapper()

        self.assertIsNotNone(wrapper.handler)
        assert wrapper.handler is not None

        tools = wrapper.handler.tool_registry.get_tools()
        self.assertEqual(len(tools), 0)

    def test_delete_clears_handler(self) -> 'None':
        """ Verifies that delete sets handler to None.
        """

        server = _MockServer()

        config = _MockBunch({
            'name': 'delete-channel',
            'services': [],
        })

        wrapper = ChannelMCPWrapper(config, server) # pyright: ignore[reportArgumentType]
        wrapper.build_wrapper()

        self.assertIsNotNone(wrapper.handler)

        wrapper.delete()

        self.assertIsNone(wrapper.handler)

# ################################################################################################################################
# ################################################################################################################################

class ChannelMCPWrapperInvoke(TestCase):

    def test_invoke_service_through_wrapper(self) -> 'None':
        """ Verifies that a service can be invoked through the wrapper handler.
        """

        server = _MockServer()
        server.service_store.add_service('crm.get-customer')
        server._invoke_responses['crm.get-customer'] = {'name': 'Test Customer'}

        config = _MockBunch({
            'name': 'invoke-channel',
            'services': ['crm.get-customer'],
        })

        wrapper = ChannelMCPWrapper(config, server) # pyright: ignore[reportArgumentType]
        wrapper.build_wrapper()

        assert wrapper.handler is not None

        # Build a tools/call request
        request = {
            'jsonrpc': '2.0',
            'method': 'tools/call',
            'id': 1,
            'params': {
                'name': 'crm.get-customer',
                'arguments': {'customer_id': '123'},
            },
        }
        raw = dumps(request)

        assert wrapper.handler is not None
        session_manager = wrapper.handler.session_manager
        session_id = session_manager.create(_mcp_protocol_version, _test_sec_def_id)
        mcp_response = wrapper.handler.handle_raw_request(raw, session_id=session_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        result = body['result']
        self.assertNotIn('isError', result)

        # The response text should contain the serialized service response
        content = result['content']
        first_content = content[0]
        text = first_content['text']
        parsed_response = loads(text)
        self.assertEqual(parsed_response['name'], 'Test Customer')

# ################################################################################################################################
# ################################################################################################################################

class MCPEndpointServiceDispatch(TestCase):
    """ Tests the MCPEndpoint service's dispatch logic without a running server.
    We simulate the service's handle() method by creating the same objects it uses.
    """

    def test_dispatch_ping(self) -> 'None':
        """ Verifies that a ping request dispatches correctly.
        """

        server = _MockServer()

        config = _MockBunch({
            'name': 'test-channel',
            'services': [],
        })

        wrapper = ChannelMCPWrapper(config, server) # pyright: ignore[reportArgumentType]
        wrapper.build_wrapper()

        request = {
            'jsonrpc': '2.0',
            'method': 'ping',
            'id': 1,
        }
        raw = dumps(request)

        assert wrapper.handler is not None
        session_manager = wrapper.handler.session_manager
        session_id = session_manager.create(_mcp_protocol_version, _test_sec_def_id)
        mcp_response = wrapper.handler.handle_raw_request(raw, session_id=session_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        result = body['result']
        self.assertEqual(result, {})

    def test_dispatch_batch_all_notifications_returns_204(self) -> 'None':
        """ Verifies that a batch of only notifications returns 204.
        """

        server = _MockServer()

        config = _MockBunch({
            'name': 'test-channel',
            'services': [],
        })

        wrapper = ChannelMCPWrapper(config, server) # pyright: ignore[reportArgumentType]
        wrapper.build_wrapper()

        batch = [
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
        ]
        raw = dumps(batch)

        assert wrapper.handler is not None
        mcp_response = wrapper.handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.status_code, NO_CONTENT)
        self.assertIsNone(mcp_response.body)

# ################################################################################################################################
# ################################################################################################################################
