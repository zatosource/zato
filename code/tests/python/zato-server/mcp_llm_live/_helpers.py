# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import re
import time
import unicodedata
from json import dumps, loads

# requests
import requests

# Zato
from zato.common.audit_log.api import AuditEvent
from zato.common.crypto.api import WebAdminCryptoManager
from zato.common.typing_ import cast_

# local
import _audit
import _constants
from _client import MCPClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from requests import Response
    from zato.common.typing_ import anydict, anydictnone, anytuple, callable_, dictlist, strlist, tupnone

    Response = Response

# ################################################################################################################################
# ################################################################################################################################

# How long a re-imported change may take to reach live enforcement, in seconds
_reimport_timeout = 60

# How often to poll for it, in seconds
_reimport_poll_interval = 0.5

# ################################################################################################################################
# ################################################################################################################################

# What every initialize request of the suite says about itself
_initialize_params = {
    'protocolVersion': _constants.Protocol_Version_Sessions,
    'capabilities': {},
    'clientInfo': {'name': 'zato-mcp-test', 'version': '1.0'},
}

# A digit-grouping separator between two digits - NFKC folds the space variants first,
# so a comma and a plain space are all that can remain.
_digit_group_separator = re.compile(r'(?<=\d)[, ](?=\d)')

# NFKC already folds the space variants, so this table holds only the characters NFKC keeps.
_unicode_variants = (
    ('\u2018', "'"),  # Left single quotation mark
    ('\u2019', "'"),  # Right single quotation mark
    ('\u201c', '"'),  # Left double quotation mark
    ('\u201d', '"'),  # Right double quotation mark
    ('\u2010', '-'),  # Hyphen
    ('\u2011', '-'),  # Non-breaking hyphen
    ('\u2013', '-'),  # En dash
    ('\u2014', '-'),  # Em dash
)

# ################################################################################################################################
# ################################################################################################################################

def normalize_llm_text(text:'str') -> 'str':
    """ The model's output with its Unicode variants folded into their plain equivalents -
    NFKC folds the space variants and the table above folds the quotation and dash variants.
    """

    out = unicodedata.normalize('NFKC', text)

    for variant, replacement in _unicode_variants:
        out = out.replace(variant, replacement)

    return out

# ################################################################################################################################

def text_contains(haystack:'str', needle:'str') -> 'bool':
    """ Whether the model's output contains the given text, with the Unicode variants
    of both sides folded first and case ignored.
    """

    normalized_haystack = normalize_llm_text(haystack)
    normalized_haystack = normalized_haystack.casefold()

    normalized_needle = normalize_llm_text(needle)
    normalized_needle = normalized_needle.casefold()

    out = normalized_needle in normalized_haystack
    return out

# ################################################################################################################################

def text_contains_number(haystack:'str', number:'str') -> 'bool':
    """ Whether the model's output contains the given number, with any digit-grouping
    separators the model writes between digits removed first.
    """

    normalized = normalize_llm_text(haystack)
    normalized = _digit_group_separator.sub('', normalized)

    out = number in normalized
    return out

# ################################################################################################################################

def contains_any_word(text:'str', words:'anytuple') -> 'bool':
    """ Whether the model's output contains any of the given lower-case words,
    with its Unicode variants folded and its case lowered first.
    """

    text = normalize_llm_text(text)
    text = text.lower()

    for word in words:
        if word in text:
            out = True
            break
    else:
        out = False

    return out

# ################################################################################################################################
# ################################################################################################################################

def admin_invoke(zato_server:'anydict', service_name:'str', request:'anydict') -> 'anydict':
    """ Invokes an admin service through the server's REST API, authenticated
    with the invoke credentials of the test environment's web-admin.
    """

    repo_dir = os.path.join(zato_server['temp_directory'], 'web-admin', 'config', 'repo')
    config_path = os.path.join(repo_dir, 'web-admin.conf')

    with open(config_path) as config_file:
        config = loads(config_file.read())

    crypto_manager = WebAdminCryptoManager(repo_dir=repo_dir)
    password = crypto_manager.decrypt(config['ADMIN_INVOKE_PASSWORD'])

    if isinstance(password, bytes):
        password = password.decode('utf8')

    url = zato_server['mcp_url'](f'/zato/api/invoke/{service_name}')
    auth = (config['ADMIN_INVOKE_NAME'], password)

    response = requests.post(url, data=dumps(request), auth=auth)

    if not response.ok:
        raise Exception(f'Admin invoke of `{service_name}` failed with HTTP {response.status_code}: {response.text}')

    out = response.json()

    # The invoker proxies the target service, so a failure inside the target
    # still comes back as HTTP 200 - the envelope carries the actual result.
    if 'zato_env' in out:
        zato_env = out['zato_env']

        if zato_env['result'] != 'ZATO_OK':
            raise Exception(f'Admin invoke of `{service_name}` failed: {response.text}')

    return out

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

def call_and_read_event(
    zato_server:'anydict',
    url_path:'str',
    gateway_name:'str',
    tool_name:'str',
    arguments:'anydict',
    ) -> 'anytuple':
    """ One tool call through the given gateway on a fresh session, returning
    the whole response body and the audit data document of the call's event.
    """

    audit_db_path = zato_server['audit_db_path']
    min_id = _audit.last_event_id(audit_db_path)

    client = make_client(zato_server, url_path)
    session_id = open_session(client)

    body = call_tool(client, session_id, tool_name, arguments)

    events = _audit.wait_for_events(
        audit_db_path, 1,
        object_name=gateway_name,
        event_type=AuditEvent.MCP_Tools_Call,
        min_id=min_id)

    out = body, events[-1]['data']
    return out

# ################################################################################################################################

def read_new_log_text(server_log_path:'str', log_offset:'int') -> 'str':
    """ What the server logged since the given offset.
    """

    with open(server_log_path) as server_log:
        _ = server_log.seek(log_offset)
        out = server_log.read()

    return out

# ################################################################################################################################

def wait_until(condition:'callable_', description:'str') -> 'None':
    """ Polls until the condition function returns True, which is how the tests wait
    for a re-imported change to reach live enforcement.
    """

    deadline = time.monotonic() + _reimport_timeout

    while time.monotonic() < deadline:

        if condition():
            return

        time.sleep(_reimport_poll_interval)

    raise Exception(f'Condition did not hold within {_reimport_timeout}s: {description}')

# ################################################################################################################################
# ################################################################################################################################
