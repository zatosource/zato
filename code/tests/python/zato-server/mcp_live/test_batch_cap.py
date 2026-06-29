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
from _constants import _demo_echo_service, _error_invalid_request, _jsonrpc_version

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# The maximum batch size configured on the server
_max_batch_size = 20

# The error message returned when the batch exceeds the maximum size
_expected_error_message = 'Invalid request: batch too large'

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

class TestBatchCap:
    """ Tests that the server rejects oversized JSON-RPC batch requests.
    """

    def test_oversized_batch_rejected(self, client:'MCPClient', session_id:'str') -> 'None':
        """ A batch with more than the configured max elements returns a single invalid-request error.
        """

        # Build a batch one element larger than the cap ..
        oversized_count = _max_batch_size + 1
        messages = []

        for idx in range(oversized_count):
            request_id = idx + 1
            message:'anydict' = {
                'jsonrpc': _jsonrpc_version,
                'method': 'tools/list',
                'id': request_id,
            }
            messages.append(message)

        # .. send the oversized batch ..
        response = client.jsonrpc_batch(messages, session_id=session_id)

        assert response.status_code == OK

        # .. the response must be a single error object, not an array ..
        data = response.json()
        assert isinstance(data, dict)
        assert 'error' in data

        # .. with the correct code and message.
        error = data['error']
        assert error['code'] == _error_invalid_request
        assert error['message'] == _expected_error_message

# ################################################################################################################################

    def test_oversized_batch_invokes_no_service(self, client:'MCPClient', session_id:'str') -> 'None':
        """ None of the member services in an oversized batch are invoked.
        """

        # Build a batch of tools/call requests that would invoke demo.echo,
        # exceeding the cap so none should execute ..
        oversized_count = _max_batch_size + 1
        messages = []

        for idx in range(oversized_count):
            request_id = idx + 1
            message:'anydict' = {
                'jsonrpc': _jsonrpc_version,
                'method': 'tools/call',
                'id': request_id,
                'params': {'name': _demo_echo_service, 'arguments': {'payload': 'test'}},
            }
            messages.append(message)

        # .. send the oversized batch ..
        response = client.jsonrpc_batch(messages, session_id=session_id)

        assert response.status_code == OK

        # .. the response must be a single error object (no per-element responses),
        # proving that no individual dispatch occurred.
        data = response.json()
        assert isinstance(data, dict)
        assert 'error' in data
        assert 'result' not in data

# ################################################################################################################################

    def test_batch_at_limit_succeeds(self, client:'MCPClient', session_id:'str') -> 'None':
        """ A batch of exactly the configured max elements is processed normally.
        """

        # Build a batch of exactly the cap size ..
        messages = []

        for idx in range(_max_batch_size):
            request_id = idx + 1
            message:'anydict' = {
                'jsonrpc': _jsonrpc_version,
                'method': 'tools/list',
                'id': request_id,
            }
            messages.append(message)

        # .. send the batch ..
        response = client.jsonrpc_batch(messages, session_id=session_id)

        assert response.status_code == OK

        # .. the response must be an array with one entry per request.
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == _max_batch_size

# ################################################################################################################################
# ################################################################################################################################
