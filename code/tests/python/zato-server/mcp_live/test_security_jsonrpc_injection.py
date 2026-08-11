# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from collections.abc import Iterator
from http.client import OK

# pytest
import pytest

# requests
import requests

# local
from _client import MCPClient
from _constants import _error_invalid_request, _jsonrpc_version

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# Size threshold for an oversized payload test
_oversized_payload_bytes = 1_100_000

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='function')
def client(zato_server:'any_') -> 'MCPClient':
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

class TestJSONRPCInjection:
    """ Tests for JSON-RPC envelope manipulation and edge cases.
    """

    def test_array_body_rejected_with_valid_session(self, client:'MCPClient', session_id:'str') -> 'None':
        """ An array body is rejected as one invalid request even when the session is valid -
        no element of it is ever dispatched.
        """

        messages = [
            {'jsonrpc': _jsonrpc_version, 'method': 'ping', 'id': 1},
            {'jsonrpc': _jsonrpc_version, 'method': 'nonexistent.method', 'id': 2},
        ]
        response = client.jsonrpc_array_body(messages, session_id=session_id)
        data = response.json()

        assert isinstance(data, dict)
        assert 'error' in data

        error = data['error']
        assert error['code'] == _error_invalid_request

# ################################################################################################################################

    def test_nested_jsonrpc_in_params_is_opaque(self, client:'MCPClient', session_id:'str') -> 'None':
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

        response = client.jsonrpc('tools/call', params=params, session_id=session_id)
        assert response.status_code == OK

        data = response.json()

        # .. the outer call should succeed, the nested object is just data.
        assert 'result' in data

# ################################################################################################################################

    def test_oversized_payload_rejected(self, client:'MCPClient') -> 'None':
        """ A payload larger than the 1 MiB server limit must be rejected, not crash.

        The Rust HTTP layer caps reads at MAX_REQUEST_SIZE (1 MiB), so an oversized
        body is truncated and never parses as valid JSON. The server may either drop
        the connection (request too large) or return a JSON-RPC parse error over
        HTTP 200. Both are valid rejections - what matters is that the server stays up.
        """

        large_data = b'x' * _oversized_payload_bytes

        # .. a dropped connection is itself a valid rejection of an oversized body ..
        try:
            response = client.jsonrpc_raw(large_data)
        except requests.exceptions.ConnectionError:
            return

        # .. otherwise the server must not have processed it as a successful request ..
        if response.status_code >= 400:
            return

        # .. at HTTP 200 the truncated body must surface as a JSON-RPC error, never a result.
        data = response.json()
        assert 'error' in data

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

    def test_array_body_rejected_without_session(self, client:'MCPClient') -> 'None':
        """ An array body sent with no session is rejected the same way.
        """

        messages = [
            {'jsonrpc': _jsonrpc_version, 'method': 'ping', 'id': 1},
        ]

        response = client.jsonrpc_array_body(messages)
        data = response.json()

        assert isinstance(data, dict)
        assert 'error' in data

        error = data['error']
        assert error['code'] == _error_invalid_request

# ################################################################################################################################
# ################################################################################################################################
