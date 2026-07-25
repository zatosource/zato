# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The CMS structures of RFC 5652 and RFC 5083 recomputed from scratch - the object
# identifiers are typed out literally, the DER is parsed independently of the code
# under test, and every cryptographic value is redone with primitives alone.

# stdlib
from base64 import b64decode
from hashlib import sha256

# asn1crypto
from asn1crypto.cms import ContentInfo
from asn1crypto.core import Integer, OctetString, Sequence

# cryptography
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.ciphers.algorithms import AES256
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.hashes import SHA256

# Zato
from zato.common.as2.common import EncryptionAlgorithm
from zato.common.as2.smime import encrypt, sign

# Zato
from .conformance_helpers import boundary_of, EDI_Entity, edi_part, split_multipart

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# RFC 5652 sections 4, 5 and 6 with RFC 5083 - the CMS content type identifiers.
_oid_signed_data         = '1.2.840.113549.1.7.2'
_oid_enveloped_data      = '1.2.840.113549.1.7.3'
_oid_auth_enveloped_data = '1.2.840.113549.1.9.16.1.23'

# RFC 5652 section 11.2 - the message-digest signed attribute.
_oid_message_digest = '1.2.840.113549.1.9.4'

# RFC 8017 - RSAES-PKCS1-v1_5 key transport.
_oid_rsa = '1.2.840.113549.1.1.1'

# NIST algorithm identifiers - AES-256 in CBC and GCM modes.
_oid_aes256_cbc = '2.16.840.1.101.3.4.1.42'
_oid_aes256_gcm = '2.16.840.1.101.3.4.1.46'

# ################################################################################################################################
# ################################################################################################################################

class _GCMParameters(Sequence):
    """ RFC 5084 section 3.2 - the AES-GCM nonce with the tag length, typed out
    from the specification instead of relying on any parser's built-in knowledge.
    """
    _fields = [
        ('nonce', OctetString),
        ('icv_len', Integer),
    ]

# ################################################################################################################################
# ################################################################################################################################

class TestSignedDataRecompute:
    """ RFC 5652 sections 5.4 and 5.6 - the SignedData of a multipart/signed message
    verifies after an independent DER parse: the message digest recomputes with
    hashlib over the covered part and the signature verifies with the public key alone.
    """

    def test_signature_recomputes_independently(self, parties:'any_') -> 'None':
        part = edi_part()
        signed = sign(part, parties.sender)

        # Split the multipart with plain byte operations ..
        boundary = boundary_of(signed.content_type)
        parts = split_multipart(signed.data, boundary)

        part_count = len(parts)
        assert part_count == 2

        covered = parts[0]
        signature_part = parts[1]

        # .. the covered part is the literally typed MIME entity ..
        assert covered == EDI_Entity

        # .. the second part carries the base64 of a DER SignedData ..
        _, _, signature_body = signature_part.partition(b'\r\n\r\n')
        signature_der = b64decode(signature_body)

        content_info = ContentInfo.load(signature_der)
        assert content_info['content_type'].dotted == _oid_signed_data

        signed_data = content_info['content']
        signer_infos = signed_data['signer_infos']
        signer_info = signer_infos[0]

        # .. the declared digest algorithm is SHA-256 ..
        digest_algorithm = signer_info['digest_algorithm']
        assert digest_algorithm['algorithm'].native == 'sha256'

        # .. the message-digest attribute recomputes with hashlib over the covered part ..
        declared_digest = b''

        for attribute in signer_info['signed_attrs']:
            if attribute['type'].dotted == _oid_message_digest:
                values = attribute['values']
                first_entry = values[0]
                declared_digest = first_entry.native

        recomputed_digest = sha256(covered).digest()
        assert declared_digest == recomputed_digest

        # .. and the signature verifies with the public key alone - RFC 5652 section 5.4
        # says the signature covers the signed attributes re-encoded as an explicit SET OF.
        signed_attrs_der = signer_info['signed_attrs'].dump()
        set_of_der = b'\x31' + signed_attrs_der[1:]

        public_key = parties.sender.signing_certificate.public_key()
        signature = signer_info['signature'].native

        padding = PKCS1v15()
        digest = SHA256()

        # Raises InvalidSignature if the value does not verify.
        public_key.verify(signature, set_of_der, padding, digest)

# ################################################################################################################################
# ################################################################################################################################

class TestEnvelopedDataRecompute:
    """ RFC 5652 section 6 and RFC 5083 - the enveloped entity decrypts from scratch
    with cryptography primitives only, using nothing but what the DER itself declares.
    """

    def test_cbc_envelope_decrypts_with_primitives_alone(self, parties:'any_') -> 'None':
        part = edi_part()
        encrypted = encrypt(part, parties.sender.peer_encryption_certificate, EncryptionAlgorithm.AES_256_CBC)

        # The DER declares an EnvelopedData with RSA key transport and AES-256-CBC ..
        content_info = ContentInfo.load(encrypted.data)
        assert content_info['content_type'].dotted == _oid_enveloped_data

        enveloped = content_info['content']
        recipient_infos = enveloped['recipient_infos']
        first_recipient = recipient_infos[0]
        recipient = first_recipient.chosen

        key_encryption_algorithm = recipient['key_encryption_algorithm']
        assert key_encryption_algorithm['algorithm'].dotted == _oid_rsa

        content_info_encrypted = enveloped['encrypted_content_info']
        algorithm = content_info_encrypted['content_encryption_algorithm']
        assert algorithm['algorithm'].dotted == _oid_aes256_cbc

        # .. the content key unwraps with the private key and PKCS1v15 alone ..
        wrapped_key = recipient['encrypted_key'].native
        padding = PKCS1v15()
        content_key = parties.receiver.decryption_key.decrypt(wrapped_key, padding)

        # .. the ciphertext decrypts with a bare AES-CBC cipher and the declared IV ..
        initialization_vector = algorithm['parameters'].native
        ciphertext = content_info_encrypted['encrypted_content'].native

        cipher_algorithm = AES256(content_key)
        mode = CBC(initialization_vector)

        cipher = Cipher(cipher_algorithm, mode)
        decryptor = cipher.decryptor()

        padded = decryptor.update(ciphertext) + decryptor.finalize()

        # .. and stripping the PKCS#7 padding by hand yields the literally typed entity.
        pad_length = padded[-1]
        plaintext = padded[:-pad_length]

        assert plaintext == EDI_Entity

# ################################################################################################################################

    def test_gcm_envelope_decrypts_with_primitives_alone(self, parties:'any_') -> 'None':
        part = edi_part()
        encrypted = encrypt(part, parties.sender.peer_encryption_certificate, EncryptionAlgorithm.AES_256_GCM)

        # The DER declares an AuthEnvelopedData with AES-256-GCM ..
        content_info = ContentInfo.load(encrypted.data)
        assert content_info['content_type'].dotted == _oid_auth_enveloped_data

        enveloped = content_info['content']
        recipient_infos = enveloped['recipient_infos']
        first_recipient = recipient_infos[0]
        recipient = first_recipient.chosen

        key_encryption_algorithm = recipient['key_encryption_algorithm']
        assert key_encryption_algorithm['algorithm'].dotted == _oid_rsa

        content_info_encrypted = enveloped['auth_encrypted_content_info']
        algorithm = content_info_encrypted['content_encryption_algorithm']
        assert algorithm['algorithm'].dotted == _oid_aes256_gcm

        # .. the content key unwraps with the private key and PKCS1v15 alone ..
        wrapped_key = recipient['encrypted_key'].native
        padding = PKCS1v15()
        content_key = parties.receiver.decryption_key.decrypt(wrapped_key, padding)

        # .. and the ciphertext decrypts with a bare AESGCM cipher, the declared nonce
        # and the authentication tag the structure carries next to the content.
        parameters_der = algorithm['parameters'].dump()
        parameters = _GCMParameters.load(parameters_der)
        nonce = parameters['nonce'].native

        ciphertext = content_info_encrypted['encrypted_content'].native
        tag = enveloped['mac'].native
        sealed = ciphertext + tag

        cipher = AESGCM(content_key)
        plaintext = cipher.decrypt(nonce, sealed, None)

        assert plaintext == EDI_Entity

# ################################################################################################################################
# ################################################################################################################################
