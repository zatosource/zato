# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK

# pytest
import pytest

# local
from _client import MCPClient
from _constants import _error_method_not_found, _jsonrpc_version

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# Maximum number of messages in a large batch test
_large_batch_size = 1000

# Size threshold for an oversized payload test
_oversized_payload_bytes = 1_100_000

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def client(zato_server:'any_') -> 'MCPClient':
    out = MCPClient(zato_server['mcp_url'])
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestJSONRPCInjection:
    """ Tests for JSON-RPC envelope manipulation and edge cases.
    """

    def test_batch_with_mixed_valid_invalid(self, client:'MCPClient') -> 'None':
        """ A batch mixing valid and invalid methods must handle each independently.
        """

        messages = [
            {'jsonrpc': _jsonrpc_version, 'method': 'ping', 'id': 1},
            {'jsonrpc': _jsonrpc_version, 'method': 'nonexistent.method', 'id': 2},
        ]
        response = client.jsonrpc_batch(messages)
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 2

        # .. find response for each id ..
        response_by_id = {}

        for item in data:
            response_by_id[item['id']] = item

        # .. ping should succeed, nonexistent should error.
        assert 'result' in response_by_id[1]
        assert 'error' in response_by_id[2]
        assert response_by_id[2]['error']['code'] == _error_method_not_found

# ################################################################################################################################

    def test_nested_jsonrpc_in_params_is_opaque(self, client:'MCPClient') -> 'None':
        """ Nested JSON-RPC objects inside params must be treated as opaque data.
        """

        nested_payload = {
            'jsonrpc': _jsonrpc_version,
            'method': 'initialize',
            'id': 999,
        }

        params = {
            'name': 'demo.echo',
            'arguments': {'nested': nested_payload},
        }

        response = client.jsonrpc('tools/call', params=params)
        assert response.status_code == OK

        data = response.json()

        # .. the outer call should succeed, the nested object is just data.
        assert 'result' in data

# ################################################################################################################################

    def test_oversized_payload_rejected(self, client:'MCPClient') -> 'None':
        """ A payload larger than 1MB must be rejected.
        """

        large_data = b'x' * _oversized_payload_bytes
        response = client.jsonrpc_raw(large_data)

        # .. the server should reject it, not crash.
        assert response.status_code >= 400

# ################################################################################################################################

    def test_duplicate_id_fields(self, client:'MCPClient') -> 'None':
        """ A message with duplicate id fields must produce a defined response.
        """

        # JSON spec says last key wins for duplicates
        raw_body = b'{"jsonrpc":"2.0","method":"ping","id":1,"id":2}'
        response = client.jsonrpc_raw(raw_body)
        data = response.json()

        # .. it should process successfully with whichever id the parser chose.
        assert 'result' in data or 'error' in data

# ################################################################################################################################

    def test_large_batch_all_processed(self, client:'MCPClient') -> 'None':
        """ A batch with many messages must process all of them.
        """

        messages = []

        for request_idx in range(_large_batch_size):
            message = {
                'jsonrpc': _jsonrpc_version,
                'method': 'ping',
                'id': request_idx,
            }
            messages.append(message)

        response = client.jsonrpc_batch(messages)
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == _large_batch_size

# ################################################################################################################################
# ################################################################################################################################
