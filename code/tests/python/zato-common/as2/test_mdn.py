# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.as2.common import AS2Error, AS2Exception, AS2ProtocolException, AS2SecurityException, Failure
from zato.common.as2.mdn import build_mdn, disposition_from_exception, format_disposition, is_known_modifier, MDNRequest, \
    MDNSigningConfig, new_error_disposition, new_failure_disposition, new_message_id, new_processed_disposition, \
    new_warning_disposition, parse_disposition, parse_mdn, parse_mdn_request
from zato.common.as2.smime import compute_mic, new_part

# ################################################################################################################################
# ################################################################################################################################

_message_id = '<20260709100000.12345@sender.example.com>'

# ################################################################################################################################
# ################################################################################################################################

def _make_request(
    requests_signed_mdn=False,
    signed_receipt_protocol='',
    mic_algorithms=None,
    async_mdn_url='',
    ):
    """ Returns an MDN request the way the inbound pipeline would have parsed it.
    """
    out = MDNRequest()

    out.message_id = _message_id
    out.as2_from = 'PartnerCorp'
    out.as2_to = 'ZatoRetail'
    out.requests_mdn = True
    out.requests_signed_mdn = requests_signed_mdn
    out.signed_receipt_protocol = signed_receipt_protocol

    if mic_algorithms:
        out.mic_algorithms = mic_algorithms

    out.async_mdn_url = async_mdn_url

    return out

# ################################################################################################################################

def _make_signing_config(parties):
    out = MDNSigningConfig()
    out.keystore = parties.receiver

    return out

# ################################################################################################################################

def _sample_mic():
    """ A MIC over a sample payload, the way the inbound pipeline would have computed it.
    """
    part = new_part(b'ISA*00*          *00*          *', 'application/edi-x12', 'binary')

    out = compute_mic(part, is_signed=True, is_encrypted=False)
    return out

# ################################################################################################################################

def _crlf_join(lines):
    """ Joins wire-format lines with CRLF, the way an AS2 peer would have sent them.
    """
    encoded:'list[bytes]' = []

    for line in lines:
        encoded.append(line.encode('utf-8'))

    out = b'\r\n'.join(encoded)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestDispositionFormatting:
    """ The historic RFC 4130 constructions are what every AS2 implementation accepts,
    so they are the only form ever emitted.
    """

    def test_processed(self):
        disposition = new_processed_disposition()

        assert format_disposition(disposition) == 'automatic-action/MDN-sent-automatically; processed'

    def test_processed_error(self):
        disposition = new_error_disposition(AS2Error.Decryption_Failed)

        assert format_disposition(disposition) == 'automatic-action/MDN-sent-automatically; processed/error: decryption-failed'

    def test_processed_warning(self):
        disposition = new_warning_disposition('duplicate-document')

        assert format_disposition(disposition) == \
            'automatic-action/MDN-sent-automatically; processed/warning: duplicate-document'

    def test_failed_failure(self):
        disposition = new_failure_disposition(Failure.Unsupported_MIC_Algorithms)

        assert format_disposition(disposition) == \
            'automatic-action/MDN-sent-automatically; failed/Failure: unsupported MIC-algorithms'

# ################################################################################################################################
# ################################################################################################################################

class TestDispositionSelection:
    """ The disposition table - error modifiers ride on processed/error, while failure descriptions,
    reserved for problems with the MDN request itself, ride on failed/Failure.
    """

    @pytest.mark.parametrize('modifier', [
        AS2Error.Integrity_Check_Failed,
        AS2Error.Authentication_Failed,
        AS2Error.Decryption_Failed,
        AS2Error.Decompression_Failed,
        AS2Error.Unexpected_Processing_Error,
    ])
    def test_content_processing_problems_are_errors(self, modifier):
        exception = AS2SecurityException(modifier, 'Test error detail')

        disposition = disposition_from_exception(exception)

        assert disposition.disposition_type == 'processed'
        assert disposition.modifier_kind == 'error'
        assert disposition.modifier == modifier

    @pytest.mark.parametrize('description', [
        Failure.Unsupported_Format,
        Failure.Unsupported_MIC_Algorithms,
    ])
    def test_mdn_request_problems_are_failures(self, description):
        exception = AS2ProtocolException(description, 'Test failure detail')

        disposition = disposition_from_exception(exception)

        assert disposition.disposition_type == 'failed'
        assert disposition.modifier_kind == 'failure'
        assert disposition.modifier == description

# ################################################################################################################################
# ################################################################################################################################

class TestDispositionParsing:

    def test_historic_processed(self):
        disposition = parse_disposition('automatic-action/MDN-sent-automatically; processed')

        assert disposition.mode == 'automatic-action/MDN-sent-automatically'
        assert disposition.disposition_type == 'processed'
        assert disposition.modifier_kind == ''
        assert disposition.modifier == ''

    def test_historic_error(self):
        disposition = parse_disposition('automatic-action/MDN-sent-automatically; processed/error: authentication-failed')

        assert disposition.disposition_type == 'processed'
        assert disposition.modifier_kind == 'error'
        assert disposition.modifier == 'authentication-failed'

    def test_historic_failure(self):
        disposition = parse_disposition('automatic-action/MDN-sent-automatically; failed/Failure: unsupported format')

        assert disposition.disposition_type == 'failed'
        assert disposition.modifier_kind == 'failure'
        assert disposition.modifier == 'unsupported format'

    def test_capitalized_error_kind_is_accepted(self):
        disposition = parse_disposition('automatic-action/MDN-sent-automatically; processed/Error: decryption-failed')

        assert disposition.modifier_kind == 'error'
        assert disposition.modifier == 'decryption-failed'

    def test_rfc_8098_bare_modifier_form(self):
        # The RFC 8098 form may carry the bare kind alone, with the details in separate fields.
        disposition = parse_disposition('automatic-action/MDN-sent-automatically; processed/error')

        assert disposition.disposition_type == 'processed'
        assert disposition.modifier_kind == 'error'
        assert disposition.modifier == ''

    def test_manual_action_mode(self):
        disposition = parse_disposition('manual-action/MDN-sent-manually; processed')

        assert disposition.mode == 'manual-action/MDN-sent-manually'
        assert disposition.disposition_type == 'processed'

    def test_mode_may_be_absent(self):
        disposition = parse_disposition('processed/error: decryption-failed')

        assert disposition.disposition_type == 'processed'
        assert disposition.modifier_kind == 'error'
        assert disposition.modifier == 'decryption-failed'

    def test_modifier_is_never_split_on_a_comma(self):
        value = 'automatic-action/MDN-sent-automatically; processed/warning: authentication-failed, processing continued'

        disposition = parse_disposition(value)

        assert disposition.modifier_kind == 'warning'
        assert disposition.modifier == 'authentication-failed, processing continued'

    def test_emitted_form_parses_back(self):
        original = new_error_disposition(AS2Error.Integrity_Check_Failed)

        parsed = parse_disposition(format_disposition(original))

        assert parsed.mode == original.mode
        assert parsed.disposition_type == original.disposition_type
        assert parsed.modifier_kind == original.modifier_kind
        assert parsed.modifier == original.modifier

# ################################################################################################################################
# ################################################################################################################################

class TestKnownModifiers:
    """ The registry modifiers of the AS2 specification modernization draft parse as known values.
    """

    @pytest.mark.parametrize('modifier', [
        'authentication-failed',
        'decompression-failed',
        'decryption-failed',
        'duplicate-filename',
        'illegal-filename',
        'insufficient-message-security',
        'integrity-check-failed',
        'invalid-message-id',
        'unexpected-processing-error',
        'unknown-trading-partner',
        'unknown-trading-relationship',
    ])
    def test_registry_modifiers_are_known(self, modifier):
        assert is_known_modifier(modifier)

    def test_free_text_is_not_a_registry_value(self):
        assert not is_known_modifier('sender-equals-receiver')

# ################################################################################################################################
# ################################################################################################################################

class TestMDNRequestParsing:

    def test_full_signed_sync_request(self):
        headers = {
            'message-id': _message_id,
            'as2-from': 'PartnerCorp',
            'as2-to': 'ZatoRetail',
            'disposition-notification-to': 'edi@partnercorp.example.com',
            'disposition-notification-options':
                'signed-receipt-protocol=optional, pkcs7-signature; signed-receipt-micalg=optional, sha-256, sha1',
        }

        request = parse_mdn_request(headers)

        assert request.message_id == _message_id
        assert request.as2_from == 'PartnerCorp'
        assert request.as2_to == 'ZatoRetail'
        assert request.requests_mdn is True
        assert request.requests_signed_mdn is True
        assert request.signed_receipt_protocol == 'pkcs7-signature'
        assert request.mic_algorithms == ['sha-256', 'sha1']
        assert request.async_mdn_url == ''

    def test_async_request(self):
        headers = {
            'message-id': _message_id,
            'as2-from': 'PartnerCorp',
            'as2-to': 'ZatoRetail',
            'disposition-notification-to': 'edi@partnercorp.example.com',
            'receipt-delivery-option': 'https://partnercorp.example.com/as2/mdn',
        }

        request = parse_mdn_request(headers)

        assert request.requests_mdn is True
        assert request.requests_signed_mdn is False
        assert request.async_mdn_url == 'https://partnercorp.example.com/as2/mdn'

    def test_no_mdn_requested(self):
        headers = {
            'message-id': _message_id,
            'as2-from': 'PartnerCorp',
            'as2-to': 'ZatoRetail',
        }

        request = parse_mdn_request(headers)

        assert request.requests_mdn is False
        assert request.requests_signed_mdn is False

    def test_empty_protocol_value_is_tolerated(self):
        # The specification shows this degenerate shape explicitly - it must not be rejected.
        headers = {
            'message-id': _message_id,
            'disposition-notification-to': 'edi@partnercorp.example.com',
            'disposition-notification-options': 'signed-receipt-protocol=optional,; signed-receipt-micalg=optional,,,',
        }

        request = parse_mdn_request(headers)

        assert request.requests_mdn is True
        assert request.requests_signed_mdn is False
        assert request.signed_receipt_protocol == ''
        assert request.mic_algorithms == []

# ################################################################################################################################
# ################################################################################################################################

class TestBuildUnsignedMDN:

    def test_processed_mdn(self):
        request = _make_request()
        mic = _sample_mic()

        body, headers = build_mdn(request, new_processed_disposition(), mic)

        # The identities swap places because the MDN flows back to the message's sender.
        assert headers['AS2-From'] == 'ZatoRetail'
        assert headers['AS2-To'] == 'PartnerCorp'
        assert headers['MIME-Version'] == '1.0'
        assert headers['Message-ID'].startswith('<')
        assert headers['Message-ID'].endswith('@zato>')

        assert headers['Content-Type'].startswith('multipart/report; report-type=disposition-notification')

        # The machine-readable fields ride in the body as they will appear on the wire.
        assert b'Reporting-UA: Zato' in body
        assert f'Original-Message-ID: {_message_id}'.encode('ascii') in body
        assert b'Original-Recipient: rfc822; ZatoRetail' in body
        assert b'Final-Recipient: rfc822; ZatoRetail' in body
        assert f'Received-Content-MIC: {mic}'.encode('ascii') in body
        assert b'Disposition: automatic-action/MDN-sent-automatically; processed' in body

    def test_error_mdn_without_mic(self):
        # When decryption failed there is nothing to digest, so the MIC field is absent.
        request = _make_request()
        disposition = new_error_disposition(AS2Error.Decryption_Failed)

        body, _ = build_mdn(request, disposition)

        assert b'Received-Content-MIC' not in body
        assert b'Disposition: automatic-action/MDN-sent-automatically; processed/error: decryption-failed' in body

    def test_unsupported_receipt_protocol_yields_an_unsigned_mdn(self, parties):
        # An unsigned MDN is the legitimate answer when the requested protocol is not the one AS2 defines.
        request = _make_request(requests_signed_mdn=True, signed_receipt_protocol='pgp-signature')
        signing_config = _make_signing_config(parties)

        _, headers = build_mdn(request, new_processed_disposition(), _sample_mic(), signing_config)

        assert headers['Content-Type'].startswith('multipart/report')

    def test_no_signing_material_yields_an_unsigned_mdn(self):
        # An unknown AS2-From/AS2-To pair gets an unsigned explanatory MDN - there is no partnership
        # to sign under, so no signing material is passed in.
        request = _make_request(requests_signed_mdn=True, signed_receipt_protocol='pkcs7-signature')
        disposition = new_error_disposition(AS2Error.Unknown_Trading_Partner)

        body, headers = build_mdn(request, disposition)

        assert headers['Content-Type'].startswith('multipart/report')
        assert b'processed/error: unknown-trading-partner' in body

# ################################################################################################################################
# ################################################################################################################################

class TestBuildSignedMDN:

    def test_signed_processed_mdn_verifies(self, parties):
        request = _make_request(
            requests_signed_mdn=True, signed_receipt_protocol='pkcs7-signature', mic_algorithms=['sha-256'])
        signing_config = _make_signing_config(parties)
        mic = _sample_mic()

        body, headers = build_mdn(request, new_processed_disposition(), mic, signing_config)

        assert headers['Content-Type'].startswith('multipart/signed')

        # The sender verifies the MDN against its own keystore, which trusts the receiver's CA.
        info = parse_mdn(body, headers['Content-Type'], parties.sender)

        assert info.is_signed is True
        assert info.signer_certificate == parties.receiver.signing_certificate
        assert info.original_message_id == _message_id
        assert info.disposition == 'processed'
        assert info.mic_algorithm == 'sha-256'

    def test_signed_receipt_request_is_honored_even_when_processing_failed(self, parties):
        request = _make_request(
            requests_signed_mdn=True, signed_receipt_protocol='pkcs7-signature', mic_algorithms=['sha-256'])
        signing_config = _make_signing_config(parties)
        disposition = new_error_disposition(AS2Error.Integrity_Check_Failed)

        body, headers = build_mdn(request, disposition, signing_config=signing_config)

        assert headers['Content-Type'].startswith('multipart/signed')

        info = parse_mdn(body, headers['Content-Type'], parties.sender)

        assert info.disposition == 'processed'
        assert info.modifier_kind == 'error'
        assert info.modifier == 'integrity-check-failed'

    def test_signature_algorithm_honors_the_request(self, parties):
        request = _make_request(
            requests_signed_mdn=True, signed_receipt_protocol='pkcs7-signature', mic_algorithms=['sha384', 'sha-256'])
        signing_config = _make_signing_config(parties)

        _, headers = build_mdn(request, new_processed_disposition(), _sample_mic(), signing_config)

        # The first supported algorithm from the request carries the signature,
        # announced in the RFC 5751 spelling regardless of how it was requested.
        assert 'micalg=sha-384' in headers['Content-Type']

    def test_unsupported_mic_algorithms_still_get_a_signed_failure_mdn(self, parties):
        # Nothing on the request's list is supported, so the failure MDN reports it -
        # signed all the same, under our own default algorithm.
        request = _make_request(
            requests_signed_mdn=True, signed_receipt_protocol='pkcs7-signature', mic_algorithms=['md5', 'crc32'])
        signing_config = _make_signing_config(parties)
        disposition = new_failure_disposition(Failure.Unsupported_MIC_Algorithms)

        body, headers = build_mdn(request, disposition, signing_config=signing_config)

        assert headers['Content-Type'].startswith('multipart/signed')
        assert 'micalg=sha-256' in headers['Content-Type']

        info = parse_mdn(body, headers['Content-Type'], parties.sender)

        assert info.disposition == 'failed'
        assert info.modifier_kind == 'failure'
        assert info.modifier == 'unsupported MIC-algorithms'

# ################################################################################################################################
# ################################################################################################################################

class TestParseMDN:

    def test_unsigned_roundtrip(self):
        request = _make_request()
        mic = _sample_mic()

        body, headers = build_mdn(request, new_processed_disposition(), mic)

        info = parse_mdn(body, headers['Content-Type'])

        assert info.is_signed is False
        assert info.signer_certificate is None
        assert info.original_message_id == _message_id
        assert info.mode == 'automatic-action/MDN-sent-automatically'
        assert info.disposition == 'processed'
        assert info.modifier_kind == ''
        assert info.modifier == ''
        assert f'{info.mic}, {info.mic_algorithm}' == mic
        assert 'MDN for -' in info.text

    def test_async_mdn_payload_parses_the_same(self):
        # An asynchronous MDN is the same multipart/report, delivered by a separate POST
        # to the requested URL rather than in the HTTP response.
        request = _make_request(async_mdn_url='https://partnercorp.example.com/as2/mdn')
        mic = _sample_mic()

        body, headers = build_mdn(request, new_processed_disposition(), mic)

        assert request.async_mdn_url == 'https://partnercorp.example.com/as2/mdn'

        info = parse_mdn(body, headers['Content-Type'])

        assert info.original_message_id == _message_id
        assert info.disposition == 'processed'
        assert f'{info.mic}, {info.mic_algorithm}' == mic

    def test_micalg_spelling_variants_are_normalized(self):
        # A peer's MDN may spell the algorithm without the dash - the parsed name is normalized.
        body = _crlf_join([
            '--test-boundary',
            'Content-Type: text/plain',
            '',
            'The message was processed.',
            '--test-boundary',
            'Content-Type: message/disposition-notification',
            '',
            f'Original-Message-ID: {_message_id}',
            'Received-Content-MIC: q83vEjRWeJA=, sha256',
            'Disposition: automatic-action/MDN-sent-automatically; processed',
            '--test-boundary--',
            '',
        ])
        content_type = 'multipart/report; report-type=disposition-notification; boundary="test-boundary"'

        info = parse_mdn(body, content_type)

        assert info.mic == 'q83vEjRWeJA='
        assert info.mic_algorithm == 'sha-256'

    def test_error_and_failure_dispositions_parse(self):
        request = _make_request()

        for disposition, expected_type, expected_kind, expected_modifier in [
            (new_error_disposition(AS2Error.Authentication_Failed), 'processed', 'error', 'authentication-failed'),
            (new_warning_disposition('duplicate-document'), 'processed', 'warning', 'duplicate-document'),
            (new_failure_disposition(Failure.Unsupported_Format), 'failed', 'failure', 'unsupported format'),
        ]:
            body, headers = build_mdn(request, disposition)

            info = parse_mdn(body, headers['Content-Type'])

            assert info.disposition == expected_type
            assert info.modifier_kind == expected_kind
            assert info.modifier == expected_modifier

    def test_tampered_signed_mdn_is_rejected(self, parties):
        request = _make_request(
            requests_signed_mdn=True, signed_receipt_protocol='pkcs7-signature', mic_algorithms=['sha-256'])
        signing_config = _make_signing_config(parties)

        body, headers = build_mdn(request, new_processed_disposition(), _sample_mic(), signing_config)

        tampered = body.replace(b'processed', b'PROCESSED', 1)

        with pytest.raises(AS2SecurityException) as exception_info:
            _ = parse_mdn(tampered, headers['Content-Type'], parties.sender)

        assert exception_info.value.modifier == AS2Error.Integrity_Check_Failed

    def test_signed_mdn_without_a_keystore_is_rejected(self, parties):
        request = _make_request(
            requests_signed_mdn=True, signed_receipt_protocol='pkcs7-signature', mic_algorithms=['sha-256'])
        signing_config = _make_signing_config(parties)

        body, headers = build_mdn(request, new_processed_disposition(), _sample_mic(), signing_config)

        with pytest.raises(AS2Exception):
            _ = parse_mdn(body, headers['Content-Type'])

    def test_non_mdn_content_type_is_rejected(self):
        with pytest.raises(AS2ProtocolException) as exception_info:
            _ = parse_mdn(b'Not an MDN at all', 'text/plain')

        assert exception_info.value.modifier == AS2Error.Unexpected_Processing_Error

    def test_report_without_a_boundary_is_rejected(self):
        with pytest.raises(AS2ProtocolException) as exception_info:
            _ = parse_mdn(b'Not a valid report body', 'multipart/report; report-type=disposition-notification')

        assert exception_info.value.modifier == AS2Error.Unexpected_Processing_Error

# ################################################################################################################################
# ################################################################################################################################

class TestMessageID:

    def test_message_ids_are_unique_and_bracketed(self):
        first = new_message_id()
        second = new_message_id()

        assert first != second
        assert first.startswith('<')
        assert first.endswith('@zato>')

# ################################################################################################################################
# ################################################################################################################################
