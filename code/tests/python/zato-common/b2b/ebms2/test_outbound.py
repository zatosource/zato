# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta
from http.client import INTERNAL_SERVER_ERROR, OK, SERVICE_UNAVAILABLE

# pytest
import pytest

# Zato
from zato.common.b2b.common.outcome import FinalState, SignalKind
from zato.common.b2b.common.retry import RetryAction
from zato.common.b2b.ebms2.common import EbMS2Exception, ErrorCode, MessageOrderSemantics, PerMessage, Root_Content_Type, \
    SyncReplyMode
from zato.common.b2b.ebms2.inbound import receive
from zato.common.b2b.ebms2.inbound_common import payload_digests
from zato.common.b2b.ebms2.outbound import accept_response, give_up, next_action, OutboundState, record_resend, \
    SendOptions
from zato.common.b2b.ebms2.packaging import unpack
from zato.common.test.b2b_cpa import new_settings, Receiver_Endpoint
from zato.common.test.b2b_ebms2 import answer, deliver, new_exchange, new_payload, send, Start_Time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.b2b_cpa import AgreementSettings
    from zato.common.test.b2b_pki import TestParties
    AgreementSettings = AgreementSettings
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

_retry_interval_seconds = 30

# ################################################################################################################################
# ################################################################################################################################

def _settings(parties:'TestParties', sync_reply_mode:'str'=SyncReplyMode.MSH_Signals_Only) -> 'AgreementSettings':
    out = new_settings(parties, Start_Time)
    out.business_channel.sync_reply_mode = sync_reply_mode

    return out

# ################################################################################################################################

def _signed_receipts(parties:'TestParties') -> 'AgreementSettings':
    """ Returns the settings of an agreement whose acknowledgments are signed and echo the references of the message.
    """
    out = _settings(parties)
    out.business_channel.ack_signature_requested = PerMessage.Always
    out.is_msh_signed = True

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestBuild:
    """ Outgoing messages as the agreement and the caller describe them.
    """

    def test_build(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        exchange = new_exchange(parties, settings)

        payload = new_payload()

        options = SendOptions()
        options.message_id = 'b2b-message-1@b2b.test'

        outbound = send(exchange, [payload], options)

        expected_digests = payload_digests([payload])

        assert outbound.message_id == 'b2b-message-1@b2b.test'
        assert outbound.header.conversation_id
        assert outbound.endpoint == Receiver_Endpoint
        assert outbound.is_ack_requested
        assert not outbound.is_ack_signature_requested
        assert outbound.is_sync_reply
        assert outbound.signature is not None
        assert len(outbound.sent_digests) == 2
        assert outbound.policy.retries == 3
        assert outbound.policy.retry_interval == timedelta(seconds=_retry_interval_seconds)
        assert outbound.retry_state.attempt_count == 1
        assert outbound.retry_state.last_attempt_at == Start_Time
        assert outbound.state == OutboundState.Pending
        assert outbound.outcome.payload_digests == expected_digests
        assert outbound.package.headers['Content-Type'].startswith('multipart/related')

    def test_content_ids_are_generated(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)
        unpacked = unpack(outbound.package.headers, outbound.package.body)

        content_id = unpacked.payloads[0].content_id
        reference = f'cid:{content_id}'.encode('ascii')

        assert content_id
        assert reference in unpacked.envelope

    def test_ordered_conversation_needs_sequence_number(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        settings.message_order = MessageOrderSemantics.Guaranteed
        exchange = new_exchange(parties, settings)

        with pytest.raises(EbMS2Exception) as info:
            _ = send(exchange)

        assert info.value.error_code == ErrorCode.Inconsistent

# ################################################################################################################################
# ################################################################################################################################

class TestResponses:
    """ What comes back for an outgoing message - acknowledgments, error messages, faults and transport failures.
    """

    def test_synchronous_acknowledgment(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)
        result = deliver(exchange, outbound)
        outcome = answer(exchange, outbound, result)

        assert outbound.state == OutboundState.Acknowledged
        assert outbound.completed_at == Start_Time
        assert outcome.delivered
        assert outcome.signal_kind == SignalKind.Receipt
        assert outcome.final_state == FinalState.Delivered
        assert not outcome.signature_verified

        decision = next_action(outbound, exchange.clock)
        assert decision.action == RetryAction.Done

    def test_asynchronous_acknowledgment(self, parties:'TestParties') -> 'None':
        settings = _settings(parties, SyncReplyMode.No_Reply)
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)
        result = deliver(exchange, outbound)

        outcome = accept_response(outbound, result.response.status_code, result.response.headers, result.response.body,
            exchange.clock)

        assert outbound.state == OutboundState.Pending
        assert not outcome.delivered

        outcome = answer(exchange, outbound, result)

        assert outbound.state == OutboundState.Acknowledged
        assert outcome.delivered

    def test_signed_acknowledgment(self, parties:'TestParties') -> 'None':
        settings = _signed_receipts(parties)
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)
        result = deliver(exchange, outbound)
        outcome = answer(exchange, outbound, result)

        assert outbound.is_ack_signature_requested
        assert b'Reference' in result.response.body
        assert outbound.state == OutboundState.Acknowledged
        assert outcome.signature_verified
        assert outcome.delivered

    def test_signed_acknowledgment_of_other_digests(self, parties:'TestParties') -> 'None':
        settings = _signed_receipts(parties)
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)
        result = deliver(exchange, outbound)

        for uri in outbound.sent_digests:
            outbound.sent_digests[uri] = 'AAAA'

        outcome = answer(exchange, outbound, result)

        assert outbound.state == OutboundState.Failed
        assert outcome.error_code == ErrorCode.Security_Failure
        assert not outcome.delivered

    def test_unsigned_acknowledgment_when_signature_requested(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)
        outbound.is_ack_signature_requested = True

        result = deliver(exchange, outbound)
        outcome = answer(exchange, outbound, result)

        assert outbound.state == OutboundState.Failed
        assert outcome.error_code == ErrorCode.Security_Failure

    def test_acknowledgment_of_another_message(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        exchange = new_exchange(parties, settings)

        first = send(exchange)
        second = send(exchange)

        result = deliver(exchange, first)
        outcome = answer(exchange, second, result)

        assert second.state == OutboundState.Pending
        assert not outcome.delivered

    def test_error_message(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        exchange = new_exchange(parties, settings)

        other_settings = _settings(parties)
        other_settings.cpa_id = 'b2b-other-agreement'
        other_exchange = new_exchange(parties, other_settings)

        outbound = send(exchange)
        result = deliver(other_exchange, outbound)
        outcome = answer(exchange, outbound, result)

        assert outbound.state == OutboundState.Failed
        assert outcome.signal_kind == SignalKind.Error
        assert outcome.error_code == ErrorCode.Value_Not_Recognized
        assert outcome.final_state == FinalState.Failed

    def test_soap_fault(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)

        receiver = exchange.receiver
        headers = {'Content-Type': Root_Content_Type}
        result = receive(exchange.agreement, receiver.local_keys, headers, b'not xml', receiver.store, exchange.clock)

        response = result.response
        assert response.status_code == INTERNAL_SERVER_ERROR

        outcome = accept_response(outbound, response.status_code, response.headers, response.body, exchange.clock)

        assert outbound.state == OutboundState.Failed
        assert outcome.error_code == ErrorCode.Other_XML

    def test_transport_failure(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)
        outcome = accept_response(outbound, SERVICE_UNAVAILABLE, {}, b'', exchange.clock)

        assert outbound.state == OutboundState.Pending
        assert outbound.completed_at is None
        assert outcome.final_state == FinalState.Failed
        assert not outcome.delivered

    def test_no_acknowledgment_expected(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        settings.business_channel.ack_requested = PerMessage.Never
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)
        outcome = accept_response(outbound, OK, {}, b'', exchange.clock)

        assert outbound.state == OutboundState.Acknowledged
        assert outcome.delivered
        assert outcome.signal_kind == SignalKind.No_Signal

# ################################################################################################################################
# ################################################################################################################################

class TestRetries:
    """ Messages that are not acknowledged in time are sent again, until the retries or the time to live run out.
    """

    def test_retries_run_out(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)

        decision = next_action(outbound, exchange.clock)
        retry_at = Start_Time + timedelta(seconds=_retry_interval_seconds)

        assert decision.action == RetryAction.Wait
        assert decision.at == retry_at

        for _ in range(settings.retries):

            exchange.clock.advance(_retry_interval_seconds)

            decision = next_action(outbound, exchange.clock)
            assert decision.action == RetryAction.Resend

            record_resend(outbound, exchange.clock)

        exchange.clock.advance(_retry_interval_seconds)

        decision = next_action(outbound, exchange.clock)
        assert decision.action == RetryAction.Give_Up
        assert outbound.outcome.retry_count == settings.retries

        give_up(outbound)

        assert outbound.state == OutboundState.Failed
        assert outbound.outcome.error_code == ErrorCode.Delivery_Failure

    def test_acknowledgment_of_a_resent_message(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)

        exchange.clock.advance(_retry_interval_seconds)
        record_resend(outbound, exchange.clock)

        result = deliver(exchange, outbound)
        outcome = answer(exchange, outbound, result)

        assert outcome.delivered
        assert outcome.retry_count == 1

        decision = next_action(outbound, exchange.clock)
        assert decision.action == RetryAction.Done

    def test_time_to_live_ends_retries(self, parties:'TestParties') -> 'None':
        settings = _settings(parties)
        exchange = new_exchange(parties, settings)

        options = SendOptions()
        options.time_to_live = Start_Time + timedelta(seconds=10)

        outbound = send(exchange, None, options)

        decision = next_action(outbound, exchange.clock)

        assert decision.action == RetryAction.Wait
        assert decision.at == options.time_to_live

        exchange.clock.advance(11)

        decision = next_action(outbound, exchange.clock)
        assert decision.action == RetryAction.Give_Up

# ################################################################################################################################
# ################################################################################################################################
