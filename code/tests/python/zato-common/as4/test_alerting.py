# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# Zato
from zato.common.as2.alerting import Kind_Cert_Expiry, Kind_Receipt_Missing
from zato.common.as4.alerting import collect_findings
from zato.common.audit_log.api import AuditSource
from zato.common.ext.bunch import Bunch
from zato.common.util.api import utcnow

from .conftest import make_certificate_pem
from .test_audit import audit_db
from .test_resend import _record_send, _single_document, _From_Party, _Missing_Receipt_After, _Server_Name, _To_Party

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

def _findings_of_kind(findings:'anylist', kind:'str') -> 'anylist':
    """ Filters one sweep's findings down to a single kind - a test seeding the store for one check
    must not trip over the others.
    """

    # Our response to produce
    out:'anylist' = []

    for finding in findings:
        if finding.kind == kind:
            out.append(finding)

    return out

# The fixture is imported for its side effect of pointing the audit log at a database of its own.
audit_db = audit_db

# ################################################################################################################################
# ################################################################################################################################

# The party pair every finding of these tests is filed under.
_Pair = f'{_From_Party}:{_To_Party}'

# How many days are left on a certificate the sweep is expected to warn about
# and on one it is expected to stay quiet about.
_Expiring_Days_Left = 10
_Healthy_Days_Left = 365

# ################################################################################################################################
# ################################################################################################################################

def _new_outgoing_config(**overrides:'any_') -> 'any_':
    """ One outgoing AS4 connection, the way the sweep sees it.
    """
    out = Bunch()

    out['name'] = 'Partner AS4'
    out['as4_from_party'] = _From_Party
    out['as4_to_party'] = _To_Party
    out['as4_retry_max_attempts'] = 3
    out['as4_retry_interval'] = 900
    out['as4_missing_receipt_after'] = _Missing_Receipt_After

    out.update(overrides)

    return out

# ################################################################################################################################

def _new_channel_config(**overrides:'any_') -> 'any_':
    """ One AS4 channel, the way the sweep sees it.
    """
    out = Bunch()

    out['name'] = 'Partner AS4 channel'
    out['as4_from_party'] = _From_Party
    out['as4_to_party'] = _To_Party

    out.update(overrides)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestExpiringCertificates:
    """ Which certificates of an AS4 exchange the sweep warns about, on both sides of it.
    """

    def test_an_expiring_certificate_of_a_connection_raises_a_finding(self) -> 'None':

        certificate_pem = make_certificate_pem(_Expiring_Days_Left)
        config = _new_outgoing_config(as4_signing_cert_chain=certificate_pem)

        findings = collect_findings([config], [], utcnow(), _Server_Name)
        findings = _findings_of_kind(findings, Kind_Cert_Expiry)

        assert len(findings) == 1

        finding = findings[0]

        assert finding.source == AuditSource.AS4
        assert finding.partner == _Pair
        assert 'Partner AS4' in finding.message
        assert 'expires in' in finding.message

# ################################################################################################################################

    def test_a_healthy_certificate_raises_nothing(self) -> 'None':

        certificate_pem = make_certificate_pem(_Healthy_Days_Left)
        config = _new_outgoing_config(as4_signing_cert_chain=certificate_pem)

        findings = collect_findings([config], [], utcnow(), _Server_Name)
        findings = _findings_of_kind(findings, Kind_Cert_Expiry)

        assert findings == []

# ################################################################################################################################

    def test_every_certificate_of_a_connection_is_watched(self) -> 'None':

        certificate_pem = make_certificate_pem(_Expiring_Days_Left)

        config = _new_outgoing_config(
            as4_signing_cert_chain=certificate_pem,
            as4_peer_signing_cert=certificate_pem,
            as4_peer_encryption_cert=certificate_pem,
        )

        findings = collect_findings([config], [], utcnow(), _Server_Name)
        findings = _findings_of_kind(findings, Kind_Cert_Expiry)

        assert len(findings) == 3

# ################################################################################################################################

    def test_the_receiving_side_is_watched_too(self) -> 'None':

        certificate_pem = make_certificate_pem(_Expiring_Days_Left)
        config = _new_channel_config(as4_signing_cert_chain=certificate_pem)

        findings = collect_findings([], [config], utcnow(), _Server_Name)
        findings = _findings_of_kind(findings, Kind_Cert_Expiry)

        assert len(findings) == 1
        assert 'Partner AS4 channel' in findings[0].message

# ################################################################################################################################

    def test_an_item_saved_without_certificates_raises_nothing(self) -> 'None':

        findings = collect_findings([_new_outgoing_config()], [_new_channel_config()], utcnow(), _Server_Name)
        findings = _findings_of_kind(findings, Kind_Cert_Expiry)

        assert findings == []

# ################################################################################################################################
# ################################################################################################################################

class TestMissingReceipts:
    """ Which unanswered exchanges the sweep reports.
    """

    def test_an_exchange_past_its_window_raises_a_finding(self, audit_db:'None') -> 'None':

        _record_send('msg-1', _single_document())

        past_the_window = utcnow() + timedelta(seconds=_Missing_Receipt_After + 100)
        findings = collect_findings([_new_outgoing_config()], [], past_the_window, _Server_Name)
        findings = _findings_of_kind(findings, Kind_Receipt_Missing)

        assert len(findings) == 1

        finding = findings[0]

        assert finding.source == AuditSource.AS4
        assert finding.partner == _Pair
        assert 'msg-1' in finding.message

# ################################################################################################################################

    def test_an_exchange_inside_its_window_raises_nothing(self, audit_db:'None') -> 'None':

        _record_send('msg-1', _single_document())

        findings = collect_findings([_new_outgoing_config()], [], utcnow(), _Server_Name)
        findings = _findings_of_kind(findings, Kind_Receipt_Missing)

        assert findings == []

# ################################################################################################################################
# ################################################################################################################################
