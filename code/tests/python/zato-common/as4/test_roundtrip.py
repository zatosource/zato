# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# lxml
from lxml import etree

# Zato
from zato.common.as4.common import EbMSError, NS
from zato.common.as4.ebms import parse_messaging
from zato.common.util.xml_.core import qname
from zato.common.as4.inbound import handle
from zato.common.as4.outbound import build_push_message, new_part
from zato.common.as4.profiles import new_edelivery1_pmode, new_edelivery2_pmode, new_peppol_pmode
from zato.common.as4.security.verify import verify_envelope

# ################################################################################################################################
# ################################################################################################################################

Payload = b'<Invoice xmlns="urn:test"><Total>100</Total></Invoice>'

# ################################################################################################################################
# ################################################################################################################################

def _make_pmode(factory):
    out = factory()

    out.initiator.party_id = 'party-a'
    out.responder.party_id = 'party-b'

    out.service = 'urn:test:service'
    out.action = 'SubmitInvoice'

    return out

# ################################################################################################################################

def _roundtrip(pmode, parties):
    """ Builds a push message as the sender and processes it as the receiver.
    """
    parts = [new_part(Payload)]
    body, content_type, message_id, sent_digests = build_push_message(pmode, parties.sender, parts)

    result = handle(body, content_type, [pmode], parties.receiver)

    out = (result, message_id, sent_digests)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestPushRoundtrip:

    def test_edelivery1_roundtrip(self, rsa_parties):
        pmode = _make_pmode(new_edelivery1_pmode)
        result, message_id, _ = _roundtrip(pmode, rsa_parties)

        assert not result.is_error
        assert result.user_message.message_id == message_id
        assert result.user_message.service == 'urn:test:service'

        # The payload arrives decrypted and decompressed.
        assert len(result.payloads) == 1
        assert result.payloads[0].data == Payload
        assert result.payloads[0].content_type == 'application/xml'

    def test_edelivery1_wire_is_encrypted_and_compressed(self, rsa_parties):
        pmode = _make_pmode(new_edelivery1_pmode)
        parts = [new_part(Payload)]

        body, _, _, _ = build_push_message(pmode, rsa_parties.sender, parts)

        # Neither the payload nor its gzip form appears on the wire in the clear.
        assert Payload not in body
        assert b'EncryptedKey' in body
        assert b'CompressionType' in body

    def test_edelivery2_roundtrip(self, eddsa_parties):
        pmode = _make_pmode(new_edelivery2_pmode)
        result, message_id, _ = _roundtrip(pmode, eddsa_parties)

        assert not result.is_error
        assert result.user_message.message_id == message_id
        assert result.payloads[0].data == Payload

    def test_peppol_roundtrip(self, rsa_parties):
        pmode = _make_pmode(new_peppol_pmode)
        pmode.original_sender = '0192:991825827'
        pmode.final_recipient = '0192:810418052'

        result, message_id, _ = _roundtrip(pmode, rsa_parties)

        assert not result.is_error
        assert result.payloads[0].data == Payload
        assert result.user_message.message_properties['originalSender'] == '0192:991825827'
        assert result.user_message.message_properties['finalRecipient'] == '0192:810418052'

    def test_peppol_wire_is_not_encrypted(self, rsa_parties):
        pmode = _make_pmode(new_peppol_pmode)
        parts = [new_part(Payload)]

        body, _, _, _ = build_push_message(pmode, rsa_parties.sender, parts)

        assert b'EncryptedKey' not in body
        assert b'Signature' in body

# ################################################################################################################################
# ################################################################################################################################

class TestReceipt:

    def test_receipt_is_signed_and_echoes_digests(self, rsa_parties):
        pmode = _make_pmode(new_edelivery1_pmode)
        result, message_id, sent_digests = _roundtrip(pmode, rsa_parties)

        receipt_envelope = etree.fromstring(result.body)
        messaging = parse_messaging(receipt_envelope)

        signal = messaging.signals[0]
        assert signal.is_receipt
        assert signal.ref_to_message_id == message_id

        # The receipt is signed by the receiver and the sender can verify it.
        verify_result = verify_envelope(receipt_envelope, [], rsa_parties.sender)
        assert verify_result.signer_certificate == rsa_parties.receiver.signing_certificate

        # Every digest the sender computed comes back unchanged - non-repudiation of receipt.
        for reference in signal.receipt_references:
            uri = reference.get('URI')
            digest_value = reference.find(qname(NS.DS, 'DigestValue')).text
            assert digest_value == sent_digests[uri]

# ################################################################################################################################
# ################################################################################################################################

class TestDuplicateDetection:

    def test_duplicate_gets_receipt_but_no_delivery(self, rsa_parties):
        pmode = _make_pmode(new_edelivery1_pmode)
        parts = [new_part(Payload)]
        body, content_type, message_id, _ = build_push_message(pmode, rsa_parties.sender, parts)

        seen = set()

        def is_duplicate(incoming_message_id):
            out = incoming_message_id in seen
            seen.add(incoming_message_id)
            return out

        # The first delivery goes through.
        first = handle(body, content_type, [pmode], rsa_parties.receiver, is_duplicate)
        assert not first.is_duplicate
        assert first.payloads[0].data == Payload

        # The replay still gets a receipt but no payloads are delivered.
        second = handle(body, content_type, [pmode], rsa_parties.receiver, is_duplicate)
        assert second.is_duplicate
        assert second.payloads == []
        assert not second.is_error

        messaging = parse_messaging(etree.fromstring(second.body))
        assert messaging.signals[0].is_receipt
        assert messaging.signals[0].ref_to_message_id == message_id

# ################################################################################################################################
# ################################################################################################################################

class TestInboundErrors:

    def test_tampered_message_yields_0101_error_signal(self, rsa_parties):
        pmode = _make_pmode(new_edelivery1_pmode)
        parts = [new_part(Payload)]
        body, content_type, _, _ = build_push_message(pmode, rsa_parties.sender, parts)

        # Change the signed eb:Action element on the wire.
        tampered = body.replace(b'SubmitInvoice', b'submitinvoice', 1)

        result = handle(tampered, content_type, [pmode], rsa_parties.receiver)

        assert result.is_error
        assert result.error_code == EbMSError.Failed_Authentication

        messaging = parse_messaging(etree.fromstring(result.body))
        assert messaging.signals[0].errors[0].error_code == EbMSError.Failed_Authentication

    def test_unparseable_envelope_yields_0009_error_signal(self, rsa_parties):
        pmode = _make_pmode(new_edelivery1_pmode)

        result = handle(b'this is not xml', 'application/soap+xml', [pmode], rsa_parties.receiver)

        assert result.is_error
        assert result.error_code == EbMSError.Invalid_Header

    def test_pull_request_is_refused_with_0002(self, rsa_parties):
        pmode = _make_pmode(new_edelivery1_pmode)

        from zato.common.as4.ebms import build_envelope, build_pull_request
        envelope = build_envelope()
        _ = build_pull_request(envelope, 'urn:test:mpc')
        body = etree.tostring(envelope)

        result = handle(body, 'application/soap+xml', [pmode], rsa_parties.receiver)

        assert result.is_error
        assert result.error_code == EbMSError.Feature_Not_Supported

# ################################################################################################################################
# ################################################################################################################################

class TestAsyncSignals:

    def test_async_receipt_is_surfaced_to_the_caller(self, rsa_parties):
        # Simulate an asynchronous receipt arriving on its own.
        from zato.common.as4.ebms import build_envelope, build_receipt
        envelope = build_envelope()
        _ = build_receipt(envelope, 'earlier-message@test', [])
        body = etree.tostring(envelope)

        pmode = _make_pmode(new_edelivery1_pmode)
        result = handle(body, 'application/soap+xml', [pmode], rsa_parties.receiver)

        assert not result.is_error
        assert len(result.signals) == 1
        assert result.signals[0].is_receipt
        assert result.signals[0].ref_to_message_id == 'earlier-message@test'

# ################################################################################################################################
# ################################################################################################################################
