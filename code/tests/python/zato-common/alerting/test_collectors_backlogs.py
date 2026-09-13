# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# Zato
from zato.common.alerting.collectors import collect_feed_silent_facts, collect_outstanding_facts
from zato.common.audit_log.api import get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.monitoring.health import EndpointMetrics
from zato.common.util.api import utcnow

# Local
from alerting_seeds import backdate, Channel_Name, Other_Channel_Name, Server_Name

# ################################################################################################################################
# ################################################################################################################################

class TestOutstandingFacts:

    def test_a_message_without_its_followup_counts_with_its_age(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        # One message sent ten minutes ago, never acknowledged
        event_id = audit_log.insert(AuditSource.MLLP_Outgoing, AuditEvent.Message_Sent, Channel_Name,
            cid='facts-mf-1', msg_id='MSG-facts-mf-1', outcome=AuditOutcome.OK)
        backdate(event_id, now - timedelta(seconds=600))

        facts = collect_outstanding_facts(engine, AuditEvent.Message_Sent, AuditEvent.Ack_Received, now)

        assert len(facts) == 1

        fact = facts[0]
        assert fact['source'] == AuditSource.MLLP_Outgoing
        assert fact['object_name'] == Channel_Name
        assert fact['outstanding'] == 1
        assert fact['oldest_waiting_seconds'] >= 599

# ################################################################################################################################

    def test_an_answered_message_never_counts(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        # A message and its acknowledgment, on the same correlation id
        _ = audit_log.insert(AuditSource.MLLP_Outgoing, AuditEvent.Message_Sent, Channel_Name,
            cid='facts-ok-1', outcome=AuditOutcome.OK)
        _ = audit_log.insert(AuditSource.MLLP_Outgoing, AuditEvent.Ack_Received, Channel_Name,
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
            Channel_Name: silent_metrics,
            Other_Channel_Name: never_active_metrics,
        }

        facts = collect_feed_silent_facts(metrics_by_name, AuditSource.MLLP_Channel)

        assert len(facts) == 1
        assert facts[0]['object_name'] == Channel_Name
        assert facts[0]['silent_seconds'] == 900

# ################################################################################################################################
# ################################################################################################################################
