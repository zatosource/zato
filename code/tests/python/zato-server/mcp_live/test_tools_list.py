# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# local
from _client import MCPClient
from _constants import _demo_echo_service

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def client(zato_server:'dict') -> 'MCPClient':
    out = MCPClient(zato_server['mcp_url'])
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestToolsList:
    """ Tests for the MCP tools/list JSON-RPC method.
    """

    def test_tools_list_contains_demo_echo(self, client:'MCPClient') -> 'None':
        """ The tool registry must include demo.echo.
        """

        response = client.jsonrpc('tools/list')
        result = response.json()['result']
        tools = result['tools']

        # Collect all tool names ..
        tool_names = []

        for tool in tools:
            tool_names.append(tool['name'])

        # .. demo.echo must be among them.
        assert _demo_echo_service in tool_names

# ################################################################################################################################

    def test_each_tool_has_required_fields(self, client:'MCPClient') -> 'None':
        """ Every tool must have name, description, and inputSchema.
        """

        response = client.jsonrpc('tools/list')
        tools = response.json()['result']['tools']

        # Each tool must expose the three mandatory MCP fields ..
        for tool in tools:
            assert 'name' in tool
            assert 'description' in tool
            assert 'inputSchema' in tool

# ################################################################################################################################

    def test_demo_echo_has_description(self, client:'MCPClient') -> 'None':
        """ The demo.echo tool must have a non-empty description.
        """

        response = client.jsonrpc('tools/list')
        tools = response.json()['result']['tools']

        # Find demo.echo in the tool list ..
        for tool in tools:
            if tool['name'] == _demo_echo_service:
                echo_tool = tool
                break
        else:
            raise AssertionError(f'{_demo_echo_service} not found in tool list')

        assert echo_tool['description'] != ''

# ################################################################################################################################

    def test_pagination_with_cursor_zero(self, client:'MCPClient') -> 'None':
        """ Requesting tools/list with cursor 0 returns a valid page.
        """

        response = client.jsonrpc('tools/list', params={'cursor': '0'})
        result = response.json()['result']

        # The response must contain a tools array.
        assert 'tools' in result

# ################################################################################################################################

    def test_pagination_beyond_end(self, client:'MCPClient') -> 'None':
        """ A cursor value beyond the total tool count returns an empty page with no nextCursor.
        """

        response = client.jsonrpc('tools/list', params={'cursor': '99999'})
        result = response.json()['result']

        # Beyond the end, the tools list must be empty
        # and there must be no nextCursor.
        assert result['tools'] == []
        assert 'nextCursor' not in result

# ################################################################################################################################
# ################################################################################################################################
