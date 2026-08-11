# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import NO_CONTENT, OK
from unittest import TestCase

# Zato
from zato.common.api import MCP
from zato.common.json_internal import dumps
from zato.common.test import _test_sec_def_id
from zato.common.util.safeguards.config import build_safeguard_config
from zato.common.util.truncate.tokens import build_token_cap_config
from zato.server.connection.mcp.handler import MCPHandler, _error_invalid_request, _error_method_not_found, \
    _server_name, _server_version
from zato.server.connection.mcp.prompts import SkillPrompts
from zato.server.connection.mcp.session import MCPSessionManager
from zato.server.connection.mcp.stateless import _error_header_mismatch, _error_unsupported_protocol_version, \
    _meta_key_server_info, _tools_list_cache_scope, _tools_list_ttl_ms

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anydictnone, anylist, anylistnone, callable_, strnone

# ################################################################################################################################
# ################################################################################################################################

# The tool most tests below invoke
_test_tool_name = 'crm.get-customer'

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

def _invoke_success(service_name:'str', payload:'anydict') -> 'anydict':
    """ Mock invoke function that returns a simple dict.
    """

    return {'service': service_name, 'input': payload}

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

    # Response shaping and input validation stay off in these tests - empty configs keep every stage disabled.
    safeguard_config = build_safeguard_config({})
    token_cap_config = build_token_cap_config({})

    out = MCPHandler(registry, invoke_func, session_manager, safeguard_config, token_cap_config, False, SkillPrompts('', []))
    return out

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

def _dispatch(
    handler:'MCPHandler',
    request:'anydict',
    mcp_method_header:'strnone',
    mcp_name_header:'strnone' = None,
    protocol_version_header:'strnone' = MCP.Protocol_Version_Stateless,
    ) -> 'any_':
    """ Sends one request through the handler the way the endpoint does for the stateless revision.
    """

    raw = dumps(request)

    out = handler.handle_raw_request(
        raw, _test_sec_def_id,
        protocol_version_header=protocol_version_header,
        mcp_method_header=mcp_method_header,
        mcp_name_header=mcp_name_header,
    )

    return out

# ################################################################################################################################
# ################################################################################################################################

class VersionRouting(TestCase):
    """ Tests how requests are routed to the stateless revision and how unsupported versions are rejected.
    """

    def test_header_routes_to_stateless_dispatch(self) -> 'None':
        """ A request with the stateless version in its header needs no session at all.
        """

        handler = _make_handler()

        request = _make_request('tools/list')
        mcp_response = _dispatch(handler, request, 'tools/list')

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        self.assertIn('result', body)

    def test_meta_routes_to_stateless_dispatch(self) -> 'None':
        """ A request naming the stateless version in params._meta routes the same way as the header.
        """

        handler = _make_handler()

        params = {'_meta': {'io.modelcontextprotocol/protocolVersion': MCP.Protocol_Version_Stateless}}
        request = _make_request('tools/list', params)
        mcp_response = _dispatch(handler, request, 'tools/list', protocol_version_header=None)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        self.assertIn('result', body)

    def test_unsupported_version_is_rejected(self) -> 'None':
        """ A version this gateway does not speak returns its own error code.
        """

        handler = _make_handler()

        request = _make_request('tools/list')
        mcp_response = _dispatch(handler, request, 'tools/list', protocol_version_header='2030-01-01')

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        error = body['error']
        self.assertEqual(error['code'], _error_unsupported_protocol_version)

    def test_array_body_is_invalid(self) -> 'None':
        """ An array body is rejected before any routing happens.
        """

        handler = _make_handler()

        messages = [
            _make_request('tools/list', request_id=1),
            _make_request('tools/list', request_id=2),
        ]
        raw = dumps(messages)

        mcp_response = handler.handle_raw_request(
            raw, _test_sec_def_id,
            protocol_version_header=MCP.Protocol_Version_Stateless,
            mcp_method_header='tools/list',
        )

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        error = body['error']
        self.assertEqual(error['code'], _error_invalid_request)

# ################################################################################################################################
# ################################################################################################################################

class ServerDiscover(TestCase):
    """ Tests the server/discover method.
    """

    def test_discover_advertises_versions_and_identity(self) -> 'None':

        handler = _make_handler()

        request = _make_request('server/discover')
        mcp_response = _dispatch(handler, request, 'server/discover')

        self.assertEqual(mcp_response.status_code, OK)
        self.assertEqual(mcp_response.method, 'server/discover')

        body = mcp_response.body
        result = body['result']

        self.assertEqual(result['protocolVersions'], MCP.Protocol_Versions_Supported)
        self.assertEqual(result['resultType'], 'complete')

        capabilities = result['capabilities']
        tools_capability = capabilities['tools']
        self.assertIsInstance(tools_capability, dict)

        server_info = result['serverInfo']
        self.assertEqual(server_info['name'], _server_name)
        self.assertEqual(server_info['version'], _server_version)

    def test_discover_routes_without_a_version_header(self) -> 'None':
        """ A discover probe carries no version of its own and still routes to the stateless dispatch.
        """

        handler = _make_handler()

        request = _make_request('server/discover')
        mcp_response = _dispatch(handler, request, 'server/discover', protocol_version_header=None)

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        result = body['result']
        self.assertEqual(result['protocolVersions'], MCP.Protocol_Versions_Supported)

# ################################################################################################################################
# ################################################################################################################################

class HeaderAgreement(TestCase):
    """ Tests that the Mcp-Method and Mcp-Name headers must agree with the request body.
    """

    def test_missing_method_header_is_a_mismatch(self) -> 'None':

        handler = _make_handler()

        request = _make_request('tools/list')
        mcp_response = _dispatch(handler, request, None)

        body = mcp_response.body
        error = body['error']
        self.assertEqual(error['code'], _error_header_mismatch)

    def test_wrong_method_header_is_a_mismatch(self) -> 'None':

        handler = _make_handler()

        request = _make_request('tools/list')
        mcp_response = _dispatch(handler, request, 'tools/call')

        body = mcp_response.body
        error = body['error']
        self.assertEqual(error['code'], _error_header_mismatch)

    def test_missing_name_header_is_a_mismatch_for_tools_call(self) -> 'None':

        registry = _MockToolRegistry(allowed_tools={_test_tool_name})
        handler = _make_handler(registry=registry)

        params = {'name': _test_tool_name, 'arguments': {}}
        request = _make_request('tools/call', params)
        mcp_response = _dispatch(handler, request, 'tools/call')

        body = mcp_response.body
        error = body['error']
        self.assertEqual(error['code'], _error_header_mismatch)

    def test_wrong_name_header_is_a_mismatch_for_tools_call(self) -> 'None':

        registry = _MockToolRegistry(allowed_tools={_test_tool_name})
        handler = _make_handler(registry=registry)

        params = {'name': _test_tool_name, 'arguments': {}}
        request = _make_request('tools/call', params)
        mcp_response = _dispatch(handler, request, 'tools/call', mcp_name_header='other.tool')

        body = mcp_response.body
        error = body['error']
        self.assertEqual(error['code'], _error_header_mismatch)

# ################################################################################################################################
# ################################################################################################################################

class StatelessToolsFlow(TestCase):
    """ Tests tools/list and tools/call in the stateless revision.
    """

    def test_tools_list_carries_cache_hints_and_result_type(self) -> 'None':

        tools = [
            {'name': _test_tool_name, 'description': 'Get customer', 'inputSchema': {'type': 'object'}},
        ]
        registry = _MockToolRegistry(tools=tools)
        handler = _make_handler(registry=registry)

        request = _make_request('tools/list')
        mcp_response = _dispatch(handler, request, 'tools/list')

        self.assertEqual(mcp_response.status_code, OK)

        body = mcp_response.body
        result = body['result']

        self.assertEqual(result['tools'], tools)
        self.assertEqual(result['ttlMs'], _tools_list_ttl_ms)
        self.assertEqual(result['cacheScope'], _tools_list_cache_scope)
        self.assertEqual(result['resultType'], 'complete')

        meta = result['_meta']
        server_info = meta[_meta_key_server_info]
        self.assertEqual(server_info['name'], _server_name)
        self.assertEqual(server_info['version'], _server_version)

    def test_tools_call_needs_no_session(self) -> 'None':

        registry = _MockToolRegistry(allowed_tools={_test_tool_name})
        handler = _make_handler(registry=registry)

        params = {'name': _test_tool_name, 'arguments': {'customer_id': '123'}}
        request = _make_request('tools/call', params)
        mcp_response = _dispatch(handler, request, 'tools/call', mcp_name_header=_test_tool_name)

        self.assertEqual(mcp_response.status_code, OK)
        self.assertEqual(mcp_response.method, 'tools/call')
        self.assertEqual(mcp_response.tool_name, _test_tool_name)

        body = mcp_response.body
        result = body['result']

        self.assertNotIn('isError', result)
        self.assertEqual(result['resultType'], 'complete')

        content = result['content']
        first_content = content[0]
        self.assertEqual(first_content['type'], 'text')

    def test_no_session_is_ever_created(self) -> 'None':

        registry = _MockToolRegistry(allowed_tools={_test_tool_name})
        handler = _make_handler(registry=registry)
        session_manager = handler.session_manager

        params = {'name': _test_tool_name, 'arguments': {}}
        request = _make_request('tools/call', params)
        mcp_response = _dispatch(handler, request, 'tools/call', mcp_name_header=_test_tool_name)

        self.assertIsNone(mcp_response.session_id)
        self.assertEqual(session_manager.session_count, 0)

# ################################################################################################################################
# ################################################################################################################################

class SessionRevisionMethods(TestCase):
    """ Tests that the methods of the session-based revision do not exist in the stateless one.
    """

    def test_initialize_is_unknown(self) -> 'None':

        handler = _make_handler()

        params = {'protocolVersion': MCP.Protocol_Version_Stateless, 'capabilities': {}}
        request = _make_request('initialize', params)
        mcp_response = _dispatch(handler, request, 'initialize')

        body = mcp_response.body
        error = body['error']
        self.assertEqual(error['code'], _error_method_not_found)

    def test_ping_is_unknown(self) -> 'None':

        handler = _make_handler()

        request = _make_request('ping')
        mcp_response = _dispatch(handler, request, 'ping')

        body = mcp_response.body
        error = body['error']
        self.assertEqual(error['code'], _error_method_not_found)

# ################################################################################################################################
# ################################################################################################################################

class StatelessNotifications(TestCase):
    """ Tests that notifications produce no response body.
    """

    def test_notification_returns_204(self) -> 'None':

        handler = _make_handler()

        request = {'jsonrpc': '2.0', 'method': 'notifications/progress'}
        raw = dumps(request)

        mcp_response = handler.handle_raw_request(
            raw, _test_sec_def_id,
            protocol_version_header=MCP.Protocol_Version_Stateless,
            mcp_method_header='notifications/progress',
        )

        self.assertEqual(mcp_response.status_code, NO_CONTENT)
        self.assertIsNone(mcp_response.body)

# ################################################################################################################################
# ################################################################################################################################
