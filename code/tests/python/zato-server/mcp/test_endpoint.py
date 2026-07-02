# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import FORBIDDEN, NO_CONTENT, NOT_FOUND, OK
from unittest import TestCase

# Zato
from zato.common.json_internal import dumps, loads
from zato.common.test import _test_sec_def_id
from zato.server.connection.mcp.handler import _mcp_protocol_version, MCPHandler
from zato.server.generic.api.channel_mcp import ChannelMCPWrapper
from zato.server.service.internal.channel import mcp as mcp_endpoint_module
from zato.server.service.internal.channel.mcp import MCPEndpoint

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

class _MockChannelSecurity:
    """ Mock of the authenticated security definition on a channel.
    """
    def __init__(self) -> 'None':
        self.id = _test_sec_def_id
        self.username = 'test.user'

# ################################################################################################################################
# ################################################################################################################################

class _MockChannel:
    """ Mock of the channel a service runs on.
    """
    def __init__(self, name:'str') -> 'None':
        self.name = name
        self.security = _MockChannelSecurity()

# ################################################################################################################################
# ################################################################################################################################

class _MockHTTPRequest:
    """ Mock of the HTTP portion of a service request.
    """
    def __init__(self) -> 'None':
        self.headers = {}
        self.method = 'POST'

# ################################################################################################################################
# ################################################################################################################################

class _MockRequest:
    """ Mock of a service request.
    """
    def __init__(self) -> 'None':
        self.http = _MockHTTPRequest()
        self.raw_request = ''

# ################################################################################################################################
# ################################################################################################################################

class _MockResponse:
    """ Mock of a service response.
    """
    def __init__(self) -> 'None':
        self.status_code = OK
        self.payload = None
        self.headers = {}
        self.data_format = ''

# ################################################################################################################################
# ################################################################################################################################

class _MockConfigManager:
    """ Mock of the server's config manager holding MCP channel configs.
    """
    def __init__(self) -> 'None':
        self.channel_mcp = {}

# ################################################################################################################################
# ################################################################################################################################

class _MockEndpointServer:
    """ Mock of the parallel server an endpoint service reaches through self.server.
    """
    def __init__(self) -> 'None':
        self.config_manager = _MockConfigManager()

# ################################################################################################################################
# ################################################################################################################################

def _make_endpoint(channel_name:'str', wrapper:'ChannelMCPWrapper') -> 'MCPEndpoint':
    """ Builds an MCPEndpoint with only the attributes that handle() uses,
    bypassing the full service initialization machinery.
    """

    endpoint = MCPEndpoint.__new__(MCPEndpoint)

    endpoint.channel = _MockChannel(channel_name) # pyright: ignore[reportAttributeAccessIssue]
    endpoint.request = _MockRequest() # pyright: ignore[reportAttributeAccessIssue]
    endpoint.response = _MockResponse() # pyright: ignore[reportAttributeAccessIssue]
    endpoint.wsgi_environ = {'zato.http.remote_addr': '127.0.0.1'}

    server = _MockEndpointServer()
    channel_config = _MockBunch({'conn': wrapper})
    server.config_manager.channel_mcp[channel_name] = channel_config
    endpoint.server = server # pyright: ignore[reportAttributeAccessIssue]

    out = endpoint
    return out

# ################################################################################################################################
# ################################################################################################################################

class MCPEndpointOriginValidation(TestCase):
    """ Tests that the Origin header is validated to prevent DNS rebinding attacks.
    """

    def setUp(self) -> 'None':
        self._original_check_origin = mcp_endpoint_module.check_origin
        mcp_endpoint_module.check_origin = True

    def tearDown(self) -> 'None':
        mcp_endpoint_module.check_origin = self._original_check_origin

    def test_request_without_origin_is_allowed(self) -> 'None':
        """ A request that carries no Origin header (a non-browser MCP client)
        is processed normally.
        """

        server = _MockServer()

        config = _MockBunch({
            'name': 'origin-channel',
            'services': [],
        })

        wrapper = ChannelMCPWrapper(config, server) # pyright: ignore[reportArgumentType]
        wrapper.build_wrapper()

        assert wrapper.handler is not None
        session_manager = wrapper.handler.session_manager
        session_id = session_manager.create(_mcp_protocol_version, _test_sec_def_id)

        endpoint = _make_endpoint('origin-channel', wrapper)
        endpoint.request.http.headers['mcp-session-id'] = session_id
        endpoint.request.raw_request = dumps({'jsonrpc': '2.0', 'method': 'ping', 'id': 1})

        endpoint.handle()

        self.assertEqual(endpoint.response.status_code, OK)

    def test_request_with_disallowed_origin_rejected(self) -> 'None':
        """ A request carrying an Origin not on the allow list is rejected with 403
        and the target service is never invoked.
        """

        server = _MockServer()

        config = _MockBunch({
            'name': 'origin-channel',
            'services': [],
        })

        wrapper = ChannelMCPWrapper(config, server) # pyright: ignore[reportArgumentType]
        wrapper.build_wrapper()

        assert wrapper.handler is not None
        session_manager = wrapper.handler.session_manager
        session_id = session_manager.create(_mcp_protocol_version, _test_sec_def_id)

        endpoint = _make_endpoint('origin-channel', wrapper)
        endpoint.request.http.headers['mcp-session-id'] = session_id
        endpoint.request.http.headers['origin'] = 'https://evil.example.com'
        endpoint.request.raw_request = dumps({'jsonrpc': '2.0', 'method': 'ping', 'id': 1})

        endpoint.handle()

        self.assertEqual(endpoint.response.status_code, FORBIDDEN)
        self.assertEqual(endpoint.response.payload, '')

    def test_request_with_allowed_origin_accepted(self) -> 'None':
        """ A request carrying an Origin that is on the channel's allow list is processed.
        """

        server = _MockServer()

        config = _MockBunch({
            'name': 'origin-channel',
            'services': [],
            'allowed_origins': ['https://app.example.com'],
        })

        wrapper = ChannelMCPWrapper(config, server) # pyright: ignore[reportArgumentType]
        wrapper.build_wrapper()

        assert wrapper.handler is not None
        session_manager = wrapper.handler.session_manager
        session_id = session_manager.create(_mcp_protocol_version, _test_sec_def_id)

        endpoint = _make_endpoint('origin-channel', wrapper)
        endpoint.request.http.headers['mcp-session-id'] = session_id
        endpoint.request.http.headers['origin'] = 'https://app.example.com'
        endpoint.request.raw_request = dumps({'jsonrpc': '2.0', 'method': 'ping', 'id': 1})

        endpoint.handle()

        self.assertEqual(endpoint.response.status_code, OK)

# ################################################################################################################################
# ################################################################################################################################

class MCPEndpointNoHandler(TestCase):
    """ Tests requests arriving when the wrapper has no handler,
    which happens when the channel is not built yet, its build failed,
    or it is being deleted.
    """

    def test_request_after_wrapper_delete_returns_not_found(self) -> 'None':
        """ A request processed after the wrapper's handler was cleared
        returns 404 instead of failing with an exception.
        """

        server = _MockServer()

        config = _MockBunch({
            'name': 'deleted-channel',
            'services': [],
        })

        wrapper = ChannelMCPWrapper(config, server) # pyright: ignore[reportArgumentType]
        wrapper.build_wrapper()

        # Simulate the channel being deleted while a request is in flight ..
        wrapper.delete()

        # .. a request arriving now must get a clean 404 ..
        endpoint = _make_endpoint('deleted-channel', wrapper)
        endpoint.request.raw_request = dumps({'jsonrpc': '2.0', 'method': 'ping', 'id': 1})

        endpoint.handle()

        self.assertEqual(endpoint.response.status_code, NOT_FOUND)
        self.assertEqual(endpoint.response.payload, '')

    def test_delete_request_after_wrapper_delete_returns_not_found(self) -> 'None':
        """ A DELETE for session termination after the wrapper's handler
        was cleared also returns 404.
        """

        server = _MockServer()

        config = _MockBunch({
            'name': 'deleted-channel',
            'services': [],
        })

        wrapper = ChannelMCPWrapper(config, server) # pyright: ignore[reportArgumentType]
        wrapper.build_wrapper()
        wrapper.delete()

        endpoint = _make_endpoint('deleted-channel', wrapper)
        endpoint.request.http.method = 'DELETE'

        endpoint.handle()

        self.assertEqual(endpoint.response.status_code, NOT_FOUND)
        self.assertEqual(endpoint.response.payload, '')

    def test_request_before_wrapper_build_returns_not_found(self) -> 'None':
        """ A request arriving after the wrapper is constructed
        but before build_wrapper runs also returns 404.
        """

        server = _MockServer()

        config = _MockBunch({
            'name': 'unbuilt-channel',
            'services': [],
        })

        # The wrapper exists but build_wrapper was never called, so there is no handler ..
        wrapper = ChannelMCPWrapper(config, server) # pyright: ignore[reportArgumentType]

        # .. a request arriving now must get a clean 404 ..
        endpoint = _make_endpoint('unbuilt-channel', wrapper)
        endpoint.request.raw_request = dumps({'jsonrpc': '2.0', 'method': 'ping', 'id': 1})

        endpoint.handle()

        self.assertEqual(endpoint.response.status_code, NOT_FOUND)
        self.assertEqual(endpoint.response.payload, '')

    def test_request_with_live_wrapper_dispatches_normally(self) -> 'None':
        """ The same endpoint construction with a live wrapper dispatches normally,
        proving the 404 above comes from the no-handler guard.
        """

        server = _MockServer()

        config = _MockBunch({
            'name': 'live-channel',
            'services': [],
        })

        wrapper = ChannelMCPWrapper(config, server) # pyright: ignore[reportArgumentType]
        wrapper.build_wrapper()

        assert wrapper.handler is not None
        session_manager = wrapper.handler.session_manager
        session_id = session_manager.create(_mcp_protocol_version, _test_sec_def_id)

        endpoint = _make_endpoint('live-channel', wrapper)
        endpoint.request.http.headers['mcp-session-id'] = session_id
        endpoint.request.raw_request = dumps({'jsonrpc': '2.0', 'method': 'ping', 'id': 1})

        endpoint.handle()

        self.assertEqual(endpoint.response.status_code, OK)

        body = loads(endpoint.response.payload)
        result = body['result']
        self.assertEqual(result, {})

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
