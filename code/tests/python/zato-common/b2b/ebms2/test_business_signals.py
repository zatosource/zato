# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# lxml
from lxml.etree import fromstring

# pytest
import pytest

# Zato
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.audit_log.common import AuditSource
from zato.common.b2b.common.business_log import BusinessLog, BusinessState, expired
from zato.common.b2b.common.exceptions import B2BException
from zato.common.b2b.common.outcome import FinalState
from zato.common.b2b.ebms2.business_signals import accept_business_message, build_signal, business_deadlines, \
    BusinessSignal, new_business_message, new_ebbp_signal, ReceiptExceptionType, Signal_Content_Type, signal_errors
from zato.common.b2b.ebms2.common import NS
from zato.common.b2b.ebms2.inbound import receive
from zato.common.b2b.ebms2.outbound import build, SendOptions
from zato.common.test.b2b_cpa import new_settings, Receiver_Name, Sender_Name
from zato.common.test.b2b_ebms2 import deliver, new_exchange, new_payload, resolve, send, Start_Time
from zato.common.util.xml_.core import qname

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from pytest import MonkeyPatch
    from zato.common.b2b.common.business_log import BusinessOutcome
    from zato.common.b2b.ebms2.header import MessageHeader
    from zato.common.b2b.ebms2.inbound import InboundResult
    from zato.common.b2b.ebms2.outbound import OutboundMessage
    from zato.common.test.b2b_ebms2 import Exchange
    from zato.common.test.b2b_pki import TestParties
    from zato.common.typing_ import any_, strlist
    any_ = any_
    BusinessOutcome = BusinessOutcome
    Exchange = Exchange
    InboundResult = InboundResult
    MessageHeader = MessageHeader
    MonkeyPatch = MonkeyPatch
    OutboundMessage = OutboundMessage
    Path = Path
    strlist = strlist
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

# The server the business log of the tests records its messages under.
_server_name = 'b2b-test-server'

# The action of the response the receiver sends back to the sender.
_response_action = 'Confirm'

# The deadlines of the business transactions of the tests.
_time_to_acknowledge_receipt = 'PT2M'
_time_to_perform = 'PT10M'
_zero_duration = 'PT0S'

_receipt_seconds = 120
_perform_seconds = 600

# How far past a deadline the clock is moved.
_past_deadline_seconds = 1

_signal_kinds = [
    BusinessSignal.Receipt_Acknowledgement,
    BusinessSignal.Receipt_Acknowledgement_Exception,
    BusinessSignal.Acceptance_Acknowledgement_Exception,
]

_exception_kinds = [
    BusinessSignal.Receipt_Acknowledgement_Exception,
    BusinessSignal.Acceptance_Acknowledgement_Exception,
]

_errors = ['The order number is not known', 'The delivery date is in the past']

_reason_tag = qname(NS.EBBP_Signals, 'Reason')
_exception_message_tag = qname(NS.EBBP_Signals, 'ExceptionMessage')
_original_message_tag = qname(NS.EBBP_Signals, 'OriginalMessageIdentifier')
_from_party_tag = qname(NS.EBBP_Signals, 'FromPartyInfo')
_to_party_tag = qname(NS.EBBP_Signals, 'ToPartyInfo')
_receipt_exception_tag = qname(NS.EBBP_Signals, 'ReceiptException')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def business_log(tmp_path:'Path', monkeypatch:'MonkeyPatch') -> 'BusinessLog':
    """ A business log on an audit log database of its own.
    """
    path = tmp_path / 'audit.db'

    monkeypatch.setenv(AuditLogCtx.Env_Enabled, 'True')
    monkeypatch.setenv(AuditLogCtx.Env_Type, AuditLogCtx.Type_SQLite)
    monkeypatch.setenv(AuditLogCtx.Env_Name, str(path))

    out = BusinessLog(AuditSource.EbMS2, _server_name)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _exchange(
    parties:'TestParties',
    time_to_acknowledge_receipt:'str'=_time_to_acknowledge_receipt,
    time_to_perform:'str'=_time_to_perform,
    ) -> 'Exchange':
    """ Returns an exchange under which the receiver sends business signals and a response back to the sender.
    """
    settings = new_settings(parties, Start_Time)
    settings.time_to_acknowledge_receipt = time_to_acknowledge_receipt
    settings.time_to_perform = time_to_perform

    for kind in _signal_kinds:
        settings.reply_actions.append(kind)

    settings.reply_actions.append(_response_action)

    out = new_exchange(parties, settings)
    return out

# ################################################################################################################################

def _received_header(exchange:'Exchange', outbound:'OutboundMessage') -> 'MessageHeader':
    """ Delivers a message of the sender to the receiver and returns its header as the receiver read it.
    """
    result = deliver(exchange, outbound)

    assert result.outcome.final_state == FinalState.Delivered
    assert result.header is not None

    out = result.header
    return out

# ################################################################################################################################

def _to_sender(exchange:'Exchange', outbound:'OutboundMessage') -> 'InboundResult':
    """ Passes a message of the receiver to the sender.
    """
    sender = exchange.sender
    package = outbound.package

    out = receive(exchange.agreement, sender.local_keys, package.headers, package.body, sender.store, exchange.clock)
    return out

# ################################################################################################################################

def _signal(exchange:'Exchange', received_header:'MessageHeader', kind:'str', errors:'strlist') -> 'OutboundMessage':
    """ Builds a business signal of the receiver about a message it received.
    """
    now = exchange.clock.now()
    document = new_ebbp_signal(kind, received_header, now, errors)

    out = build_signal(exchange.agreement, exchange.receiver.local_keys, received_header, kind, document, exchange.clock)
    return out

# ################################################################################################################################

def _response(exchange:'Exchange', received_header:'MessageHeader') -> 'OutboundMessage':
    """ Builds the response of the receiver to a message it received.
    """
    binding = resolve(exchange, _response_action, is_reverse=True)
    payload = new_payload()

    options = SendOptions()
    options.conversation_id = received_header.conversation_id
    options.ref_to_message_id = received_header.message_data.message_id

    out = build(exchange.agreement, exchange.receiver.local_keys, binding, [payload], exchange.clock, options)
    return out

# ################################################################################################################################

def _accept(business_log:'BusinessLog', exchange:'Exchange', reply:'OutboundMessage') -> 'BusinessOutcome | None':
    """ Delivers a signal or a response to the sender and matches it against the messages the sender sent.
    """
    result = _to_sender(exchange, reply)

    assert result.outcome.final_state == FinalState.Delivered
    assert result.header is not None

    delivery = result.deliveries[0]

    out = accept_business_message(business_log, result.header, delivery.payloads, exchange.clock)
    return out

# ################################################################################################################################

def _send_logged(business_log:'BusinessLog', exchange:'Exchange') -> 'OutboundMessage':
    """ Builds a message of the sender and records it in the business log.
    """
    out = send(exchange)

    message = new_business_message(out)
    business_log.record_sent(message)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSignalConstruction:
    """ The header, the signature and the document of each business signal.
    """

    @pytest.mark.parametrize('kind', _signal_kinds)
    def test_header(self, parties:'TestParties', kind:'str') -> 'None':
        exchange = _exchange(parties)
        outbound = send(exchange)
        received_header = _received_header(exchange, outbound)

        signal = _signal(exchange, received_header, kind, _errors)
        header = signal.header

        assert header.service == received_header.service
        assert header.service_type == received_header.service_type
        assert header.action == kind
        assert header.conversation_id == received_header.conversation_id
        assert header.message_data.ref_to_message_id == outbound.message_id
        assert header.message_data.message_id != outbound.message_id

        from_party_id = header.from_party.party_ids[0]
        to_party_id = header.to_party.party_ids[0]

        assert from_party_id.value == Receiver_Name
        assert to_party_id.value == Sender_Name

    @pytest.mark.parametrize('kind', _signal_kinds)
    def test_signature(self, parties:'TestParties', kind:'str') -> 'None':
        exchange = _exchange(parties)
        outbound = send(exchange)
        received_header = _received_header(exchange, outbound)

        signal = _signal(exchange, received_header, kind, _errors)

        assert signal.signature is not None

        result = _to_sender(exchange, signal)

        assert result.outcome.final_state == FinalState.Delivered
        assert result.outcome.signature_verified

        delivery = result.deliveries[0]
        payload = delivery.payloads[0]

        assert delivery.action == kind
        assert delivery.ref_to_message_id == outbound.message_id
        assert payload.content_type == Signal_Content_Type

    @pytest.mark.parametrize('kind', _signal_kinds)
    def test_document_is_valid(self, parties:'TestParties', ebbp_signals_schema:'any_', kind:'str') -> 'None':
        exchange = _exchange(parties)
        outbound = send(exchange)
        received_header = _received_header(exchange, outbound)

        now = exchange.clock.now()
        document = new_ebbp_signal(kind, received_header, now, _errors)
        root = fromstring(document)

        ebbp_signals_schema.assertValid(root)

        original_message = root.find(_original_message_tag)
        from_party = root.find(_from_party_tag)
        to_party = root.find(_to_party_tag)

        assert original_message.text == outbound.message_id
        assert from_party.text == Receiver_Name
        assert to_party.text == Sender_Name

    @pytest.mark.parametrize('kind', _exception_kinds)
    def test_exception_errors(self, parties:'TestParties', kind:'str') -> 'None':
        exchange = _exchange(parties)
        outbound = send(exchange)
        received_header = _received_header(exchange, outbound)

        now = exchange.clock.now()
        document = new_ebbp_signal(kind, received_header, now, _errors)
        root = fromstring(document)

        reason = root.find(_reason_tag)
        exception_message = root.find(_exception_message_tag)

        assert reason.text == _errors[0]
        assert exception_message.text == _errors[1]

        payload = new_payload(document)
        errors = signal_errors([payload])

        assert errors == _errors

    @pytest.mark.parametrize('kind', _exception_kinds)
    def test_exception_requires_errors(self, parties:'TestParties', kind:'str') -> 'None':
        exchange = _exchange(parties)
        outbound = send(exchange)
        received_header = _received_header(exchange, outbound)

        now = exchange.clock.now()

        with pytest.raises(B2BException):
            _ = new_ebbp_signal(kind, received_header, now, [])

    def test_exception_type(self, parties:'TestParties', ebbp_signals_schema:'any_') -> 'None':
        exchange = _exchange(parties)
        outbound = send(exchange)
        received_header = _received_header(exchange, outbound)

        now = exchange.clock.now()
        kind = BusinessSignal.Receipt_Acknowledgement_Exception
        document = new_ebbp_signal(kind, received_header, now, _errors, ReceiptExceptionType.Signature)
        root = fromstring(document)

        ebbp_signals_schema.assertValid(root)

        exception_type = root.find('.//' + _receipt_exception_tag)
        assert exception_type.text == ReceiptExceptionType.Signature

    def test_errors_of_other_formats(self) -> 'None':
        other_xml = new_payload(b'<Refusal xmlns="urn:zato:b2b:test"><Text>The order is refused</Text></Refusal>')
        plain_text = new_payload(b'The order is refused')

        assert signal_errors([other_xml]) == []
        assert signal_errors([plain_text]) == []
        assert signal_errors([]) == []

# ################################################################################################################################
# ################################################################################################################################

class TestCorrelation:
    """ The signals and the responses that refer to a message sent, matched against the business log.
    """

    def test_receipt_then_response(self, parties:'TestParties', business_log:'BusinessLog') -> 'None':
        exchange = _exchange(parties)
        outbound = _send_logged(business_log, exchange)
        received_header = _received_header(exchange, outbound)

        receipt = _signal(exchange, received_header, BusinessSignal.Receipt_Acknowledgement, [])
        outcome = _accept(business_log, exchange, receipt)

        assert outcome is not None
        assert outcome.message_id == outbound.message_id
        assert outcome.state == BusinessState.Receipted
        assert outcome.reply_message_id == receipt.message_id
        assert outcome.errors == []

        response = _response(exchange, received_header)
        outcome = _accept(business_log, exchange, response)

        assert outcome is not None
        assert outcome.state == BusinessState.Answered
        assert outcome.reply_message_id == response.message_id

        message = business_log.read(outbound.message_id)

        assert message is not None
        assert message.state == BusinessState.Answered
        assert message.reply_message_id == response.message_id
        assert message.from_party == Sender_Name
        assert message.to_party == Receiver_Name

    def test_response_without_receipt(self, parties:'TestParties', business_log:'BusinessLog') -> 'None':
        exchange = _exchange(parties)
        outbound = _send_logged(business_log, exchange)
        received_header = _received_header(exchange, outbound)

        response = _response(exchange, received_header)
        outcome = _accept(business_log, exchange, response)

        assert outcome is not None
        assert outcome.state == BusinessState.Answered

    def test_receipt_refused(self, parties:'TestParties', business_log:'BusinessLog') -> 'None':
        exchange = _exchange(parties)
        outbound = _send_logged(business_log, exchange)
        received_header = _received_header(exchange, outbound)

        refusal = _signal(exchange, received_header, BusinessSignal.Receipt_Acknowledgement_Exception, _errors)
        outcome = _accept(business_log, exchange, refusal)

        assert outcome is not None
        assert outcome.state == BusinessState.Receipt_Refused
        assert outcome.reply_message_id == refusal.message_id
        assert outcome.errors == _errors

        # A response after a refusal does not change a transaction that ended.
        response = _response(exchange, received_header)
        outcome = _accept(business_log, exchange, response)

        assert outcome is not None
        assert outcome.state == BusinessState.Receipt_Refused
        assert outcome.reply_message_id == refusal.message_id

    def test_acceptance_refused(self, parties:'TestParties', business_log:'BusinessLog') -> 'None':
        exchange = _exchange(parties)
        outbound = _send_logged(business_log, exchange)
        received_header = _received_header(exchange, outbound)

        receipt = _signal(exchange, received_header, BusinessSignal.Receipt_Acknowledgement, [])
        _ = _accept(business_log, exchange, receipt)

        refusal = _signal(exchange, received_header, BusinessSignal.Acceptance_Acknowledgement_Exception, _errors)
        outcome = _accept(business_log, exchange, refusal)

        assert outcome is not None
        assert outcome.state == BusinessState.Acceptance_Refused
        assert outcome.errors == _errors

        message = business_log.read(outbound.message_id)

        assert message is not None
        assert message.state == BusinessState.Acceptance_Refused
        assert message.errors == _errors

    def test_signals_of_two_messages(self, parties:'TestParties', business_log:'BusinessLog') -> 'None':
        exchange = _exchange(parties)

        first = _send_logged(business_log, exchange)
        second = _send_logged(business_log, exchange)

        first_header = _received_header(exchange, first)
        _ = _received_header(exchange, second)

        receipt = _signal(exchange, first_header, BusinessSignal.Receipt_Acknowledgement, [])
        _ = _accept(business_log, exchange, receipt)

        first_message = business_log.read(first.message_id)
        second_message = business_log.read(second.message_id)

        assert first_message is not None
        assert second_message is not None
        assert first_message.state == BusinessState.Receipted
        assert second_message.state == BusinessState.Sent

    def test_unknown_reference(self, parties:'TestParties', business_log:'BusinessLog') -> 'None':
        exchange = _exchange(parties)

        # The message is sent without being recorded, so nothing in the log refers to it.
        outbound = send(exchange)
        received_header = _received_header(exchange, outbound)

        receipt = _signal(exchange, received_header, BusinessSignal.Receipt_Acknowledgement, [])
        outcome = _accept(business_log, exchange, receipt)

        assert outcome is None

    def test_no_reference(self, parties:'TestParties', business_log:'BusinessLog') -> 'None':
        exchange = _exchange(parties)
        _ = _send_logged(business_log, exchange)

        binding = resolve(exchange, _response_action, is_reverse=True)
        payload = new_payload()
        message = build(exchange.agreement, exchange.receiver.local_keys, binding, [payload], exchange.clock)

        outcome = _accept(business_log, exchange, message)

        assert outcome is None

# ################################################################################################################################
# ################################################################################################################################

class TestDeadlines:
    """ The deadlines of a business transaction, driven through their expiry by a clock that stands still.
    """

    def test_from_characteristics(self, parties:'TestParties') -> 'None':
        exchange = _exchange(parties)
        binding = resolve(exchange)

        deadlines = business_deadlines(binding, Start_Time)

        receipt_period = timedelta(seconds=_receipt_seconds)
        perform_period = timedelta(seconds=_perform_seconds)

        assert deadlines.receipt == Start_Time + receipt_period
        assert deadlines.response == Start_Time + perform_period

    def test_zero_and_absent(self, parties:'TestParties') -> 'None':
        exchange = _exchange(parties, _zero_duration, '')
        binding = resolve(exchange)

        deadlines = business_deadlines(binding, Start_Time)

        assert deadlines.receipt is None
        assert deadlines.response is None

    def test_receipt_deadline(self, parties:'TestParties', business_log:'BusinessLog') -> 'None':
        exchange = _exchange(parties)
        outbound = _send_logged(business_log, exchange)

        exchange.clock.advance(_receipt_seconds)
        now = exchange.clock.now()

        assert expired(business_log, now) == []

        exchange.clock.advance(_past_deadline_seconds)
        now = exchange.clock.now()

        outcomes = expired(business_log, now)
        outcome = outcomes[0]

        assert len(outcomes) == 1
        assert outcome.message_id == outbound.message_id
        assert outcome.state == BusinessState.Timed_Out

        message = business_log.read(outbound.message_id)

        assert message is not None
        assert message.state == BusinessState.Timed_Out
        assert business_log.awaiting(1) == []

    def test_response_deadline_after_receipt(self, parties:'TestParties', business_log:'BusinessLog') -> 'None':
        exchange = _exchange(parties)
        outbound = _send_logged(business_log, exchange)
        received_header = _received_header(exchange, outbound)

        receipt = _signal(exchange, received_header, BusinessSignal.Receipt_Acknowledgement, [])
        _ = _accept(business_log, exchange, receipt)

        # The receipt arrived, so the passing of its deadline ends nothing ..
        exchange.clock.advance(_receipt_seconds + _past_deadline_seconds)
        now = exchange.clock.now()

        assert expired(business_log, now) == []

        # .. while the passing of the deadline of the response does.
        exchange.clock.advance(_perform_seconds)
        now = exchange.clock.now()

        outcomes = expired(business_log, now)
        outcome = outcomes[0]

        assert outcome.message_id == outbound.message_id
        assert outcome.state == BusinessState.Timed_Out

    def test_zero_receipt_deadline(self, parties:'TestParties', business_log:'BusinessLog') -> 'None':
        exchange = _exchange(parties, _zero_duration, _time_to_perform)
        outbound = _send_logged(business_log, exchange)

        message = business_log.read(outbound.message_id)

        assert message is not None
        assert message.receipt_deadline is None

        # No receipt is awaited, so only the deadline of the response applies.
        exchange.clock.advance(_receipt_seconds + _past_deadline_seconds)
        now = exchange.clock.now()

        assert expired(business_log, now) == []

        exchange.clock.advance(_perform_seconds)
        now = exchange.clock.now()

        outcomes = expired(business_log, now)
        outcome = outcomes[0]

        assert outcome.message_id == outbound.message_id
        assert outcome.state == BusinessState.Timed_Out

    def test_answered_in_time(self, parties:'TestParties', business_log:'BusinessLog') -> 'None':
        exchange = _exchange(parties)
        outbound = _send_logged(business_log, exchange)
        received_header = _received_header(exchange, outbound)

        response = _response(exchange, received_header)
        _ = _accept(business_log, exchange, response)

        exchange.clock.advance(_perform_seconds + _past_deadline_seconds)
        now = exchange.clock.now()

        assert expired(business_log, now) == []
        assert business_log.awaiting(1) == []

    def test_late_signal(self, parties:'TestParties', business_log:'BusinessLog') -> 'None':
        exchange = _exchange(parties)
        outbound = _send_logged(business_log, exchange)
        received_header = _received_header(exchange, outbound)

        exchange.clock.advance(_receipt_seconds + _past_deadline_seconds)

        receipt = _signal(exchange, received_header, BusinessSignal.Receipt_Acknowledgement, [])
        outcome = _accept(business_log, exchange, receipt)

        assert outcome is not None
        assert outcome.state == BusinessState.Timed_Out
        assert outcome.reply_message_id == ''

    def test_no_deadlines(self, parties:'TestParties', business_log:'BusinessLog') -> 'None':
        exchange = _exchange(parties, '', '')
        outbound = _send_logged(business_log, exchange)

        assert business_log.awaiting(1) == []

        message = business_log.read(outbound.message_id)

        assert message is not None
        assert message.state == BusinessState.Sent

# ################################################################################################################################
# ################################################################################################################################
