# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import time

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def make_jsonrpc_initialize():
    return json.dumps({
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

# ################################################################################################################################
# ################################################################################################################################

def wait_for_mcp_channel(port, url_path, timeout=45):
    """ Polls an MCP channel until it responds with something other than 404. """
    import requests as req_lib

    url = f'http://127.0.0.1:{port}{url_path}'
    deadline = time.monotonic() + timeout
    attempt = 0

    while time.monotonic() < deadline:
        attempt += 1
        try:
            resp = req_lib.post(url, data=make_jsonrpc_initialize(),
                headers={'Content-Type': 'application/json'}, timeout=5)
            if attempt <= 3 or attempt % 10 == 0:
                logger.warning('[wait_for_mcp_channel] attempt=%d POST %s -> %d', attempt, url, resp.status_code)
            if resp.status_code != 404:
                return
        except Exception as e:
            if attempt <= 3:
                logger.warning('[wait_for_mcp_channel] attempt=%d exception: %s', attempt, e)
        time.sleep(1)

    raise Exception(f'MCP channel at {url} not available within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################
