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
from zato.common.alerting.collectors import collect_auth_failure_facts, collect_canary_facts, collect_certificate_facts, \
    collect_consecutive_failure_facts, collect_error_rate_facts, collect_facts, collect_feed_silent_facts, \
    collect_health_facts, collect_latency_facts, collect_outstanding_facts, collect_scheduler_facts, new_fact, \
    Attr_Days_Left
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

class TestCanaryFacts:

    def test_the_newest_outcome_is_the_current_truth(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # A connection whose canary failed and one whose canary recovered
        _ = audit_log.insert(AuditSource.Canary, AuditEvent.Canary_Executed, _channel_name,
            cid='canary-1', outcome=AuditOutcome.OK)
        _ = audit_log.insert(AuditSource.Canary, AuditEvent.Canary_Executed, _channel_name,
            cid='canary-2', outcome=AuditOutcome.Error, status='Upload failed')

        _ = audit_log.insert(AuditSource.Canary, AuditEvent.Canary_Executed, _other_channel_name,
            cid='canary-3', outcome=AuditOutcome.Error, status='Upload failed')
        _ = audit_log.insert(AuditSource.Canary, AuditEvent.Canary_Executed, _other_channel_name,
            cid='canary-4', outcome=AuditOutcome.OK)

        facts = collect_canary_facts(engine, now)
        by_name = {fact['object_name']: fact for fact in facts}

        assert len(facts) == 2
        assert by_name[_channel_name]['canary_failed'] == 1
        assert by_name[_other_channel_name]['canary_failed'] == 0

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

class TestPerSourceWindows:

    def test_a_source_with_a_window_of_its_own_is_measured_over_it(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # A file transfer error older than the default window but within
        # the file transfer family's own longer one
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
