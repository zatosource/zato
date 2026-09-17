# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# Zato
from zato.common.alerting.collectors import collect_auth_failure_facts, collect_consecutive_failure_facts, \
    collect_error_rate_facts, collect_latency_facts, new_fact
from zato.common.audit_log.api import get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.util.api import utcnow

# Local
from alerting_seeds import backdate, seed_exchange, seed_outcome, Channel_Name, Connection_Name, Other_Channel_Name, Server_Name, \
    Window_Seconds

# ################################################################################################################################
# ################################################################################################################################

class TestNewFact:

    def test_a_resting_fact_carries_every_measure_at_zero(self) -> 'None':
        fact = new_fact(AuditSource.MLLP_Channel, Channel_Name)

        assert fact['source'] == AuditSource.MLLP_Channel
        assert fact['object_name'] == Channel_Name
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
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        # Three of four outcomes are errors - a 75% error rate
        seed_outcome(audit_log, 'facts-er-1', AuditOutcome.Error)
        seed_outcome(audit_log, 'facts-er-2', AuditOutcome.Error)
        seed_outcome(audit_log, 'facts-er-3', AuditOutcome.Error)
        seed_outcome(audit_log, 'facts-er-4', AuditOutcome.OK)

        facts = collect_error_rate_facts(engine, Window_Seconds, now)

        assert len(facts) == 1

        fact = facts[0]
        assert fact['source'] == AuditSource.MLLP_Channel
        assert fact['object_name'] == Channel_Name
        assert fact['error_rate'] == 0.75
        assert fact['error_count'] == 3
        assert fact['total_count'] == 4
        assert fact['window_seconds'] == Window_Seconds

# ################################################################################################################################

    def test_each_object_gets_its_own_fact(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        seed_outcome(audit_log, 'facts-two-1', AuditOutcome.Error)
        seed_outcome(audit_log, 'facts-two-2', AuditOutcome.OK, object_name=Other_Channel_Name)

        facts = collect_error_rate_facts(engine, Window_Seconds, now)
        by_name = {fact['object_name']: fact for fact in facts}

        assert len(facts) == 2
        assert by_name[Channel_Name]['error_rate'] == 1.0
        assert by_name[Other_Channel_Name]['error_rate'] == 0.0

# ################################################################################################################################

    def test_a_soap_outgoing_connection_whose_every_call_fails_reads_a_full_error_rate(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        # Only the response half of each pair is measured, the way it is for a REST connection,
        # so three failed calls read as three errors out of three and not out of six
        seed_exchange(audit_log, AuditSource.SOAP_Outgoing, 'soap-rate-1', AuditOutcome.Error)
        seed_exchange(audit_log, AuditSource.SOAP_Outgoing, 'soap-rate-2', AuditOutcome.Error)
        seed_exchange(audit_log, AuditSource.SOAP_Outgoing, 'soap-rate-3', AuditOutcome.Error)

        facts = collect_error_rate_facts(engine, Window_Seconds, now, source=AuditSource.SOAP_Outgoing)

        assert len(facts) == 1

        fact = facts[0]
        assert fact['source'] == AuditSource.SOAP_Outgoing
        assert fact['object_name'] == Connection_Name
        assert fact['error_rate'] == 1.0
        assert fact['error_count'] == 3
        assert fact['total_count'] == 3

# ################################################################################################################################

    def test_traffic_outside_the_window_never_counts(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        # One error, moved outside the window
        event_id = audit_log.insert(AuditSource.MLLP_Channel, AuditEvent.Ack_Sent, Channel_Name,
            cid='facts-old-1', outcome=AuditOutcome.Error)
        backdate(event_id, now - timedelta(seconds=Window_Seconds + 60))

        facts = collect_error_rate_facts(engine, Window_Seconds, now)

        assert facts == []

# ################################################################################################################################

    def test_the_newest_failing_event_of_a_resubmittable_type_is_pointed_at(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        # Two failed per-hop deliveries of a source counting every event - the request-sent type is what
        # their source declared resubmittable, and the newer of the two is the one to point at
        _ = audit_log.insert(AuditSource.Email_SMTP, AuditEvent.Request_Sent, Channel_Name,
            cid='resub-er-1', outcome=AuditOutcome.Error)
        newest_id = audit_log.insert(AuditSource.Email_SMTP, AuditEvent.Request_Sent, Channel_Name,
            cid='resub-er-2', outcome=AuditOutcome.Error)

        facts = collect_error_rate_facts(engine, Window_Seconds, now)

        assert len(facts) == 1
        assert facts[0]['last_error_event_id'] == newest_id
        assert facts[0]['is_resubmittable'] == 1

# ################################################################################################################################

    def test_a_failing_event_of_an_undeclared_type_is_pointed_at_without_a_resend_offer(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        # An outbound acknowledgment is no type its source declared resubmittable
        event_id = audit_log.insert(AuditSource.MLLP_Channel, AuditEvent.Ack_Sent, Channel_Name,
            cid='resub-er-3', outcome=AuditOutcome.Error)

        facts = collect_error_rate_facts(engine, Window_Seconds, now)

        assert len(facts) == 1
        assert facts[0]['last_error_event_id'] == event_id
        assert facts[0]['is_resubmittable'] == 0

# ################################################################################################################################

    def test_an_object_without_failures_points_at_nothing(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        _ = audit_log.insert(AuditSource.Email_SMTP, AuditEvent.Request_Sent, Channel_Name,
            cid='resub-er-4', outcome=AuditOutcome.OK)

        facts = collect_error_rate_facts(engine, Window_Seconds, now)

        assert len(facts) == 1
        assert facts[0]['last_error_event_id'] == 0
        assert facts[0]['is_resubmittable'] == 0

# ################################################################################################################################
# ################################################################################################################################


class TestConsecutiveFailureFacts:

    def test_an_unbroken_run_of_errors_is_counted(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        seed_outcome(audit_log, 'consec-1', AuditOutcome.OK)
        seed_outcome(audit_log, 'consec-2', AuditOutcome.Error)
        seed_outcome(audit_log, 'consec-3', AuditOutcome.Error)
        seed_outcome(audit_log, 'consec-4', AuditOutcome.Error)

        facts = collect_consecutive_failure_facts(engine, now)

        assert len(facts) == 1
        assert facts[0]['consecutive_failures'] == 3

# ################################################################################################################################

    def test_a_success_breaks_the_streak(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        # The newest outcome is an error but the one before it is not
        seed_outcome(audit_log, 'break-1', AuditOutcome.Error)
        seed_outcome(audit_log, 'break-2', AuditOutcome.OK)
        seed_outcome(audit_log, 'break-3', AuditOutcome.Error)

        facts = collect_consecutive_failure_facts(engine, now)

        assert len(facts) == 1
        assert facts[0]['consecutive_failures'] == 1

# ################################################################################################################################

    def test_the_ok_halves_of_paired_events_never_hide_a_streak(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        # A source that writes paired events - the request half always leaves with an OK
        # outcome while the response half carries the real one
        for index in range(3):
            _ = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, Channel_Name,
                cid=f'paired-{index}', outcome=AuditOutcome.OK)
            _ = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Response_Received, Channel_Name,
                cid=f'paired-{index}', outcome=AuditOutcome.Error)

        facts = collect_consecutive_failure_facts(engine, now)

        assert len(facts) == 1
        assert facts[0]['consecutive_failures'] == 3

# ################################################################################################################################

    def test_a_clean_object_still_reports_a_zero(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        seed_outcome(audit_log, 'clean-1', AuditOutcome.OK)

        facts = collect_consecutive_failure_facts(engine, now)

        assert len(facts) == 1
        assert facts[0]['consecutive_failures'] == 0

# ################################################################################################################################
# ################################################################################################################################

class TestHealthCheckStreamIsCountedApart:

    def test_a_failing_ping_does_not_add_to_the_traffic_streak(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        # One connection, failing on both what it carries and what watches it
        seed_exchange(audit_log, AuditSource.REST_Outgoing, 'apart-call-1', AuditOutcome.Error)
        seed_exchange(audit_log, AuditSource.REST_Outgoing, 'apart-call-2', AuditOutcome.Error)
        seed_exchange(audit_log, AuditSource.REST_Outgoing_Health, 'apart-check-1', AuditOutcome.Error)
        seed_exchange(audit_log, AuditSource.REST_Outgoing_Health, 'apart-check-2', AuditOutcome.Error)

        facts = collect_consecutive_failure_facts(engine, now)

        streaks_by_source = {}

        for fact in facts:
            assert fact['object_name'] == Connection_Name
            streaks_by_source[fact['source']] = fact['consecutive_failures']

        # Two streams of two, rather than one of four
        assert streaks_by_source == {
            AuditSource.REST_Outgoing: 2,
            AuditSource.REST_Outgoing_Health: 2,
        }

# ################################################################################################################################

    def test_a_succeeding_ping_no_longer_breaks_the_traffic_streak(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        # A check that answers between failing calls, oldest first. On one shared stream the
        # newest three outcomes would read OK, error, OK and the streak would stop at one.
        seed_exchange(audit_log, AuditSource.REST_Outgoing, 'interleaved-call-1', AuditOutcome.Error)
        seed_exchange(audit_log, AuditSource.REST_Outgoing_Health, 'interleaved-check-1', AuditOutcome.OK)
        seed_exchange(audit_log, AuditSource.REST_Outgoing, 'interleaved-call-2', AuditOutcome.Error)
        seed_exchange(audit_log, AuditSource.REST_Outgoing_Health, 'interleaved-check-2', AuditOutcome.OK)
        seed_exchange(audit_log, AuditSource.REST_Outgoing, 'interleaved-call-3', AuditOutcome.Error)

        facts = collect_consecutive_failure_facts(engine, now)

        streaks_by_source = {}

        for fact in facts:
            streaks_by_source[fact['source']] = fact['consecutive_failures']

        # The three failed calls are an unbroken run, and the answering check says so
        assert streaks_by_source[AuditSource.REST_Outgoing] == 3
        assert streaks_by_source[AuditSource.REST_Outgoing_Health] == 0

# ################################################################################################################################

    def test_a_connection_with_only_a_health_check_reports_only_the_health_source(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        seed_exchange(audit_log, AuditSource.REST_Outgoing_Health, 'only-check-1', AuditOutcome.Error)
        seed_exchange(audit_log, AuditSource.REST_Outgoing_Health, 'only-check-2', AuditOutcome.Error)
        seed_exchange(audit_log, AuditSource.REST_Outgoing_Health, 'only-check-3', AuditOutcome.Error)

        facts = collect_consecutive_failure_facts(engine, now)

        assert len(facts) == 1

        fact = facts[0]
        assert fact['source'] == AuditSource.REST_Outgoing_Health
        assert fact['object_name'] == Connection_Name
        assert fact['consecutive_failures'] == 3

# ################################################################################################################################

    def test_a_soap_check_is_counted_apart_from_soap_traffic(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        seed_exchange(audit_log, AuditSource.SOAP_Outgoing, 'soap-call-1', AuditOutcome.Error)
        seed_exchange(audit_log, AuditSource.SOAP_Outgoing_Health, 'soap-check-1', AuditOutcome.Error)
        seed_exchange(audit_log, AuditSource.SOAP_Outgoing_Health, 'soap-check-2', AuditOutcome.Error)

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
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        # An unbroken run of failed per-hop deliveries - the newest one is the one
        # to point at, and its type is what its source declared resubmittable
        _ = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, Channel_Name,
            cid='resub-cf-1', outcome=AuditOutcome.Error)
        newest_id = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, Channel_Name,
            cid='resub-cf-2', outcome=AuditOutcome.Error)

        facts = collect_consecutive_failure_facts(engine, now)

        assert len(facts) == 1
        assert facts[0]['consecutive_failures'] == 2
        assert facts[0]['last_error_event_id'] == newest_id
        assert facts[0]['is_resubmittable'] == 1

# ################################################################################################################################

    def test_a_clean_object_points_at_nothing(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        # A failure with a recovery after it - no streak, so nothing to point at either
        seed_outcome(audit_log, 'resub-cf-3', AuditOutcome.Error)
        seed_outcome(audit_log, 'resub-cf-4', AuditOutcome.OK)

        facts = collect_consecutive_failure_facts(engine, now)

        assert len(facts) == 1
        assert facts[0]['consecutive_failures'] == 0
        assert facts[0]['last_error_event_id'] == 0
        assert facts[0]['is_resubmittable'] == 0

# ################################################################################################################################
# ################################################################################################################################

class TestLatencyFacts:

    def test_the_average_covers_only_events_that_carry_a_duration(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        # Two completed calls with durations and one request event without one
        _ = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Response_Received, Channel_Name,
            cid='lat-1', outcome=AuditOutcome.OK, duration_ms=100)
        _ = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Response_Received, Channel_Name,
            cid='lat-2', outcome=AuditOutcome.OK, duration_ms=300)
        _ = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Request_Sent, Channel_Name,
            cid='lat-3', outcome=AuditOutcome.OK)

        facts = collect_latency_facts(engine, Window_Seconds, now)

        assert len(facts) == 1
        assert facts[0]['avg_duration_ms'] == 200
        assert facts[0]['window_seconds'] == Window_Seconds

# ################################################################################################################################

    def test_traffic_outside_the_window_never_counts(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        event_id = audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Response_Received, Channel_Name,
            cid='lat-old-1', outcome=AuditOutcome.OK, duration_ms=9000)
        backdate(event_id, now - timedelta(seconds=Window_Seconds + 60))

        facts = collect_latency_facts(engine, Window_Seconds, now)

        assert facts == []

# ################################################################################################################################
# ################################################################################################################################

class TestAuthFailureFacts:

    def test_only_the_auth_failed_events_are_counted(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        # Two credentials rejections and one ordinary failure
        _ = audit_log.insert(AuditSource.Email_SMTP, AuditEvent.Auth_Failed, Channel_Name,
            cid='auth-1', outcome=AuditOutcome.Error)
        _ = audit_log.insert(AuditSource.Email_SMTP, AuditEvent.Auth_Failed, Channel_Name,
            cid='auth-2', outcome=AuditOutcome.Error)
        _ = audit_log.insert(AuditSource.Email_SMTP, AuditEvent.Message_Sent, Channel_Name,
            cid='auth-3', outcome=AuditOutcome.Error)

        facts = collect_auth_failure_facts(engine, Window_Seconds, now)

        assert len(facts) == 1
        assert facts[0]['auth_failure_count'] == 2

# ################################################################################################################################
# ################################################################################################################################
