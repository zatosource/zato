# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# SQLAlchemy
from sqlalchemy import update

# Zato
from zato.common.alerting.collectors import collect_channel_silence_facts, collect_channel_status_facts, \
    collect_error_rate_facts, collect_facts, collect_latency_facts, Measure_Auth_Failures, Measure_Client_Errors, \
    Measure_Error_Rate, Measure_Latency, Measure_Server_Errors, Window_Seconds_By_Measure_Key
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
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
_server_name = 'test-alerting-server'

# The channels and the outgoing connection the tests seed calls for
_channel_name = 'orders.api'
_other_channel_name = 'orders.status'
_outgoing_name = 'crm.api'

# The callers the calls authenticate as
_caller_a = 'partner-a'
_caller_b = 'partner-b'

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

def _seed_call(
    audit_log:'AuditLog',
    cid:'str',
    status:'str',
    *,
    object_name:'str' = _channel_name,
    source:'str' = AuditSource.REST_Channel,
    caller:'str' = _caller_a,
    duration_ms:'int' = 20,
    ) -> 'int':
    """ Stores the two events one call of a channel leaves behind - the request as it arrived
    and the response as it left, the response carrying the status and the outcome.
    """
    if status.startswith('2'):
        outcome = AuditOutcome.OK
    else:
        outcome = AuditOutcome.Error

    _ = audit_log.insert(source, AuditEvent.Request_Received, object_name, cid=cid, outcome=AuditOutcome.OK,
        ext_client_id=caller)

    out = audit_log.insert(source, AuditEvent.Response_Sent, object_name, cid=cid, outcome=outcome, status=status,
        ext_client_id=caller, duration_ms=duration_ms)

    return out

# ################################################################################################################################

def _seed_outgoing(audit_log:'AuditLog', cid:'str', outcome:'str') -> 'None':
    """ Stores the request and response pair an outgoing REST connection leaves behind.
    """
    _ = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _outgoing_name, cid=cid, outcome=AuditOutcome.OK)
    _ = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Response_Received, _outgoing_name, cid=cid, outcome=outcome,
        duration_ms=50)

# ################################################################################################################################

def _fact_of(facts:'list', object_name:'str', source:'str'=AuditSource.REST_Channel) -> 'stranydict':
    """ The one fact of an object among the facts collected.
    """
    for fact in facts:
        if fact['source'] == source:
            if fact['object_name'] == object_name:
                return fact

    raise AssertionError(f'No fact for {source} {object_name} in {facts}')

# ################################################################################################################################
# ################################################################################################################################

class TestErrorRateOverResponses:

    def test_a_channel_counts_its_calls_not_its_events(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Three calls, two of them failed - six events in all
        _ = _seed_call(audit_log, 'er-1', '500')
        _ = _seed_call(audit_log, 'er-2', '500')
        _ = _seed_call(audit_log, 'er-3', '200')

        fact = _fact_of(collect_error_rate_facts(engine, _window_seconds, now), _channel_name)

        assert fact['total_count'] == 3
        assert fact['error_count'] == 2
        assert round(fact['error_rate'], 2) == 0.67

    def test_an_outgoing_connection_is_measured_as_before(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_outgoing(audit_log, 'out-1', AuditOutcome.Error)
        _seed_outgoing(audit_log, 'out-2', AuditOutcome.OK)

        fact = _fact_of(collect_error_rate_facts(engine, _window_seconds, now), _outgoing_name, AuditSource.REST_Outgoing)

        # Every event counts for a source outside the response map - the request halves included
        assert fact['total_count'] == 4
        assert fact['error_count'] == 1
        assert fact['error_rate'] == 0.25

    def test_a_channel_asked_for_by_name_is_measured_alone(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_call(audit_log, 'name-1', '500')
        _ = _seed_call(audit_log, 'name-2', '200', object_name=_other_channel_name)

        facts = collect_error_rate_facts(engine, _window_seconds, now, source=AuditSource.REST_Channel,
            object_name=_channel_name)

        assert len(facts) == 1
        assert facts[0]['object_name'] == _channel_name
        assert facts[0]['total_count'] == 1

# ################################################################################################################################
# ################################################################################################################################

class TestStatusClasses:

    def test_one_query_sorts_the_statuses_into_three_measures(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_call(audit_log, 'st-1', '401')
        _ = _seed_call(audit_log, 'st-2', '403')
        _ = _seed_call(audit_log, 'st-3', '400')
        _ = _seed_call(audit_log, 'st-4', '404')
        _ = _seed_call(audit_log, 'st-5', '429')
        _ = _seed_call(audit_log, 'st-6', '500')
        _ = _seed_call(audit_log, 'st-7', '503')
        _ = _seed_call(audit_log, 'st-8', '200')

        fact = _fact_of(collect_channel_status_facts(engine, _window_seconds, now), _channel_name)

        assert fact['auth_failure_count'] == 2
        assert fact['client_error_count'] == 3
        assert fact['server_error_count'] == 2
        assert fact['server_error_rate'] == 0.25
        assert fact['window_seconds'] == _window_seconds

    def test_a_status_line_with_a_reason_is_read_by_its_code(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_call(audit_log, 'line-1', '401 Unauthorized')
        _ = _seed_call(audit_log, 'line-2', '500 Internal Server Error')

        fact = _fact_of(collect_channel_status_facts(engine, _window_seconds, now), _channel_name)

        assert fact['auth_failure_count'] == 1
        assert fact['server_error_count'] == 1
        assert fact['server_error_rate'] == 0.5

    def test_ok_responses_count_nowhere(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_call(audit_log, 'ok-1', '200')
        _ = _seed_call(audit_log, 'ok-2', '201')

        fact = _fact_of(collect_channel_status_facts(engine, _window_seconds, now), _channel_name)

        assert fact['auth_failure_count'] == 0
        assert fact['client_error_count'] == 0
        assert fact['server_error_count'] == 0
        assert fact['server_error_rate'] == 0.0

    def test_a_soap_channel_is_measured_too_and_a_connection_is_not(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_call(audit_log, 'soap-1', '500', source=AuditSource.SOAP_Channel)
        _seed_outgoing(audit_log, 'out-1', AuditOutcome.Error)

        facts = collect_channel_status_facts(engine, _window_seconds, now)

        assert len(facts) == 1
        assert facts[0]['source'] == AuditSource.SOAP_Channel
        assert facts[0]['server_error_count'] == 1

    def test_responses_outside_the_window_are_not_counted(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        old_id = _seed_call(audit_log, 'old-1', '500')
        _backdate(old_id, now - timedelta(seconds=_window_seconds + 60))

        _ = _seed_call(audit_log, 'new-1', '500')

        fact = _fact_of(collect_channel_status_facts(engine, _window_seconds, now), _channel_name)

        assert fact['server_error_count'] == 1
        assert fact['server_error_rate'] == 1.0

    def test_a_source_outside_the_map_measures_nothing(self) -> 'None':
        engine = get_audit_engine()
        now = utcnow()

        facts = collect_channel_status_facts(engine, _window_seconds, now, source=AuditSource.REST_Outgoing)

        assert facts == []

# ################################################################################################################################
# ################################################################################################################################

class TestSilence:

    def test_only_the_names_passed_in_are_measured(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        request_id = _seed_call(audit_log, 'sil-1', '200')
        _ = _seed_call(audit_log, 'sil-2', '200', object_name=_other_channel_name)

        # The newest request of the channel is a quarter of an hour old
        _backdate(request_id - 1, now - timedelta(seconds=900))
        _backdate(request_id, now - timedelta(seconds=900))

        facts = collect_channel_silence_facts(engine, now, {_channel_name})

        assert len(facts) == 1
        assert facts[0]['source'] == AuditSource.REST_Channel
        assert facts[0]['object_name'] == _channel_name
        assert facts[0]['silent_seconds'] == 900

    def test_no_names_means_no_facts(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_call(audit_log, 'sil-1', '200')

        assert collect_channel_silence_facts(engine, now, set()) == []

    def test_a_channel_that_never_received_a_request_has_nothing_to_measure(self) -> 'None':
        engine = get_audit_engine()
        now = utcnow()

        assert collect_channel_silence_facts(engine, now, {_channel_name}) == []

# ################################################################################################################################
# ################################################################################################################################

class TestLatency:

    def test_latency_is_unchanged_for_channels(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_call(audit_log, 'lat-1', '200', duration_ms=100)
        _ = _seed_call(audit_log, 'lat-2', '500', duration_ms=300)

        fact = _fact_of(collect_latency_facts(engine, _window_seconds, now), _channel_name)

        assert fact['avg_duration_ms'] == 200

# ################################################################################################################################
# ################################################################################################################################

class TestCollectFacts:

    def test_a_channel_fact_carries_every_measure_at_once(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_call(audit_log, 'all-1', '401')
        _ = _seed_call(audit_log, 'all-2', '500')
        _ = _seed_call(audit_log, 'all-3', '404')
        _ = _seed_call(audit_log, 'all-4', '200')

        facts = collect_facts(engine, {}, AuditSource.MLLP_Channel, now, window_seconds=_window_seconds,
            silence_expected_names={_channel_name})

        fact = _fact_of(facts, _channel_name)

        assert fact['total_count'] == 4
        assert fact['error_count'] == 3
        assert fact['error_rate'] == 0.75
        assert fact['auth_failure_count'] == 1
        assert fact['client_error_count'] == 1
        assert fact['server_error_count'] == 1
        assert fact['server_error_rate'] == 0.25
        assert fact['silent_seconds'] == 0
        assert fact['window_seconds'] == _window_seconds

    def test_each_measure_names_its_window(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_call(audit_log, 'win-1', '401')

        facts = collect_facts(engine, {}, AuditSource.MLLP_Channel, now, window_seconds=_window_seconds)

        fact = _fact_of(facts, _channel_name)

        assert fact[Window_Seconds_By_Measure_Key] == {
            Measure_Error_Rate:    _window_seconds,
            Measure_Latency:       _window_seconds,
            Measure_Auth_Failures: _window_seconds,
            Measure_Client_Errors: _window_seconds,
            Measure_Server_Errors: _window_seconds,
        }

    def test_the_rejected_callers_and_the_error_rate_have_windows_of_their_own(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Two rejections half an hour ago and one failure a minute ago
        old_1 = _seed_call(audit_log, 'own-1', '401')
        old_2 = _seed_call(audit_log, 'own-2', '401')
        _backdate(old_1, now - timedelta(seconds=1800))
        _backdate(old_2, now - timedelta(seconds=1800))

        _ = _seed_call(audit_log, 'own-3', '500')
        _ = _seed_call(audit_log, 'own-4', '200')

        # The rejected callers are counted over the hour, the error rate over the last five minutes
        window_seconds_by_object = {
            AuditSource.REST_Channel: {
                _channel_name: {
                    Measure_Auth_Failures: 3600,
                    Measure_Error_Rate: 300,
                },
            },
        }

        facts = collect_facts(engine, {}, AuditSource.MLLP_Channel, now, window_seconds=_window_seconds,
            window_seconds_by_object=window_seconds_by_object)

        fact = _fact_of(facts, _channel_name)

        assert fact['auth_failure_count'] == 2
        assert fact['total_count'] == 2
        assert fact['error_count'] == 1
        assert fact['error_rate'] == 0.5
        assert fact['window_seconds'] == 300
        assert fact[Window_Seconds_By_Measure_Key][Measure_Auth_Failures] == 3600
        assert fact[Window_Seconds_By_Measure_Key][Measure_Error_Rate] == 300
        assert fact[Window_Seconds_By_Measure_Key][Measure_Latency] == _window_seconds

    def test_a_source_window_covers_the_measures_it_names_alone(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        old = _seed_call(audit_log, 'src-1', '500')
        _backdate(old, now - timedelta(seconds=1800))
        _ = _seed_call(audit_log, 'src-2', '200')

        window_seconds_by_source = {
            AuditSource.REST_Channel: {
                Measure_Server_Errors: 300,
            },
        }

        facts = collect_facts(engine, {}, AuditSource.MLLP_Channel, now, window_seconds=_window_seconds,
            window_seconds_by_source=window_seconds_by_source)

        fact = _fact_of(facts, _channel_name)

        # The server errors saw the last five minutes, the error rate the whole hour
        assert fact['server_error_count'] == 0
        assert fact['error_count'] == 1
        assert fact['total_count'] == 2
        assert fact[Window_Seconds_By_Measure_Key][Measure_Server_Errors] == 300
        assert fact[Window_Seconds_By_Measure_Key][Measure_Error_Rate] == _window_seconds

    def test_the_rest_type_measures_error_rate_and_latency_over_its_one_window(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_outgoing(audit_log, 'rest-1', AuditOutcome.Error)

        window_seconds_by_source = {
            AuditSource.REST_Outgoing: {
                Measure_Error_Rate: 600,
                Measure_Latency: 600,
            },
        }

        facts = collect_facts(engine, {}, AuditSource.MLLP_Channel, now, window_seconds=_window_seconds,
            window_seconds_by_source=window_seconds_by_source)

        fact = _fact_of(facts, _outgoing_name, AuditSource.REST_Outgoing)

        assert fact['window_seconds'] == 600
        assert fact[Window_Seconds_By_Measure_Key][Measure_Error_Rate] == 600
        assert fact[Window_Seconds_By_Measure_Key][Measure_Latency] == 600

# ################################################################################################################################
# ################################################################################################################################

class TestSoapChannel:

    def test_a_soap_channels_silence_is_measured_under_its_own_source(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        request_id = _seed_call(audit_log, 'soap-sil-1', '200', source=AuditSource.SOAP_Channel)

        # The newest request of the channel is a quarter of an hour old
        _backdate(request_id - 1, now - timedelta(seconds=900))
        _backdate(request_id, now - timedelta(seconds=900))

        facts = collect_channel_silence_facts(engine, now, {_channel_name})

        assert len(facts) == 1
        assert facts[0]['source'] == AuditSource.SOAP_Channel
        assert facts[0]['object_name'] == _channel_name
        assert facts[0]['silent_seconds'] == 900

    def test_a_soap_channels_status_classes_count_as_a_rest_channels_do(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_call(audit_log, 'soap-1', '401', source=AuditSource.SOAP_Channel)
        _ = _seed_call(audit_log, 'soap-2', '500', source=AuditSource.SOAP_Channel)
        _ = _seed_call(audit_log, 'soap-3', '404', source=AuditSource.SOAP_Channel)
        _ = _seed_call(audit_log, 'soap-4', '200', source=AuditSource.SOAP_Channel)

        fact = _fact_of(collect_error_rate_facts(engine, _window_seconds, now), _channel_name, AuditSource.SOAP_Channel)

        assert fact['total_count'] == 4
        assert fact['error_count'] == 3

        fact = _fact_of(collect_channel_status_facts(engine, _window_seconds, now), _channel_name, AuditSource.SOAP_Channel)

        assert fact['auth_failure_count'] == 1
        assert fact['client_error_count'] == 1
        assert fact['server_error_count'] == 1
        assert fact['server_error_rate'] == 0.25

    def test_a_rest_and_a_soap_channel_of_one_name_get_facts_of_their_own_source(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # The REST channel fails once out of two calls, the SOAP one of the same name three times out of three
        _ = _seed_call(audit_log, 'rest-1', '500')
        _ = _seed_call(audit_log, 'rest-2', '200')
        _ = _seed_call(audit_log, 'soap-1', '500', source=AuditSource.SOAP_Channel)
        _ = _seed_call(audit_log, 'soap-2', '500', source=AuditSource.SOAP_Channel)
        _ = _seed_call(audit_log, 'soap-3', '401', source=AuditSource.SOAP_Channel)

        # Both channels expect traffic and both heard from a caller just now
        facts = collect_facts(engine, {}, AuditSource.MLLP_Channel, now, window_seconds=_window_seconds,
            silence_expected_names={_channel_name})

        rest_fact = _fact_of(facts, _channel_name)
        soap_fact = _fact_of(facts, _channel_name, AuditSource.SOAP_Channel)

        assert rest_fact['total_count'] == 2
        assert rest_fact['error_rate'] == 0.5
        assert rest_fact['auth_failure_count'] == 0
        assert rest_fact['silent_seconds'] == 0

        assert soap_fact['total_count'] == 3
        assert soap_fact['error_rate'] == 1
        assert soap_fact['auth_failure_count'] == 1
        assert soap_fact['server_error_count'] == 2
        assert soap_fact['silent_seconds'] == 0

# ################################################################################################################################
# ################################################################################################################################
