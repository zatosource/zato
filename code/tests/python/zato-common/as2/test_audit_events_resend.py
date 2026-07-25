# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import select

# Zato
from .audit_helpers import load_events, Payload
from .audit_outconn_helpers import make_connection
from zato.common.as2.audit import decode_raw_mime
from zato.common.as2.reconcile import MDNReconciler
from zato.common.as2.resubmit import load_event, resend
from zato.common.audit_log.api import AuditEvent, event_table, get_audit_engine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

class TestResendEvidence:

    def test_resend_records_one_linked_attempt_without_duplicates(self, parties:'TestParties') -> 'None':

        connection = make_connection(parties)

        # The original delivery records itself ..
        original = connection.send('cid-original', Payload)
        assert original.is_ok

        sent_events = load_events(AuditEvent.Message_Sent)
        assert len(sent_events) == 1

        # .. the stored event is what the operator resend runs on ..
        engine = get_audit_engine()

        with engine.connect() as db_connection:
            statement = select(event_table.c.id).where(event_table.c.event_type == AuditEvent.Message_Sent)
            db_result = db_connection.execute(statement)
            event_id = db_result.scalar()

        event = load_event(event_id)

        # .. the resend turns the connection's own recording off, the way the resend service does.
        def send(payload:'any_', filename:'any_') -> 'any_':
            out = connection.send('cid-resend', payload, filename, needs_audit=False)
            return out

        reconciler = MDNReconciler('test-server')
        result = resend(event, send, reconciler, 'cid-resend')

        assert result.is_ok

        # Exactly one new message-sent event exists, linked to the original by its CID ..
        sent_events = load_events(AuditEvent.Message_Sent)
        assert len(sent_events) == 2

        resend_event = sent_events[1]
        assert resend_event.cid == 'cid-resend'
        assert resend_event.correl_id == 'cid-original'

        # .. with the raw MIME of the new attempt stored as evidence ..
        raw_mime = decode_raw_mime(resend_event.details['raw_mime'])
        assert raw_mime == result.request_body

        # .. and both exchanges closed by their synchronous MDNs.
        mdn_events = load_events(AuditEvent.MDN_Received)
        assert len(mdn_events) == 2

# ################################################################################################################################
# ################################################################################################################################
