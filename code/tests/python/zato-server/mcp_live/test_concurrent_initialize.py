# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from concurrent.futures import as_completed, ThreadPoolExecutor
from http.client import OK

# pytest
import pytest

# local
from _client import MCPClient, _session_header
from _constants import _demo_echo_service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

# How many interleaved rounds of tools/call and initialize to run
_interleaved_round_count = 20

# How many worker threads run the rounds in parallel
_worker_count = 20

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='function')
def client(zato_server:'anydict') -> 'MCPClient':
    out = MCPClient(zato_server['mcp_url'], auth=zato_server['mcp_auth'])
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestConcurrentInitialize:
    """ Tests MCP protocol conformance under concurrent load.
    """

# ################################################################################################################################

    def test_concurrent_tools_call_and_initialize(self, client:'MCPClient') -> 'None':
        """ Runs tools/call and initialize requests in parallel on the same channel.
        Per the MCP spec, only initialize responses carry the Mcp-Session-Id header
        and each initialize produces its own unique session ID.
        """

        # Establish the session that all tools/call requests will use ..
        initialize_result = client.initialize()
        session_id = initialize_result.session_id

        # .. each round sends one tools/call ..
        def _run_tools_call_round(round_index:'int') -> 'anydict':
            params = {'name': _demo_echo_service, 'arguments': {'message': f'round {round_index}'}}
            response = client.jsonrpc('tools/call', params=params, session_id=session_id, request_id=round_index)

            out = {
                'kind': 'tools_call',
                'status_code': response.status_code,
                'session_header': response.headers.get(_session_header),
            }
            return out

        # .. and each initialize round creates a brand new session ..
        def _run_initialize_round(round_index:'int') -> 'anydict':
            initialize_result = client.initialize()
            initialize_response = initialize_result.response

            out = {
                'kind': 'initialize',
                'status_code': initialize_response.status_code,
                'session_header': initialize_result.session_id,
            }
            return out

        # .. run both kinds of rounds in parallel ..
        results:'anylist' = []

        with ThreadPoolExecutor(max_workers=_worker_count) as executor:

            futures:'anylist' = []

            for round_index in range(_interleaved_round_count):
                tools_call_future = executor.submit(_run_tools_call_round, round_index)
                futures.append(tools_call_future)

                initialize_future = executor.submit(_run_initialize_round, round_index)
                futures.append(initialize_future)

            for future in as_completed(futures):
                result = future.result()
                results.append(result)

        # .. every request must have succeeded ..
        for result in results:
            assert result['status_code'] == OK, f'Request failed: {result}'

        # .. per the spec, only initialize responses carry the session header ..
        created_session_ids:'anylist' = []

        for result in results:

            if result['kind'] == 'tools_call':
                assert result['session_header'] is None, f'Unexpected session header in tools/call response: {result}'

            else:
                created_session_ids.append(result['session_header'])

        # .. every initialize must have produced its own unique session ID ..
        unique_session_ids = set(created_session_ids)
        created_count = len(created_session_ids)
        unique_count = len(unique_session_ids)

        assert created_count == _interleaved_round_count
        assert unique_count == created_count

        # .. clean up all the sessions this test created.
        for created_session_id in created_session_ids:
            _ = client.delete_session(session_id=created_session_id)

        _ = client.delete_session(session_id=session_id)

# ################################################################################################################################
# ################################################################################################################################
