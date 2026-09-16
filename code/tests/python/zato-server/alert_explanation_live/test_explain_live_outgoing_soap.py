# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The explain service end to end for an outgoing SOAP connection whose upstream answers with faults - a real
# quickstart server with a SOAP channel of its own in front of the service that always raises, both imported
# through enmasse, so every call through the connection comes back as a Receiver fault on a 500. Real calls
# through the connection from inside the server, one real sweep, and the explained alert read off the server's
# own databases and received by a real SMTP receiver. The health check proof of a SOAP connection lives next door,
# in test_explain_live_outgoing.

# stdlib
import os
from time import sleep, time

# SQLAlchemy
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

# Zato
from zato.common.alerting.explain.evidence import Heading_Object
from zato.common.alerting.explain.settings_info import Label_Alerts, On
from zato.common.alerting.explain.store import ExplanationStore
from zato.common.api import Alerting
from zato.common.audit_log.api import AuditEvent, AuditSource, event_table
from zato.common.defaults import default_cluster_id
from zato.common.soap.common import FaultCode
from zato.common.test.client import AdminClient

# Test helpers
from live_config import LiveServer
from live_enmasse import deactivate_document, get_id_by_name, import_document
from live_trace import Channel_Explain, Channel_Outgoing, Received, Sent, separator, trace
from test_explain_live import _assert_sound_explanation, _email_to, _trace_delivery
from test_explain_live_channel import _new_admin_client, _new_notification_config, _point_smtp_at_receiver, \
     _server_audit_engine, _soap_fault_string, unwrap as _unwrap
from test_explain_live_outgoing import _http_soap_list_service, _outgoing_timeout, _soap_action, _status_separator, \
     _wrapper_not_found, _wrapper_wait_step, _wrapper_wait_timeout

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

class TestExplainLiveOutgoingSOAPFaults:

    def test_a_soap_outgoing_connections_faults_are_explained(
        self,
        ollama:'any_',
        zato_server:'any_',
        smtp_receiver:'any_',
        ) -> 'None':

        client = _new_admin_client()

        # The server's own notification connection delivers to the receiver ..
        _point_smtp_at_receiver(smtp_receiver)

        # .. a SOAP channel of the same server, in front of the service that raises, is the upstream every call
        # of the connection reaches and comes back from with a fault ..
        channel_document = _create_faulting_channel()

        # .. and the connection points at it, with the audit log on and a fault threshold four calls go past.
        host = f'http://{LiveServer.host}:{LiveServer.server_port}'
        outgoing_document = _create_faulting_outgoing(host)
        conn_id = get_id_by_name(client, _http_soap_list_service, _faulting_name)

        # The sweep explains through the LLM connection and mails from the address below
        notification_config = _new_notification_config()

        # Real calls through the connection, from inside the server, each answered with a fault
        _produce_faults(client, conn_id)

        # One real sweep inside the server - the collectors, the rules, the explain service and the delivery
        trace(Channel_Outgoing, Sent, f'invoke {Alerting.Service} with {notification_config}')
        _ = client.invoke(Alerting.Service, notification_config)

        # Each faulting call is on record under the connection's name, the 500 as its status and the fault's code
        # as what the envelope said ..
        responses = _get_fault_responses()

        assert len(responses) == _fault_call_count

        for row in responses:
            assert row['status'].split(' ')[0] == _status_server_error, row
            assert row['application_outcome'] == FaultCode.Receiver, row

        # .. the faults fired the faults rule and not the status codes one, because a 500 carrying a fault
        # is counted as the fault it carries ..
        explanations = _get_stored_fault_explanations()
        by_rule = {}

        for explanation in explanations:
            assert explanation['object_name'] == _faulting_name
            assert explanation['source'] == AuditSource.SOAP_Outgoing
            by_rule[explanation['rule']] = explanation

        assert _faults_rule in by_rule, sorted(by_rule)
        assert _status_codes_rule not in by_rule, sorted(by_rule)

        explained = by_rule[_faults_rule]
        evidence = explained['evidence']

        # .. its Object is the connection's own, read from the SOAP row ..
        assert Heading_Object in evidence
        assert f'Name: {_faulting_name}' in evidence
        assert 'Transport: SOAP' in evidence
        assert f'SOAP action: {_soap_action}' in evidence
        assert f'SOAP version: {_soap_version}' in evidence
        assert f'Address: {host}{_faulting_channel_path}' in evidence
        assert f'Timeout: {_outgoing_timeout} s' in evidence
        assert f'{Label_Alerts}: {On}' in evidence

        # .. the failures are the faults, grouped under the status and the code the envelope carried,
        # and the fault's own text is in the evidence ..
        assert _fault_group in evidence
        assert _soap_fault_string in evidence

        _assert_sound_explanation(explained, _faulting_words)

        # .. the one remediation an outgoing connection's explanation may propose is a resubmit ..
        for explanation in explanations:
            if explanation['remediation'] is not None:
                assert explanation['remediation']['action'] == Alerting.Remediation_Resubmit, explanation

        # .. and the explained alert reached the mailbox.
        _trace_delivery(smtp_receiver)

        bodies = []
        for received in smtp_receiver.messages:
            assert received.recipients == _email_to
            bodies.append(received.body)

        for body in bodies:
            if explained['explanation'] in body:
                break
        else:
            raise AssertionError(f'Expected an email carrying {explained["explanation"]!r}')

        deactivate_document(outgoing_document)
        deactivate_document(channel_document)

# ################################################################################################################################
# ################################################################################################################################

# How many calls the proof makes through the connection - one more than the threshold below asks for
_fault_call_count = 4
_fault_threshold = 3

# The rule the faults fire and the one they leave alone
_faults_rule = 'SOAP_Faults'
_status_codes_rule = 'Status_Codes'

# The status a fault built for a service that raised arrives with
_status_server_error = '500'
_status_server_error_line = '500 Internal Server Error'

# What the failures of the explanation are grouped under - the status line and the code the envelope carried
_fault_group = _status_server_error_line + _status_separator + FaultCode.Receiver

# The channel of the live server the connection calls - open to everyone, in front of the service that raises
_faulting_channel_name = 'explain.live.upstream.faulting.channel'
_faulting_channel_path = '/explain-live/upstream/faulting'

# The version the channel and the connection speak - 1.2, whose fault for a service that raised is a Receiver one,
# where 1.1 would call the same fault a Server one
_soap_version = '1.2'

# The connection itself and the operation its calls carry
_faulting_name = 'explain.live.upstream.faulting'
_faulting_operation = 'orders'
_faulting_message = f'<{_faulting_operation} xmlns="{_soap_action}"><order_id>ORD-1</order_id></{_faulting_operation}>'

# The words a sound explanation of a faulting upstream is expected to use at least one of
_faulting_words = ['fault', 'receiver', 'server', 'backend', 'exception', 'raise', 'service', '500', 'error']

# ################################################################################################################################
# ################################################################################################################################

def _create_faulting_channel() -> 'anydict':
    """ A SOAP channel of the live server in front of the service that raises - no security of its own,
    so every call gets through to the service and comes back as the fault the server builds for it.
    What is returned is the document the channel went in with, for the proof to deactivate it with once it is through.
    """
    out = {
        'channel_soap': [{
            'name': _faulting_channel_name,
            'is_active': True,
            'service': LiveServer.raising_service,
            'url_path': _faulting_channel_path,
            'soap_action': _soap_action,
            'soap_version': _soap_version,
            'data_format': 'xml',
            'is_audit_log_active': False,
            'alerts': {
                'is_active': False,
            },
        }],
    }

    import_document(out)

    trace(Channel_Outgoing, Sent, f'faulting channel `{_faulting_channel_name}` at {_faulting_channel_path} -> ' +
        f'{LiveServer.raising_service}')
    separator(Channel_Outgoing)

    return out

# ################################################################################################################################

def _create_faulting_outgoing(host:'str') -> 'anydict':
    """ The SOAP connection of the proof - the audit log on, the LLM explaining its alerts, no security of its own,
    the default fault codes and a threshold low enough for four faults to fire its rule. What is returned is the
    document it went in with, for the proof to deactivate it with once it is through.
    """
    out = {
        'outgoing_soap': [{
            'name': _faulting_name,
            'is_active': True,
            'host': host,
            'url_path': _faulting_channel_path,
            'soap_action': _soap_action,
            'soap_version': _soap_version,
            'data_format': 'xml',
            'timeout': _outgoing_timeout,
            'is_audit_log_active': True,
            'alerts': {
                'is_active': True,
                'use_llm': True,
                'fault_threshold': _fault_threshold,
            },
        }],
    }

    import_document(out)

    trace(Channel_Outgoing, Sent, f'faulting connection `{_faulting_name}` -> {host}{_faulting_channel_path}')
    separator(Channel_Outgoing)

    return out

# ################################################################################################################################

def _invoke_faulting(client:'AdminClient', conn_id:'int') -> 'anydict':
    """ One call through the connection, from inside the server, with the operation and its message - a connection
    just created takes a moment to appear among the server's wrappers, so the first call waits for it.
    """
    payload = {'id': conn_id, 'operation': _faulting_operation, 'payload': _faulting_message}
    deadline = time() + _wrapper_wait_timeout

    while True:
        try:
            out = _unwrap(client.invoke('zato.http-soap.invoke-outconn', payload))
        except Exception as e:
            if _wrapper_not_found in str(e) and time() < deadline:
                sleep(_wrapper_wait_step)
                continue
            raise
        else:
            return out

# ################################################################################################################################

def _produce_faults(client:'AdminClient', conn_id:'int') -> 'None':
    """ Real calls through the connection - each of them reaches the service that raises and comes back
    as the fault the server built for it, with its status and code named on the trace.
    """
    for _ in range(_fault_call_count):

        trace(Channel_Outgoing, Sent, f'faulting: {_faulting_operation} through `{_faulting_name}`')

        response = _invoke_faulting(client, conn_id)

        trace(Channel_Outgoing, Received, f'faulting: status {response["status_code"]} in {response["response_time"]}')
        trace(Channel_Outgoing, Received, f'faulting: fault {response["response_body"]}')
        separator(Channel_Outgoing)

        # The fault arrives with the 500 the server gave it and its code and reason are the body of the answer
        assert str(response['status_code']) == _status_server_error, response
        assert response['response_body'].startswith(FaultCode.Receiver), response
        assert _soap_fault_string in response['response_body'], response

# ################################################################################################################################

def _get_fault_responses() -> 'anylist':
    """ Every response the live server received through the connection, as its audit log recorded it
    under the SOAP outgoing source.
    """
    engine = _server_audit_engine()

    query = select(event_table).\
        where(event_table.c.source == AuditSource.SOAP_Outgoing).\
        where(event_table.c.object_name == _faulting_name).\
        where(event_table.c.event_type == AuditEvent.Response_Received)

    with engine.connect() as connection:
        out = [dict(row._mapping) for row in connection.execute(query)]

    for row in out:
        trace(Channel_Outgoing, Received, f'faulting audit log: {row["event_time_iso"]} {row["status"]!r} ' +
            f'{row["application_outcome"]!r} {row["data"]!r}')

    separator(Channel_Outgoing)

    return out

# ################################################################################################################################

def _get_stored_fault_explanations() -> 'anylist':
    """ Every explanation the live server stored for the connection, read off its own ODB - the proofs share
    the server, so this one reads the explanations of its own connection alone.
    """
    path = os.path.join(os.path.dirname(LiveServer.server_directory), 'zato.db')
    session_maker = sessionmaker(bind=create_engine(f'sqlite:///{path}'))

    store = ExplanationStore(session_maker, default_cluster_id)

    # Our response to produce
    out:'anylist' = []

    for explanation in store.get_list():
        if explanation['source'] == AuditSource.SOAP_Outgoing:
            if explanation['object_name'] == _faulting_name:
                out.append(explanation)

    for explanation in out:
        trace(Channel_Explain, Received, f'faulting {explanation["rule"]}: {explanation["explanation"]}')
        trace(Channel_Explain, Received, f'confidence: {explanation["confidence"]}, remediation: {explanation["remediation"]}')
        separator(Channel_Explain)

    return out

# ################################################################################################################################
# ################################################################################################################################
