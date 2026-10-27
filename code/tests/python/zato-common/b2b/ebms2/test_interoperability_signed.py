# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.b2b.common.outcome import FinalState, SignalKind
from zato.common.b2b.ebms2.common import ErrorCode, PerMessage
from zato.common.b2b.ebms2.message import collect_elements, parse_envelope, serialize
from zato.common.b2b.ebms2.outbound import accept_signal, OutboundState, SendOptions
from zato.common.b2b.ebms2.signals import parse_acknowledgment
from zato.common.b2b.ebms2.signature import DigestAlgorithm, SignatureAlgorithm, verify_envelope
from zato.common.test.b2b_ebms2 import new_exchange, new_payload, send
from zato.common.test.b2b_interoperability import add_key_value, clear_x509_data, declare_xpath_prefix, echo_digests, \
    manifest_payloads, outbound_answered, package_message, receive_message, refresh_digests, \
    remove_xpath_transform, reply_elements, retarget_reference, set_canonicalization, settings_for, sign_message, \
    sign_signed_info, signed_message
from zato.common.util.xml_.constants import Algorithm

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.b2b.ebms2.inbound import InboundResult
    from zato.common.b2b.ebms2.outbound import OutboundMessage
    from zato.common.b2b.ebms2.packaging import payload_list
    from zato.common.test.b2b_ebms2 import Exchange
    from zato.common.test.b2b_interoperability import FixtureDirectory
    from zato.common.test.b2b_pki import TestParties, TestParty
    from zato.common.typing_ import any_
    any_ = any_
    Exchange = Exchange
    FixtureDirectory = FixtureDirectory
    InboundResult = InboundResult
    OutboundMessage = OutboundMessage
    payload_list = payload_list
    TestParties = TestParties
    TestParty = TestParty

# ################################################################################################################################
# ################################################################################################################################

# The Content-ID that a signature names in place of the one the manifest names.
_unlisted_content_id = 'cid:summary@b2b.test'

# The Content-ID of the payload whose digest a signed receipt echoes.
_receipt_content_id = 'recordpayload111@example.com'

# ################################################################################################################################
# ################################################################################################################################

def _signed_exchange(
    parties:'TestParties',
    data:'bytes',
    *,
    is_answer:'bool'=False,
    is_sha1:'bool'=False,
    ack_signature_requested:'str'=PerMessage.Never,
    ) -> 'Exchange':
    """ Returns an exchange under a signed agreement whose parties are the ones a SOAP part names.
    """
    settings = settings_for(parties, data, is_answer=is_answer)
    settings.is_signed = True
    settings.is_msh_signed = True
    settings.business_channel.ack_signature_requested = ack_signature_requested

    if is_sha1:
        settings.signature_algorithm = SignatureAlgorithm.RSA_SHA1
        settings.hash_function = DigestAlgorithm.SHA1

    out = new_exchange(parties, settings)
    return out

# ################################################################################################################################

def _acknowledged_message_id(data:'bytes') -> 'str':
    """ Returns the MessageId that the Acknowledgment of a SOAP part names.
    """
    envelope = parse_envelope(data)
    elements = collect_elements(envelope)
    acknowledgment = parse_acknowledgment(elements.acknowledgment)

    out = acknowledgment.ref_to_message_id
    return out

# ################################################################################################################################

def _receive(exchange:'Exchange', envelope:'any_', payloads:'payload_list') -> 'InboundResult':
    """ Receives an envelope signed at test time, together with its payloads.
    """
    data = serialize(envelope)
    message = package_message(data, payloads)

    out = receive_message(exchange, message)
    return out

# ################################################################################################################################

def _assert_verified(result:'InboundResult') -> 'None':
    assert result.outcome.signature_verified
    assert result.outcome.delivered
    assert result.outcome.final_state == FinalState.Delivered
    assert len(result.deliveries) == 1

# ################################################################################################################################

def _assert_security_failure(result:'InboundResult') -> 'None':
    assert result.outcome.error_code == ErrorCode.Security_Failure
    assert result.outcome.final_state == FinalState.Rejected
    assert not result.deliveries

# ################################################################################################################################

def _accept_signed_signal(exchange:'Exchange', outbound:'OutboundMessage', data:'bytes', party:'TestParty') -> 'None':
    """ Signs a signal with the rsa-sha1 profile and passes it to the sender as the asynchronous answer to its message.
    """
    signed = signed_message(data, [], party, SignatureAlgorithm.RSA_SHA1, DigestAlgorithm.SHA1)
    message = package_message(signed, [])

    _ = accept_signal(outbound, message.headers, message.body, exchange.clock)

# ################################################################################################################################
# ################################################################################################################################

class TestSignedRequests:
    """ Signed business messages in the forms other message service handlers send them in, signed at test time.
    """

    def test_key_value_before_certificate(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('signed-request-sha256-roles.xml')
        exchange = _signed_exchange(parties, data)
        payloads = manifest_payloads(data)

        envelope, signature = sign_message(data, payloads, parties.sender)
        add_key_value(signature, parties.sender.certificate, is_before_x509_data=True)

        result = _receive(exchange, envelope, payloads)
        _assert_verified(result)

    def test_xpath_prefix_declared_on_the_filter(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('signed-request-sha256-roles.xml')
        exchange = _signed_exchange(parties, data)
        payloads = manifest_payloads(data)

        envelope, signature = sign_message(data, payloads, parties.sender)
        declare_xpath_prefix(signature)
        sign_signed_info(signature, parties.sender)

        result = _receive(exchange, envelope, payloads)
        _assert_verified(result)

    def test_xpath_prefix_not_declared(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('signed-request-sha256-roles.xml')
        exchange = _signed_exchange(parties, data)
        payloads = manifest_payloads(data)

        envelope, signature = sign_message(data, payloads, parties.sender)
        declare_xpath_prefix(signature, is_declared=False)
        sign_signed_info(signature, parties.sender)

        result = _receive(exchange, envelope, payloads)
        _assert_security_failure(result)

    def test_key_value_without_certificate(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('signed-request-key-value-empty-x509.xml')
        exchange = _signed_exchange(parties, data)
        payloads = manifest_payloads(data)

        envelope, signature = sign_message(data, payloads, parties.sender)
        clear_x509_data(signature)
        add_key_value(signature, parties.sender.certificate, is_before_x509_data=True, has_modulus=False)

        # Without a certificate in the signature, it is verified against the one the agreement names.
        result = _receive(exchange, envelope, payloads)
        _assert_verified(result)

    def test_reference_to_a_part_the_manifest_does_not_name(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('signed-request-reference-not-in-manifest.xml')
        exchange = _signed_exchange(parties, data, is_sha1=True)
        payloads = manifest_payloads(data)

        envelope, signature = sign_message(data, payloads, parties.sender, SignatureAlgorithm.RSA_SHA1, DigestAlgorithm.SHA1)
        remove_xpath_transform(signature)
        refresh_digests(envelope, signature, payloads)

        first_payload = payloads[0]
        payload_uri = f'cid:{first_payload.content_id}'

        retarget_reference(signature, payload_uri, _unlisted_content_id)
        sign_signed_info(signature, parties.sender)

        result = _receive(exchange, envelope, payloads)
        _assert_security_failure(result)

    def test_sha1_with_signed_acknowledgment(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('signed-request-sha1-typed-service.xml')
        exchange = _signed_exchange(parties, data, is_sha1=True, ack_signature_requested=PerMessage.Per_Message)

        payloads = manifest_payloads(data)
        envelope, _ = sign_message(data, payloads, parties.sender, SignatureAlgorithm.RSA_SHA1, DigestAlgorithm.SHA1)

        result = _receive(exchange, envelope, payloads)
        _assert_verified(result)

        elements = reply_elements(result)
        acknowledgment = parse_acknowledgment(elements.acknowledgment)
        verified = verify_envelope(elements.envelope, elements.signature, [], parties.receiver.certificate)

        assert result.outcome.signal_kind == SignalKind.Receipt
        assert verified.certificate == parties.receiver.certificate
        assert len(acknowledgment.references) == len(payloads) + 1

    def test_payload_digest(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('signed-request-payload-digest-url-service.xml')
        exchange = _signed_exchange(parties, data)
        payloads = manifest_payloads(data)

        envelope, _ = sign_message(data, payloads, parties.sender)

        result = _receive(exchange, envelope, payloads)
        _assert_verified(result)

    def test_changed_payload(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('signed-request-payload-digest-url-service.xml')
        exchange = _signed_exchange(parties, data)
        payloads = manifest_payloads(data)

        envelope, _ = sign_message(data, payloads, parties.sender)

        first_payload = payloads[0]
        first_payload.data = first_payload.data.replace(b'0', b'1', 1)

        result = _receive(exchange, envelope, payloads)
        _assert_security_failure(result)

    def test_exclusive_canonicalization(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('error-list-unprefixed-attributes.xml')
        exchange = _signed_exchange(parties, data)

        envelope, signature = sign_message(data, [], parties.sender)
        set_canonicalization(signature, Algorithm.C14N_Exclusive)
        sign_signed_info(signature, parties.sender)

        result = _receive(exchange, envelope, [])
        _assert_security_failure(result)

# ################################################################################################################################
# ################################################################################################################################

class TestSignedAcknowledgments:
    """ Signed acknowledgments in the forms other message service handlers send them in, signed at test time.
    """

    def _receipt_exchange(self, parties:'TestParties', data:'bytes') -> 'tuple[Exchange, OutboundMessage]':
        """ Returns the message of the sender that a signed receipt acknowledges, under an agreement whose acknowledgments
        are signed and echo the digests of the message.
        """
        exchange = _signed_exchange(parties, data, is_answer=True, is_sha1=True, ack_signature_requested=PerMessage.Always)

        options = SendOptions()
        options.message_id = _acknowledged_message_id(data)

        payload = new_payload(content_id=_receipt_content_id)
        outbound = send(exchange, [payload], options)

        out = (exchange, outbound)
        return out

    def test_receipt_with_echoed_digests(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('acknowledgment-receipt-references.xml')
        exchange, outbound = self._receipt_exchange(parties, data)

        echoed = echo_digests(data, outbound.sent_digests)
        _accept_signed_signal(exchange, outbound, echoed, parties.receiver)

        assert outbound.is_ack_signature_requested
        assert outbound.state == OutboundState.Acknowledged
        assert outbound.outcome.signature_verified
        assert outbound.outcome.delivered

    def test_receipt_without_digests(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('acknowledgment-receipt-references.xml')
        exchange, outbound = self._receipt_exchange(parties, data)

        _accept_signed_signal(exchange, outbound, data, parties.receiver)

        assert outbound.state == OutboundState.Failed
        assert outbound.outcome.error_code == ErrorCode.Security_Failure

    def _key_value_acknowledgment(self, parties:'TestParties', data:'bytes', *, is_declared:'bool') -> 'OutboundMessage':
        """ Passes an acknowledgment signed with a KeyValue after the certificate and with its own prefix
        in the XPath filter to the sender of the message it acknowledges, and returns that message.
        """
        exchange = _signed_exchange(parties, data, is_answer=True, is_sha1=True)

        message_id = _acknowledged_message_id(data)
        out = outbound_answered(exchange, message_id)

        envelope, signature = sign_message(data, [], parties.receiver, SignatureAlgorithm.RSA_SHA1, DigestAlgorithm.SHA1)
        declare_xpath_prefix(signature, is_declared=is_declared)
        add_key_value(signature, parties.receiver.certificate, is_before_x509_data=False)
        sign_signed_info(signature, parties.receiver)

        signed = serialize(envelope)
        message = package_message(signed, [])

        _ = accept_signal(out, message.headers, message.body, exchange.clock)
        return out

    def test_key_value_after_certificate(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('acknowledgment-key-value-and-certificate.xml')
        outbound = self._key_value_acknowledgment(parties, data, is_declared=True)

        assert outbound.state == OutboundState.Acknowledged
        assert outbound.outcome.signature_verified

    def test_key_value_with_undeclared_prefix(self, messages:'FixtureDirectory', parties:'TestParties') -> 'None':
        data = messages.load('acknowledgment-key-value-and-certificate.xml')
        outbound = self._key_value_acknowledgment(parties, data, is_declared=False)

        assert outbound.state == OutboundState.Failed
        assert outbound.outcome.error_code == ErrorCode.Security_Failure

# ################################################################################################################################
# ################################################################################################################################
