# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import time
from http.client import NOT_FOUND

# requests
import requests

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def make_jsonrpc_initialize() -> 'str':
    """ Builds a JSON-RPC 2.0 initialize request body for MCP protocol negotiation.
    """

    out = json.dumps({
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'initialize',
        'params': {
            'protocolVersion': '2025-11-05',
            'capabilities': {},
            'clientInfo': {
                'name': 'test-client',
                'version': '1.0.0',
            },
        },
    })

    return out

# ################################################################################################################################
# ################################################################################################################################

def wait_for_mcp_channel(port:'int', url_path:'str', timeout:'int'=45) -> 'None':
    """ Polls an MCP channel until it responds with something other than NOT_FOUND.
    """

    url = f'http://127.0.0.1:{port}{url_path}'
    deadline = time.monotonic() + timeout
    attempt = 0

    while time.monotonic() < deadline:
        attempt += 1
        try:
            headers = {'Content-Type': 'application/json'}
            data = make_jsonrpc_initialize()
            response = requests.post(url, data=data, headers=headers, timeout=5)

            if attempt <= 3:
                logger.info('[wait_for_mcp_channel] attempt=%d POST %s -> %d', attempt, url, response.status_code)
            elif attempt % 10 == 0:
                logger.info('[wait_for_mcp_channel] attempt=%d POST %s -> %d', attempt, url, response.status_code)

            if response.status_code != NOT_FOUND:
                return

        except Exception as e:
            if attempt <= 3:
                logger.info('[wait_for_mcp_channel] attempt=%d exception: %s', attempt, e)

        time.sleep(1)

    raise Exception(f'MCP channel at {url} not available within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################
