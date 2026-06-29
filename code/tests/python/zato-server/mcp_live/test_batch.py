# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import NO_CONTENT, OK

# pytest
import pytest

# local
from _client import MCPClient
from _constants import _error_invalid_request, _jsonrpc_version

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
# ################################################################################################################################

class TestBatch:
    """ Tests for JSON-RPC batch request handling.
    """

    def test_batch_with_initialize_rejected(self, client:'MCPClient') -> 'None':
        """ The MCP spec says initialize MUST NOT appear in a batch.
        """

        messages = [
            {'jsonrpc': _jsonrpc_version, 'method': 'initialize', 'id': 1},
            {'jsonrpc': _jsonrpc_version, 'method': 'notifications/initialized'},
        ]

        response = client.jsonrpc_batch(messages)

        assert response.status_code == OK

        data = response.json()
        assert 'error' in data
        assert data['error']['code'] == _error_invalid_request

# ################################################################################################################################

    def test_empty_batch_returns_error(self, client:'MCPClient') -> 'None':
        """ An empty batch array returns an invalid-request error.
        """

        response = client.jsonrpc_batch([])

        assert response.status_code == OK

        data = response.json()
        assert 'error' in data

        error = data['error']
        assert error['code'] == _error_invalid_request

# ################################################################################################################################

    def test_all_notifications_returns_no_content(self, client:'MCPClient') -> 'None':
        """ A batch of only notifications returns 204 No Content.
        """

        messages = [
            {'jsonrpc': _jsonrpc_version, 'method': 'notifications/initialized'},
            {'jsonrpc': _jsonrpc_version, 'method': 'notifications/initialized'},
        ]

        response = client.jsonrpc_batch(messages)

        assert response.status_code == NO_CONTENT

# ################################################################################################################################

    def test_batch_with_two_requests(self, client:'MCPClient') -> 'None':
        """ A batch with two requests returns two responses.
        """

        messages = [
            {'jsonrpc': _jsonrpc_version, 'method': 'ping', 'id': 10},
            {'jsonrpc': _jsonrpc_version, 'method': 'ping', 'id': 20},
        ]

        response = client.jsonrpc_batch(messages)

        assert response.status_code == OK

        # The batch response must contain exactly two elements ..
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

        # .. collect the IDs to verify both responses are present.
        response_ids:'set[int]' = set()

        for item in data:
            response_ids.add(item['id'])

        assert 10 in response_ids
        assert 20 in response_ids

# ################################################################################################################################
# ################################################################################################################################
