# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone
from subprocess import run as subprocess_run

# cryptography
from cryptography.hazmat.primitives.serialization import Encoding

# pytest
import pytest

# Zato
from zato.common.as2.common import AS2Error, AS2ProtocolException, AS2SecurityException, EncryptionAlgorithm
from zato.common.as2.smime import compress, decompress, decrypt, encrypt, new_part, serialize_part, sign, verify
from zato.common.util.xml_.keystore import DecryptionEntry, new_keystore

# ################################################################################################################################
# ################################################################################################################################

# A small X12 purchase order interchange used as the payload throughout.
_edi_payload = b'ISA*00*          *00*          *ZZ*SENDERID       *ZZ*RECEIVERID     ' + \
    b'*260709*1200*U*00401*000000001*0*P*>~GS*PO*SENDERID*RECEIVERID*20260709*1200*1*X*004010~' + \
    b'ST*850*0001~BEG*00*SA*PO-2026-001**20260709~SE*3*0001~GE*1*1~IEA*1*000000001~'

_edi_content_type = 'application/edi-x12'

# ################################################################################################################################
# ################################################################################################################################

def _edi_part():
    out = new_part(_edi_payload, _edi_content_type)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSignVerify:

    def test_sign_verify_roundtrip(self, parties):
        part = _edi_part()

        signed = sign(part, parties.sender)
        result = verify(signed, parties.receiver)

        assert result.part.data == _edi_payload
        assert result.part.content_type == _edi_content_type
        assert result.signer_certificate == parties.sender.signing_certificate
        assert result.digest_algorithm == 'sha-256'

    def test_signed_content_type_declares_the_protocol_and_micalg(self, parties):
        part = _edi_part()

        # The input spelling has no dash - the output must use the RFC 5751 one regardless.
        signed = sign(part, parties.sender, digest_algorithm='sha256')

        assert signed.content_type.startswith('multipart/signed')
        assert 'protocol="application/pkcs7-signature"' in signed.content_type
        assert 'micalg=sha-256' in signed.content_type

    @pytest.mark.parametrize('algorithm', ['sha-1', 'sha-256', 'sha-384', 'sha-512'])
    def test_sign_verify_all_digest_algorithms(self, parties, algorithm):
        part = _edi_part()

        signed = sign(part, parties.sender, digest_algorithm=algorithm)
        result = verify(signed, parties.receiver)

        assert result.digest_algorithm == algorithm
        assert result.part.data == _edi_payload

    @pytest.mark.parametrize('algorithm', ['sha-1', 'sha-256'])
    def test_signing_time_is_extracted(self, parties, algorithm):
        part = _edi_part()

        before = datetime.now(timezone.utc) - timedelta(minutes=1)
        after = datetime.now(timezone.utc) + timedelta(minutes=1)

        signed = sign(part, parties.sender, digest_algorithm=algorithm)
        result = verify(signed, parties.receiver)

        assert result.signing_time is not None
        assert before <= result.signing_time <= after

    def test_tampered_content_is_detected(self, parties):
        part = _edi_part()
        signed = sign(part, parties.sender)

        signed.data = signed.data.replace(b'PO-2026-001', b'PO-2026-999')

        with pytest.raises(AS2SecurityException) as exception_info:
            _ = verify(signed, parties.receiver)

        assert exception_info.value.modifier == AS2Error.Integrity_Check_Failed

    def test_garbage_signature_is_detected(self, parties):
        part = _edi_part()
        signed = sign(part, parties.sender)

        # The base64 of a DER ContentInfo always starts with MII - corrupting it
        # makes the signature part unparseable.
        signed.data = signed.data.replace(b'MII', b'NII', 1)

        with pytest.raises(AS2SecurityException) as exception_info:
            _ = verify(signed, parties.receiver)

        assert exception_info.value.modifier == AS2Error.Integrity_Check_Failed

    def test_trust_anchor_mode_accepts_a_chain_to_the_anchor(self, parties):
        part = _edi_part()
        signed = sign(part, parties.sender)

        # No pinned certificate - trust flows from the CA anchor alone.
        keystore = new_keystore()
        keystore.trust_anchors = [parties.ca_certificate]

        result = verify(signed, keystore)

        assert result.signer_certificate == parties.sender.signing_certificate

    def test_untrusted_ca_is_rejected(self, parties, unrelated_ca_certificate):
        part = _edi_part()
        signed = sign(part, parties.sender)

        keystore = new_keystore()
        keystore.trust_anchors = [unrelated_ca_certificate]

        with pytest.raises(AS2SecurityException) as exception_info:
            _ = verify(signed, keystore)

        assert exception_info.value.modifier == AS2Error.Authentication_Failed

    def test_wrong_pinned_certificate_is_rejected(self, parties):
        part = _edi_part()
        signed = sign(part, parties.sender)

        # Pin the receiver's own certificate instead of the sender's.
        keystore = new_keystore()
        keystore.peer_signing_certificate = parties.receiver.signing_certificate

        with pytest.raises(AS2SecurityException) as exception_info:
            _ = verify(signed, keystore)

        assert exception_info.value.modifier == AS2Error.Authentication_Failed

    def test_unsigned_entity_is_rejected(self, parties):
        part = _edi_part()

        with pytest.raises(AS2ProtocolException) as exception_info:
            _ = verify(part, parties.receiver)

        assert exception_info.value.modifier == AS2Error.Insufficient_Message_Security

    def test_accepted_certificates_admit_a_listed_signer(self, parties, make_rotated_pair):
        part = _edi_part()
        signed = sign(part, parties.sender)

        # An empty keystore would reject the signer - the rotation list alone admits it.
        keystore = new_keystore()
        rotated = make_rotated_pair('as2-sender-rotated')

        accepted = [rotated.certificate, parties.sender.signing_certificate]
        result = verify(signed, keystore, accepted)

        assert result.signer_certificate == parties.sender.signing_certificate

    def test_accepted_certificates_reject_an_unlisted_signer(self, parties, make_rotated_pair):
        part = _edi_part()
        signed = sign(part, parties.sender)

        # The rotation list holds another certificate, so even the pinned keystore
        # entry does not help - the list is the trust decision.
        rotated = make_rotated_pair('as2-sender-rotated')
        accepted = [rotated.certificate]

        with pytest.raises(AS2SecurityException) as exception_info:
            _ = verify(signed, parties.receiver, accepted)

        assert exception_info.value.modifier == AS2Error.Authentication_Failed

# ################################################################################################################################
# ################################################################################################################################

class TestEncryptDecrypt:

    @pytest.mark.parametrize('algorithm', [EncryptionAlgorithm.AES_128_CBC, EncryptionAlgorithm.AES_256_CBC])
    def test_encrypt_decrypt_cbc(self, parties, algorithm):
        part = _edi_part()

        encrypted = encrypt(part, parties.sender.peer_encryption_certificate, algorithm)
        decrypted = decrypt(encrypted, parties.receiver)

        assert 'smime-type=enveloped-data' in encrypted.content_type
        assert _edi_payload not in encrypted.data
        assert decrypted.data == _edi_payload
        assert decrypted.content_type == _edi_content_type

    @pytest.mark.parametrize('algorithm', [EncryptionAlgorithm.AES_128_GCM, EncryptionAlgorithm.AES_256_GCM])
    def test_encrypt_decrypt_gcm(self, parties, algorithm):
        part = _edi_part()

        encrypted = encrypt(part, parties.sender.peer_encryption_certificate, algorithm)
        decrypted = decrypt(encrypted, parties.receiver)

        assert 'smime-type=enveloped-data' in encrypted.content_type
        assert _edi_payload not in encrypted.data
        assert decrypted.data == _edi_payload
        assert decrypted.content_type == _edi_content_type

    def test_force_base64_roundtrip(self, parties):
        part = _edi_part()

        encrypted = encrypt(part, parties.sender.peer_encryption_certificate, force_base64=True)

        assert encrypted.content_transfer_encoding == 'base64'

        decrypted = decrypt(encrypted, parties.receiver)

        assert decrypted.data == _edi_payload

    def test_wrong_key_is_rejected(self, parties):
        part = _edi_part()

        encrypted = encrypt(part, parties.sender.peer_encryption_certificate)

        # The sender's own keystore has no key for a message encrypted to the receiver.
        with pytest.raises(AS2SecurityException) as exception_info:
            _ = decrypt(encrypted, parties.sender)

        assert exception_info.value.modifier == AS2Error.Decryption_Failed

    def test_wrong_key_is_rejected_for_gcm(self, parties):
        part = _edi_part()

        encrypted = encrypt(part, parties.sender.peer_encryption_certificate, EncryptionAlgorithm.AES_256_GCM)

        with pytest.raises(AS2SecurityException) as exception_info:
            _ = decrypt(encrypted, parties.sender)

        assert exception_info.value.modifier == AS2Error.Decryption_Failed

    def test_garbage_input_is_rejected(self, parties):
        garbage = new_part(b'This is not a CMS structure at all', 'application/pkcs7-mime; smime-type=enveloped-data')

        with pytest.raises(AS2SecurityException) as exception_info:
            _ = decrypt(garbage, parties.receiver)

        assert exception_info.value.modifier == AS2Error.Decryption_Failed

    def test_rotation_entry_key_decrypts_a_message_encrypted_to_its_certificate(self, parties, make_rotated_pair):
        part = _edi_part()
        rotated = make_rotated_pair('as2-receiver-rotated')

        # The message is encrypted to the receiver's new certificate ..
        encrypted = encrypt(part, rotated.certificate)

        # .. whose key lives on the rotation entries, next to the primary pair.
        keystore = new_keystore()
        keystore.signing_key = parties.receiver.signing_key
        keystore.signing_certificate_chain = parties.receiver.signing_certificate_chain
        keystore.decryption_key = parties.receiver.decryption_key

        entry = DecryptionEntry()
        entry.key = rotated.key
        entry.certificate = rotated.certificate
        keystore.decryption_entries.append(entry)

        decrypted = decrypt(encrypted, keystore)

        assert decrypted.data == _edi_payload
        assert decrypted.content_type == _edi_content_type

    def test_primary_pair_still_decrypts_with_rotation_entries_present(self, parties, make_rotated_pair):
        part = _edi_part()
        rotated = make_rotated_pair('as2-receiver-rotated')

        # The message is encrypted to the receiver's current certificate ..
        encrypted = encrypt(part, parties.sender.peer_encryption_certificate)

        # .. and the presence of a rotation entry does not get in the primary pair's way.
        keystore = new_keystore()
        keystore.signing_key = parties.receiver.signing_key
        keystore.signing_certificate_chain = parties.receiver.signing_certificate_chain
        keystore.decryption_key = parties.receiver.decryption_key

        entry = DecryptionEntry()
        entry.key = rotated.key
        entry.certificate = rotated.certificate
        keystore.decryption_entries.append(entry)

        decrypted = decrypt(encrypted, keystore)

        assert decrypted.data == _edi_payload

    def test_an_expired_rotation_entry_does_not_decrypt(self, parties, make_rotated_pair):
        part = _edi_part()
        rotated = make_rotated_pair('as2-receiver-rotated')

        encrypted = encrypt(part, rotated.certificate)

        # The entry's validity window closed a day ago, so its key is not a candidate anymore.
        keystore = new_keystore()
        keystore.signing_key = parties.receiver.signing_key
        keystore.signing_certificate_chain = parties.receiver.signing_certificate_chain
        keystore.decryption_key = parties.receiver.decryption_key

        entry = DecryptionEntry()
        entry.key = rotated.key
        entry.certificate = rotated.certificate
        entry.valid_until = datetime.now(timezone.utc) - timedelta(days=1)
        keystore.decryption_entries.append(entry)

        with pytest.raises(AS2SecurityException) as exception_info:
            _ = decrypt(encrypted, keystore)

        assert exception_info.value.modifier == AS2Error.Decryption_Failed

    def test_3des_is_accepted_inbound(self, parties, tmp_path):
        part = _edi_part()

        # Encrypt to the receiver with an implementation we did not write, using 3DES
        # which is only ever accepted on the way in.
        payload_path = tmp_path / 'payload.bin'
        certificate_path = tmp_path / 'recipient.pem'
        envelope_path = tmp_path / 'envelope.der'

        certificate_pem = parties.sender.peer_encryption_certificate.public_bytes(Encoding.PEM)

        _ = payload_path.write_bytes(serialize_part(part))
        _ = certificate_path.write_bytes(certificate_pem)

        command = [
            'openssl', 'smime', '-encrypt', '-des3', '-binary',
            '-outform', 'DER',
            '-in', str(payload_path),
            '-out', str(envelope_path),
            str(certificate_path),
        ]
        _ = subprocess_run(command, check=True)

        encrypted = new_part(envelope_path.read_bytes(), 'application/pkcs7-mime; smime-type=enveloped-data')
        decrypted = decrypt(encrypted, parties.receiver)

        assert decrypted.data == _edi_payload
        assert decrypted.content_type == _edi_content_type

# ################################################################################################################################
# ################################################################################################################################

class TestCompression:

    def test_compress_decompress_roundtrip(self):
        part = _edi_part()

        compressed = compress(part)

        assert 'smime-type=compressed-data' in compressed.content_type
        assert _edi_payload not in compressed.data

        decompressed = decompress(compressed)

        assert decompressed.data == _edi_payload
        assert decompressed.content_type == _edi_content_type

    def test_compress_then_sign(self, parties):
        part = _edi_part()

        compressed = compress(part)
        signed = sign(compressed, parties.sender)

        result = verify(signed, parties.receiver)

        assert 'smime-type=compressed-data' in result.part.content_type

        decompressed = decompress(result.part)

        assert decompressed.data == _edi_payload

    def test_sign_then_compress(self, parties):
        part = _edi_part()

        signed = sign(part, parties.sender)
        compressed = compress(signed)

        decompressed = decompress(compressed)

        assert decompressed.content_type.startswith('multipart/signed')

        result = verify(decompressed, parties.receiver)

        assert result.part.data == _edi_payload

    def test_garbage_input_is_rejected(self):
        garbage = new_part(b'This is not a CMS structure at all', 'application/pkcs7-mime; smime-type=compressed-data')

        with pytest.raises(AS2ProtocolException) as exception_info:
            _ = decompress(garbage)

        assert exception_info.value.modifier == AS2Error.Decompression_Failed

    def test_enveloped_input_is_rejected(self, parties):
        part = _edi_part()

        encrypted = encrypt(part, parties.sender.peer_encryption_certificate)

        with pytest.raises(AS2ProtocolException) as exception_info:
            _ = decompress(encrypted)

        assert exception_info.value.modifier == AS2Error.Decompression_Failed

# ################################################################################################################################
# ################################################################################################################################
