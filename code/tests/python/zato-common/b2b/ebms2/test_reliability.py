# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from tempfile import NamedTemporaryFile

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import create_engine

# Zato
from zato.common.b2b.common.commit_group import GroupCommitWriter
from zato.common.b2b.common.store import MessageStore
from zato.common.b2b.common.outcome import FinalState, SignalKind
from zato.common.b2b.ebms2.common import ErrorCode, MessageOrderSemantics, PerMessage, SequenceStatus, SyncReplyMode
from zato.common.b2b.ebms2.outbound import SendOptions
from zato.common.b2b.ebms2.reliability import next_sequence_number
from zato.common.test.b2b_cpa import new_settings
from zato.common.test.b2b_ebms2 import deliver, new_exchange, new_payload, send, Start_Time
from zato.common.test.b2b_write_path import CommitRefused, FailingCommit, new_memory_engine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.b2b.ebms2.outbound import OutboundMessage
    from zato.common.test.b2b_cpa import AgreementSettings
    from zato.common.test.b2b_ebms2 import Exchange
    from zato.common.test.b2b_pki import TestParties
    AgreementSettings = AgreementSettings
    Exchange = Exchange
    OutboundMessage = OutboundMessage
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

_seconds_per_day = 86400

_conversation_id = 'b2b-ordered-conversation'

# The highest sequence number of ebMS 2.0, after which a conversation starts from zero again.
_max_sequence_number = 99999999

# ################################################################################################################################
# ################################################################################################################################

def _settings(parties:'TestParties') -> 'AgreementSettings':
    out = new_settings(parties, Start_Time)
    out.business_channel.sync_reply_mode = SyncReplyMode.MSH_Signals_Only

    return out

# ################################################################################################################################

def _ordered(parties:'TestParties') -> 'Exchange':
    settings = _settings(parties)
    settings.message_order = MessageOrderSemantics.Guaranteed

    out = new_exchange(parties, settings)
    return out

# ################################################################################################################################

def _numbered(exchange:'Exchange', sequence_number:'int', status:'str'=SequenceStatus.Continue) -> 'OutboundMessage':
    """ Returns a message of an ordered conversation with its sequence number as its payload.
    """
    options = SendOptions()
    options.conversation_id = _conversation_id
    options.sequence_number = sequence_number
    options.sequence_status = status

    data = f'<Order><Id>{sequence_number}</Id></Order>'.encode('ascii')
    payload = new_payload(data)

    out = send(exchange, [payload], options)
    return out

# ################################################################################################################################

def _delivered_data(exchange:'Exchange', outbound:'OutboundMessage') -> 'list[bytes]':
    """ Delivers a message and returns the payload of each message that the delivery handed over, in order.
    """
    result = deliver(exchange, outbound)

    out:'list[bytes]' = []

    for delivery in result.deliveries:
        payload = delivery.payloads[0]
        out.append(payload.data)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestDuplicateElimination:
    """ Copies of a message that is already recorded are answered and not delivered again.
    """

    def test_duplicate_is_not_delivered(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)

        first = deliver(exchange, outbound)
        second = deliver(exchange, outbound)

        assert first.outcome.delivered
        assert len(first.deliveries) == 1

        assert second.outcome.duplicate
        assert second.outcome.final_state == FinalState.Duplicate
        assert not second.deliveries

        # The copy is answered with the very acknowledgment the first one was answered with.
        assert second.response.body == first.response.body
        assert second.response.content_type == first.response.content_type

    def test_asynchronous_answer_of_a_duplicate(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        settings.business_channel.sync_reply_mode = SyncReplyMode.No_Reply
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)

        first = deliver(exchange, outbound)
        second = deliver(exchange, outbound)

        assert first.async_signal is not None
        assert second.async_signal is not None
        assert second.async_signal.package.body == first.async_signal.package.body
        assert second.async_signal.endpoint == first.async_signal.endpoint
        assert not second.deliveries

    def test_after_persist_duration(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)
        _ = deliver(exchange, outbound)

        exchange.clock.advance(_seconds_per_day + 1)
        result = deliver(exchange, outbound)

        assert result.outcome.delivered
        assert not result.outcome.duplicate

    def test_never_eliminated(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        settings.business_channel.duplicate_elimination = PerMessage.Never
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)

        first = deliver(exchange, outbound)
        second = deliver(exchange, outbound)

        assert not outbound.header.duplicate_elimination
        assert first.outcome.delivered
        assert second.outcome.delivered
        assert not second.outcome.duplicate

    def test_per_message(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        settings.business_channel.duplicate_elimination = PerMessage.Per_Message
        exchange = new_exchange(parties, settings)

        options = SendOptions()
        options.duplicate_elimination = False

        outbound = send(exchange, None, options)

        first = deliver(exchange, outbound)
        second = deliver(exchange, outbound)

        assert first.outcome.delivered
        assert second.outcome.delivered

    def test_same_message_id_other_payload(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        exchange = new_exchange(parties, settings)

        options = SendOptions()
        options.message_id = 'b2b-message-1@b2b.test'

        first_payload = new_payload(b'<Order><Id>1</Id></Order>')
        second_payload = new_payload(b'<Order><Id>2</Id></Order>')

        first = send(exchange, [first_payload], options)
        second = send(exchange, [second_payload], options)

        _ = deliver(exchange, first)
        result = deliver(exchange, second)

        assert result.outcome.duplicate
        assert not result.deliveries

    def test_duplicate_is_acknowledged(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)

        first = deliver(exchange, outbound)
        second = deliver(exchange, outbound)

        assert first.outcome.signal_kind == SignalKind.Receipt
        assert second.outcome.signal_kind == SignalKind.Receipt
        assert b'Acknowledgment' in second.response.body

    def test_database_store(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        exchange = new_exchange(parties, settings)

        with NamedTemporaryFile(suffix='.db') as database:

            engine = create_engine(f'sqlite:///{database.name}')
            writer = GroupCommitWriter(engine)
            exchange.receiver.store = MessageStore(writer)

            outbound = send(exchange)

            first = deliver(exchange, outbound)
            second = deliver(exchange, outbound)

            writer.stop()
            engine.dispose()

        assert first.outcome.delivered
        assert second.outcome.duplicate
        assert second.response.body == first.response.body

    def test_failed_commit(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        exchange = new_exchange(parties, settings)

        writer = GroupCommitWriter(new_memory_engine(), interval_ms=0, is_started=False)
        exchange.receiver.store = MessageStore(writer)

        outbound = send(exchange)

        # A claim that is not committed produces neither an acknowledgment nor a delivery ..
        failing = FailingCommit(writer.engine)

        with pytest.raises(CommitRefused):
            _ = deliver(exchange, outbound)

        failing.stop()

        # .. and the resend of the partner is delivered as the first copy.
        resent = deliver(exchange, outbound)

        assert resent.outcome.delivered
        assert not resent.outcome.duplicate

# ################################################################################################################################
# ################################################################################################################################

class TestMessageOrder:
    """ The messages of an ordered conversation are delivered in the order of their sequence numbers.
    """

    def test_in_order(self, parties:'TestParties') -> 'None':
        exchange = _ordered(parties)

        first = _numbered(exchange, 0)
        second = _numbered(exchange, 1)

        assert _delivered_data(exchange, first) == [b'<Order><Id>0</Id></Order>']
        assert _delivered_data(exchange, second) == [b'<Order><Id>1</Id></Order>']

    def test_out_of_order(self, parties:'TestParties') -> 'None':
        exchange = _ordered(parties)

        first = _numbered(exchange, 0)
        second = _numbered(exchange, 1)
        third = _numbered(exchange, 2)

        third_result = deliver(exchange, third)
        second_result = deliver(exchange, second)

        assert third_result.outcome.final_state == FinalState.Held
        assert second_result.outcome.final_state == FinalState.Held
        assert not third_result.deliveries
        assert not second_result.deliveries

        # A held message is acknowledged on receipt, before it is delivered.
        assert third_result.outcome.signal_kind == SignalKind.Receipt

        delivered = _delivered_data(exchange, first)

        assert delivered == [
            b'<Order><Id>0</Id></Order>',
            b'<Order><Id>1</Id></Order>',
            b'<Order><Id>2</Id></Order>',
        ]

    def test_reset(self, parties:'TestParties') -> 'None':
        exchange = _ordered(parties)

        first = _numbered(exchange, 0)
        reset = _numbered(exchange, 50, SequenceStatus.Reset)
        following = _numbered(exchange, 51)

        _ = _delivered_data(exchange, first)

        assert _delivered_data(exchange, reset) == [b'<Order><Id>50</Id></Order>']
        assert _delivered_data(exchange, following) == [b'<Order><Id>51</Id></Order>']

    def test_number_already_delivered(self, parties:'TestParties') -> 'None':
        exchange = _ordered(parties)

        first = _numbered(exchange, 0)
        second = _numbered(exchange, 1)
        repeated = _numbered(exchange, 0)

        _ = deliver(exchange, first)
        _ = deliver(exchange, second)

        result = deliver(exchange, repeated)

        assert result.outcome.duplicate
        assert not result.deliveries

    def test_missing_message_order(self, parties:'TestParties') -> 'None':
        exchange = _ordered(parties)

        # The message is built under an agreement without ordering and received under one with it.
        settings = _settings(parties)
        unordered_exchange = new_exchange(parties, settings)
        unordered = send(unordered_exchange)

        result = deliver(exchange, unordered)

        assert result.outcome.error_code == ErrorCode.Inconsistent
        assert not result.deliveries

    def test_sequence_numbers_wrap(self) -> 'None':
        assert next_sequence_number(0) == 1
        assert next_sequence_number(_max_sequence_number) == 0

# ################################################################################################################################
# ################################################################################################################################
