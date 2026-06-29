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
from _constants import _demo_echo_service

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

class TestToolsList:
    """ Tests for the MCP tools/list JSON-RPC method.
    """

    def test_tools_list_contains_demo_echo(self, client:'MCPClient', session_id:'str') -> 'None':
        """ The tool registry must include demo.echo.
        """

        response = client.jsonrpc('tools/list', session_id=session_id)
        json_body = response.json()
        result = json_body['result']
        tools = result['tools']

        # Collect all tool names ..
        tool_names = []

        for tool in tools:
            tool_names.append(tool['name'])

        # .. demo.echo must be among them.
        assert _demo_echo_service in tool_names

# ################################################################################################################################

    def test_each_tool_has_required_fields(self, client:'MCPClient', session_id:'str') -> 'None':
        """ Every tool must have name, description, and inputSchema.
        """

        response = client.jsonrpc('tools/list', session_id=session_id)
        json_body = response.json()
        result = json_body['result']
        tools = result['tools']

        # Each tool must expose the three mandatory MCP fields ..
        for tool in tools:
            assert 'name' in tool
            assert 'description' in tool
            assert 'inputSchema' in tool

# ################################################################################################################################

    def test_demo_echo_has_description(self, client:'MCPClient', session_id:'str') -> 'None':
        """ The demo.echo tool must have a non-empty description.
        """

        response = client.jsonrpc('tools/list', session_id=session_id)
        json_body = response.json()
        result = json_body['result']
        tools = result['tools']

        # Find demo.echo in the tool list ..
        for tool in tools:
            if tool['name'] == _demo_echo_service:
                echo_tool = tool
                break
        else:
            raise AssertionError(f'{_demo_echo_service} not found in tool list')

        assert echo_tool['description'] != ''

# ################################################################################################################################

    def test_tools_list_returns_valid_schema(self, client:'MCPClient', session_id:'str') -> 'None':
        """ Every tool's inputSchema must be a valid JSON Schema object with a type field.
        """

        response = client.jsonrpc('tools/list', session_id=session_id)
        json_body = response.json()
        result = json_body['result']
        tools = result['tools']

        for tool in tools:
            schema = tool['inputSchema']

            # Each inputSchema must be a dict with at least a 'type' key ..
            assert isinstance(schema, dict), f'Tool "{tool["name"]}" inputSchema is not a dict'
            assert 'type' in schema, f'Tool "{tool["name"]}" inputSchema missing "type"'
            assert schema['type'] == 'object', f'Tool "{tool["name"]}" inputSchema type is not "object"'

# ################################################################################################################################

    def test_pagination_with_cursor_zero(self, client:'MCPClient', session_id:'str') -> 'None':
        """ Requesting tools/list with cursor 0 returns a valid page.
        """

        response = client.jsonrpc('tools/list', params={'cursor': '0'}, session_id=session_id)
        json_body = response.json()
        result = json_body['result']

        # The response must contain a tools array.
        assert 'tools' in result

# ################################################################################################################################

    def test_pagination_beyond_end(self, client:'MCPClient', session_id:'str') -> 'None':
        """ A cursor value beyond the total tool count returns an empty page with no nextCursor.
        """

        response = client.jsonrpc('tools/list', params={'cursor': '99999'}, session_id=session_id)
        json_body = response.json()
        result = json_body['result']

        # Beyond the end, the tools list must be empty
        # and there must be no nextCursor.
        assert result['tools'] == []
        assert 'nextCursor' not in result

# ################################################################################################################################
# ################################################################################################################################
