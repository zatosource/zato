# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# local
from _client import MCPClient
from _constants import _demo_echo_service, _error_method_not_found, _zato_internal_prefix

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def client(zato_server:'anydict') -> 'MCPClient':
    out = MCPClient(zato_server['mcp_url'], auth=zato_server['mcp_auth'])

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestACL:
    """ Tests for access control list enforcement on MCP channels.
    """

    def test_internal_service_rejected(self, client:'MCPClient') -> 'None':
        """ Calling a zato.* internal service returns tool-not-found.
        """

        params = {'name': 'zato.ping', 'arguments': {}}
        response = client.jsonrpc('tools/call', params=params)
        data = response.json()

        assert 'error' in data

        error = data['error']
        assert error['code'] == _error_method_not_found

# ################################################################################################################################

    def test_unlisted_service_rejected(self, client:'MCPClient') -> 'None':
        """ Calling a service not in the channel's allow list returns tool-not-found.
        """

        params = {'name': 'my.private.service', 'arguments': {}}
        response = client.jsonrpc('tools/call', params=params)
        data = response.json()

        assert 'error' in data

        error = data['error']
        assert error['code'] == _error_method_not_found

# ################################################################################################################################

    def test_tools_list_has_no_internal_services(self, client:'MCPClient') -> 'None':
        """ The tools/list response must not include any zato.* internal services.
        """

        response = client.jsonrpc('tools/list')
        json_body = response.json()
        result = json_body['result']
        tools = result['tools']

        # No tool name should start with the zato. prefix.
        for tool in tools:
            tool_name = tool['name']
            assert not tool_name.startswith(_zato_internal_prefix), \
                f'Internal service exposed in tools/list: {tool_name}'

# ################################################################################################################################

    def test_tools_list_only_shows_allow_listed_services(self, client:'MCPClient') -> 'None':
        """ The tools/list response must only show services from the channel's allow list.
        """

        response = client.jsonrpc('tools/list')
        json_body = response.json()
        result = json_body['result']
        tools = result['tools']

        # The default channel allows only demo.echo ..
        tool_names = []

        for tool in tools:
            tool_names.append(tool['name'])

        assert _demo_echo_service in tool_names

        # .. and no other services should be present.
        assert len(tool_names) == 1

# ################################################################################################################################
# ################################################################################################################################
