# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# local
from _client import MCPClient
from _constants import _session_header, _session_id_prefix

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_expected_protocol_version = '2025-11-05'
_expected_server_name      = 'Apache'
_expected_server_version   = '2.4'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='function')
def client(zato_server:'anydict') -> 'MCPClient':
    out = MCPClient(zato_server['mcp_url'], auth=zato_server['mcp_auth'])

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestInitialize:
    """ Tests for the MCP initialize JSON-RPC method.
    """

    def test_initialize_returns_valid_jsonrpc(self, client:'MCPClient') -> 'None':
        """ Initialize returns a valid JSON-RPC 2.0 response with the expected protocol version.
        """

        response = client.jsonrpc('initialize')
        data = response.json()

        # The response must be a valid JSON-RPC 2.0 success ..
        assert data['jsonrpc'] == '2.0'
        assert data['id'] == 1
        assert 'result' in data

        # .. with the negotiated protocol version.
        result = data['result']

        assert result['protocolVersion'] == _expected_protocol_version

# ################################################################################################################################

    def test_initialize_returns_capabilities(self, client:'MCPClient') -> 'None':
        """ Initialize advertises tool list change notification capability.
        """

        response = client.jsonrpc('initialize')
        json_body = response.json()
        result = json_body['result']

        # The capabilities must include tools with listChanged ..
        capabilities = result['capabilities']
        tools = capabilities['tools']

        assert tools['listChanged'] is True

# ################################################################################################################################

    def test_initialize_returns_server_information(self, client:'MCPClient') -> 'None':
        """ Initialize reports the masked server identity.
        """

        response = client.jsonrpc('initialize')
        json_body = response.json()
        result = json_body['result']

        # The server information must report the masked identity ..
        server_information = result['serverInfo']

        assert server_information['name'] == _expected_server_name
        assert server_information['version'] == _expected_server_version

# ################################################################################################################################

    def test_initialize_returns_session_id_header(self, client:'MCPClient') -> 'None':
        """ Initialize sets the Mcp-Session-Id response header.
        """

        response = client.jsonrpc('initialize')

        # The session ID must be present in the response headers
        # and start with the expected prefix.
        session_id = response.headers[_session_header]

        assert session_id.startswith(_session_id_prefix)

# ################################################################################################################################

    def test_second_initialize_creates_different_session(self, client:'MCPClient') -> 'None':
        """ Each initialize creates a distinct session ID.
        """

        # Initialize twice - we discard the response objects
        # because only the session IDs matter for this comparison ..
        _, session_id_1 = client.initialize()
        _, session_id_2 = client.initialize()

        # .. they must differ.
        assert session_id_1 != session_id_2

# ################################################################################################################################
# ################################################################################################################################
