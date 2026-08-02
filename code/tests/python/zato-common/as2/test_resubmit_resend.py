# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import timedelta

# pytest
import pytest

# Zato
from .resubmit_helpers import cleanup_env, get_events, get_last_event_id, SendRecorder, use_tmp_audit_db
from zato.common.as2.common import AS2Exception
from zato.common.as2.reconcile import MDNReconciler
from zato.common.as2.resubmit import load_event, resend
from zato.common.audit_log.api import AuditEvent
from zato.common.json_internal import loads
from zato.common.util.api import utcnow
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class TestResend:

    def test_resend_delivers_the_stored_payload_again(self, tmp_path:'os.PathLike') -> 'None':
        try:
            use_tmp_audit_db(tmp_path)
            reconciler = MDNReconciler('test-server')

            options = {
                'cid': 'cid-original',
                'payload': 'ISA*00*Test payload of an 850 order',
                'filename': 'orders-850.edi',
                }
            reconciler.record_message_sent('ZatoRetail', 'PartnerCorp', '<orders-850@zato>', **cast_('any_', options))

            event_id = get_last_event_id()
            event = load_event(event_id)

            send = SendRecorder()
            result = resend(event, send, reconciler, 'cid-resend')

            # The stored payload went back through the connection, with its filename ..
            assert send.payload == b'ISA*00*Test payload of an 850 order'
            assert send.filename == 'orders-850.edi'
            assert result.message_id == '<resent-message@zato>'

            # .. the new attempt is its own event, linked to the original by its CID ..
            events = get_events(AuditEvent.Message_Sent)
            event_count = len(events)
            assert event_count == 2

            resent = events[1]
            assert resent['cid'] == 'cid-resend'
            assert resent['correl_id'] == 'cid-original'
            assert resent['object_name'] == 'ZatoRetail:PartnerCorp'
            assert resent['msg_id'] == 'resent-message@zato'

            # .. and it carries the payload too, so it can be resent once again.
            details = loads(resent['data'])
            assert details['payload'] == 'ISA*00*Test payload of an 850 order'
            assert details['filename'] == 'orders-850.edi'
            assert details['mic'] == 'UmVzZW50TUlDVmFsdWU=, sha-256'

        finally:
            cleanup_env()

# ################################################################################################################################

    def test_resend_is_a_fresh_open_item(self, tmp_path:'os.PathLike') -> 'None':
        try:
            use_tmp_audit_db(tmp_path)
            reconciler = MDNReconciler('test-server')

            options = {
                'cid': 'cid-original',
                'payload': 'ISA*00*Test payload of an 850 order',
                }
            reconciler.record_message_sent('ZatoRetail', 'PartnerCorp', '<orders-850@zato>', **cast_('any_', options))

            # The original message reconciles once its MDN arrives ..
            reconciler.record_mdn_received('<orders-850@zato>')

            event = load_event(1)
            send = SendRecorder()
            _ = resend(event, send, reconciler, 'cid-resend')

            # .. while the resent one waits for an MDN of its own.
            cutoff = utcnow() + timedelta(seconds=1)
            outstanding = reconciler.outstanding(cutoff)

            outstanding_count = len(outstanding)
            first_outstanding = outstanding[0]

            assert outstanding_count == 1
            assert first_outstanding.message_id == 'resent-message@zato'

        finally:
            cleanup_env()

# ################################################################################################################################

    def test_resend_rejects_other_event_types(self, tmp_path:'os.PathLike') -> 'None':
        try:
            use_tmp_audit_db(tmp_path)
            reconciler = MDNReconciler('test-server')

            reconciler.record_message_sent('ZatoRetail', 'PartnerCorp', '<orders-850@zato>', payload='Test payload')

            # The MDN arrival is an event too, only not a resendable one.
            reconciler.record_mdn_received('<orders-850@zato>', data='{"disposition": "processed"}')

            event_id = get_last_event_id()
            event = load_event(event_id)

            send = SendRecorder()

            with pytest.raises(AS2Exception, match='can be resent'):
                _ = resend(event, send, reconciler, 'cid-resend')

        finally:
            cleanup_env()

# ################################################################################################################################

    def test_resend_rejects_an_event_without_a_payload(self, tmp_path:'os.PathLike') -> 'None':
        try:
            use_tmp_audit_db(tmp_path)
            reconciler = MDNReconciler('test-server')

            # A reconciliation-only entry, recorded without the payload.
            reconciler.record_message_sent('ZatoRetail', 'PartnerCorp', '<orders-850@zato>')

            event = load_event(1)
            send = SendRecorder()

            with pytest.raises(AS2Exception, match='does not carry a payload'):
                _ = resend(event, send, reconciler, 'cid-resend')

        finally:
            cleanup_env()

# ################################################################################################################################
# ################################################################################################################################
