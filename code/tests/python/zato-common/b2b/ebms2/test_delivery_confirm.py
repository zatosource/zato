# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import AuditEvent, event_table
from zato.common.b2b.common.outcome import FinalState
from zato.common.b2b.ebms2.common import MessageOrderSemantics, MessageStatus, MSHService, SequenceStatus, SyncReplyMode
from zato.common.b2b.ebms2.inbound_common import new_receive_log, pending_deliveries
from zato.common.b2b.ebms2.outbound import SendOptions
from zato.common.test.b2b_cpa import new_settings
from zato.common.test.b2b_ebms2 import answer, confirm, deliver, new_exchange, new_payload, resolve, send, Server_Name, \
    Start_Time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.b2b.ebms2.inbound import InboundResult
    from zato.common.b2b.ebms2.outbound import OutboundMessage
    from zato.common.test.b2b_cpa import AgreementSettings
    from zato.common.test.b2b_ebms2 import Exchange
    from zato.common.test.b2b_pki import TestParties
    from zato.common.typing_ import strlist
    AgreementSettings = AgreementSettings
    Exchange = Exchange
    InboundResult = InboundResult
    OutboundMessage = OutboundMessage
    strlist = strlist
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

_conversation_id = 'b2b-confirmed-conversation'

# How many deliveries one page of a recovery holds in the paging test, and how many messages that test receives.
_page_size = 2
_paged_message_count = 5

# ################################################################################################################################
# ################################################################################################################################

def _settings(parties:'TestParties') -> 'AgreementSettings':
    out = new_settings(parties, Start_Time)
    out.business_channel.sync_reply_mode = SyncReplyMode.MSH_Signals_Only

    return out

# ################################################################################################################################

def _exchange(parties:'TestParties') -> 'Exchange':
    settings = _settings(parties)

    out = new_exchange(parties, settings)
    return out

# ################################################################################################################################

def _ordered(parties:'TestParties') -> 'Exchange':
    settings = _settings(parties)
    settings.message_order = MessageOrderSemantics.Guaranteed

    out = new_exchange(parties, settings)
    return out

# ################################################################################################################################

def _numbered(exchange:'Exchange', sequence_number:'int') -> 'OutboundMessage':
    """ Returns a message of an ordered conversation with its sequence number as its payload.
    """
    options = SendOptions()
    options.conversation_id = _conversation_id
    options.sequence_number = sequence_number
    options.sequence_status = SequenceStatus.Continue

    data = f'<Order><Id>{sequence_number}</Id></Order>'.encode('ascii')
    payload = new_payload(data)

    out = send(exchange, [payload], options)
    return out

# ################################################################################################################################

def _payload_data(result:'InboundResult') -> 'list[bytes]':
    out:'list[bytes]' = []

    for delivery in result.deliveries:
        payload = delivery.payloads[0]
        out.append(payload.data)

    return out

# ################################################################################################################################

def _pending_ids(exchange:'Exchange') -> 'strlist':
    """ Returns the MessageId of each delivery the receiver has not confirmed, in the order the deliveries began.
    """
    out:'strlist' = []

    for delivery in pending_deliveries(exchange.receiver.receive_log, _paged_message_count):
        out.append(delivery.message_id)

    return out

# ################################################################################################################################

def _event_types(exchange:'Exchange', message_id:'str') -> 'strlist':
    query = select(event_table.c.event_type).where(event_table.c.msg_id == message_id).order_by(event_table.c.id)

    with exchange.receiver.receive_log.writer.engine.connect() as connection:
        out = list(connection.execute(query).scalars())

    return out

# ################################################################################################################################

def _status_of(exchange:'Exchange', message_id:'str') -> 'str':
    """ Returns the status a StatusRequest about a message is answered with.
    """
    options = SendOptions()
    options.status_request_ref = message_id

    binding = resolve(exchange, MSHService.Status_Request, is_msh=True)
    outbound = send(exchange, [], options, binding)

    result = deliver(exchange, outbound)
    _ = answer(exchange, outbound, result)

    status_response = outbound.status_response
    assert status_response is not None

    out = status_response.message_status
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestConfirmation:
    """ A received message stays pending until the application confirms that it processed it.
    """

    def test_pending_until_confirmed(self, parties:'TestParties') -> 'None':
        exchange = _exchange(parties)

        outbound = send(exchange)
        result = deliver(exchange, outbound)

        delivery = result.deliveries[0]

        assert not delivery.is_possible_duplicate
        assert delivery.identity.message_id == outbound.message_id
        assert delivery.cpa_id == exchange.agreement.cpa_id
        assert _pending_ids(exchange) == [outbound.message_id]

        confirm(exchange, result)

        assert _pending_ids(exchange) == []
        assert _event_types(exchange, outbound.message_id) == [AuditEvent.Message_Received, AuditEvent.Message_Delivered]

    def test_status_request(self, parties:'TestParties') -> 'None':
        exchange = _exchange(parties)

        outbound = send(exchange)
        result = deliver(exchange, outbound)

        assert _status_of(exchange, outbound.message_id) == MessageStatus.Received

        confirm(exchange, result)

        assert _status_of(exchange, outbound.message_id) == MessageStatus.Processed

    def test_duplicate_while_pending(self, parties:'TestParties') -> 'None':
        exchange = _exchange(parties)

        outbound = send(exchange)

        first = deliver(exchange, outbound)
        second = deliver(exchange, outbound)

        # The copy is answered with the stored acknowledgment and is not delivered a second time ..
        assert second.outcome.final_state == FinalState.Duplicate
        assert not second.deliveries
        assert second.response.body == first.response.body

        # .. and the message is pending once.
        assert _pending_ids(exchange) == [outbound.message_id]

# ################################################################################################################################
# ################################################################################################################################

class TestRecovery:
    """ The deliveries that the application did not confirm are read again after a restart.
    """

    def test_unconfirmed_delivery_is_recovered(self, parties:'TestParties') -> 'None':
        exchange = _exchange(parties)

        confirmed = send(exchange)
        unconfirmed = send(exchange)

        confirmed_result = deliver(exchange, confirmed)
        unconfirmed_result = deliver(exchange, unconfirmed)

        confirm(exchange, confirmed_result)

        # A restarted server has a new receive log over the same database.
        store = exchange.receiver.receive_log.store
        receive_log = new_receive_log(store, Server_Name)

        recovered = pending_deliveries(receive_log, _page_size)

        assert len(recovered) == 1

        delivery = recovered[0]
        original = unconfirmed_result.deliveries[0]

        assert delivery.is_possible_duplicate
        assert delivery.identity == original.identity
        assert delivery.cpa_id == original.cpa_id
        assert delivery.conversation_id == original.conversation_id
        assert delivery.action == original.action
        assert delivery.payloads[0].data == original.payloads[0].data

        receive_log.confirm(delivery.identity, delivery.cpa_id)

        assert pending_deliveries(receive_log, _page_size) == []

    def test_recovery_in_pages(self, parties:'TestParties') -> 'None':
        exchange = _exchange(parties)

        expected:'strlist' = []

        for _ in range(_paged_message_count):
            outbound = send(exchange)
            _ = deliver(exchange, outbound)
            expected.append(outbound.message_id)

        receive_log = exchange.receiver.receive_log

        recovered:'strlist' = []
        after_id = 0

        while page := pending_deliveries(receive_log, _page_size, after_id):

            assert len(page) <= _page_size

            for delivery in page:
                recovered.append(delivery.message_id)

            after_id = page[-1].record_id

        assert recovered == expected

# ################################################################################################################################
# ################################################################################################################################

class TestHeldMessages:
    """ A held message of an ordered conversation is not pending until a message before it releases it.
    """

    def test_held_message_is_not_pending(self, parties:'TestParties') -> 'None':
        exchange = _ordered(parties)

        _ = _numbered(exchange, 0)
        second = _numbered(exchange, 1)

        result = deliver(exchange, second)

        assert result.outcome.final_state == FinalState.Held
        assert _pending_ids(exchange) == []
        assert _event_types(exchange, second.message_id) == [AuditEvent.Message_Received, AuditEvent.Message_Held]

    def test_release_opens_the_deliveries_in_order(self, parties:'TestParties') -> 'None':
        exchange = _ordered(parties)

        first = _numbered(exchange, 0)
        second = _numbered(exchange, 1)
        third = _numbered(exchange, 2)

        _ = deliver(exchange, third)
        _ = deliver(exchange, second)
        result = deliver(exchange, first)

        assert _payload_data(result) == [
            b'<Order><Id>0</Id></Order>',
            b'<Order><Id>1</Id></Order>',
            b'<Order><Id>2</Id></Order>',
        ]

        # The released messages are delivered as they arrived, and each one is pending in the order of delivery.
        for delivery in result.deliveries:
            assert not delivery.is_possible_duplicate

        assert _pending_ids(exchange) == [first.message_id, second.message_id, third.message_id]

        confirm(exchange, result)

        assert _pending_ids(exchange) == []

    def test_released_message_is_recovered(self, parties:'TestParties') -> 'None':
        exchange = _ordered(parties)

        first = _numbered(exchange, 0)
        second = _numbered(exchange, 1)

        _ = deliver(exchange, second)
        _ = deliver(exchange, first)

        recovered = pending_deliveries(exchange.receiver.receive_log, _page_size)

        assert len(recovered) == 2
        assert recovered[1].message_id == second.message_id
        assert recovered[1].payloads[0].data == b'<Order><Id>1</Id></Order>'
        assert recovered[1].is_possible_duplicate

# ################################################################################################################################
# ################################################################################################################################
