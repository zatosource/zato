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
from zato.common.alerting.engine import AlertTransports
from zato.common.alerting.model import AlertAction, Default_Dedup_Window_Seconds, FindingKind
from zato.common.alerting.sweep import collect_for_rule, parse_rule, run_sweep, Default_Error_Rate_Threshold
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.monitoring.health import EndpointMetrics
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.typing_ import anylist
    anylist = anylist
    datetime = datetime

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-sweep-server'

# The channels the tests seed events and metrics for
_channel_name = 'hl7.sweep.channel'
_other_channel_name = 'hl7.sweep.other'

# The addresses the email rules send to
_addresses = ['ops@example.com']

# ################################################################################################################################
# ################################################################################################################################

class _TransportRecorder:
    """ A stand-in for the real transports, remembering everything that went out.
    """
    def __init__(self) -> 'None':
        self.emails:'anylist' = []
        self.invocations:'anylist' = []
        self.publications:'anylist' = []
        self.posts:'anylist' = []

    def make(self) -> 'AlertTransports':
        out = AlertTransports()

        out.send_email = lambda addresses, subject, body: self.emails.append((addresses, subject, body))
        out.invoke_service = lambda service, payload: self.invocations.append((service, payload))
        out.publish = lambda topic, payload: self.publications.append((topic, payload))
        out.http_post = lambda url, payload: self.posts.append((url, payload))

        return out

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
    _ = audit_log.insert(AuditSource.HL7, AuditEvent.Ack_Sent, object_name, cid=cid, outcome=outcome)

# ################################################################################################################################
# ################################################################################################################################

class TestParseRule:

    def test_a_full_definition_round_trips(self) -> 'None':
        rule_data = {
            'kind': FindingKind.Error_Rate,
            'source': AuditSource.HL7,
            'object_name': _channel_name,
            'action': AlertAction.Slack,
            'action_config': {'webhook_url': 'https://hooks.example.com/services/T000/B000/XXX'},
            'config': {'window_seconds': 120, 'threshold': 0.5},
            'dedup_window_seconds': 1800,
            'is_active': True,
        }

        rule = parse_rule('degraded-channels', rule_data)

        assert rule.name == 'degraded-channels'
        assert rule.kind == FindingKind.Error_Rate
        assert rule.source == AuditSource.HL7
        assert rule.object_name == _channel_name
        assert rule.action == AlertAction.Slack
        assert rule.action_config['webhook_url'] == 'https://hooks.example.com/services/T000/B000/XXX'
        assert rule.config == {'window_seconds': 120, 'threshold': 0.5}
        assert rule.dedup_window_seconds == 1800
        assert rule.is_active is True

# ################################################################################################################################

    def test_a_minimal_definition_receives_the_defaults(self) -> 'None':
        rule_data = {
            'kind': FindingKind.Feed_Silent,
        }

        rule = parse_rule('silent-feeds', rule_data)

        assert rule.source == ''
        assert rule.object_name == ''
        assert rule.action == AlertAction.Email_Digest
        assert rule.action_config == {}
        assert rule.config == {}
        assert rule.dedup_window_seconds == Default_Dedup_Window_Seconds
        assert rule.is_active is True

# ################################################################################################################################
# ################################################################################################################################

class TestCollectForRule:

    def test_an_error_rate_rule_runs_its_collector_with_its_own_config(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Three of four outcomes are errors - a 75% error rate
        _seed_outcome(audit_log, 'sweep-er-1', AuditOutcome.Error)
        _seed_outcome(audit_log, 'sweep-er-2', AuditOutcome.Error)
        _seed_outcome(audit_log, 'sweep-er-3', AuditOutcome.Error)
        _seed_outcome(audit_log, 'sweep-er-4', AuditOutcome.OK)

        rule = parse_rule('degraded', {
            'kind': FindingKind.Error_Rate,
            'config': {'window_seconds': 3600, 'threshold': 0.5},
        })

        findings = collect_for_rule(engine, rule, {}, now)

        assert len(findings) == 1
        assert findings[0].kind == FindingKind.Error_Rate
        assert findings[0].object_name == _channel_name

# ################################################################################################################################

    def test_a_rule_below_its_threshold_collects_nothing(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # One of four outcomes is an error - a 25% error rate
        _seed_outcome(audit_log, 'sweep-low-1', AuditOutcome.Error)
        _seed_outcome(audit_log, 'sweep-low-2', AuditOutcome.OK)
        _seed_outcome(audit_log, 'sweep-low-3', AuditOutcome.OK)
        _seed_outcome(audit_log, 'sweep-low-4', AuditOutcome.OK)

        rule = parse_rule('degraded', {
            'kind': FindingKind.Error_Rate,
            'config': {'window_seconds': 3600, 'threshold': 0.5},
        })

        findings = collect_for_rule(engine, rule, {}, now)

        assert findings == []

# ################################################################################################################################

    def test_a_missing_followup_rule_finds_the_unanswered_message(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # One message sent past the deadline, never acknowledged
        event_id = audit_log.insert(AuditSource.HL7, AuditEvent.Message_Sent, _channel_name,
            cid='sweep-mf-1', msg_id='MSG-sweep-mf-1', outcome=AuditOutcome.OK)
        _backdate(event_id, now - timedelta(seconds=600))

        rule = parse_rule('sent-not-acked', {
            'kind': FindingKind.Missing_Followup,
            'config': {'deadline_seconds': 300},
        })

        findings = collect_for_rule(engine, rule, {}, now)

        assert len(findings) == 1
        assert findings[0].kind == FindingKind.Missing_Followup
        assert 'MSG-sweep-mf-1' in findings[0].message

# ################################################################################################################################

    def test_a_feed_silent_rule_runs_over_the_live_metrics(self) -> 'None':
        engine = get_audit_engine()
        now = utcnow()

        silent_metrics = EndpointMetrics()
        silent_metrics.silence_seconds = 900.0

        active_metrics = EndpointMetrics()
        active_metrics.silence_seconds = 5.0

        metrics_by_name = {
            _channel_name: silent_metrics,
            _other_channel_name: active_metrics,
        }

        rule = parse_rule('silent-feeds', {
            'kind': FindingKind.Feed_Silent,
            'config': {'silent_after_seconds': 600},
        })

        findings = collect_for_rule(engine, rule, metrics_by_name, now)

        assert len(findings) == 1
        assert findings[0].object_name == _channel_name

# ################################################################################################################################

    def test_an_unknown_kind_collects_nothing(self) -> 'None':
        engine = get_audit_engine()
        now = utcnow()

        rule = parse_rule('domain-pack-rule', {
            'kind': 'certificate-expiring',
        })

        findings = collect_for_rule(engine, rule, {}, now)

        assert findings == []

# ################################################################################################################################

    def test_the_defaults_apply_when_the_rule_has_no_config(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        now = utcnow()

        # Half the outcomes are errors - above the default 25% threshold
        _seed_outcome(audit_log, 'sweep-def-1', AuditOutcome.Error)
        _seed_outcome(audit_log, 'sweep-def-2', AuditOutcome.OK)

        rule = parse_rule('degraded', {
            'kind': FindingKind.Error_Rate,
        })

        findings = collect_for_rule(engine, rule, {}, now)

        assert len(findings) == 1
        assert str(round(Default_Error_Rate_Threshold * 100)) in findings[0].message

# ################################################################################################################################
# ################################################################################################################################

class TestRunSweep:

    def test_a_sweep_collects_dispatches_and_deduplicates(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        recorder = _TransportRecorder()
        now = utcnow()

        # A degraded channel the error-rate rule will notice
        _seed_outcome(audit_log, 'sweep-run-1', AuditOutcome.Error)
        _seed_outcome(audit_log, 'sweep-run-2', AuditOutcome.Error)

        rules = [
            parse_rule('degraded', {
                'kind': FindingKind.Error_Rate,
                'action': AlertAction.Email_Digest,
                'action_config': {'addresses': _addresses},
                'config': {'window_seconds': 3600, 'threshold': 0.5},
            }),
        ]

        # The first sweep raises and dispatches ..
        result = run_sweep(engine, rules, {}, recorder.make(), audit_log, 'cid-sweep-1', now)

        assert result.rule_count == 1
        assert result.finding_count == 1
        assert result.raised_count == 1
        assert result.deduplicated_count == 0
        assert result.dispatched == [('degraded', AlertAction.Email_Digest)]
        assert len(recorder.emails) == 1

        # .. and the second one, still inside the dedup window, only counts.
        result_2 = run_sweep(engine, rules, {}, recorder.make(), audit_log, 'cid-sweep-2', now)

        assert result_2.raised_count == 0
        assert result_2.deduplicated_count == 1
        assert result_2.dispatched == []

# ################################################################################################################################

    def test_an_inactive_rule_never_runs_its_collector(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        recorder = _TransportRecorder()
        now = utcnow()

        _seed_outcome(audit_log, 'sweep-off-1', AuditOutcome.Error)

        rules = [
            parse_rule('degraded', {
                'kind': FindingKind.Error_Rate,
                'action_config': {'addresses': _addresses},
                'config': {'window_seconds': 3600, 'threshold': 0.5},
                'is_active': False,
            }),
        ]

        result = run_sweep(engine, rules, {}, recorder.make(), audit_log, 'cid-sweep-off', now)

        assert result.rule_count == 0
        assert result.finding_count == 0
        assert result.dispatched == []

# ################################################################################################################################

    def test_two_rules_of_the_same_kind_never_cross_dispatch(self) -> 'None':
        audit_log = AuditLog(_server_name)
        engine = get_audit_engine()
        recorder = _TransportRecorder()
        now = utcnow()

        # Both channels are erroring, each rule watches only its own one
        _seed_outcome(audit_log, 'sweep-two-1', AuditOutcome.Error)
        _seed_outcome(audit_log, 'sweep-two-2', AuditOutcome.Error, object_name=_other_channel_name)

        rules = [
            parse_rule('degraded-main', {
                'kind': FindingKind.Error_Rate,
                'object_name': _channel_name,
                'action': AlertAction.Invoke_Service,
                'action_config': {'service': 'hl7.channel.restart'},
                'config': {'window_seconds': 3600, 'threshold': 0.5},
            }),
            parse_rule('degraded-other', {
                'kind': FindingKind.Error_Rate,
                'object_name': _other_channel_name,
                'action': AlertAction.Publish_To_Topic,
                'action_config': {'topic': 'zato.alerts'},
                'config': {'window_seconds': 3600, 'threshold': 0.5},
            }),
        ]

        result = run_sweep(engine, rules, {}, recorder.make(), audit_log, 'cid-sweep-two', now)

        # Each rule dispatched exactly once, through its own action
        assert result.raised_count == 2
        assert sorted(result.dispatched) == [
            ('degraded-main', AlertAction.Invoke_Service),
            ('degraded-other', AlertAction.Publish_To_Topic),
        ]

        assert len(recorder.invocations) == 1
        assert len(recorder.publications) == 1

        assert recorder.invocations[0][1]['object_name'] == _channel_name
        assert recorder.publications[0][1]['object_name'] == _other_channel_name

# ################################################################################################################################
# ################################################################################################################################
