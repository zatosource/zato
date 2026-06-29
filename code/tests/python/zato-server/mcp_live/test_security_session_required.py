# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import BAD_REQUEST, OK

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

# Protocol version that the server supports
_supported_protocol_version = '2025-11-05'

# Protocol version that the server does not support
_unsupported_protocol_version = '1999-01-01'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='function')
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

        # .. there must be an error field ..
        assert 'error' in data

        error = data['error']
        assert error['code'] == _error_invalid_request

        # .. and the service must never have run, so no successful result is present.
        assert 'result' not in data

# ################################################################################################################################

    def test_tools_list_without_session_id_rejected(self, client:'MCPClient') -> 'None':
        """ A tools/list sent with no Mcp-Session-Id is rejected with a protocol error.
        """

        # Send a tools/list without ever calling initialize, so no session header is present ..
        response = client.jsonrpc('tools/list')

        # .. the session gate must reject it as a protocol error, not an auth error ..
        assert response.status_code == BAD_REQUEST

        # .. the body must carry the canonical JSON-RPC invalid-request error ..
        data = response.json()

        # .. there must be an error field ..
        assert 'error' in data

        error = data['error']
        assert error['code'] == _error_invalid_request

        # .. and no tool listing is returned.
        assert 'result' not in data

# ################################################################################################################################

    def test_ping_without_session_id_rejected(self, client:'MCPClient') -> 'None':
        """ A ping sent with no Mcp-Session-Id is rejected with a protocol error.
        """

        # Send a ping without ever calling initialize, so no session header is present ..
        response = client.jsonrpc('ping')

        # .. the session gate must reject it as a protocol error ..
        assert response.status_code == BAD_REQUEST

        # .. the body must carry the canonical JSON-RPC invalid-request error ..
        data = response.json()

        # .. there must be an error field ..
        assert 'error' in data

        error = data['error']
        assert error['code'] == _error_invalid_request

        # .. and no result is returned.
        assert 'result' not in data

# ################################################################################################################################

    def test_initialize_without_session_id_succeeds(self, client:'MCPClient') -> 'None':
        """ Initialize with no Mcp-Session-Id returns 200 and a new session id in the response header.
        """

        # Send an initialize without any session header ..
        params = {
            'protocolVersion': _supported_protocol_version,
            'capabilities': {},
            'clientInfo': {'name': 'test', 'version': '1.0'},
        }
        response = client.jsonrpc('initialize', params=params)

        # .. it must succeed ..
        assert response.status_code == OK

        # .. and the response must contain a non-empty session id header.
        session_id = response.headers['Mcp-Session-Id']

        session_id_length = len(session_id)
        assert session_id_length > 0

# ################################################################################################################################

    def test_unknown_session_id_rejected(self, client:'MCPClient') -> 'None':
        """ A non-initialize request with a syntactically valid but unknown session id
        is rejected identically to the missing-header path.
        """

        # Use a plausible but never-issued session id ..
        fake_session_id = 'mcp00000000000000000000000000000000'
        response = client.jsonrpc('tools/list', session_id=fake_session_id)

        # .. the session gate must reject it ..
        assert response.status_code == BAD_REQUEST

        # .. with the canonical JSON-RPC invalid-request error ..
        data = response.json()

        # .. there must be an error field ..
        assert 'error' in data

        error = data['error']
        assert error['code'] == _error_invalid_request

        # .. and no result is returned.
        assert 'result' not in data

# ################################################################################################################################

    def test_new_session_after_delete(self, client:'MCPClient') -> 'None':
        """ After deleting a session, using the dead id returns 400,
        but a fresh initialize issues a new working session.
        """

        # Create a session and then delete it ..
        initialize_result = client.initialize()
        dead_session_id = initialize_result.session_id

        _ = client.delete_session(dead_session_id)

        # .. using the dead session id must fail ..
        params = {'name': _demo_echo_service, 'arguments': {'message': 'hi'}}
        response = client.jsonrpc('tools/call', params=params, session_id=dead_session_id)

        assert response.status_code == BAD_REQUEST

        # .. and the error must be the canonical invalid-request ..
        data = response.json()

        error = data['error']
        assert error['code'] == _error_invalid_request

        # .. but a fresh initialize must succeed and produce a new working session ..
        new_result = client.initialize()
        new_session_id = new_result.session_id

        new_session_id_length = len(new_session_id)
        assert new_session_id_length > 0
        assert new_session_id != dead_session_id

        # .. and the new session must work for subsequent requests.
        response = client.jsonrpc('tools/list', session_id=new_session_id)
        assert response.status_code == OK

# ################################################################################################################################

    def test_request_without_header_after_initialize_rejected(self, client:'MCPClient') -> 'None':
        """ After a successful initialize, a follow-up tools/call that omits
        the Mcp-Session-Id header is rejected.
        """

        # Establish a valid session first ..
        _ = client.initialize()

        # .. then send a tools/call without the session header ..
        params = {'name': _demo_echo_service, 'arguments': {'message': 'hi'}}
        response = client.jsonrpc('tools/call', params=params)

        # .. the session gate must reject it ..
        assert response.status_code == BAD_REQUEST

        # .. with the canonical JSON-RPC invalid-request error.
        data = response.json()

        error = data['error']
        assert error['code'] == _error_invalid_request

# ################################################################################################################################

    def test_initialize_unsupported_version_returns_server_version(self, client:'MCPClient') -> 'None':
        """ Initialize with an unsupported protocolVersion returns the server's version per spec.
        """

        # Send an initialize with a version the server does not support ..
        params = {
            'protocolVersion': _unsupported_protocol_version,
            'capabilities': {},
            'clientInfo': {'name': 'test', 'version': '1.0'},
        }
        response = client.jsonrpc('initialize', params=params)

        # .. it must succeed ..
        assert response.status_code == OK

        # .. the result must carry the server's own version.
        data = response.json()
        result = data['result']

        assert result['protocolVersion'] == _supported_protocol_version

# ################################################################################################################################

    def test_initialize_unsupported_version_creates_session(self, client:'MCPClient') -> 'None':
        """ Initialize with an unsupported protocolVersion still creates a session.
        """

        # Send an initialize with a version the server does not support ..
        params = {
            'protocolVersion': _unsupported_protocol_version,
            'capabilities': {},
            'clientInfo': {'name': 'test', 'version': '1.0'},
        }
        response = client.jsonrpc('initialize', params=params)

        # .. a session must have been created ..
        assert 'Mcp-Session-Id' in response.headers

# ################################################################################################################################

    def test_initialize_supported_protocol_version_echoed(self, client:'MCPClient') -> 'None':
        """ Initialize with the supported version returns 200 and echoes the negotiated protocolVersion.
        """

        # Send an initialize with the correct version ..
        params = {
            'protocolVersion': _supported_protocol_version,
            'capabilities': {},
            'clientInfo': {'name': 'test', 'version': '1.0'},
        }
        response = client.jsonrpc('initialize', params=params)

        # .. it must succeed ..
        assert response.status_code == OK

        # .. and the result must echo back the negotiated version.
        data = response.json()

        # .. there must be a result field ..
        assert 'result' in data

        result = data['result']
        assert result['protocolVersion'] == _supported_protocol_version

# ################################################################################################################################

    def test_mismatched_protocol_version_header_rejected(self, client:'MCPClient') -> 'None':
        """ A request whose MCP-Protocol-Version header disagrees with the session's
        negotiated version is rejected.
        """

        # Establish a valid session ..
        initialize_result = client.initialize()
        session_id = initialize_result.session_id

        # .. send a request with a wrong MCP-Protocol-Version header ..
        response = client.jsonrpc(
            'tools/list',
            session_id=session_id,
            extra_headers={'MCP-Protocol-Version': _unsupported_protocol_version},
        )

        # .. the server must reject it ..
        assert response.status_code == BAD_REQUEST

        # .. with the canonical JSON-RPC invalid-request error.
        data = response.json()

        error = data['error']
        assert error['code'] == _error_invalid_request

# ################################################################################################################################

    def test_delete_with_mismatched_protocol_version_rejected(self, client:'MCPClient') -> 'None':
        """ A DELETE request whose MCP-Protocol-Version header disagrees with the session's
        negotiated version is rejected, consistent with the POST path.
        """

        # Establish a valid session ..
        initialize_result = client.initialize()
        session_id = initialize_result.session_id

        # .. send a DELETE with a wrong MCP-Protocol-Version header ..
        response = client.delete_session(
            session_id=session_id,
            extra_headers={'MCP-Protocol-Version': _unsupported_protocol_version},
        )

        # .. the server must reject it ..
        assert response.status_code == BAD_REQUEST

        # .. with the canonical JSON-RPC invalid-request error.
        data = response.json()

        error = data['error']
        assert error['code'] == _error_invalid_request

# ################################################################################################################################

    def test_initialize_without_protocol_version_rejected(self, client:'MCPClient') -> 'None':
        """ Initialize with no protocolVersion in params is rejected per the MCP spec.
        """

        # Send an initialize without the required protocolVersion field ..
        params = {
            'capabilities': {},
            'clientInfo': {'name': 'test', 'version': '1.0'},
        }
        response = client.jsonrpc('initialize', params=params)

        # .. the response must carry a JSON-RPC error ..
        assert response.status_code == OK

        data = response.json()
        assert 'error' in data

        error = data['error']
        assert error['code'] == _error_invalid_request

# ################################################################################################################################

    def test_initialize_without_protocol_version_creates_no_session(self, client:'MCPClient') -> 'None':
        """ Initialize with no protocolVersion must not create a session.
        """

        # Send an initialize without the required protocolVersion field ..
        params = {
            'capabilities': {},
            'clientInfo': {'name': 'test', 'version': '1.0'},
        }
        response = client.jsonrpc('initialize', params=params)

        # .. no session must have been created, so no Mcp-Session-Id header ..
        assert 'Mcp-Session-Id' not in response.headers

# ################################################################################################################################
# ################################################################################################################################
