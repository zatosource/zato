# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sqlite3
import time
from http.client import OK
from json import loads
from typing import NamedTuple

# requests
import requests

# Zato
from zato.common.api import MCP
from zato.common.audit_log.common import AuditSource
from zato.common.audit_log.export.config import ModuleCtx as ExportCtx

# Test support
from live_otel.containers import OTelCollector

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_environment.quickstart import ZatoEnvironment
    from zato.common.typing_ import anydict, anydictnone, callable_, dictlist, strlist, strnone, strstrdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The gateway people sign in to, the bearer definition that lets the group's members in and their group
    Gateway_Name    = 'test.audit.export.billing'
    Gateway_Path    = '/audit-export/billing'
    Definition_Name = 'test.audit.export.billing-agents'
    Group_Name      = 'audit-export.billing-agents'

    # A second gateway whose definition lets any signed-in person in with a daily limit of calls
    Limited_Gateway_Name    = 'test.audit.export.billing-limited'
    Limited_Gateway_Path    = '/audit-export/billing-limited'
    Limited_Definition_Name = 'test.audit.export.anyone-limited'
    Limited_Group_Name      = 'audit-export.limited'
    Daily_Limit             = 2

    # A gateway with OAuth off, secured with an API key, so the suite can tell when the tool registry is ready
    Key_Gateway_Name    = 'test.audit.export.partner-key'
    Key_Gateway_Path    = '/audit-export/partner-key'
    Key_Definition_Name = 'test.audit.export.partner-key'
    Key_Group_Name      = 'audit-export.partner-key'
    Key_Header          = 'X-API-Key'

    # The REST channel whose events leave without payloads and the one whose events leave with them
    REST_Channel_Name = 'test.audit.export.rest'
    REST_Channel_Path = '/audit-export/rest'

    REST_Payload_Channel_Name = 'test.audit.export.rest-payload'
    REST_Payload_Channel_Path = '/audit-export/rest-payload'

    # The service every gateway and channel exposes
    Echo_Service = 'demo.echo'

    # The quota tier created through the API, which writes a config event, and the rules it carries
    Tier_Name  = 'test.audit.export.tier'
    Tier_Rules = [{
        'cidr_list': ['10.0.0.0/8'],
        'time_range': [{
            'is_all_day': True,
            'disabled': False,
            'disallowed': False,
            'rate': 10,
            'burst': 20,
            'limit': 100,
            'limit_unit': 'minute',
        }]
    }]

    # A bearer definition verifying inbound tokens has a username column to fill, which nothing reads,
    # one per definition because the database enforces unique usernames
    Definition_Username         = 'zato-audit-export'
    Limited_Definition_Username = 'zato-audit-export-limited'

    # How long the demo service has to appear in a gateway's tool list after the start
    Tools_Timeout       = 60
    Tools_Poll_Interval = 1

    # How long an audit event has to appear in the database after the request it records
    Audit_Timeout       = 10
    Audit_Poll_Interval = 0.2

    # How long the export has to recover after the collector comes back - the retry backoff grows up to a minute
    Resume_Timeout = 120

    # Timeout of the HTTP requests of the tests, in seconds
    HTTP_Timeout = 30

    # The name the quickstart server runs under
    Server_Name = 'server1'

    # The two protocol revisions the gateway speaks and the headers they travel with
    Protocol_Version_Sessions  = MCP.Protocol_Version_Sessions
    Protocol_Version_Stateless = MCP.Protocol_Version_Stateless

    Session_Header = 'Mcp-Session-Id'
    Version_Header = 'MCP-Protocol-Version'
    Method_Header  = 'Mcp-Method'
    Name_Header    = 'Mcp-Name'

# ################################################################################################################################
# ################################################################################################################################

# The sources the server exports - config events stay in the database only
Exported_Sources = f'{AuditSource.MCP},{AuditSource.REST_Channel}'

# ################################################################################################################################
# ################################################################################################################################

class InitializeResult(NamedTuple):
    response: 'requests.Response'
    session_id: 'str'

# ################################################################################################################################
# ################################################################################################################################

class MCPCaller:
    """ A simulated MCP client - JSON-RPC over HTTP with whatever credential headers it was given.
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
        """ Sends one request of the revision with sessions.
        """
        extra:'anydict' = {}

        if session_id:
            extra[ModuleCtx.Session_Header] = session_id

        out = self._post(method, params, self._build_headers(extra))
        return out

# ################################################################################################################################

    def post_stateless(self, method:'str', params:'anydictnone'=None, name:'strnone'=None) -> 'requests.Response':
        """ Sends one self-contained request - the revision and the method travel in headers.
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
            'clientInfo': {'name': 'zato-audit-export-test', 'version': '1.0'},
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
# ################################################################################################################################

def bearer_caller(url:'str', token:'str') -> 'MCPCaller':
    out = MCPCaller(url, {'Authorization': f'Bearer {token}'})
    return out

# ################################################################################################################################

def api_key_caller(url:'str', api_key:'str') -> 'MCPCaller':
    out = MCPCaller(url, {ModuleCtx.Key_Header: api_key})
    return out

# ################################################################################################################################

def tool_names(response:'requests.Response') -> 'strlist':
    """ The names of the tools a tools/list response lists.
    """
    out:'strlist' = []

    data = response.json()
    result = data.get('result') or {}

    for tool in result.get('tools') or []:
        out.append(tool['name'])

    return out

# ################################################################################################################################
# ################################################################################################################################

class AuditExportEnvironment(NamedTuple):
    """ Everything a test needs - the server, the collector and the addresses of the gateways and channels.
    """
    zato: 'ZatoEnvironment'
    collector: 'OTelCollector'
    server_address: 'str'
    gateway_url: 'str'
    limited_gateway_url: 'str'
    key_gateway_url: 'str'
    rest_url: 'str'
    rest_payload_url: 'str'
    api_key: 'str'
    audit_db_path: 'str'
    server_log_path: 'str'

# ################################################################################################################################
# ################################################################################################################################

# The columns the assertions compare records against, in the order the select below returns them
_event_columns = ('id', 'cid', 'cid_sequence', 'source', 'event_type', 'object_name', 'msg_id', 'correl_id', 'ext_client_id',
    'pub_time_iso', 'event_time_iso', 'server_name', 'endpoint', 'sub_key', 'size', 'priority', 'outcome',
    'application_outcome', 'classification', 'status', 'duration_ms', 'data')

# ################################################################################################################################
# ################################################################################################################################

def build_export_environment(collector:'OTelCollector', *, protocol:'str', sources:'str') -> 'strstrdict':
    """ The variables that point a server's export at the collector over the given protocol.
    """
    if protocol == ExportCtx.Protocol_GRPC:
        endpoint = collector.grpc_endpoint
    else:
        endpoint = collector.http_endpoint

    out = {
        ExportCtx.Env_Endpoint: endpoint,
        ExportCtx.Env_Protocol: protocol,
        ExportCtx.Env_SSL_CA_File: collector.ca_file,
        ExportCtx.Env_Headers: f'Authorization=Bearer {collector.bearer_token}',
        ExportCtx.Env_Sources: sources,
    }

    return out

# ################################################################################################################################

def wait_for_tools(gateway_url:'str', api_key:'str') -> 'None':
    """ Waits until the gateway secured with the key lists the demo service, which is the moment every
    gateway's tool registry holds the services the start deployed.
    """
    deadline = time.monotonic() + ModuleCtx.Tools_Timeout
    caller = api_key_caller(gateway_url, api_key)

    while time.monotonic() < deadline:

        try:
            response = caller.tools_list_stateless()
        except requests.exceptions.ConnectionError:
            time.sleep(ModuleCtx.Tools_Poll_Interval)
            continue

        if response.status_code == OK:
            if ModuleCtx.Echo_Service in tool_names(response):
                return

        time.sleep(ModuleCtx.Tools_Poll_Interval)

    raise Exception(f'`{ModuleCtx.Echo_Service}` did not appear in the tools of {gateway_url} within {ModuleCtx.Tools_Timeout}s')

# ################################################################################################################################
# ################################################################################################################################

def read_events(audit_db_path:'str', source:'str', object_name:'str', min_id:'int'=0) -> 'dictlist':
    """ Reads the audit events of one object out of the live server's audit database, newer than the given
    row id, oldest first, each with its attributes attached and, when it is JSON, its data document parsed.
    """

    # An empty result before the server ever wrote an event - the file does not exist yet
    if not os.path.isfile(audit_db_path):
        return []

    column_list = ', '.join(_event_columns)
    query = f'select {column_list} from event where source = ? and object_name = ? and id > ? order by id'
    attr_query = 'select name, value, value_number from event_attr where event_id = ?'

    connection = sqlite3.connect(audit_db_path)

    try:
        cursor = connection.execute(query, (source, object_name, min_id))
        db_rows = cursor.fetchall()

        out = []

        for db_row in db_rows:
            row:'anydict' = dict(zip(_event_columns, db_row))

            try:
                row['document'] = loads(row['data'])
            except ValueError:
                row['document'] = None

            attrs:'anydict' = {}
            for name, value, value_number in connection.execute(attr_query, (row['id'],)).fetchall():
                if value_number is not None:
                    attrs[name] = value_number
                else:
                    attrs[name] = value

            row['attrs'] = attrs
            out.append(row)

    finally:
        connection.close()

    return out

# ################################################################################################################################

def last_event_id(audit_db_path:'str', source:'str', object_name:'str') -> 'int':
    """ The id of the newest event of an object, zero before any was written - what a test reads events after.
    """
    events = read_events(audit_db_path, source, object_name)

    if events:
        last = events[-1]
        out = last['id']
    else:
        out = 0

    return out

# ################################################################################################################################

def wait_for_event(audit_db_path:'str', source:'str', object_name:'str', min_id:'int', is_wanted:'callable_') -> 'anydict':
    """ Waits for the first event newer than the given id that the predicate accepts and returns it.
    """
    deadline = time.monotonic() + ModuleCtx.Audit_Timeout

    while time.monotonic() < deadline:

        for event in read_events(audit_db_path, source, object_name, min_id):
            if is_wanted(event):
                return event

        time.sleep(ModuleCtx.Audit_Poll_Interval)

    events = read_events(audit_db_path, source, object_name, min_id)
    raise Exception(f'No matching audit event of `{object_name}` within {ModuleCtx.Audit_Timeout}s, got: {events}')

# ################################################################################################################################

def wait_for_event_of_type(audit_db_path:'str', source:'str', object_name:'str', min_id:'int', event_type:'str') -> 'anydict':

    def _is_wanted(event:'anydict') -> 'bool':
        out = event['event_type'] == event_type
        return out

    out = wait_for_event(audit_db_path, source, object_name, min_id, _is_wanted)
    return out

# ################################################################################################################################

def count_lines(log_path:'str', text:'str') -> 'int':
    """ How many lines of the server's log contain the text.
    """
    if not os.path.isfile(log_path):
        return 0

    out = 0

    with open(log_path) as file_:
        for line in file_:
            if text in line:
                out += 1

    return out

# ################################################################################################################################

def wait_for_line(log_path:'str', text:'str', timeout:'float') -> 'None':
    """ Waits until the server's log holds a line with the text.
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:

        if count_lines(log_path, text):
            return

        time.sleep(ModuleCtx.Audit_Poll_Interval)

    raise Exception(f'No line with `{text}` in {log_path} within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################
