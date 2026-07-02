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

# local
from _client import MCPClient
from _constants import _error_invalid_params, _error_invalid_request, _error_method_not_found, _error_parse

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

class TestErrors:
    """ Tests for JSON-RPC error handling.
    """

    def test_non_json_body_returns_parse_error(self, client:'MCPClient') -> 'None':
        """ Sending non-JSON bytes returns a parse error.
        """

        response = client.jsonrpc_raw(b'<html>Not Found</html>')
        data = response.json()

        assert 'error' in data

        error = data['error']
        assert error['code'] == _error_parse

# ################################################################################################################################

    def test_missing_jsonrpc_field_returns_invalid_request(self, client:'MCPClient') -> 'None':
        """ A request without the jsonrpc field returns an invalid-request error.
        """

        response = client.jsonrpc_raw(b'{"method": "ping", "id": 1}')
        data = response.json()

        assert 'error' in data

        error = data['error']
        assert error['code'] == _error_invalid_request

# ################################################################################################################################

    def test_missing_method_field_returns_invalid_request(self, client:'MCPClient') -> 'None':
        """ A request without the method field returns an invalid-request error.
        """

        response = client.jsonrpc_raw(b'{"jsonrpc": "2.0", "id": 1}')
        data = response.json()

        assert 'error' in data

        error = data['error']
        assert error['code'] == _error_invalid_request

# ################################################################################################################################

    def test_wrong_jsonrpc_version_returns_invalid_request(self, client:'MCPClient') -> 'None':
        """ A request with jsonrpc version 1.0 returns an invalid-request error.
        """

        response = client.jsonrpc_raw(b'{"jsonrpc": "1.0", "method": "ping", "id": 1}')
        data = response.json()

        assert 'error' in data

        error = data['error']
        assert error['code'] == _error_invalid_request

# ################################################################################################################################

    def test_unknown_method_returns_method_not_found(self, client:'MCPClient', session_id:'str') -> 'None':
        """ An unknown method returns a method-not-found error.
        """

        response = client.jsonrpc('resources/list', session_id=session_id)
        data = response.json()

        assert 'error' in data

        error = data['error']
        assert error['code'] == _error_method_not_found

# ################################################################################################################################

    def test_tools_call_without_name_returns_invalid_params(self, client:'MCPClient', session_id:'str') -> 'None':
        """ Calling tools/call without the name parameter returns an invalid-params error.
        """

        response = client.jsonrpc('tools/call', params={}, session_id=session_id)
        data = response.json()

        assert 'error' in data

        error = data['error']
        assert error['code'] == _error_invalid_params

# ################################################################################################################################

    def test_ping_returns_empty_result(self, client:'MCPClient', session_id:'str') -> 'None':
        """ Ping returns an empty result object.
        """

        response = client.jsonrpc('ping', session_id=session_id)

        assert response.status_code == OK

        data = response.json()
        assert data['result'] == {}

# ################################################################################################################################

    def test_batch_with_non_dict_elements(self, client:'MCPClient', session_id:'str') -> 'None':
        """ A batch mixing non-dict elements with a valid request returns
        one error per invalid element and still processes the valid one.
        """

        raw_body = b'[1, "not a request", null, {"jsonrpc": "2.0", "method": "ping", "id": 4}]'
        response = client.jsonrpc_raw(raw_body, session_id=session_id)

        assert response.status_code == OK

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 4

        # The three non-dict elements must each report an invalid-request error ..
        for item in data[:3]:
            assert 'error' in item

            error = item['error']
            assert error['code'] == _error_invalid_request

        # .. and the valid ping must still succeed.
        ping_response = data[3]
        assert 'result' in ping_response
        assert ping_response['id'] == 4

# ################################################################################################################################

    def test_params_as_list_returns_invalid_params(self, client:'MCPClient', session_id:'str') -> 'None':
        """ A params field that is a list returns an invalid-params error.
        """

        raw_body = b'{"jsonrpc": "2.0", "method": "tools/list", "id": 1, "params": ["not", "an", "object"]}'
        response = client.jsonrpc_raw(raw_body, session_id=session_id)

        assert response.status_code == OK

        data = response.json()
        assert 'error' in data

        error = data['error']
        assert error['code'] == _error_invalid_params

# ################################################################################################################################

    def test_params_as_string_returns_invalid_params(self, client:'MCPClient', session_id:'str') -> 'None':
        """ A params field that is a string returns an invalid-params error.
        """

        raw_body = b'{"jsonrpc": "2.0", "method": "tools/call", "id": 1, "params": "name=demo.echo"}'
        response = client.jsonrpc_raw(raw_body, session_id=session_id)

        assert response.status_code == OK

        data = response.json()
        assert 'error' in data

        error = data['error']
        assert error['code'] == _error_invalid_params

# ################################################################################################################################

    def test_initialize_params_as_number_returns_invalid_params(self, client:'MCPClient') -> 'None':
        """ Initialize with a numeric params field returns an invalid-params error
        and creates no session.
        """

        raw_body = b'{"jsonrpc": "2.0", "method": "initialize", "id": 1, "params": 123}'
        response = client.jsonrpc_raw(raw_body)

        assert response.status_code == OK

        data = response.json()
        assert 'error' in data

        error = data['error']
        assert error['code'] == _error_invalid_params

        # No session must have been created for the rejected initialize
        assert 'Mcp-Session-Id' not in response.headers

# ################################################################################################################################
# ################################################################################################################################
