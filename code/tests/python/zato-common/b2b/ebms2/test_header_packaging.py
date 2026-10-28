# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import INTERNAL_SERVER_ERROR, OK

# lxml
from lxml.etree import fromstring, SubElement, tostring

# pytest
import pytest

# Zato
from zato.common.b2b.common.outcome import FinalState, SignalKind
from zato.common.b2b.ebms2.common import EbMS2Exception, ErrorCode, NS, Root_Content_Type, SequenceStatus
from zato.common.b2b.ebms2.compose import compose, Composition, new_message_header, new_message_id
from zato.common.b2b.ebms2.header import AckRequested, MessageOrder, parse_message_header
from zato.common.b2b.ebms2.inbound import receive
from zato.common.b2b.ebms2.message import collect_elements, parse_envelope, serialize
from zato.common.b2b.ebms2.packaging import package, unpack
from zato.common.b2b.ebms2.xml_ import SOAP_Must_Understand
from zato.common.test.b2b_cpa import new_settings, Receiver_Name, Sender_Name
from zato.common.test.b2b_ebms2 import new_exchange, new_payload, resolve, Start_Time
from zato.common.util.xml_.core import qname

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

_conversation_id = 'b2b-conversation-1'

_soap12_envelope = b'<env:Envelope xmlns:env="http://www.w3.org/2003/05/soap-envelope"><env:Body/></env:Envelope>'

_soap11_without_header = b'<SOAP:Envelope xmlns:SOAP="http://schemas.xmlsoap.org/soap/envelope/"><SOAP:Header/><SOAP:Body/></SOAP:Envelope>'

_text_headers = {'Content-Type': Root_Content_Type}

_eb_prefix = f'{{{NS.EB}}}'

# ################################################################################################################################
# ################################################################################################################################

def _composition(exchange:'Exchange') -> 'Composition':
    """ Returns an unsigned message of the sender with one payload and every optional header block.
    """
    binding = resolve(exchange)
    message_id = new_message_id()

    message_order = MessageOrder()
    message_order.sequence_number = 0
    message_order.status = SequenceStatus.Reset

    out = Composition()
    out.header = new_message_header(binding, Start_Time, _conversation_id, message_id)
    out.ack_requested = AckRequested()
    out.sync_reply = True
    out.message_order = message_order
    payload = new_payload(content_id='payload-1@b2b.test')

    out.payloads = [payload]

    return out

# ################################################################################################################################

def _eb_elements(envelope:'any_') -> 'any_':
    """ Returns copies of the ebMS elements of an envelope, each as the root of a document of its own.
    """
    out = []

    soap_header = envelope[0]
    soap_body = envelope[1]

    for parent in (soap_header, soap_body):
        for element in parent:
            if element.tag.startswith(_eb_prefix):
                data = tostring(element)
                copy = fromstring(data)
                out.append(copy)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestMessageHeader:
    """ The eb:MessageHeader and the other ebMS 2.0 header blocks.
    """

    def test_header_round_trip(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        composition = _composition(exchange)
        composed = compose(composition)

        data = serialize(composed.envelope)
        envelope = parse_envelope(data)
        elements = collect_elements(envelope)

        header = parse_message_header(elements.message_header)

        assert header.cpa_id == settings.cpa_id
        assert header.conversation_id == _conversation_id
        assert header.service == settings.service
        assert header.action == settings.action
        assert header.from_party.party_ids[0].value == Sender_Name
        assert header.to_party.party_ids[0].value == Receiver_Name
        assert header.from_party.role == settings.sender.role
        assert header.to_party.role == settings.receiver.role
        assert header.message_data.message_id == composition.header.message_data.message_id
        assert header.message_data.timestamp == Start_Time

        assert elements.ack_requested is not None
        assert elements.sync_reply is not None
        assert elements.message_order is not None
        assert elements.manifest is not None

    def test_header_blocks_are_schema_valid(self, parties:'TestParties', msg_header_schema:'any_') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        composition = _composition(exchange)
        composed = compose(composition)

        elements = _eb_elements(composed.envelope)
        assert len(elements) == 5

        for element in elements:
            msg_header_schema.assertValid(element)

    def test_envelope_is_schema_valid(self, parties:'TestParties', soap11_schema:'any_') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        composition = _composition(exchange)
        composed = compose(composition)

        soap11_schema.assertValid(composed.envelope)

    def test_duplicate_header_block_is_rejected(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        composition = _composition(exchange)
        composed = compose(composition)

        soap_header = composed.envelope[0]
        message_header = soap_header[0]
        data = tostring(message_header)
        duplicate = fromstring(data)
        soap_header.append(duplicate)

        with pytest.raises(EbMS2Exception) as info:
            _ = collect_elements(composed.envelope)

        assert info.value.error_code == ErrorCode.Inconsistent

# ################################################################################################################################
# ################################################################################################################################

class TestPackaging:
    """ The SOAP with Attachments packaging of messages.
    """

    def test_package_round_trip(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        first = new_payload(b'<First/>', 'first@b2b.test')
        second = new_payload(b'<Second/>', 'second@b2b.test')

        composition = _composition(exchange)
        composition.payloads = [first, second]
        composed = compose(composition)

        unpacked = unpack(composed.package.headers, composed.package.body)

        assert len(unpacked.payloads) == 2
        assert unpacked.payloads[0].content_id == 'first@b2b.test'
        assert unpacked.payloads[0].data == b'<First/>'
        assert unpacked.payloads[1].content_id == 'second@b2b.test'
        assert unpacked.payloads[1].data == b'<Second/>'

        envelope = parse_envelope(unpacked.envelope)
        assert envelope.tag == qname(NS.SOAP, 'Envelope')

    def test_headers_are_case_insensitive(self) -> 'None':
        payload = new_payload()
        packaged = package(_soap11_without_header, [payload])

        headers:'any_' = {}

        for name, value in packaged.headers.items():
            upper_name = name.upper()
            headers[upper_name] = value

        unpacked = unpack(headers, packaged.body)
        assert len(unpacked.payloads) == 1

    def test_unsupported_media_type(self) -> 'None':
        with pytest.raises(EbMS2Exception) as info:
            _ = unpack({'Content-Type': 'application/octet-stream'}, b'data')

        assert info.value.error_code == ErrorCode.MIME_Problem

    def test_missing_content_type(self) -> 'None':
        with pytest.raises(EbMS2Exception) as info:
            _ = unpack({}, b'data')

        assert info.value.error_code == ErrorCode.MIME_Problem

# ################################################################################################################################
# ################################################################################################################################

class TestUnreadableMessages:
    """ Messages whose MessageHeader cannot be read are answered with a SOAP Fault.
    """

    def _receive(self, exchange:'Exchange', headers:'any_', body:'bytes') -> 'any_':
        receiver = exchange.receiver
        out = receive(exchange.agreement, receiver.local_keys, headers, body, receiver.receive_log, exchange.clock)
        return out

    def test_missing_message_header(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        result = self._receive(exchange, _text_headers, _soap11_without_header)

        assert result.response.status_code == INTERNAL_SERVER_ERROR
        assert b'Fault' in result.response.body
        assert result.outcome.error_code == ErrorCode.Inconsistent
        assert result.outcome.final_state == FinalState.Rejected
        assert not result.deliveries

    def test_soap12_is_not_supported(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        result = self._receive(exchange, _text_headers, _soap12_envelope)

        assert result.response.status_code == INTERNAL_SERVER_ERROR
        assert result.outcome.error_code == ErrorCode.Not_Supported

    def test_not_xml(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        result = self._receive(exchange, _text_headers, b'not xml')

        assert result.response.status_code == INTERNAL_SERVER_ERROR
        assert result.outcome.error_code == ErrorCode.Other_XML

    def test_unknown_mandatory_header_block(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        composition = _composition(exchange)
        composition.payloads = []
        composed = compose(composition)

        soap_header = composed.envelope[0]
        block = SubElement(soap_header, '{urn:zato:b2b:test:extension}Block')
        block.set(SOAP_Must_Understand, '1')

        body = serialize(composed.envelope)
        result = self._receive(exchange, _text_headers, body)

        assert result.response.status_code == OK
        assert b'ErrorList' in result.response.body
        assert result.outcome.signal_kind == SignalKind.Error
        assert result.outcome.error_code == ErrorCode.Not_Supported
        assert not result.deliveries

# ################################################################################################################################
# ################################################################################################################################
