# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The outgoing connection producer - a connection's responses counted by their status code and its calls that
# failed before any response arrived counted on their own, over the window, the transport statuses never landing
# among the codes, the error rate of an outgoing REST connection read off its responses alone, and a channel and a
# connection of one name each getting facts of their own source.

# stdlib
from datetime import timedelta

# SQLAlchemy
from sqlalchemy import update

# Zato
from zato.common.alerting.collectors import channel_sources, collect_error_rate_facts, collect_facts, \
    collect_outgoing_status_facts, outgoing_sources, Measure_Connection_Failures, Measure_Status_Codes, \
    Window_Seconds_By_Measure_Key
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.common import TransportStatus
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.typing_ import stranydict
    datetime = datetime
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-alerting-outgoing-server'

# The connections the tests seed calls for - one of them shares its name with a channel
_conn_name = 'crm.api'
_other_conn_name = 'billing.api'

# The window the measures cover in these tests, in seconds
_window_seconds = 3600

# ################################################################################################################################
# ################################################################################################################################

def _backdate(event_id:'int', event_time:'datetime') -> 'None':
    """ Moves one stored event back in time.
    """
    engine = get_audit_engine()

    statement = update(event_table)
    statement = statement.where(event_table.c.id == event_id)
    statement = statement.values(event_time_iso=event_time.isoformat())

    with engine.begin() as connection:
        _ = connection.execute(statement)

# ################################################################################################################################

def _seed_call(audit_log:'AuditLog', cid:'str', status:'str', *, object_name:'str'=_conn_name,
    source:'str'=AuditSource.REST_Outgoing, fault_code:'str'='') -> 'int':
    """ Stores the request and response pair one call of an outgoing connection leaves behind - a response with
    its HTTP status line, a SOAP fault with its code on top, or a failed call with its transport status.
    The id of the response is returned.
    """
    if status.startswith('2'):
        outcome = AuditOutcome.OK
    else:
        outcome = AuditOutcome.Error

    _ = audit_log.insert(source, AuditEvent.Request_Sent, object_name, cid=cid, outcome=AuditOutcome.OK)

    out = audit_log.insert(source, AuditEvent.Response_Received, object_name, cid=cid, outcome=outcome, status=status,
        application_outcome=fault_code, duration_ms=20)

    return out

# ################################################################################################################################

def _fact_of(facts:'list', object_name:'str', source:'str'=AuditSource.REST_Outgoing) -> 'stranydict':
    """ The one fact of an object among the facts collected.
    """
    for fact in facts:
        if fact['source'] == source:
            if fact['object_name'] == object_name:
                return fact

    raise AssertionError(f'No fact for {source} {object_name} in {facts}')

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingStatusFacts:

    def test_the_responses_are_counted_by_code_and_the_failed_calls_on_their_own(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_call(audit_log, 'ok-1', '200 OK')
        _ = _seed_call(audit_log, 'ok-2', '200 OK')
        _ = _seed_call(audit_log, 'rejected-1', '401 Unauthorized')
        _ = _seed_call(audit_log, 'rejected-2', '401 Unauthorized')
        _ = _seed_call(audit_log, 'down-1', '503 Service Unavailable')
        _ = _seed_call(audit_log, 'timeout-1', TransportStatus.Timeout)
        _ = _seed_call(audit_log, 'refused-1', TransportStatus.Connection_Error)
        _ = _seed_call(audit_log, 'tls-1', TransportStatus.TLS_Error)

        facts = collect_outgoing_status_facts(engine, _window_seconds, now)
        fact = _fact_of(facts, _conn_name)

        assert fact['status_counts'] == {'200': 2, '401': 2, '503': 1}
        assert fact['connection_failure_count'] == 3
        assert fact['window_seconds'] == _window_seconds

        # The codes are for the sweep to match - nothing is derived here
        assert fact['status_code_count'] == 0

        # A REST connection never carries faults
        assert fact['fault_counts'] == {}
        assert fact['fault_count'] == 0

    def test_a_transport_status_never_lands_among_the_codes(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_call(audit_log, 'timeout-1', TransportStatus.Timeout)
        _ = _seed_call(audit_log, 'error-1', TransportStatus.Error)

        facts = collect_outgoing_status_facts(engine, _window_seconds, now)
        fact = _fact_of(facts, _conn_name)

        assert fact['status_counts'] == {}
        assert fact['connection_failure_count'] == 2

    def test_a_response_without_a_status_counts_nowhere(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_call(audit_log, 'blank-1', '')

        facts = collect_outgoing_status_facts(engine, _window_seconds, now)

        assert facts == []

    def test_responses_outside_the_window_are_not_counted(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        old_id = _seed_call(audit_log, 'old-1', '503 Service Unavailable')
        _backdate(old_id, now - timedelta(seconds=_window_seconds + 60))

        _ = _seed_call(audit_log, 'new-1', '503 Service Unavailable')

        fact = _fact_of(collect_outgoing_status_facts(engine, _window_seconds, now), _conn_name)

        assert fact['status_counts'] == {'503': 1}

    def test_a_connection_asked_for_by_name_is_measured_alone(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_call(audit_log, 'name-1', '503 Service Unavailable')
        _ = _seed_call(audit_log, 'name-2', '503 Service Unavailable', object_name=_other_conn_name)

        facts = collect_outgoing_status_facts(engine, _window_seconds, now, source=AuditSource.REST_Outgoing,
            object_name=_conn_name)

        assert len(facts) == 1
        assert facts[0]['object_name'] == _conn_name

    def test_an_outgoing_soap_connection_is_counted_by_status_as_a_rest_one(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_call(audit_log, 'soap-1', '500 Internal Server Error', source=AuditSource.SOAP_Outgoing)
        _ = _seed_call(audit_log, 'soap-2', TransportStatus.Timeout, source=AuditSource.SOAP_Outgoing)

        facts = collect_outgoing_status_facts(engine, _window_seconds, now)
        fact = _fact_of(facts, _conn_name, AuditSource.SOAP_Outgoing)

        assert fact['status_counts'] == {'500': 1}
        assert fact['connection_failure_count'] == 1

        facts = collect_outgoing_status_facts(engine, _window_seconds, now, source=AuditSource.SOAP_Outgoing)
        fact = _fact_of(facts, _conn_name, AuditSource.SOAP_Outgoing)
        assert fact['status_counts'] == {'500': 1}

    def test_a_fault_is_counted_by_its_code_and_never_as_a_status_code(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_call(audit_log, 'fault-1', '500 Internal Server Error', source=AuditSource.SOAP_Outgoing, fault_code='Receiver')
        _ = _seed_call(audit_log, 'fault-2', '500 Internal Server Error', source=AuditSource.SOAP_Outgoing, fault_code='Receiver')
        _ = _seed_call(audit_log, 'fault-3', '400 Bad Request', source=AuditSource.SOAP_Outgoing, fault_code='Sender')

        # A proxy's 503 page is not a fault, and a timeout is neither
        _ = _seed_call(audit_log, 'proxy-1', '503 Service Unavailable', source=AuditSource.SOAP_Outgoing)
        _ = _seed_call(audit_log, 'timeout-1', TransportStatus.Timeout, source=AuditSource.SOAP_Outgoing)

        facts = collect_outgoing_status_facts(engine, _window_seconds, now)
        fact = _fact_of(facts, _conn_name, AuditSource.SOAP_Outgoing)

        assert fact['fault_counts'] == {'Receiver': 2, 'Sender': 1}
        assert fact['status_counts'] == {'503': 1}
        assert fact['connection_failure_count'] == 1

        # The codes are for the sweep to match - nothing is derived here
        assert fact['fault_count'] == 0
        assert fact['fault_code_counts'] == {}

    def test_a_connection_with_faults_alone_gets_a_fact(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_call(audit_log, 'fault-1', '500 Internal Server Error', source=AuditSource.SOAP_Outgoing, fault_code='Receiver')

        facts = collect_outgoing_status_facts(engine, _window_seconds, now)
        fact = _fact_of(facts, _conn_name, AuditSource.SOAP_Outgoing)

        assert fact['fault_counts'] == {'Receiver': 1}
        assert fact['status_counts'] == {}
        assert fact['connection_failure_count'] == 0

    def test_a_source_outside_the_outgoing_ones_measures_nothing(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_call(audit_log, 'chan-1', '500 Internal Server Error', source=AuditSource.REST_Channel)

        facts = collect_outgoing_status_facts(engine, _window_seconds, now)
        assert facts == []

        facts = collect_outgoing_status_facts(engine, _window_seconds, now, source=AuditSource.REST_Channel)
        assert facts == []

# ################################################################################################################################
# ################################################################################################################################

class TestErrorRateOverResponses:

    def test_an_outgoing_rest_connection_whose_every_call_fails_reads_as_100_percent(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_call(audit_log, 'down-1', '503 Service Unavailable')
        _ = _seed_call(audit_log, 'down-2', TransportStatus.Timeout)

        fact = _fact_of(collect_error_rate_facts(engine, _window_seconds, now), _conn_name)

        # The request halves went out fine, and they do not count as successes
        assert fact['total_count'] == 2
        assert fact['error_count'] == 2
        assert fact['error_rate'] == 1.0

# ################################################################################################################################
# ################################################################################################################################

class TestSources:

    def test_the_channels_are_the_channels_alone(self) -> 'None':
        assert channel_sources == (AuditSource.REST_Channel, AuditSource.SOAP_Channel)
        assert outgoing_sources == (AuditSource.REST_Outgoing, AuditSource.SOAP_Outgoing, AuditSource.FHIR)

    def test_a_channel_and_a_connection_of_one_name_each_get_facts_of_their_own_source(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # The connection fails on a 503 and a timeout ..
        _ = _seed_call(audit_log, 'conn-1', '503 Service Unavailable')
        _ = _seed_call(audit_log, 'conn-2', TransportStatus.Timeout)

        # .. and the channel of the same name rejects a caller.
        _ = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Request_Received, _conn_name, cid='chan-1',
            outcome=AuditOutcome.OK)
        _ = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Response_Sent, _conn_name, cid='chan-1',
            outcome=AuditOutcome.Error, status='401 Unauthorized')

        facts = collect_facts(engine, {}, AuditSource.MLLP_Channel, now, window_seconds=_window_seconds)

        conn_fact = _fact_of(facts, _conn_name)
        channel_fact = _fact_of(facts, _conn_name, AuditSource.REST_Channel)

        # The connection's fact carries the outgoing measures and none of the channel's ..
        assert conn_fact['status_counts'] == {'503': 1}
        assert conn_fact['connection_failure_count'] == 1
        assert conn_fact['auth_failure_count'] == 0
        assert conn_fact[Window_Seconds_By_Measure_Key][Measure_Status_Codes] == _window_seconds
        assert conn_fact[Window_Seconds_By_Measure_Key][Measure_Connection_Failures] == _window_seconds

        # .. and the channel's the other way round.
        assert channel_fact['auth_failure_count'] == 1
        assert channel_fact['status_counts'] == {}
        assert channel_fact['connection_failure_count'] == 0

# ################################################################################################################################
# ################################################################################################################################
