# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from collections.abc import Iterator
from http.client import BAD_REQUEST, FORBIDDEN, OK
from json import loads

# pytest
import pytest

# local
from _client import MCPClient
from _constants import _demo_echo_service

# Zato - test helpers
import keycloak_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strnone

    import requests

# ################################################################################################################################
# ################################################################################################################################

# The protocol version the test client announces during initialize
_protocol_version = '2025-11-05'

# ################################################################################################################################
# ################################################################################################################################

class BearerMCPClient(MCPClient):
    """ An MCP test client that authenticates with a bearer token instead of Basic Auth.
    """

    def __init__(self, mcp_url:'str', token:'str') -> 'None':
        super().__init__(mcp_url)
        self.token = token

# ################################################################################################################################

    def jsonrpc_bearer(self, method:'str', params:'anydict | None'=None, session_id:'strnone'=None) -> 'requests.Response':
        """ Sends a single JSON-RPC request with the Authorization header carrying the token.
        """
        extra_headers = {'Authorization': f'Bearer {self.token}'}

        out = self.jsonrpc(method, params=params, session_id=session_id, extra_headers=extra_headers)
        return out

# ################################################################################################################################

    def initialize_bearer(self) -> 'requests.Response':
        """ Sends an initialize request with the bearer token.
        """
        params = {
            'protocolVersion': _protocol_version,
            'capabilities': {},
            'clientInfo': {'name': 'zato-mcp-test', 'version': '1.0'},
        }

        out = self.jsonrpc_bearer('initialize', params=params)
        return out

# ################################################################################################################################

    def delete_session_bearer(self, session_id:'str') -> 'requests.Response':
        """ Terminates a session with the bearer token.
        """
        extra_headers = {'Authorization': f'Bearer {self.token}'}

        out = self.delete_session(session_id=session_id, extra_headers=extra_headers)
        return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module', autouse=True)
def keycloak() -> 'None':
    keycloak_.ensure_keycloak()

# ################################################################################################################################

@pytest.fixture(scope='function')
def accounting_client(zato_server:'anydict') -> 'BearerMCPClient':
    token = keycloak_.get_token(keycloak_.Client_Accounting, keycloak_.Secret_Accounting)

    out = BearerMCPClient(zato_server['mcp_url'], token)
    return out

# ################################################################################################################################

@pytest.fixture(scope='function')
def sales_client(zato_server:'anydict') -> 'BearerMCPClient':
    token = keycloak_.get_token(keycloak_.Client_Sales, keycloak_.Secret_Sales)

    out = BearerMCPClient(zato_server['mcp_url'], token)
    return out

# ################################################################################################################################

@pytest.fixture(scope='function')
def accounting_session(accounting_client:'BearerMCPClient') -> 'Iterator[str]':
    response = accounting_client.initialize_bearer()
    assert response.status_code == OK, response.text

    out = response.headers['Mcp-Session-Id']

    yield out

    _ = accounting_client.delete_session_bearer(out)

# ################################################################################################################################
# ################################################################################################################################

class TestBearerHappyPath:
    """ Valid Keycloak JWTs work through the full initialize and tools/call flow.
    """

    def test_initialize_and_tools_call(self, accounting_client:'BearerMCPClient', accounting_session:'str') -> 'None':

        arguments = {'hello': 'world'}
        params = {'name': _demo_echo_service, 'arguments': arguments}

        response = accounting_client.jsonrpc_bearer('tools/call', params=params, session_id=accounting_session)
        assert response.status_code == OK, response.text

        json_body = response.json()
        result = json_body['result']

        # The result must contain content with the echoed data ..
        content = result['content']
        assert len(content) >= 1

        # .. extract the text from the first content element and parse it.
        first_content = content[0]
        text = first_content['text']
        parsed = loads(text)

        # .. demo.echo returns the request payload unchanged.
        assert parsed['hello'] == 'world'

# ################################################################################################################################

    def test_static_bearer_member(self, zato_server:'anydict') -> 'None':

        # The static definition is a group member too, so its exact token authenticates callers
        client = BearerMCPClient(zato_server['mcp_url'], zato_server['bearer_static_token'])

        response = client.initialize_bearer()
        assert response.status_code == OK, response.text

        session_id = response.headers['Mcp-Session-Id']
        _ = client.delete_session_bearer(session_id)

# ################################################################################################################################
# ################################################################################################################################

class TestBearerRejections:
    """ Tokens that do not match any group member are rejected.
    """

    def test_wrong_audience(self, zato_server:'anydict') -> 'None':

        token = keycloak_.get_token(keycloak_.Client_Wrong_Audience, keycloak_.Secret_Wrong_Audience)
        client = BearerMCPClient(zato_server['mcp_url'], token)

        response = client.initialize_bearer()
        assert response.status_code == FORBIDDEN, response.text

# ################################################################################################################################

    def test_missing_claim(self, zato_server:'anydict') -> 'None':

        # This token has the right audience but carries no department claim,
        # so neither claim-filtered definition matches it
        token = keycloak_.get_token(keycloak_.Client_No_Department, keycloak_.Secret_No_Department)
        client = BearerMCPClient(zato_server['mcp_url'], token)

        response = client.initialize_bearer()
        assert response.status_code == FORBIDDEN, response.text

# ################################################################################################################################

    def test_invalid_static_token(self, zato_server:'anydict') -> 'None':

        client = BearerMCPClient(zato_server['mcp_url'], 'this-is-not-the-configured-token')

        response = client.initialize_bearer()
        assert response.status_code == FORBIDDEN, response.text

# ################################################################################################################################
# ################################################################################################################################

class TestBearerSessionIdentity:
    """ Sessions are bound to the bearer identity that created them.
    """

    def test_session_bound_to_bearer_identity(
        self,
        zato_server:'anydict',
        accounting_client:'BearerMCPClient',
        accounting_session:'str',
        ) -> 'None':

        # A session created with a bearer token cannot be used with Basic Auth credentials
        basic_auth_client = MCPClient(zato_server['mcp_url'], auth=zato_server['mcp_auth'])

        response = basic_auth_client.jsonrpc('ping', session_id=accounting_session)
        assert response.status_code == BAD_REQUEST, response.text

# ################################################################################################################################

    def test_claim_filters_resolve_to_different_identities(
        self,
        accounting_client:'BearerMCPClient',
        accounting_session:'str',
        sales_client:'BearerMCPClient',
        ) -> 'None':

        # Both tokens come from the same IdP and carry the same audience, yet the claim
        # filters resolve them to two different definitions - so the Sales identity
        # cannot use a session created by the Accounting one
        response = sales_client.jsonrpc_bearer('ping', session_id=accounting_session)
        assert response.status_code == BAD_REQUEST, response.text

        # The Accounting identity itself keeps working
        response = accounting_client.jsonrpc_bearer('ping', session_id=accounting_session)
        assert response.status_code == OK, response.text

# ################################################################################################################################
# ################################################################################################################################
