# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.client import OK

# pytest
import pytest

# local
from _client import MCPClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

_concurrent_request_count = 20

# Standard params for initialize requests in tests
_initialize_params = {'protocolVersion': '2025-11-05', 'capabilities': {}, 'clientInfo': {'name': 'test', 'version': '1.0'}}

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='function')
def client(zato_server:'anydict') -> 'MCPClient':
    out = MCPClient(zato_server['mcp_url'], auth=zato_server['mcp_auth'])

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestConcurrent:
    """ Tests for concurrent MCP request handling.
    """

# ################################################################################################################################

    def test_concurrent_requests(self, client:'MCPClient') -> 'None':
        """ Fire 20 parallel initialize requests, assert all return 200.
        """

        def _send_request() -> 'int':
            response = client.jsonrpc('initialize', params=_initialize_params)
            return response.status_code

        results:'anylist' = []

        with ThreadPoolExecutor(max_workers=_concurrent_request_count) as executor:

            futures:'anylist' = []
            for _ in range(_concurrent_request_count):
                future = executor.submit(_send_request)
                futures.append(future)

            for future in as_completed(futures):
                status_code = future.result()
                results.append(status_code)

        for idx, status_code in enumerate(results):
            assert status_code == OK, f'Request {idx} returned {status_code}, expected {OK}'

# ################################################################################################################################
# ################################################################################################################################
