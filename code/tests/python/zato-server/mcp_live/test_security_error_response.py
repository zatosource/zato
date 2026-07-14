# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from collections.abc import Iterator
from http.client import OK

# pytest
import pytest

# local
from _client import MCPClient
from _constants import _raise_service, _zato_internal_prefix

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

# Standard params for initialize requests in tests
_initialize_params = {'protocolVersion': '2025-11-05', 'capabilities': {}, 'clientInfo': {'name': 'test', 'version': '1.0'}}

# The generic error message expected from the server
_expected_error_message = 'Bad request'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='function')
def client(zato_server:'any_') -> 'MCPClient':
    out = MCPClient(zato_server['mcp_url'], auth=zato_server['mcp_auth'])
    return out

# ################################################################################################################################

@pytest.fixture(scope='function')
def session_id(client:'MCPClient') -> 'Iterator[str]':
    out = client.initialize().session_id

    yield out

    _ = client.delete_session(session_id=out)

# ################################################################################################################################
# ################################################################################################################################

class TestErrorResponse:
    """ Tests that error responses and server metadata do not expose internal details.
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

        error = data['error']
        error_message = error['message']

        # .. the error may mention the requested name, but must not expose internal ones.
        assert 'zato.server' not in error_message
        assert 'zato.gateway' not in error_message

# ################################################################################################################################

    def test_server_header_masks_identity(self, client:'MCPClient') -> 'None':
        """ The initialize response must report the masked server name.
        """

        response = client.jsonrpc('initialize', params=_initialize_params)
        data = response.json()

        result = data['result']
        server_info = result['serverInfo']

        assert server_info['name'] == _expected_server_name
        assert server_info['version'] == _expected_server_version

        # .. clean up the session.
        session_id = response.headers['Mcp-Session-Id']
        _ = client.delete_session(session_id=session_id)

# ################################################################################################################################

    def test_tools_list_never_exposes_internal_services(self, client:'MCPClient', session_id:'str') -> 'None':
        """ The tools/list response must never include zato.* internal services.
        """

        response = client.jsonrpc('tools/list', session_id=session_id)
        json_body = response.json()
        result = json_body['result']
        tools = result['tools']

        for tool in tools:
            tool_name = tool['name']
            assert not tool_name.startswith(_zato_internal_prefix), \
                f'Internal service found in tools/list: {tool_name}'

# ################################################################################################################################
# ################################################################################################################################

class TestExceptionResponse:
    """ Tests that service exceptions return a generic message and no internal details.
    """

    def test_service_exception_returns_generic_message(self, client:'MCPClient', session_id:'str') -> 'None':
        """ A tool whose service raises returns the generic error message with isError: True.
        """

        params = {'name': _raise_service, 'arguments': {}}
        response = client.jsonrpc('tools/call', params=params, session_id=session_id)

        assert response.status_code == OK

        data = response.json()
        result = data['result']
        content = result['content']
        first_entry = content[0]

        assert first_entry['text'] == _expected_error_message
        assert result['isError'] is True

# ################################################################################################################################

    def test_service_exception_body_has_no_internal_detail(self, client:'MCPClient', session_id:'str') -> 'None':
        """ The response body contains no exception text, file paths, tracebacks, or SQL.
        """

        params = {'name': _raise_service, 'arguments': {}}
        response = client.jsonrpc('tools/call', params=params, session_id=session_id)
        response_text = response.text

        # .. must not contain the actual exception message ..
        assert 'Test exception' not in response_text

        # .. must not contain file paths ..
        assert '.py' not in response_text

        # .. must not contain traceback markers ..
        assert 'Traceback' not in response_text
        assert 'File "' not in response_text

        # .. must not contain SQL fragments.
        assert 'SELECT' not in response_text
        assert 'INSERT' not in response_text

# ################################################################################################################################
# ################################################################################################################################
