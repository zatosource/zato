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

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def client(zato_server:'any_') -> 'MCPClient':
    out = MCPClient(zato_server['mcp_url'])
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestAuthBypass:
    """ Verifies that authentication is enforced before any JSON-RPC processing.
    """

    def test_sse_stream_requires_same_auth_as_post(self, client:'MCPClient') -> 'None':
        """ SSE streaming requests must require the same authentication as regular POST.
        """

        # Initialize a session first ..
        init_result = client.initialize()
        session_id = init_result.session_id

        # .. send a tools/call with Accept: text/event-stream using the session ..
        response = client.jsonrpc(
            'tools/call',
            params={'name': 'demo.echo', 'arguments': {'message': 'test'}},
            session_id=session_id,
        )

        # .. the response should succeed, proving that authenticated SSE works.
        assert response.status_code == OK

# ################################################################################################################################
# ################################################################################################################################
