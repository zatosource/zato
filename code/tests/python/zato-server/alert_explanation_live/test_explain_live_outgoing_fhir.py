# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The explain service end to end for an outgoing FHIR connection whose upstream answers with OperationOutcomes - a real
# quickstart server with REST channels of its own in front of the service that answers every call with an
# OperationOutcome of `exception` on a 500, the way a FHIR server answers for a resource it failed on. Real calls
# through the connection from inside the server, one real sweep, and the explained alert read off the server's own
# databases and received by a real SMTP receiver. The second proof gives a connection a health check, fired by the
# suite's own scheduler every second, and reads the pair each check writes under the connection's health source.

# stdlib
import os
from json import loads
from time import sleep, time

# SQLAlchemy
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import sessionmaker

# Zato
from zato.common.alerting.explain.evidence import Heading_Object
from zato.common.alerting.explain.settings_info import Label_Alerts, On
from zato.common.alerting.explain.store import ExplanationStore
from zato.common.api import Alerting, GENERIC, HL7
from zato.common.audit_log.api import AuditEvent, AuditSource, event_table
from zato.common.defaults import default_cluster_id
from zato.common.test.client import AdminClient

# Test helpers
from live_config import LiveServer
from live_trace import Channel_Explain, Channel_Outgoing, Received, Sent, separator, trace
from test_explain_live import _assert_sound_explanation, _email_to, _trace_delivery
from test_explain_live_channel import _find_by_name, _new_admin_client, _new_notification_config, _point_smtp_at_receiver, \
     _server_audit_engine, _unwrap
from test_explain_live_outgoing import _status_separator, _wrapper_wait_step, _wrapper_wait_timeout

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

class TestExplainLiveOutgoingFHIROutcomes:

    def test_a_fhir_outgoing_connections_outcomes_are_explained(
        self,
        ollama:'any_',
        zato_server:'any_',
        smtp_receiver:'any_',
        ) -> 'None':

        client = _new_admin_client()

        # The server's own notification connection delivers to the receiver ..
        _point_smtp_at_receiver(client, smtp_receiver)

        # .. a REST channel of the same server, in front of the service that answers with OperationOutcomes,
        # is the upstream every read of a Patient through the connection reaches ..
        channel_id = _create_outcome_channel(client, _patient_channel_name, _patient_channel_path)

        # .. and the connection points at it, with the audit log on and an outcome threshold four calls go past.
        address = _upstream_address()
        conn_id = _create_outcome_outgoing(client, _outcome_name, address)

        # The sweep explains through the LLM connection and mails from the address below
        notification_config = _new_notification_config()

        # Real calls through the connection, from inside the server, each answered with an OperationOutcome
        _produce_outcomes(client)

        # One real sweep inside the server - the collectors, the rules, the explain service and the delivery
        trace(Channel_Outgoing, Sent, f'invoke {Alerting.Service} with {notification_config}')
        _ = client.invoke(Alerting.Service, notification_config)

        # Each call is on record under the connection's name, the 500 as its status and the issue code
        # as what the OperationOutcome said ..
        responses = _get_outcome_responses(AuditSource.FHIR, _outcome_name)

        for row in responses:
            trace(Channel_Outgoing, Received, f'outcome audit log: {row["event_time_iso"]} {row["status"]!r} '
                f'{row["application_outcome"]!r} {row["data"]!r}')

        separator(Channel_Outgoing)

        assert len(responses) == _outcome_call_count

        for row in responses:
            assert row['status'].split(' ')[0] == _status_server_error, row
            assert row['application_outcome'] == LiveServer.outcome_code, row
            assert LiveServer.outcome_text in row['data'], row

        # .. the outcomes fired the outcomes rule and not the status codes one, because a 500 carrying
        # an OperationOutcome is counted as the issue code it carries ..
        explanations = _get_stored_outcome_explanations(AuditSource.FHIR, _outcome_name)
        by_rule = {}

        for explanation in explanations:
            assert explanation['object_name'] == _outcome_name
            assert explanation['source'] == AuditSource.FHIR
            by_rule[explanation['rule']] = explanation

        assert _outcomes_rule in by_rule, sorted(by_rule)
        assert _status_codes_rule not in by_rule, sorted(by_rule)

        explained = by_rule[_outcomes_rule]
        evidence = explained['evidence']

        # .. its Object is the connection's own, read from the generic connection row ..
        assert Heading_Object in evidence
        assert f'Name: {_outcome_name}' in evidence
        assert 'Type: FHIR' in evidence
        assert f'Address: {address}' in evidence
        assert f'{Label_Alerts}: {On}' in evidence

        # .. the failures are the outcomes, grouped under the status and the issue code the resource carried,
        # and the diagnostics text of the outcome is in the evidence ..
        assert _outcome_group in evidence
        assert LiveServer.outcome_text in evidence

        _assert_sound_explanation(explained, _outcome_words)

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

        _ = client.delete('zato.generic.connection.delete', id=conn_id)
        _ = client.delete('zato.http-soap.delete', id=channel_id)

# ################################################################################################################################
# ################################################################################################################################

class TestExplainLiveOutgoingFHIRHealthCheck:

    def test_a_fhir_outgoing_connections_health_check_is_explained(
        self,
        ollama:'any_',
        zato_server:'any_',
        scheduler_process:'any_',
        smtp_receiver:'any_',
        ) -> 'None':

        client = _new_admin_client()

        # The server's own notification connection delivers to the receiver ..
        _point_smtp_at_receiver(client, smtp_receiver)

        # .. a REST channel of the same server answers the connection's pings - a GET of the CapabilityStatement -
        # with the same OperationOutcome on a 500, so every check of the connection fails with an issue code ..
        channel_id = _create_outcome_channel(client, _capability_channel_name, _capability_channel_path)

        # .. and a FHIR connection with a health check every second and three failed checks bringing it down.
        address = _upstream_address()
        conn_id = _create_outcome_outgoing(client, _checked_name, address, is_checked=True)

        # The sweep explains through the LLM connection and mails from the address below
        notification_config = _new_notification_config()

        # The suite's own scheduler fires the check, the server pings and each ping lands under the health source
        pings = _wait_for_pings(_ping_count)

        for row in pings:
            assert row['status'].split(' ')[0] == _status_server_error, row
            assert row['application_outcome'] == LiveServer.outcome_code, row

        # A check is written under its own source, never under the connection's traffic
        assert _get_outcome_responses(AuditSource.FHIR, _checked_name) == []

        # One real sweep inside the server - the collectors, the rules, the explain service and the delivery
        trace(Channel_Outgoing, Sent, f'invoke {Alerting.Service} with {notification_config}')
        _ = client.invoke(Alerting.Service, notification_config)

        # The check's streak fired the down rule and was explained ..
        explanations = _get_stored_outcome_explanations(AuditSource.FHIR_Health, _checked_name)
        by_rule = {}

        for explanation in explanations:
            assert explanation['object_name'] == _checked_name
            assert explanation['source'] == AuditSource.FHIR_Health
            by_rule[explanation['rule']] = explanation

        assert _down_rule in by_rule, sorted(by_rule)

        explained = by_rule[_down_rule]
        evidence = explained['evidence']

        # .. its Object is the connection's own, read from the generic connection row, with how often the check runs ..
        assert Heading_Object in evidence
        assert f'Name: {_checked_name}' in evidence
        assert 'Type: FHIR' in evidence
        assert f'Address: {address}' in evidence
        assert f'Health check: every {_run_every} second' in evidence
        assert f'{Label_Alerts}: {On}' in evidence

        # .. the failures are the failed checks, grouped under the status and the issue code the resource carried ..
        assert _outcome_group in evidence

        _assert_sound_explanation(explained, _outcome_words)

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

        # Deleting the connection deletes its check job with it, so the scheduler stops pinging
        _ = client.delete('zato.generic.connection.delete', id=conn_id)
        _ = client.delete('zato.http-soap.delete', id=channel_id)

# ################################################################################################################################
# ################################################################################################################################

# The type of connection under proof
_fhir_type = GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR

# How many calls the proof makes through the connection - one more than the threshold below asks for
_outcome_call_count = 4
_outcome_threshold = 3

# The rules the outcomes fire, the one they leave alone and the one a failing check fires
_outcomes_rule = 'Operation_Outcomes'
_status_codes_rule = 'Status_Codes'
_down_rule = 'Connection_Down'

# The status the OperationOutcome arrives with
_status_server_error = '500'
_status_server_error_line = '500 Internal Server Error'

# What the failures of the explanation are grouped under - the status line and the issue code the resource carried
_outcome_group = _status_server_error_line + _status_separator + LiveServer.outcome_code

# The channels of the live server the connections call - open to everyone, in front of the service that answers
# with OperationOutcomes. The upstream's base path is what the connections carry as their address, the Patient
# channel answers the reads of the first proof and the CapabilityStatement channel the pings of the second.
_upstream_path = '/explain-live/upstream/fhir'
_patient_channel_name = 'explain.live.upstream.fhir.patient.channel'
_patient_channel_path = _upstream_path + '/Patient/{patient_id}'
_capability_channel_name = 'explain.live.upstream.fhir.capability.channel'
_capability_channel_path = _upstream_path + '/CapabilityStatement'

# The connection that reads Patients and the path each read asks for
_outcome_name = 'explain.live.upstream.fhir'
_patient_path = 'Patient/1'

# The connection whose health check the proof watches, how often it is pinged and the streak that brings it down
_checked_name = 'explain.live.upstream.fhir.checked'
_run_every = 1
_run_unit = 'seconds'
_consecutive_failures = 3

# How many pings to wait for - as many as the down rule needs - and how long to give the scheduler for them
_ping_count = _consecutive_failures
_ping_wait_timeout = 90
_ping_wait_step = 0.5

# The words a sound explanation of an upstream answering with exceptions is expected to use at least one of
_outcome_words = ['exception', 'fhir', 'server', 'backend', 'registry', 'upstream', 'outcome', '500', 'error', 'fail']

# ################################################################################################################################
# ################################################################################################################################

def _upstream_address() -> 'str':
    """ The base address of the upstream - the live server's own channels under the FHIR path.
    """
    out = f'http://{LiveServer.host}:{LiveServer.server_port}{_upstream_path}'
    return out

# ################################################################################################################################

def _create_outcome_channel(client:'AdminClient', name:'str', url_path:'str') -> 'int':
    """ A REST channel of the live server in front of the service that answers with OperationOutcomes - no security
    of its own, so every call gets through to the service and comes back as the outcome it builds.
    """
    existing = _find_by_name(client, 'zato.http-soap.get-list', name)

    if existing is not None:
        return existing['id']

    response = _unwrap(client.create('zato.http-soap.create',
        cluster_id=default_cluster_id,
        name=name,
        is_active=True,
        is_internal=False,
        connection='channel',
        transport='plain_http',
        data_format='json',
        url_path=url_path,
        service=LiveServer.outcome_service,
        is_audit_log_active=False,
        alert_is_active=False,
    ))
    out = response['id']

    trace(Channel_Outgoing, Sent, f'outcome channel `{name}` at {url_path} -> {LiveServer.outcome_service}')
    separator(Channel_Outgoing)

    return out

# ################################################################################################################################

def _create_outcome_outgoing(client:'AdminClient', name:'str', address:'str', *, is_checked:'bool'=False) -> 'int':
    """ A FHIR connection of the proof - the audit log on, the LLM explaining its alerts, no security of its own,
    the default outcome codes and a threshold low enough for four outcomes to fire its rule. A checked one is
    pinged every second and a streak of three failed checks brings it down.
    """
    request = {
        'cluster_id': default_cluster_id,
        'type_': _fhir_type,
        'name': name,
        'is_active': True,
        'is_internal': False,
        'is_channel': False,
        'is_outconn': True,
        'address': address,
        'pool_size': HL7.Default.pool_size,
        'security_id': 0,
        'auth_type': HL7.Const.FHIR_Auth_Type.No_Auth.id,
        'is_audit_log_active': True,
        'alert_is_active': True,
        'alert_use_llm': True,
        'alert_outcome_threshold': _outcome_threshold,
        'alert_consecutive_failures': _consecutive_failures,
    }

    if is_checked:
        request['health_check_run_every'] = _run_every
        request['health_check_run_unit'] = _run_unit

    response = _unwrap(client.create('zato.generic.connection.create', **request))
    out = response['id']

    if is_checked:
        trace(Channel_Outgoing, Sent, f'fhir connection `{name}` -> {address}, checked every {_run_every} {_run_unit}')
    else:
        trace(Channel_Outgoing, Sent, f'fhir connection `{name}` -> {address}')

    separator(Channel_Outgoing)

    return out

# ################################################################################################################################

def _invoke_outcome(client:'AdminClient') -> 'str':
    """ One read of a Patient through the connection, from inside the server - a connection just created takes
    a moment to appear among the server's wrappers, so the first call waits for it. The read comes back with
    the exception fhirpy raises for the status, as the invoke service's own text.
    """
    payload = {'conn_type': _fhir_type, 'conn_name': _outcome_name, 'request_data': _patient_path}
    deadline = time() + _wrapper_wait_timeout

    while True:
        try:
            response = _unwrap(client.invoke('zato.generic.connection.invoke', payload))
        except Exception as e:
            if _outcome_name in str(e) and time() < deadline:
                sleep(_wrapper_wait_step)
                continue
            raise
        else:
            out = response['response_data']
            return out

# ################################################################################################################################

def _produce_outcomes(client:'AdminClient') -> 'None':
    """ Real reads through the connection - each of them reaches the service that answers with an OperationOutcome
    and comes back as the exception fhirpy raises for a 500, with the outcome named on the trace.
    """
    for _ in range(_outcome_call_count):

        trace(Channel_Outgoing, Sent, f'outcome: GET {_patient_path} through `{_outcome_name}`')

        response = _invoke_outcome(client)

        # The read failed with the OperationOutcome the upstream built for it - the resource is the text
        # of the exception fhirpy raised, after the traceback that led to it
        outcome = loads(response[response.index('{'):])
        issue = outcome['issue'][0]

        trace(Channel_Outgoing, Received, f'outcome: {outcome["resourceType"]} {issue["code"]} - {issue["diagnostics"]}')
        separator(Channel_Outgoing)

        assert issue['code'] == LiveServer.outcome_code, response
        assert issue['diagnostics'] == LiveServer.outcome_text, response

# ################################################################################################################################

def _get_outcome_responses(source:'str', name:'str') -> 'anylist':
    """ Every response the live server received through the connection, as its audit log recorded it under the source.
    """
    engine = _server_audit_engine()

    # The server creates the table with its first audit row, so until the first call lands there is nothing to read
    if not inspect(engine).has_table(event_table.name):
        return []

    query = select(event_table).\
        where(event_table.c.source == source).\
        where(event_table.c.object_name == name).\
        where(event_table.c.event_type == AuditEvent.Response_Received).\
        order_by(event_table.c.id)

    with engine.connect() as connection:
        out = [dict(row._mapping) for row in connection.execute(query)]

    return out

# ################################################################################################################################

def _wait_for_pings(count:'int') -> 'anylist':
    """ Waits until the scheduler has fired the check that many times, naming each ping with its status and issue
    code as it lands.
    """
    deadline = time() + _ping_wait_timeout
    seen = 0

    while True:
        out = _get_outcome_responses(AuditSource.FHIR_Health, _checked_name)

        # Each new ping is traced once, when it first shows up
        for row in out[seen:]:
            trace(Channel_Outgoing, Received, f'fhir ping: {row["event_time_iso"]} {row["status"]!r} '
                f'{row["application_outcome"]!r}')

        seen = len(out)

        if seen >= count:
            separator(Channel_Outgoing)
            return out

        if time() > deadline:
            raise AssertionError(f'Expected {count} pings of `{_checked_name}` within {_ping_wait_timeout}s, found {seen}')

        sleep(_ping_wait_step)

# ################################################################################################################################

def _get_stored_outcome_explanations(source:'str', name:'str') -> 'anylist':
    """ Every explanation the live server stored for the connection under the source, read off its own ODB -
    the proofs share the server, so each one reads the explanations of its own connection alone.
    """
    path = os.path.join(os.path.dirname(LiveServer.server_directory), 'zato.db')
    session_maker = sessionmaker(bind=create_engine(f'sqlite:///{path}'))

    store = ExplanationStore(session_maker, default_cluster_id)

    # Our response to produce
    out:'anylist' = []

    for explanation in store.get_list():
        if explanation['source'] == source:
            if explanation['object_name'] == name:
                out.append(explanation)

    for explanation in out:
        trace(Channel_Explain, Received, f'fhir {explanation["rule"]}: {explanation["explanation"]}')
        trace(Channel_Explain, Received, f'confidence: {explanation["confidence"]}, remediation: {explanation["remediation"]}')
        separator(Channel_Explain)

    return out

# ################################################################################################################################
# ################################################################################################################################
