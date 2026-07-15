# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sqlite3
import time
from base64 import b64encode
from json import dumps, loads
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# local
from _client import MCPClient

# Zato
from zato.common.api import GENERIC
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource
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

# The columns the assertions read, in the order the select below returns them
_event_columns = ('id', 'source', 'event_type', 'object_name', 'cid', 'endpoint', 'ext_client_id', 'sub_key',
    'size', 'outcome', 'data')

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

def _set_audit_log_active(zato_server:'anydict', gateway:'anydict', is_active:'bool') -> 'None':
    """ Edits the gateway's audit log toggle, keeping everything else as it was.
    """

    payload = dict(gateway)
    payload['is_audit_log_active'] = is_active

    _ = _admin_invoke(zato_server, 'zato.generic.connection.edit', payload)

# ################################################################################################################################

def _read_events(zato_server:'anydict', min_id:'int' = 0) -> 'dictlist':
    """ Reads the MCP audit events of the default gateway out of the live server's audit database,
    newer than the given row ID, oldest first.
    """

    audit_db_path = zato_server['audit_db_path']

    # An empty result before the server ever wrote an event - the file does not exist yet
    if not os.path.isfile(audit_db_path):
        return []

    column_list = ', '.join(_event_columns)
    query = f'select {column_list} from event where source = ? and object_name = ? and id > ? order by id'

    connection = sqlite3.connect(audit_db_path)

    try:
        cursor = connection.execute(query, (AuditSource.MCP, mcp_gateway_name, min_id))
        db_rows = cursor.fetchall()
    finally:
        connection.close()

    out = []

    for db_row in db_rows:
        row = dict(zip(_event_columns, db_row))
        out.append(row)

    return out

# ################################################################################################################################

def _run_one_sequence(zato_server:'anydict') -> 'str':
    """ Runs one full MCP conversation - initialize, tools/list, tools/call and DELETE -
    and returns the session ID it used.
    """

    client = MCPClient(zato_server['mcp_url'], auth=zato_server['mcp_auth'])
    session_id = client.initialize().session_id

    _ = client.jsonrpc('tools/list', session_id=session_id)

    params = {'name': _demo_echo_service, 'arguments': {'customer': 'Customer name here'}}
    _ = client.jsonrpc('tools/call', params=params, session_id=session_id)

    _ = client.delete_session(session_id)

    return session_id

# ################################################################################################################################

def _wait_until_audit_is_on(zato_server:'anydict') -> 'int':
    """ Polls the gateway with initialize requests until the toggled-on config reaches the wrapper
    and the first audit row lands. Returns the highest event ID written so far, so the test
    can look only at the rows its own scripted sequence produces.
    """

    deadline = time.monotonic() + _rebuild_timeout

    while time.monotonic() < deadline:

        client = MCPClient(zato_server['mcp_url'], auth=zato_server['mcp_auth'])
        _ = client.initialize()

        events = _read_events(zato_server)

        if events:
            last_event = events[-1]
            out = last_event['id']
            return out

        time.sleep(_rebuild_poll_interval)

    raise Exception(f'No audit events appeared within {_rebuild_timeout}s of toggling the audit log on')

# ################################################################################################################################
# ################################################################################################################################

class TestMCPAuditLog:
    """ One audit event per MCP request - the toggle is flipped the same way the dashboard does it
    and the events are asserted straight in the live server's audit database.
    """

    def test_audit_log_records_one_event_per_request(self, zato_server:'anydict') -> 'None':

        gateway = _get_demo_gateway(zato_server)

        # The toggle is off by default, so a full conversation leaves no trace ..
        _ = _run_one_sequence(zato_server)

        events = _read_events(zato_server)
        assert events == [], f'Expected no events while the toggle is off, got: {events}'

        try:
            # .. toggle the audit log on and wait until enforcement picks it up ..
            _set_audit_log_active(zato_server, gateway, True)
            last_seen_id = _wait_until_audit_is_on(zato_server)

            # .. run one full scripted conversation ..
            session_id = _run_one_sequence(zato_server)

            # .. which lands as exactly four events, in order.
            events = _read_events(zato_server, min_id=last_seen_id)

            event_types = [event['event_type'] for event in events]
            expected_types = [
                AuditEvent.MCP_Initialize,
                AuditEvent.MCP_Tools_List,
                AuditEvent.MCP_Tools_Call,
                AuditEvent.MCP_Session_Delete,
            ]
            assert event_types == expected_types, f'Expected {expected_types}, got: {events}'

            # Every event carries the published columns ..
            for event in events:
                assert event['source'] == AuditSource.MCP
                assert event['object_name'] == mcp_gateway_name
                assert event['ext_client_id'] == zato_server['mcp_sec_def_name']
                assert event['sub_key'] == session_id
                assert event['outcome'] == AuditOutcome.OK
                assert event['cid'], f'Expected a CID, got: {event}'

                data = loads(event['data'])
                assert data['remote_address'], f'Expected a remote address, got: {data}'
                assert data['duration_ms'] >= 0, f'Expected a duration, got: {data}'

            # .. only the tools/call event names the tool ..
            initialize_event, tools_list_event, tools_call_event, delete_event = events

            assert tools_call_event['endpoint'] == _demo_echo_service
            assert initialize_event['endpoint'] == ''
            assert tools_list_event['endpoint'] == ''
            assert delete_event['endpoint'] == ''

            # .. the response size is recorded for every response-carrying event ..
            assert tools_call_event['size'] > 0, f'Expected a response size, got: {tools_call_event}'

            # .. and the payload itself never reaches the audit log.
            assert 'Customer name here' not in tools_call_event['data']

        finally:
            # The gateway always goes back to its previous shape for the other tests.
            _set_audit_log_active(zato_server, gateway, False)

# ################################################################################################################################
# ################################################################################################################################
