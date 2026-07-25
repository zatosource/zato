# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The openssl CLI as the third-party oracle of the conformance suite - what we produce
# it consumes and what it produces we consume, in both the signing and the encryption
# direction, with no shared code between the two sides.

# stdlib
from base64 import b64encode
from subprocess import run as subprocess_run

# cryptography
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

# Zato
from zato.common.as2.common import EncryptionAlgorithm
from zato.common.as2.smime import decrypt, encrypt, new_part, sign, verify

# Zato
from .conformance_helpers import EDI_Content_Type, EDI_Entity, edi_part, EDI_Payload

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import any_
    Path = Path

# ################################################################################################################################
# ################################################################################################################################

# RFC 8551 - the media type an enveloped-data body travels under.
_enveloped_content_type = 'application/pkcs7-mime; smime-type=enveloped-data'

# The boundary the detached signature of the oracle is framed with.
_oracle_boundary = b'openssl-oracle-boundary'

# ################################################################################################################################
# ################################################################################################################################

class TestOpenSSLOracle:
    """ The openssl CLI as the third-party oracle - what we sign and encrypt,
    openssl verifies and decrypts, and what openssl signs and encrypts,
    we verify and decrypt.
    """

    def test_our_signature_verifies_with_openssl(self, parties:'any_', tmp_path:'Path') -> 'None':
        part = edi_part()
        signed = sign(part, parties.sender)

        # Wrap the multipart in a full S/MIME entity for the CLI ..
        message_path = tmp_path / 'message.smime'
        ca_path = tmp_path / 'ca.pem'
        content_path = tmp_path / 'content.bin'

        content_type_bytes = signed.content_type.encode('ascii')
        entity = b'MIME-Version: 1.0\r\nContent-Type: ' + content_type_bytes + b'\r\n\r\n' + signed.data

        ca_pem = parties.ca_certificate.public_bytes(Encoding.PEM)

        _ = message_path.write_bytes(entity)
        _ = ca_path.write_bytes(ca_pem)

        # .. and have an implementation we did not write verify the signature.
        command = [
            'openssl', 'cms', '-verify',
            '-in', str(message_path),
            '-inform', 'SMIME',
            '-CAfile', str(ca_path),
            '-out', str(content_path),
        ]
        _ = subprocess_run(command, check=True, capture_output=True)

        # What openssl recovered is the covered entity, byte for byte.
        recovered = content_path.read_bytes()
        assert recovered == EDI_Entity

# ################################################################################################################################

    def test_openssl_signature_verifies_with_ours(self, parties:'any_', tmp_path:'Path') -> 'None':

        # Sign with an implementation we did not write ..
        payload_path = tmp_path / 'payload.bin'
        key_path = tmp_path / 'sender-key.pem'
        certificate_path = tmp_path / 'sender-cert.pem'
        signature_path = tmp_path / 'signature.der'

        no_encryption = NoEncryption()
        key_pem = parties.sender.signing_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, no_encryption)
        certificate_pem = parties.sender.signing_certificate.public_bytes(Encoding.PEM)

        _ = payload_path.write_bytes(EDI_Entity)
        _ = key_path.write_bytes(key_pem)
        _ = certificate_path.write_bytes(certificate_pem)

        command = [
            'openssl', 'cms', '-sign', '-binary',
            '-md', 'sha256',
            '-in', str(payload_path),
            '-signer', str(certificate_path),
            '-inkey', str(key_path),
            '-outform', 'DER',
            '-out', str(signature_path),
        ]
        _ = subprocess_run(command, check=True, capture_output=True)

        # .. frame the detached signature in the multipart/signed layout of RFC 1847,
        # with the CRLF boundary framing of RFC 2046 ..
        signature_der = signature_path.read_bytes()
        signature_base64 = b64encode(signature_der)

        body = b'--' + _oracle_boundary + b'\r\n' + \
            EDI_Entity + b'\r\n' + \
            b'--' + _oracle_boundary + b'\r\n' + \
            b'Content-Type: application/pkcs7-signature\r\n' + \
            b'Content-Transfer-Encoding: base64\r\n\r\n' + \
            signature_base64 + b'\r\n' + \
            b'--' + _oracle_boundary + b'--\r\n'

        boundary_text = _oracle_boundary.decode('ascii')

        content_type = 'multipart/signed; protocol="application/pkcs7-signature"; ' + \
            f'micalg=sha-256; boundary="{boundary_text}"'

        # .. and verify it with ours - the recovered content is the entity openssl signed.
        signed = new_part(body, content_type)
        result = verify(signed, parties.receiver)

        assert result.part.data == EDI_Payload
        assert result.part.content_type == EDI_Content_Type

# ################################################################################################################################

    def test_our_envelope_decrypts_with_openssl(self, parties:'any_', tmp_path:'Path') -> 'None':
        part = edi_part()
        encrypted = encrypt(part, parties.sender.peer_encryption_certificate, EncryptionAlgorithm.AES_256_CBC)

        envelope_path = tmp_path / 'envelope.der'
        key_path = tmp_path / 'receiver-key.pem'
        certificate_path = tmp_path / 'receiver-cert.pem'
        plaintext_path = tmp_path / 'plaintext.bin'

        no_encryption = NoEncryption()
        key_pem = parties.receiver.decryption_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, no_encryption)
        certificate_pem = parties.sender.peer_encryption_certificate.public_bytes(Encoding.PEM)

        _ = envelope_path.write_bytes(encrypted.data)
        _ = key_path.write_bytes(key_pem)
        _ = certificate_path.write_bytes(certificate_pem)

        # Decrypt with an implementation we did not write.
        command = [
            'openssl', 'cms', '-decrypt',
            '-inform', 'DER',
            '-in', str(envelope_path),
            '-inkey', str(key_path),
            '-recip', str(certificate_path),
            '-out', str(plaintext_path),
        ]
        _ = subprocess_run(command, check=True, capture_output=True)

        recovered = plaintext_path.read_bytes()
        assert recovered == EDI_Entity

# ################################################################################################################################

    def test_openssl_envelope_decrypts_with_ours(self, parties:'any_', tmp_path:'Path') -> 'None':

        # Encrypt to the receiver with an implementation we did not write ..
        payload_path = tmp_path / 'payload.bin'
        certificate_path = tmp_path / 'recipient.pem'
        envelope_path = tmp_path / 'envelope.der'

        certificate_pem = parties.sender.peer_encryption_certificate.public_bytes(Encoding.PEM)

        _ = payload_path.write_bytes(EDI_Entity)
        _ = certificate_path.write_bytes(certificate_pem)

        command = [
            'openssl', 'cms', '-encrypt', '-aes-256-cbc', '-binary',
            '-outform', 'DER',
            '-in', str(payload_path),
            '-out', str(envelope_path),
            str(certificate_path),
        ]
        _ = subprocess_run(command, check=True, capture_output=True)

        # .. and decrypt it with ours.
        envelope_der = envelope_path.read_bytes()

        encrypted = new_part(envelope_der, _enveloped_content_type)
        decrypted = decrypt(encrypted, parties.receiver)

        assert decrypted.data == EDI_Payload
        assert decrypted.content_type == EDI_Content_Type

# ################################################################################################################################
# ################################################################################################################################
