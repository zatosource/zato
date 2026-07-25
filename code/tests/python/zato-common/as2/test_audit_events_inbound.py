# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from .audit_channel_helpers import build_wire_message, make_runtime
from .audit_helpers import load_events, Payload, Receiver_Identifier, Sender_Identifier
from zato.common.as2.audit import decode_raw_mime
from zato.common.as2.mdn import normalize_message_id
from zato.common.audit_log.api import AuditEvent, AuditOutcome

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

class TestInboundEvidence:

    def test_an_accepted_message_records_message_received_and_mdn_sent(self, parties:'TestParties') -> 'None':

        runtime = make_runtime(parties)

        body, headers, message_id, _ = build_wire_message(parties)
        result = runtime.handle('cid-1', body, headers)

        assert not result.is_error

        # The arrival landed as one message-received event ..
        received_events = load_events(AuditEvent.Message_Received)
        assert len(received_events) == 1

        event = received_events[0]

        # .. filed under the pair as it arrived on the wire ..
        assert event.object_name == f'{Sender_Identifier}:{Receiver_Identifier}'
        assert event.msg_id == normalize_message_id(message_id)
        assert event.outcome == AuditOutcome.OK

        # .. with the complete raw MIME body exactly as received ..
        raw_mime = decode_raw_mime(event.details['raw_mime'])
        assert raw_mime == body

        # .. the MIC computed over the received content ..
        assert event.details['mic'] == result.mic
        assert event.details['mic']

        # .. and the clear payload for a later reprocess.
        assert event.details['payload'] == Payload.decode('utf8')

        # The receipt that went back landed as one mdn-sent event, with its own raw bytes.
        mdn_events = load_events(AuditEvent.MDN_Sent)
        assert len(mdn_events) == 1

        mdn_event = mdn_events[0]

        assert mdn_event.details['disposition'] == 'processed'
        assert mdn_event.details['modifier_kind'] == ''

        mdn_raw_mime = decode_raw_mime(mdn_event.details['raw_mime'])
        assert mdn_raw_mime == result.body

# ################################################################################################################################

    def test_a_rejected_message_records_the_error_disposition(self, parties:'TestParties') -> 'None':

        # No partnership is configured, so the message is rejected.
        runtime = make_runtime(parties, with_partnership=False)

        body, headers, _, _ = build_wire_message(parties)
        result = runtime.handle('cid-1', body, headers)

        assert result.is_error

        # The arrival was still recorded, with the error modifier as its outcome detail ..
        received_events = load_events(AuditEvent.Message_Received)
        assert len(received_events) == 1

        event = received_events[0]

        assert event.outcome == AuditOutcome.Error
        assert event.details['error'] == 'unknown-trading-relationship'

        # .. and so was the explanatory MDN that went back.
        mdn_events = load_events(AuditEvent.MDN_Sent)
        assert len(mdn_events) == 1

        mdn_event = mdn_events[0]

        assert mdn_event.outcome == AuditOutcome.Error
        assert mdn_event.details['modifier_kind'] == 'error'
        assert mdn_event.details['modifier'] == 'unknown-trading-relationship'

# ################################################################################################################################

    def test_a_replay_records_no_new_events(self, parties:'TestParties') -> 'None':

        runtime = make_runtime(parties)

        body, headers, _, _ = build_wire_message(parties)

        first = runtime.handle('cid-1', body, headers)
        assert not first.is_duplicate

        # The replay reuses the same body and headers, Message-ID included.
        second = runtime.handle('cid-2', body, headers)
        assert second.is_duplicate

        # Only the first delivery left its pair of events behind.
        received_events = load_events(AuditEvent.Message_Received)
        assert len(received_events) == 1

        mdn_events = load_events(AuditEvent.MDN_Sent)
        assert len(mdn_events) == 1

# ################################################################################################################################
# ################################################################################################################################
