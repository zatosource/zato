# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from base64 import b64encode
from json import dumps, loads
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# local
from _client import MCPClient

# Zato
from zato.common.api import GENERIC
from zato.common.defaults import default_cluster_id
from zato.common.util.gateway import mcp_gateway_name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, dictlist

# ################################################################################################################################
# ################################################################################################################################

# The demo service exposed on the default MCP gateway
_demo_echo_service = 'demo.echo'

# How long to wait for an edited gateway's wrapper to be rebuilt with the new config
_rebuild_timeout = 30

# How long to pause between polls for the rebuilt wrapper
_rebuild_poll_interval = 0.5

# Timeout in seconds for the admin invoke HTTP requests
_invoke_timeout = 30

# The response shaping fields the test toggles on and then restores - the cap must stay
# above the minimum usable byte budget for graceful trimming, i.e. 1000 tokens at 4 characters each.
_shaping_on = {
    'safeguards_strip_nulls': True,
    'max_response_size': 2048,
    'size_cap_mode': 'truncate',
}

_shaping_off = {
    'safeguards_strip_nulls': False,
    'max_response_size': 0,
    'size_cap_mode': 'truncate',
}

# ################################################################################################################################
# ################################################################################################################################

def _admin_invoke(zato_server:'anydict', service_name:'str', payload:'anydict') -> 'any_':
    """ Invokes an admin service on the live server through the admin.invoke channel.
    """

    host = zato_server['host']
    port = zato_server['port']
    password = zato_server['password']

    url = f'http://{host}:{port}/zato/api/invoke/{service_name}'
    body = dumps(payload).encode()

    credentials = f'admin.invoke:{password}'
    auth = b64encode(credentials.encode()).decode()

    request = Request(url, data=body, method='POST')
    request.add_header('Authorization', f'Basic {auth}')
    request.add_header('Content-Type', 'application/json')

    try:
        with urlopen(request, timeout=_invoke_timeout) as response:
            raw = response.read()
    except HTTPError as error:
        raw = error.read()
        error_text = raw.decode('utf-8', errors='replace')
        raise Exception(f'{service_name} returned HTTP {error.code}: {error_text}')

    out = loads(raw)
    return out

# ################################################################################################################################

def _get_demo_gateway(zato_server:'anydict') -> 'anydict':
    """ Returns the full config dict of the default MCP gateway, opaque attributes included.
    """

    items:'dictlist' = _admin_invoke(zato_server, 'zato.generic.connection.get-list', {
        'cluster_id': default_cluster_id,
        'type_': GENERIC.CONNECTION.TYPE.GATEWAY_MCP,
    })

    for item in items:
        if item['name'] == mcp_gateway_name:
            out = item
            break
    else:
        raise Exception(f'MCP gateway `{mcp_gateway_name}` not found in {items}')

    return out

# ################################################################################################################################

def _edit_gateway(zato_server:'anydict', gateway:'anydict', shaping:'anydict') -> 'None':
    """ Edits the gateway with the given response shaping fields, keeping everything else as it was.
    """

    payload = dict(gateway)
    payload.update(shaping)

    _ = _admin_invoke(zato_server, 'zato.generic.connection.edit', payload)

# ################################################################################################################################

def _call_echo(zato_server:'anydict', arguments:'anydict') -> 'anydict':
    """ Runs one initialize plus tools/call round trip against the live gateway
    and returns the result object of the JSON-RPC response.
    """

    client = MCPClient(zato_server['mcp_url'], auth=zato_server['mcp_auth'])
    session_id = client.initialize().session_id

    params = {'name': _demo_echo_service, 'arguments': arguments}
    response = client.jsonrpc('tools/call', params=params, session_id=session_id)

    data = response.json()

    out = data['result']
    return out

# ################################################################################################################################

def _get_echoed(result:'anydict') -> 'any_':
    """ Extracts and parses the echoed payload from a tools/call result.
    """

    content = result['content']
    first_content = content[0]
    text = first_content['text']

    out = loads(text)
    return out

# ################################################################################################################################

def _wait_until_nulls_are_stripped(zato_server:'anydict') -> 'None':
    """ Polls the gateway until the rebuilt wrapper starts stripping nulls,
    which proves the edited config took effect.
    """

    probe = {'customer': 'Customer name here', 'middle_name': None}
    deadline = time.monotonic() + _rebuild_timeout

    while time.monotonic() < deadline:

        result = _call_echo(zato_server, probe)
        echoed = _get_echoed(result)

        if 'middle_name' not in echoed:
            return

        time.sleep(_rebuild_poll_interval)

    raise Exception(f'Gateway `{mcp_gateway_name}` did not pick up the edited config within {_rebuild_timeout}s')

# ################################################################################################################################

def _make_rows(count:'int') -> 'dictlist':
    out = []
    for index in range(count):
        row = {'id': f'inv-{index:05}', 'customer': 'Customer name here'}
        out.append(row)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestResponseShaping:
    """ A full dashboard-style round trip - the gateway is edited with the same opaque keys the dashboard
    posts, the wrapper rebuilds itself, and tool responses come back cleaned and capped.
    """

    def test_edited_gateway_cleans_and_truncates_responses(self, zato_server:'anydict') -> 'None':

        gateway = _get_demo_gateway(zato_server)

        try:
            # Switch null stripping and a small token cap on ..
            _edit_gateway(zato_server, gateway, _shaping_on)
            _wait_until_nulls_are_stripped(zato_server)

            # .. null keys now disappear from responses while real values survive ..
            result = _call_echo(zato_server, {'customer': 'Customer name here', 'middle_name': None, 'fax': None})
            echoed = _get_echoed(result)

            assert 'isError' not in result
            assert echoed == {'customer': 'Customer name here'}

            # .. and an oversized response is gracefully trimmed to fit the cap ..
            result = _call_echo(zato_server, {'status': 'ok', 'rows': _make_rows(2000)})
            echoed = _get_echoed(result)

            assert 'isError' not in result
            assert echoed['status'] == 'ok'
            assert len(echoed['rows']) < 2000

        finally:
            # .. and the gateway always goes back to its previous shape for the other tests.
            _edit_gateway(zato_server, gateway, _shaping_off)

# ################################################################################################################################
# ################################################################################################################################
