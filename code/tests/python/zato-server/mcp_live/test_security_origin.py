# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from collections.abc import Iterator
from http.client import FORBIDDEN, OK

# pytest
import pytest

# local
from _client import MCPClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# An Origin that is not on any gateway's allow list
_disallowed_origin = 'https://evil.example.com'

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

class TestOriginValidation:
    """ Tests that the server validates the Origin header to prevent DNS rebinding attacks.
    """

    def test_request_with_disallowed_origin_rejected(self, client:'MCPClient', session_id:'str') -> 'None':
        """ A request carrying an Origin that is not on the allow list is rejected with 403.
        """

        response = client.jsonrpc(
            'ping',
            session_id=session_id,
            extra_headers={'Origin': _disallowed_origin},
        )

        assert response.status_code == FORBIDDEN

# ################################################################################################################################

    def test_request_without_origin_allowed(self, client:'MCPClient', session_id:'str') -> 'None':
        """ A request that carries no Origin header is processed normally,
        proving the rejection above comes from the Origin check.
        """

        response = client.jsonrpc('ping', session_id=session_id)

        assert response.status_code == OK

        body = response.json()
        assert 'result' in body

# ################################################################################################################################

    def test_initialize_with_disallowed_origin_rejected(self, client:'MCPClient') -> 'None':
        """ Even initialize, the one method that needs no session, is rejected
        when it carries a disallowed Origin.
        """

        params = {
            'protocolVersion': '2025-11-05',
            'capabilities': {},
            'clientInfo': {'name': 'zato-mcp-test', 'version': '1.0'},
        }

        response = client.jsonrpc(
            'initialize',
            params=params,
            extra_headers={'Origin': _disallowed_origin},
        )

        assert response.status_code == FORBIDDEN

# ################################################################################################################################
# ################################################################################################################################
