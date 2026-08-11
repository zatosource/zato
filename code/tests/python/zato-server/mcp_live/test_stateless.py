# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import FORBIDDEN, OK

# pytest
import pytest

# local
from _client_stateless import MCPStatelessClient
from _constants import _demo_echo_service, _error_header_mismatch, _error_method_not_found, \
    _error_unsupported_protocol_version, _protocol_version_stateless, _raise_service, _zato_internal_prefix
from test_audit_log import _get_demo_gateway, _read_events, _set_audit_log_active, _wait_until_audit_is_on

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource
from zato.common.util.gateway import mcp_gateway_name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# The session-based protocol revision, advertised by server/discover next to the stateless one
_protocol_version_sessions = '2025-06-18'

# The identity the server reports
_expected_server_name    = 'Apache'
_expected_server_version = '2.4'

# The _meta key naming the server in each result
_meta_key_server_info = 'io.modelcontextprotocol/serverInfo'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='function')
def client(zato_server:'anydict') -> 'MCPStatelessClient':
    out = MCPStatelessClient(zato_server['mcp_url'], auth=zato_server['mcp_auth'])
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestDiscover:
    """ Tests the server/discover method.
    """

    def test_discover_advertises_versions_and_identity(self, client:'MCPStatelessClient') -> 'None':
        """ Discover names both protocol revisions, the capabilities and the server identity.
        """

        response = client.discover()
        assert response.status_code == OK

        data = response.json()
        result = data['result']

        assert result['protocolVersions'] == [_protocol_version_sessions, _protocol_version_stateless]
        assert result['resultType'] == 'complete'

        capabilities = result['capabilities']
        assert 'tools' in capabilities

        server_info = result['serverInfo']
        assert server_info['name'] == _expected_server_name
        assert server_info['version'] == _expected_server_version

# ################################################################################################################################

    def test_discover_needs_no_version_header(self, zato_server:'anydict') -> 'None':
        """ A discover probe works even without the MCP-Protocol-Version header.
        """

        client = MCPStatelessClient(zato_server['mcp_url'], auth=zato_server['mcp_auth'])
        response = client.jsonrpc('server/discover', include_version_header=False)

        assert response.status_code == OK

        data = response.json()
        result = data['result']
        assert result['protocolVersions'] == [_protocol_version_sessions, _protocol_version_stateless]

# ################################################################################################################################
# ################################################################################################################################

class TestToolsFlow:
    """ Tests the stateless tools/list and tools/call flow - no initialize, no session headers.
    """

    def test_tools_list_carries_cache_hints(self, client:'MCPStatelessClient') -> 'None':

        response = client.tools_list()
        assert response.status_code == OK

        data = response.json()
        result = data['result']

        assert result['ttlMs'] > 0
        assert result['cacheScope'] == 'private'
        assert result['resultType'] == 'complete'

        meta = result['_meta']
        server_info = meta[_meta_key_server_info]
        assert server_info['name'] == _expected_server_name
        assert server_info['version'] == _expected_server_version

# ################################################################################################################################

    def test_tools_list_is_sorted_by_name(self, client:'MCPStatelessClient') -> 'None':

        response = client.tools_list()
        data = response.json()
        result = data['result']
        tools = result['tools']

        tool_names = []

        for tool in tools:
            tool_names.append(tool['name'])

        assert tool_names == sorted(tool_names)
        assert _demo_echo_service in tool_names
        assert _raise_service in tool_names

# ################################################################################################################################

    def test_tools_call_needs_no_session(self, client:'MCPStatelessClient') -> 'None':

        response = client.tools_call(_demo_echo_service, {'message': 'hello'})
        assert response.status_code == OK

        data = response.json()
        result = data['result']

        assert 'isError' not in result
        assert result['resultType'] == 'complete'

        content = result['content']
        first_content = content[0]
        assert first_content['type'] == 'text'

        # No session is ever created on this path.
        assert 'Mcp-Session-Id' not in response.headers

# ################################################################################################################################

    def test_initialize_is_unknown(self, client:'MCPStatelessClient') -> 'None':

        params = {'protocolVersion': _protocol_version_stateless, 'capabilities': {}}
        response = client.jsonrpc('initialize', params=params)

        data = response.json()
        error = data['error']
        assert error['code'] == _error_method_not_found

# ################################################################################################################################

    def test_ping_is_unknown(self, client:'MCPStatelessClient') -> 'None':

        response = client.jsonrpc('ping')

        data = response.json()
        error = data['error']
        assert error['code'] == _error_method_not_found

# ################################################################################################################################
# ################################################################################################################################

class TestHeaders:
    """ Tests that the Mcp-Method and Mcp-Name headers must agree with the request body.
    """

    def test_missing_method_header_is_a_mismatch(self, client:'MCPStatelessClient') -> 'None':

        response = client.jsonrpc('tools/list', include_method_header=False)

        data = response.json()
        error = data['error']
        assert error['code'] == _error_header_mismatch

# ################################################################################################################################

    def test_wrong_method_header_is_a_mismatch(self, client:'MCPStatelessClient') -> 'None':

        response = client.jsonrpc('tools/list', mcp_method_header='tools/call')

        data = response.json()
        error = data['error']
        assert error['code'] == _error_header_mismatch

# ################################################################################################################################

    def test_missing_name_header_is_a_mismatch_for_tools_call(self, client:'MCPStatelessClient') -> 'None':

        params = {'name': _demo_echo_service, 'arguments': {}}
        response = client.jsonrpc('tools/call', params=params)

        data = response.json()
        error = data['error']
        assert error['code'] == _error_header_mismatch

# ################################################################################################################################

    def test_wrong_name_header_is_a_mismatch_for_tools_call(self, client:'MCPStatelessClient') -> 'None':

        params = {'name': _demo_echo_service, 'arguments': {}}
        response = client.jsonrpc('tools/call', params=params, mcp_name_header='other.service')

        data = response.json()
        error = data['error']
        assert error['code'] == _error_header_mismatch

# ################################################################################################################################

    def test_unsupported_version_is_rejected(self, client:'MCPStatelessClient') -> 'None':

        response = client.jsonrpc('tools/list', protocol_version_header='2030-01-01')

        data = response.json()
        error = data['error']
        assert error['code'] == _error_unsupported_protocol_version

# ################################################################################################################################
# ################################################################################################################################

class TestAuth:
    """ Tests that authentication is enforced on the stateless path the same as on the session-based one.
    """

    def test_wrong_credentials_rejected(self, zato_server:'anydict') -> 'None':

        client = MCPStatelessClient(zato_server['mcp_url'], auth=('test.wrong.user', 'test.wrong.password'))
        response = client.tools_list()

        assert response.status_code == FORBIDDEN

# ################################################################################################################################
# ################################################################################################################################

class TestACL:
    """ Tests that the allow list is enforced on the stateless path.
    """

    def test_internal_service_rejected(self, client:'MCPStatelessClient') -> 'None':

        response = client.tools_call('zato.ping')

        data = response.json()
        error = data['error']
        assert error['code'] == _error_method_not_found

# ################################################################################################################################

    def test_unlisted_service_rejected(self, client:'MCPStatelessClient') -> 'None':

        response = client.tools_call('my.private.service')

        data = response.json()
        error = data['error']
        assert error['code'] == _error_method_not_found

# ################################################################################################################################

    def test_tools_list_has_no_internal_services(self, client:'MCPStatelessClient') -> 'None':

        response = client.tools_list()

        data = response.json()
        result = data['result']
        tools = result['tools']

        for tool in tools:
            tool_name = tool['name']
            assert not tool_name.startswith(_zato_internal_prefix), \
                f'Internal service exposed in tools/list: {tool_name}'

# ################################################################################################################################
# ################################################################################################################################

class TestDiscoverAuditLog:
    """ Tests that server/discover lands in the audit log under its own event type.
    """

    def test_discover_audits_with_no_session(self, zato_server:'anydict') -> 'None':

        gateway = _get_demo_gateway(zato_server)

        try:
            # Toggle the audit log on and wait until enforcement picks it up ..
            _set_audit_log_active(zato_server, gateway, True)
            last_seen_id = _wait_until_audit_is_on(zato_server)

            # .. run one discover request ..
            client = MCPStatelessClient(zato_server['mcp_url'], auth=zato_server['mcp_auth'])
            response = client.discover()
            assert response.status_code == OK

            # .. which lands as exactly one mcp-discover event ..
            events = _read_events(zato_server, min_id=last_seen_id)

            event_count = len(events)
            assert event_count == 1, f'Expected one event, got: {events}'

            discover_event = events[0]
            assert discover_event['source'] == AuditSource.MCP
            assert discover_event['event_type'] == AuditEvent.MCP_Discover
            assert discover_event['object_name'] == mcp_gateway_name
            assert discover_event['outcome'] == AuditOutcome.OK

            # .. and there is no session on this path, so the session column stays empty.
            assert discover_event['sub_key'] == ''

        finally:
            # The gateway always goes back to its previous shape for the other tests.
            _set_audit_log_active(zato_server, gateway, False)

# ################################################################################################################################
# ################################################################################################################################
