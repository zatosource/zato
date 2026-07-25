# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from .mdn_helpers import make_request, make_signing_config, Message_ID, sample_mic
from zato.common.as2.common import AS2Error, Failure
from zato.common.as2.mdn import build_mdn, new_error_disposition, new_failure_disposition, new_message_id, \
    new_processed_disposition, parse_mdn

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

class TestBuildUnsignedMDN:

    def test_processed_mdn(self) -> 'None':
        request = make_request()
        mic = sample_mic()
        disposition = new_processed_disposition()

        body, headers = build_mdn(request, disposition, mic)

        # The identities swap places because the MDN flows back to the message's sender.
        assert headers['AS2-From'] == 'ZatoRetail'
        assert headers['AS2-To'] == 'PartnerCorp'
        assert headers['MIME-Version'] == '1.0'
        assert headers['Message-ID'].startswith('<')
        assert headers['Message-ID'].endswith('@zato>')

        assert headers['Content-Type'].startswith('multipart/report; report-type=disposition-notification')

        # The machine-readable fields ride in the body as they will appear on the wire.
        assert b'Reporting-UA: Zato' in body
        assert f'Original-Message-ID: {Message_ID}'.encode('ascii') in body
        assert b'Original-Recipient: rfc822; ZatoRetail' in body
        assert b'Final-Recipient: rfc822; ZatoRetail' in body
        assert f'Received-Content-MIC: {mic}'.encode('ascii') in body
        assert b'Disposition: automatic-action/MDN-sent-automatically; processed' in body

# ################################################################################################################################

    def test_error_mdn_without_mic(self) -> 'None':
        # When decryption failed there is nothing to digest, so the MIC field is absent.
        request = make_request()
        disposition = new_error_disposition(AS2Error.Decryption_Failed)

        body, _ = build_mdn(request, disposition)

        assert b'Received-Content-MIC' not in body
        assert b'Disposition: automatic-action/MDN-sent-automatically; processed/error: decryption-failed' in body

# ################################################################################################################################

    def test_unsupported_receipt_protocol_yields_an_unsigned_mdn(self, parties:'TestParties') -> 'None':
        # An unsigned MDN is the legitimate answer when the requested protocol is not the one AS2 defines.
        request = make_request(requests_signed_mdn=True, signed_receipt_protocol='pgp-signature')
        signing_config = make_signing_config(parties)
        disposition = new_processed_disposition()
        mic = sample_mic()

        _, headers = build_mdn(request, disposition, mic, signing_config)

        assert headers['Content-Type'].startswith('multipart/report')

# ################################################################################################################################

    def test_no_signing_material_yields_an_unsigned_mdn(self) -> 'None':
        # An unknown AS2-From/AS2-To pair gets an unsigned explanatory MDN - there is no partnership
        # to sign under, so no signing material is passed in.
        request = make_request(requests_signed_mdn=True, signed_receipt_protocol='pkcs7-signature')
        disposition = new_error_disposition(AS2Error.Unknown_Trading_Partner)

        body, headers = build_mdn(request, disposition)

        assert headers['Content-Type'].startswith('multipart/report')
        assert b'processed/error: unknown-trading-partner' in body

# ################################################################################################################################
# ################################################################################################################################

class TestBuildSignedMDN:

    def test_signed_processed_mdn_verifies(self, parties:'TestParties') -> 'None':
        options = {
            'requests_signed_mdn': True,
            'signed_receipt_protocol': 'pkcs7-signature',
            'mic_algorithms': ['sha-256'],
        }

        request = make_request(**options)
        signing_config = make_signing_config(parties)
        disposition = new_processed_disposition()
        mic = sample_mic()

        body, headers = build_mdn(request, disposition, mic, signing_config)

        assert headers['Content-Type'].startswith('multipart/signed')

        # The sender verifies the MDN against its own keystore, which trusts the receiver's CA.
        information = parse_mdn(body, headers['Content-Type'], parties.sender)

        assert information.is_signed is True
        assert information.signer_certificate == parties.receiver.signing_certificate
        assert information.original_message_id == Message_ID
        assert information.disposition == 'processed'
        assert information.mic_algorithm == 'sha-256'

# ################################################################################################################################

    def test_signed_receipt_request_is_honored_even_when_processing_failed(self, parties:'TestParties') -> 'None':
        options = {
            'requests_signed_mdn': True,
            'signed_receipt_protocol': 'pkcs7-signature',
            'mic_algorithms': ['sha-256'],
        }

        request = make_request(**options)
        signing_config = make_signing_config(parties)
        disposition = new_error_disposition(AS2Error.Integrity_Check_Failed)

        body, headers = build_mdn(request, disposition, signing_config=signing_config)

        assert headers['Content-Type'].startswith('multipart/signed')

        information = parse_mdn(body, headers['Content-Type'], parties.sender)

        assert information.disposition == 'processed'
        assert information.modifier_kind == 'error'
        assert information.modifier == 'integrity-check-failed'

# ################################################################################################################################

    def test_signature_algorithm_honors_the_request(self, parties:'TestParties') -> 'None':
        options = {
            'requests_signed_mdn': True,
            'signed_receipt_protocol': 'pkcs7-signature',
            'mic_algorithms': ['sha384', 'sha-256'],
        }

        request = make_request(**options)
        signing_config = make_signing_config(parties)
        disposition = new_processed_disposition()
        mic = sample_mic()

        _, headers = build_mdn(request, disposition, mic, signing_config)

        # The first supported algorithm from the request carries the signature,
        # announced in the RFC 5751 spelling regardless of how it was requested.
        assert 'micalg=sha-384' in headers['Content-Type']

# ################################################################################################################################

    def test_unsupported_mic_algorithms_still_get_a_signed_failure_mdn(self, parties:'TestParties') -> 'None':
        # Nothing on the request's list is supported, so the failure MDN reports it -
        # signed all the same, under our own default algorithm.
        options = {
            'requests_signed_mdn': True,
            'signed_receipt_protocol': 'pkcs7-signature',
            'mic_algorithms': ['md5', 'crc32'],
        }

        request = make_request(**options)
        signing_config = make_signing_config(parties)
        disposition = new_failure_disposition(Failure.Unsupported_MIC_Algorithms)

        body, headers = build_mdn(request, disposition, signing_config=signing_config)

        assert headers['Content-Type'].startswith('multipart/signed')
        assert 'micalg=sha-256' in headers['Content-Type']

        information = parse_mdn(body, headers['Content-Type'], parties.sender)

        assert information.disposition == 'failed'
        assert information.modifier_kind == 'failure'
        assert information.modifier == 'unsupported MIC-algorithms'

# ################################################################################################################################
# ################################################################################################################################

class TestMessageID:

    def test_message_ids_are_unique_and_bracketed(self) -> 'None':
        first = new_message_id()
        second = new_message_id()

        assert first != second
        assert first.startswith('<')
        assert first.endswith('@zato>')

# ################################################################################################################################
# ################################################################################################################################
