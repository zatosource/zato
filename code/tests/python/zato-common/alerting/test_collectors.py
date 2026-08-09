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
from zato.common.alerting.collectors import collect_error_rate_facts, collect_facts, collect_feed_silent_facts, \
    collect_outstanding_facts, new_fact
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
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
