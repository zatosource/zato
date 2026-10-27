# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re
from datetime import datetime, timedelta, timezone
from http.client import SERVICE_UNAVAILABLE

# lxml
from lxml.etree import fromstring, SubElement, tostring

# pytest
import pytest

# Zato
from zato.common.b2b.common.keys import LocalKeys
from zato.common.b2b.common.outcome import FinalState, SignalKind
from zato.common.b2b.common.retry import RetryAction
from zato.common.b2b.ebms2.common import Actor, Direction, EbMS2Exception, ErrorCode, MSHService, new_party_id
from zato.common.b2b.ebms2.header import parse_manifest, parse_message_header
from zato.common.b2b.ebms2.inbound import receive
from zato.common.b2b.ebms2.message import collect_elements, parse_envelope, serialize
from zato.common.b2b.ebms2.outbound import accept_response, build, next_action, OutboundState, record_resend, SendOptions
from zato.common.b2b.ebms2.packaging import package, unpack
from zato.common.b2b.ebms2.xml_ import SOAP_Actor
from zato.common.test.b2b_cpa import Default_Action, Default_Service, new_settings, Receiver_Endpoint, Sender_Endpoint, \
    ServiceSettings
from zato.common.test.b2b_ebms2 import answer, deliver, new_exchange, new_local_keys, new_payload, resolve, send, Start_Time
from zato.common.test.b2b_interoperability import reply_elements
from zato.common.test.b2b_pki import ca_party, issue_party, make_certificate, make_key, TestParties, TestParty

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.b2b.ebms2.agreement import Binding
    from zato.common.b2b.ebms2.inbound import InboundResult
    from zato.common.b2b.ebms2.outbound import OutboundMessage
    from zato.common.b2b.ebms2.packaging import payload_list
    from zato.common.test.b2b_cpa import AgreementSettings
    from zato.common.test.b2b_ebms2 import Exchange
    from zato.common.typing_ import any_
    any_ = any_
    AgreementSettings = AgreementSettings
    Binding = Binding
    Exchange = Exchange
    InboundResult = InboundResult
    OutboundMessage = OutboundMessage
    payload_list = payload_list

# ################################################################################################################################
# ################################################################################################################################

# A purchase order in a document format of the tests.
_purchase_order_line = b'<Line><Item>b2b-item-1</Item><Quantity>4</Quantity></Line>'
_purchase_order = b'<PurchaseOrder xmlns="urn:zato:b2b:test:orders:v1"><Number>PO-0001</Number>' + _purchase_order_line + \
    b'</PurchaseOrder>'

# Binary payloads with every byte value in them, which no transfer encoding may alter.
_byte_values = range(256)
_all_bytes = bytes(_byte_values)
_reversed_bytes = _all_bytes[::-1]

_image_data = b'\x89PNG\r\n\x1a\n' + _all_bytes
_pdf_data = b'%PDF-1.4\n' + _reversed_bytes + b'\n%%EOF\n'

_image_content_type = 'image/png'
_pdf_content_type = 'application/pdf'

# The service types of two versions of one service that are both in effect.
_first_version = 'v1'
_second_version = 'v2'

# The action that a receiver answers a request with.
_response_action = 'Respond'

# The CPAId of an agreement the receiver does not have.
_other_cpa_id = 'b2b-other-agreement'

# A header block that an intermediary adds for the next message service handler.
_hop_tag = '{urn:zato:b2b:test:extension}Hop'

# The form of an XML name without a colon, which eb:id is to have.
_ncname_pattern = re.compile(r'^[A-Za-z_][\w.-]*$')

# The days around the current moment that a dated certificate is valid for.
_expired_days_before = 730
_expired_days_after = -1
_valid_days = 30

# What a message names its parties, its agreement, its service and its action with, what replaces each one,
# and the error the receiver reports.
_header_mismatches = {
    'from':    (b'>b2b-sender<', b'>b2b-unknown-sender<', ErrorCode.Value_Not_Recognized),
    'to':      (b'>b2b-receiver<', b'>b2b-unknown-receiver<', ErrorCode.Value_Not_Recognized),
    'service': (b'>urn:zato:b2b:test:orders<', b'>urn:zato:b2b:test:unknown<', ErrorCode.Value_Not_Recognized),
    'action':  (b'>Submit<', b'>Unknown<', ErrorCode.Not_Supported),
    'cpa_id':  (b'>b2b-test-agreement<', b'>b2b-unknown-agreement<', ErrorCode.Value_Not_Recognized),
}

_header_mismatch_fields = sorted(_header_mismatches)

# ################################################################################################################################
# ################################################################################################################################

def _unsigned(parties:'TestParties') -> 'AgreementSettings':
    out = new_settings(parties, Start_Time)
    out.is_signed = False

    return out

# ################################################################################################################################

def _with_sender(parties:'TestParties', sender:'TestParty') -> 'TestParties':
    """ Returns the test parties with another sender in place of the usual one.
    """
    out = TestParties()
    out.ca_key = parties.ca_key
    out.ca_certificate = parties.ca_certificate
    out.sender = sender
    out.receiver = parties.receiver

    return out

# ################################################################################################################################

def _dated_sender(parties:'TestParties', days_before:'int', days_after:'int') -> 'TestParty':
    """ Returns a sender whose certificate the CA of the tests issued for the given days around the current moment,
    which is the moment certificate chains are validated at.
    """
    key = make_key()
    public_key = key.public_key()
    ca_name = parties.ca_certificate.subject
    now = datetime.now(timezone.utc)

    not_before = now - timedelta(days=days_before)
    not_after = now + timedelta(days=days_after)

    out = TestParty()
    out.key = key
    out.certificate = make_certificate('b2b-sender', public_key, ca_name, parties.ca_key,
        not_before=not_before, not_after=not_after)

    return out

# ################################################################################################################################

def _reverse_exchange(parties:'TestParties') -> 'Exchange':
    """ Returns an exchange in which the receiver answers each request of the sender with a business response.
    """
    response_service = ServiceSettings()
    response_service.service = Default_Service
    response_service.action = _response_action

    settings = _unsigned(parties)
    settings.extra_services.append(response_service)
    settings.sender.can_receive = True
    settings.receiver.can_send = True

    out = new_exchange(parties, settings)
    return out

# ################################################################################################################################

def _respond(exchange:'Exchange', request:'OutboundMessage') -> 'InboundResult':
    """ Builds the business response of the receiver to a request and passes it to the sender.
    """
    options = SendOptions()
    options.conversation_id = request.header.conversation_id
    options.ref_to_message_id = request.message_id

    binding = resolve(exchange, _response_action, is_reverse=True)
    payloads = [new_payload()]

    receiver = exchange.receiver
    sender = exchange.sender

    response = build(exchange.agreement, receiver.local_keys, binding, payloads, exchange.clock, options)
    wire = response.package

    out = receive(exchange.agreement, sender.local_keys, wire.headers, wire.body, sender.store, exchange.clock)
    return out

# ################################################################################################################################

def _resolve_version(exchange:'Exchange', service_type:'str') -> 'Binding':
    """ Returns the binding of the default action of the default service under one of its service types.
    """
    sender_settings = exchange.sender.settings
    receiver_settings = exchange.receiver.settings

    from_party_id = new_party_id(sender_settings.party_id, sender_settings.party_id_type)
    to_party_id = new_party_id(receiver_settings.party_id, receiver_settings.party_id_type)

    out = exchange.agreement.resolve([from_party_id], [to_party_id], Default_Service, service_type, Default_Action,
        Direction.Send)
    return out

# ################################################################################################################################

def _deliver_changed(exchange:'Exchange', outbound:'OutboundMessage', envelope:'any_', payloads:'payload_list') \
    -> 'InboundResult':
    """ Passes a message to the receiver with its envelope changed after it was built.
    """
    data = serialize(envelope)
    wire = package(data, payloads)
    receiver = exchange.receiver

    out = receive(exchange.agreement, receiver.local_keys, wire.headers, wire.body, receiver.store, exchange.clock)
    return out

# ################################################################################################################################

def _assert_delivered(result:'InboundResult') -> 'None':
    assert result.outcome.delivered
    assert result.outcome.final_state == FinalState.Delivered
    assert len(result.deliveries) == 1

# ################################################################################################################################

def _assert_rejected(result:'InboundResult', error_code:'str') -> 'None':
    assert result.outcome.error_code == error_code
    assert result.outcome.final_state == FinalState.Rejected
    assert not result.deliveries

# ################################################################################################################################
# ################################################################################################################################

class TestConversations:
    """ Requests, their acknowledgments and their responses, correlated by ConversationId and RefToMessageId.
    """

    def test_response_routed_by_conversation(self, parties:'TestParties') -> 'None':
        exchange = _reverse_exchange(parties)

        request = send(exchange)
        request_result = deliver(exchange, request)

        elements = reply_elements(request_result)
        acknowledgment_header = parse_message_header(elements.message_header)

        response_result = _respond(exchange, request)
        _assert_delivered(response_result)

        response = response_result.deliveries[0]

        assert acknowledgment_header.conversation_id == request.header.conversation_id
        assert response.conversation_id == request.header.conversation_id
        assert response.ref_to_message_id == request.message_id
        assert response.action == _response_action

    def test_custom_document_exchange(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        payload = new_payload(_purchase_order)
        outbound = send(exchange, [payload])

        result = deliver(exchange, outbound)
        outcome = answer(exchange, outbound, result)

        _assert_delivered(result)
        assert result.deliveries[0].payloads[0].data == _purchase_order
        assert outbound.state == OutboundState.Acknowledged
        assert outcome.signal_kind == SignalKind.Receipt

    def test_correlation_properties(self, parties:'TestParties') -> 'None':
        settings = _unsigned(parties)
        exchange = new_exchange(parties, settings)

        options = SendOptions()
        options.conversation_id = 'b2b-conversation-0001'
        options.ref_to_message_id = 'b2b-earlier-message@b2b.test'

        outbound = send(exchange, None, options)
        result = deliver(exchange, outbound)

        _assert_delivered(result)
        delivery = result.deliveries[0]

        assert delivery.conversation_id == options.conversation_id
        assert delivery.ref_to_message_id == options.ref_to_message_id
        assert delivery.message_id == outbound.message_id

    def test_duplicate_elimination(self, parties:'TestParties') -> 'None':
        settings = _unsigned(parties)
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)

        first = deliver(exchange, outbound)
        second = deliver(exchange, outbound)

        _assert_delivered(first)

        assert first.async_signal is not None
        assert second.async_signal is not None
        assert second.outcome.duplicate
        assert not second.deliveries
        assert second.async_signal.package.body == first.async_signal.package.body

# ################################################################################################################################
# ################################################################################################################################

class TestAgreementIdentification:
    """ A message is accepted only under an agreement that names its parties, its service and its action.
    """

    def test_unknown_agreement(self, parties:'TestParties') -> 'None':
        settings = _unsigned(parties)
        exchange = new_exchange(parties, settings)

        other_settings = _unsigned(parties)
        other_settings.cpa_id = _other_cpa_id
        other_exchange = new_exchange(parties, other_settings)

        outbound = send(other_exchange)
        result = deliver(exchange, outbound)

        _assert_rejected(result, ErrorCode.Value_Not_Recognized)

    @pytest.mark.parametrize('field', _header_mismatch_fields)
    def test_header_mismatch(self, parties:'TestParties', field:'str') -> 'None':
        settings = _unsigned(parties)
        exchange = new_exchange(parties, settings)

        current, changed, error_code = _header_mismatches[field]

        outbound = send(exchange)
        body = outbound.package.body

        assert current in body
        changed_body = body.replace(current, changed, 1)

        result = deliver(exchange, outbound, changed_body)
        _assert_rejected(result, error_code)

    def test_service_versions(self, parties:'TestParties') -> 'None':
        second_version = ServiceSettings()
        second_version.service = Default_Service
        second_version.service_type = _second_version
        second_version.action = Default_Action

        settings = _unsigned(parties)
        settings.service_type = _first_version
        settings.extra_services.append(second_version)

        exchange = new_exchange(parties, settings)

        first_binding = _resolve_version(exchange, _first_version)
        second_binding = _resolve_version(exchange, _second_version)

        assert first_binding.send_binding is not second_binding.send_binding

        first_outbound = send(exchange, None, None, first_binding)
        second_outbound = send(exchange, None, None, second_binding)

        first_result = deliver(exchange, first_outbound)
        second_result = deliver(exchange, second_outbound)

        _assert_delivered(first_result)
        _assert_delivered(second_result)

        assert first_result.deliveries[0].service_type == _first_version
        assert second_result.deliveries[0].service_type == _second_version

    def test_undefined_action(self, parties:'TestParties') -> 'None':
        settings = _unsigned(parties)
        exchange = new_exchange(parties, settings)

        with pytest.raises(EbMS2Exception) as info:
            _ = resolve(exchange, 'Undefined')

        assert info.value.error_code == ErrorCode.Not_Supported

# ################################################################################################################################
# ################################################################################################################################

class TestOutboundMessages:
    """ Outgoing messages as the agreement describes them, and as they are sent again.
    """

    def test_manifest_identifiers(self, parties:'TestParties', msg_header_schema:'any_') -> 'None':
        settings = _unsigned(parties)
        exchange = new_exchange(parties, settings)

        # A Content-ID that starts with a digit is not an NCName, so it cannot serve as an eb:id as it is.
        first_payload = new_payload(content_id='b2b-part-1@b2b.test')
        second_payload = new_payload(content_id='2-b2b-part@b2b.test')

        outbound = send(exchange, [first_payload, second_payload])

        unpacked = unpack(outbound.package.headers, outbound.package.body)
        envelope = parse_envelope(unpacked.envelope)
        elements = collect_elements(envelope)
        manifest = parse_manifest(elements.manifest)

        standalone_data = tostring(elements.manifest)
        standalone = fromstring(standalone_data)

        assert len(manifest.references) == 2
        assert msg_header_schema.validate(standalone)

        for reference in manifest.references:
            if reference.reference_id:
                assert _ncname_pattern.match(reference.reference_id), reference.reference_id

    def test_retransmission_identity(self, parties:'TestParties') -> 'None':
        settings = _unsigned(parties)
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)
        sent_body = outbound.package.body

        _ = accept_response(outbound, SERVICE_UNAVAILABLE, {}, b'', exchange.clock)

        decision = next_action(outbound, exchange.clock)
        retry_after = decision.at - exchange.clock.now()
        retry_after_seconds = retry_after.total_seconds()
        exchange.clock.advance(retry_after_seconds)

        decision = next_action(outbound, exchange.clock)
        assert decision.action == RetryAction.Resend

        record_resend(outbound, exchange.clock)
        result = deliver(exchange, outbound)

        _assert_delivered(result)
        assert outbound.package.body == sent_body
        assert result.deliveries[0].message_id == outbound.message_id
        assert outbound.retry_state.attempt_count == 2

    def test_signing_without_a_key(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)
        exchange.sender.local_keys = LocalKeys()

        with pytest.raises(EbMS2Exception) as info:
            _ = send(exchange)

        assert info.value.error_code == ErrorCode.Not_Supported

    def test_ping_and_pong_endpoints(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        binding = resolve(exchange, MSHService.Ping, is_msh=True)
        ping = send(exchange, [], None, binding)
        result = deliver(exchange, ping)

        assert ping.endpoint == Receiver_Endpoint
        assert result.async_signal is not None
        assert result.async_signal.endpoint == Sender_Endpoint

        elements = reply_elements(result)
        pong = parse_message_header(elements.message_header)

        assert pong.action == MSHService.Pong
        assert pong.message_data.ref_to_message_id == ping.message_id

        outcome = answer(exchange, ping, result)

        assert ping.state == OutboundState.Answered
        assert outcome.signal_kind == SignalKind.Pong

# ################################################################################################################################
# ################################################################################################################################

class TestSignatures:
    """ Signed messages from the senders, the certificates and the intermediaries that deployments encounter.
    """

    def test_key_outside_the_agreement(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        ca = ca_party(parties)
        other_sender = issue_party('b2b-sender', ca)
        exchange.sender.local_keys = new_local_keys(other_sender)

        outbound = send(exchange)
        result = deliver(exchange, outbound)

        _assert_rejected(result, ErrorCode.Security_Failure)

    def test_unsigned_message_under_a_signing_agreement(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        unsigned_settings = _unsigned(parties)
        unsigned_exchange = new_exchange(parties, unsigned_settings)

        outbound = send(unsigned_exchange)
        result = deliver(exchange, outbound)

        _assert_rejected(result, ErrorCode.Security_Failure)

    def test_intermediary_blocks(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)

        unpacked = unpack(outbound.package.headers, outbound.package.body)
        envelope = parse_envelope(unpacked.envelope)
        elements = collect_elements(envelope)

        soap_header = elements.message_header.getparent()
        block = SubElement(soap_header, _hop_tag)
        block.set(SOAP_Actor, Actor.Next_MSH)
        block.text = 'b2b-relay-1'

        result = _deliver_changed(exchange, outbound, envelope, unpacked.payloads)

        _assert_delivered(result)
        assert result.outcome.signature_verified

    def test_binary_attachments(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        document = new_payload()

        image = new_payload(_image_data)
        image.content_type = _image_content_type

        pdf = new_payload(_pdf_data)
        pdf.content_type = _pdf_content_type

        outbound = send(exchange, [document, image, pdf])
        result = deliver(exchange, outbound)

        _assert_delivered(result)
        assert result.outcome.signature_verified

        received_document, received_image, received_pdf = result.deliveries[0].payloads

        assert received_document.data == document.data
        assert received_image.data == _image_data
        assert received_pdf.data == _pdf_data

    def test_certificate_in_effect(self, parties:'TestParties') -> 'None':
        sender = _dated_sender(parties, _valid_days, _valid_days)
        signing_parties = _with_sender(parties, sender)

        settings = new_settings(signing_parties, Start_Time)
        exchange = new_exchange(signing_parties, settings)

        outbound = send(exchange)
        result = deliver(exchange, outbound)

        _assert_delivered(result)
        assert result.outcome.signature_verified

    def test_expired_certificate(self, parties:'TestParties') -> 'None':
        sender = _dated_sender(parties, _expired_days_before, _expired_days_after)
        signing_parties = _with_sender(parties, sender)

        settings = new_settings(signing_parties, Start_Time)
        exchange = new_exchange(signing_parties, settings)

        outbound = send(exchange)
        result = deliver(exchange, outbound)

        _assert_rejected(result, ErrorCode.Security_Failure)

# ################################################################################################################################
# ################################################################################################################################
