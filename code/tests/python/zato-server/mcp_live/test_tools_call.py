# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads

# pytest
import pytest

# local
from _client import MCPClient
from _constants import _demo_echo_service, _error_method_not_found

# ################################################################################################################################
# ################################################################################################################################

# A realistic but non-existent service name for testing tool-not-found errors
_nonexistent_service = 'billing.generate-invoice'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def client(zato_server:'dict') -> 'MCPClient':
    out = MCPClient(zato_server['mcp_url'])
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestToolsCall:
    """ Tests for the MCP tools/call JSON-RPC method.
    """

    def test_call_echo_with_arguments(self, client:'MCPClient') -> 'None':
        """ Calling demo.echo with arguments returns the echoed data.
        """

        arguments = {'hello': 'world'}
        params = {'name': _demo_echo_service, 'arguments': arguments}

        response = client.jsonrpc('tools/call', params=params)
        result = response.json()['result']

        # The result must contain content with the echoed data ..
        content = result['content']
        assert len(content) >= 1

        # .. extract the text from the first content element and parse it.
        first_content = content[0]
        text = first_content['text']
        parsed = loads(text)

        assert parsed['hello'] == 'world'

# ################################################################################################################################

    def test_call_echo_with_empty_arguments(self, client:'MCPClient') -> 'None':
        """ Calling demo.echo with empty arguments succeeds.
        """

        params = {'name': _demo_echo_service, 'arguments': {}}

        response = client.jsonrpc('tools/call', params=params)
        data = response.json()

        # Must be a success response without isError ..
        assert 'result' in data
        assert 'isError' not in data['result']

# ################################################################################################################################

    def test_call_nonexistent_tool(self, client:'MCPClient') -> 'None':
        """ Calling a tool that does not exist returns a method-not-found error.
        """

        params = {'name': _nonexistent_service, 'arguments': {}}

        response = client.jsonrpc('tools/call', params=params)
        data = response.json()

        # The response must be an error with the method-not-found code.
        assert 'error' in data
        assert data['error']['code'] == _error_method_not_found

# ################################################################################################################################
# ################################################################################################################################
