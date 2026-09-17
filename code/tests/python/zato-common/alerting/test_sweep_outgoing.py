# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# One sweep over outgoing REST connections with settings of their own - a connection's own status codes decide
# which responses the Status_Codes rule counts, timeouts and refused connections raise Connection_Failures, a
# connection with alerts off is skipped together with its health check, and its own window reaches its traffic
# source alone while the check source keeps its hour.

# stdlib
from datetime import timedelta

# SQLAlchemy
from sqlalchemy import update

# Zato
from zato.common.alerting.engine import AlertDefaults, AlertTransports
from zato.common.alerting.object_config import alert_type_fhir, alert_type_rest, alert_type_soap, \
    get_defaults as get_object_defaults
from zato.common.alerting.seed.rules_connections import rest_rules, soap_rules
from zato.common.alerting.seed.rules_fhir import fhir_rules
from zato.common.alerting.sweep import run_sweep
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.common import TransportStatus
from zato.common.rule_engine.loading import load_documents
from zato.common.rule_engine.parser import parse_data_details
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Engine
    from zato.common.alerting.sweep import rule_engine_rule_list, SweepResult
    from zato.common.typing_ import any_, anydict, anylist, stranydict
    any_ = any_
    anydict = anydict
    anylist = anylist
    datetime = datetime
    Engine = Engine
    rule_engine_rule_list = rule_engine_rule_list
    stranydict = stranydict
    SweepResult = SweepResult

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-sweep-outgoing-server'

# The ruleset the connections are judged by - the one the seed ships
_ruleset_name = 'alerts_rest'
_soap_ruleset_name = 'alerts_soap'
_fhir_ruleset_name = 'alerts_fhir'

# The connection with settings of its own and the one without any
_conn_name = 'crm.api'
_other_conn_name = 'billing.api'

# The addresses the email rules send to
_addresses = ['ops@example.com']

# ################################################################################################################################
# ################################################################################################################################

class _TransportRecorder:
    """ A stand-in for the real transports, remembering everything that went out.
    """
    def __init__(self) -> 'None':
        self.emails:'anylist' = []

    def make(self) -> 'AlertTransports':
        out = AlertTransports()

        def send_email(addresses:'anylist', subject:'str', body:'str', email_connection:'str'='') -> 'None':
            self.emails.append((addresses, subject, body))

        def invoke_service(service:'str', payload:'stranydict') -> 'None':
            pass

        def publish(topic:'str', payload:'stranydict') -> 'None':
            pass

        def http_post(url:'str', payload:'stranydict') -> 'None':
            pass

        out.send_email = send_email
        out.invoke_service = invoke_service
        out.publish = publish
        out.http_post = http_post

        return out

# ################################################################################################################################

def _load_rest_rules() -> 'rule_engine_rule_list':
    """ The seeded rest, soap and fhir rules as runtime rules, all of them active - each outgoing kind
    is judged by the ruleset of its own type.
    """
    out = []

    for ruleset_name, contents in ((_ruleset_name, rest_rules), (_soap_ruleset_name, soap_rules), (_fhir_ruleset_name, fhir_rules)):
        documents, errors = parse_data_details(contents, ruleset_name)
        assert errors == []

        loaded = load_documents(documents)

        for full_name in loaded.rule_names:
            out.append(loaded.manager[full_name])

    return out

# ################################################################################################################################

def _seed_call(audit_log:'AuditLog', engine:'Engine', now:'datetime', cid:'str', status:'str', *,
    object_name:'str'=_conn_name, seconds_back:'int'=0, source:'str'=AuditSource.REST_Outgoing, fault_code:'str'='') -> 'None':
    """ Stores the request and response pair one call of a connection leaves behind, moved back in time if asked to,
    a SOAP fault carrying its code on top of its status.
    """
    if status.startswith('2'):
        outcome = AuditOutcome.OK
    else:
        outcome = AuditOutcome.Error

    request_id = audit_log.insert(source, AuditEvent.Request_Sent, object_name, cid=cid, outcome=AuditOutcome.OK)

    response_id = audit_log.insert(source, AuditEvent.Response_Received, object_name, cid=cid,
        outcome=outcome, status=status, application_outcome=fault_code, duration_ms=20)

    if seconds_back:
        event_time_iso = (now - timedelta(seconds=seconds_back)).isoformat()

        statement = update(event_table)
        statement = statement.where(event_table.c.id.in_([request_id, response_id]))
        statement = statement.values(event_time_iso=event_time_iso)

        with engine.begin() as connection:
            _ = connection.execute(statement)

# ################################################################################################################################

def _seed_failures(audit_log:'AuditLog', engine:'Engine', now:'datetime', prefix:'str', count:'int', status:'str', *,
    object_name:'str'=_conn_name, seconds_back:'int'=0, source:'str'=AuditSource.REST_Outgoing, fault_code:'str'='') -> 'None':
    """ Stores the given number of calls that failed with the status, each followed by a call that went through,
    so the failures never form an unbroken streak and only the rules about counts and rates see them.
    """
    for idx in range(count):
        _seed_call(audit_log, engine, now, f'{prefix}-{idx}-failed', status, object_name=object_name,
            seconds_back=seconds_back, source=source, fault_code=fault_code)
        _seed_call(audit_log, engine, now, f'{prefix}-{idx}-ok', '200 OK', object_name=object_name,
            seconds_back=seconds_back, source=source)

# ################################################################################################################################

def _new_object_settings(alert_type:'str'=alert_type_rest, **values:'any_') -> 'anydict':
    """ The object settings of one outgoing connection of the type at the defaults, with the given values on top.
    The LLM stays out of it, so the actions run directly and can be observed.
    """
    settings = get_object_defaults(alert_type)
    settings['use_llm'] = False
    settings.update(values)

    out = {alert_type: {_conn_name: settings}}
    return out

# ################################################################################################################################

def _run_rest_sweep(engine:'Engine', audit_log:'AuditLog', now:'datetime', cid:'str',
    object_settings:'anydict | None') -> 'tuple[SweepResult, _TransportRecorder]':
    """ Runs one sweep of the seeded rest ruleset with the given object settings.
    """
    defaults = AlertDefaults()
    defaults.email_to = _addresses

    recorder = _TransportRecorder()
    rules = _load_rest_rules()

    result = run_sweep(engine, rules, {}, AuditSource.MLLP_Channel, recorder.make(), audit_log, cid, now,
        defaults=defaults, object_settings=object_settings)

    return result, recorder

# ################################################################################################################################

def _rule_names(result:'SweepResult') -> 'list':
    """ The names of the rules that dispatched an action, in order.
    """
    out = []
    for rule_name, _ in result.dispatched:
        out.append(rule_name)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingRestSweep:

    def test_the_default_codes_fire_on_a_503_and_not_on_a_404(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Three 404s - not among the default 401, 403 and 5xx, and too few for the error rate ..
        _seed_failures(audit_log, engine, now, 'nf', 3, '404 Not Found')
        _seed_failures(audit_log, engine, now, 'ok', 30, '200 OK')

        result, recorder = _run_rest_sweep(engine, audit_log, now, 'cid-rest-default-1', None)

        assert result.raised_count == 0
        assert recorder.emails == []

        # .. and three 503s are.
        _seed_failures(audit_log, engine, now, 'down', 3, '503 Service Unavailable')

        result, recorder = _run_rest_sweep(engine, audit_log, now, 'cid-rest-default-2', None)

        assert _rule_names(result) == ['Status_Codes']
        assert len(recorder.emails) == 1

        _, _, body = recorder.emails[0]
        assert _conn_name in body
        assert '3 responses with a status the connection alerts on (503 x3)' in body

# ################################################################################################################################

    def test_the_connections_own_codes_stand_in_for_the_default(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_failures(audit_log, engine, now, 'nf', 3, '404 Not Found')
        _seed_failures(audit_log, engine, now, 'ok', 30, '200 OK')

        # The connection alerts on 404s of its own accord ..
        object_settings = _new_object_settings(status_codes='404')
        result, recorder = _run_rest_sweep(engine, audit_log, now, 'cid-rest-own-1', object_settings)

        assert _rule_names(result) == ['Status_Codes']

        _, _, body = recorder.emails[0]
        assert '3 responses with a status the connection alerts on (404 x3)' in body

        # .. and the other way round - 503s the connection does not alert on raise nothing for it.
        _seed_failures(audit_log, engine, now, 'down', 3, '503 Service Unavailable', object_name=_other_conn_name)
        _seed_failures(audit_log, engine, now, 'ok-other', 30, '200 OK', object_name=_other_conn_name)

        object_settings = _new_object_settings(status_codes='401')
        result, recorder = _run_rest_sweep(engine, audit_log, now, 'cid-rest-own-2', object_settings)

        # The other connection, on the defaults, is the one alerted on
        assert _rule_names(result) == ['Status_Codes']

        _, _, body = recorder.emails[0]
        assert _other_conn_name in body
        assert _conn_name not in body

# ################################################################################################################################

    def test_the_connections_own_threshold_stands_in_for_the_rules_default(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_failures(audit_log, engine, now, 'down', 2, '503 Service Unavailable')
        _seed_failures(audit_log, engine, now, 'ok', 30, '200 OK')

        # Two are under the rule's three ..
        result, _ = _run_rest_sweep(engine, audit_log, now, 'cid-rest-threshold-1', None)
        assert result.raised_count == 0

        # .. and enough once the connection asks for two.
        object_settings = _new_object_settings(status_code_threshold=2)
        result, _ = _run_rest_sweep(engine, audit_log, now, 'cid-rest-threshold-2', object_settings)

        assert _rule_names(result) == ['Status_Codes']

# ################################################################################################################################

    def test_timeouts_and_refused_connections_raise_connection_failures(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_failures(audit_log, engine, now, 'timeout', 2, TransportStatus.Timeout)
        _seed_failures(audit_log, engine, now, 'refused', 1, TransportStatus.Connection_Error)
        _seed_failures(audit_log, engine, now, 'ok', 30, '200 OK')

        result, recorder = _run_rest_sweep(engine, audit_log, now, 'cid-rest-failures', None)

        # The transport statuses are no status codes, so only the failures rule speaks
        assert _rule_names(result) == ['Connection_Failures']

        _, _, body = recorder.emails[0]
        assert _conn_name in body
        assert '3 timeouts or connection failures' in body

# ################################################################################################################################

    def test_a_connection_with_alerts_off_is_skipped_with_its_health_check(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # The connection fails on its calls and on its checks, and so does the other one
        _seed_failures(audit_log, engine, now, 'down-a', 3, '503 Service Unavailable')
        _seed_failures(audit_log, engine, now, 'down-b', 3, '503 Service Unavailable', object_name=_other_conn_name)

        for idx in range(3):
            _seed_call(audit_log, engine, now, f'check-a-{idx}', TransportStatus.Timeout,
                source=AuditSource.REST_Outgoing_Health)
            _seed_call(audit_log, engine, now, f'check-b-{idx}', TransportStatus.Timeout,
                source=AuditSource.REST_Outgoing_Health, object_name=_other_conn_name)

        object_settings = _new_object_settings(is_active=False)
        result, recorder = _run_rest_sweep(engine, audit_log, now, 'cid-rest-off', object_settings)

        # Every alert is about the other connection - its codes, its check being down, its error rate
        assert 'Status_Codes' in _rule_names(result)
        assert 'Connection_Down' in _rule_names(result)

        for _, _, body in recorder.emails:
            assert _other_conn_name in body
            assert _conn_name not in body

# ################################################################################################################################

    def test_the_connections_own_window_reaches_its_traffic_alone(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Three 503s an hour and a half back for both connections
        _seed_failures(audit_log, engine, now, 'win-a', 3, '503 Service Unavailable', seconds_back=5400)
        _seed_failures(audit_log, engine, now, 'win-b', 3, '503 Service Unavailable', object_name=_other_conn_name,
            seconds_back=5400)

        # The rule measures over five minutes, the connection over two hours - only the connection is alerted on
        object_settings = _new_object_settings(status_codes_window=7200)
        result, recorder = _run_rest_sweep(engine, audit_log, now, 'cid-rest-window', object_settings)

        assert _rule_names(result) == ['Status_Codes']

        _, _, body = recorder.emails[0]
        assert _conn_name in body
        assert _other_conn_name not in body
        assert 'over 7200s' in body

# ################################################################################################################################

    def test_a_soap_outgoing_connection_is_judged_by_its_own_rules_and_named_as_soap(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Three 503s among the traffic of a SOAP connection - the same default codes a REST one alerts on ..
        _seed_failures(audit_log, engine, now, 'soap-down', 3, '503 Service Unavailable', source=AuditSource.SOAP_Outgoing)
        _seed_failures(audit_log, engine, now, 'soap-ok', 30, '200 OK', source=AuditSource.SOAP_Outgoing)

        result, recorder = _run_rest_sweep(engine, audit_log, now, 'cid-soap-codes', None)

        assert _rule_names(result) == ['Status_Codes']
        assert len(recorder.emails) == 1

        # .. and the message names the connection by its own transport, not as a REST one.
        _, _, body = recorder.emails[0]
        assert _conn_name in body
        assert 'SOAP outgoing' in body
        assert 'REST outgoing' not in body
        assert '3 responses with a status the connection alerts on (503 x3)' in body

        # Three calls that never got a response in a row bring the connection down under the SOAP name too
        for idx in range(3):
            _seed_call(audit_log, engine, now, f'soap-streak-{idx}', TransportStatus.Connection_Error,
                source=AuditSource.SOAP_Outgoing)

        result, recorder = _run_rest_sweep(engine, audit_log, now, 'cid-soap-down', None)

        # The streak brings the connection down and the refused connections count as failures on their own
        assert 'Connection_Down' in _rule_names(result)
        assert 'Connection_Failures' in _rule_names(result)

        for _, _, body in recorder.emails:
            assert '(SOAP outgoing)' in body
            assert '3 consecutive failures' in body

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingSoapSweep:

    def test_three_faults_raise_soap_faults_alone_and_not_status_codes(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Three Receiver faults on 500 - a 500 is among the default status codes, yet a fault is a fault
        _seed_failures(audit_log, engine, now, 'fault', 3, '500 Internal Server Error', source=AuditSource.SOAP_Outgoing,
            fault_code='Receiver')
        _seed_failures(audit_log, engine, now, 'ok', 30, '200 OK', source=AuditSource.SOAP_Outgoing)

        result, recorder = _run_rest_sweep(engine, audit_log, now, 'cid-soap-faults', None)

        assert _rule_names(result) == ['SOAP_Faults']
        assert len(recorder.emails) == 1

        _, _, body = recorder.emails[0]
        assert _conn_name in body
        assert '(SOAP outgoing)' in body
        assert '3 SOAP faults the connection alerts on (Receiver x3)' in body

# ################################################################################################################################

    def test_the_connections_own_fault_codes_stand_in_for_the_default(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Three Sender faults - the default alerts on them ..
        _seed_failures(audit_log, engine, now, 'sender', 3, '400 Bad Request', source=AuditSource.SOAP_Outgoing,
            fault_code='Sender')
        _seed_failures(audit_log, engine, now, 'ok', 30, '200 OK', source=AuditSource.SOAP_Outgoing)

        result, recorder = _run_rest_sweep(engine, audit_log, now, 'cid-soap-default', None)
        assert _rule_names(result) == ['SOAP_Faults']

        _, _, body = recorder.emails[0]
        assert '3 SOAP faults the connection alerts on (Sender x3)' in body

        # .. a connection alerting on the endpoint's own faults alone stays quiet on them ..
        object_settings = _new_object_settings(alert_type_soap, fault_codes='Receiver')
        result, recorder = _run_rest_sweep(engine, audit_log, now, 'cid-soap-own-quiet', object_settings)

        assert _rule_names(result) == []

        # .. and three Receiver faults on top wake it up, counted by its own codes.
        _seed_failures(audit_log, engine, now, 'receiver', 3, '500 Internal Server Error', source=AuditSource.SOAP_Outgoing,
            fault_code='Receiver')

        result, recorder = _run_rest_sweep(engine, audit_log, now, 'cid-soap-own-fires', object_settings)
        assert _rule_names(result) == ['SOAP_Faults']

        _, _, body = recorder.emails[0]
        assert '3 SOAP faults the connection alerts on (Receiver x3)' in body

# ################################################################################################################################

    def test_a_rest_and_a_soap_connection_of_one_name_read_settings_of_their_own(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Three 404s through a REST connection and three Sender faults through a SOAP one, both of one name
        _seed_failures(audit_log, engine, now, 'rest-nf', 3, '404 Not Found')
        _seed_failures(audit_log, engine, now, 'rest-ok', 30, '200 OK')
        _seed_failures(audit_log, engine, now, 'soap-sender', 3, '400 Bad Request', source=AuditSource.SOAP_Outgoing,
            fault_code='Sender')
        _seed_failures(audit_log, engine, now, 'soap-ok', 30, '200 OK', source=AuditSource.SOAP_Outgoing)

        # The REST one alerts on 404s of its own accord, the SOAP one on Receiver faults alone
        object_settings = _new_object_settings(status_codes='404')
        object_settings.update(_new_object_settings(alert_type_soap, fault_codes='Receiver'))

        result, recorder = _run_rest_sweep(engine, audit_log, now, 'cid-both', object_settings)

        # The REST connection's 404s fire, the SOAP connection's Sender faults do not
        assert _rule_names(result) == ['Status_Codes']

        _, _, body = recorder.emails[0]
        assert '(REST outgoing)' in body
        assert '3 responses with a status the connection alerts on (404 x3)' in body

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingFhirSweep:

    def test_three_outcomes_raise_operation_outcomes_alone_and_not_status_codes(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Three exception outcomes on 500 - a 500 is among the default status codes, yet an outcome is an outcome
        _seed_failures(audit_log, engine, now, 'outcome', 3, '500 Internal Server Error', source=AuditSource.FHIR,
            fault_code='exception')
        _seed_failures(audit_log, engine, now, 'ok', 30, '200 OK', source=AuditSource.FHIR)

        result, recorder = _run_rest_sweep(engine, audit_log, now, 'cid-fhir-outcomes', None)

        assert _rule_names(result) == ['Operation_Outcomes']
        assert len(recorder.emails) == 1

        _, _, body = recorder.emails[0]
        assert _conn_name in body
        assert '(FHIR outgoing)' in body
        assert '3 operation outcomes the connection alerts on (exception x3)' in body

# ################################################################################################################################

    def test_the_connections_own_outcome_codes_stand_in_for_the_default(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Three not-found outcomes - the default does not alert on a missing resource ..
        _seed_failures(audit_log, engine, now, 'nf', 3, '404 Not Found', source=AuditSource.FHIR, fault_code='not-found')
        _seed_failures(audit_log, engine, now, 'ok', 30, '200 OK', source=AuditSource.FHIR)

        result, recorder = _run_rest_sweep(engine, audit_log, now, 'cid-fhir-default-quiet', None)
        assert _rule_names(result) == []

        # .. a connection that names it alerts on them, counted by its own codes ..
        object_settings = _new_object_settings(alert_type_fhir, outcome_codes='not-found')
        result, recorder = _run_rest_sweep(engine, audit_log, now, 'cid-fhir-own-fires', object_settings)

        assert _rule_names(result) == ['Operation_Outcomes']

        _, _, body = recorder.emails[0]
        assert '3 operation outcomes the connection alerts on (not-found x3)' in body

        # .. and three exceptions on top leave that connection quiet on them while the default fires on them alone.
        _seed_failures(audit_log, engine, now, 'exc', 3, '500 Internal Server Error', source=AuditSource.FHIR,
            fault_code='exception')

        result, recorder = _run_rest_sweep(engine, audit_log, now, 'cid-fhir-own-still', object_settings)
        assert _rule_names(result) == ['Operation_Outcomes']

        _, _, body = recorder.emails[0]
        assert '3 operation outcomes the connection alerts on (not-found x3)' in body

        result, recorder = _run_rest_sweep(engine, audit_log, now, 'cid-fhir-default-fires', None)
        assert _rule_names(result) == ['Operation_Outcomes']

        _, _, body = recorder.emails[0]
        assert '3 operation outcomes the connection alerts on (exception x3)' in body

# ################################################################################################################################

    def test_a_fhir_health_check_is_judged_by_the_fhir_rules(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Three failed checks in a row - the check's own streak, the connection's traffic being fine
        for idx in range(3):
            _seed_call(audit_log, engine, now, f'check-{idx}', TransportStatus.Connection_Error, source=AuditSource.FHIR_Health)

        _seed_failures(audit_log, engine, now, 'ok', 5, '200 OK', source=AuditSource.FHIR)

        result, recorder = _run_rest_sweep(engine, audit_log, now, 'cid-fhir-check', None)

        assert 'Connection_Down' in _rule_names(result)

        _, _, body = recorder.emails[0]
        assert 'FHIR check failed 3 times' in body

# ################################################################################################################################
# ################################################################################################################################
