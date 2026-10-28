# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import AuditEvent, AuditLink, AuditSource, event_link_table, event_table
from zato.common.b2b.common.outcome import FinalState
from zato.common.b2b.common.send_log import SendLog
from zato.common.b2b.common.store import new_memory_store
from zato.common.b2b.ebms2.inbound_common import pending_deliveries, redeliver
from zato.common.b2b.ebms2.outbound_record import new_sent_message
from zato.common.b2b.ebms2.packaging import unpack
from zato.common.b2b.ebms2.reprocess import reprocess
from zato.common.test.b2b_cpa import new_settings
from zato.common.test.b2b_ebms2 import confirm, deliver, new_exchange, new_payload, send, Start_Time
from zato.common.test.b2b_write_path import receipt_outcome

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.b2b.ebms2.outbound import OutboundMessage
    from zato.common.test.b2b_ebms2 import Exchange
    from zato.common.test.b2b_pki import TestParties
    from zato.common.typing_ import strlist
    Exchange = Exchange
    OutboundMessage = OutboundMessage
    strlist = strlist
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

_server_name = 'b2b-test-server'

_payload_data = 'Zamówienie 請求書 τιμολόγιο'.encode('utf8')

# How many deliveries one page of a recovery holds.
_page_size = 10

# ################################################################################################################################
# ################################################################################################################################

def _sent(parties:'TestParties') -> 'tuple[Exchange, SendLog, OutboundMessage]':
    """ Returns an exchange, a send log, and a message that the log recorded the first delivery of.
    """
    exchange = new_exchange(parties, new_settings(parties, Start_Time))

    store = new_memory_store()
    send_log = SendLog(AuditSource.EbMS2, _server_name, exchange.clock, store.writer)

    payload = new_payload(_payload_data)
    outbound = send(exchange, [payload])

    sent = new_sent_message(outbound, outbound.package)
    send_log.record_first_attempt(sent)

    return exchange, send_log, outbound

# ################################################################################################################################

def _event_types(send_log:'SendLog', message_id:'str') -> 'strlist':
    query = select(event_table.c.event_type).where(event_table.c.msg_id == message_id)
    statement = query.order_by(event_table.c.id)

    out:'strlist' = []

    with send_log.engine.connect() as connection:
        for event_type in connection.execute(statement).scalars():
            out.append(event_type)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestResend:
    """ A resend sends the same bytes under the same MessageId and reopens an ended exchange with a new retry budget.
    """

    def test_identical_bytes(self, parties:'TestParties') -> 'None':
        exchange, send_log, outbound = _sent(parties)
        message_id = outbound.message_id

        first_bytes = send_log.wire_body(message_id)

        sent = send_log.get(message_id)
        send_log.record_completion(sent, receipt_outcome())

        assert not send_log.is_open(message_id)

        exchange.clock.advance(60)
        resent = send_log.resend(message_id)

        assert send_log.is_open(message_id)
        assert resent.message_id == message_id
        assert resent.retry_state.attempt_count == 1
        assert not resent.retry_state.is_answered
        assert resent.retry_state.last_attempt_at == exchange.clock.now()

        assert send_log.wire_body(message_id) == first_bytes
        assert first_bytes == outbound.package.body

        assert _event_types(send_log, message_id) == [
            AuditEvent.Message_Sent,
            AuditEvent.Message_Completed,
            AuditEvent.Message_Resent,
        ]

    def test_reopened_exchange_is_recovered(self, parties:'TestParties') -> 'None':
        exchange, send_log, outbound = _sent(parties)
        message_id = outbound.message_id

        sent = send_log.get(message_id)
        send_log.record_completion(sent, receipt_outcome())

        exchange.clock.advance(60)
        _ = send_log.resend(message_id)

        restarted = SendLog(AuditSource.EbMS2, _server_name, exchange.clock, send_log.writer)

        assert restarted.recover() == 1

        recovered = restarted.get(message_id)

        assert not recovered.retry_state.is_answered
        assert recovered.retry_state.last_attempt_at == exchange.clock.now()

# ################################################################################################################################
# ################################################################################################################################

class TestReprocess:
    """ A reprocess sends the payloads again under a new MessageId, linked to the original, which it supersedes.
    """

    def test_new_message_id_and_link(self, parties:'TestParties') -> 'None':
        exchange, send_log, outbound = _sent(parties)
        original_id = outbound.message_id
        original = send_log.get(original_id)

        reprocessed = reprocess(send_log, exchange.agreement, exchange.sender.local_keys, original_id, exchange.clock)

        assert reprocessed.message_id != original_id
        assert reprocessed.header.conversation_id == outbound.header.conversation_id

        unpacked = unpack(reprocessed.package.headers, reprocessed.package.body)
        assert unpacked.payloads[0].data == _payload_data

        # The first delivery of the new message is linked to that of the original ..
        new_sent = send_log.get(reprocessed.message_id)
        statement = select(event_link_table).where(event_link_table.c.child_event_id == new_sent.wire_event_id)

        with send_log.engine.connect() as connection:
            links = connection.execute(statement).all()

        assert len(links) == 1
        assert links[0].parent_event_id == original.wire_event_id
        assert links[0].link_type == AuditLink.Resubmit_Of

        # .. and the original, whose exchange was open, is superseded.
        assert not send_log.is_open(original_id)
        assert send_log.get(original_id).outcome.final_state == FinalState.Superseded
        assert send_log.is_open(reprocessed.message_id)

        # The new message is accepted by the partner like any other.
        result = deliver(exchange, reprocessed)
        assert result.deliveries[0].payloads[0].data == _payload_data

    def test_ended_original_stays_as_it_ended(self, parties:'TestParties') -> 'None':
        exchange, send_log, outbound = _sent(parties)
        original_id = outbound.message_id

        sent = send_log.get(original_id)
        send_log.record_completion(sent, receipt_outcome())

        _ = reprocess(send_log, exchange.agreement, exchange.sender.local_keys, original_id, exchange.clock)

        assert send_log.get(original_id).outcome.final_state == FinalState.Delivered

# ################################################################################################################################
# ################################################################################################################################

class TestRedeliver:
    """ A redelivery hands a received message to the application again, flagged, from its stored bytes.
    """

    def test_redeliver(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties, new_settings(parties, Start_Time))

        payload = new_payload(_payload_data)
        outbound = send(exchange, [payload])

        result = deliver(exchange, outbound)
        confirm(exchange, result)

        receive_log = exchange.receiver.receive_log
        assert pending_deliveries(receive_log, _page_size) == []

        delivery = redeliver(receive_log, outbound.message_id)

        assert delivery.is_possible_duplicate
        assert delivery.payloads[0].data == _payload_data
        assert len(pending_deliveries(receive_log, _page_size)) == 1

        query = select(event_table.c.event_type).where(event_table.c.msg_id == outbound.message_id)

        with receive_log.writer.engine.connect() as connection:
            event_types = connection.execute(query.order_by(event_table.c.id)).scalars().all()

        assert list(event_types) == [
            AuditEvent.Message_Received,
            AuditEvent.Message_Delivered,
            AuditEvent.Message_Redelivered,
        ]

# ################################################################################################################################
# ################################################################################################################################
