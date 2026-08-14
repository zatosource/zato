# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads

# Zato
from zato.common.typing_ import cast_

# local
import _constants
from _client import MCPClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from requests import Response
    from zato.common.typing_ import anydict, anydictnone, dictlist, strlist, tupnone

    Response = Response

# ################################################################################################################################
# ################################################################################################################################

# What every initialize request of the suite says about itself
_initialize_params = {
    'protocolVersion': _constants.Protocol_Version_Sessions,
    'capabilities': {},
    'clientInfo': {'name': 'zato-mcp-test', 'version': '1.0'},
}

# ################################################################################################################################
# ################################################################################################################################

def make_client(zato_server:'anydict', url_path:'str', auth:'tupnone | str' = 'default') -> 'MCPClient':
    """ A client for one gateway of the suite - the main basic auth credentials
    unless the test says otherwise, including an explicit None for no credentials at all.
    """

    if auth == 'default':
        auth = zato_server['basic_auth']

    mcp_url = zato_server['mcp_url'](url_path)

    # By now the sentinel is resolved and only a tuple or None remains
    client_auth = cast_('tupnone', auth)

    out = MCPClient(mcp_url, auth=client_auth)
    return out

# ################################################################################################################################

def initialize_response(client:'MCPClient', extra_headers:'anydictnone' = None) -> 'Response':
    """ One initialize request, returning the raw response - for the tests
    where the status code itself is the assertion.
    """

    out = client.jsonrpc('initialize', params=_initialize_params, extra_headers=extra_headers)
    return out

# ################################################################################################################################

def open_session(client:'MCPClient', extra_headers:'anydictnone' = None) -> 'str':
    """ One initialize round trip, returning the session the server issued.
    """

    response = initialize_response(client, extra_headers)

    out = response.headers['Mcp-Session-Id']
    return out

# ################################################################################################################################

def list_tools(client:'MCPClient', session_id:'str', extra_headers:'anydictnone' = None) -> 'dictlist':
    """ The tool definitions one tools/list request returns.
    """

    response = client.jsonrpc('tools/list', session_id=session_id, extra_headers=extra_headers)
    body = response.json()

    out = body['result']['tools']
    return out

# ################################################################################################################################

def get_tool_names(tools:'dictlist') -> 'strlist':
    """ Just the names of the given tool definitions, in the order they were listed.
    """

    out:'strlist' = []

    for tool in tools:
        out.append(tool['name'])

    return out

# ################################################################################################################################

def call_tool(
    client:'MCPClient',
    session_id:'str',
    tool_name:'str',
    arguments:'anydictnone' = None,
    extra_headers:'anydictnone' = None,
    ) -> 'anydict':
    """ One tools/call request, returning the whole JSON-RPC response body -
    the caller decides whether an error or a result is the expected outcome.
    """

    if arguments is None:
        arguments = {}

    params = {'name': tool_name, 'arguments': arguments}
    response = client.jsonrpc('tools/call', params=params, session_id=session_id, extra_headers=extra_headers)

    out = response.json()
    return out

# ################################################################################################################################

def get_result_text(body:'anydict') -> 'str':
    """ The text of the first content element of a tools/call result.
    """

    out = body['result']['content'][0]['text']
    return out

# ################################################################################################################################

def get_result_data(body:'anydict') -> 'anydict':
    """ The text of a tools/call result parsed back into the document the service produced.
    """

    text = get_result_text(body)

    out = loads(text)
    return out

# ################################################################################################################################

def bearer_headers(token:'str') -> 'anydict':
    """ The header a bearer token travels in.
    """

    out = {'Authorization': f'Bearer {token}'}
    return out

# ################################################################################################################################

def apikey_headers(key_value:'str') -> 'anydict':
    """ The header an API key travels in.
    """

    out = {_constants.APIKey_Header: key_value}
    return out

# ################################################################################################################################
# ################################################################################################################################
