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
from _constants import _error_invalid_params, _error_invalid_request, _error_method_not_found, _error_parse

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def client(zato_server:'dict') -> 'MCPClient':
    out = MCPClient(zato_server['mcp_url'])
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestErrors:
    """ Tests for JSON-RPC error handling.
    """

    def test_non_json_body_returns_parse_error(self, client:'MCPClient') -> 'None':
        """ Sending non-JSON bytes returns a parse error.
        """

        response = client.jsonrpc_raw(b'<html>Not Found</html>')
        data = response.json()

        assert 'error' in data
        assert data['error']['code'] == _error_parse

# ################################################################################################################################

    def test_missing_jsonrpc_field_returns_invalid_request(self, client:'MCPClient') -> 'None':
        """ A request without the jsonrpc field returns an invalid-request error.
        """

        response = client.jsonrpc_raw(b'{"method": "ping", "id": 1}')
        data = response.json()

        assert 'error' in data
        assert data['error']['code'] == _error_invalid_request

# ################################################################################################################################

    def test_missing_method_field_returns_invalid_request(self, client:'MCPClient') -> 'None':
        """ A request without the method field returns an invalid-request error.
        """

        response = client.jsonrpc_raw(b'{"jsonrpc": "2.0", "id": 1}')
        data = response.json()

        assert 'error' in data
        assert data['error']['code'] == _error_invalid_request

# ################################################################################################################################

    def test_wrong_jsonrpc_version_returns_invalid_request(self, client:'MCPClient') -> 'None':
        """ A request with jsonrpc version 1.0 returns an invalid-request error.
        """

        response = client.jsonrpc_raw(b'{"jsonrpc": "1.0", "method": "ping", "id": 1}')
        data = response.json()

        assert 'error' in data
        assert data['error']['code'] == _error_invalid_request

# ################################################################################################################################

    def test_unknown_method_returns_method_not_found(self, client:'MCPClient') -> 'None':
        """ An unknown method returns a method-not-found error.
        """

        response = client.jsonrpc('resources/list')
        data = response.json()

        assert 'error' in data
        assert data['error']['code'] == _error_method_not_found

# ################################################################################################################################

    def test_tools_call_without_name_returns_invalid_params(self, client:'MCPClient') -> 'None':
        """ Calling tools/call without the name parameter returns an invalid-params error.
        """

        response = client.jsonrpc('tools/call', params={})
        data = response.json()

        assert 'error' in data
        assert data['error']['code'] == _error_invalid_params

# ################################################################################################################################

    def test_ping_returns_empty_result(self, client:'MCPClient') -> 'None':
        """ Ping returns an empty result object.
        """

        response = client.jsonrpc('ping')

        assert response.status_code == OK

        data = response.json()
        assert data['result'] == {}

# ################################################################################################################################
# ################################################################################################################################
