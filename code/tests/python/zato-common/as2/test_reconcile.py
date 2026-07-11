# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import timedelta

# Zato
from zato.common.as2.common import AS2Error
from zato.common.as2.mdn import build_mdn, MDNRequest, MDNSigningConfig, new_error_disposition, new_processed_disposition
from zato.common.as2.reconcile import MDNReconciler, process_incoming_mdn
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

def _make_reconciler(tmp_path:'os.PathLike') -> 'MDNReconciler':
    """ Points the audit database at a per-test SQLite file and builds a reconciler on it.
    """
    database_path = os.path.join(str(tmp_path), 'audit.db')

    os.environ[AuditLogCtx.Env_Type] = AuditLogCtx.Type_SQLite
    os.environ[AuditLogCtx.Env_Name] = database_path

    out = MDNReconciler('test-server')
    return out

# ################################################################################################################################

def _cleanup_env() -> 'None':
    del os.environ[AuditLogCtx.Env_Type]
    del os.environ[AuditLogCtx.Env_Name]

# ################################################################################################################################

def _build_mdn_bytes(message_id:'any_', disposition:'any_'=None, mic:'any_'='', signing_keystore:'any_'=None) -> 'any_':
    """ Builds one real MDN answering the given Message-ID, returning its body and content type.
    """
    request = MDNRequest()
    request.message_id = message_id
    request.as2_from = 'ZatoRetail'
    request.as2_to = 'PartnerCorp'

    # A signing keystore means the MDN comes out signed, the way a partner
    # honoring a signed receipt request would produce it.
    if signing_keystore:
        request.requests_signed_mdn = True
        request.signed_receipt_protocol = 'pkcs7-signature'
        request.mic_algorithms = ['sha-256']

        signing_config = MDNSigningConfig()
        signing_config.keystore = signing_keystore
    else:
        signing_config = None

    if disposition is None:
        disposition = new_processed_disposition()

    body, headers = build_mdn(request, disposition, mic, signing_config)

    out = body, headers['Content-Type']
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestMatching:

    def test_sent_message_matches_until_its_mdn_arrives(self, tmp_path:'os.PathLike') -> 'None':
        try:
            reconciler = _make_reconciler(tmp_path)

            reconciler.record_message_sent(
                'ZatoRetail', 'PartnerCorp', '<abc@zato>',
                mic='QUFB, sha-256',
                async_mdn_url='https://zatoretail.example.com/zato/as2/mdn',
                cid='cid-1',
            )

            # Everything recorded at send time comes back - the angle brackets are normalized away.
            pending = reconciler.match('abc@zato')

            assert pending is not None
            assert pending.as2_from == 'ZatoRetail'
            assert pending.as2_to == 'PartnerCorp'
            assert pending.message_id == 'abc@zato'
            assert pending.mic == 'QUFB, sha-256'
            assert pending.async_mdn_url == 'https://zatoretail.example.com/zato/as2/mdn'
            assert pending.cid == 'cid-1'
            assert pending.sent_time_iso

            # Once the MDN arrives, the same Message-ID no longer matches.
            reconciler.record_mdn_received('abc@zato')

            assert reconciler.match('abc@zato') is None

        finally:
            _cleanup_env()

# ################################################################################################################################

    def test_unknown_message_id_matches_nothing(self, tmp_path:'os.PathLike') -> 'None':
        try:
            reconciler = _make_reconciler(tmp_path)

            assert reconciler.match('never-sent@zato') is None

        finally:
            _cleanup_env()

# ################################################################################################################################
# ################################################################################################################################

class TestOutstanding:

    def test_outstanding_shrinks_as_mdns_arrive(self, tmp_path:'os.PathLike') -> 'None':
        try:
            reconciler = _make_reconciler(tmp_path)

            reconciler.record_message_sent('ZatoRetail', 'PartnerCorp', '<abc@zato>', cid='cid-abc')
            reconciler.record_message_sent('ZatoRetail', 'PartnerCorp', '<def@zato>', cid='cid-def')

            cutoff = utcnow() + timedelta(seconds=1)

            outstanding = reconciler.outstanding(cutoff)
            assert len(outstanding) == 2
            assert outstanding[0].message_id == 'abc@zato'
            assert outstanding[1].message_id == 'def@zato'

            reconciler.record_mdn_received('<abc@zato>')

            outstanding = reconciler.outstanding(cutoff)
            assert len(outstanding) == 1
            assert outstanding[0].message_id == 'def@zato'

            reconciler.record_mdn_received('def@zato')

            assert reconciler.outstanding(cutoff) == []

        finally:
            _cleanup_env()

# ################################################################################################################################

    def test_recent_messages_are_not_overdue(self, tmp_path:'os.PathLike') -> 'None':
        try:
            reconciler = _make_reconciler(tmp_path)

            reconciler.record_message_sent('ZatoRetail', 'PartnerCorp', '<abc@zato>')

            # A cutoff before the send time means nothing is overdue yet.
            cutoff = utcnow() - timedelta(hours=1)

            assert reconciler.outstanding(cutoff) == []

        finally:
            _cleanup_env()

# ################################################################################################################################
# ################################################################################################################################

class TestProcessIncomingMDN:

    def test_matched_mdn_reconciles_ok(self, tmp_path:'os.PathLike') -> 'None':
        try:
            reconciler = _make_reconciler(tmp_path)
            reconciler.record_message_sent('ZatoRetail', 'PartnerCorp', '<abc@zato>')

            body, content_type = _build_mdn_bytes('<abc@zato>')
            result = process_incoming_mdn(body, content_type, reconciler)

            assert result.is_parsed
            assert result.is_matched
            assert result.is_ok

            assert result.pending is not None
            assert result.pending.as2_from == 'ZatoRetail'
            assert result.pending.as2_to == 'PartnerCorp'

            # The message is reconciled now, so it no longer matches.
            assert reconciler.match('abc@zato') is None

        finally:
            _cleanup_env()

# ################################################################################################################################

    def test_mic_must_match_what_was_computed_at_send_time(self, tmp_path:'os.PathLike') -> 'None':
        try:
            reconciler = _make_reconciler(tmp_path)
            reconciler.record_message_sent('ZatoRetail', 'PartnerCorp', '<abc@zato>', mic='QUFB, sha-256')

            # The MDN claims a different MIC - the delivery is a failure, though still reconciled.
            body, content_type = _build_mdn_bytes('<abc@zato>', mic='REVG, sha-256')
            result = process_incoming_mdn(body, content_type, reconciler)

            assert result.is_parsed
            assert result.is_matched
            assert not result.is_ok

        finally:
            _cleanup_env()

# ################################################################################################################################

    def test_error_disposition_is_not_ok(self, tmp_path:'os.PathLike') -> 'None':
        try:
            reconciler = _make_reconciler(tmp_path)
            reconciler.record_message_sent('ZatoRetail', 'PartnerCorp', '<abc@zato>')

            disposition = new_error_disposition(AS2Error.Decryption_Failed)
            body, content_type = _build_mdn_bytes('<abc@zato>', disposition=disposition)

            result = process_incoming_mdn(body, content_type, reconciler)

            assert result.is_parsed
            assert result.is_matched
            assert not result.is_ok

        finally:
            _cleanup_env()

# ################################################################################################################################

    def test_unknown_message_id_is_accepted_and_logged(self, tmp_path:'os.PathLike') -> 'None':
        try:
            reconciler = _make_reconciler(tmp_path)

            body, content_type = _build_mdn_bytes('<never-sent@partnercorp>')
            result = process_incoming_mdn(body, content_type, reconciler)

            assert result.is_parsed
            assert not result.is_matched
            assert not result.is_ok

        finally:
            _cleanup_env()

# ################################################################################################################################

    def test_already_reconciled_message_id_is_accepted_and_logged(self, tmp_path:'os.PathLike') -> 'None':
        try:
            reconciler = _make_reconciler(tmp_path)
            reconciler.record_message_sent('ZatoRetail', 'PartnerCorp', '<abc@zato>')

            body, content_type = _build_mdn_bytes('<abc@zato>')

            first = process_incoming_mdn(body, content_type, reconciler)
            second = process_incoming_mdn(body, content_type, reconciler)

            assert first.is_matched
            assert second.is_parsed
            assert not second.is_matched

        finally:
            _cleanup_env()

# ################################################################################################################################

    def test_garbage_body_is_accepted_and_logged(self, tmp_path:'os.PathLike') -> 'None':
        try:
            reconciler = _make_reconciler(tmp_path)

            result = process_incoming_mdn(b'This is not an MDN', 'text/plain', reconciler)

            assert not result.is_parsed
            assert not result.is_matched
            assert not result.is_ok

        finally:
            _cleanup_env()

# ################################################################################################################################

    def test_accepted_certificates_admit_a_rotated_signer(self, tmp_path:'os.PathLike', parties:'TestParties', make_rotated_pair:'any_') -> 'None':
        try:
            reconciler = _make_reconciler(tmp_path)
            reconciler.record_message_sent('ZatoRetail', 'PartnerCorp', '<abc@zato>')

            # The MDN is signed by the partner's current pair while the rotation list
            # already carries the next certificate too - the signer is on the list.
            body, content_type = _build_mdn_bytes('<abc@zato>', signing_keystore=parties.receiver)

            rotated = make_rotated_pair('as2-receiver-rotation')
            accepted = [rotated.certificate, parties.receiver.signing_certificate]

            result = process_incoming_mdn(body, content_type, reconciler, parties.sender, accepted_certificates=accepted)

            assert result.is_parsed
            assert result.is_matched
            assert result.is_ok

        finally:
            _cleanup_env()

# ################################################################################################################################

    def test_accepted_certificates_reject_an_unlisted_signer(self, tmp_path:'os.PathLike', parties:'TestParties', make_rotated_pair:'any_') -> 'None':
        try:
            reconciler = _make_reconciler(tmp_path)
            reconciler.record_message_sent('ZatoRetail', 'PartnerCorp', '<abc@zato>')

            body, content_type = _build_mdn_bytes('<abc@zato>', signing_keystore=parties.receiver)

            # The rotation list does not include the actual signer, so the MDN
            # does not verify and counts as unparseable - accepted and logged.
            rotated = make_rotated_pair('as2-receiver-rotation')
            accepted = [rotated.certificate]

            result = process_incoming_mdn(body, content_type, reconciler, parties.sender, accepted_certificates=accepted)

            assert not result.is_parsed
            assert not result.is_matched
            assert not result.is_ok

        finally:
            _cleanup_env()

# ################################################################################################################################
# ################################################################################################################################
