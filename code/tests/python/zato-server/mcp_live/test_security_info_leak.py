# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# local
from _client import MCPClient
from _constants import _zato_internal_prefix

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# Expected server name that masks the real identity
_expected_server_name = 'Apache'

# Expected server version returned in initialize
_expected_server_version = '2.4'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def client(zato_server:'any_') -> 'MCPClient':
    out = MCPClient(zato_server['mcp_url'])
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestInformationLeakage:
    """ Tests that error responses and server metadata do not leak internal details.
    """

    def test_error_responses_have_no_stack_traces(self, client:'MCPClient') -> 'None':
        """ Error responses must never contain Python stack traces.
        """

        params = {'name': 'nonexistent.service', 'arguments': {}}
        response = client.jsonrpc('tools/call', params=params)
        response_text = response.text

        # .. stack traces contain 'Traceback', 'File "', or 'line ' ..
        assert 'Traceback' not in response_text
        assert 'File "' not in response_text

# ################################################################################################################################

    def test_error_does_not_expose_internal_service_names(self, client:'MCPClient') -> 'None':
        """ Error responses must not reveal internal service names beyond what was requested.
        """

        requested_name = 'nonexistent.service'
        params = {'name': requested_name, 'arguments': {}}
        response = client.jsonrpc('tools/call', params=params)
        data = response.json()

        error_message = data['error']['message']

        # .. the error may mention the requested name, but must not leak internal ones.
        assert 'zato.server' not in error_message
        assert 'zato.channel' not in error_message

# ################################################################################################################################

    def test_server_header_masks_identity(self, client:'MCPClient') -> 'None':
        """ The initialize response must report the masked server name.
        """

        response = client.jsonrpc('initialize')
        data = response.json()

        server_info = data['result']['serverInfo']

        assert server_info['name'] == _expected_server_name
        assert server_info['version'] == _expected_server_version

# ################################################################################################################################

    def test_tools_list_never_exposes_internal_services(self, client:'MCPClient') -> 'None':
        """ The tools/list response must never include zato.* internal services.
        """

        response = client.jsonrpc('tools/list')
        tools = response.json()['result']['tools']

        for tool in tools:
            tool_name = tool['name']
            assert not tool_name.startswith(_zato_internal_prefix), \
                f'Internal service leaked in tools/list: {tool_name}'

# ################################################################################################################################
# ################################################################################################################################
