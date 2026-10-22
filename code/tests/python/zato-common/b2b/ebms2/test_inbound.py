# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta
from http.client import OK

# Zato
from zato.common.b2b.common.outcome import FinalState, SignalKind
from zato.common.b2b.ebms2.common import ErrorCode, PerMessage, Root_Content_Type, SyncReplyMode
from zato.common.b2b.ebms2.inbound import receive
from zato.common.b2b.ebms2.inbound_common import payload_digests
from zato.common.b2b.ebms2.compose import compose, Composition, new_message_header, new_message_id
from zato.common.b2b.ebms2.message import serialize
from zato.common.b2b.ebms2.outbound import SendOptions
from zato.common.test.b2b_cpa import new_settings, Receiver_Name, Sender_Endpoint, Sender_Name, Validity_Days
from zato.common.test.b2b_ebms2 import deliver, new_exchange, new_payload, resolve, send, Start_Time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.b2b.ebms2.inbound import InboundResult
    from zato.common.test.b2b_cpa import AgreementSettings
    from zato.common.test.b2b_pki import TestParties
    AgreementSettings = AgreementSettings
    InboundResult = InboundResult
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

_seconds_per_day = 86400

# ################################################################################################################################
# ################################################################################################################################

def _settings(parties:'TestParties', sync_reply_mode:'str'=SyncReplyMode.No_Reply) -> 'AgreementSettings':
    out = new_settings(parties, Start_Time)
    out.business_channel.sync_reply_mode = sync_reply_mode

    return out

# ################################################################################################################################

def _assert_rejected(result:'InboundResult', error_code:'str') -> 'None':
    assert result.outcome.error_code == error_code
    assert result.outcome.signal_kind == SignalKind.Error
    assert result.outcome.final_state == FinalState.Rejected
    assert not result.outcome.delivered
    assert not result.deliveries

# ################################################################################################################################
# ################################################################################################################################

class TestDelivery:
    """ Business messages that are received and handed over to the application.
    """

    def test_delivery(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        exchange = new_exchange(parties, settings)

        first = new_payload(b'<First/>', 'first@b2b.test')
        second = new_payload(b'<Second/>', 'second@b2b.test')

        options = SendOptions()
        options.conversation_id = 'b2b-conversation-1'

        outbound = send(exchange, [first, second], options)
        result = deliver(exchange, outbound)

        delivery = result.deliveries[0]

        assert len(result.deliveries) == 1
        assert delivery.message_id == outbound.message_id
        assert delivery.conversation_id == 'b2b-conversation-1'
        assert delivery.service == settings.service
        assert delivery.action == settings.action
        assert delivery.from_party == Sender_Name
        assert delivery.to_party == Receiver_Name
        assert delivery.payloads[0].data == b'<First/>'
        assert delivery.payloads[1].data == b'<Second/>'

        expected_digests = payload_digests([first, second])

        assert result.outcome.delivered
        assert result.outcome.final_state == FinalState.Delivered
        assert result.outcome.payload_digests == expected_digests
        assert result.header is not None
        assert result.header.message_data.message_id == outbound.message_id

# ################################################################################################################################
# ################################################################################################################################

class TestReplyModes:
    """ Where the acknowledgment of a received message goes, as the delivery channels of the agreement say.
    """

    def test_asynchronous_acknowledgment(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)
        result = deliver(exchange, outbound)

        assert not outbound.is_sync_reply
        assert result.response.status_code == OK
        assert not result.response.body
        assert result.async_signal is not None
        assert result.async_signal.endpoint == Sender_Endpoint
        assert b'Acknowledgment' in result.async_signal.package.body
        assert result.outcome.signal_kind == SignalKind.Receipt

    def test_synchronous_acknowledgment(self, parties:'TestParties') -> 'None':
        settings = _settings(parties, SyncReplyMode.MSH_Signals_Only)
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)
        result = deliver(exchange, outbound)

        assert outbound.is_sync_reply
        assert result.async_signal is None
        assert b'Acknowledgment' in result.response.body
        assert result.response.headers['Content-Type'].startswith('multipart/related')
        assert result.outcome.signal_kind == SignalKind.Receipt

    def test_signals_only(self, parties:'TestParties') -> 'None':
        settings = _settings(parties, SyncReplyMode.Signals_Only)
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)
        result = deliver(exchange, outbound)

        assert result.async_signal is None
        assert b'Acknowledgment' in result.response.body

    def test_response_only(self, parties:'TestParties') -> 'None':
        settings = _settings(parties, SyncReplyMode.Response_Only)
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)
        result = deliver(exchange, outbound)

        assert outbound.is_sync_reply
        assert not result.response.body
        assert result.async_signal is not None

    def test_no_acknowledgment(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        settings.business_channel.ack_requested = PerMessage.Never
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)
        result = deliver(exchange, outbound)

        assert not outbound.is_ack_requested
        assert not result.response.body
        assert result.async_signal is None
        assert result.outcome.signal_kind == SignalKind.No_Signal
        assert result.outcome.delivered

    def test_acknowledgment_per_message(self, parties:'TestParties') -> 'None':
        settings = _settings(parties, SyncReplyMode.MSH_Signals_Only)
        settings.business_channel.ack_requested = PerMessage.Per_Message
        exchange = new_exchange(parties, settings)

        options = SendOptions()
        options.ack_requested = False

        unacknowledged = send(exchange, None, options)
        unacknowledged_result = deliver(exchange, unacknowledged)

        acknowledged = send(exchange)
        acknowledged_result = deliver(exchange, acknowledged)

        assert not unacknowledged_result.response.body
        assert b'Acknowledgment' in acknowledged_result.response.body

# ################################################################################################################################
# ################################################################################################################################

class TestRejection:
    """ Business messages that are answered with an error message instead of being delivered.
    """

    def test_unknown_agreement(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        exchange = new_exchange(parties, settings)

        other_settings = _settings(parties)
        other_settings.cpa_id = 'b2b-other-agreement'
        other_exchange = new_exchange(parties, other_settings)

        outbound = send(exchange)
        result = deliver(other_exchange, outbound)

        _assert_rejected(result, ErrorCode.Value_Not_Recognized)

        # Without a binding, the error message goes back on the same connection.
        assert result.async_signal is None
        assert b'ErrorList' in result.response.body

    def test_agreement_not_in_effect(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)

        exchange.clock.advance((Validity_Days + 1) * _seconds_per_day)
        result = deliver(exchange, outbound)

        _assert_rejected(result, ErrorCode.Inconsistent)

    def test_expired_time_to_live(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        exchange = new_exchange(parties, settings)

        options = SendOptions()
        options.time_to_live = Start_Time + timedelta(seconds=60)

        outbound = send(exchange, None, options)

        exchange.clock.advance(120)
        result = deliver(exchange, outbound)

        _assert_rejected(result, ErrorCode.Time_To_Live_Expired)

        # With a binding, the error message follows the reply mode of the sender's channel.
        assert result.async_signal is not None
        assert b'ErrorList' in result.async_signal.package.body

    def test_time_to_live_not_reached(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        exchange = new_exchange(parties, settings)

        options = SendOptions()
        options.time_to_live = Start_Time + timedelta(seconds=60)

        outbound = send(exchange, None, options)

        exchange.clock.advance(30)
        result = deliver(exchange, outbound)

        assert result.outcome.delivered

    def test_envelope_without_its_part(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        settings.is_signed = False
        exchange = new_exchange(parties, settings)

        binding = resolve(exchange)
        message_id = new_message_id()
        payload = new_payload(content_id='payload-1@b2b.test')

        composition = Composition()
        composition.header = new_message_header(binding, Start_Time, 'b2b-conversation-1', message_id)
        composition.payloads = [payload]

        composed = compose(composition)

        # The envelope travels without the MIME part its manifest names.
        envelope = serialize(composed.envelope)
        headers = {'Content-Type': Root_Content_Type}

        receiver = exchange.receiver
        result = receive(exchange.agreement, receiver.local_keys, headers, envelope, receiver.store, exchange.clock)

        _assert_rejected(result, ErrorCode.MIME_Problem)

    def test_message_without_payloads(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        exchange = new_exchange(parties, settings)

        outbound = send(exchange, [])
        result = deliver(exchange, outbound)

        assert result.outcome.delivered
        assert result.outcome.signature_verified
        assert result.deliveries[0].payloads == []

# ################################################################################################################################
# ################################################################################################################################
