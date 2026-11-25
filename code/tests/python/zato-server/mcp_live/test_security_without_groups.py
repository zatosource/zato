# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import FORBIDDEN

# pytest
import pytest

# local
from _client import MCPClient
from _constants import _mcp_empty_group_gateway

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# The MCP protocol revision the initialize requests ask for
_protocol_version = '2025-06-18'

_initialize_params = {
    'protocolVersion': _protocol_version,
    'capabilities': {},
    'clientInfo': {'name': 'zato-mcp-test', 'version': '1.0'},
}

# The two gateways that carry no security - one with no groups at all
# and one whose only group has no members
_url_keys = ['mcp_url_without_groups', 'mcp_url_empty_group']

# The server record that each request to the gateway whose only group has no members produces
_empty_group_record = f'Channel `{_mcp_empty_group_gateway}` is protected by security groups that have no members'

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('url_key', _url_keys)
class TestWithoutSecurity:
    """ Verifies that a gateway without security rejects every request.
    """

    def test_initialize_without_credentials_is_rejected(self, zato_server:'any_', url_key:'str') -> 'None':
        """ An initialize request with no credentials gets 403 with an empty payload.
        """

        zato_server['expected_server_records'].append(_empty_group_record)

        client = MCPClient(zato_server[url_key])
        response = client.jsonrpc('initialize', params=_initialize_params)

        assert response.status_code == FORBIDDEN
        assert response.text == ''

    def test_initialize_with_valid_credentials_is_rejected(self, zato_server:'any_', url_key:'str') -> 'None':
        """ An initialize request carrying the valid basic-auth credentials
        of the demo gateway's group is rejected too.
        """

        zato_server['expected_server_records'].append(_empty_group_record)

        client = MCPClient(zato_server[url_key], auth=zato_server['mcp_auth'])
        response = client.jsonrpc('initialize', params=_initialize_params)

        assert response.status_code == FORBIDDEN
        assert response.text == ''

    def test_tools_list_without_credentials_is_rejected(self, zato_server:'any_', url_key:'str') -> 'None':
        """ A tools/list request with no credentials gets 403 with an empty payload.
        """

        zato_server['expected_server_records'].append(_empty_group_record)

        client = MCPClient(zato_server[url_key])
        response = client.jsonrpc('tools/list')

        assert response.status_code == FORBIDDEN
        assert response.text == ''

# ################################################################################################################################
# ################################################################################################################################
