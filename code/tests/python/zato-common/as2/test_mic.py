# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64encode
from hashlib import sha1, sha256, sha384, sha512

# pytest
import pytest

# Zato
from zato.common.as2.common import AS2ProtocolException, Failure
from zato.common.as2.smime import compute_mic, new_part, normalize_micalg, select_mic_algorithm, sign, verify

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

_text_payload = b'Purchase order confirmation for PO-2026-001\r\nAll thirty units will ship on Friday.\r\n'
_binary_payload = b'\x00\x01\x02\n\x03\r\x04\r\n\x05'

# ################################################################################################################################
# ################################################################################################################################

def _expected_mic(covered:'any_', digest_function:'any_', algorithm:'any_') -> 'any_':
    """ Recomputes a MIC independently of the code under test.
    """
    digest = digest_function(covered).digest()
    encoded_bytes = b64encode(digest)
    encoded = encoded_bytes.decode('ascii')

    out = f'{encoded}, {algorithm}'
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestReceivedContentMIC:
    """ The three coverage cases of RFC 4130 section 7.3.1.
    """

    def test_signed_message_covers_headers_and_content(self) -> 'None':
        part = new_part(_text_payload, 'text/plain', '7bit')

        # For a signed message the MIC covers the complete MIME entity - typed out here byte by byte.
        covered = b'Content-Type: text/plain\r\nContent-Transfer-Encoding: 7bit\r\n\r\n' + _text_payload
        expected = _expected_mic(covered, sha256, 'sha-256')

        mic = compute_mic(part, is_signed=True, is_encrypted=False)

        assert mic == expected

# ################################################################################################################################

    def test_encrypted_unsigned_message_covers_headers_and_content(self) -> 'None':
        part = new_part(_text_payload, 'text/plain', '7bit')

        # For an encrypted unsigned message the MIC covers the decrypted MIME entity, headers included.
        covered = b'Content-Type: text/plain\r\nContent-Transfer-Encoding: 7bit\r\n\r\n' + _text_payload
        expected = _expected_mic(covered, sha256, 'sha-256')

        mic = compute_mic(part, is_signed=False, is_encrypted=True)

        assert mic == expected

# ################################################################################################################################

    def test_plain_message_covers_content_alone(self) -> 'None':
        part = new_part(_text_payload, 'text/plain', '7bit')

        # For an unsigned unencrypted message the MIC covers the content alone, without any headers.
        expected = _expected_mic(_text_payload, sha256, 'sha-256')

        mic = compute_mic(part, is_signed=False, is_encrypted=False)

        assert mic == expected

# ################################################################################################################################

    def test_plain_and_signed_coverage_differ(self) -> 'None':
        part = new_part(_text_payload, 'text/plain', '7bit')

        signed_mic = compute_mic(part, is_signed=True, is_encrypted=False)
        plain_mic = compute_mic(part, is_signed=False, is_encrypted=False)

        assert signed_mic != plain_mic

# ################################################################################################################################
# ################################################################################################################################

class TestCanonicalization:
    """ CRLF canonicalization applies to text/* content only and never to binary or base64 content.
    """

    def test_text_content_is_crlf_canonicalized(self) -> 'None':
        part = new_part(b'First line\nSecond line\rThird line\r\nLast line', 'text/plain', '7bit')

        canonical = b'First line\r\nSecond line\r\nThird line\r\nLast line'
        expected = _expected_mic(canonical, sha256, 'sha-256')

        mic = compute_mic(part, is_signed=False, is_encrypted=False)

        assert mic == expected

# ################################################################################################################################

    def test_binary_encoding_is_never_canonicalized(self) -> 'None':
        part = new_part(_binary_payload, 'text/plain', 'binary')

        expected = _expected_mic(_binary_payload, sha256, 'sha-256')

        mic = compute_mic(part, is_signed=False, is_encrypted=False)

        assert mic == expected

# ################################################################################################################################

    def test_base64_encoding_is_never_canonicalized(self) -> 'None':
        # base64 content with a bare LF between its lines must be digested exactly as it is.
        payload = b'UHVyY2hhc2Ugb3JkZXIgY29uZmlybWF0aW9u\nZm9yIFBPLTIwMjYtMDAx'
        part = new_part(payload, 'text/plain', 'base64')

        expected = _expected_mic(payload, sha256, 'sha-256')

        mic = compute_mic(part, is_signed=False, is_encrypted=False)

        assert mic == expected

# ################################################################################################################################

    def test_non_text_content_is_never_canonicalized(self) -> 'None':
        part = new_part(_binary_payload, 'application/octet-stream', '7bit')

        expected = _expected_mic(_binary_payload, sha256, 'sha-256')

        mic = compute_mic(part, is_signed=False, is_encrypted=False)

        assert mic == expected

# ################################################################################################################################

    def test_prevent_canonicalization_escape_hatch(self) -> 'None':
        payload = b'First line\nSecond line'
        part = new_part(payload, 'text/plain', '7bit')

        expected = _expected_mic(payload, sha256, 'sha-256')

        mic = compute_mic(part, is_signed=False, is_encrypted=False, prevent_canonicalization=True)

        assert mic == expected

# ################################################################################################################################
# ################################################################################################################################

class TestMICAlgorithmNames:

    @pytest.mark.parametrize('value,expected', [
        ('sha1', 'sha-1'),
        ('sha-1', 'sha-1'),
        ('SHA1', 'sha-1'),
        ('sha256', 'sha-256'),
        ('sha-256', 'sha-256'),
        ('SHA-256', 'sha-256'),
        ('Sha384', 'sha-384'),
        ('SHA512', 'sha-512'),
        (' sha-512 ', 'sha-512'),
    ])
    def test_input_spellings_are_accepted(self, value:'any_', expected:'any_') -> 'None':
        assert normalize_micalg(value) == expected

# ################################################################################################################################

    def test_unknown_spelling_is_rejected(self) -> 'None':
        with pytest.raises(AS2ProtocolException) as exception_info:
            _ = normalize_micalg('md5')

        assert exception_info.value.modifier == Failure.Unsupported_MIC_Algorithms

    @pytest.mark.parametrize('algorithm,digest_function,expected_name', [
        ('sha1', sha1, 'sha-1'),
        ('sha256', sha256, 'sha-256'),
        ('sha384', sha384, 'sha-384'),
        ('sha512', sha512, 'sha-512'),
    ])

# ################################################################################################################################

    def test_output_always_uses_the_rfc_5751_spelling(self, algorithm:'any_', digest_function:'any_', expected_name:'any_') -> 'None':
        part = new_part(_text_payload, 'text/plain', '7bit')

        expected = _expected_mic(_text_payload, digest_function, expected_name)

        mic = compute_mic(part, algorithm, is_signed=False, is_encrypted=False)

        assert mic == expected
        assert mic.endswith(f', {expected_name}')

# ################################################################################################################################
# ################################################################################################################################

class TestMICAlgorithmSelection:

    def test_selection_honors_the_request_order(self) -> 'None':
        assert select_mic_algorithm(['sha384', 'sha-256']) == 'sha-384'
        assert select_mic_algorithm(['sha-256', 'sha384']) == 'sha-256'

# ################################################################################################################################

    def test_selection_skips_unsupported_entries(self) -> 'None':
        assert select_mic_algorithm(['md5', 'sha-256']) == 'sha-256'

# ################################################################################################################################

    def test_nothing_supported_is_the_failure_path(self) -> 'None':
        with pytest.raises(AS2ProtocolException) as exception_info:
            _ = select_mic_algorithm(['md5', 'crc32'])

        assert exception_info.value.modifier == Failure.Unsupported_MIC_Algorithms

# ################################################################################################################################
# ################################################################################################################################

class TestMICReconciliation:

    def test_verified_content_yields_the_senders_mic(self, parties:'TestParties') -> 'None':
        """ The MIC the sender stores at send time must equal a digest over the exact bytes
        the receiver's signature verification reports as covered.
        """
        part = new_part(_text_payload, 'text/plain', '7bit')

        sender_mic = compute_mic(part, is_signed=True, is_encrypted=False)

        signed = sign(part, parties.sender)
        result = verify(signed, parties.receiver)

        receiver_mic = _expected_mic(result.content, sha256, 'sha-256')

        assert receiver_mic == sender_mic

# ################################################################################################################################
# ################################################################################################################################
