# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The explain service end to end for outgoing REST connections - a real quickstart server with three connections
# of its own imported through enmasse, the audit log on, each pointed at a different kind of trouble: a channel of
# the same server that rejects the connection's calls, a port nothing listens on, and a socket that accepts and
# never answers. Real calls through each connection, one real sweep inside the server, and the explained alerts
# read off the server's own databases and received by a real SMTP receiver. Then the same for a SOAP connection
# whose health check, fired by the suite's own scheduler every second, is refused until its streak brings it down.

# stdlib
import os
import socket
from contextlib import closing
from dataclasses import dataclass
from time import sleep, time

# SQLAlchemy
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import sessionmaker

# Zato
from zato.common.alerting.explain.evidence import Heading_Object
from zato.common.alerting.explain.settings_info import Label_Alerts, On
from zato.common.alerting.explain.store import ExplanationStore
from zato.common.api import Alerting
from zato.common.audit_log.api import AuditEvent, AuditSource, event_table
from zato.common.audit_log.common import TransportStatus
from zato.common.defaults import default_cluster_id
from zato.common.test.client import AdminClient

# Test helpers
from live_config import LiveServer
from live_enmasse import deactivate_document, get_id_by_name, import_document
from live_trace import Channel_Explain, Channel_Outgoing, Received, Sent, separator, trace
from test_explain_live import _assert_sound_explanation, _email_to, _trace_delivery
from test_explain_live_channel import _ensure_basic_auth, _new_admin_client, _new_notification_config, \
     _point_smtp_at_receiver, _security_name, _server_audit_engine, _unwrap

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class _OutgoingDescription:
    """ One outgoing connection the proof runs against - what it is called, where it points, which rule
    its failures fire, what its audit rows say and what the evidence of its explanation has to carry.
    """
    label:'str'
    name:'str'
    url_path:'str'
    rule:'str'
    status:'str'
    evidence_text:'str'
    words:'strlist'

# ################################################################################################################################
# ################################################################################################################################

class TestExplainLiveOutgoing:

    def test_outgoing_rest_failures_are_explained(
        self,
        ollama:'any_',
        zato_server:'any_',
        smtp_receiver:'any_',
        ) -> 'None':

        client = _new_admin_client()

        # The server's own notification connection delivers to the receiver ..
        _point_smtp_at_receiver(smtp_receiver)

        # .. a guarded channel of the same server is the upstream the rejected connection calls without credentials ..
        _ensure_basic_auth()
        channel_document = _create_guarded_channel()

        # .. nothing listens on this port, so the refused connection cannot connect ..
        refused_port = _find_closed_port()

        # .. and this socket accepts without ever answering, so the silent connection waits until its timeout.
        with closing(_new_silent_listener()) as listener:

            silent_port = listener.getsockname()[1]

            hosts = {
                _rejected.name: f'http://{LiveServer.host}:{LiveServer.server_port}',
                _refused.name: f'http://{LiveServer.host}:{refused_port}',
                _silent.name: f'http://{LiveServer.host}:{silent_port}',
            }

            # The three connections in one import, each with the audit log on and thresholds of its own
            outgoing_document = _create_outgoings(hosts)

            conn_ids = {}
            for outgoing in _outgoings:
                conn_ids[outgoing.name] = get_id_by_name(client, _http_soap_list_service, outgoing.name)

            # The sweep explains through the LLM connection and mails from the address below
            notification_config = _new_notification_config()

            # Real calls through each connection, from inside the server
            for outgoing in _outgoings:
                _produce_outgoing_failures(client, outgoing, conn_ids[outgoing.name])

            # One real sweep inside the server - the collectors, the rules, the explain service and the delivery
            trace(Channel_Outgoing, Sent, f'invoke {Alerting.Service} with {notification_config}')
            _ = client.invoke(Alerting.Service, notification_config)

        # Each connection's failing calls are on record under its own name, with the status the transport gave them ..
        for outgoing in _outgoings:
            responses = _get_outgoing_responses(outgoing)

            assert len(responses) == _outgoing_call_count

            for row in responses:
                assert row['status'].split(' ')[0] == outgoing.status, row

        # .. each connection's own rule fired and was explained, with the evidence of that connection alone ..
        for outgoing in _outgoings:

            explanations = _get_stored_explanations(outgoing)
            by_rule = {}

            for explanation in explanations:
                assert explanation['object_name'] == outgoing.name
                assert explanation['source'] == AuditSource.REST_Outgoing
                by_rule[explanation['rule']] = explanation

            assert outgoing.rule in by_rule, sorted(by_rule)

            explained = by_rule[outgoing.rule]
            evidence = explained['evidence']

            assert Heading_Object in evidence
            assert f'Name: {outgoing.name}' in evidence
            assert f'Address: {hosts[outgoing.name]}{outgoing.url_path}' in evidence
            assert f'Timeout: {_outgoing_timeout} s' in evidence
            assert f'{Label_Alerts}: {On}' in evidence
            assert outgoing.evidence_text in evidence

            # A rejected call's evidence never mentions the other connections' trouble
            for other in _outgoings:
                if other is not outgoing:
                    assert other.name not in evidence

            _assert_sound_explanation(explained, outgoing.words)

            # .. the one remediation an outgoing connection's explanation may propose is a resubmit ..
            for explanation in explanations:
                if explanation['remediation'] is not None:
                    assert explanation['remediation']['action'] == Alerting.Remediation_Resubmit, explanation

        # .. and every explained alert reached the mailbox.
        _trace_delivery(smtp_receiver)

        bodies = []
        for received in smtp_receiver.messages:
            assert received.recipients == _email_to
            bodies.append(received.body)

        for outgoing in _outgoings:
            for explanation in _get_stored_explanations(outgoing):
                for body in bodies:
                    if explanation['explanation'] in body:
                        break
                else:
                    raise AssertionError(f'Expected an email carrying {explanation["explanation"]!r}')

        deactivate_document(outgoing_document)
        deactivate_document(channel_document)

# ################################################################################################################################
# ################################################################################################################################

class TestExplainLiveOutgoingSOAP:

    def test_a_soap_outgoing_connections_health_check_is_explained(
        self,
        ollama:'any_',
        zato_server:'any_',
        scheduler_process:'any_',
        smtp_receiver:'any_',
        ) -> 'None':

        client = _new_admin_client()

        # The server's own notification connection delivers to the receiver ..
        _point_smtp_at_receiver(smtp_receiver)

        # .. nothing listens on this port, so every ping of the connection's health check is refused.
        refused_port = _find_closed_port()
        host = f'http://{LiveServer.host}:{refused_port}'

        # A SOAP connection with a health check every second and three failed checks bringing it down
        soap_document = _create_soap_outgoing(host)

        # The sweep explains through the LLM connection and mails from the address below
        notification_config = _new_notification_config()

        # The suite's own scheduler fires the check, the server pings and the pings land in the audit log
        pings = _wait_for_soap_pings(_soap_ping_count)

        for row in pings:
            assert row['status'] == TransportStatus.Connection_Error, row

        # One real sweep inside the server - the collectors, the rules, the explain service and the delivery
        trace(Channel_Outgoing, Sent, f'invoke {Alerting.Service} with {notification_config}')
        _ = client.invoke(Alerting.Service, notification_config)

        # The check's streak fired the down rule and was explained ..
        explanations = _get_stored_soap_health_explanations()
        by_rule = {}

        for explanation in explanations:
            assert explanation['object_name'] == _soap_name
            assert explanation['source'] == AuditSource.SOAP_Outgoing_Health
            by_rule[explanation['rule']] = explanation

        assert _soap_rule in by_rule, sorted(by_rule)

        explained = by_rule[_soap_rule]
        evidence = explained['evidence']

        # .. its Object is the connection's own, read from the SOAP row, with how often the check runs ..
        assert Heading_Object in evidence
        assert f'Name: {_soap_name}' in evidence
        assert 'Transport: SOAP' in evidence
        assert f'SOAP action: {_soap_action}' in evidence
        assert f'SOAP version: {_soap_version}' in evidence
        assert f'Address: {host}{_soap_url_path}' in evidence
        assert f'Health check: every {_soap_run_every} second' in evidence
        assert f'{Label_Alerts}: {On}' in evidence

        # .. the failures are the refused pings, grouped under the status the transport gave them ..
        assert TransportStatus.Connection_Error + _status_separator in evidence

        _assert_sound_explanation(explained, _refused_words)

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

        # The check job of an inactive connection is inactive with it, so the scheduler stops pinging
        deactivate_document(soap_document)

# ################################################################################################################################
# ################################################################################################################################

# How many calls the proof makes through each connection - one more than the thresholds below ask for
_outgoing_call_count = 4

# The thresholds each connection carries of its own, so four calls are enough for each rule
_status_code_threshold = 3
_connection_failures_threshold = 3

# The status codes the rejected connection watches for and the code the guarded channel answers with
_status_codes = '401, 403'
_status_unauthorized = '401'

# How long a call through a connection may take before the transport gives up, in seconds
_outgoing_timeout = 1

# How long to wait for a connection just created to appear among the server's wrappers, in seconds
_wrapper_wait_timeout = 30
_wrapper_wait_step = 0.5

# What the server says when a connection's wrapper is not there yet
_wrapper_not_found = 'not found'

# The list service a proof learns the id of a channel or an outgoing connection it imported through
_http_soap_list_service = 'zato.http-soap.get-list'

# The channel the rejected connection calls - the service behind it never runs, no call gets past the guard
_guarded_channel_name = 'explain.live.upstream.guarded'
_guarded_channel_path = '/explain-live/upstream/guarded'

# What a response whose status the transport gave says in its data - the failure's own text follows it
_status_separator = ' - '

# The words a sound explanation of each failure is expected to use at least one of
_rejected_words = ['auth', 'credential', 'password', '401', 'unauthori', 'reject', 'security']
_refused_words = ['refuse', 'connect', 'reach', 'listen', 'down', 'port', 'network']
_silent_words = ['timeout', 'timed out', 'time out', 'slow', 'respond', 'answer', 'wait']

# ################################################################################################################################

_rejected = _OutgoingDescription(
    label='rejected',
    name='explain.live.upstream.rejected',
    url_path=_guarded_channel_path,
    rule='Status_Codes',
    status=_status_unauthorized,
    evidence_text=_status_unauthorized,
    words=_rejected_words,
)

_refused = _OutgoingDescription(
    label='refused',
    name='explain.live.upstream.refused',
    url_path='/explain-live/upstream/refused',
    rule='Connection_Failures',
    status=TransportStatus.Connection_Error,
    evidence_text=TransportStatus.Connection_Error + _status_separator,
    words=_refused_words,
)

_silent = _OutgoingDescription(
    label='silent',
    name='explain.live.upstream.timeout',
    url_path='/explain-live/upstream/silent',
    rule='Connection_Failures',
    status=TransportStatus.Timeout,
    evidence_text=TransportStatus.Timeout + _status_separator,
    words=_silent_words,
)

_outgoings = [_rejected, _refused, _silent]

# ################################################################################################################################

# The SOAP connection whose health check the proof watches - what it calls and how often it is pinged
_soap_name = 'explain.live.upstream.soap'
_soap_url_path = '/explain-live/upstream/soap'
_soap_action = 'urn:explain-live:orders'
_soap_version = '1.1'

# The check runs every second and three failed checks in a row bring the connection down
_soap_run_every = 1
_soap_run_unit = 'seconds'
_soap_consecutive_failures = 3
_soap_rule = 'Connection_Down'

# How many pings to wait for - as many as the rule needs
_soap_ping_count = _soap_consecutive_failures

# How long to wait for the scheduler to fire the check that many times, in seconds - the job is created
# once the connection is, and the scheduler picks it up from its command stream before the first fire
_soap_ping_wait_timeout = 90
_soap_ping_wait_step = 0.5

# ################################################################################################################################
# ################################################################################################################################

def _find_closed_port() -> 'int':
    """ A port the kernel just handed out and released - nothing listens on it, so a connection to it is refused.
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind((LiveServer.host, 0))
        out = sock.getsockname()[1]

    return out

# ################################################################################################################################

def _new_silent_listener() -> 'socket.socket':
    """ A socket that accepts connections in its backlog and never reads from or writes to any of them -
    a client connects fine and then waits for an answer that never comes.
    """
    out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    out.bind((LiveServer.host, 0))
    out.listen()

    return out

# ################################################################################################################################

def _create_guarded_channel() -> 'anydict':
    """ A channel of the live server that only callers with the partner's credentials get through -
    the rejected connection calls it with none and is turned away with a 401 each time. What is returned
    is the document the channel went in with, for the proof to deactivate it with once it is through.
    """
    out = {
        'channel_rest': [{
            'name': _guarded_channel_name,
            'is_active': True,
            'service': LiveServer.raising_service,
            'url_path': _guarded_channel_path,
            'security': _security_name,
            'data_format': 'json',
            'is_audit_log_active': False,
            'alerts': {
                'is_active': False,
            },
        }],
    }

    import_document(out)

    trace(Channel_Outgoing, Sent, f'guarded channel `{_guarded_channel_name}` at {_guarded_channel_path} behind {_security_name}')
    separator(Channel_Outgoing)

    return out

# ################################################################################################################################

def _create_outgoings(hosts:'anydict') -> 'anydict':
    """ The outgoing connections of the proof in one import - each with the audit log on, the LLM explaining its
    alerts, no security of its own, a short timeout and thresholds low enough for four calls to fire its rule.
    What is returned is the document they went in with, for the proof to deactivate them with once it is through.
    """
    definitions = []

    for outgoing in _outgoings:
        host = hosts[outgoing.name]

        definitions.append({
            'name': outgoing.name,
            'is_active': True,
            'host': host,
            'url_path': outgoing.url_path,
            'data_format': 'json',
            'timeout': _outgoing_timeout,
            'is_audit_log_active': True,
            'alerts': {
                'is_active': True,
                'use_llm': True,
                'status_codes': _status_codes,
                'status_code_threshold': _status_code_threshold,
                'connection_failures': _connection_failures_threshold,
            },
        })

        trace(Channel_Outgoing, Sent, f'{outgoing.label} connection `{outgoing.name}` -> {host}{outgoing.url_path}')

    separator(Channel_Outgoing)

    out = {'outgoing_rest': definitions}

    import_document(out)

    return out

# ################################################################################################################################

def _invoke_outgoing(client:'AdminClient', conn_id:'int') -> 'anydict':
    """ One call through a connection, from inside the server - a connection just created takes a moment
    to appear among the server's wrappers, so the first call waits for it.
    """
    payload = {'id': conn_id, 'request_method': 'GET'}
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

def _produce_outgoing_failures(client:'AdminClient', outgoing:'_OutgoingDescription', conn_id:'int') -> 'None':
    """ Real calls through one connection - each of them fails the way the connection's upstream makes it fail.
    """
    for _ in range(_outgoing_call_count):

        trace(Channel_Outgoing, Sent, f'{outgoing.label}: GET through `{outgoing.name}`')

        response = _invoke_outgoing(client, conn_id)

        trace(Channel_Outgoing, Received, f'{outgoing.label}: status {response["status_code"]} in {response["response_time"]}')
        trace(Channel_Outgoing, Received, response['response_body'])
        separator(Channel_Outgoing)

        # A rejected call comes back with the channel's status, a transport failure with none
        if outgoing is _rejected:
            assert str(response['status_code']) == _status_unauthorized, response
        else:
            assert response['status_code'] == 0, response

# ################################################################################################################################

def _get_outgoing_responses(outgoing:'_OutgoingDescription') -> 'anylist':
    """ Every response the live server received, or failed to receive, through the connection,
    as its audit log recorded it under the outgoing source.
    """
    engine = _server_audit_engine()

    query = select(event_table).\
        where(event_table.c.source == AuditSource.REST_Outgoing).\
        where(event_table.c.object_name == outgoing.name).\
        where(event_table.c.event_type == AuditEvent.Response_Received)

    with engine.connect() as connection:
        out = [dict(row._mapping) for row in connection.execute(query)]

    for row in out:
        trace(Channel_Outgoing, Received, f'{outgoing.label} audit log: {row["event_time_iso"]} {row["status"]!r} {row["data"]!r}')

    separator(Channel_Outgoing)

    return out

# ################################################################################################################################

def _get_stored_explanations(outgoing:'_OutgoingDescription') -> 'anylist':
    """ Every explanation the live server stored for the connection, read off its own ODB - the proofs share
    the server, so this one reads the explanations of its own connections alone.
    """
    path = os.path.join(os.path.dirname(LiveServer.server_directory), 'zato.db')
    session_maker = sessionmaker(bind=create_engine(f'sqlite:///{path}'))

    store = ExplanationStore(session_maker, default_cluster_id)

    # Our response to produce
    out:'anylist' = []

    for explanation in store.get_list():
        if explanation['source'] == AuditSource.REST_Outgoing:
            if explanation['object_name'] == outgoing.name:
                out.append(explanation)

    for explanation in out:
        trace(Channel_Explain, Received, f'{outgoing.label} {explanation["rule"]}: {explanation["explanation"]}')
        trace(Channel_Explain, Received, f'confidence: {explanation["confidence"]}, remediation: {explanation["remediation"]}')
        separator(Channel_Explain)

    return out

# ################################################################################################################################

def _create_soap_outgoing(host:'str') -> 'anydict':
    """ The SOAP connection of the proof - the audit log on, the LLM explaining its alerts, no security of its own,
    a health check every second and a streak of three failed checks bringing it down. What is returned is the
    document it went in with, for the proof to deactivate it with once it is through.
    """
    out = {
        'outgoing_soap': [{
            'name': _soap_name,
            'is_active': True,
            'host': host,
            'url_path': _soap_url_path,
            'soap_action': _soap_action,
            'soap_version': _soap_version,
            'data_format': 'xml',
            'timeout': _outgoing_timeout,
            'is_audit_log_active': True,
            'health_check_run_every': _soap_run_every,
            'health_check_run_unit': _soap_run_unit,
            'alerts': {
                'is_active': True,
                'use_llm': True,
                'consecutive_failures': _soap_consecutive_failures,
            },
        }],
    }

    import_document(out)

    trace(Channel_Outgoing, Sent, f'soap connection `{_soap_name}` -> {host}{_soap_url_path}, '
        f'checked every {_soap_run_every} {_soap_run_unit}')
    separator(Channel_Outgoing)

    return out

# ################################################################################################################################

def _get_soap_pings() -> 'anylist':
    """ Every ping the live server's scheduler had it make through the SOAP connection so far,
    as its audit log recorded it under the connection's health source.
    """
    engine = _server_audit_engine()

    # The server creates the table with its first audit row, so until the first ping lands there is nothing to read
    if not inspect(engine).has_table(event_table.name):
        return []

    query = select(event_table).\
        where(event_table.c.source == AuditSource.SOAP_Outgoing_Health).\
        where(event_table.c.object_name == _soap_name).\
        where(event_table.c.event_type == AuditEvent.Response_Received).\
        order_by(event_table.c.id)

    with engine.connect() as connection:
        out = [dict(row._mapping) for row in connection.execute(query)]

    return out

# ################################################################################################################################

def _wait_for_soap_pings(count:'int') -> 'anylist':
    """ Waits until the scheduler has fired the check that many times, naming each ping as it lands.
    """
    deadline = time() + _soap_ping_wait_timeout
    seen = 0

    while True:
        out = _get_soap_pings()

        # Each new ping is traced once, when it first shows up
        for row in out[seen:]:
            trace(Channel_Outgoing, Received, f'soap ping: {row["event_time_iso"]} {row["status"]!r} {row["data"]!r}')

        seen = len(out)

        if seen >= count:
            separator(Channel_Outgoing)
            return out

        if time() > deadline:
            raise AssertionError(f'Expected {count} pings of `{_soap_name}` within {_soap_ping_wait_timeout}s, found {seen}')

        sleep(_soap_ping_wait_step)

# ################################################################################################################################

def _get_stored_soap_health_explanations() -> 'anylist':
    """ Every explanation the live server stored for the SOAP connection's health check, read off its own ODB.
    """
    path = os.path.join(os.path.dirname(LiveServer.server_directory), 'zato.db')
    session_maker = sessionmaker(bind=create_engine(f'sqlite:///{path}'))

    store = ExplanationStore(session_maker, default_cluster_id)

    # Our response to produce
    out:'anylist' = []

    for explanation in store.get_list():
        if explanation['source'] == AuditSource.SOAP_Outgoing_Health:
            if explanation['object_name'] == _soap_name:
                out.append(explanation)

    for explanation in out:
        trace(Channel_Explain, Received, f'soap check {explanation["rule"]}: {explanation["explanation"]}')
        trace(Channel_Explain, Received, f'confidence: {explanation["confidence"]}, remediation: {explanation["remediation"]}')
        separator(Channel_Explain)

    return out

# ################################################################################################################################
# ################################################################################################################################
