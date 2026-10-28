# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import INTERNAL_SERVER_ERROR, OK

# Zato
from zato.common.b2b.common.outcome import FinalState, SignalKind
from zato.common.b2b.ebms2.common import ErrorCode, MessageStatus, MSHService, Severity
from zato.common.b2b.ebms2.header import parse_message_header
from zato.common.b2b.ebms2.message import collect_elements, parse_envelope
from zato.common.b2b.ebms2.outbound import accept_response, accept_signal, OutboundState, SendOptions
from zato.common.b2b.ebms2.signals import parse_acknowledgment, parse_error_list
from zato.common.test.b2b_cpa import Sender_Endpoint
from zato.common.test.b2b_ebms2 import answer, confirm, deliver, new_exchange, resolve, send
from zato.common.test.b2b_interoperability import outbound_answered, package_message, read_header, receive_message, \
    reply_elements, settings_for

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.b2b.ebms2.inbound import InboundResult
    from zato.common.b2b.ebms2.message import MessageElements
    from zato.common.b2b.ebms2.outbound import OutboundMessage
    from zato.common.b2b.ebms2.packaging import payload_list
    from zato.common.test.b2b_ebms2 import Exchange
    from zato.common.test.b2b_interoperability import FixtureDirectory
    from zato.common.test.b2b_pki import TestParties
    Exchange = Exchange
    FixtureDirectory = FixtureDirectory
    InboundResult = InboundResult
    MessageElements = MessageElements
    OutboundMessage = OutboundMessage
    payload_list = payload_list
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

# The xml:lang of the Description of an error, without which the error list cannot be read.
_description_language = b' xml:lang="en"'

# The message status of a StatusResponse, and one that ebMS 2.0 does not define.
_processed_status = b'"Processed"'
_undefined_status = b'"Archived"'

# ################################################################################################################################
# ################################################################################################################################

def _elements(data:'bytes') -> 'MessageElements':
    envelope = parse_envelope(data)

    out = collect_elements(envelope)
    return out

# ################################################################################################################################

def _acknowledged_message_id(data:'bytes') -> 'str':
    """ Returns the MessageId that the Acknowledgment of a SOAP part names.
    """
    elements = _elements(data)
    acknowledgment = parse_acknowledgment(elements.acknowledgment)

    out = acknowledgment.ref_to_message_id
    return out

# ################################################################################################################################

def _answered(parties:'TestParties', data:'bytes', message_id:'str', action:'str'='') -> 'tuple[Exchange, OutboundMessage]':
    """ Returns an exchange under which a SOAP part answers a message of the sender, and that message.
    """
    settings = settings_for(parties, data, is_answer=True)
    exchange = new_exchange(parties, settings)
    outbound = outbound_answered(exchange, message_id, action)

    out = (exchange, outbound)
    return out

# ################################################################################################################################

def _accept_signal(
    exchange:'Exchange',
    outbound:'OutboundMessage',
    data:'bytes',
    payloads:'payload_list | None'=None,
    ) -> 'None':
    """ Passes a SOAP part to the sender as a signal that answers its message asynchronously.
    """
    message = package_message(data, payloads)
    _ = accept_signal(outbound, message.headers, message.body, exchange.clock)

# ################################################################################################################################

def _receive(parties:'TestParties', data:'bytes', payloads:'payload_list | None'=None) -> 'InboundResult':
    """ Receives a SOAP part under an agreement whose sender is its From.
    """
    settings = settings_for(parties, data)
    exchange = new_exchange(parties, settings)
    message = package_message(data, payloads)

    out = receive_message(exchange, message)
    return out

# ################################################################################################################################

def _assert_pending(outbound:'OutboundMessage') -> 'None':
    """ A signal that cannot be read leaves the exchange of the message it answers as it was.
    """
    assert outbound.state == OutboundState.Pending
    assert not outbound.retry_state.is_answered

# ################################################################################################################################

def _assert_failed(outbound:'OutboundMessage', error_code:'str') -> 'None':
    assert outbound.state == OutboundState.Failed
    assert outbound.outcome.signal_kind == SignalKind.Error
    assert outbound.outcome.error_code == error_code
    assert outbound.outcome.final_state == FinalState.Failed

# ################################################################################################################################

def _assert_acknowledged(outbound:'OutboundMessage') -> 'None':
    assert outbound.state == OutboundState.Acknowledged
    assert outbound.outcome.signal_kind == SignalKind.Receipt
    assert outbound.outcome.final_state == FinalState.Delivered
    assert outbound.outcome.delivered

# ################################################################################################################################
# ################################################################################################################################

class TestPingAndPong:
    """ Ping, Pong and StatusRequest messages in the forms other message service handlers send them in.
    """

    def _assert_pong(self, result:'InboundResult') -> 'None':
        """ A Ping without eb:SyncReply is answered with a Pong sent asynchronously.
        """
        assert result.outcome.signal_kind == SignalKind.Pong
        assert result.outcome.final_state == FinalState.Answered
        assert result.async_signal is not None
        assert result.async_signal.endpoint == Sender_Endpoint
        assert not result.response.body

        elements = reply_elements(result)
        pong = parse_message_header(elements.message_header)

        assert result.header is not None
        assert pong.action == MSHService.Pong
        assert pong.message_data.ref_to_message_id == result.header.message_data.message_id

    def test_ping_with_two_prefixes_for_soap(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('ping-ack-requested-two-soap-prefixes.xml')
        result = _receive(parties, data)

        self._assert_pong(result)

    def test_ping_with_whitespace_after_declaration(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('ping-whitespace-after-declaration.xml')
        result = _receive(parties, data)

        self._assert_pong(result)

    def test_pong_with_manifest(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('pong-with-manifest.xml')
        header = read_header(data)

        exchange, outbound = _answered(parties, data, header.message_data.ref_to_message_id, MSHService.Ping)
        _accept_signal(exchange, outbound, data)

        assert outbound.state == OutboundState.Answered
        assert outbound.outcome.signal_kind == SignalKind.Pong
        assert outbound.outcome.final_state == FinalState.Answered

    def test_pong_in_the_http_response(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('pong-ref-to-message-id.xml')
        header = read_header(data)

        exchange, outbound = _answered(parties, data, header.message_data.ref_to_message_id, MSHService.Ping)
        message = package_message(data)

        outcome = accept_response(outbound, OK, message.headers, message.body, exchange.clock)

        assert outbound.state == OutboundState.Answered
        assert outcome.signal_kind == SignalKind.Pong

    def _status_request(self, exchange:'Exchange', message_id:'str') -> 'tuple[OutboundMessage, InboundResult]':
        """ Sends a StatusRequest about a message and returns it with the result of its receipt.
        """
        options = SendOptions()
        options.status_request_ref = message_id

        binding = resolve(exchange, MSHService.Status_Request, is_msh=True)
        outbound = send(exchange, [], options, binding)
        result = deliver(exchange, outbound)

        out = (outbound, result)
        return out

    def test_status_of_a_delivered_message(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('ping-whitespace-after-declaration.xml')
        settings = settings_for(parties, data)
        exchange = new_exchange(parties, settings)

        business = send(exchange)
        delivered = deliver(exchange, business)
        confirm(exchange, delivered)

        outbound, result = self._status_request(exchange, business.message_id)
        outcome = answer(exchange, outbound, result)

        assert outcome.signal_kind == SignalKind.Status
        assert outbound.status_response is not None
        assert outbound.status_response.ref_to_message_id == business.message_id
        assert outbound.status_response.message_status == MessageStatus.Processed

    def test_status_of_an_unknown_message(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('ping-whitespace-after-declaration.xml')
        settings = settings_for(parties, data)
        exchange = new_exchange(parties, settings)

        outbound, result = self._status_request(exchange, 'unknown@b2b.test')
        _ = answer(exchange, outbound, result)

        assert outbound.status_response is not None
        assert outbound.status_response.message_status == MessageStatus.Not_Recognized

    def test_undefined_message_status(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('ping-whitespace-after-declaration.xml')
        settings = settings_for(parties, data)
        exchange = new_exchange(parties, settings)

        business = send(exchange)
        delivered = deliver(exchange, business)
        confirm(exchange, delivered)

        outbound, result = self._status_request(exchange, business.message_id)

        assert result.async_signal is not None
        package = result.async_signal.package

        assert _processed_status in package.body
        changed = package.body.replace(_processed_status, _undefined_status, 1)

        _ = accept_signal(outbound, package.headers, changed, exchange.clock)

        assert outbound.status_response is None
        _assert_pending(outbound)

# ################################################################################################################################
# ################################################################################################################################

class TestAcknowledgments:
    """ Acknowledgments in the forms other message service handlers send them in.
    """

    def _acknowledge(self, parties:'TestParties', data:'bytes') -> 'OutboundMessage':
        """ Passes an acknowledgment to the sender of the message it acknowledges, and returns that message.
        """
        message_id = _acknowledged_message_id(data)
        exchange, out = _answered(parties, data, message_id)

        _accept_signal(exchange, out, data)
        return out

    def test_acknowledgment_with_manifest(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('acknowledgment-with-manifest.xml')
        outbound = self._acknowledge(parties, data)

        _assert_acknowledged(outbound)

    def test_plain_acknowledgment(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('acknowledgment-plain.xml')
        outbound = self._acknowledge(parties, data)

        _assert_acknowledged(outbound)
        assert not outbound.outcome.signature_verified

    def test_non_standard_schema_instance_namespace(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('acknowledgment-non-standard-xsi.xml')
        outbound = self._acknowledge(parties, data)

        _assert_acknowledged(outbound)

    def test_two_ref_to_message_ids_and_empty_party(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('acknowledgment-two-ref-to-empty-party.xml')
        agreement_data = messages.load('acknowledgment-plain.xml')

        settings = settings_for(parties, agreement_data)
        exchange = new_exchange(parties, settings)
        message = package_message(data)

        result = receive_message(exchange, message)

        assert result.outcome.error_code == ErrorCode.Inconsistent
        assert result.outcome.final_state == FinalState.Rejected
        assert result.response.status_code == INTERNAL_SERVER_ERROR
        assert b'Fault' in result.response.body

        message_id = _acknowledged_message_id(agreement_data)
        exchange, outbound = _answered(parties, agreement_data, message_id)
        _accept_signal(exchange, outbound, data)

        _assert_pending(outbound)

    def test_must_understand_as_true(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('acknowledgment-redeclared-namespaces.xml')
        result = _receive(parties, data)

        # The MessageHeader can be read, so the error goes back to the sender as an error message.
        assert result.outcome.error_code == ErrorCode.Inconsistent
        assert result.outcome.final_state == FinalState.Rejected

        elements = reply_elements(result)
        error_list = parse_error_list(elements.error_list)

        assert error_list.errors[0].error_code == ErrorCode.Inconsistent

        header = read_header(data)
        exchange, outbound = _answered(parties, data, header.message_data.ref_to_message_id)
        _accept_signal(exchange, outbound, data)

        _assert_pending(outbound)

# ################################################################################################################################
# ################################################################################################################################

class TestErrorMessages:
    """ Error messages in the forms other message service handlers send them in.
    """

    def _report(self, parties:'TestParties', data:'bytes', payloads:'payload_list | None'=None) -> 'OutboundMessage':
        """ Passes an error message to the sender of the message it reports on, and returns that message.
        """
        header = read_header(data)
        exchange, out = _answered(parties, data, header.message_data.ref_to_message_id)

        _accept_signal(exchange, out, data, payloads)
        return out

    def test_extra_namespaces(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('error-list-extra-namespaces.xml')
        outbound = self._report(parties, data)

        _assert_failed(outbound, ErrorCode.Value_Not_Recognized)
        assert outbound.outcome.error_severity == Severity.Error

    def test_error_message_that_cannot_be_read(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('error-list-extra-namespaces.xml')

        assert _description_language in data
        changed = data.replace(_description_language, b'', 1)

        result = _receive(parties, changed)

        # An error message that reports errors is never answered with another error message.
        assert result.outcome.error_code == ErrorCode.Inconsistent
        assert result.outcome.final_state == FinalState.Rejected
        assert result.async_signal is None
        assert not result.response.body

        outbound = self._report(parties, changed)
        _assert_pending(outbound)

    def test_several_errors_with_code_context(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('error-list-several-code-context.xml')
        outbound = self._report(parties, data)

        elements = _elements(data)
        error_list = parse_error_list(elements.error_list)
        first, second = error_list.errors

        _assert_failed(outbound, ErrorCode.Value_Not_Recognized)
        assert first.code_context == 'urn:oasis:names:tc:ebxml-msg:service:errors'
        assert second.code_context == 'urn:oasis:names:tc:ebxml-msg:service:errors'
        assert first.description == '501319:Unknown eb:CPAId'
        assert second.description == '501320:Unknown eb:Service'

    def test_xpointer_location(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('error-list-xpointer-location.xml')
        outbound = self._report(parties, data)

        elements = _elements(data)
        error_list = parse_error_list(elements.error_list)

        _assert_failed(outbound, ErrorCode.Value_Not_Recognized)
        assert error_list.errors[0].location == 'xpointer(//MessageHeader/CpaId)'

    def test_unprefixed_attributes(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('error-list-unprefixed-attributes.xml')
        result = _receive(parties, data, [])

        # All of the errors it reports are warnings, so the error message is answered with one of its own.
        assert result.outcome.error_code == ErrorCode.Inconsistent
        assert result.outcome.final_state == FinalState.Rejected

        elements = reply_elements(result)
        error_list = parse_error_list(elements.error_list)

        assert error_list.errors[0].error_code == ErrorCode.Inconsistent

    def test_delivery_failure(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('error-delivery-failure.xml')
        outbound = self._report(parties, data)

        _assert_failed(outbound, ErrorCode.Delivery_Failure)

    def test_unauthorized_sender(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('error-security-failure-unauthorized.xml')
        outbound = self._report(parties, data)

        _assert_failed(outbound, ErrorCode.Security_Failure)

    def test_failed_security_checks(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('error-security-failure-checks.xml')
        outbound = self._report(parties, data)

        _assert_failed(outbound, ErrorCode.Security_Failure)

# ################################################################################################################################
# ################################################################################################################################
