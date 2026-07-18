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
from zato.common.alerting.collectors import collect_error_rate, collect_feed_silent, collect_missing_followups, \
    collect_outstanding_threshold
from zato.common.alerting.model import FindingKind
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

# The deadline the absence checks give a follow-up, in seconds
_deadline_seconds = 300

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

def _seed_sent(audit_log:'AuditLog', cid:'str', event_time:'datetime', *, object_name:'str'=_channel_name) -> 'int':
    """ Stores one outbound message the way the live pipeline would have recorded it.
    """
    event_id = audit_log.insert(AuditSource.HL7, AuditEvent.Message_Sent, object_name,
        cid=cid, msg_id=f'MSG-{cid}', outcome=AuditOutcome.OK)

    _backdate(event_id, event_time)

    return event_id

# ################################################################################################################################

def _seed_ack(audit_log:'AuditLog', cid:'str', event_time:'datetime') -> 'None':
    """ Stores the acknowledgment that answers one outbound message.
    """
    event_id = audit_log.insert(AuditSource.HL7, AuditEvent.Ack_Received, _channel_name,
        cid=cid, outcome=AuditOutcome.OK)

    _backdate(event_id, event_time)

# ################################################################################################################################
# ################################################################################################################################

class TestMissingFollowups:

    def test_a_message_without_its_ack_past_the_deadline_is_a_finding(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Sent long ago, never acknowledged ..
        _ = _seed_sent(audit_log, 'cid-overdue', now - timedelta(seconds=600))

        # .. sent long ago and acknowledged ..
        _ = _seed_sent(audit_log, 'cid-answered', now - timedelta(seconds=600))
        _seed_ack(audit_log, 'cid-answered', now - timedelta(seconds=550))

        # .. sent a moment ago - still inside its deadline.
        _ = _seed_sent(audit_log, 'cid-recent', now - timedelta(seconds=10))

        findings = collect_missing_followups(engine, AuditSource.HL7,
            AuditEvent.Message_Sent, AuditEvent.Ack_Received, _deadline_seconds, now)

        # Only the overdue unanswered one raises a finding
        assert len(findings) == 1
        assert findings[0].kind == FindingKind.Missing_Followup
        assert findings[0].source == AuditSource.HL7
        assert findings[0].object_name == _channel_name
        assert 'MSG-cid-overdue' in findings[0].message

# ################################################################################################################################

    def test_the_object_filter_narrows_the_sweep(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_sent(audit_log, 'cid-ours', now - timedelta(seconds=600))
        _ = _seed_sent(audit_log, 'cid-other', now - timedelta(seconds=600), object_name=_other_channel_name)

        findings = collect_missing_followups(engine, AuditSource.HL7,
            AuditEvent.Message_Sent, AuditEvent.Ack_Received, _deadline_seconds, now,
            object_name=_other_channel_name)

        assert len(findings) == 1
        assert findings[0].object_name == _other_channel_name

# ################################################################################################################################
# ################################################################################################################################

class TestOutstandingThreshold:

    def test_a_backlog_at_the_threshold_is_a_finding_per_object(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Three outstanding on one channel, one on the other
        for index in range(3):
            _ = _seed_sent(audit_log, f'cid-backlog-{index}', now)

        _ = _seed_sent(audit_log, 'cid-single', now, object_name=_other_channel_name)

        findings = collect_outstanding_threshold(engine, AuditSource.HL7,
            AuditEvent.Message_Sent, AuditEvent.Ack_Received, 3)

        # Only the channel that reached the threshold raises a finding
        assert len(findings) == 1
        assert findings[0].kind == FindingKind.Outstanding
        assert findings[0].object_name == _channel_name
        assert '3 outstanding' in findings[0].message

# ################################################################################################################################

    def test_answered_messages_never_count_toward_the_backlog(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        _ = _seed_sent(audit_log, 'cid-answered', now)
        _seed_ack(audit_log, 'cid-answered', now)

        _ = _seed_sent(audit_log, 'cid-waiting', now)

        findings = collect_outstanding_threshold(engine, AuditSource.HL7,
            AuditEvent.Message_Sent, AuditEvent.Ack_Received, 2)

        assert findings == []

# ################################################################################################################################
# ################################################################################################################################

class TestErrorRate:

    def test_a_channel_erroring_at_the_threshold_is_a_finding(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Half of the recent messages on one channel failed ..
        for index in range(2):
            _ = audit_log.insert(AuditSource.HL7, AuditEvent.Message_Received, _channel_name,
                cid=f'cid-rate-ok-{index}', outcome=AuditOutcome.OK)

        for index in range(2):
            _ = audit_log.insert(AuditSource.HL7, AuditEvent.Message_Received, _channel_name,
                cid=f'cid-rate-error-{index}', outcome=AuditOutcome.Error)

        # .. while the other channel stays clean.
        _ = audit_log.insert(AuditSource.HL7, AuditEvent.Message_Received, _other_channel_name,
            cid='cid-rate-clean', outcome=AuditOutcome.OK)

        findings = collect_error_rate(engine, AuditSource.HL7, 300, 0.5, now)

        assert len(findings) == 1
        assert findings[0].kind == FindingKind.Error_Rate
        assert findings[0].object_name == _channel_name
        assert '50%' in findings[0].message

# ################################################################################################################################

    def test_old_errors_fall_out_of_the_window(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        event_id = audit_log.insert(AuditSource.HL7, AuditEvent.Message_Received, _channel_name,
            cid='cid-rate-old', outcome=AuditOutcome.Error)
        _backdate(event_id, now - timedelta(seconds=600))

        findings = collect_error_rate(engine, AuditSource.HL7, 300, 0.5, now)

        assert findings == []

# ################################################################################################################################
# ################################################################################################################################

class TestFeedSilent:

    def test_a_quiet_feed_is_a_finding(self) -> 'None':

        silent = EndpointMetrics()
        silent.silence_seconds = 400.0

        active = EndpointMetrics()
        active.silence_seconds = 5.0

        metrics_by_name = {
            _channel_name: silent,
            _other_channel_name: active,
        }

        findings = collect_feed_silent(metrics_by_name, AuditSource.HL7, 300.0)

        assert len(findings) == 1
        assert findings[0].kind == FindingKind.Feed_Silent
        assert findings[0].object_name == _channel_name
        assert 'silent for 400s' in findings[0].message

# ################################################################################################################################

    def test_a_feed_that_never_started_is_not_silent(self) -> 'None':

        # Zero silence means nothing arrived yet - a configuration matter, not a dead feed
        never_started = EndpointMetrics()
        never_started.silence_seconds = 0.0

        findings = collect_feed_silent({_channel_name: never_started}, AuditSource.HL7, 300.0)

        assert findings == []

# ################################################################################################################################
# ################################################################################################################################
