# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import uuid
from http.client import BAD_REQUEST, NOT_FOUND

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

# Number of sequential UUIDs to try during enumeration test
_enumeration_attempts = 10

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='function')
def client(zato_server:'any_') -> 'MCPClient':
    out = MCPClient(zato_server['mcp_url'], auth=zato_server['mcp_auth'])
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSessionValidation:
    """ Tests that session IDs cannot be forged, reused, or enumerated.
    """

    def test_forged_session_id_rejected(self, client:'MCPClient') -> 'None':
        """ A forged session ID with valid UUID format must be rejected with 404.
        """

        forged_id = f'mcp{uuid.uuid4().hex}'
        response = client.jsonrpc('ping', session_id=forged_id)

        assert response.status_code == NOT_FOUND

# ################################################################################################################################

    def test_deleted_session_cannot_be_reused(self, client:'MCPClient') -> 'None':
        """ A deleted session ID must not be accepted for subsequent requests.
        """

        # Create and then delete a session ..
        initialize_result = client.initialize()
        session_id = initialize_result.session_id

        _ = client.delete_session(session_id)

        # .. trying to use the deleted session should return 404.
        response = client.jsonrpc('ping', session_id=session_id)

        assert response.status_code == NOT_FOUND

# ################################################################################################################################

    def test_session_id_enumeration(self, client:'MCPClient') -> 'None':
        """ Iterating through sequential UUIDs must all be rejected as 404 (not found).
        """

        for _ in range(_enumeration_attempts):
            guessed_id = f'mcp{uuid.uuid4().hex}'
            response = client.jsonrpc('ping', session_id=guessed_id)

            assert response.status_code == NOT_FOUND

# ################################################################################################################################

    def test_empty_session_id_header(self, client:'MCPClient') -> 'None':
        """ An empty session ID header must produce a defined response.
        """

        response = client.jsonrpc('ping', session_id='')

        # .. empty string is not a valid session, so the request is a protocol error.
        assert response.status_code == BAD_REQUEST

# ################################################################################################################################
# ################################################################################################################################
