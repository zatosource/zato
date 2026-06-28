# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import BAD_REQUEST

# pytest
import pytest

# local
from _client import MCPClient
from _constants import _demo_echo_service, _error_invalid_request

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def client(zato_server:'any_') -> 'MCPClient':
    out = MCPClient(zato_server['mcp_url'], auth=zato_server['mcp_auth'])

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSessionRequired:
    """ Tests that every method other than initialize requires a valid session.
    """

    def test_tools_call_without_session_id_rejected(self, client:'MCPClient') -> 'None':
        """ A tools/call sent with no Mcp-Session-Id is rejected with a protocol error
        and the target service is never invoked.
        """

        # Send a tools/call without ever calling initialize, so no session header is present ..
        params = {'name': _demo_echo_service, 'arguments': {'message': 'hello'}}
        response = client.jsonrpc('tools/call', params=params)

        # .. the session gate must reject it as a protocol error, not an auth error ..
        assert response.status_code == BAD_REQUEST

        # .. the body must carry the canonical JSON-RPC invalid-request error ..
        data = response.json()
        assert 'error' in data

        error = data['error']
        assert error['code'] == _error_invalid_request

        # .. and the service must never have run, so no successful result is present.
        assert 'result' not in data

# ################################################################################################################################
# ################################################################################################################################
