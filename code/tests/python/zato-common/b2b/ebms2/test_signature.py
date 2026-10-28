# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# lxml
from lxml.etree import SubElement

# pytest
import pytest

# Zato
from zato.common.b2b.common.outcome import FinalState
from zato.common.b2b.ebms2.common import Actor, EbMS2SecurityException, ErrorCode, NS
from zato.common.b2b.ebms2.compose import compose, Composition, new_message_header, new_message_id, signing_for
from zato.common.b2b.ebms2.inbound import receive
from zato.common.b2b.ebms2.message import collect_elements, parse_envelope
from zato.common.b2b.ebms2.packaging import unpack
from zato.common.b2b.ebms2.security import sender_non_repudiation
from zato.common.b2b.ebms2.signature import DigestAlgorithm, SignatureAlgorithm, verify_envelope, XPath_Transform
from zato.common.b2b.ebms2.xml_ import eb_tag, SOAP_Actor
from zato.common.test.b2b_cpa import new_settings
from zato.common.test.b2b_ebms2 import deliver, new_exchange, new_local_keys, new_payload, resolve, send, Start_Time
from zato.common.test.b2b_pki import ca_party, issue_party, make_ca, TestParties, Weak_RSA_Key_Size
from zato.common.util.xml_.constants import Algorithm, Transform
from zato.common.util.xml_.core import qname

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.b2b.ebms2.compose import Composed
    from zato.common.b2b.ebms2.inbound import InboundResult
    from zato.common.b2b.ebms2.packaging import Package
    from zato.common.test.b2b_cpa import AgreementSettings
    from zato.common.test.b2b_ebms2 import Exchange
    from zato.common.test.b2b_pki import TestParty
    AgreementSettings = AgreementSettings
    Composed = Composed
    Exchange = Exchange
    InboundResult = InboundResult
    Package = Package
    TestParty = TestParty

# ################################################################################################################################
# ################################################################################################################################

_ds_signed_info = qname(NS.DS, 'SignedInfo')
_ds_signature_method = qname(NS.DS, 'SignatureMethod')
_ds_reference = qname(NS.DS, 'Reference')
_ds_transform = qname(NS.DS, 'Transform')
_soap_header = qname(NS.SOAP, 'Header')

_conversation_id_tag = eb_tag('ConversationId')

_extension_tag = '{urn:zato:b2b:test:extension}Hop'

# ################################################################################################################################
# ################################################################################################################################

def _composition(exchange:'Exchange', *, is_signed:'bool'=True) -> 'Composition':
    """ Returns a business message of the sender with one payload, signed the way the agreement says.
    """
    binding = resolve(exchange)
    message_id = new_message_id()
    payload = new_payload(content_id='payload-1@b2b.test')

    out = Composition()
    out.header = new_message_header(binding, Start_Time, 'b2b-conversation-1', message_id)
    out.payloads = [payload]

    if is_signed:
        non_repudiation = sender_non_repudiation(binding)
        out.signing = signing_for(non_repudiation, exchange.sender.local_keys)

    return out

# ################################################################################################################################

def _signed(parties:'TestParties', settings:'AgreementSettings | None'=None) -> 'tuple[Composition, Composed]':
    if settings is None:
        settings = new_settings(parties, Start_Time)

    exchange = new_exchange(parties, settings)

    composition = _composition(exchange)
    composed = compose(composition)

    out = (composition, composed)
    return out

# ################################################################################################################################

def _receive_package(exchange:'Exchange', package:'Package') -> 'InboundResult':
    receiver = exchange.receiver
    out = receive(exchange.agreement, receiver.local_keys, package.headers, package.body, receiver.receive_log, exchange.clock)
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

def _assert_security_failure(result:'InboundResult') -> 'None':
    """ The agreements of these tests have no synchronous replies, so the error message is sent asynchronously.
    """
    assert result.outcome.error_code == ErrorCode.Security_Failure
    assert result.outcome.final_state == FinalState.Rejected
    assert not result.response.body
    assert result.async_signal is not None
    assert b'SecurityFailure' in result.async_signal.package.body
    assert not result.deliveries

# ################################################################################################################################
# ################################################################################################################################

class TestSignatureProfile:
    """ The ebMS 2.0 XMLDSig profile - an enveloped signature over the envelope and a reference to each payload.
    """

    def test_sign_and_verify(self, parties:'TestParties') -> 'None':
        composition, composed = _signed(parties)

        verified = verify_envelope(composed.envelope, composed.signature, composition.payloads, parties.sender.certificate)

        assert len(verified.references) == 2
        assert verified.certificate == parties.sender.certificate

    def test_verify_after_transfer(self, parties:'TestParties') -> 'None':
        _, composed = _signed(parties)

        unpacked = unpack(composed.package.headers, composed.package.body)
        envelope = parse_envelope(unpacked.envelope)
        elements = collect_elements(envelope)

        verified = verify_envelope(elements.envelope, elements.signature, unpacked.payloads, parties.sender.certificate)
        assert verified.certificate == parties.sender.certificate

    def test_profile(self, parties:'TestParties') -> 'None':
        _, composed = _signed(parties)

        signature = composed.signature
        assert signature.getparent().tag == _soap_header

        signed_info = signature.find(_ds_signed_info)
        signature_method = signed_info.find(_ds_signature_method)
        assert signature_method.get('Algorithm') == SignatureAlgorithm.RSA_SHA256

        envelope_reference, payload_reference = signed_info.findall(_ds_reference)

        transforms = []

        for transform in envelope_reference.iter(_ds_transform):
            algorithm = transform.get('Algorithm')
            transforms.append(algorithm)

        assert envelope_reference.get('URI') == ''
        assert transforms == [Transform.Enveloped, XPath_Transform, Algorithm.C14N]
        assert payload_reference.get('URI') == 'cid:payload-1@b2b.test'

    def test_sha1(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        settings.signature_algorithm = SignatureAlgorithm.RSA_SHA1
        settings.hash_function = DigestAlgorithm.SHA1

        composition, composed = _signed(parties, settings)

        signed_info = composed.signature.find(_ds_signed_info)
        signature_method = signed_info.find(_ds_signature_method)
        assert signature_method.get('Algorithm') == SignatureAlgorithm.RSA_SHA1

        verified = verify_envelope(composed.envelope, composed.signature, composition.payloads, parties.sender.certificate)
        assert verified.certificate == parties.sender.certificate

    def test_tampered_payload(self, parties:'TestParties') -> 'None':
        composition, composed = _signed(parties)

        composition.payloads[0].data = b'<Order><Id>2</Id></Order>'

        with pytest.raises(EbMS2SecurityException):
            _ = verify_envelope(composed.envelope, composed.signature, composition.payloads, parties.sender.certificate)

    def test_tampered_header(self, parties:'TestParties') -> 'None':
        composition, composed = _signed(parties)

        conversation_id = composed.envelope.find(f'.//{_conversation_id_tag}')
        conversation_id.text = 'b2b-conversation-2'

        with pytest.raises(EbMS2SecurityException):
            _ = verify_envelope(composed.envelope, composed.signature, composition.payloads, parties.sender.certificate)

    def test_block_for_next_msh_may_change(self, parties:'TestParties') -> 'None':
        composition, composed = _signed(parties)

        soap_header = composed.envelope.find(_soap_header)
        block = SubElement(soap_header, _extension_tag)
        block.set(SOAP_Actor, Actor.Next_MSH)

        verified = verify_envelope(composed.envelope, composed.signature, composition.payloads, parties.sender.certificate)
        assert verified.certificate == parties.sender.certificate

    def test_other_block_may_not_change(self, parties:'TestParties') -> 'None':
        composition, composed = _signed(parties)

        soap_header = composed.envelope.find(_soap_header)
        _ = SubElement(soap_header, _extension_tag)

        with pytest.raises(EbMS2SecurityException):
            _ = verify_envelope(composed.envelope, composed.signature, composition.payloads, parties.sender.certificate)

# ################################################################################################################################
# ################################################################################################################################

class TestSignatureTrust:
    """ Received signatures are verified against the certificates and the trust anchors of the agreement.
    """

    def test_signed_message_is_delivered(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)
        result = deliver(exchange, outbound)

        assert outbound.signature is not None
        assert result.outcome.signature_verified
        assert result.outcome.delivered
        assert len(result.deliveries) == 1

    def test_unsigned_agreement(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        settings.is_signed = False
        exchange = new_exchange(parties, settings)

        outbound = send(exchange)
        result = deliver(exchange, outbound)

        assert outbound.signature is None
        assert not result.outcome.signature_verified
        assert result.outcome.delivered

    def test_unsigned_message_when_required(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)

        composition = _composition(exchange, is_signed=False)
        composed = compose(composition)

        result = _receive_package(exchange, composed.package)
        _assert_security_failure(result)

    def test_signer_other_than_agreement_names(self, parties:'TestParties') -> 'None':
        settings = new_settings(parties, Start_Time)
        exchange = new_exchange(parties, settings)
        exchange.sender.local_keys = new_local_keys(parties.receiver)

        outbound = send(exchange)
        result = deliver(exchange, outbound)

        _assert_security_failure(result)

    def test_certificate_of_unrelated_ca(self, parties:'TestParties') -> 'None':
        unrelated_ca = make_ca('b2b-unrelated-ca')
        sender = issue_party('b2b-sender', unrelated_ca)
        signing_parties = _with_sender(parties, sender)

        settings = new_settings(signing_parties, Start_Time)
        exchange = new_exchange(signing_parties, settings)

        outbound = send(exchange)
        result = deliver(exchange, outbound)

        _assert_security_failure(result)

    def test_weak_key(self, parties:'TestParties') -> 'None':
        ca = ca_party(parties)
        sender = issue_party('b2b-sender', ca, Weak_RSA_Key_Size)
        signing_parties = _with_sender(parties, sender)

        settings = new_settings(signing_parties, Start_Time)
        exchange = new_exchange(signing_parties, settings)

        outbound = send(exchange)
        result = deliver(exchange, outbound)

        _assert_security_failure(result)

# ################################################################################################################################
# ################################################################################################################################
