# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sqlite3
import time
from json import loads
from typing import NamedTuple

# requests
import requests

# Zato
from zato.common.api import MCP
from zato.common.audit_log.api import AuditSource

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_environment.quickstart import ZatoEnvironment
    from zato.common.typing_ import any_, anydict, anydictnone, callable_, dictlist, strnone

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The gateway people sign in to, the bearer definition that lets the group's members in and their group
    Gateway_Name    = 'test.mcp.oauth.billing'
    Gateway_Path    = '/mcp/billing'
    Definition_Name = 'test.mcp.oauth.billing-agents'
    Group_Name      = 'mcp.test-oauth-billing'

    # The scopes the gateway tells clients to ask for
    Scopes = 'openid profile'

    # A second gateway whose definition lets any signed-in person of the realm in with a daily limit of calls,
    # for the tests that two people get counters and sessions of their own
    Limited_Gateway_Name    = 'test.mcp.oauth.billing-limited'
    Limited_Gateway_Path    = '/mcp/billing-limited'
    Limited_Definition_Name = 'test.mcp.oauth.anyone-limited'
    Limited_Group_Name      = 'mcp.test-oauth-limited'
    Daily_Limit             = 3

    # A gateway with OAuth off, secured with an API key
    Key_Gateway_Name    = 'test.mcp.oauth.partner-key'
    Key_Gateway_Path    = '/mcp/partner-key'
    Key_Definition_Name = 'test.mcp.oauth.partner-key'
    Key_Group_Name      = 'mcp.test-oauth-partner-key'
    Key_Header          = 'X-API-Key'

    # The service every gateway exposes
    Echo_Service = 'demo.echo'

    # A bearer definition verifying inbound tokens has a username column to fill, which nothing reads,
    # one per definition because the database enforces unique usernames
    Definition_Username         = 'zato-mcp-oauth'
    Limited_Definition_Username = 'zato-mcp-oauth-limited'

    # How long the demo service has to appear in a gateway's tool list after the start
    Tools_Timeout       = 60
    Tools_Poll_Interval = 1

    # How long an audit event has to appear after the request it records
    Audit_Timeout       = 10
    Audit_Poll_Interval = 0.2

    # Timeout of the HTTP requests of the tests, in seconds
    HTTP_Timeout = 30

    # The two protocol revisions the gateway speaks - the one with sessions the client products speak today
    # and the self-contained one where each request names its revision and method in headers
    Protocol_Version_Sessions  = MCP.Protocol_Version_Sessions
    Protocol_Version_Stateless = MCP.Protocol_Version_Stateless

    # The headers of the two revisions and the header a challenge arrives in
    Session_Header   = 'Mcp-Session-Id'
    Version_Header   = 'MCP-Protocol-Version'
    Method_Header    = 'Mcp-Method'
    Name_Header      = 'Mcp-Name'
    Challenge_Header = 'WWW-Authenticate'

    # Where every request of the tests comes from, as the server sees it
    Remote_Address = '127.0.0.1'

# ################################################################################################################################
# ################################################################################################################################

class OAuthLiveEnvironment(NamedTuple):
    """ Everything a test case needs - the server, the address clients reach it under and the gateways on it.
    """
    zato: 'ZatoEnvironment'
    server_address: 'str'
    gateway_url: 'str'
    limited_gateway_url: 'str'
    key_gateway_url: 'str'
    api_key: 'str'
    audit_db_path: 'str'

# ################################################################################################################################

class InitializeResult(NamedTuple):
    response: 'requests.Response'
    session_id: 'str'

# ################################################################################################################################
# ################################################################################################################################

# The columns the audit assertions read, in the order the select below returns them
_event_columns = ('id', 'event_time_iso', 'event_type', 'object_name', 'cid', 'endpoint', 'ext_client_id', 'sub_key',
    'size', 'outcome', 'data')

# ################################################################################################################################
# ################################################################################################################################

class MCPCaller:
    """ A simulated MCP client - JSON-RPC over HTTP with whatever credential headers it was given. The session
    methods speak the revision with sessions, the stateless ones the self-contained revision.
    """

    def __init__(self, url:'str', headers:'anydictnone'=None) -> 'None':
        self.url = url
        self.headers = headers or {}

# ################################################################################################################################

    def _build_headers(self, extra:'anydictnone'=None) -> 'anydict':
        out:'anydict' = {'Content-Type': 'application/json'}
        out.update(self.headers)

        if extra:
            out.update(extra)

        return out

# ################################################################################################################################

    def _post(self, method:'str', params:'anydictnone', headers:'anydict') -> 'requests.Response':
        body:'anydict' = {'jsonrpc': '2.0', 'id': 1, 'method': method}

        if params is not None:
            body['params'] = params

        out = requests.post(self.url, json=body, headers=headers, timeout=ModuleCtx.HTTP_Timeout)
        return out

# ################################################################################################################################

    def post(self, method:'str', params:'anydictnone'=None, session_id:'strnone'=None) -> 'requests.Response':
        """ Sends one request of the revision with sessions and returns the raw response.
        """
        extra:'anydict' = {}

        if session_id:
            extra[ModuleCtx.Session_Header] = session_id

        out = self._post(method, params, self._build_headers(extra))
        return out

# ################################################################################################################################

    def post_stateless(self, method:'str', params:'anydictnone'=None, name:'strnone'=None) -> 'requests.Response':
        """ Sends one self-contained request - the revision and the method travel in headers, and a tools/call
        names its tool in a header too.
        """
        extra:'anydict' = {
            ModuleCtx.Version_Header: ModuleCtx.Protocol_Version_Stateless,
            ModuleCtx.Method_Header: method,
        }

        if name:
            extra[ModuleCtx.Name_Header] = name

        out = self._post(method, params, self._build_headers(extra))
        return out

# ################################################################################################################################

    def initialize(self) -> 'InitializeResult':
        params = {
            'protocolVersion': ModuleCtx.Protocol_Version_Sessions,
            'capabilities': {},
            'clientInfo': {'name': 'zato-mcp-oauth-test', 'version': '1.0'},
        }

        response = self.post('initialize', params)
        session_id = response.headers.get(ModuleCtx.Session_Header, '')

        out = InitializeResult(response, session_id)
        return out

# ################################################################################################################################

    def tools_list(self, session_id:'str') -> 'requests.Response':
        out = self.post('tools/list', session_id=session_id)
        return out

# ################################################################################################################################

    def tools_call(self, session_id:'str', name:'str', arguments:'anydict') -> 'requests.Response':
        out = self.post('tools/call', {'name': name, 'arguments': arguments}, session_id=session_id)
        return out

# ################################################################################################################################

    def tools_list_stateless(self) -> 'requests.Response':
        out = self.post_stateless('tools/list')
        return out

# ################################################################################################################################

    def tools_call_stateless(self, name:'str', arguments:'anydict') -> 'requests.Response':
        out = self.post_stateless('tools/call', {'name': name, 'arguments': arguments}, name=name)
        return out

# ################################################################################################################################

    def delete(self, session_id:'str') -> 'requests.Response':
        headers = self._build_headers({ModuleCtx.Session_Header: session_id})

        out = requests.delete(self.url, headers=headers, timeout=ModuleCtx.HTTP_Timeout)
        return out

# ################################################################################################################################
# ################################################################################################################################

def bearer_caller(url:'str', token:'str') -> 'MCPCaller':
    out = MCPCaller(url, {'Authorization': f'Bearer {token}'})
    return out

# ################################################################################################################################

def api_key_caller(url:'str', api_key:'str') -> 'MCPCaller':
    out = MCPCaller(url, {ModuleCtx.Key_Header: api_key})
    return out

# ################################################################################################################################

def tool_names(response:'requests.Response') -> 'list[str]':
    """ The names of the tools a tools/list response lists.
    """
    out:'list[str]' = []

    data = response.json()
    result = data.get('result') or {}

    for tool in result.get('tools') or []:
        out.append(tool['name'])

    return out

# ################################################################################################################################
# ################################################################################################################################

def read_events(audit_db_path:'str', gateway_name:'str', min_id:'int'=0) -> 'dictlist':
    """ Reads the MCP audit events of one gateway out of the live server's audit database, newer than the given
    row ID, oldest first, each with its data document parsed and its attributes attached.
    """

    # An empty result before the server ever wrote an event - the file does not exist yet
    if not os.path.isfile(audit_db_path):
        return []

    column_list = ', '.join(_event_columns)
    query = f'select {column_list} from event where source = ? and object_name = ? and id > ? order by id'
    attr_query = 'select name, value from event_attr where event_id = ?'

    connection = sqlite3.connect(audit_db_path)

    try:
        cursor = connection.execute(query, (AuditSource.MCP, gateway_name, min_id))
        db_rows = cursor.fetchall()

        out = []

        for db_row in db_rows:
            row:'anydict' = dict(zip(_event_columns, db_row))
            row['data'] = loads(row['data'])

            attrs:'anydict' = {}
            for name, value in connection.execute(attr_query, (row['id'],)).fetchall():
                attrs[name] = value

            row['attrs'] = attrs
            out.append(row)

    finally:
        connection.close()

    return out

# ################################################################################################################################

def last_event_id(audit_db_path:'str', gateway_name:'str') -> 'int':
    """ The ID of the newest event of a gateway, zero before any was written - what a test reads events after.
    """
    events = read_events(audit_db_path, gateway_name)

    if events:
        last = events[-1]
        out = last['id']
    else:
        out = 0

    return out

# ################################################################################################################################

def wait_for_event(audit_db_path:'str', gateway_name:'str', min_id:'int', is_wanted:'callable_') -> 'anydict':
    """ Waits for the first event newer than the given ID that the predicate accepts and returns it.
    """
    deadline = time.monotonic() + ModuleCtx.Audit_Timeout

    while time.monotonic() < deadline:

        for event in read_events(audit_db_path, gateway_name, min_id):
            if is_wanted(event):
                return event

        time.sleep(ModuleCtx.Audit_Poll_Interval)

    events = read_events(audit_db_path, gateway_name, min_id)
    raise Exception(f'No matching audit event of `{gateway_name}` within {ModuleCtx.Audit_Timeout}s, got: {events}')

# ################################################################################################################################

def wait_for_event_of_type(audit_db_path:'str', gateway_name:'str', min_id:'int', event_type:'str') -> 'anydict':

    def _is_wanted(event:'any_') -> 'bool':
        out = event['event_type'] == event_type
        return out

    out = wait_for_event(audit_db_path, gateway_name, min_id, _is_wanted)
    return out

# ################################################################################################################################
# ################################################################################################################################
