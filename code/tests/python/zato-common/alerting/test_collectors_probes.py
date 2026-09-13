# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.alerting.collectors import collect_certificate_facts, collect_health_facts, collect_test_transfer_facts, \
    Attr_Days_Left
from zato.common.audit_log.api import get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.util.api import utcnow

# Local
from conftest import Channel_Name, Other_Channel_Name, Server_Name

# ################################################################################################################################
# ################################################################################################################################

class TestCertificateFacts:

    def test_the_newest_days_left_measure_surfaces(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        # An older measure and a newer one - only the newer one speaks
        _ = audit_log.insert(AuditSource.Certificate, AuditEvent.Cert_Checked, Channel_Name,
            cid='cert-1', outcome=AuditOutcome.OK, attrs={Attr_Days_Left: 30.0})
        _ = audit_log.insert(AuditSource.Certificate, AuditEvent.Cert_Checked, Channel_Name,
            cid='cert-2', outcome=AuditOutcome.OK, attrs={Attr_Days_Left: 5.4})

        facts = collect_certificate_facts(engine, now)

        assert len(facts) == 1
        assert facts[0]['object_name'] == Channel_Name
        assert facts[0]['cert_days_left'] == 5

# ################################################################################################################################

    def test_a_failed_check_reports_nothing_rather_than_a_false_zero(self) -> 'None':
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        # A handshake that failed wrote an error event with no days-left attr
        _ = audit_log.insert(AuditSource.Certificate, AuditEvent.Cert_Checked, Channel_Name,
            cid='cert-err-1', outcome=AuditOutcome.Error, status='Connection refused')

        facts = collect_certificate_facts(engine, now)

        assert facts == []

# ################################################################################################################################
# ################################################################################################################################

class TestHealthFacts:

    def test_the_newest_state_of_each_service_surfaces(self) -> 'None':
        audit_log = AuditLog(Server_Name)
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
        audit_log = AuditLog(Server_Name)
        engine = get_audit_engine()
        now = utcnow()

        # A connection whose test transfer failed and one whose test transfer recovered
        _ = audit_log.insert(AuditSource.Test_Transfer, AuditEvent.Test_Transfer_Executed, Channel_Name,
            cid='test-transfer-1', outcome=AuditOutcome.OK)
        _ = audit_log.insert(AuditSource.Test_Transfer, AuditEvent.Test_Transfer_Executed, Channel_Name,
            cid='test-transfer-2', outcome=AuditOutcome.Error, status='Upload failed')

        _ = audit_log.insert(AuditSource.Test_Transfer, AuditEvent.Test_Transfer_Executed, Other_Channel_Name,
            cid='test-transfer-3', outcome=AuditOutcome.Error, status='Upload failed')
        _ = audit_log.insert(AuditSource.Test_Transfer, AuditEvent.Test_Transfer_Executed, Other_Channel_Name,
            cid='test-transfer-4', outcome=AuditOutcome.OK)

        facts = collect_test_transfer_facts(engine, now)
        by_name = {fact['object_name']: fact for fact in facts}

        assert len(facts) == 2
        assert by_name[Channel_Name]['test_transfer_failed'] == 1
        assert by_name[Other_Channel_Name]['test_transfer_failed'] == 0

# ################################################################################################################################
# ################################################################################################################################
