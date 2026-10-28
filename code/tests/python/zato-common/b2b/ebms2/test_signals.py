# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# lxml
from lxml.etree import fromstring, tostring

# Zato
from zato.common.b2b.common.outcome import FinalState, SignalKind
from zato.common.b2b.ebms2.common import Actor, ErrorCode, MessageStatus, MSHService, new_party_id, Severity
from zato.common.b2b.ebms2.header import HeaderParty
from zato.common.b2b.ebms2.message import new_envelope, parse_envelope, serialize
from zato.common.b2b.ebms2.outbound import OutboundState, SendOptions
from zato.common.b2b.ebms2.signals import Acknowledgment, add_acknowledgment, add_error_list, add_status_request, \
    add_status_response, MessageError, new_error_list, parse_acknowledgment, parse_error_list, parse_status_request, \
    parse_status_response, StatusRequest, StatusResponse
from zato.common.b2b.ebms2.xml_ import eb_tag
from zato.common.test.b2b_cpa import new_settings, Party_Id_Type, Receiver_Name, Sender_Endpoint
from zato.common.test.b2b_ebms2 import answer, confirm, deliver, new_exchange, resolve, send, Start_Time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.b2b_ebms2 import Exchange
    from zato.common.test.b2b_pki import TestParties
    from zato.common.typing_ import any_
    Exchange = Exchange
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

_message_id = 'b2b-message-1@b2b.test'

_acknowledgment_path = './/' + eb_tag('Acknowledgment')
_error_list_path = './/' + eb_tag('ErrorList')
_status_request_path = './/' + eb_tag('StatusRequest')
_status_response_path = './/' + eb_tag('StatusResponse')

# ################################################################################################################################
# ################################################################################################################################

def _reparse(envelope:'any_') -> 'any_':
    """ Serializes and parses an envelope again, the way it travels.
    """
    data = serialize(envelope)

    out = parse_envelope(data)
    return out

# ################################################################################################################################

def _standalone(element:'any_') -> 'any_':
    """ Returns a copy of an element as the root of a document of its own.
    """
    data = tostring(element)

    out = fromstring(data)
    return out

# ################################################################################################################################

def _ping(exchange:'Exchange', action:'str'=MSHService.Ping, options:'SendOptions | None'=None) -> 'any_':
    binding = resolve(exchange, action, is_msh=True)

    out = send(exchange, [], options, binding)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSignalElements:
    """ The ebMS 2.0 signal elements, built and read back.
    """

    def test_acknowledgment(self, msg_header_schema:'any_') -> 'None':
        party_id = new_party_id(Receiver_Name, Party_Id_Type)

        from_party = HeaderParty()
        from_party.party_ids = [party_id]

        acknowledgment = Acknowledgment()
        acknowledgment.timestamp = Start_Time
        acknowledgment.ref_to_message_id = _message_id
        acknowledgment.from_party = from_party

        envelope, soap_header, _ = new_envelope()
        add_acknowledgment(soap_header, acknowledgment)

        envelope = _reparse(envelope)
        element = envelope.find(_acknowledgment_path)

        document = _standalone(element)
        msg_header_schema.assertValid(document)

        parsed = parse_acknowledgment(element)

        assert parsed.timestamp == Start_Time
        assert parsed.ref_to_message_id == _message_id
        assert parsed.actor == Actor.To_Party_MSH
        assert parsed.from_party is not None
        assert parsed.from_party.party_ids[0].value == Receiver_Name
        assert parsed.references == []

    def test_error_list(self, msg_header_schema:'any_') -> 'None':
        error_list = new_error_list(ErrorCode.Value_Not_Recognized, 'Unknown CPAId', 'eb:CPAId')

        envelope, soap_header, _ = new_envelope()
        add_error_list(soap_header, error_list)

        envelope = _reparse(envelope)
        element = envelope.find(_error_list_path)

        document = _standalone(element)
        msg_header_schema.assertValid(document)

        parsed = parse_error_list(element)
        error = parsed.errors[0]

        assert len(parsed.errors) == 1
        assert parsed.highest_severity == Severity.Error
        assert error.error_code == ErrorCode.Value_Not_Recognized
        assert error.severity == Severity.Error
        assert error.location == 'eb:CPAId'
        assert error.description == 'Unknown CPAId'

    def test_warnings_only(self) -> 'None':
        error_list = new_error_list(ErrorCode.Unknown, 'Advisory', severity=Severity.Warning)

        warning = MessageError()
        warning.error_code = ErrorCode.Inconsistent
        warning.severity = Severity.Warning
        error_list.errors.append(warning)

        envelope, soap_header, _ = new_envelope()
        add_error_list(soap_header, error_list)

        envelope = _reparse(envelope)
        element = envelope.find(_error_list_path)
        parsed = parse_error_list(element)

        assert len(parsed.errors) == 2
        assert parsed.highest_severity == Severity.Warning

    def test_status_request_and_response(self, msg_header_schema:'any_') -> 'None':
        status_request = StatusRequest()
        status_request.ref_to_message_id = _message_id

        status_response = StatusResponse()
        status_response.ref_to_message_id = _message_id
        status_response.message_status = MessageStatus.Processed
        status_response.timestamp = Start_Time

        envelope, _, soap_body = new_envelope()
        add_status_request(soap_body, status_request)
        add_status_response(soap_body, status_response)

        envelope = _reparse(envelope)
        request_element = envelope.find(_status_request_path)
        response_element = envelope.find(_status_response_path)

        request_document = _standalone(request_element)
        response_document = _standalone(response_element)

        msg_header_schema.assertValid(request_document)
        msg_header_schema.assertValid(response_document)

        parsed_request = parse_status_request(request_element)
        parsed_response = parse_status_response(response_element)

        assert parsed_request.ref_to_message_id == _message_id
        assert parsed_response.ref_to_message_id == _message_id
        assert parsed_response.message_status == MessageStatus.Processed
        assert parsed_response.timestamp == Start_Time

# ################################################################################################################################
# ################################################################################################################################

class TestMessageServiceHandler:
    """ Ping and Pong, and StatusRequest and StatusResponse, exchanged between the two parties.
    """

    def test_ping_is_answered_with_pong(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        outbound = _ping(exchange)
        result = deliver(exchange, outbound)

        assert not outbound.is_ack_requested
        assert not outbound.is_sync_reply
        assert result.outcome.signal_kind == SignalKind.Pong
        assert result.outcome.final_state == FinalState.Answered
        assert result.async_signal is not None
        assert result.async_signal.endpoint == Sender_Endpoint
        assert not result.response.body

        outcome = answer(exchange, outbound, result)

        assert outbound.state == OutboundState.Answered
        assert outcome.signal_kind == SignalKind.Pong
        assert outcome.final_state == FinalState.Answered

    def test_status_of_a_delivered_message(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        business = send(exchange)
        delivered = deliver(exchange, business)
        confirm(exchange, delivered)

        options = SendOptions()
        options.status_request_ref = business.message_id

        outbound = _ping(exchange, MSHService.Status_Request, options)
        result = deliver(exchange, outbound)
        outcome = answer(exchange, outbound, result)

        assert outcome.signal_kind == SignalKind.Status
        assert outbound.status_response is not None
        assert outbound.status_response.ref_to_message_id == business.message_id
        assert outbound.status_response.message_status == MessageStatus.Processed
        assert outbound.status_response.timestamp == Start_Time

    def test_status_of_an_unknown_message(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        options = SendOptions()
        options.status_request_ref = _message_id

        outbound = _ping(exchange, MSHService.Status_Request, options)
        result = deliver(exchange, outbound)
        _ = answer(exchange, outbound, result)

        assert outbound.status_response is not None
        assert outbound.status_response.message_status == MessageStatus.Not_Recognized
        assert outbound.status_response.timestamp is None

    def test_unknown_action_of_the_service(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        outbound = _ping(exchange, 'Unknown')
        result = deliver(exchange, outbound)

        assert result.outcome.error_code == ErrorCode.Not_Supported
        assert result.outcome.final_state == FinalState.Rejected

# ################################################################################################################################
# ################################################################################################################################
