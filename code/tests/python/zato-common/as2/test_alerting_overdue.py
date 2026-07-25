# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# Zato
from zato.common.api import AS2
from zato.common.as2.alerting import collect_findings, Kind_Ack_Overdue, Kind_MDN_Overdue
from zato.common.as2.reconcile import MDNReconciler
from zato.common.audit_log.api import AuditSource
from zato.common.util.api import utcnow
from zato.edi.reconcile import Reconciler

from .alerting_helpers import AS2_From, AS2_To, findings_of_kind, new_config, Our_ISA_ID, Pair, Partner_ISA_ID, \
    Server_Name, X12_Pair

# ################################################################################################################################
# ################################################################################################################################

class TestOverdueMDNs:

    def test_an_overdue_mdn_raises_a_finding(self) -> 'None':

        reconciler = MDNReconciler(Server_Name)
        reconciler.record_message_sent(AS2_From, AS2_To, 'msg-1@zato', mic='abc, sha-256')

        config = new_config(ack_overdue_after=3600)

        # The sweep runs after the partner's window has passed.
        now = utcnow() + timedelta(seconds=3700)
        findings = collect_findings([config], now, server_name=Server_Name)
        findings = findings_of_kind(findings, Kind_MDN_Overdue)

        assert len(findings) == 1

        finding = findings[0]

        assert finding.source == AuditSource.AS2
        assert finding.partner == Pair
        assert 'msg-1@zato' in finding.message
        assert 'source=as2' in finding.link
        assert 'status=outstanding' in finding.link

# ################################################################################################################################

    def test_a_pending_mdn_inside_the_window_raises_nothing(self) -> 'None':

        reconciler = MDNReconciler(Server_Name)
        reconciler.record_message_sent(AS2_From, AS2_To, 'msg-1@zato', mic='abc, sha-256')

        config = new_config(ack_overdue_after=3600)

        # The sweep runs right after the send, well inside the window.
        now = utcnow()
        findings = collect_findings([config], now, server_name=Server_Name)
        findings = findings_of_kind(findings, Kind_MDN_Overdue)

        assert findings == []

# ################################################################################################################################

    def test_the_default_window_applies_without_a_matching_partner(self) -> 'None':

        # The pair maps to no configured partner, so the default window decides.
        reconciler = MDNReconciler(Server_Name)
        reconciler.record_message_sent('SomeoneElse', 'Unconfigured', 'msg-1@zato', mic='abc, sha-256')

        default_window = AS2.Alerting.Default_Ack_Overdue_Seconds

        # Inside the default window nothing is raised ..
        now = utcnow() + timedelta(seconds=default_window - 100)
        findings = collect_findings([], now, server_name=Server_Name)
        findings = findings_of_kind(findings, Kind_MDN_Overdue)

        assert findings == []

        # .. and past it the finding appears.
        now = utcnow() + timedelta(seconds=default_window + 100)
        findings = collect_findings([], now, server_name=Server_Name)
        findings = findings_of_kind(findings, Kind_MDN_Overdue)

        assert len(findings) == 1

# ################################################################################################################################

    def test_an_opted_out_partner_raises_nothing(self) -> 'None':

        reconciler = MDNReconciler(Server_Name)
        reconciler.record_message_sent(AS2_From, AS2_To, 'msg-1@zato', mic='abc, sha-256')

        config = new_config(ack_overdue_after=3600, alerting_opt_out=True)

        now = utcnow() + timedelta(seconds=3700)
        findings = collect_findings([config], now, server_name=Server_Name)
        findings = findings_of_kind(findings, Kind_MDN_Overdue)

        assert findings == []

# ################################################################################################################################
# ################################################################################################################################

class TestOverdueAcks:

    def test_an_overdue_acknowledgment_raises_a_finding(self) -> 'None':

        reconciler = Reconciler(Server_Name)
        reconciler.record_interchange_sent(Our_ISA_ID, Partner_ISA_ID, '000000001')

        # The partner maps back through its EDI identifier.
        config = new_config(ack_overdue_after=3600)

        now = utcnow() + timedelta(seconds=3700)
        findings = collect_findings([config], now, server_name=Server_Name)
        findings = findings_of_kind(findings, Kind_Ack_Overdue)

        assert len(findings) == 1

        finding = findings[0]

        assert finding.source == AuditSource.X12
        assert finding.partner == X12_Pair
        assert '1' in finding.message
        assert 'source=x12' in finding.link
        assert 'status=outstanding' in finding.link

# ################################################################################################################################

    def test_an_acknowledged_interchange_raises_nothing(self) -> 'None':

        reconciler = Reconciler(Server_Name)
        reconciler.record_interchange_sent(Our_ISA_ID, Partner_ISA_ID, '000000001')
        reconciler.record_ack_received(Our_ISA_ID, Partner_ISA_ID, '000000001')

        config = new_config(ack_overdue_after=3600)

        now = utcnow() + timedelta(seconds=3700)
        findings = collect_findings([config], now, server_name=Server_Name)
        findings = findings_of_kind(findings, Kind_Ack_Overdue)

        assert findings == []

# ################################################################################################################################

    def test_an_opted_out_partner_raises_nothing(self) -> 'None':

        reconciler = Reconciler(Server_Name)
        reconciler.record_interchange_sent(Our_ISA_ID, Partner_ISA_ID, '000000001')

        config = new_config(ack_overdue_after=3600, alerting_opt_out=True)

        now = utcnow() + timedelta(seconds=3700)
        findings = collect_findings([config], now, server_name=Server_Name)
        findings = findings_of_kind(findings, Kind_Ack_Overdue)

        assert findings == []

# ################################################################################################################################
# ################################################################################################################################
