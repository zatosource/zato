# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import INTERNAL_SERVER_ERROR, OK

# Zato
from zato.common.b2b.common.outcome import FinalState, SignalKind
from zato.common.b2b.ebms2.common import Actor, ErrorCode, PerMessage
from zato.common.b2b.ebms2.header import parse_manifest, parse_message_header
from zato.common.b2b.ebms2.message import collect_elements, parse_envelope
from zato.common.b2b.ebms2.outbound import build, SendOptions
from zato.common.b2b.ebms2.packaging import unpack
from zato.common.b2b.ebms2.signals import parse_acknowledgment
from zato.common.b2b.ebms2.signature import verify_envelope
from zato.common.test.b2b_cpa import Receiver_Name, Sender_Endpoint, Sender_Name, ServiceSettings
from zato.common.test.b2b_ebms2 import deliver, new_exchange, new_payload, resolve, send
from zato.common.test.b2b_interoperability import package_message, read_header, receive_message, reply_elements, \
    settings_for

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.b2b.ebms2.inbound import InboundResult
    from zato.common.b2b.ebms2.inbound_common import Delivery
    from zato.common.test.b2b_cpa import AgreementSettings
    from zato.common.test.b2b_ebms2 import Exchange
    from zato.common.test.b2b_interoperability import FixtureDirectory
    from zato.common.test.b2b_pki import TestParties
    from zato.common.typing_ import strlist
    AgreementSettings = AgreementSettings
    Delivery = Delivery
    Exchange = Exchange
    FixtureDirectory = FixtureDirectory
    InboundResult = InboundResult
    strlist = strlist
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

# The SOAP envelope namespace without its trailing slash, which some senders bind their prefix to.
_soap_namespace_declaration = b'xmlns:SOAP="http://schemas.xmlsoap.org/soap/envelope/"'
_soap_namespace_without_slash = b'xmlns:SOAP="http://schemas.xmlsoap.org/soap/envelope"'

# The content of the file a file transfer sends.
_file_content_id = 'file-0001@b2b.test'
_file_data = b'<File xmlns="urn:zato:b2b:test:files"><Name>transfer.xml</Name></File>'

# ################################################################################################################################
# ################################################################################################################################

def _exchange(parties:'TestParties', data:'bytes', settings:'AgreementSettings | None'=None) -> 'Exchange':
    """ Returns an exchange under an agreement whose sender is the From of a SOAP part.
    """
    if settings is None:
        settings = settings_for(parties, data)

    out = new_exchange(parties, settings)
    return out

# ################################################################################################################################

def _receive(messages:'FixtureDirectory', parties:'TestParties', name:'str') -> 'InboundResult':
    """ Receives a fixture with the payloads its manifest names, under an agreement derived from it.
    """
    data = messages.load(name)
    exchange = _exchange(parties, data)
    message = package_message(data)

    out = receive_message(exchange, message)
    return out

# ################################################################################################################################

def _delivered(result:'InboundResult') -> 'Delivery':
    """ Returns the one delivery of a message that was delivered.
    """
    assert result.outcome.delivered
    assert result.outcome.final_state == FinalState.Delivered
    assert len(result.deliveries) == 1

    out = result.deliveries[0]
    return out

# ################################################################################################################################

def _content_ids(delivery:'Delivery') -> 'strlist':
    out:'strlist' = []

    for payload in delivery.payloads:
        out.append(payload.content_id)

    return out

# ################################################################################################################################

def _assert_rejected(result:'InboundResult', error_code:'str') -> 'None':
    assert result.outcome.error_code == error_code
    assert result.outcome.signal_kind == SignalKind.Error
    assert result.outcome.final_state == FinalState.Rejected
    assert not result.deliveries

# ################################################################################################################################

def _assert_fault(result:'InboundResult', error_code:'str') -> 'None':
    """ A message whose MessageHeader cannot be read is answered with a SOAP Fault.
    """
    _assert_rejected(result, error_code)

    assert result.response.status_code == INTERNAL_SERVER_ERROR
    assert b'Fault' in result.response.body

# ################################################################################################################################

def _assert_asynchronous_acknowledgment(result:'InboundResult', actor:'str'=Actor.To_Party_MSH) -> 'None':
    """ The agreements derived from the fixtures have no synchronous replies, so a message without eb:SyncReply
    is acknowledged asynchronously, with the actor its eb:AckRequested names.
    """
    assert result.async_signal is not None
    assert result.async_signal.endpoint == Sender_Endpoint
    assert result.outcome.signal_kind == SignalKind.Receipt

    elements = reply_elements(result)
    acknowledgment = parse_acknowledgment(elements.acknowledgment)

    assert result.header is not None
    assert acknowledgment.ref_to_message_id == result.header.message_data.message_id
    assert acknowledgment.actor == actor

# ################################################################################################################################

def _assert_synchronous_acknowledgment(result:'InboundResult') -> 'None':
    assert result.async_signal is None
    assert result.response.status_code == OK
    assert b'Acknowledgment' in result.response.body
    assert result.outcome.signal_kind == SignalKind.Receipt

# ################################################################################################################################
# ################################################################################################################################

class TestRequests:
    """ Business messages in the forms that other message service handlers send them in.
    """

    def test_free_form_party_type(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        result = _receive(messages, parties, 'request-default-service-free-type.xml')
        delivery = _delivered(result)

        assert delivery.service == 'genericservice'
        assert delivery.service_type == 'string'
        assert delivery.action == 'genericaction'
        assert delivery.from_party == Sender_Name
        assert delivery.to_party == Receiver_Name
        assert _content_ids(delivery) == ['records/batch/RecordBatch.xml@node0093.b2b.test']

        _assert_asynchronous_acknowledgment(result)

    def test_sync_reply_with_typed_service(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        result = _receive(messages, parties, 'request-sync-reply-typed-service.xml')
        delivery = _delivered(result)

        assert delivery.service_type == 'string'
        _assert_synchronous_acknowledgment(result)

    def test_url_service_before_time_to_live(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        result = _receive(messages, parties, 'request-url-service-time-to-live.xml')
        delivery = _delivered(result)

        assert delivery.service == 'http://b2b.test/ebms/inbound'
        assert not delivery.service_type
        assert _content_ids(delivery) == ['Payload-0']

    def test_url_service_after_time_to_live(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('request-url-service-time-to-live.xml')
        exchange = _exchange(parties, data)
        message = package_message(data)

        exchange.clock.advance(1)
        result = receive_message(exchange, message)

        _assert_rejected(result, ErrorCode.Time_To_Live_Expired)
        assert result.async_signal is not None
        assert b'TimeToLiveExpired' in result.async_signal.package.body

    def test_no_manifest(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('request-no-manifest-duplicate-elimination.xml')
        exchange = _exchange(parties, data)
        message = package_message(data)

        result = receive_message(exchange, message)
        delivery = _delivered(result)

        assert delivery.payloads == []
        assert not result.outcome.signature_verified
        _assert_synchronous_acknowledgment(result)

        duplicate = receive_message(exchange, message)

        assert duplicate.outcome.duplicate
        assert not duplicate.deliveries
        assert duplicate.response.body == result.response.body

    def test_unknown_elements_in_the_body(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        result = _receive(messages, parties, 'request-unknown-eb-body-elements.xml')

        _assert_rejected(result, ErrorCode.Not_Supported)

        # The message is rejected before its binding is resolved, so the error message goes back on the same connection.
        assert result.async_signal is None
        assert b'NotSupported' in result.response.body

    def test_message_header_in_another_namespace(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('request-unknown-eb-body-elements.xml')
        exchange = _exchange(parties, data)

        changed = data.replace(_soap_namespace_declaration, _soap_namespace_without_slash, 1)
        message = package_message(changed)

        result = receive_message(exchange, message)
        _assert_fault(result, ErrorCode.Inconsistent)

    def test_signed_acknowledgment_requested(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('request-numeric-party-type-signed-ack.xml')

        settings = settings_for(parties, data)
        settings.business_channel.ack_signature_requested = PerMessage.Per_Message

        exchange = _exchange(parties, data, settings)
        message = package_message(data)

        result = receive_message(exchange, message)
        delivery = _delivered(result)

        elements = reply_elements(result)
        verified = verify_envelope(elements.envelope, elements.signature, [], parties.receiver.certificate)

        assert delivery.service == 'http://example.com/ebms/records'
        assert elements.signature is not None
        assert verified is not None

    def test_two_payloads_in_manifest_order(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        result = _receive(messages, parties, 'request-two-payloads-ref-to.xml')
        delivery = _delivered(result)

        first, second = delivery.payloads

        assert _content_ids(delivery) == ['Payload-0', 'Payload-1']
        assert b'<Position>0</Position>' in first.data
        assert b'<Position>1</Position>' in second.data
        assert delivery.ref_to_message_id == 'earlierMessageId'

    def test_duplicate_returns_the_stored_acknowledgment(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('request-sync-reply-duplicate.xml')
        exchange = _exchange(parties, data)
        message = package_message(data)

        first = receive_message(exchange, message)
        second = receive_message(exchange, message)

        _ = _delivered(first)
        _assert_synchronous_acknowledgment(first)

        assert second.outcome.duplicate
        assert second.outcome.final_state == FinalState.Duplicate
        assert not second.deliveries
        assert second.response.body == first.response.body

    def test_alternative_serialization_is_a_duplicate(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('request-sync-reply-duplicate.xml')
        other_data = messages.load('request-sync-reply-alternative-serialization.xml')

        exchange = _exchange(parties, data)
        message = package_message(data)
        other_message = package_message(other_data)

        first = receive_message(exchange, message)
        second = receive_message(exchange, other_message)

        _ = _delivered(first)

        assert second.outcome.duplicate
        assert not second.deliveries

    def test_no_acknowledgment_requested(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('request-soapenv-prefix-encoding-namespaces.xml')

        settings = settings_for(parties, data)
        settings.business_channel.ack_requested = PerMessage.Per_Message

        exchange = _exchange(parties, data, settings)
        message = package_message(data)

        result = receive_message(exchange, message)
        _ = _delivered(result)

        assert result.async_signal is None
        assert not result.response.body
        assert result.outcome.signal_kind == SignalKind.No_Signal

    def test_reference_to_an_earlier_message(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        result = _receive(messages, parties, 'request-ack-requested-ref-to-loopback-service.xml')
        delivery = _delivered(result)

        assert delivery.service == 'http://127.0.0.1/ebms/sender'
        assert delivery.ref_to_message_id == 'earlierMessageId'

        _assert_asynchronous_acknowledgment(result)

    def test_typed_service_with_spaces(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        result = _receive(messages, parties, 'request-roles-service-with-spaces.xml')
        delivery = _delivered(result)

        assert delivery.service == 'Manage Record Exchange'
        assert delivery.service_type == 'v4.0'
        assert delivery.action == 'requestSingleRecordCheck'
        assert delivery.conversation_id == 'localconid'

        _assert_asynchronous_acknowledgment(result)

    def test_mismatched_end_tag(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('envelope-mismatched-end-tag.xml')
        agreement_data = messages.load('ping-whitespace-after-declaration.xml')

        exchange = _exchange(parties, agreement_data)
        message = package_message(data, [])

        result = receive_message(exchange, message)
        _assert_fault(result, ErrorCode.Other_XML)

    def test_textual_timestamp(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('request-text-timestamp.xml')
        agreement_data = messages.load('request-sync-reply-duplicate.xml')

        exchange = _exchange(parties, agreement_data)
        message = package_message(data)

        result = receive_message(exchange, message)
        _assert_fault(result, ErrorCode.Inconsistent)

# ################################################################################################################################
# ################################################################################################################################

class TestFileTransfer:
    """ A file transfer between two parties with roles, built through the API.
    """

    def test_roles_and_content_id(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('envelope-mismatched-end-tag.xml')
        data = data.replace(b'SOAP:Envelop ', b'SOAP:Envelope ', 1)

        settings = settings_for(parties, data)
        settings.is_signed = False

        exchange = new_exchange(parties, settings)
        payload = new_payload(_file_data, _file_content_id)

        outbound = send(exchange, [payload])

        unpacked = unpack(outbound.package.headers, outbound.package.body)
        envelope = parse_envelope(unpacked.envelope)
        elements = collect_elements(envelope)

        header = parse_message_header(elements.message_header)
        manifest = parse_manifest(elements.manifest)

        assert header.from_party.role == 'Sender'
        assert header.to_party.role == 'Receiver'
        assert header.service == 'urn:zato:b2b:test:files'
        assert header.action == 'FileTransfer'
        assert manifest.references[0].href == f'cid:{_file_content_id}'
        assert unpacked.payloads[0].content_id == _file_content_id
        assert unpacked.payloads[0].data == _file_data

        result = deliver(exchange, outbound)
        delivery = _delivered(result)

        assert delivery.payloads[0].data == _file_data

# ################################################################################################################################
# ################################################################################################################################

class TestManifestVariants:
    """ Business messages whose manifests reference their payloads in the forms other senders use.
    """

    def test_reference_to_own_message_id(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        result = _receive(messages, parties, 'response-ref-to-own-message-id.xml')
        delivery = _delivered(result)

        assert delivery.ref_to_message_id == delivery.message_id
        _assert_synchronous_acknowledgment(result)

    def test_response_correlated_to_its_request(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('response-reliable-correlated.xml')
        header = read_header(data)

        request_service = ServiceSettings()
        request_service.service = header.service
        request_service.action = 'RecordQuery'

        settings = settings_for(parties, data)
        settings.extra_services.append(request_service)
        settings.sender.can_receive = True
        settings.receiver.can_send = True

        exchange = _exchange(parties, data, settings)

        options = SendOptions()
        options.message_id = header.message_data.ref_to_message_id
        options.conversation_id = header.conversation_id

        binding = resolve(exchange, 'RecordQuery', is_reverse=True)
        payloads = [new_payload()]
        request = build(exchange.agreement, exchange.receiver.local_keys, binding, payloads, exchange.clock, options)

        message = package_message(data)
        result = receive_message(exchange, message)
        delivery = _delivered(result)

        assert delivery.ref_to_message_id == request.message_id
        assert delivery.conversation_id == request.header.conversation_id

    def test_payload_and_attachment(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        result = _receive(messages, parties, 'request-payload-and-attachment.xml')
        delivery = _delivered(result)

        assert _content_ids(delivery) == [
            '376CE5F9-27D4-4D60-8881-A9A915DE725E@b2b.test',
            '2F548C4F-A7B5-46CB-A6ED-2FACEC47991F@b2b.test',
        ]

    def test_unsolicited(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        result = _receive(messages, parties, 'request-unsolicited.xml')
        delivery = _delivered(result)

        assert not delivery.ref_to_message_id
        assert delivery.message_id == '0D1C6060-2F12-4F3A-9028-AB3A079A9D51'

    def test_unknown_ref_to_message_id(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        result = _receive(messages, parties, 'request-unknown-ref-to-message-id.xml')
        delivery = _delivered(result)

        assert delivery.ref_to_message_id == 'B7C54B75-8C36-4DCC-8471-EAB9CDEAF9F2'
        _assert_synchronous_acknowledgment(result)

    def test_mid_references(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        result = _receive(messages, parties, 'request-mid-references.xml')
        delivery = _delivered(result)

        assert _content_ids(delivery) == ['afaf1a7b-97e1-4238-b3b6-9f08b32f3052@b2b.test']
        _assert_asynchronous_acknowledgment(result, Actor.Next_MSH)

    def test_mixed_cid_and_mid_references(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        result = _receive(messages, parties, 'request-mixed-cid-mid-numeric-id.xml')
        delivery = _delivered(result)

        assert _content_ids(delivery) == [
            'c02e6bed-fc1f-40cf-9c5c-be28018db195@b2b.test',
            '6CFF6640-66FE-4E1F-8594-2C03CA38617E',
        ]
        _assert_asynchronous_acknowledgment(result, Actor.Next_MSH)

    def test_multiline_description(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        result = _receive(messages, parties, 'request-multiline-description.xml')
        delivery = _delivered(result)

        assert _content_ids(delivery) == [
            'aadea16a-4fee-4e03-8e0b-5ac84c464b2f@b2b.test',
            '939402D3-E098-461D-8DDD-F0A0EC30F8F4',
        ]
        _assert_asynchronous_acknowledgment(result, Actor.Next_MSH)

    def test_mid_binary_attachment(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        result = _receive(messages, parties, 'request-mid-binary-attachment.xml')
        delivery = _delivered(result)

        assert _content_ids(delivery) == ['f7848184-b0db-4c4b-b110-45707ebec6f0@b2b.test']
        _assert_asynchronous_acknowledgment(result, Actor.Next_MSH)

    def test_mid_xml_attachment(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        result = _receive(messages, parties, 'request-mid-xml-attachment.xml')
        delivery = _delivered(result)

        assert _content_ids(delivery) == ['8031db0b-a613-4867-a8b1-79b1ae524bda@b2b.test']
        _assert_asynchronous_acknowledgment(result)

# ################################################################################################################################
# ################################################################################################################################
