# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# Zato
from zato.common.as2.alerting import collect_findings, Kind_Ship_Notice_Missing
from zato.common.audit_log.api import AuditSource
from zato.common.util.api import utcnow
from zato.edi.reconcile import Reconciler

# Zato
from .alerting_helpers import findings_of_kind, new_config, Our_ISA_ID, Partner_ISA_ID, Server_Name

# ################################################################################################################################
# ################################################################################################################################

class TestShipNoticeGuard:

    def test_an_unanswered_order_past_the_window_raises_a_finding(self) -> 'None':

        reconciler = Reconciler(Server_Name)

        # An 850 arrived from the partner and nothing went back.
        reconciler.record_interchange_received(Partner_ISA_ID, Our_ISA_ID, '000000042', document_type='850')

        config = new_config(ship_notice_window_hours=4)

        now = utcnow() + timedelta(hours=5)
        findings = collect_findings([config], now, server_name=Server_Name)
        findings = findings_of_kind(findings, Kind_Ship_Notice_Missing)

        assert len(findings) == 1

        finding = findings[0]

        assert finding.source == AuditSource.X12
        assert finding.partner == f'{Partner_ISA_ID}:{Our_ISA_ID}'
        assert '42' in finding.message
        assert 'ship notice' in finding.message
        assert 'source=x12' in finding.link

# ################################################################################################################################

    def test_a_ship_notice_sent_back_answers_the_order(self) -> 'None':

        reconciler = Reconciler(Server_Name)

        reconciler.record_interchange_received(Partner_ISA_ID, Our_ISA_ID, '000000042', document_type='850')
        reconciler.record_interchange_sent(Our_ISA_ID, Partner_ISA_ID, '000000043', document_type='856')

        config = new_config(ship_notice_window_hours=4)

        now = utcnow() + timedelta(hours=5)
        findings = collect_findings([config], now, server_name=Server_Name)
        findings = findings_of_kind(findings, Kind_Ship_Notice_Missing)

        assert findings == []

# ################################################################################################################################

    def test_a_notice_sent_before_the_order_does_not_answer_it(self) -> 'None':

        reconciler = Reconciler(Server_Name)

        # The notice went out first, so it answers whatever came before it, not this order.
        reconciler.record_interchange_sent(Our_ISA_ID, Partner_ISA_ID, '000000043', document_type='856')
        reconciler.record_interchange_received(Partner_ISA_ID, Our_ISA_ID, '000000042', document_type='850')

        config = new_config(ship_notice_window_hours=4)

        now = utcnow() + timedelta(hours=5)
        findings = collect_findings([config], now, server_name=Server_Name)
        findings = findings_of_kind(findings, Kind_Ship_Notice_Missing)

        assert len(findings) == 1

        finding = findings[0]
        assert '42' in finding.message

# ################################################################################################################################

    def test_a_notice_to_one_partner_does_not_answer_another_ones_order(self) -> 'None':

        reconciler = Reconciler(Server_Name)
        other_isa_id = 'PARTNERCORPEU'

        # Both partners ordered and only one of them got a ship notice back.
        reconciler.record_interchange_received(Partner_ISA_ID, Our_ISA_ID, '000000042', document_type='850')
        reconciler.record_interchange_received(other_isa_id, Our_ISA_ID, '000000044', document_type='850')
        reconciler.record_interchange_sent(Our_ISA_ID, other_isa_id, '000000045', document_type='856')

        first = new_config(ship_notice_window_hours=4)

        options = {
            'name': 'PartnerCorp EU AS2',
            'as2_to': 'PartnerCorpEU',
            'isa_id': other_isa_id,
            'ship_notice_window_hours': 4,
        }

        second = new_config(**options)

        now = utcnow() + timedelta(hours=5)
        findings = collect_findings([first, second], now, server_name=Server_Name)
        findings = findings_of_kind(findings, Kind_Ship_Notice_Missing)

        assert len(findings) == 1

        finding = findings[0]
        assert finding.partner == f'{Partner_ISA_ID}:{Our_ISA_ID}'

# ################################################################################################################################

    def test_an_order_inside_the_window_raises_nothing(self) -> 'None':

        reconciler = Reconciler(Server_Name)
        reconciler.record_interchange_received(Partner_ISA_ID, Our_ISA_ID, '000000042', document_type='850')

        config = new_config(ship_notice_window_hours=4)

        now = utcnow()
        findings = collect_findings([config], now, server_name=Server_Name)
        findings = findings_of_kind(findings, Kind_Ship_Notice_Missing)

        assert findings == []

# ################################################################################################################################

    def test_a_partner_without_a_window_is_not_guarded(self) -> 'None':

        reconciler = Reconciler(Server_Name)
        reconciler.record_interchange_received(Partner_ISA_ID, Our_ISA_ID, '000000042', document_type='850')

        config = new_config()

        now = utcnow() + timedelta(hours=5)
        findings = collect_findings([config], now, server_name=Server_Name)
        findings = findings_of_kind(findings, Kind_Ship_Notice_Missing)

        assert findings == []

# ################################################################################################################################
# ################################################################################################################################
