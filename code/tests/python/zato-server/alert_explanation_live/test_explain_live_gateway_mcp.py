# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The explain service end to end for an MCP gateway agents misuse - a real quickstart server, a gateway with the audit
# log on exposing one service as a tool behind a security group, imported through enmasse with thresholds of its own,
# real MCP over HTTP the way an agent speaks it - one initialize, four calls of a tool the gateway does not expose,
# six calls of the real tool from the one session - one real sweep, and the two explained alerts read off the server's
# own databases and received by a real SMTP receiver.

# stdlib
import os
from http.client import OK
from json import dumps

# requests
import requests

# SQLAlchemy
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import sessionmaker

# Zato
from zato.common.alerting.explain.evidence import Heading_Failures, Heading_Object
from zato.common.alerting.explain.settings_info import Label_Alerts, On
from zato.common.alerting.explain.store import ExplanationStore
from zato.common.api import Alerting
from zato.common.audit_log.api import AuditEvent, AuditSource, event_table
from zato.common.defaults import default_cluster_id

# Test helpers
from live_config import LiveServer
from live_enmasse import deactivate_document, import_document
from live_trace import Channel_Explain, Channel_MCP, Received, Sent, separator, trace
from test_explain_live import _assert_sound_explanation, _email_to, _trace_delivery
from test_explain_live_channel import _new_admin_client, _new_notification_config, _point_smtp_at_receiver, \
     _server_audit_engine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strnone

# ################################################################################################################################
# ################################################################################################################################

class TestExplainLiveGatewayMCP:

    def test_an_mcp_gateways_misused_tools_are_explained(
        self,
        ollama:'any_',
        zato_server:'any_',
        smtp_receiver:'any_',
        ) -> 'None':

        client = _new_admin_client()

        # The server's own notification connection delivers to the receiver ..
        _point_smtp_at_receiver(smtp_receiver)

        # .. and a gateway with the audit log on exposes the echo service to the one agent that may call it, with
        # thresholds four invalid calls and six repeated ones go past.
        gateway_document = _create_gateway()

        # The sweep explains through the LLM connection and mails from the address below
        notification_config = _new_notification_config()

        # Real MCP over HTTP - one session, four calls of a tool that is not there, six calls of the one that is
        session_id = _initialize()
        _produce_invalid_calls(session_id)
        _produce_repeated_calls(session_id)

        # One real sweep inside the server - the collectors, the rules, the explain service and the delivery
        trace(Channel_MCP, Sent, f'invoke {Alerting.Service} with {notification_config}')
        _ = client.invoke(Alerting.Service, notification_config)

        # Every tool call is on record under the gateway's name, the session as its sub key, the tool as its endpoint
        # and the agent's definition as the caller ..
        calls = _get_tool_calls()

        for row in calls:
            trace(Channel_MCP, Received, f'tool call audit log: {row["event_time_iso"]} {row["endpoint"]!r} ' +
                f'{row["outcome"]!r} {row["sub_key"]!r} {row["ext_client_id"]!r}')

        separator(Channel_MCP)

        assert len(calls) == _invalid_call_count + _repeat_call_count

        for row in calls:
            assert row['sub_key'] == session_id, row
            assert row['ext_client_id'] == _security_name, row

        invalid_rows = [row for row in calls if row['endpoint'] == _unknown_tool]
        assert len(invalid_rows) == _invalid_call_count

        # .. the calls fired the two rules of the MCP ruleset the gateway set thresholds for ..
        explanations = _get_stored_explanations()
        by_rule = {}

        for explanation in explanations:
            assert explanation['object_name'] == _gateway_name
            assert explanation['source'] == AuditSource.MCP
            by_rule[explanation['rule']] = explanation

        assert _invalid_calls_rule in by_rule, sorted(by_rule)
        assert _repeated_calls_rule in by_rule, sorted(by_rule)

        # .. the Object of each is the gateway's own, read from the generic connection row - its path, the one tool
        # it exposes, who may call it and the thresholds it sets of its own ..
        for rule in (_invalid_calls_rule, _repeated_calls_rule):
            evidence = by_rule[rule]['evidence']

            assert Heading_Object in evidence
            assert f'Name: {_gateway_name}' in evidence
            assert 'Type: MCP gateway' in evidence
            assert f'Path: {_url_path}' in evidence
            assert f'Services: {_tool_name}' in evidence
            assert 'Tools: 1' in evidence
            assert f'Callers: {_security_name}' in evidence
            assert 'Audit log: on' in evidence
            assert f'{Label_Alerts}: {On}' in evidence
            assert f'Invalid tool calls {_invalid_calls_threshold}' in evidence
            assert f'Repeated calls {_repeat_calls_threshold}' in evidence

        # .. the failures of the invalid calls group under the unknown tool's name, with the tool and the caller ..
        invalid_evidence = by_rule[_invalid_calls_rule]['evidence']

        assert Heading_Failures in invalid_evidence
        assert _unknown_tool in invalid_evidence
        assert 'error_code=-32601' in invalid_evidence
        assert f'Count: {_invalid_call_count}' in invalid_evidence
        assert f'Tool: {_unknown_tool}' in invalid_evidence
        assert f'Caller: {_security_name}' in invalid_evidence

        _assert_sound_explanation(by_rule[_invalid_calls_rule], _invalid_words)

        # .. the repeated calls name the session and the tool the fact carries, the six calls as the evidence ..
        repeated_evidence = by_rule[_repeated_calls_rule]['evidence']

        assert f'repeat_call_tool = {_tool_name}' in repeated_evidence
        assert f'repeat_call_session = {session_id}' in repeated_evidence
        assert f'Count: {_repeat_call_count}' in repeated_evidence
        assert f'Tool: {_tool_name}' in repeated_evidence

        _assert_sound_explanation(by_rule[_repeated_calls_rule], _repeat_words)

        # .. a gateway's explanation never proposes a remediation ..
        for explanation in explanations:
            assert explanation['remediation'] is None, explanation

        # .. and both explained alerts reached the mailbox.
        _trace_delivery(smtp_receiver)

        bodies = []
        for received in smtp_receiver.messages:
            assert received.recipients == _email_to
            bodies.append(received.body)

        for rule in (_invalid_calls_rule, _repeated_calls_rule):
            for body in bodies:
                if by_rule[rule]['explanation'] in body:
                    break
            else:
                raise AssertionError(f'Expected an email carrying {by_rule[rule]["explanation"]!r}')

        deactivate_document(gateway_document)

# ################################################################################################################################
# ################################################################################################################################

# The gateway of the proof, where it listens and the one tool it exposes
_gateway_name = 'explain.live.gateway.mcp'
_url_path = '/mcp/explain-live'
_tool_name = 'demo.echo'

# The tool the agent asks for that the gateway does not expose
_unknown_tool = 'demo.echoo'

# The agent's credentials and the group the gateway lets in
_security_name = 'explain.live.agent'
_security_username = 'explain-live-agent'
_security_password = 'agent-live-secret-1'
_group_name = 'explain.live.agents'

# How many calls of each kind the proof makes and the thresholds that many go past
_invalid_call_count = 4
_invalid_calls_threshold = 3
_repeat_call_count = 6
_repeat_calls_threshold = 5

# The rules the proof expects to fire, of the ruleset the MCP gateways are judged by
_invalid_calls_rule = 'Invalid_Tool_Calls'
_repeated_calls_rule = 'Repeated_Calls'

# What every MCP request carries and how long one may take, in seconds
_content_type = 'application/json'
_accept = 'application/json, text/event-stream'
_protocol_version = '2025-06-18'
_session_header = 'Mcp-Session-Id'
_request_timeout = 30

# The words a sound explanation of each misuse is expected to use at least one of
_invalid_words = ['tool', 'not exist', 'unknown', 'name', 'expose', 'agent', 'invalid', '-32601', 'method']
_repeat_words = ['loop', 'repeat', 'same', 'session', 'agent', 'over and over', 'again', 'tool']

# ################################################################################################################################
# ################################################################################################################################

def _create_gateway() -> 'anydict':
    """ The agent's Basic Auth definition, the group it is the one member of and the gateway that lets the group in -
    the audit log on, the LLM explaining its alerts, arguments validated, the echo service its one tool and thresholds
    low enough for four invalid and six repeated calls to fire their rules. What is returned is the document the
    gateway went in with, for the proof to deactivate it with once it is through.
    """
    out = {
        'security': [{
            'name': _security_name,
            'type': 'basic_auth',
            'is_active': True,
            'username': _security_username,
            'password': _security_password,
            'realm': 'Zato',
        }],
        'groups': [{
            'name': _group_name,
            'members': [_security_name],
        }],
        'mcp_gateway': [{
            'name': _gateway_name,
            'is_active': True,
            'url_path': _url_path,
            'services': [_tool_name],
            'security_groups': [_group_name],
            'is_audit_log_active': True,
            'validate_input': True,
            'alerts': {
                'is_active': True,
                'use_llm': True,
                'invalid_calls': _invalid_calls_threshold,
                'invalid_calls_window': 300,
                'repeat_calls': _repeat_calls_threshold,
                'repeat_calls_window': 300,
            },
        }],
    }

    import_document(out)

    trace(Channel_MCP, Sent, f'mcp gateway `{_gateway_name}` at {_url_path} -> {_tool_name}, callers {_group_name}')
    separator(Channel_MCP)

    return out

# ################################################################################################################################

def _jsonrpc(method:'str', params:'anydict', session_id:'strnone'=None) -> 'requests.Response':
    """ One JSON-RPC request to the gateway over HTTP, the way an agent sends it - the session header once there is one.
    """
    url = f'http://{LiveServer.host}:{LiveServer.server_port}{_url_path}'

    headers = {
        'Content-Type': _content_type,
        'Accept': _accept,
    }

    if session_id:
        headers[_session_header] = session_id

    body = {
        'jsonrpc': '2.0',
        'method': method,
        'id': 1,
        'params': params,
    }

    out = requests.post(url, data=dumps(body), headers=headers, auth=(_security_username, _security_password),
        timeout=_request_timeout)

    return out

# ################################################################################################################################

def _initialize() -> 'str':
    """ Opens the one session of the proof and returns its id.
    """
    params = {
        'protocolVersion': _protocol_version,
        'capabilities': {},
        'clientInfo': {'name': 'zato-explain-live', 'version': '1.0'},
    }

    trace(Channel_MCP, Sent, 'initialize')
    response = _jsonrpc('initialize', params)

    assert response.status_code == OK, response.text

    out = response.headers[_session_header]

    trace(Channel_MCP, Received, f'initialize -> {response.status_code}, session {out}')
    separator(Channel_MCP)

    return out

# ################################################################################################################################

def _call_tool(session_id:'str', tool:'str', arguments:'anydict') -> 'anydict':
    """ One tools/call of the session, named on the trace by the tool, and what the gateway answered.
    """
    trace(Channel_MCP, Sent, f'tools/call {tool} {arguments}')

    response = _jsonrpc('tools/call', {'name': tool, 'arguments': arguments}, session_id)
    out = response.json()

    if 'error' in out:
        trace(Channel_MCP, Received, f'tools/call {tool} -> error {out["error"]["code"]}: {out["error"]["message"]}')
    else:
        trace(Channel_MCP, Received, f'tools/call {tool} -> ok')

    separator(Channel_MCP)

    return out

# ################################################################################################################################

def _produce_invalid_calls(session_id:'str') -> 'None':
    """ The agent asks for a tool the gateway does not expose, four times - each answered with -32601.
    """
    for index in range(_invalid_call_count):
        result = _call_tool(session_id, _unknown_tool, {'attempt': index + 1})

        assert 'error' in result, result
        assert result['error']['code'] == -32601, result

# ################################################################################################################################

def _produce_repeated_calls(session_id:'str') -> 'None':
    """ The agent calls the one real tool six times over with the same arguments, the way an agent in a loop does.
    """
    for _ in range(_repeat_call_count):
        result = _call_tool(session_id, _tool_name, {'customer': 'Explain live'})

        assert 'error' not in result, result

# ################################################################################################################################

def _get_tool_calls() -> 'anylist':
    """ Every tool call the live gateway recorded, as the server's audit log has it, oldest first.
    """
    engine = _server_audit_engine()

    # The server creates the table with its first audit row, so until the first request lands there is nothing to read
    if not inspect(engine).has_table(event_table.name):
        return []

    query = select(event_table).\
        where(event_table.c.source == AuditSource.MCP).\
        where(event_table.c.object_name == _gateway_name).\
        where(event_table.c.event_type == AuditEvent.MCP_Tools_Call).\
        order_by(event_table.c.id)

    with engine.connect() as connection:
        out = [dict(row._mapping) for row in connection.execute(query)]

    return out

# ################################################################################################################################

def _get_stored_explanations() -> 'anylist':
    """ Every explanation the live server stored for the gateway, read off its own ODB - the proofs share the
    server, so this one reads the explanations of its own gateway alone.
    """
    path = os.path.join(os.path.dirname(LiveServer.server_directory), 'zato.db')
    session_maker = sessionmaker(bind=create_engine(f'sqlite:///{path}'))

    store = ExplanationStore(session_maker, default_cluster_id)

    # Our response to produce
    out:'anylist' = []

    for explanation in store.get_list():
        if explanation['source'] == AuditSource.MCP:
            if explanation['object_name'] == _gateway_name:
                out.append(explanation)

    for explanation in out:
        trace(Channel_Explain, Received, f'mcp {explanation["rule"]}: {explanation["message"]}')
        trace(Channel_Explain, Received, f'mcp {explanation["rule"]}: {explanation["explanation"]}')
        trace(Channel_Explain, Received, f'confidence: {explanation["confidence"]}, remediation: {explanation["remediation"]}')
        separator(Channel_Explain)

    return out

# ################################################################################################################################
# ################################################################################################################################
