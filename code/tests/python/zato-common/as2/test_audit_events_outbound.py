# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# Zato
from .audit_helpers import load_events, Payload, Receiver_Identifier, Sender_Identifier
from .audit_outconn_helpers import make_connection
from zato.common.as2.audit import decode_raw_mime
from zato.common.as2.mdn import normalize_message_id
from zato.common.as2.reconcile import MDNReconciler
from zato.common.audit_log.api import AuditEvent, AuditOutcome
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

class TestOutboundEvidence:

    def test_send_records_the_full_evidence_tuple(self, parties:'TestParties') -> 'None':

        connection = make_connection(parties)
        result = connection.send('cid-1', Payload, 'orders-850.edi')

        assert result.is_ok

        # The delivery landed as one message-sent event ..
        sent_events = load_events(AuditEvent.Message_Sent)
        assert len(sent_events) == 1

        event = sent_events[0]

        # .. filed under the identity pair with the normalized Message-ID ..
        assert event.object_name == f'{Sender_Identifier}:{Receiver_Identifier}'
        assert event.msg_id == normalize_message_id(result.message_id)
        assert event.cid == 'cid-1'

        # .. carrying the MIC computed at send time, algorithm included ..
        assert event.details['mic'] == result.mic
        assert 'sha-256' in event.details['mic']

        # .. the complete raw MIME body that went over the wire ..
        raw_mime = decode_raw_mime(event.details['raw_mime'])
        assert raw_mime == result.request_body

        # .. and the clear payload with its filename, for a later resend.
        assert event.details['payload'] == Payload.decode('utf8')
        assert event.details['filename'] == 'orders-850.edi'

# ################################################################################################################################

    def test_the_sync_mdn_is_recorded_and_closes_the_exchange(self, parties:'TestParties') -> 'None':

        connection = make_connection(parties)
        result = connection.send('cid-1', Payload)

        assert result.is_ok

        # The receipt landed as one mdn-received event ..
        mdn_events = load_events(AuditEvent.MDN_Received)
        assert len(mdn_events) == 1

        event = mdn_events[0]

        # .. reporting clean processing, with the raw MDN bytes as the evidence ..
        assert event.outcome == AuditOutcome.OK
        assert event.details['disposition'] == 'processed'

        raw_mime = decode_raw_mime(event.details['raw_mime'])
        assert raw_mime == result.response_body

        # .. and the exchange is closed for reconciliation.
        reconciler = MDNReconciler('test-server')
        cutoff = utcnow() + timedelta(seconds=1)

        assert reconciler.outstanding(cutoff) == []

# ################################################################################################################################

    def test_an_unconfirmed_delivery_records_an_error_mdn(self, parties:'TestParties') -> 'None':

        # The receiver does not know this sender, so its MDN reports an error disposition.
        connection = make_connection(parties, as2_from='UnknownSender')
        result = connection.send('cid-1', Payload)

        assert not result.is_ok

        mdn_events = load_events(AuditEvent.MDN_Received)
        assert len(mdn_events) == 1

        event = mdn_events[0]

        assert event.outcome == AuditOutcome.Error
        assert event.details['modifier_kind'] == 'error'

# ################################################################################################################################

    def test_needs_audit_off_records_nothing(self, parties:'TestParties') -> 'None':

        connection = make_connection(parties)
        result = connection.send('cid-1', Payload, needs_audit=False)

        assert result.is_ok
        assert load_events() == []

# ################################################################################################################################
# ################################################################################################################################
