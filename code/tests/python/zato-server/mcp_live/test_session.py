# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import NOT_FOUND, OK

# pytest
import pytest

# local
from _client import MCPClient

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def client(zato_server:'dict') -> 'MCPClient':
    out = MCPClient(zato_server['mcp_url'])
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSession:
    """ Tests for MCP session lifecycle: create, validate, delete, and invalid.
    """

    def test_session_id_works_for_subsequent_requests(self, client:'MCPClient') -> 'None':
        """ A session ID obtained from initialize can be used for tools/list.
        """

        # Initialize to get a session ID ..
        _, session_id = client.initialize()

        # .. use it for a tools/list request.
        response = client.jsonrpc('tools/list', session_id=session_id)
        data = response.json()

        assert response.status_code == OK
        assert 'result' in data

# ################################################################################################################################

    def test_bogus_session_id_returns_not_found(self, client:'MCPClient') -> 'None':
        """ A bogus session ID returns 404.
        """

        response = client.jsonrpc('ping', session_id='not-a-real-session')

        assert response.status_code == NOT_FOUND

# ################################################################################################################################

    def test_delete_valid_session_returns_ok(self, client:'MCPClient') -> 'None':
        """ Deleting an existing session returns 200.
        """

        # Create a session ..
        _, session_id = client.initialize()

        # .. then delete it.
        response = client.delete_session(session_id=session_id)

        assert response.status_code == OK

# ################################################################################################################################

    def test_delete_same_session_twice_returns_not_found(self, client:'MCPClient') -> 'None':
        """ Deleting an already-deleted session returns 404.
        """

        # Create and delete a session ..
        _, session_id = client.initialize()
        _ = client.delete_session(session_id=session_id)

        # .. deleting it again must return 404.
        response = client.delete_session(session_id=session_id)

        assert response.status_code == NOT_FOUND

# ################################################################################################################################

    def test_request_with_deleted_session_returns_not_found(self, client:'MCPClient') -> 'None':
        """ A request with a deleted session ID returns 404.
        """

        # Create and delete a session ..
        _, session_id = client.initialize()
        _ = client.delete_session(session_id=session_id)

        # .. a subsequent request with that session ID must fail.
        response = client.jsonrpc('ping', session_id=session_id)

        assert response.status_code == NOT_FOUND

# ################################################################################################################################

    def test_ping_without_session_id_succeeds(self, client:'MCPClient') -> 'None':
        """ Ping without a session ID header succeeds (session is optional).
        """

        response = client.jsonrpc('ping')

        assert response.status_code == OK

        data = response.json()
        assert 'result' in data

# ################################################################################################################################
# ################################################################################################################################
