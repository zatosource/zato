# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from collections.abc import Iterator

# pytest
import pytest

# local
from _client import MCPClient
from _constants import _demo_echo_service, _error_method_not_found, _raise_service, _zato_internal_prefix

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='function')
def client(zato_server:'anydict') -> 'MCPClient':
    out = MCPClient(zato_server['mcp_url'], auth=zato_server['mcp_auth'])
    return out

# ################################################################################################################################

@pytest.fixture(scope='function')
def session_id(client:'MCPClient') -> 'Iterator[str]':
    out = client.initialize().session_id

    yield out

    _ = client.delete_session(session_id=out)

# ################################################################################################################################
# ################################################################################################################################

class TestACL:
    """ Tests for access control list enforcement on MCP gateways.
    """

    def test_internal_service_rejected(self, client:'MCPClient', session_id:'str') -> 'None':
        """ Calling a zato.* internal service returns tool-not-found.
        """

        params = {'name': 'zato.ping', 'arguments': {}}
        response = client.jsonrpc('tools/call', params=params, session_id=session_id)
        data = response.json()

        assert 'error' in data

        error = data['error']
        assert error['code'] == _error_method_not_found

# ################################################################################################################################

    def test_unlisted_service_rejected(self, client:'MCPClient', session_id:'str') -> 'None':
        """ Calling a service not in the gateway's allow list returns tool-not-found.
        """

        params = {'name': 'my.private.service', 'arguments': {}}
        response = client.jsonrpc('tools/call', params=params, session_id=session_id)
        data = response.json()

        assert 'error' in data

        error = data['error']
        assert error['code'] == _error_method_not_found

# ################################################################################################################################

    def test_tools_list_has_no_internal_services(self, client:'MCPClient', session_id:'str') -> 'None':
        """ The tools/list response must not include any zato.* internal services.
        """

        response = client.jsonrpc('tools/list', session_id=session_id)
        json_body = response.json()
        result = json_body['result']
        tools = result['tools']

        # No tool name should start with the zato. prefix.
        for tool in tools:
            tool_name = tool['name']
            assert not tool_name.startswith(_zato_internal_prefix), \
                f'Internal service exposed in tools/list: {tool_name}'

# ################################################################################################################################

    def test_tools_list_only_shows_allow_listed_services(self, client:'MCPClient', session_id:'str') -> 'None':
        """ The tools/list response must only show services from the gateway's allow list.
        """

        response = client.jsonrpc('tools/list', session_id=session_id)
        json_body = response.json()
        result = json_body['result']
        tools = result['tools']

        # The default gateway allows demo.echo and test.raise ..
        tool_names = []

        for tool in tools:
            tool_names.append(tool['name'])

        assert _demo_echo_service in tool_names
        assert _raise_service in tool_names

        # .. and no other services should be present.
        assert len(tool_names) == 2

# ################################################################################################################################
# ################################################################################################################################
