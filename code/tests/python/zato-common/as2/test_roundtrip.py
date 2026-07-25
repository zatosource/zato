# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone
from http.client import ACCEPTED, NO_CONTENT, OK

# httpx
import httpx

# pytest
import pytest

# Zato
from .wire import do_send, new_exchange, Payload as _payload, Receiver_Identifier as _receiver_identifier, \
    Sender_Endpoint_URL as _sender_endpoint_url, Sender_Identifier as _sender_identifier, set_security
from zato.common.as2.common import AS2Error, Default, DigestAlgorithm, EncryptionAlgorithm, MDNMode, TransferMode
from zato.common.as2.inbound import handle
from zato.common.as2.inbound import layers as inbound_layers, payloads as inbound_payloads, pipeline as inbound_pipeline
from zato.common.as2.mdn import build_mdn, MDNRequest, new_processed_disposition, normalize_message_id, parse_mdn
from zato.common.as2.outbound import build_message, PayloadItem
from zato.common.as2.partnership import CertificateEntry, HTTPAuth
from zato.common.util.xml_.keystore import DecryptionEntry, new_keystore

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

class TestRoundtrip:
    """ The sender's send against the receiver's handle, over a mock wire.
    """

    def test_signed_encrypted_compressed(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.compress = True

        result = do_send(exchange)

        assert result.is_ok
        assert result.message_id
        assert result.mic
        assert result.http_status == OK

        # The receiver delivered exactly one document, byte for byte.
        inbound = exchange.results[0]

        assert not inbound.is_error
        assert not inbound.is_duplicate
        assert len(inbound.payloads) == 1
        assert inbound.payloads[0].data == _payload
        assert inbound.payloads[0].content_type == 'application/edi-x12'

        # Both sides computed the same MIC.
        assert inbound.mic == result.mic

# ################################################################################################################################

    def test_sha1_signed_3des_encrypted(self, parties:'TestParties') -> 'None':

        # The exact wire combination the SHA-1 and 3DES partnership preset produces -
        # an in-house SHA-1 SignedData inside an in-house 3DES envelope,
        # with a signed SHA-1 MDN MIC.
        exchange = new_exchange(parties)
        exchange.sender_partnership.sign_algorithm = DigestAlgorithm.SHA1
        exchange.sender_partnership.encryption_algorithm = EncryptionAlgorithm.DES_EDE3_CBC
        exchange.sender_partnership.mdn_mic_algorithms = [DigestAlgorithm.SHA1]

        result = do_send(exchange)

        assert result.is_ok
        assert result.message_id
        assert result.mic
        assert result.http_status == OK

        # The receiver delivered exactly one document, byte for byte.
        inbound = exchange.results[0]

        assert not inbound.is_error
        assert not inbound.is_duplicate
        assert len(inbound.payloads) == 1
        assert inbound.payloads[0].data == _payload

        # Both sides computed the same SHA-1 MIC.
        assert inbound.mic == result.mic
        assert result.mic.endswith('sha-1')

# ################################################################################################################################

    def test_signed_only(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        set_security(exchange, True, False)

        result = do_send(exchange)

        assert result.is_ok
        first_payload = exchange.results[0].payloads[0]
        assert first_payload.data == _payload

# ################################################################################################################################

    def test_encrypted_only(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        set_security(exchange, False, True)

        result = do_send(exchange)

        assert result.is_ok
        first_payload = exchange.results[0].payloads[0]
        assert first_payload.data == _payload

# ################################################################################################################################

    def test_plain(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        set_security(exchange, False, False)

        result = do_send(exchange)

        assert result.is_ok
        first_payload = exchange.results[0].payloads[0]
        assert first_payload.data == _payload

        # Nothing wrapped the payload, so it went over the wire as it is.
        assert exchange.bodies[0] == _payload

# ################################################################################################################################

    @pytest.mark.parametrize('compress_before_signing', [True, False])
    def test_compression_in_both_orders(self, parties:'TestParties', compress_before_signing:'any_') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.compress = True
        exchange.sender_partnership.compress_before_signing = compress_before_signing

        result = do_send(exchange)

        assert result.is_ok
        first_payload = exchange.results[0].payloads[0]
        assert first_payload.data == _payload
        assert exchange.results[0].mic == result.mic

# ################################################################################################################################

    def test_force_base64(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.force_base64 = True

        result = do_send(exchange)

        assert result.is_ok
        first_payload = exchange.results[0].payloads[0]
        assert first_payload.data == _payload

        # The outermost entity actually travelled base64-encoded.
        request = exchange.requests[0]
        assert request.headers['content-transfer-encoding'] == 'base64'

# ################################################################################################################################
# ################################################################################################################################

class TestWireShape:
    """ Wire-level assertions - what actually left the sender, not what the APIs report.
    """

    def test_ciphertext_on_the_wire(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        _ = do_send(exchange)

        request = exchange.requests[0]
        body = exchange.bodies[0]

        # The wire carries an encrypted entity and none of the plaintext.
        assert request.headers['content-type'].startswith('application/pkcs7-mime; smime-type=enveloped-data')
        assert b'ISA*00' not in body
        assert b'4523891' not in body

# ################################################################################################################################

    def test_compression_on_the_wire(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        set_security(exchange, False, False)
        exchange.sender_partnership.compress = True

        result = do_send(exchange)

        request = exchange.requests[0]
        body = exchange.bodies[0]

        # The wire carries a compressed entity and none of the plaintext.
        assert request.headers['content-type'].startswith('application/pkcs7-mime; smime-type=compressed-data')
        assert b'ISA*00' not in body

        assert result.is_ok

# ################################################################################################################################

    def test_as2_headers(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        result = do_send(exchange)

        request = exchange.requests[0]

        assert request.headers['as2-version'] == '1.2'
        assert request.headers['as2-from'] == _sender_identifier
        assert request.headers['as2-to'] == _receiver_identifier
        assert request.headers['message-id'] == result.message_id
        assert request.headers['subject'] == Default.Subject
        assert request.headers['mime-version'] == '1.0'
        assert request.headers['ediint-features'] == 'multiple-attachments, AS2-Reliability'

        # A signed synchronous MDN was requested.
        assert request.headers['disposition-notification-to'] == _sender_identifier
        assert request.headers['disposition-notification-options'] == \
            'signed-receipt-protocol=required, pkcs7-signature; signed-receipt-micalg=required, sha-256'
        assert 'receipt-delivery-option' not in request.headers

# ################################################################################################################################

    def test_version_pinning(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.as2_version = '1.1'

        result = do_send(exchange)

        assert result.is_ok
        assert exchange.requests[0].headers['as2-version'] == '1.1'

# ################################################################################################################################

    def test_inbound_accepts_an_absent_version(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        # An AS2 1.0 peer sends no AS2-Version header at all - inbound never rejects on version.
        body, headers, _, _ = build_message(exchange.sender_partnership, exchange.sender_keystore, _payload)
        del headers['AS2-Version']

        result = handle(body, headers, exchange.receiver_partnerships, exchange.receiver_keystore)

        assert not result.is_error
        assert result.payloads[0].data == _payload

# ################################################################################################################################

    def test_quoted_identifiers(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.as2_from = 'Zato Retail'
        exchange.sender_partnership.as2_to = 'Partner:Corp'

        receiver_partnership = exchange.receiver_partnerships[0]
        receiver_partnership.as2_from = 'Partner:Corp'
        receiver_partnership.as2_to = 'Zato Retail'

        result = do_send(exchange)

        # Identifiers with a space or a colon travel as quoted-strings ..
        request = exchange.requests[0]
        assert request.headers['as2-from'] == '"Zato Retail"'
        assert request.headers['as2-to'] == '"Partner:Corp"'

        # .. and the receiver unquoted them back before matching the partnership.
        inbound = exchange.results[0]
        assert inbound.as2_from == 'Zato Retail'
        assert inbound.as2_to == 'Partner:Corp'
        assert not inbound.is_error

        assert result.is_ok

# ################################################################################################################################

    def test_ediint_features_are_surfaced(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        _ = do_send(exchange)

        inbound = exchange.results[0]
        assert inbound.ediint_features == 'multiple-attachments, AS2-Reliability'

# ################################################################################################################################
# ################################################################################################################################

class TestTransferModes:
    """ Content-Length is the default framing, chunked is per partner, threshold switches on size.
    """

    def test_content_length_by_default(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        result = do_send(exchange)

        request = exchange.requests[0]
        assert 'content-length' in request.headers
        assert 'transfer-encoding' not in request.headers

        assert result.is_ok

# ################################################################################################################################

    def test_chunked(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.http_transfer_mode = TransferMode.Chunked

        result = do_send(exchange)

        request = exchange.requests[0]
        assert request.headers['transfer-encoding'] == 'chunked'
        assert 'content-length' not in request.headers

        assert result.is_ok

# ################################################################################################################################

    def test_threshold_switches_to_chunked(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.http_transfer_mode = TransferMode.Threshold
        exchange.sender_partnership.chunked_threshold_bytes = 16

        result = do_send(exchange)

        request = exchange.requests[0]
        assert request.headers['transfer-encoding'] == 'chunked'

        assert result.is_ok

# ################################################################################################################################

    def test_threshold_keeps_content_length_below_it(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.http_transfer_mode = TransferMode.Threshold
        exchange.sender_partnership.chunked_threshold_bytes = 100 * 1024 * 1024

        result = do_send(exchange)

        request = exchange.requests[0]
        assert 'content-length' in request.headers
        assert 'transfer-encoding' not in request.headers

        assert result.is_ok

# ################################################################################################################################

    def test_basic_auth(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        auth = HTTPAuth()
        auth.username = 'zato.retail'
        auth.password = 'Test password'

        exchange.sender_partnership.http_auth = auth

        result = do_send(exchange)

        request = exchange.requests[0]
        assert request.headers['authorization'].startswith('Basic ')

        assert result.is_ok

# ################################################################################################################################
# ################################################################################################################################

class TestMDNModes:
    """ Synchronous, asynchronous and no MDN at all.
    """

    def test_no_mdn_requested(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.mdn_mode = MDNMode.None_

        result = do_send(exchange)

        assert result.is_ok
        assert result.mdn is None
        assert result.http_status == NO_CONTENT

        request = exchange.requests[0]
        assert 'disposition-notification-to' not in request.headers

        # The payload was still delivered.
        first_payload = exchange.results[0].payloads[0]
        assert first_payload.data == _payload

# ################################################################################################################################

    def test_unsigned_sync_mdn(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.mdn_signed = False

        result = do_send(exchange)

        assert result.is_ok
        assert result.mdn
        assert result.mdn.is_signed is False

# ################################################################################################################################

    def test_signed_sync_mdn(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        result = do_send(exchange)

        assert result.is_ok
        assert result.mdn
        assert result.mdn.is_signed is True
        assert result.mdn.original_message_id == result.message_id

        # The MDN's MIC is the one the receiver computed, matching the sender's.
        digest, _, algorithm = result.mic.partition(', ')
        assert result.mdn.mic == digest
        assert result.mdn.mic_algorithm == algorithm

# ################################################################################################################################

    def test_async_mdn(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.mdn_mode = MDNMode.Async
        exchange.sender_partnership.async_mdn_url = 'https://zatoretail.example.com/zato/as2/mdn'

        result = do_send(exchange)

        # The inbound POST is merely accepted - the MDN travels separately.
        assert result.is_ok
        assert result.mdn is None
        assert result.http_status == ACCEPTED

        request = exchange.requests[0]
        assert request.headers['receipt-delivery-option'] == 'https://zatoretail.example.com/zato/as2/mdn'

        # The receiver prepared the MDN for asynchronous delivery ..
        inbound = exchange.results[0]
        pending = inbound.pending_async_mdn

        assert pending
        assert pending.url == 'https://zatoretail.example.com/zato/as2/mdn'

        # .. and once delivered, it reconciles against the message that was sent.
        mdn = parse_mdn(pending.body, pending.headers['Content-Type'], exchange.sender_keystore)

        assert mdn.is_signed
        assert normalize_message_id(mdn.original_message_id) == normalize_message_id(result.message_id)

        digest, _, algorithm = result.mic.partition(', ')
        assert mdn.mic == digest
        assert mdn.mic_algorithm == algorithm

# ################################################################################################################################

    def test_async_mdn_for_an_unknown_message_id_does_not_match(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.mdn_mode = MDNMode.Async
        exchange.sender_partnership.async_mdn_url = 'https://zatoretail.example.com/zato/as2/mdn'

        result = do_send(exchange)

        pending = exchange.results[0].pending_async_mdn
        mdn = parse_mdn(pending.body, pending.headers['Content-Type'], exchange.sender_keystore)

        # An MDN answering some other message must never reconcile against this one.
        unknown_id = '<already-reconciled-or-unknown@partnercorp.example.com>'

        assert normalize_message_id(mdn.original_message_id) == normalize_message_id(result.message_id)
        assert normalize_message_id(mdn.original_message_id) != normalize_message_id(unknown_id)

# ################################################################################################################################

    def test_the_async_destination_carries_the_partnerships_transport_settings(
        self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.mdn_mode = MDNMode.Async
        exchange.sender_partnership.async_mdn_url = 'https://zatoretail.example.com/zato/as2/mdn'

        receiver_partnership = exchange.receiver_partnerships[0]
        receiver_partnership.verify_tls = False
        receiver_partnership.http_timeout_seconds = 17

        _ = do_send(exchange)

        # The transport settings travel with the pending delivery, so the caller making the
        # outgoing request does not have to reach back for the partnership.
        pending = exchange.results[0].pending_async_mdn

        assert pending.verify_tls is False
        assert pending.timeout_seconds == 17

# ################################################################################################################################
# ################################################################################################################################

class TestAsyncMDNDestination:
    """ The asynchronous MDN destination arrives in the sender's own Receipt-Delivery-Option
    header, so an unchecked one would let a caller choose where the server makes an outgoing
    request to - and the header is read on the error paths too, before the message has proven
    to come from the partner at all.
    """

    def _send_with_destination(self, exchange:'any_', destination:'any_') -> 'any_':
        exchange.sender_partnership.mdn_mode = MDNMode.Async
        exchange.sender_partnership.async_mdn_url = destination

        out = do_send(exchange)
        return out

    def test_the_partners_own_endpoint_host_is_accepted(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        _ = self._send_with_destination(exchange, 'https://zatoretail.example.com/zato/as2/mdn')

        pending = exchange.results[0].pending_async_mdn

        assert pending
        assert pending.url == 'https://zatoretail.example.com/zato/as2/mdn'

# ################################################################################################################################

    def test_another_host_is_refused_and_the_mdn_rides_on_the_response(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        _ = self._send_with_destination(exchange, 'https://attacker.example.net/collect')

        inbound = exchange.results[0]

        # No outgoing request was prepared at all, and the receipt came back on the response
        # instead, which still gets it to whoever made the request.
        assert inbound.pending_async_mdn is None
        assert inbound.status_code == OK
        assert inbound.body

        # The receipt on the response is a real MDN for the message that arrived.
        mdn = parse_mdn(inbound.body, inbound.content_type, exchange.sender_keystore)

        assert mdn.disposition == 'processed'
        assert normalize_message_id(mdn.original_message_id) == inbound.message_id

# ################################################################################################################################

    def test_another_port_on_the_same_host_is_refused(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        # A different port is a different service, so the host matching alone is not enough.
        _ = self._send_with_destination(exchange, 'https://zatoretail.example.com:9443/collect')

        assert exchange.results[0].pending_async_mdn is None

# ################################################################################################################################

    @pytest.mark.parametrize('destination', [
        'file:///etc/passwd',
        'gopher://zatoretail.example.com/1',
        'ftp://zatoretail.example.com/receipts',
    ])
    def test_only_http_and_https_are_accepted(self, parties:'TestParties', destination:'any_') -> 'None':
        exchange = new_exchange(parties)

        _ = self._send_with_destination(exchange, destination)

        assert exchange.results[0].pending_async_mdn is None

# ################################################################################################################################

    def test_an_unknown_partner_may_not_name_a_destination(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        # No partnership matched, so there is nothing to hold the destination against and the
        # caller is a stranger - this is the path an unauthenticated request takes.
        exchange.receiver_partnerships.clear()

        _ = self._send_with_destination(exchange, 'https://attacker.example.net/collect')

        inbound = exchange.results[0]

        assert inbound.partnership is None
        assert inbound.pending_async_mdn is None
        assert inbound.error_modifier == AS2Error.Unknown_Trading_Relationship

# ################################################################################################################################

    def test_a_rejected_message_may_not_name_a_destination_either(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        # The message fails the partnership's security policy, which is an error path that
        # still builds an MDN - and it must not become an outgoing request of the peer's choosing.
        exchange.sender_partnership.sign = False
        exchange.sender_partnership.encrypt = False

        _ = self._send_with_destination(exchange, 'https://attacker.example.net/collect')

        inbound = exchange.results[0]

        assert inbound.is_error
        assert inbound.pending_async_mdn is None

# ################################################################################################################################

    def test_a_partnership_without_an_endpoint_accepts_no_destination(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        # A receive-only partnership names no endpoint, so no host can be established
        # as the partner's own.
        exchange.receiver_partnerships[0].endpoint_url = ''

        _ = self._send_with_destination(exchange, 'https://zatoretail.example.com/zato/as2/mdn')

        assert exchange.results[0].pending_async_mdn is None

# ################################################################################################################################
# ################################################################################################################################

class TestReliability:
    """ The resend semantics - the same content travels under the same Message-ID
    because no MDN arrived for the original attempt.
    """

    def test_resend_reuses_the_message_id(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        first = do_send(exchange)

        # The resend goes out under the original Message-ID ..
        second = do_send(exchange, message_id=first.message_id)

        assert second.message_id == first.message_id

        # .. and both attempts reconcile, the second one against the stored MDN.
        assert first.is_ok
        assert second.is_ok

# ################################################################################################################################

    def test_fresh_sends_get_fresh_message_ids(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        first = do_send(exchange)
        second = do_send(exchange)

        assert first.message_id != second.message_id
        assert not exchange.results[1].is_duplicate

# ################################################################################################################################
# ################################################################################################################################

class TestDuplicateDetection:
    """ A replay of an already-processed message is answered with the stored MDN bytes,
    byte for byte, and its payload is never delivered a second time.
    """

    def test_duplicate_gets_the_stored_mdn_bytes(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        first = do_send(exchange)
        second = do_send(exchange, message_id=first.message_id)

        # The second delivery was recognized as a replay ..
        first_inbound = exchange.results[0]
        second_inbound = exchange.results[1]

        assert not first_inbound.is_duplicate
        assert second_inbound.is_duplicate

        # .. its payload was not delivered again ..
        assert len(first_inbound.payloads) == 1
        assert len(second_inbound.payloads) == 0

        # .. and the MDN bytes went out exactly as stored, never recomputed.
        assert second.response_body == first.response_body
        assert second_inbound.body == first_inbound.body

# ################################################################################################################################

    def test_different_message_ids_are_not_duplicates(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        _ = do_send(exchange)
        _ = do_send(exchange)

        assert not exchange.results[0].is_duplicate
        assert not exchange.results[1].is_duplicate

        # Both deliveries handed their payload over.
        assert len(exchange.results[0].payloads) == 1
        assert len(exchange.results[1].payloads) == 1

# ################################################################################################################################
# ################################################################################################################################

class TestMultipleAttachments:
    """ Several documents ride together in a multipart/related - the ship-notice-plus-PDF shape.
    """

    def test_two_documents_roundtrip(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.preserve_filename = True

        pdf_data = b'%PDF-1.7 Test bill of lading content'

        payload = [
            PayloadItem(_payload, 'application/edi-x12', 'ship-notice-856.edi'),
            PayloadItem(pdf_data, 'application/pdf', 'bill-of-lading.pdf'),
        ]

        result = do_send(exchange, payload=payload)

        assert result.is_ok

        inbound = exchange.results[0]
        assert len(inbound.payloads) == 2

        first, second = inbound.payloads

        assert first.data == _payload
        assert first.content_type == 'application/edi-x12'
        assert first.filename == 'ship-notice-856.edi'

        assert second.data == pdf_data
        assert second.content_type == 'application/pdf'
        assert second.filename == 'bill-of-lading.pdf'

# ################################################################################################################################

    def test_filename_preservation_for_a_single_document(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.preserve_filename = True

        result = do_send(exchange, filename='po-850.edi')

        assert result.is_ok

        inbound = exchange.results[0]
        assert inbound.payloads[0].filename == 'po-850.edi'

# ################################################################################################################################

    def test_no_filename_without_preservation(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        result = do_send(exchange, filename='po-850.edi')

        assert result.is_ok

        inbound = exchange.results[0]
        assert inbound.payloads[0].filename == ''

# ################################################################################################################################
# ################################################################################################################################

class TestPeerSuppliedFilename:
    """ The filename arrives from the peer and travels into the routed message and the stored
    audit data. Nothing here writes a file under it, but a service or subscriber that does would
    be the one exposed, so it is reduced to a plain name at this boundary instead.
    """

    @pytest.mark.parametrize('sent,expected', [
        ('../../../etc/passwd', 'passwd'),
        ('..\\..\\windows\\system32\\config', 'config'),
        ('/absolute/path/po-850.edi', 'po-850.edi'),
        ('subdir/po-850.edi', 'po-850.edi'),
        ('..', ''),
        ('...', ''),
        ('/', ''),
        ('po-850.edi', 'po-850.edi'),
    ])
    def test_the_name_is_reduced_to_a_plain_one(self, parties:'TestParties', sent:'any_', expected:'any_') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.preserve_filename = True

        result = do_send(exchange, filename=sent)

        assert result.is_ok

        inbound = exchange.results[0]
        assert inbound.payloads[0].filename == expected

# ################################################################################################################################

    def test_a_name_longer_than_a_filesystem_accepts_is_truncated(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.preserve_filename = True

        result = do_send(exchange, filename='a' * 400)

        assert result.is_ok

        received = exchange.results[0]
        assert len(received.payloads[0].filename) == inbound_payloads._max_filename_length

# ################################################################################################################################
# ################################################################################################################################

class TestErrorDispositions:
    """ Failures still produce an MDN with the matching disposition modifier.
    """

    def test_tampered_content_yields_integrity_check_failed(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        set_security(exchange, True, False)

        def _tampering_handler(request:'httpx.Request') -> 'any_':
            body = request.read()

            # Flip payload bytes inside the signed entity before it reaches the receiver.
            tampered = body.replace(b'4523891', b'4523892')

            inbound = handle(
                tampered, dict(request.headers), exchange.receiver_partnerships, exchange.receiver_keystore)
            exchange.results.append(inbound)

            response = httpx.Response(inbound.status_code, content=inbound.body, headers=inbound.headers)
            return response

        transport = httpx.MockTransport(_tampering_handler)
        exchange.client = httpx.Client(transport=transport)

        result = do_send(exchange)

        # The sender learns from the MDN that delivery failed ..
        assert not result.is_ok
        assert result.mdn
        assert result.mdn.modifier == AS2Error.Integrity_Check_Failed

        # .. and the receiver never handed the payload over.
        inbound = exchange.results[0]
        assert inbound.is_error
        assert inbound.error_modifier == AS2Error.Integrity_Check_Failed
        assert len(inbound.payloads) == 0

# ################################################################################################################################

    def test_wrong_key_yields_decryption_failed(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        # The receiver's own certificate is not the one this message was encrypted to -
        # the fixture is session-scoped, so the change is always undone.
        exchange.sender_keystore.peer_encryption_certificate = parties.sender.signing_certificate

        try:
            result = do_send(exchange)

            assert not result.is_ok
            assert result.mdn
            assert result.mdn.modifier == AS2Error.Decryption_Failed

        finally:
            exchange.sender_keystore.peer_encryption_certificate = parties.receiver.signing_certificate

# ################################################################################################################################

    def test_error_mdn_is_signed_when_a_signed_receipt_was_requested(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        set_security(exchange, True, False)

        def _tampering_handler(request:'httpx.Request') -> 'any_':
            body = request.read()
            tampered = body.replace(b'4523891', b'4523892')

            result = handle(
                tampered, dict(request.headers), exchange.receiver_partnerships, exchange.receiver_keystore)
            exchange.results.append(result)

            response = httpx.Response(result.status_code, content=result.body, headers=result.headers)
            return response

        transport = httpx.MockTransport(_tampering_handler)
        exchange.client = httpx.Client(transport=transport)

        result = do_send(exchange)

        assert not result.is_ok
        assert result.mdn
        assert result.mdn.is_signed is True

# ################################################################################################################################

    def test_unknown_partner_gets_an_unsigned_explanatory_mdn(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        # The receiver has no partnership for this identity pair at all.
        exchange.receiver_partnerships.clear()

        result = do_send(exchange)

        assert not result.is_ok
        assert result.mdn
        assert result.mdn.is_signed is False
        assert result.mdn.modifier == AS2Error.Unknown_Trading_Relationship

        inbound = exchange.results[0]
        assert inbound.is_error
        assert inbound.error_modifier == AS2Error.Unknown_Trading_Relationship
        assert inbound.partnership is None

# ################################################################################################################################

    def test_unsupported_mic_algorithms_yield_a_failure_mdn(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        body, headers, _, _ = build_message(exchange.sender_partnership, exchange.sender_keystore, _payload)

        # The sender insists on a MIC algorithm nobody supports.
        headers['Disposition-Notification-Options'] = \
            'signed-receipt-protocol=required, pkcs7-signature; signed-receipt-micalg=required, md5'

        result = handle(body, headers, exchange.receiver_partnerships, exchange.receiver_keystore)

        assert result.is_error
        assert result.status_code == OK

        # The answer is a failed/Failure MDN, still signed because a signed receipt was requested.
        mdn = parse_mdn(result.body, result.content_type, exchange.sender_keystore)

        assert mdn.is_signed
        assert mdn.disposition == 'failed'
        assert mdn.modifier_kind == 'failure'
        assert mdn.modifier == 'unsupported MIC-algorithms'

# ################################################################################################################################
# ################################################################################################################################

class TestInboundBounds:
    """ Every unbounded quantity on the pre-authentication path has a ceiling, because all of it
    runs before the message is known to come from the partner at all.
    """

    def test_an_oversized_body_is_turned_down(self, parties:'TestParties', monkeypatch:'any_') -> 'None':
        exchange = new_exchange(parties)

        # A ceiling low enough to cross without building a genuinely huge request.
        monkeypatch.setattr(inbound_pipeline, 'Max_Inbound_Bytes', 16)

        result = do_send(exchange)

        assert not result.is_ok

        inbound_result = exchange.results[0]

        assert inbound_result.is_error
        assert inbound_result.error_modifier == AS2Error.Unexpected_Processing_Error
        assert len(inbound_result.payloads) == 0

# ################################################################################################################################

    def test_a_body_within_the_ceiling_is_accepted(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        result = do_send(exchange)

        assert result.is_ok
        assert exchange.results[0].payloads[0].data == _payload

# ################################################################################################################################

    def test_stacked_layers_are_turned_down(self, parties:'TestParties', monkeypatch:'any_') -> 'None':
        exchange = new_exchange(parties)

        # Signing plus encryption is two layers, so a ceiling of one is crossed by the
        # ordinary message the sender builds, exercising the same guard a stacked one would.
        monkeypatch.setattr(inbound_layers, 'Max_Layer_Depth', 1)

        result = do_send(exchange)

        assert not result.is_ok

        inbound_result = exchange.results[0]

        assert inbound_result.is_error
        assert inbound_result.error_modifier == AS2Error.Unexpected_Processing_Error
        assert len(inbound_result.payloads) == 0

# ################################################################################################################################

    def test_the_ordinary_layer_count_stays_within_the_ceiling(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        # Compression, signing and encryption together - the deepest shape real messages use.
        exchange.sender_partnership.compress = True

        result = do_send(exchange)

        assert result.is_ok
        assert exchange.results[0].payloads[0].data == _payload

# ################################################################################################################################
# ################################################################################################################################

class TestInboundSecurityPolicy:
    """ The partnership's own signing and encryption terms are enforced on what arrives,
    not merely on what we send - otherwise the identity pair, which travels in the clear
    in every message, would be the only thing standing between a stranger and a delivered document.
    """

    def test_unsigned_message_is_rejected_when_the_partnership_requires_signing(
        self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        # The sender drops signing while the receiving side still requires it.
        exchange.sender_partnership.sign = False

        result = do_send(exchange)

        assert not result.is_ok
        assert result.mdn
        assert result.mdn.modifier == AS2Error.Insufficient_Message_Security

        # Nothing was handed over to the application.
        inbound = exchange.results[0]

        assert inbound.is_error
        assert inbound.error_modifier == AS2Error.Insufficient_Message_Security
        assert len(inbound.payloads) == 0

# ################################################################################################################################

    def test_unencrypted_message_is_rejected_when_the_partnership_requires_encryption(
        self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        exchange.sender_partnership.encrypt = False

        result = do_send(exchange)

        assert not result.is_ok
        assert result.mdn
        assert result.mdn.modifier == AS2Error.Insufficient_Message_Security

        inbound = exchange.results[0]

        assert inbound.is_error
        assert inbound.error_modifier == AS2Error.Insufficient_Message_Security
        assert len(inbound.payloads) == 0

# ################################################################################################################################

    def test_plaintext_post_is_rejected_when_the_partnership_requires_both(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        # The bare payload with only the AS2 identity headers, which is what an attacker
        # who merely read one of the partner's messages is able to construct.
        exchange.sender_partnership.sign = False
        exchange.sender_partnership.encrypt = False

        result = do_send(exchange)

        assert not result.is_ok
        assert exchange.bodies[0] == _payload

        inbound = exchange.results[0]

        assert inbound.is_error
        assert inbound.error_modifier == AS2Error.Insufficient_Message_Security
        assert len(inbound.payloads) == 0

# ################################################################################################################################

    def test_the_error_mdn_still_reports_the_received_content_mic(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        exchange.sender_partnership.sign = False
        exchange.sender_partnership.encrypt = False

        _ = do_send(exchange)

        # The MIC is computed before the policy check, so the partner can tell
        # which message we turned down.
        inbound = exchange.results[0]
        assert inbound.mic

# ################################################################################################################################

    def test_a_partnership_requiring_nothing_accepts_a_plaintext_post(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        set_security(exchange, False, False)

        result = do_send(exchange)

        assert result.is_ok

        inbound = exchange.results[0]
        assert not inbound.is_error
        assert inbound.payloads[0].data == _payload

# ################################################################################################################################

    def test_more_security_than_required_is_accepted(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        # The receiving side asks for signing alone while the sender also encrypts -
        # the requirement is a floor, not an exact match.
        for partnership in exchange.receiver_partnerships:
            partnership.encrypt = False

        result = do_send(exchange)

        assert result.is_ok

        inbound = exchange.results[0]
        assert not inbound.is_error
        assert inbound.payloads[0].data == _payload

# ################################################################################################################################
# ################################################################################################################################

def _certificate_entry(certificate:'any_', valid_from:'any_'=None, valid_until:'any_'=None) -> 'any_':
    """ Builds one entry of a partner's certificate rotation list.
    """
    out = CertificateEntry()

    out.certificate = certificate
    out.valid_from = valid_from
    out.valid_until = valid_until

    return out

# ################################################################################################################################

def _rotated_sender_keystore(parties:'TestParties', rotated:'any_') -> 'any_':
    """ The sending side's keystore after it rotated its signing pair -
    encryption and MDN verification still target the receiver's current certificate.
    """
    out = new_keystore()

    out.signing_key = rotated.key
    out.signing_certificate_chain = [rotated.certificate]
    out.peer_encryption_certificate = parties.receiver.signing_certificate
    out.peer_signing_certificate = parties.receiver.signing_certificate

    return out

# ################################################################################################################################

def _receiver_keystore_with_entry(parties:'TestParties', rotated:'any_') -> 'any_':
    """ The receiving side's keystore during a rotation of its own decryption pair -
    the old key stays primary while the new pair joins the rotation entries.
    """
    out = new_keystore()

    out.signing_key = parties.receiver.signing_key
    out.signing_certificate_chain = parties.receiver.signing_certificate_chain
    out.decryption_key = parties.receiver.decryption_key
    out.peer_signing_certificate = parties.receiver.peer_signing_certificate

    entry = DecryptionEntry()
    entry.key = rotated.key
    entry.certificate = rotated.certificate
    out.decryption_entries.append(entry)

    return out

# ################################################################################################################################

def _receiver_keystore_signing_with(parties:'TestParties', rotated:'any_') -> 'any_':
    """ The receiving side's keystore after it rotated its signing pair - the old
    decryption pair stays on the rotation entries so incoming messages still decrypt.
    """
    out = new_keystore()

    out.signing_key = rotated.key
    out.signing_certificate_chain = [rotated.certificate]
    out.decryption_key = parties.receiver.decryption_key
    out.peer_signing_certificate = parties.receiver.peer_signing_certificate

    entry = DecryptionEntry()
    entry.key = parties.receiver.decryption_key
    entry.certificate = parties.receiver.signing_certificate
    out.decryption_entries.append(entry)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestCertificateRotation:
    """ The overlap window end to end - more than two live certificates, staged activation,
    encryption following the most recently activated certificate and rotation of our own keys.
    """

    def test_overlap_window_accepts_signatures_from_all_live_certificates(self, parties:'TestParties', make_rotated_pair:'any_') -> 'None':
        exchange = new_exchange(parties)

        first_rotated = make_rotated_pair('as2-sender-rotation-first')
        second_rotated = make_rotated_pair('as2-sender-rotation-second')

        now = datetime.now(timezone.utc)

        # Three of the partner's certificates are live at once - the original one
        # plus two staged rotations whose activation dates have passed.
        receiver_partnership = exchange.receiver_partnerships[0]

        receiver_partnership.verification_certificates.append(
            _certificate_entry(parties.sender.signing_certificate))
        receiver_partnership.verification_certificates.append(
            _certificate_entry(first_rotated.certificate, valid_from=now - timedelta(days=2)))
        receiver_partnership.verification_certificates.append(
            _certificate_entry(second_rotated.certificate, valid_from=now - timedelta(days=1)))

        # A message signed with each of the three keys is accepted.
        result = do_send(exchange)
        assert result.is_ok

        exchange.sender_keystore = _rotated_sender_keystore(parties, first_rotated)
        result = do_send(exchange)
        assert result.is_ok

        exchange.sender_keystore = _rotated_sender_keystore(parties, second_rotated)
        result = do_send(exchange)
        assert result.is_ok

        for inbound in exchange.results:
            assert not inbound.is_error
            assert inbound.payloads[0].data == _payload

# ################################################################################################################################

    def test_a_not_yet_activated_certificate_is_rejected(self, parties:'TestParties', make_rotated_pair:'any_') -> 'None':
        exchange = new_exchange(parties)

        rotated = make_rotated_pair('as2-sender-rotation-early')
        now = datetime.now(timezone.utc)

        # The staged certificate only activates a month from now.
        receiver_partnership = exchange.receiver_partnerships[0]

        receiver_partnership.verification_certificates.append(
            _certificate_entry(parties.sender.signing_certificate))
        receiver_partnership.verification_certificates.append(
            _certificate_entry(rotated.certificate, valid_from=now + timedelta(days=30)))

        # A message already signed with the staged key is not accepted yet.
        exchange.sender_keystore = _rotated_sender_keystore(parties, rotated)
        result = do_send(exchange)

        assert not result.is_ok
        assert result.mdn
        assert result.mdn.modifier == AS2Error.Authentication_Failed

        inbound = exchange.results[0]
        assert inbound.is_error
        assert inbound.error_modifier == AS2Error.Authentication_Failed

# ################################################################################################################################

    def test_outbound_encrypts_to_the_most_recently_activated_certificate(self, parties:'TestParties', make_rotated_pair:'any_') -> 'None':
        exchange = new_exchange(parties)

        rotated = make_rotated_pair('as2-receiver-rotation')
        now = datetime.now(timezone.utc)

        # The partner's rotation list holds the current certificate plus an activated next one.
        sender_partnership = exchange.sender_partnership

        sender_partnership.encryption_certificates.append(
            _certificate_entry(parties.receiver.signing_certificate))
        sender_partnership.encryption_certificates.append(
            _certificate_entry(rotated.certificate, valid_from=now - timedelta(days=1)))

        # The receiver still runs with its old key alone, so a message encrypted
        # to the next certificate does not decrypt there - the wire-level proof
        # that encryption switched over.
        result = do_send(exchange)

        assert not result.is_ok
        assert result.mdn
        assert result.mdn.modifier == AS2Error.Decryption_Failed

        # Once the next key joins the receiver's rotation entries, the same send decrypts.
        exchange.receiver_keystore = _receiver_keystore_with_entry(parties, rotated)

        result = do_send(exchange)

        assert result.is_ok
        assert exchange.results[1].payloads[0].data == _payload

# ################################################################################################################################

    def test_the_old_certificate_still_decrypts_during_our_own_rotation(self, parties:'TestParties', make_rotated_pair:'any_') -> 'None':
        exchange = new_exchange(parties)

        # The receiver already carries its next pair on the rotation entries ..
        rotated = make_rotated_pair('as2-receiver-rotation')
        exchange.receiver_keystore = _receiver_keystore_with_entry(parties, rotated)

        # .. while the sender still encrypts to the old certificate - the primary pair handles it.
        result = do_send(exchange)

        assert result.is_ok
        first_payload = exchange.results[0].payloads[0]
        assert first_payload.data == _payload

# ################################################################################################################################

    def test_sync_mdn_signed_with_the_partners_new_certificate_reconciles(self, parties:'TestParties', make_rotated_pair:'any_') -> 'None':
        exchange = new_exchange(parties)

        rotated = make_rotated_pair('as2-receiver-rotation')
        now = datetime.now(timezone.utc)

        # The receiver already signs its MDNs with the new pair ..
        exchange.receiver_keystore = _receiver_keystore_signing_with(parties, rotated)

        # .. and the sender's rotation list carries both of the partner's certificates.
        sender_partnership = exchange.sender_partnership

        sender_partnership.verification_certificates.append(
            _certificate_entry(parties.receiver.signing_certificate))
        sender_partnership.verification_certificates.append(
            _certificate_entry(rotated.certificate, valid_from=now - timedelta(days=1)))

        result = do_send(exchange)

        assert result.is_ok
        assert result.mdn
        assert result.mdn.signer_certificate.serial_number == rotated.certificate.serial_number

# ################################################################################################################################

    def test_sync_mdn_from_an_unlisted_certificate_does_not_reconcile(self, parties:'TestParties', make_rotated_pair:'any_') -> 'None':
        exchange = new_exchange(parties)

        rotated = make_rotated_pair('as2-receiver-rotation')

        # The receiver signs its MDNs with a pair the sender was never told about ..
        exchange.receiver_keystore = _receiver_keystore_signing_with(parties, rotated)

        # .. and the sender's rotation list only knows the partner's current certificate.
        exchange.sender_partnership.verification_certificates.append(
            _certificate_entry(parties.receiver.signing_certificate))

        result = do_send(exchange)

        # The MDN's signer is not accepted, so it counts as no MDN received.
        assert not result.is_ok
        assert result.mdn is None

# ################################################################################################################################
# ################################################################################################################################
