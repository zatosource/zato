# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone

# cryptography
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509 import CertificateBuilder, Name, NameAttribute, random_serial_number
from cryptography.x509.oid import NameOID

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.as2.alerting import build_digest, collect_findings, get_cert_days_left, record_alerts, \
    Kind_Ack_Overdue, Kind_Cert_Expiry, Kind_MDN_Overdue, Kind_Ship_Notice_Missing, Own_Keystore_Name
from zato.common.api import AS2
from zato.common.as2.reconcile import MDNReconciler
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditSource, event_table, get_audit_engine
from zato.common.ext.bunch import Bunch
from zato.common.json_internal import loads
from zato.common.util.api import utcnow
from zato.edi.reconcile import Reconciler

# ################################################################################################################################
# ################################################################################################################################

# The reconciliation store all the tests write to and the sweep reads from.
_server_name = 'test-server'

# The identities of both sides
_as2_from = 'ZatoRetail'
_as2_to   = 'PartnerCorp'
_pair     = f'{_as2_from}:{_as2_to}'

# The X12 identifiers of both sides
_our_isa_id     = 'ZATORETAIL'
_partner_isa_id = 'PARTNERCORP'
_x12_pair       = f'{_our_isa_id}:{_partner_isa_id}'

# RSA parameters for throwaway test keys.
_rsa_public_exponent = 65537
_rsa_key_size = 2048

# ################################################################################################################################
# ################################################################################################################################

def _new_config(**overrides):
    """ One partner's connection configuration, the way the alerting sweep sees it.
    """
    out = Bunch()

    out['name'] = 'PartnerCorp AS2'
    out['as2_from'] = _as2_from
    out['as2_to'] = _as2_to
    out['isa_id'] = _partner_isa_id
    out['ack_overdue_after'] = 0
    out['alerting_opt_out'] = False
    out['ship_notice_window_hours'] = 0
    out['as2_partner_cert'] = ''

    out.update(overrides)

    return out

# ################################################################################################################################

def _make_certificate_pem(days_left):
    """ Issues one self-signed certificate expiring in the given number of days,
    returned as a PEM string the way the partner form stores it.
    """
    key = generate_private_key(_rsa_public_exponent, _rsa_key_size)
    name = Name([NameAttribute(NameOID.COMMON_NAME, 'alerting-test')])
    now = datetime.now(timezone.utc)

    builder = CertificateBuilder()
    builder = builder.subject_name(name)
    builder = builder.issuer_name(name)
    builder = builder.public_key(key.public_key())
    builder = builder.serial_number(random_serial_number())
    builder = builder.not_valid_before(now - timedelta(days=1))
    builder = builder.not_valid_after(now + timedelta(days=days_left))

    certificate = builder.sign(key, SHA256())

    out = certificate.public_bytes(Encoding.PEM).decode('ascii')
    return out

# ################################################################################################################################

def _findings_of_kind(findings, kind):
    """ Filters one sweep's findings down to a single kind - a test seeding
    the store for one check must not trip over the others.
    """
    out = []

    for finding in findings:
        if finding.kind == kind:
            out.append(finding)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestOverdueMDNs:

    def test_an_overdue_mdn_raises_a_finding(self):

        reconciler = MDNReconciler(_server_name)
        reconciler.record_message_sent(_as2_from, _as2_to, 'msg-1@zato', mic='abc, sha-256')

        config = _new_config(ack_overdue_after=3600)

        # The sweep runs after the partner's window has passed.
        now = utcnow() + timedelta(seconds=3700)
        findings = _findings_of_kind(collect_findings([config], now, server_name=_server_name), Kind_MDN_Overdue)

        assert len(findings) == 1

        finding = findings[0]

        assert finding.source == AuditSource.AS2
        assert finding.partner == _pair
        assert 'msg-1@zato' in finding.message
        assert 'source=as2' in finding.link
        assert 'status=outstanding' in finding.link

    def test_a_pending_mdn_inside_the_window_raises_nothing(self):

        reconciler = MDNReconciler(_server_name)
        reconciler.record_message_sent(_as2_from, _as2_to, 'msg-1@zato', mic='abc, sha-256')

        config = _new_config(ack_overdue_after=3600)

        # The sweep runs right after the send, well inside the window.
        now = utcnow()
        findings = _findings_of_kind(collect_findings([config], now, server_name=_server_name), Kind_MDN_Overdue)

        assert findings == []

    def test_the_default_window_applies_without_a_matching_partner(self):

        # The pair maps to no configured partner, so the default window decides.
        reconciler = MDNReconciler(_server_name)
        reconciler.record_message_sent('SomeoneElse', 'Unconfigured', 'msg-1@zato', mic='abc, sha-256')

        default_window = AS2.Alerting.Default_Ack_Overdue_Seconds

        # Inside the default window nothing is raised ..
        now = utcnow() + timedelta(seconds=default_window - 100)
        findings = _findings_of_kind(collect_findings([], now, server_name=_server_name), Kind_MDN_Overdue)

        assert findings == []

        # .. and past it the finding appears.
        now = utcnow() + timedelta(seconds=default_window + 100)
        findings = _findings_of_kind(collect_findings([], now, server_name=_server_name), Kind_MDN_Overdue)

        assert len(findings) == 1

    def test_an_opted_out_partner_raises_nothing(self):

        reconciler = MDNReconciler(_server_name)
        reconciler.record_message_sent(_as2_from, _as2_to, 'msg-1@zato', mic='abc, sha-256')

        config = _new_config(ack_overdue_after=3600, alerting_opt_out=True)

        now = utcnow() + timedelta(seconds=3700)
        findings = _findings_of_kind(collect_findings([config], now, server_name=_server_name), Kind_MDN_Overdue)

        assert findings == []

# ################################################################################################################################
# ################################################################################################################################

class TestOverdueAcks:

    def test_an_overdue_acknowledgment_raises_a_finding(self):

        reconciler = Reconciler(_server_name)
        reconciler.record_interchange_sent(_our_isa_id, _partner_isa_id, '000000001')

        # The partner maps back through its EDI identifier.
        config = _new_config(ack_overdue_after=3600)

        now = utcnow() + timedelta(seconds=3700)
        findings = _findings_of_kind(collect_findings([config], now, server_name=_server_name), Kind_Ack_Overdue)

        assert len(findings) == 1

        finding = findings[0]

        assert finding.source == AuditSource.X12
        assert finding.partner == _x12_pair
        assert '1' in finding.message
        assert 'source=x12' in finding.link
        assert 'status=outstanding' in finding.link

    def test_an_acknowledged_interchange_raises_nothing(self):

        reconciler = Reconciler(_server_name)
        reconciler.record_interchange_sent(_our_isa_id, _partner_isa_id, '000000001')
        reconciler.record_ack_received(_our_isa_id, _partner_isa_id, '000000001')

        config = _new_config(ack_overdue_after=3600)

        now = utcnow() + timedelta(seconds=3700)
        findings = _findings_of_kind(collect_findings([config], now, server_name=_server_name), Kind_Ack_Overdue)

        assert findings == []

    def test_an_opted_out_partner_raises_nothing(self):

        reconciler = Reconciler(_server_name)
        reconciler.record_interchange_sent(_our_isa_id, _partner_isa_id, '000000001')

        config = _new_config(ack_overdue_after=3600, alerting_opt_out=True)

        now = utcnow() + timedelta(seconds=3700)
        findings = _findings_of_kind(collect_findings([config], now, server_name=_server_name), Kind_Ack_Overdue)

        assert findings == []

# ################################################################################################################################
# ################################################################################################################################

class TestExpiringCertificates:

    def test_a_partner_certificate_inside_the_window_raises_a_finding(self):

        config = _new_config(as2_partner_cert=_make_certificate_pem(10))

        now = utcnow()
        findings = _findings_of_kind(collect_findings([config], now, server_name=_server_name), Kind_Cert_Expiry)

        assert len(findings) == 1

        finding = findings[0]

        assert finding.source == AuditSource.AS2
        assert finding.partner == _pair
        assert 'PartnerCorp AS2' in finding.message
        assert 'expires in' in finding.message

    def test_a_healthy_partner_certificate_raises_nothing(self):

        config = _new_config(as2_partner_cert=_make_certificate_pem(365))

        now = utcnow()
        findings = _findings_of_kind(collect_findings([config], now, server_name=_server_name), Kind_Cert_Expiry)

        assert findings == []

    def test_our_own_certificate_is_checked_too(self):

        own_cert_chain = _make_certificate_pem(10)

        now = utcnow()
        findings = collect_findings([], now, own_cert_chain=own_cert_chain, server_name=_server_name)
        findings = _findings_of_kind(findings, Kind_Cert_Expiry)

        assert len(findings) == 1

        finding = findings[0]

        assert finding.partner == Own_Keystore_Name
        assert 'own' in finding.message

    def test_an_opted_out_partner_raises_nothing(self):

        config = _new_config(as2_partner_cert=_make_certificate_pem(10), alerting_opt_out=True)

        now = utcnow()
        findings = _findings_of_kind(collect_findings([config], now, server_name=_server_name), Kind_Cert_Expiry)

        assert findings == []

    def test_days_left_of_an_empty_chain_is_none(self):

        now = utcnow()

        assert get_cert_days_left('', now) is None
        assert get_cert_days_left('not-a-pem', now) is None

# ################################################################################################################################
# ################################################################################################################################

class TestShipNoticeGuard:

    def test_an_unanswered_order_past_the_window_raises_a_finding(self):

        reconciler = Reconciler(_server_name)

        # An 850 arrived from the partner and nothing went back.
        reconciler.record_interchange_received(_partner_isa_id, _our_isa_id, '000000042', doc_type='850')

        config = _new_config(ship_notice_window_hours=4)

        now = utcnow() + timedelta(hours=5)
        findings = collect_findings([config], now, server_name=_server_name)
        findings = _findings_of_kind(findings, Kind_Ship_Notice_Missing)

        assert len(findings) == 1

        finding = findings[0]

        assert finding.source == AuditSource.X12
        assert finding.partner == f'{_partner_isa_id}:{_our_isa_id}'
        assert '42' in finding.message
        assert 'ship notice' in finding.message
        assert 'source=x12' in finding.link

    def test_a_ship_notice_sent_back_answers_the_order(self):

        reconciler = Reconciler(_server_name)

        reconciler.record_interchange_received(_partner_isa_id, _our_isa_id, '000000042', doc_type='850')
        reconciler.record_interchange_sent(_our_isa_id, _partner_isa_id, '000000043', doc_type='856')

        config = _new_config(ship_notice_window_hours=4)

        now = utcnow() + timedelta(hours=5)
        findings = collect_findings([config], now, server_name=_server_name)
        findings = _findings_of_kind(findings, Kind_Ship_Notice_Missing)

        assert findings == []

    def test_an_order_inside_the_window_raises_nothing(self):

        reconciler = Reconciler(_server_name)
        reconciler.record_interchange_received(_partner_isa_id, _our_isa_id, '000000042', doc_type='850')

        config = _new_config(ship_notice_window_hours=4)

        now = utcnow()
        findings = collect_findings([config], now, server_name=_server_name)
        findings = _findings_of_kind(findings, Kind_Ship_Notice_Missing)

        assert findings == []

    def test_a_partner_without_a_window_is_not_guarded(self):

        reconciler = Reconciler(_server_name)
        reconciler.record_interchange_received(_partner_isa_id, _our_isa_id, '000000042', doc_type='850')

        config = _new_config()

        now = utcnow() + timedelta(hours=5)
        findings = collect_findings([config], now, server_name=_server_name)
        findings = _findings_of_kind(findings, Kind_Ship_Notice_Missing)

        assert findings == []

# ################################################################################################################################
# ################################################################################################################################

class TestDigestAndEvents:

    def _collect_one_sweep(self):
        """ Seeds the store with one overdue MDN and runs the sweep past the window.
        """
        reconciler = MDNReconciler(_server_name)
        reconciler.record_message_sent(_as2_from, _as2_to, 'msg-1@zato', mic='abc, sha-256')

        config = _new_config(ack_overdue_after=3600)

        now = utcnow() + timedelta(seconds=3700)

        out = collect_findings([config], now, server_name=_server_name)
        return out

    def test_the_digest_has_one_line_per_finding(self):

        findings = self._collect_one_sweep()

        subject, body = build_digest(findings, 'https://dashboard.example.com')

        assert subject == 'Zato B2B alert digest - 1 finding'
        assert 'msg-1@zato' in body

        # Each line links to the filtered audit log page under the given Dashboard address.
        assert f'https://dashboard.example.com/zato/audit-log/?source=as2&object_name={_pair}' in body

    def test_each_finding_becomes_an_alert_raised_event(self):

        findings = self._collect_one_sweep()

        audit_log = AuditLog(_server_name)
        record_alerts(audit_log, findings, cid='cid-alerting')

        # The alerting history is filed under the partner the finding is about.
        stmt = select(
            event_table.c.source,
            event_table.c.object_name,
            event_table.c.cid,
            event_table.c.data,
        ).where(event_table.c.event_type == AuditEvent.Alert_Raised)

        engine = get_audit_engine()

        with engine.connect() as connection:
            rows = connection.execute(stmt).fetchall()

        assert len(rows) == 1

        source, object_name, cid, data = rows[0]

        assert source == AuditSource.AS2
        assert object_name == _pair
        assert cid == 'cid-alerting'

        details = loads(data)

        assert details['kind'] == Kind_MDN_Overdue
        assert 'msg-1@zato' in details['message']

# ################################################################################################################################
# ################################################################################################################################
