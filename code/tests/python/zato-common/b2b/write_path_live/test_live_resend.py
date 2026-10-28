# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The operator actions on a message of 2 MB, on each database - a resend sends the same bytes under the same MessageId,
# a reprocess sends the same payload under a new MessageId linked to the original, and a redelivery hands a received
# message to the application again.

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import AuditLink, AuditSource, event_link_table
from zato.common.b2b.common.commit_group import GroupCommitWriter
from zato.common.b2b.common.outcome import FinalState
from zato.common.b2b.common.send_log import SendLog
from zato.common.b2b.common.store import MessageStore
from zato.common.b2b.ebms2.inbound_common import pending_deliveries, redeliver
from zato.common.b2b.ebms2.outbound_record import new_sent_message
from zato.common.b2b.ebms2.reprocess import reprocess
from zato.common.test.b2b_cpa import new_settings
from zato.common.test.b2b_ebms2 import confirm, deliver, new_exchange, new_payload, send, Server_Name, Start_Time, use_store
from zato.common.test.b2b_write_path import receipt_outcome

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_db import LiveDB
    from zato.common.test.b2b_pki import TestParties
    LiveDB = LiveDB
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

# The size of the payload of each message.
_payload_size = 2 * 1024 * 1024

# How many deliveries one page of a recovery holds.
_page_size = 10

# ################################################################################################################################
# ################################################################################################################################

def _payload_data() -> 'bytes':
    pattern = 'Zamówienie 請求書 τιμολόγιο '.encode('utf8')
    repeat_count = _payload_size // len(pattern) + 1

    out = (pattern * repeat_count)[:_payload_size]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestOperatorActions:
    """ A resend, a reprocess and a redelivery of a message of 2 MB.
    """

    def test_resend_reprocess_redeliver(self, database:'LiveDB', writer:'GroupCommitWriter', parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)

        exchange = new_exchange(parties, settings)
        use_store(exchange.receiver, MessageStore(writer))

        send_log = SendLog(AuditSource.EbMS2, Server_Name, exchange.clock, writer)

        data = _payload_data()
        payload = new_payload(data)

        outbound = send(exchange, [payload])
        message_id = outbound.message_id

        sent = new_sent_message(outbound, outbound.package)
        send_log.record_first_attempt(sent)

        first_bytes = send_log.wire_body(message_id)

        # The partner receives the message and the application confirms its delivery ..
        result = deliver(exchange, outbound)
        confirm(exchange, result)

        send_log.record_completion(send_log.get(message_id), receipt_outcome())

        # .. a resend sends the same bytes under the same MessageId ..
        exchange.clock.advance(60)
        resent = send_log.resend(message_id)

        assert resent.message_id == message_id
        assert send_log.is_open(message_id)
        assert send_log.wire_body(message_id) == first_bytes

        # .. a reprocess sends the same payload under a new MessageId, linked to the original ..
        original = send_log.get(message_id)
        reprocessed = reprocess(send_log, exchange.agreement, exchange.sender.local_keys, message_id, exchange.clock)

        assert reprocessed.message_id != message_id
        assert send_log.get(message_id).outcome.final_state == FinalState.Superseded

        new_sent = send_log.get(reprocessed.message_id)
        statement = select(event_link_table).where(event_link_table.c.child_event_id == new_sent.wire_event_id)

        with database.engine.connect() as connection:
            links = connection.execute(statement).all()

        assert len(links) == 1
        assert links[0].parent_event_id == original.wire_event_id
        assert links[0].link_type == AuditLink.Resubmit_Of

        reprocessed_result = deliver(exchange, reprocessed)
        assert reprocessed_result.deliveries[0].payloads[0].data == data

        confirm(exchange, reprocessed_result)

        # .. and a redelivery hands the first message to the application again, flagged, from its stored bytes.
        receive_log = exchange.receiver.receive_log
        assert pending_deliveries(receive_log, _page_size) == []

        delivery = redeliver(receive_log, message_id)

        assert delivery.is_possible_duplicate
        assert delivery.payloads[0].data == data
        assert len(pending_deliveries(receive_log, _page_size)) == 1

# ################################################################################################################################
# ################################################################################################################################
