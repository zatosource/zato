# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from collections.abc import Iterator
from http.client import BAD_REQUEST, OK
from uuid import uuid4

# pytest
import pytest

# local
from _client import MCPClient
from _constants import _error_invalid_request

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

@pytest.fixture(scope='function')
def client_b(zato_server:'any_') -> 'MCPClient':
    out = MCPClient(zato_server['mcp_url'], auth=zato_server['mcp_auth_b'])
    return out

# ################################################################################################################################

@pytest.fixture(scope='function')
def session_id(client:'MCPClient') -> 'Iterator[str]':
    initialize_result = client.initialize()
    out = initialize_result.session_id

    yield out

    _ = client.delete_session(session_id=out)

# ################################################################################################################################
# ################################################################################################################################

class TestSessionValidation:
    """ Tests that session IDs cannot be forged, reused, or enumerated.
    """

    def test_forged_session_id_rejected(self, client:'MCPClient') -> 'None':
        """ A forged session ID with valid UUID format must be rejected with 400.
        """

        session_uuid = uuid4()
        forged_id = f'mcp{session_uuid.hex}'
        response = client.jsonrpc('ping', session_id=forged_id)

        assert response.status_code == BAD_REQUEST

# ################################################################################################################################

    def test_deleted_session_cannot_be_reused(self, client:'MCPClient') -> 'None':
        """ A deleted session ID must not be accepted for subsequent requests.
        """

        # Create and then delete a session ..
        initialize_result = client.initialize()
        session_id = initialize_result.session_id

        _ = client.delete_session(session_id)

        # .. trying to use the deleted session should return 400.
        response = client.jsonrpc('ping', session_id=session_id)

        assert response.status_code == BAD_REQUEST

# ################################################################################################################################

    def test_session_id_enumeration(self, client:'MCPClient') -> 'None':
        """ Iterating through sequential UUIDs must all be rejected as 400.
        """

        for _ in range(_enumeration_attempts):
            session_uuid = uuid4()
            guessed_id = f'mcp{session_uuid.hex}'
            response = client.jsonrpc('ping', session_id=guessed_id)

            assert response.status_code == BAD_REQUEST

# ################################################################################################################################

    def test_empty_session_id_header(self, client:'MCPClient') -> 'None':
        """ An empty session ID header must produce a defined response.
        """

        response = client.jsonrpc('ping', session_id='')

        # .. empty string is not a valid session, so the request is a protocol error.
        assert response.status_code == BAD_REQUEST

# ################################################################################################################################
# ################################################################################################################################

class TestSessionCredentialValidation:
    """ Tests that sessions enforce credential validation.
    """

    def test_request_rejected_invalid_session_credential(self, client:'MCPClient', client_b:'MCPClient', session_id:'str') -> 'None':
        """ A request with a session credential that does not match is rejected with 400.
        """

        # Send a request using a session that was created with a different credential ..
        response = client_b.jsonrpc('tools/list', session_id=session_id)

        assert response.status_code == BAD_REQUEST

        # .. the response must contain a JSON-RPC error.
        body = response.json()
        error = body['error']

        assert error['code'] == _error_invalid_request

# ################################################################################################################################

    def test_delete_rejected_invalid_session_credential(self, client:'MCPClient', client_b:'MCPClient', session_id:'str') -> 'None':
        """ A DELETE with a session credential that does not match returns 400 and the session stays valid.
        """

        # Attempt to delete the session using a credential that did not create it ..
        response = client_b.delete_session(session_id=session_id)

        assert response.status_code == BAD_REQUEST

        # .. the session must still be valid for the correct credential.
        ping_response = client.jsonrpc('ping', session_id=session_id)

        assert ping_response.status_code == OK

# ################################################################################################################################

    def test_request_accepted_valid_session_credential(self, client:'MCPClient', session_id:'str') -> 'None':
        """ A request with the correct session credential succeeds.
        """

        response = client.jsonrpc('ping', session_id=session_id)

        assert response.status_code == OK

        body = response.json()
        assert 'result' in body

# ################################################################################################################################
# ################################################################################################################################
