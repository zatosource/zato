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
from _client import MCPClient, _session_header
from _constants import _error_invalid_request

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# The default session cap per sec_def per channel
_default_max_sessions = 100

# The generic error message returned by the server for session-related rejections
_expected_error_message = 'Bad request'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='function')
def client(zato_server:'any_') -> 'MCPClient':
    out = MCPClient(zato_server['mcp_url'], auth=zato_server['mcp_auth'])

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSessionCap:
    """ Tests that the server enforces the per-identity session cap.
    """

    def test_initialize_past_cap_rejected(self, client:'MCPClient') -> 'None':
        """ After creating the maximum number of sessions, the next initialize is rejected.
        """

        # Fill the cap with successful sessions ..
        for _ in range(_default_max_sessions):
            result = client.initialize()
            assert result.response.status_code == OK

        # .. the next initialize must be rejected with a generic error ..
        response = client.jsonrpc('initialize', params={
            'protocolVersion': '2025-11-05',
            'capabilities': {},
            'clientInfo': {'name': 'zato-mcp-test', 'version': '1.0'},
        })

        assert response.status_code == OK

        body = response.json()
        error = body['error']

        assert error['code'] == _error_invalid_request
        assert error['message'] == _expected_error_message

        # .. and no session header must be present in the rejected response.
        assert _session_header not in response.headers

# ################################################################################################################################
# ################################################################################################################################
