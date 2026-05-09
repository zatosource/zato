# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK

# pytest
import pytest

# requests
import requests

# local
from _client import MCPClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# Content type for SSE streams
_content_type_sse = 'text/event-stream'

# Content type for regular JSON responses
_content_type_json = 'application/json'

# Timeout in seconds for SSE requests
_sse_request_timeout = 30

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def client(zato_server:'any_') -> 'MCPClient':
    out = MCPClient(zato_server['mcp_url'])
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSSESecurity:
    """ Tests for SSE-specific security concerns.
    """

    def test_sse_accept_with_short_lived_service_returns_json(self, client:'MCPClient') -> 'None':
        """ When Accept: text/event-stream is sent but the service is short-lived,
        the server should still return a valid response (server chooses format).
        """

        # Initialize a session first ..
        init_result = client.initialize()
        session_id = init_result.session_id

        # .. send a tools/call with SSE Accept header ..
        headers = {
            'Content-Type': 'application/json',
            'Accept': _content_type_sse,
            'Mcp-Session-Id': session_id,
        }

        body = {
            'jsonrpc': '2.0',
            'method': 'tools/call',
            'id': 1,
            'params': {'name': 'demo.echo', 'arguments': {'message': 'hello'}},
        }

        response = requests.post(
            client.mcp_url,
            json=body,
            headers=headers,
            timeout=_sse_request_timeout,
        )

        # .. the response should be successful regardless of content type.
        assert response.status_code == OK

# ################################################################################################################################

    def test_multiple_sse_streams_from_same_session(self, client:'MCPClient') -> 'None':
        """ Multiple simultaneous requests from the same session must not interfere.
        """

        # Initialize a session ..
        init_result = client.initialize()
        session_id = init_result.session_id

        # .. send two independent tools/call requests with the same session ..
        response_first = client.jsonrpc(
            'tools/call',
            params={'name': 'demo.echo', 'arguments': {'message': 'first'}},
            session_id=session_id,
            request_id=1,
        )

        response_second = client.jsonrpc(
            'tools/call',
            params={'name': 'demo.echo', 'arguments': {'message': 'second'}},
            session_id=session_id,
            request_id=2,
        )

        # .. both should succeed independently.
        assert response_first.status_code == OK
        assert response_second.status_code == OK

# ################################################################################################################################
# ################################################################################################################################
