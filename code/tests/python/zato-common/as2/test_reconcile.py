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
from zato.common.as2.mdn import build_mdn, MDNRequest, new_error_disposition, new_processed_disposition
from zato.common.as2.reconcile import MDNReconciler, process_incoming_mdn
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

def _make_reconciler(tmp_path:'os.PathLike') -> 'MDNReconciler':
    """ Points the audit database at a per-test SQLite file and builds a reconciler on it.
    """
    db_path = os.path.join(str(tmp_path), 'audit.db')

    os.environ[AuditLogCtx.Env_Type] = AuditLogCtx.Type_SQLite
    os.environ[AuditLogCtx.Env_Name] = db_path

    out = MDNReconciler('test-server')
    return out

# ################################################################################################################################

def _cleanup_env() -> 'None':
    _ = os.environ.pop(AuditLogCtx.Env_Type, None)
    _ = os.environ.pop(AuditLogCtx.Env_Name, None)

# ################################################################################################################################

def _build_mdn_bytes(message_id, disposition=None, mic=''):
    """ Builds one real MDN answering the given Message-ID, returning its body and content type.
    """
    request = MDNRequest()
    request.message_id = message_id
    request.as2_from = 'ZatoRetail'
    request.as2_to = 'PartnerCorp'

    if disposition is None:
        disposition = new_processed_disposition()

    body, headers = build_mdn(request, disposition, mic)

    out = body, headers['Content-Type']
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestMatching:

    def test_sent_message_matches_until_its_mdn_arrives(self, tmp_path):
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

    def test_unknown_message_id_matches_nothing(self, tmp_path):
        try:
            reconciler = _make_reconciler(tmp_path)

            assert reconciler.match('never-sent@zato') is None

        finally:
            _cleanup_env()

# ################################################################################################################################
# ################################################################################################################################

class TestOutstanding:

    def test_outstanding_shrinks_as_mdns_arrive(self, tmp_path):
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

    def test_recent_messages_are_not_overdue(self, tmp_path):
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

    def test_matched_mdn_reconciles_ok(self, tmp_path):
        try:
            reconciler = _make_reconciler(tmp_path)
            reconciler.record_message_sent('ZatoRetail', 'PartnerCorp', '<abc@zato>')

            body, content_type = _build_mdn_bytes('<abc@zato>')
            result = process_incoming_mdn(body, content_type, reconciler)

            assert result.is_parsed
            assert result.is_matched
            assert result.is_ok
            assert result.pending.as2_from == 'ZatoRetail'
            assert result.pending.as2_to == 'PartnerCorp'

            # The message is reconciled now, so it no longer matches.
            assert reconciler.match('abc@zato') is None

        finally:
            _cleanup_env()

    def test_mic_must_match_what_was_computed_at_send_time(self, tmp_path):
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

    def test_error_disposition_is_not_ok(self, tmp_path):
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

    def test_unknown_message_id_is_accepted_and_logged(self, tmp_path):
        try:
            reconciler = _make_reconciler(tmp_path)

            body, content_type = _build_mdn_bytes('<never-sent@partnercorp>')
            result = process_incoming_mdn(body, content_type, reconciler)

            assert result.is_parsed
            assert not result.is_matched
            assert not result.is_ok

        finally:
            _cleanup_env()

    def test_already_reconciled_message_id_is_accepted_and_logged(self, tmp_path):
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

    def test_garbage_body_is_accepted_and_logged(self, tmp_path):
        try:
            reconciler = _make_reconciler(tmp_path)

            result = process_incoming_mdn(b'This is not an MDN', 'text/plain', reconciler)

            assert not result.is_parsed
            assert not result.is_matched
            assert not result.is_ok

        finally:
            _cleanup_env()

# ################################################################################################################################
# ################################################################################################################################
