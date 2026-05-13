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
from zato.server.connection.mcp.handler import MCPHandler
from zato.server.generic.api.channel_mcp import ChannelMCPWrapper

# ################################################################################################################################
# ################################################################################################################################

class _MockServiceStore:
    """ Mock service store for ToolRegistry.
    """
    def __init__(self): # type: ignore
        self.services = {}
        self.name_to_impl_name = {}

# ################################################################################################################################
# ################################################################################################################################

class _MockServer:
    """ Mock server with service_store and invoke method.
    """
    def __init__(self): # type: ignore
        self.service_store = _MockServiceStore()
        self._invoke_responses = {}

    def invoke(self, service_name, payload): # type: ignore
        return self._invoke_responses.get(service_name, {'status': 'ok'})

# ################################################################################################################################
# ################################################################################################################################

class _MockBunch(dict):
    """ Dict-like object that also supports attribute access.
    """
    def __getattr__(self, name): # type: ignore
        return self[name]

# ################################################################################################################################
# ################################################################################################################################

class _MockChannel:
    """ Mock channel info object.
    """
    def __init__(self, name): # type: ignore
        self.name = name

# ################################################################################################################################
# ################################################################################################################################

class _MockRequest:
    """ Mock request object with raw_request.
    """
    def __init__(self, raw_request): # type: ignore
        self.raw_request = raw_request

# ################################################################################################################################
# ################################################################################################################################

class _MockResponse:
    """ Mock response object.
    """
    def __init__(self): # type: ignore
        self.payload = ''
        self.status_code = OK
        self.data_format = ''
        self.headers = {}

# ################################################################################################################################
# ################################################################################################################################

class ChannelMCPWrapperBuild(TestCase):

    def test_build_wrapper_creates_handler(self): # type: ignore

        server = _MockServer()

        config = _MockBunch({
            'name': 'test-mcp-channel',
            'services': ['crm.get-customer'],
        })

        wrapper = ChannelMCPWrapper(config, server)
        wrapper.build_wrapper()

        self.assertIsNotNone(wrapper.handler)
        self.assertIsInstance(wrapper.handler, MCPHandler)

    def test_build_wrapper_no_opaque(self): # type: ignore

        server = _MockServer()

        config = _MockBunch({
            'name': 'empty-channel',
        })

        wrapper = ChannelMCPWrapper(config, server)
        wrapper.build_wrapper()

        self.assertIsNotNone(wrapper.handler)

    def test_build_wrapper_empty_services(self): # type: ignore

        server = _MockServer()

        config = _MockBunch({
            'name': 'empty-services-channel',
            'services': [],
        })

        wrapper = ChannelMCPWrapper(config, server)
        wrapper.build_wrapper()

        self.assertIsNotNone(wrapper.handler)

        tools = wrapper.handler.tool_registry.get_tools()
        self.assertEqual(len(tools), 0)

    def test_delete_clears_handler(self): # type: ignore

        server = _MockServer()

        config = _MockBunch({
            'name': 'delete-channel',
            'services': [],
        })

        wrapper = ChannelMCPWrapper(config, server)
        wrapper.build_wrapper()

        self.assertIsNotNone(wrapper.handler)

        wrapper.delete()

        self.assertIsNone(wrapper.handler)

# ################################################################################################################################
# ################################################################################################################################

class ChannelMCPWrapperInvoke(TestCase):

    def test_invoke_service_through_wrapper(self): # type: ignore

        server = _MockServer()
        server._invoke_responses['crm.get-customer'] = {'name': 'Test Customer'}

        config = _MockBunch({
            'name': 'invoke-channel',
            'services': ['crm.get-customer'],
        })

        wrapper = ChannelMCPWrapper(config, server)
        wrapper.build_wrapper()

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

        mcp_response = wrapper.handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.status_code, OK)

        result = mcp_response.body['result']
        self.assertNotIn('isError', result)

        # The response text should contain the serialized service response
        text = result['content'][0]['text']
        parsed_response = loads(text)
        self.assertEqual(parsed_response['name'], 'Test Customer')

# ################################################################################################################################
# ################################################################################################################################

class MCPEndpointServiceDispatch(TestCase):
    """ Tests the MCPEndpoint service's dispatch logic without a running server.
    We simulate the service's handle() method by creating the same objects it uses.
    """

    def test_dispatch_ping(self): # type: ignore

        server = _MockServer()

        config = _MockBunch({
            'name': 'test-channel',
            'services': [],
        })

        wrapper = ChannelMCPWrapper(config, server)
        wrapper.build_wrapper()

        request = {
            'jsonrpc': '2.0',
            'method': 'ping',
            'id': 1,
        }
        raw = dumps(request)

        mcp_response = wrapper.handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.status_code, OK)
        self.assertEqual(mcp_response.body['result'], {})

    def test_dispatch_batch_all_notifications_returns_204(self): # type: ignore

        server = _MockServer()

        config = _MockBunch({
            'name': 'test-channel',
            'services': [],
        })

        wrapper = ChannelMCPWrapper(config, server)
        wrapper.build_wrapper()

        batch = [
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
        ]
        raw = dumps(batch)

        mcp_response = wrapper.handler.handle_raw_request(raw)

        self.assertEqual(mcp_response.status_code, NO_CONTENT)
        self.assertIsNone(mcp_response.body)

# ################################################################################################################################
# ################################################################################################################################
