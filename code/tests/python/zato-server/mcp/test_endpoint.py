# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import FORBIDDEN, NOT_FOUND, OK
from unittest import TestCase

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome
from zato.common.json_internal import dumps, loads
from zato.common.test import _test_sec_def_id
from zato.common.typing_ import cast_
from zato.server.connection.mcp.handler import _error_invalid_request, _mcp_protocol_version, MCPHandler
from zato.server.generic.api.gateway_mcp import GatewayMCPWrapper
from zato.server.service.internal.gateway import mcp as mcp_endpoint_module
from zato.server.service.internal.gateway.mcp import MCPEndpoint

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist

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

        # Where the skill prompts would read the user skills from - no skills in these tests
        self.repo_location = ''

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

class GatewayMCPWrapperBuild(TestCase):

    def test_build_wrapper_creates_handler(self) -> 'None':
        """ Verifies that build_wrapper creates an MCPHandler instance.
        """

        server = _MockServer()
        server.service_store.add_service('crm.get-customer')

        config = _MockBunch({
            'name': 'test-mcp-gateway',
            'services': ['crm.get-customer'],
        })

        wrapper = GatewayMCPWrapper(config, server) # pyright: ignore[reportArgumentType]
        wrapper.build_wrapper()

        self.assertIsNotNone(wrapper.handler)
        self.assertIsInstance(wrapper.handler, MCPHandler)

    def test_build_wrapper_no_opaque(self) -> 'None':
        """ Verifies that build_wrapper works without an opaque services key.
        """

        server = _MockServer()

        config = _MockBunch({
            'name': 'empty-gateway',
        })

        wrapper = GatewayMCPWrapper(config, server) # pyright: ignore[reportArgumentType]
        wrapper.build_wrapper()

        self.assertIsNotNone(wrapper.handler)

    def test_build_wrapper_empty_services(self) -> 'None':
        """ Verifies that build_wrapper with empty services produces no tools.
        """

        server = _MockServer()

        config = _MockBunch({
            'name': 'empty-services-gateway',
            'services': [],
        })

        wrapper = GatewayMCPWrapper(config, server) # pyright: ignore[reportArgumentType]
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
            'name': 'delete-gateway',
            'services': [],
        })

        wrapper = GatewayMCPWrapper(config, server) # pyright: ignore[reportArgumentType]
        wrapper.build_wrapper()

        self.assertIsNotNone(wrapper.handler)

        wrapper.delete()

        self.assertIsNone(wrapper.handler)

# ################################################################################################################################
# ################################################################################################################################

class GatewayMCPWrapperInvoke(TestCase):

    def test_invoke_service_through_wrapper(self) -> 'None':
        """ Verifies that a service can be invoked through the wrapper handler.
        """

        server = _MockServer()
        server.service_store.add_service('crm.get-customer')
        server._invoke_responses['crm.get-customer'] = {'name': 'Test Customer'}

        config = _MockBunch({
            'name': 'invoke-gateway',
            'services': ['crm.get-customer'],
        })

        wrapper = GatewayMCPWrapper(config, server) # pyright: ignore[reportArgumentType]
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
        mcp_response = wrapper.handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

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
    """ Mock of the security definition on a channel - authenticated by default, or empty.
    """
    def __init__(self, is_authenticated:'bool'=True) -> 'None':
        if is_authenticated:
            self.id = _test_sec_def_id
            self.name = 'test.sec.def'
            self.username = 'test.user'
        else:
            self.id = ''
            self.name = ''
            self.username = ''

# ################################################################################################################################
# ################################################################################################################################

class _MockChannel:
    """ Mock of the channel a service runs on.
    """
    def __init__(self, name:'str', is_authenticated:'bool'=True) -> 'None':
        self.name = name
        self.security = _MockChannelSecurity(is_authenticated)

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
        self.raw = ''

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
    """ Mock of the server's config manager holding MCP gateway configs.
    """
    def __init__(self) -> 'None':
        self.gateway_mcp = {}

# ################################################################################################################################
# ################################################################################################################################

class _MockEndpointServer:
    """ Mock of the parallel server an endpoint service reaches through self.server.
    """
    def __init__(self) -> 'None':
        self.config_manager = _MockConfigManager()

# ################################################################################################################################
# ################################################################################################################################

def _make_endpoint(gateway_name:'str', wrapper:'GatewayMCPWrapper', is_authenticated:'bool'=True) -> 'MCPEndpoint':
    """ Builds an MCPEndpoint with only the attributes that handle() uses,
    bypassing the full service initialization machinery.
    """

    endpoint = MCPEndpoint.__new__(MCPEndpoint)

    channel = _MockChannel(gateway_name, is_authenticated)
    endpoint.channel = cast_('any_', channel)
    endpoint.request = _MockRequest() # pyright: ignore[reportAttributeAccessIssue]
    endpoint.response = _MockResponse() # pyright: ignore[reportAttributeAccessIssue]
    endpoint.wsgi_environ = {'zato.http.remote_addr': '127.0.0.1'}

    server = _MockEndpointServer()
    gateway_config = _MockBunch({'conn': wrapper})
    server.config_manager.gateway_mcp[gateway_name] = gateway_config
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
            'name': 'origin-gateway',
            'services': [],
        })

        wrapper = GatewayMCPWrapper(config, server) # pyright: ignore[reportArgumentType]
        wrapper.build_wrapper()

        assert wrapper.handler is not None
        session_manager = wrapper.handler.session_manager
        session_id = session_manager.create(_mcp_protocol_version, _test_sec_def_id)

        endpoint = _make_endpoint('origin-gateway', wrapper)
        endpoint.request.http.headers['mcp-session-id'] = session_id
        endpoint.request.raw = dumps({'jsonrpc': '2.0', 'method': 'ping', 'id': 1})

        endpoint.handle()

        self.assertEqual(endpoint.response.status_code, OK)

    def test_request_with_disallowed_origin_rejected(self) -> 'None':
        """ A request carrying an Origin not on the allow list is rejected with 403
        and the target service is never invoked.
        """

        server = _MockServer()

        config = _MockBunch({
            'name': 'origin-gateway',
            'services': [],
        })

        wrapper = GatewayMCPWrapper(config, server) # pyright: ignore[reportArgumentType]
        wrapper.build_wrapper()

        assert wrapper.handler is not None
        session_manager = wrapper.handler.session_manager
        session_id = session_manager.create(_mcp_protocol_version, _test_sec_def_id)

        endpoint = _make_endpoint('origin-gateway', wrapper)
        endpoint.request.http.headers['mcp-session-id'] = session_id
        endpoint.request.http.headers['origin'] = 'https://evil.example.com'
        endpoint.request.raw = dumps({'jsonrpc': '2.0', 'method': 'ping', 'id': 1})

        endpoint.handle()

        self.assertEqual(endpoint.response.status_code, FORBIDDEN)
        self.assertEqual(endpoint.response.payload, '')

    def test_request_with_allowed_origin_accepted(self) -> 'None':
        """ A request carrying an Origin that is on the gateway's allow list is processed.
        """

        server = _MockServer()

        config = _MockBunch({
            'name': 'origin-gateway',
            'services': [],
            'allowed_origins': ['https://app.example.com'],
        })

        wrapper = GatewayMCPWrapper(config, server) # pyright: ignore[reportArgumentType]
        wrapper.build_wrapper()

        assert wrapper.handler is not None
        session_manager = wrapper.handler.session_manager
        session_id = session_manager.create(_mcp_protocol_version, _test_sec_def_id)

        endpoint = _make_endpoint('origin-gateway', wrapper)
        endpoint.request.http.headers['mcp-session-id'] = session_id
        endpoint.request.http.headers['origin'] = 'https://app.example.com'
        endpoint.request.raw = dumps({'jsonrpc': '2.0', 'method': 'ping', 'id': 1})

        endpoint.handle()

        self.assertEqual(endpoint.response.status_code, OK)

# ################################################################################################################################
# ################################################################################################################################

class MCPEndpointNoHandler(TestCase):
    """ Tests requests arriving when the wrapper has no handler,
    which happens when the gateway is not built yet, its build failed,
    or it is being deleted.
    """

    def test_request_after_wrapper_delete_returns_not_found(self) -> 'None':
        """ A request processed after the wrapper's handler was cleared
        returns 404 instead of failing with an exception.
        """

        server = _MockServer()

        config = _MockBunch({
            'name': 'deleted-gateway',
            'services': [],
        })

        wrapper = GatewayMCPWrapper(config, server) # pyright: ignore[reportArgumentType]
        wrapper.build_wrapper()

        # Simulate the gateway being deleted while a request is in flight ..
        wrapper.delete()

        # .. a request arriving now must get a clean 404 ..
        endpoint = _make_endpoint('deleted-gateway', wrapper)
        endpoint.request.raw = dumps({'jsonrpc': '2.0', 'method': 'ping', 'id': 1})

        endpoint.handle()

        self.assertEqual(endpoint.response.status_code, NOT_FOUND)
        self.assertEqual(endpoint.response.payload, '')

    def test_delete_request_after_wrapper_delete_returns_not_found(self) -> 'None':
        """ A DELETE for session termination after the wrapper's handler
        was cleared also returns 404.
        """

        server = _MockServer()

        config = _MockBunch({
            'name': 'deleted-gateway',
            'services': [],
        })

        wrapper = GatewayMCPWrapper(config, server) # pyright: ignore[reportArgumentType]
        wrapper.build_wrapper()
        wrapper.delete()

        endpoint = _make_endpoint('deleted-gateway', wrapper)
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
            'name': 'unbuilt-gateway',
            'services': [],
        })

        # The wrapper exists but build_wrapper was never called, so there is no handler ..
        wrapper = GatewayMCPWrapper(config, server) # pyright: ignore[reportArgumentType]

        # .. a request arriving now must get a clean 404 ..
        endpoint = _make_endpoint('unbuilt-gateway', wrapper)
        endpoint.request.raw = dumps({'jsonrpc': '2.0', 'method': 'ping', 'id': 1})

        endpoint.handle()

        self.assertEqual(endpoint.response.status_code, NOT_FOUND)
        self.assertEqual(endpoint.response.payload, '')

    def test_request_with_live_wrapper_dispatches_normally(self) -> 'None':
        """ The same endpoint construction with a live wrapper dispatches normally,
        proving the 404 above comes from the no-handler guard.
        """

        server = _MockServer()

        config = _MockBunch({
            'name': 'live-gateway',
            'services': [],
        })

        wrapper = GatewayMCPWrapper(config, server) # pyright: ignore[reportArgumentType]
        wrapper.build_wrapper()

        assert wrapper.handler is not None
        session_manager = wrapper.handler.session_manager
        session_id = session_manager.create(_mcp_protocol_version, _test_sec_def_id)

        endpoint = _make_endpoint('live-gateway', wrapper)
        endpoint.request.http.headers['mcp-session-id'] = session_id
        endpoint.request.raw = dumps({'jsonrpc': '2.0', 'method': 'ping', 'id': 1})

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
            'name': 'test-gateway',
            'services': [],
        })

        wrapper = GatewayMCPWrapper(config, server) # pyright: ignore[reportArgumentType]
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
        mcp_response = wrapper.handler.handle_raw_request(raw, _test_sec_def_id, session_id=session_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        result = body['result']
        self.assertEqual(result, {})

    def test_dispatch_array_body_is_invalid(self) -> 'None':
        """ Verifies that an array body returns an invalid request error -
        batching is not part of any supported protocol revision.
        """

        server = _MockServer()

        config = _MockBunch({
            'name': 'test-gateway',
            'services': [],
        })

        wrapper = GatewayMCPWrapper(config, server) # pyright: ignore[reportArgumentType]
        wrapper.build_wrapper()

        messages = [
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
        ]
        raw = dumps(messages)

        assert wrapper.handler is not None
        mcp_response = wrapper.handler.handle_raw_request(raw, _test_sec_def_id)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        error = body['error']
        self.assertEqual(error['code'], _error_invalid_request)

# ################################################################################################################################
# ################################################################################################################################

class _MockUntouchableHandler:
    """ A handler stand-in that fails the test if the endpoint ever dispatches to it.
    """
    def handle_raw_request(self, *args:'any_', **kwargs:'any_') -> 'None':
        raise Exception('The handler must not be reached without credentials')

# ################################################################################################################################
# ################################################################################################################################

class _MockAuditLog:
    """ Records the audit events the endpoint inserts.
    """
    def __init__(self) -> 'None':
        self.events:'anylist' = []

    def insert(self, **kwargs:'any_') -> 'None':
        self.events.append(kwargs)

# ################################################################################################################################
# ################################################################################################################################

class MCPEndpointWithoutCredentials(TestCase):
    """ Tests requests reaching the endpoint when nothing authenticated at the HTTP layer.
    """

    def test_initialize_without_credentials_is_rejected(self) -> 'None':
        """ A well-formed initialize request without an authenticated definition
        gets 403 with an empty payload and the handler is never dispatched to.
        """

        server:'any_' = _MockServer()

        config:'any_' = _MockBunch({
            'name': 'no-security-gateway',
            'services': [],
        })

        wrapper = GatewayMCPWrapper(config, server)
        wrapper.build_wrapper()

        wrapper.handler = cast_('any_', _MockUntouchableHandler())

        endpoint = _make_endpoint('no-security-gateway', wrapper, is_authenticated=False)
        endpoint.request.raw = dumps({
            'jsonrpc': '2.0',
            'method': 'initialize',
            'id': 1,
            'params': {
                'protocolVersion': _mcp_protocol_version,
                'capabilities': {},
                'clientInfo': {'name': 'test-client', 'version': '1.0'},
            },
        })

        endpoint.handle()

        self.assertEqual(endpoint.response.status_code, FORBIDDEN)
        self.assertEqual(endpoint.response.payload, '')

    def test_valid_session_without_credentials_is_rejected(self) -> 'None':
        """ A ping that carries a valid session id is still rejected when nothing authenticated.
        """

        server:'any_' = _MockServer()

        config:'any_' = _MockBunch({
            'name': 'no-security-gateway',
            'services': [],
        })

        wrapper = GatewayMCPWrapper(config, server)
        wrapper.build_wrapper()

        assert wrapper.handler is not None
        session_manager = wrapper.handler.session_manager
        session_id = session_manager.create(_mcp_protocol_version, _test_sec_def_id)

        endpoint = _make_endpoint('no-security-gateway', wrapper, is_authenticated=False)
        endpoint.request.http.headers['mcp-session-id'] = session_id
        endpoint.request.raw = dumps({'jsonrpc': '2.0', 'method': 'ping', 'id': 1})

        endpoint.handle()

        self.assertEqual(endpoint.response.status_code, FORBIDDEN)
        self.assertEqual(endpoint.response.payload, '')

    def test_rejection_writes_audit_event(self) -> 'None':
        """ A rejection on a gateway with its audit log on writes one auth-failed
        event with an empty identity and an error outcome.
        """

        server:'any_' = _MockServer()

        config:'any_' = _MockBunch({
            'name': 'no-security-gateway',
            'services': [],
            'is_audit_log_active': True,
        })

        wrapper = GatewayMCPWrapper(config, server)
        wrapper.build_wrapper()

        # The wrapper's cached audit log is this in-memory recorder
        audit_log = _MockAuditLog()
        wrapper._audit_log = cast_('any_', audit_log)

        endpoint = _make_endpoint('no-security-gateway', wrapper, is_authenticated=False)
        endpoint.cid = 'test-cid-1'
        endpoint.request.raw = dumps({'jsonrpc': '2.0', 'method': 'ping', 'id': 1})

        endpoint.handle()

        self.assertEqual(endpoint.response.status_code, FORBIDDEN)
        self.assertEqual(len(audit_log.events), 1)

        event = audit_log.events[0]
        self.assertEqual(event['event_type'], AuditEvent.Auth_Failed)
        self.assertEqual(event['object_name'], 'no-security-gateway')
        self.assertEqual(event['ext_client_id'], '')
        self.assertEqual(event['outcome'], AuditOutcome.Error)
        self.assertEqual(event['cid'], 'test-cid-1')

# ################################################################################################################################
# ################################################################################################################################
