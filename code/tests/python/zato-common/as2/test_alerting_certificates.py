# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.as2.alerting import collect_findings, get_cert_days_left, Kind_Cert_Expiry, Own_Keystore_Name
from zato.common.audit_log.api import AuditSource
from zato.common.util.api import utcnow

from .alerting_helpers import findings_of_kind, make_certificate_pem, new_config, Pair, Server_Name

# ################################################################################################################################
# ################################################################################################################################

# How many days are left on a certificate the sweep is expected to warn about
# and on one it is expected to stay quiet about.
_expiring_days_left = 10
_healthy_days_left = 365

# ################################################################################################################################
# ################################################################################################################################

class TestExpiringCertificates:

    def test_a_partner_certificate_inside_the_window_raises_a_finding(self) -> 'None':

        certificate_pem = make_certificate_pem(_expiring_days_left)
        config = new_config(as2_partner_cert=certificate_pem)

        now = utcnow()
        findings = collect_findings([config], now, server_name=Server_Name)
        findings = findings_of_kind(findings, Kind_Cert_Expiry)

        assert len(findings) == 1

        finding = findings[0]

        assert finding.source == AuditSource.AS2
        assert finding.partner == Pair
        assert 'PartnerCorp AS2' in finding.message
        assert 'expires in' in finding.message

# ################################################################################################################################

    def test_a_healthy_partner_certificate_raises_nothing(self) -> 'None':

        certificate_pem = make_certificate_pem(_healthy_days_left)
        config = new_config(as2_partner_cert=certificate_pem)

        now = utcnow()
        findings = collect_findings([config], now, server_name=Server_Name)
        findings = findings_of_kind(findings, Kind_Cert_Expiry)

        assert findings == []

# ################################################################################################################################

    def test_our_own_certificate_is_checked_too(self) -> 'None':

        own_cert_chain = make_certificate_pem(_expiring_days_left)

        now = utcnow()
        findings = collect_findings([], now, own_cert_chain=own_cert_chain, server_name=Server_Name)
        findings = findings_of_kind(findings, Kind_Cert_Expiry)

        assert len(findings) == 1

        finding = findings[0]

        assert finding.partner == Own_Keystore_Name
        assert 'own' in finding.message

# ################################################################################################################################

    def test_an_opted_out_partner_raises_nothing(self) -> 'None':

        certificate_pem = make_certificate_pem(_expiring_days_left)
        config = new_config(as2_partner_cert=certificate_pem, alerting_opt_out=True)

        now = utcnow()
        findings = collect_findings([config], now, server_name=Server_Name)
        findings = findings_of_kind(findings, Kind_Cert_Expiry)

        assert findings == []

# ################################################################################################################################

    def test_days_left_of_an_empty_chain_is_none(self) -> 'None':

        now = utcnow()

        assert get_cert_days_left('', now) is None
        assert get_cert_days_left('not-a-pem', now) is None

# ################################################################################################################################
# ################################################################################################################################
