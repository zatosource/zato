# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from .mdn_helpers import crlf_join, make_request, make_signing_config, Message_ID, sample_mic
from zato.common.as2.common import AS2Error, AS2Exception, AS2ProtocolException, AS2SecurityException, Failure
from zato.common.as2.mdn import build_mdn, new_error_disposition, new_failure_disposition, new_processed_disposition, \
    new_warning_disposition, parse_mdn

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

class TestParseMDN:

    def test_unsigned_roundtrip(self) -> 'None':
        request = make_request()
        mic = sample_mic()
        disposition = new_processed_disposition()

        body, headers = build_mdn(request, disposition, mic)

        information = parse_mdn(body, headers['Content-Type'])

        assert information.is_signed is False
        assert information.signer_certificate is None
        assert information.original_message_id == Message_ID
        assert information.mode == 'automatic-action/MDN-sent-automatically'
        assert information.disposition == 'processed'
        assert information.modifier_kind == ''
        assert information.modifier == ''
        assert f'{information.mic}, {information.mic_algorithm}' == mic
        assert 'MDN for -' in information.text

# ################################################################################################################################

    def test_async_mdn_payload_parses_the_same(self) -> 'None':
        # An asynchronous MDN is the same multipart/report, delivered by a separate POST
        # to the requested URL rather than in the HTTP response.
        request = make_request(async_mdn_url='https://partnercorp.example.com/as2/mdn')
        mic = sample_mic()
        disposition = new_processed_disposition()

        body, headers = build_mdn(request, disposition, mic)

        assert request.async_mdn_url == 'https://partnercorp.example.com/as2/mdn'

        information = parse_mdn(body, headers['Content-Type'])

        assert information.original_message_id == Message_ID
        assert information.disposition == 'processed'
        assert f'{information.mic}, {information.mic_algorithm}' == mic

# ################################################################################################################################

    def test_micalg_spelling_variants_are_normalized(self) -> 'None':
        # A peer's MDN may spell the algorithm without the dash - the parsed name is normalized.
        body = crlf_join([
            '--test-boundary',
            'Content-Type: text/plain',
            '',
            'The message was processed.',
            '--test-boundary',
            'Content-Type: message/disposition-notification',
            '',
            f'Original-Message-ID: {Message_ID}',
            'Received-Content-MIC: q83vEjRWeJA=, sha256',
            'Disposition: automatic-action/MDN-sent-automatically; processed',
            '--test-boundary--',
            '',
        ])
        content_type = 'multipart/report; report-type=disposition-notification; boundary="test-boundary"'

        information = parse_mdn(body, content_type)

        assert information.mic == 'q83vEjRWeJA='
        assert information.mic_algorithm == 'sha-256'

# ################################################################################################################################

    def test_error_and_failure_dispositions_parse(self) -> 'None':
        request = make_request()

        error_disposition = new_error_disposition(AS2Error.Authentication_Failed)
        warning_disposition = new_warning_disposition('duplicate-document')
        failure_disposition = new_failure_disposition(Failure.Unsupported_Format)

        expected = [
            (error_disposition, 'processed', 'error', 'authentication-failed'),
            (warning_disposition, 'processed', 'warning', 'duplicate-document'),
            (failure_disposition, 'failed', 'failure', 'unsupported format'),
        ]

        for disposition, expected_type, expected_kind, expected_modifier in expected:

            body, headers = build_mdn(request, disposition)

            information = parse_mdn(body, headers['Content-Type'])

            assert information.disposition == expected_type
            assert information.modifier_kind == expected_kind
            assert information.modifier == expected_modifier

# ################################################################################################################################

    def test_tampered_signed_mdn_is_rejected(self, parties:'TestParties') -> 'None':
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

        tampered = body.replace(b'processed', b'PROCESSED', 1)

        with pytest.raises(AS2SecurityException) as exception_info:
            _ = parse_mdn(tampered, headers['Content-Type'], parties.sender)

        assert exception_info.value.modifier == AS2Error.Integrity_Check_Failed

# ################################################################################################################################

    def test_signed_mdn_without_a_keystore_is_rejected(self, parties:'TestParties') -> 'None':
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

        with pytest.raises(AS2Exception):
            _ = parse_mdn(body, headers['Content-Type'])

# ################################################################################################################################

    def test_accepted_certificates_admit_a_listed_signer(
        self,
        parties:'TestParties',
        make_rotated_pair:'any_',
        ) -> 'None':

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

        # The rotation list holds both of the partner's certificates and the actual signer is one of them.
        rotated = make_rotated_pair('as2-receiver-rotation')
        accepted = [rotated.certificate, parties.receiver.signing_certificate]

        information = parse_mdn(body, headers['Content-Type'], parties.sender, accepted)

        assert information.is_signed is True
        assert information.signer_certificate == parties.receiver.signing_certificate

# ################################################################################################################################

    def test_accepted_certificates_reject_an_unlisted_signer(
        self,
        parties:'TestParties',
        make_rotated_pair:'any_',
        ) -> 'None':

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

        # The rotation list does not include the actual signer, so even the keystore's
        # own trust does not admit it - the list is the trust decision.
        rotated = make_rotated_pair('as2-receiver-rotation')
        accepted = [rotated.certificate]

        with pytest.raises(AS2SecurityException) as exception_info:
            _ = parse_mdn(body, headers['Content-Type'], parties.sender, accepted)

        assert exception_info.value.modifier == AS2Error.Authentication_Failed

# ################################################################################################################################

    def test_non_mdn_content_type_is_rejected(self) -> 'None':
        with pytest.raises(AS2ProtocolException) as exception_info:
            _ = parse_mdn(b'Not an MDN at all', 'text/plain')

        assert exception_info.value.modifier == AS2Error.Unexpected_Processing_Error

# ################################################################################################################################

    def test_report_without_a_boundary_is_rejected(self) -> 'None':
        with pytest.raises(AS2ProtocolException) as exception_info:
            _ = parse_mdn(b'Not a valid report body', 'multipart/report; report-type=disposition-notification')

        assert exception_info.value.modifier == AS2Error.Unexpected_Processing_Error

# ################################################################################################################################
# ################################################################################################################################
