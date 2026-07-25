# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone
from subprocess import run as subprocess_run

# cryptography
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

# pytest
import pytest

# Zato
from .smime_helpers import EDI_Content_Type as _edi_content_type, EDI_Payload as _edi_payload, new_edi_part
from zato.common.as2.common import AS2Error, AS2SecurityException, EncryptionAlgorithm
from zato.common.as2.smime import decrypt, encrypt, new_part, serialize_part
from zato.common.util.xml_.keystore import DecryptionEntry, new_keystore

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import any_
    Path = Path
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

def _receiver_keystore(parties:'TestParties') -> 'any_':
    """ The receiving side's primary pair on its own, which the rotation entries then join.
    """
    out = new_keystore()

    out.signing_key = parties.receiver.signing_key
    out.signing_certificate_chain = parties.receiver.signing_certificate_chain
    out.decryption_key = parties.receiver.decryption_key

    return out

# ################################################################################################################################

def _decryption_entry(key:'any_', certificate:'any_', valid_until:'any_' = None) -> 'any_':
    """ One entry of the receiving side's decryption rotation list.
    """
    out = DecryptionEntry()

    out.key = key
    out.certificate = certificate
    out.valid_until = valid_until

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestEncryptDecrypt:
    """ Enveloping an entity for the partner and opening it again, across every algorithm
    we emit and every state a decryption key can be in.
    """

    @pytest.mark.parametrize('algorithm', [EncryptionAlgorithm.AES_128_CBC, EncryptionAlgorithm.AES_256_CBC])
    def test_encrypt_decrypt_cbc(self, parties:'TestParties', algorithm:'any_') -> 'None':
        part = new_edi_part()

        encrypted = encrypt(part, parties.sender.peer_encryption_certificate, algorithm)
        decrypted = decrypt(encrypted, parties.receiver)

        assert 'smime-type=enveloped-data' in encrypted.content_type
        assert _edi_payload not in encrypted.data
        assert decrypted.data == _edi_payload
        assert decrypted.content_type == _edi_content_type

# ################################################################################################################################

    @pytest.mark.parametrize('algorithm', [EncryptionAlgorithm.AES_128_GCM, EncryptionAlgorithm.AES_256_GCM])
    def test_encrypt_decrypt_gcm(self, parties:'TestParties', algorithm:'any_') -> 'None':
        part = new_edi_part()

        encrypted = encrypt(part, parties.sender.peer_encryption_certificate, algorithm)
        decrypted = decrypt(encrypted, parties.receiver)

        assert 'smime-type=enveloped-data' in encrypted.content_type
        assert _edi_payload not in encrypted.data
        assert decrypted.data == _edi_payload
        assert decrypted.content_type == _edi_content_type

# ################################################################################################################################

    def test_force_base64_roundtrip(self, parties:'TestParties') -> 'None':
        part = new_edi_part()

        encrypted = encrypt(part, parties.sender.peer_encryption_certificate, force_base64=True)

        assert encrypted.content_transfer_encoding == 'base64'

        decrypted = decrypt(encrypted, parties.receiver)

        assert decrypted.data == _edi_payload

# ################################################################################################################################

    def test_wrong_key_is_rejected(self, parties:'TestParties') -> 'None':
        part = new_edi_part()

        encrypted = encrypt(part, parties.sender.peer_encryption_certificate)

        # The sender's own keystore has no key for a message encrypted to the receiver.
        with pytest.raises(AS2SecurityException) as exception_information:
            _ = decrypt(encrypted, parties.sender)

        assert exception_information.value.modifier == AS2Error.Decryption_Failed

# ################################################################################################################################

    def test_wrong_key_is_rejected_for_gcm(self, parties:'TestParties') -> 'None':
        part = new_edi_part()

        encrypted = encrypt(part, parties.sender.peer_encryption_certificate, EncryptionAlgorithm.AES_256_GCM)

        with pytest.raises(AS2SecurityException) as exception_information:
            _ = decrypt(encrypted, parties.sender)

        assert exception_information.value.modifier == AS2Error.Decryption_Failed

# ################################################################################################################################

    def test_garbage_input_is_rejected(self, parties:'TestParties') -> 'None':
        garbage = new_part(b'This is not a CMS structure at all', 'application/pkcs7-mime; smime-type=enveloped-data')

        with pytest.raises(AS2SecurityException) as exception_information:
            _ = decrypt(garbage, parties.receiver)

        assert exception_information.value.modifier == AS2Error.Decryption_Failed

# ################################################################################################################################

    def test_rotation_entry_key_decrypts_a_message_encrypted_to_its_certificate(
        self, parties:'TestParties', make_rotated_pair:'any_') -> 'None':
        part = new_edi_part()
        rotated = make_rotated_pair('as2-receiver-rotated')

        # The message is encrypted to the receiver's new certificate ..
        encrypted = encrypt(part, rotated.certificate)

        # .. whose key lives on the rotation entries, next to the primary pair.
        keystore = _receiver_keystore(parties)
        entry = _decryption_entry(rotated.key, rotated.certificate)
        keystore.decryption_entries.append(entry)

        decrypted = decrypt(encrypted, keystore)

        assert decrypted.data == _edi_payload
        assert decrypted.content_type == _edi_content_type

# ################################################################################################################################

    def test_primary_pair_still_decrypts_with_rotation_entries_present(
        self, parties:'TestParties', make_rotated_pair:'any_') -> 'None':
        part = new_edi_part()
        rotated = make_rotated_pair('as2-receiver-rotated')

        # The message is encrypted to the receiver's current certificate ..
        encrypted = encrypt(part, parties.sender.peer_encryption_certificate)

        # .. and the presence of a rotation entry does not get in the primary pair's way.
        keystore = _receiver_keystore(parties)
        entry = _decryption_entry(rotated.key, rotated.certificate)
        keystore.decryption_entries.append(entry)

        decrypted = decrypt(encrypted, keystore)

        assert decrypted.data == _edi_payload

# ################################################################################################################################

    def test_an_expired_rotation_entry_does_not_decrypt(
        self, parties:'TestParties', make_rotated_pair:'any_') -> 'None':
        part = new_edi_part()
        rotated = make_rotated_pair('as2-receiver-rotated')

        encrypted = encrypt(part, rotated.certificate)

        # The entry's validity window closed a day ago, so its key is not a candidate anymore.
        closed_yesterday = datetime.now(timezone.utc) - timedelta(days=1)

        keystore = _receiver_keystore(parties)
        entry = _decryption_entry(rotated.key, rotated.certificate, closed_yesterday)
        keystore.decryption_entries.append(entry)

        with pytest.raises(AS2SecurityException) as exception_information:
            _ = decrypt(encrypted, keystore)

        assert exception_information.value.modifier == AS2Error.Decryption_Failed

# ################################################################################################################################

    def test_a_rotation_entry_with_an_expired_certificate_does_not_decrypt(
        self, parties:'TestParties', make_dated_pair:'any_') -> 'None':
        part = new_edi_part()

        now = datetime.now(timezone.utc)
        expired = make_dated_pair('as2-receiver-expired', now - timedelta(days=10), now - timedelta(days=1))

        encrypted = encrypt(part, expired.certificate)

        # The configured window is wide open, so the certificate's own expiry is what
        # takes the entry out of service.
        keystore = _receiver_keystore(parties)
        entry = _decryption_entry(expired.key, expired.certificate)
        keystore.decryption_entries.append(entry)

        with pytest.raises(AS2SecurityException) as exception_information:
            _ = decrypt(encrypted, keystore)

        assert exception_information.value.modifier == AS2Error.Decryption_Failed

# ################################################################################################################################

    def test_3des_roundtrip(self, parties:'TestParties') -> 'None':
        part = new_edi_part()

        encrypted = encrypt(part, parties.sender.peer_encryption_certificate, EncryptionAlgorithm.DES_EDE3_CBC)
        decrypted = decrypt(encrypted, parties.receiver)

        assert 'smime-type=enveloped-data' in encrypted.content_type
        assert _edi_payload not in encrypted.data
        assert decrypted.data == _edi_payload
        assert decrypted.content_type == _edi_content_type

# ################################################################################################################################

    def test_3des_is_accepted_inbound(self, parties:'TestParties', tmp_path:'Path') -> 'None':
        part = new_edi_part()

        # Encrypt to the receiver using 3DES with an implementation we did not write.
        payload_path = tmp_path / 'payload.bin'
        certificate_path = tmp_path / 'recipient.pem'
        envelope_path = tmp_path / 'envelope.der'

        serialized = serialize_part(part)
        certificate_pem = parties.sender.peer_encryption_certificate.public_bytes(Encoding.PEM)

        _ = payload_path.write_bytes(serialized)
        _ = certificate_path.write_bytes(certificate_pem)

        command = [
            'openssl', 'smime', '-encrypt', '-des3', '-binary',
            '-outform', 'DER',
            '-in', str(payload_path),
            '-out', str(envelope_path),
            str(certificate_path),
        ]
        _ = subprocess_run(command, check=True)

        envelope = envelope_path.read_bytes()

        encrypted = new_part(envelope, 'application/pkcs7-mime; smime-type=enveloped-data')
        decrypted = decrypt(encrypted, parties.receiver)

        assert decrypted.data == _edi_payload
        assert decrypted.content_type == _edi_content_type

# ################################################################################################################################

    def test_3des_is_readable_by_openssl(self, parties:'TestParties', tmp_path:'Path') -> 'None':
        part = new_edi_part()

        # Encrypt with our own implementation, using 3DES ..
        encrypted = encrypt(part, parties.sender.peer_encryption_certificate, EncryptionAlgorithm.DES_EDE3_CBC)

        # .. and decrypt with an implementation we did not write, proving that partners
        # whose stacks require 3DES can read what we emit.
        envelope_path = tmp_path / 'envelope.der'
        key_path = tmp_path / 'receiver-key.pem'
        certificate_path = tmp_path / 'receiver-cert.pem'
        plaintext_path = tmp_path / 'plaintext.bin'

        no_encryption = NoEncryption()

        key_pem = parties.receiver.decryption_key.private_bytes(
            Encoding.PEM, PrivateFormat.PKCS8, no_encryption)
        certificate_pem = parties.sender.peer_encryption_certificate.public_bytes(Encoding.PEM)

        _ = envelope_path.write_bytes(encrypted.data)
        _ = key_path.write_bytes(key_pem)
        _ = certificate_path.write_bytes(certificate_pem)

        command = [
            'openssl', 'smime', '-decrypt', '-binary',
            '-inform', 'DER',
            '-in', str(envelope_path),
            '-inkey', str(key_path),
            '-recip', str(certificate_path),
            '-out', str(plaintext_path),
        ]
        _ = subprocess_run(command, check=True)

        # What openssl recovered is the complete serialized MIME entity that was encrypted.
        recovered = plaintext_path.read_bytes()
        serialized = serialize_part(part)

        assert recovered == serialized

# ################################################################################################################################
# ################################################################################################################################
