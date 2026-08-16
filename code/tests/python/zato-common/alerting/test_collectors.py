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
from zato.common.alerting.collectors import collect_auth_failure_facts, collect_certificate_facts, \
    collect_consecutive_failure_facts, collect_error_rate_facts, collect_facts, collect_feed_silent_facts, \
    collect_file_transfer_facts, collect_health_facts, collect_latency_facts, collect_outstanding_facts, \
    collect_scheduler_facts, collect_test_transfer_facts, new_fact, Attr_Days_Left
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.scheduler import Attr_Delay_Ms
from zato.common.monitoring.health import EndpointMetrics
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    datetime = datetime

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-alerting-server'

# The channels the tests seed events for
_channel_name = 'hl7.test.channel'
_other_channel_name = 'hl7.other.channel'

# The outgoing connection the health check tests seed events for
_connection_name = 'crm.orders.api'

# The window the error-rate measures cover in these tests, in seconds
_window_seconds = 3600

# ################################################################################################################################
# ################################################################################################################################

def _backdate(event_id:'int', event_time:'datetime') -> 'None':
    """ Moves one stored event back in time - the collectors compare event times,
    and the tests need events older than their deadlines.
    """
    engine = get_audit_engine()

    statement = update(event_table)
    statement = statement.where(event_table.c.id == event_id)
    statement = statement.values(event_time_iso=event_time.isoformat())

    with engine.begin() as connection:
        _ = connection.execute(statement)

# ################################################################################################################################

def _seed_outcome(audit_log:'AuditLog', cid:'str', outcome:'str', *, object_name:'str'=_channel_name) -> 'None':
    """ Stores one inbound acknowledgment event with the given outcome.
    """
    _ = audit_log.insert(AuditSource.MLLP_Channel, AuditEvent.Ack_Sent, object_name, cid=cid, outcome=outcome)

# ################################################################################################################################

def _seed_exchange(audit_log:'AuditLog', source:'str', cid:'str', outcome:'str') -> 'None':
    """ Stores the request/response pair an outgoing connection leaves behind, the way its
    wrapper writes it - the request half always goes out fine, the response half carries
    what actually happened.
    """
    _ = audit_log.insert(source, AuditEvent.Request_Sent, _connection_name, cid=cid, outcome=AuditOutcome.OK)
    _ = audit_log.insert(source, AuditEvent.Response_Received, _connection_name, cid=cid, outcome=outcome)

# ################################################################################################################################
# ################################################################################################################################

class TestNewFact:

    def test_a_resting_fact_carries_every_measure_at_zero(self) -> 'None':
        fact = new_fact(AuditSource.MLLP_Channel, _channel_name)

        assert fact['source'] == AuditSource.MLLP_Channel
        assert fact['object_name'] == _channel_name
        assert fact['error_rate'] == 0.0
        assert fact['error_count'] == 0
        assert fact['total_count'] == 0
        assert fact['window_seconds'] == 0
        assert fact['outstanding'] == 0
        assert fact['oldest_waiting_seconds'] == 0
        assert fact['silent_seconds'] == 0
        assert fact['last_error_event_id'] == 0
        assert fact['is_resubmittable'] == 0
        assert fact['seconds_since_last_arrival'] == 0
        assert fact['arrival_overdue_ratio'] == 0.0

# ################################################################################################################################
# ################################################################################################################################

class TestErrorRateFacts:

    def test_the_measures_say_what_happened_without_judging(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Three of four outcomes are errors - a 75% error rate
        _seed_outcome(audit_log, 'facts-er-1', AuditOutcome.Error)
        _seed_outcome(audit_log, 'facts-er-2', AuditOutcome.Error)
        _seed_outcome(audit_log, 'facts-er-3', AuditOutcome.Error)
        _seed_outcome(audit_log, 'facts-er-4', AuditOutcome.OK)

        facts = collect_error_rate_facts(engine, _window_seconds, now)

        assert len(facts) == 1

        fact = facts[0]
        assert fact['source'] == AuditSource.MLLP_Channel
        assert fact['object_name'] == _channel_name
        assert fact['error_rate'] == 0.75
        assert fact['error_count'] == 3
        assert fact['total_count'] == 4
        assert fact['window_seconds'] == _window_seconds

# ################################################################################################################################

    def test_each_object_gets_its_own_fact(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_outcome(audit_log, 'facts-two-1', AuditOutcome.Error)
        _seed_outcome(audit_log, 'facts-two-2', AuditOutcome.OK, object_name=_other_channel_name)

        facts = collect_error_rate_facts(engine, _window_seconds, now)
        by_name = {fact['object_name']: fact for fact in facts}

        assert len(facts) == 2
        assert by_name[_channel_name]['error_rate'] == 1.0
        assert by_name[_other_channel_name]['error_rate'] == 0.0

# ################################################################################################################################

    def test_traffic_outside_the_window_never_counts(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # One error, moved outside the window
        event_id = audit_log.insert(AuditSource.MLLP_Channel, AuditEvent.Ack_Sent, _channel_name,
            cid='facts-old-1', outcome=AuditOutcome.Error)
        _backdate(event_id, now - timedelta(seconds=_window_seconds + 60))

        facts = collect_error_rate_facts(engine, _window_seconds, now)

        assert facts == []

# ################################################################################################################################

    def test_the_newest_failing_event_of_a_resubmittable_type_is_pointed_at(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Two failed per-hop deliveries - the request-sent type is what their source
        # declared resubmittable, and the newer of the two is the one to point at
        _ = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _channel_name,
            cid='resub-er-1', outcome=AuditOutcome.Error)
        newest_id = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _channel_name,
            cid='resub-er-2', outcome=AuditOutcome.Error)

        facts = collect_error_rate_facts(engine, _window_seconds, now)

        assert len(facts) == 1
        assert facts[0]['last_error_event_id'] == newest_id
        assert facts[0]['is_resubmittable'] == 1

# ################################################################################################################################

    def test_a_failing_event_of_an_undeclared_type_is_pointed_at_without_a_resend_offer(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # An outbound acknowledgment is no type its source declared resubmittable
        event_id = audit_log.insert(AuditSource.MLLP_Channel, AuditEvent.Ack_Sent, _channel_name,
            cid='resub-er-3', outcome=AuditOutcome.Error)

        facts = collect_error_rate_facts(engine, _window_seconds, now)

        assert len(facts) == 1
        assert facts[0]['last_error_event_id'] == event_id
        assert facts[0]['is_resubmittable'] == 0

# ################################################################################################################################

    def test_an_object_without_failures_points_at_nothing(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _channel_name,
            cid='resub-er-4', outcome=AuditOutcome.OK)

        facts = collect_error_rate_facts(engine, _window_seconds, now)

        assert len(facts) == 1
        assert facts[0]['last_error_event_id'] == 0
        assert facts[0]['is_resubmittable'] == 0

# ################################################################################################################################
# ################################################################################################################################

class TestOutstandingFacts:

    def test_a_message_without_its_followup_counts_with_its_age(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # One message sent ten minutes ago, never acknowledged
        event_id = audit_log.insert(AuditSource.MLLP_Outgoing, AuditEvent.Message_Sent, _channel_name,
            cid='facts-mf-1', msg_id='MSG-facts-mf-1', outcome=AuditOutcome.OK)
        _backdate(event_id, now - timedelta(seconds=600))

        facts = collect_outstanding_facts(engine, AuditEvent.Message_Sent, AuditEvent.Ack_Received, now)

        assert len(facts) == 1

        fact = facts[0]
        assert fact['source'] == AuditSource.MLLP_Outgoing
        assert fact['object_name'] == _channel_name
        assert fact['outstanding'] == 1
        assert fact['oldest_waiting_seconds'] >= 599

# ################################################################################################################################

    def test_an_answered_message_never_counts(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # A message and its acknowledgment, on the same correlation id
        _ = audit_log.insert(AuditSource.MLLP_Outgoing, AuditEvent.Message_Sent, _channel_name,
            cid='facts-ok-1', outcome=AuditOutcome.OK)
        _ = audit_log.insert(AuditSource.MLLP_Outgoing, AuditEvent.Ack_Received, _channel_name,
            cid='facts-ok-1', outcome=AuditOutcome.OK)

        facts = collect_outstanding_facts(engine, AuditEvent.Message_Sent, AuditEvent.Ack_Received, now)

        assert facts == []

# ################################################################################################################################
# ################################################################################################################################

class TestFeedSilentFacts:

    def test_silence_is_measured_and_no_traffic_is_skipped(self) -> 'None':
        silent_metrics = EndpointMetrics()
        silent_metrics.silence_seconds = 900.0

        # A channel that never received anything is a configuration matter, not a dead feed
        never_active_metrics = EndpointMetrics()
        never_active_metrics.silence_seconds = 0.0

        metrics_by_name = {
            _channel_name: silent_metrics,
            _other_channel_name: never_active_metrics,
        }

        facts = collect_feed_silent_facts(metrics_by_name, AuditSource.MLLP_Channel)

        assert len(facts) == 1
        assert facts[0]['object_name'] == _channel_name
        assert facts[0]['silent_seconds'] == 900

# ################################################################################################################################
# ################################################################################################################################

class TestConsecutiveFailureFacts:

    def test_an_unbroken_run_of_errors_is_counted(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_outcome(audit_log, 'consec-1', AuditOutcome.OK)
        _seed_outcome(audit_log, 'consec-2', AuditOutcome.Error)
        _seed_outcome(audit_log, 'consec-3', AuditOutcome.Error)
        _seed_outcome(audit_log, 'consec-4', AuditOutcome.Error)

        facts = collect_consecutive_failure_facts(engine, now)

        assert len(facts) == 1
        assert facts[0]['consecutive_failures'] == 3

# ################################################################################################################################

    def test_a_success_breaks_the_streak(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # The newest outcome is an error but the one before it is not
        _seed_outcome(audit_log, 'break-1', AuditOutcome.Error)
        _seed_outcome(audit_log, 'break-2', AuditOutcome.OK)
        _seed_outcome(audit_log, 'break-3', AuditOutcome.Error)

        facts = collect_consecutive_failure_facts(engine, now)

        assert len(facts) == 1
        assert facts[0]['consecutive_failures'] == 1

# ################################################################################################################################

    def test_the_ok_halves_of_paired_events_never_hide_a_streak(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # A source that writes paired events - the request half always leaves with an OK
        # outcome while the response half carries the real one
        for index in range(3):
            _ = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _channel_name,
                cid=f'paired-{index}', outcome=AuditOutcome.OK)
            _ = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Response_Received, _channel_name,
                cid=f'paired-{index}', outcome=AuditOutcome.Error)

        facts = collect_consecutive_failure_facts(engine, now)

        assert len(facts) == 1
        assert facts[0]['consecutive_failures'] == 3

# ################################################################################################################################

    def test_a_clean_object_still_reports_a_zero(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_outcome(audit_log, 'clean-1', AuditOutcome.OK)

        facts = collect_consecutive_failure_facts(engine, now)

        assert len(facts) == 1
        assert facts[0]['consecutive_failures'] == 0

# ################################################################################################################################
# ################################################################################################################################

class TestHealthCheckStreamIsCountedApart:

    def test_a_failing_ping_does_not_add_to_the_traffic_streak(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # One connection, failing on both what it carries and what watches it
        _seed_exchange(audit_log, AuditSource.REST_Outgoing, 'apart-call-1', AuditOutcome.Error)
        _seed_exchange(audit_log, AuditSource.REST_Outgoing, 'apart-call-2', AuditOutcome.Error)
        _seed_exchange(audit_log, AuditSource.REST_Outgoing_Health, 'apart-check-1', AuditOutcome.Error)
        _seed_exchange(audit_log, AuditSource.REST_Outgoing_Health, 'apart-check-2', AuditOutcome.Error)

        facts = collect_consecutive_failure_facts(engine, now)

        streaks_by_source = {}

        for fact in facts:
            assert fact['object_name'] == _connection_name
            streaks_by_source[fact['source']] = fact['consecutive_failures']

        # Two streams of two, rather than one of four
        assert streaks_by_source == {
            AuditSource.REST_Outgoing: 2,
            AuditSource.REST_Outgoing_Health: 2,
        }

# ################################################################################################################################

    def test_a_succeeding_ping_no_longer_breaks_the_traffic_streak(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # A check that answers between failing calls, oldest first. On one shared stream the
        # newest three outcomes would read OK, error, OK and the streak would stop at one.
        _seed_exchange(audit_log, AuditSource.REST_Outgoing, 'interleaved-call-1', AuditOutcome.Error)
        _seed_exchange(audit_log, AuditSource.REST_Outgoing_Health, 'interleaved-check-1', AuditOutcome.OK)
        _seed_exchange(audit_log, AuditSource.REST_Outgoing, 'interleaved-call-2', AuditOutcome.Error)
        _seed_exchange(audit_log, AuditSource.REST_Outgoing_Health, 'interleaved-check-2', AuditOutcome.OK)
        _seed_exchange(audit_log, AuditSource.REST_Outgoing, 'interleaved-call-3', AuditOutcome.Error)

        facts = collect_consecutive_failure_facts(engine, now)

        streaks_by_source = {}

        for fact in facts:
            streaks_by_source[fact['source']] = fact['consecutive_failures']

        # The three failed calls are an unbroken run, and the answering check says so
        assert streaks_by_source[AuditSource.REST_Outgoing] == 3
        assert streaks_by_source[AuditSource.REST_Outgoing_Health] == 0

# ################################################################################################################################

    def test_a_connection_with_only_a_health_check_reports_only_the_health_source(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_exchange(audit_log, AuditSource.REST_Outgoing_Health, 'only-check-1', AuditOutcome.Error)
        _seed_exchange(audit_log, AuditSource.REST_Outgoing_Health, 'only-check-2', AuditOutcome.Error)
        _seed_exchange(audit_log, AuditSource.REST_Outgoing_Health, 'only-check-3', AuditOutcome.Error)

        facts = collect_consecutive_failure_facts(engine, now)

        assert len(facts) == 1

        fact = facts[0]
        assert fact['source'] == AuditSource.REST_Outgoing_Health
        assert fact['object_name'] == _connection_name
        assert fact['consecutive_failures'] == 3

# ################################################################################################################################

    def test_a_soap_check_is_counted_apart_from_soap_traffic(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_exchange(audit_log, AuditSource.SOAP_Outgoing, 'soap-call-1', AuditOutcome.Error)
        _seed_exchange(audit_log, AuditSource.SOAP_Outgoing_Health, 'soap-check-1', AuditOutcome.Error)
        _seed_exchange(audit_log, AuditSource.SOAP_Outgoing_Health, 'soap-check-2', AuditOutcome.Error)

        facts = collect_consecutive_failure_facts(engine, now)

        streaks_by_source = {}

        for fact in facts:
            streaks_by_source[fact['source']] = fact['consecutive_failures']

        assert streaks_by_source == {
            AuditSource.SOAP_Outgoing: 1,
            AuditSource.SOAP_Outgoing_Health: 2,
        }

# ################################################################################################################################

    def test_an_object_mid_streak_points_at_its_newest_failing_event(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # An unbroken run of failed per-hop deliveries - the newest one is the one
        # to point at, and its type is what its source declared resubmittable
        _ = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _channel_name,
            cid='resub-cf-1', outcome=AuditOutcome.Error)
        newest_id = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _channel_name,
            cid='resub-cf-2', outcome=AuditOutcome.Error)

        facts = collect_consecutive_failure_facts(engine, now)

        assert len(facts) == 1
        assert facts[0]['consecutive_failures'] == 2
        assert facts[0]['last_error_event_id'] == newest_id
        assert facts[0]['is_resubmittable'] == 1

# ################################################################################################################################

    def test_a_clean_object_points_at_nothing(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # A failure with a recovery after it - no streak, so nothing to point at either
        _seed_outcome(audit_log, 'resub-cf-3', AuditOutcome.Error)
        _seed_outcome(audit_log, 'resub-cf-4', AuditOutcome.OK)

        facts = collect_consecutive_failure_facts(engine, now)

        assert len(facts) == 1
        assert facts[0]['consecutive_failures'] == 0
        assert facts[0]['last_error_event_id'] == 0
        assert facts[0]['is_resubmittable'] == 0

# ################################################################################################################################
# ################################################################################################################################

class TestLatencyFacts:

    def test_the_average_covers_only_events_that_carry_a_duration(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Two completed calls with durations and one request event without one
        _ = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Response_Received, _channel_name,
            cid='lat-1', outcome=AuditOutcome.OK, duration_ms=100)
        _ = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Response_Received, _channel_name,
            cid='lat-2', outcome=AuditOutcome.OK, duration_ms=300)
        _ = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, _channel_name,
            cid='lat-3', outcome=AuditOutcome.OK)

        facts = collect_latency_facts(engine, _window_seconds, now)

        assert len(facts) == 1
        assert facts[0]['avg_duration_ms'] == 200
        assert facts[0]['window_seconds'] == _window_seconds

# ################################################################################################################################

    def test_traffic_outside_the_window_never_counts(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        event_id = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Response_Received, _channel_name,
            cid='lat-old-1', outcome=AuditOutcome.OK, duration_ms=9000)
        _backdate(event_id, now - timedelta(seconds=_window_seconds + 60))

        facts = collect_latency_facts(engine, _window_seconds, now)

        assert facts == []

# ################################################################################################################################
# ################################################################################################################################

class TestAuthFailureFacts:

    def test_only_the_auth_failed_events_are_counted(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Two credentials rejections and one ordinary failure
        _ = audit_log.insert(AuditSource.Email_SMTP, AuditEvent.Auth_Failed, _channel_name,
            cid='auth-1', outcome=AuditOutcome.Error)
        _ = audit_log.insert(AuditSource.Email_SMTP, AuditEvent.Auth_Failed, _channel_name,
            cid='auth-2', outcome=AuditOutcome.Error)
        _ = audit_log.insert(AuditSource.Email_SMTP, AuditEvent.Message_Sent, _channel_name,
            cid='auth-3', outcome=AuditOutcome.Error)

        facts = collect_auth_failure_facts(engine, _window_seconds, now)

        assert len(facts) == 1
        assert facts[0]['auth_failure_count'] == 2

# ################################################################################################################################
# ################################################################################################################################

class TestCertificateFacts:

    def test_the_newest_days_left_measure_surfaces(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # An older measure and a newer one - only the newer one speaks
        _ = audit_log.insert(AuditSource.Certificate, AuditEvent.Cert_Checked, _channel_name,
            cid='cert-1', outcome=AuditOutcome.OK, attrs={Attr_Days_Left: 30.0})
        _ = audit_log.insert(AuditSource.Certificate, AuditEvent.Cert_Checked, _channel_name,
            cid='cert-2', outcome=AuditOutcome.OK, attrs={Attr_Days_Left: 5.4})

        facts = collect_certificate_facts(engine, now)

        assert len(facts) == 1
        assert facts[0]['object_name'] == _channel_name
        assert facts[0]['cert_days_left'] == 5

# ################################################################################################################################

    def test_a_failed_check_reports_nothing_rather_than_a_false_zero(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # A handshake that failed wrote an error event with no days-left attr
        _ = audit_log.insert(AuditSource.Certificate, AuditEvent.Cert_Checked, _channel_name,
            cid='cert-err-1', outcome=AuditOutcome.Error, status='Connection refused')

        facts = collect_certificate_facts(engine, now)

        assert facts == []

# ################################################################################################################################
# ################################################################################################################################

class TestHealthFacts:

    def test_the_newest_state_of_each_service_surfaces(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # A service that recovered and one that degraded
        _ = audit_log.insert(AuditSource.Microsoft_Health, AuditEvent.Health_Checked, 'Exchange Online',
            cid='health-1', outcome=AuditOutcome.OK, status='degraded')
        _ = audit_log.insert(AuditSource.Microsoft_Health, AuditEvent.Health_Checked, 'Exchange Online',
            cid='health-2', outcome=AuditOutcome.OK, status='')
        _ = audit_log.insert(AuditSource.Microsoft_Health, AuditEvent.Health_Checked, 'Microsoft Teams',
            cid='health-3', outcome=AuditOutcome.OK, status='interruption')

        facts = collect_health_facts(engine, now)

        # The recovered service's empty state means healthy, so only the degraded one reports
        assert len(facts) == 1
        assert facts[0]['object_name'] == 'Microsoft Teams'
        assert facts[0]['health_state'] == 'interruption'

# ################################################################################################################################
# ################################################################################################################################

class TestTransferFacts:

    def test_the_newest_outcome_is_the_current_truth(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # A connection whose test transfer failed and one whose test transfer recovered
        _ = audit_log.insert(AuditSource.Test_Transfer, AuditEvent.Test_Transfer_Executed, _channel_name,
            cid='test-transfer-1', outcome=AuditOutcome.OK)
        _ = audit_log.insert(AuditSource.Test_Transfer, AuditEvent.Test_Transfer_Executed, _channel_name,
            cid='test-transfer-2', outcome=AuditOutcome.Error, status='Upload failed')

        _ = audit_log.insert(AuditSource.Test_Transfer, AuditEvent.Test_Transfer_Executed, _other_channel_name,
            cid='test-transfer-3', outcome=AuditOutcome.Error, status='Upload failed')
        _ = audit_log.insert(AuditSource.Test_Transfer, AuditEvent.Test_Transfer_Executed, _other_channel_name,
            cid='test-transfer-4', outcome=AuditOutcome.OK)

        facts = collect_test_transfer_facts(engine, now)
        by_name = {fact['object_name']: fact for fact in facts}

        assert len(facts) == 2
        assert by_name[_channel_name]['test_transfer_failed'] == 1
        assert by_name[_other_channel_name]['test_transfer_failed'] == 0

# ################################################################################################################################
# ################################################################################################################################

class TestSchedulerFacts:

    def test_the_worst_start_delay_of_the_window_speaks(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = audit_log.insert(AuditSource.Scheduler, AuditEvent.Job_Executed, 'billing.sync',
            cid='sched-1', outcome=AuditOutcome.OK, attrs={Attr_Delay_Ms: 1200})
        _ = audit_log.insert(AuditSource.Scheduler, AuditEvent.Job_Executed, 'billing.sync',
            cid='sched-2', outcome=AuditOutcome.OK, attrs={Attr_Delay_Ms: 7400})

        facts = collect_scheduler_facts(engine, _window_seconds, now, {})

        assert len(facts) == 1
        assert facts[0]['object_name'] == 'billing.sync'
        assert facts[0]['start_delay_ms'] == 7400

# ################################################################################################################################

    def test_the_overdue_ratio_sizes_itself_against_the_jobs_own_interval(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # A job that last ran twenty minutes ago, on a five-minute interval
        event_id = audit_log.insert(AuditSource.Scheduler, AuditEvent.Job_Executed, 'billing.sync',
            cid='overdue-1', outcome=AuditOutcome.OK)
        _backdate(event_id, now - timedelta(seconds=1200))

        facts = collect_scheduler_facts(engine, _window_seconds, now, {'billing.sync': 300})

        assert len(facts) == 1
        assert facts[0]['overdue_ratio'] == 4.0

# ################################################################################################################################

    def test_a_job_without_an_interval_has_no_notion_of_being_overdue(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        event_id = audit_log.insert(AuditSource.Scheduler, AuditEvent.Job_Executed, 'one.time.job',
            cid='onetime-1', outcome=AuditOutcome.OK)
        _backdate(event_id, now - timedelta(seconds=1200))

        facts = collect_scheduler_facts(engine, _window_seconds, now, {})

        assert facts == []

# ################################################################################################################################
# ################################################################################################################################

class TestFileTransferArrivalFacts:

    # The schedules whose arrivals the tests measure
    _schedule_name = 'Daily results'
    _other_schedule_name = 'Hourly exports'

    # The connection the delivered events are written under
    _file_connection_name = 'sftp.backups'

# ################################################################################################################################

    def _seed_arrival(self, audit_log:'AuditLog', cid:'str', *, schedule:'str'='') -> 'int':
        """ Stores one delivered event of the kind a file transfer schedule writes
        when it hands a file to its target service.
        """
        if not schedule:
            schedule = self._schedule_name

        out = audit_log.insert(AuditSource.File_Outgoing, AuditEvent.Delivered, self._file_connection_name,
            cid=cid, outcome=AuditOutcome.OK, attrs={'schedule': schedule})

        return out

# ################################################################################################################################

    def test_the_time_since_the_newest_arrival_is_measured(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # An older arrival and a newer one - only the newer one sets the measure
        older_id = self._seed_arrival(audit_log, 'arrival-1')
        newer_id = self._seed_arrival(audit_log, 'arrival-2')

        _backdate(older_id, now - timedelta(seconds=1200))
        _backdate(newer_id, now - timedelta(seconds=600))

        # A five-minute window, so the newest arrival is twice as old as expected
        facts = collect_file_transfer_facts(engine, now, {self._schedule_name: 300})

        assert len(facts) == 1

        fact = facts[0]
        assert fact['source'] == AuditSource.File_Outgoing
        assert fact['object_name'] == self._schedule_name
        assert fact['seconds_since_last_arrival'] == 600
        assert fact['arrival_overdue_ratio'] == 2.0

# ################################################################################################################################

    def test_a_schedule_without_a_window_declares_no_expectation(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        event_id = self._seed_arrival(audit_log, 'arrival-no-window-1')
        _backdate(event_id, now - timedelta(seconds=3600))

        # No window on record for this schedule, so it is never measured
        facts = collect_file_transfer_facts(engine, now, {self._other_schedule_name: 300})

        assert facts == []

# ################################################################################################################################

    def test_a_schedule_that_never_delivered_has_no_baseline(self) -> 'None':
        engine = get_audit_engine()
        now = utcnow()

        # A window is declared but nothing ever arrived - there is nothing to be overdue against
        facts = collect_file_transfer_facts(engine, now, {self._schedule_name: 300})

        assert facts == []

# ################################################################################################################################

    def test_each_schedule_measures_against_its_own_window(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Two schedules whose newest arrivals are equally old ..
        first_id = self._seed_arrival(audit_log, 'arrival-own-1')
        second_id = self._seed_arrival(audit_log, 'arrival-own-2', schedule=self._other_schedule_name)

        _backdate(first_id, now - timedelta(seconds=600))
        _backdate(second_id, now - timedelta(seconds=600))

        # .. but whose windows differ, so their ratios differ too
        arrival_windows = {
            self._schedule_name: 300,
            self._other_schedule_name: 1200,
        }

        facts = collect_file_transfer_facts(engine, now, arrival_windows)
        by_name = {fact['object_name']: fact for fact in facts}

        assert len(facts) == 2
        assert by_name[self._schedule_name]['arrival_overdue_ratio'] == 2.0
        assert by_name[self._other_schedule_name]['arrival_overdue_ratio'] == 0.5

# ################################################################################################################################

    def test_the_facts_flow_through_collect_facts(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        event_id = self._seed_arrival(audit_log, 'arrival-flow-1')
        _backdate(event_id, now - timedelta(seconds=900))

        facts = collect_facts(engine, {}, AuditSource.MLLP_Channel, now,
            arrival_windows={self._schedule_name: 300})

        by_name = {fact['object_name']: fact for fact in facts}

        assert by_name[self._schedule_name]['seconds_since_last_arrival'] == 900
        assert by_name[self._schedule_name]['arrival_overdue_ratio'] == 3.0

# ################################################################################################################################
# ################################################################################################################################

class TestPerSourceWindows:

    def test_a_source_with_a_window_of_its_own_is_measured_over_it(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # A file transfer error older than the default window but within
        # the file transfer type's own longer one
        event_id = audit_log.insert(AuditSource.File_Outgoing, AuditEvent.Message_Sent, 'sftp.backups',
            cid='window-1', outcome=AuditOutcome.Error)
        _backdate(event_id, now - timedelta(seconds=400))

        facts = collect_facts(engine, {}, AuditSource.MLLP_Channel, now,
            window_seconds=300, window_seconds_by_source={AuditSource.File_Outgoing: 600})

        by_name = {fact['object_name']: fact for fact in facts}

        assert by_name['sftp.backups']['error_count'] == 1
        assert by_name['sftp.backups']['window_seconds'] == 600

# ################################################################################################################################
# ################################################################################################################################

class TestCollectFacts:

    def test_the_measures_of_one_object_merge_into_one_fact(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # The same channel errors and sits silent at the same time
        _seed_outcome(audit_log, 'facts-merge-1', AuditOutcome.Error)

        metrics = EndpointMetrics()
        metrics.silence_seconds = 1200.0
        metrics_by_name = {_channel_name: metrics}

        facts = collect_facts(engine, metrics_by_name, AuditSource.MLLP_Channel, now)

        assert len(facts) == 1

        fact = facts[0]
        assert fact['error_rate'] == 1.0
        assert fact['total_count'] == 1
        assert fact['silent_seconds'] == 1200
        assert fact['outstanding'] == 0

# ################################################################################################################################

    def test_different_objects_stay_apart(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _seed_outcome(audit_log, 'facts-apart-1', AuditOutcome.Error)

        metrics = EndpointMetrics()
        metrics.silence_seconds = 700.0
        metrics_by_name = {_other_channel_name: metrics}

        facts = collect_facts(engine, metrics_by_name, AuditSource.MLLP_Channel, now)
        by_name = {fact['object_name']: fact for fact in facts}

        assert len(facts) == 2
        assert by_name[_channel_name]['error_rate'] == 1.0
        assert by_name[_channel_name]['silent_seconds'] == 0
        assert by_name[_other_channel_name]['silent_seconds'] == 700
        assert by_name[_other_channel_name]['error_rate'] == 0.0

# ################################################################################################################################
# ################################################################################################################################
