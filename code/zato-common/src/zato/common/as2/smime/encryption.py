# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

Encrypting an outgoing entity to a partner's certificate - the EnvelopedData of RFC 5652 for the
CBC algorithms and the AuthEnvelopedData of RFC 5083 for the AES-GCM ones.
"""

# cryptography
from cryptography.hazmat.decrepit.ciphers.algorithms import TripleDES
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.ciphers import Cipher, CipherAlgorithm
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC

# Zato
from zato.common.as2.common import AS2Exception, Default, EncryptionAlgorithm
from zato.common.as2.smime.algorithms import AES_Block_Size, AES_CBC_Key_Size_By_Name, AES_CBC_OID_By_Name, \
    DES_Block_Size, DES_Key_Bits_Mask, DES_Key_Size, DES_Parity_Bit, GCM_Key_Size_By_Name, \
    GCM_Nonce_Size, GCM_OID_By_Name, GCM_Tag_Size, OID
from zato.common.as2.smime.der import Der_Null, encode_der, encode_der_integer, encode_der_octet_string, Tag
from zato.common.as2.smime.part import encode_base64_lines, serialize_part, SMIMEPart
from zato.common.crypto.api import CryptoManager
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
    from cryptography.x509 import Certificate
    Certificate = Certificate
    RSAPublicKey = RSAPublicKey

# ################################################################################################################################
# ################################################################################################################################

def build_key_transport_recipient(content_key:'bytes', certificate:'Certificate') -> 'bytes':
    """ Builds a KeyTransRecipientInfo per RFC 5652 section 6.2.1 - the content encryption key,
    RSA-encrypted to the recipient's certificate, named by issuer and serial number.
    """
    certificate_public_key = certificate.public_key()
    public_key = cast_('RSAPublicKey', certificate_public_key)

    padding = PKCS1v15()
    encrypted_key = public_key.encrypt(content_key, padding)

    issuer = certificate.issuer.public_bytes()
    serial = encode_der_integer(certificate.serial_number)
    issuer_and_serial = encode_der(Tag.Sequence, issuer + serial)

    key_algorithm = encode_der(Tag.Sequence, OID.RSA_Encryption + Der_Null)
    version = encode_der_integer(0)
    encrypted_key_octets = encode_der_octet_string(encrypted_key)

    out = encode_der(Tag.Sequence, version + issuer_and_serial + key_algorithm + encrypted_key_octets)
    return out

# ################################################################################################################################

def _encrypt_gcm(content:'bytes', certificate:'Certificate', algorithm:'str', key_size:'int') -> 'bytes':
    """ Builds a CMS AuthEnvelopedData structure per RFC 5083 with AES-GCM content encryption
    per RFC 5084 - the opt-in outbound path for partners that ask for it.
    """
    # A fresh content encryption key and nonce for every message.
    content_key = CryptoManager.generate_bytes(key_size)
    nonce = CryptoManager.generate_bytes(GCM_Nonce_Size)

    cipher = AESGCM(content_key)
    sealed = cipher.encrypt(nonce, content, None)

    # AESGCM appends the authentication tag - CMS carries it in a separate field.
    ciphertext = sealed[:-GCM_Tag_Size]
    tag = sealed[-GCM_Tag_Size:]

    recipient_info = build_key_transport_recipient(content_key, certificate)
    recipient_infos = encode_der(Tag.Set, recipient_info)

    # GCMParameters per RFC 5084 - the nonce and the explicit tag length.
    nonce_octets = encode_der_octet_string(nonce)
    tag_size = encode_der_integer(GCM_Tag_Size)
    parameters = encode_der(Tag.Sequence, nonce_octets + tag_size)
    algorithm_identifier = encode_der(Tag.Sequence, GCM_OID_By_Name[algorithm] + parameters)

    encrypted_content = encode_der(Tag.Context_0_Implicit, ciphertext)
    encrypted_content_info = encode_der(Tag.Sequence, OID.Data + algorithm_identifier + encrypted_content)

    version = encode_der_integer(0)
    mac = encode_der_octet_string(tag)
    auth_enveloped = encode_der(Tag.Sequence, version + recipient_infos + encrypted_content_info + mac)

    out = encode_der(Tag.Sequence, OID.Auth_Enveloped_Data + encode_der(Tag.Context_0, auth_enveloped))
    return out

# ################################################################################################################################

def _new_3des_key() -> 'bytes':
    """ Returns a fresh three-key 3DES key with the parity bit of every byte set,
    as DES key material is defined to carry odd parity.
    """
    raw = CryptoManager.generate_bytes(DES_Key_Size)

    key_bytes = bytearray()

    for byte in raw:

        # Keep the seven key bits and count how many of them are set ..
        key_bits = byte & DES_Key_Bits_Mask
        ones_count = bin(key_bits).count('1')

        # .. the parity bit makes the total number of set bits odd.
        if ones_count % 2 == 0:
            key_bits |= DES_Parity_Bit

        key_bytes.append(key_bits)

    out = bytes(key_bytes)
    return out

# ################################################################################################################################

def _add_cbc_padding(content:'bytes', block_size:'int') -> 'bytes':
    """ Appends the PKCS#7 block padding of a CBC plaintext - the counterpart of strip_cbc_padding.
    """
    pad_length = block_size - (len(content) % block_size)

    out = content + bytes([pad_length]) * pad_length
    return out

# ################################################################################################################################

def _encrypt_cbc(
    content:'bytes',
    certificate:'Certificate',
    content_key:'bytes',
    cipher_algorithm:'CipherAlgorithm',
    algorithm_oid:'bytes',
    block_size:'int',
    ) -> 'bytes':
    """ Builds a CMS EnvelopedData structure with CBC content encryption per RFC 5652 - the exact
    structure the inbound enveloped-data reader parses on the way in.
    """
    # A fresh IV for every message.
    initialization_vector = CryptoManager.generate_bytes(block_size)

    # CBC needs the plaintext padded to whole blocks before encryption.
    padded = _add_cbc_padding(content, block_size)

    cipher_mode = CBC(initialization_vector)

    cipher = Cipher(cipher_algorithm, cipher_mode)
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()

    recipient_info = build_key_transport_recipient(content_key, certificate)
    recipient_infos = encode_der(Tag.Set, recipient_info)

    # The algorithm identifier carries the IV as its parameter.
    iv_octets = encode_der_octet_string(initialization_vector)
    algorithm_identifier = encode_der(Tag.Sequence, algorithm_oid + iv_octets)

    encrypted_content = encode_der(Tag.Context_0_Implicit, ciphertext)
    encrypted_content_info = encode_der(Tag.Sequence, OID.Data + algorithm_identifier + encrypted_content)

    version = encode_der_integer(0)
    enveloped = encode_der(Tag.Sequence, version + recipient_infos + encrypted_content_info)

    out = encode_der(Tag.Sequence, OID.Enveloped_Data + encode_der(Tag.Context_0, enveloped))
    return out

# ################################################################################################################################

def _encrypt_aes_cbc(content:'bytes', certificate:'Certificate', key_size:'int', algorithm_oid:'bytes') -> 'bytes':
    """ Builds a CMS EnvelopedData structure with AES-CBC content encryption - the interop baseline.
    """
    # A fresh content encryption key for every message.
    content_key = CryptoManager.generate_bytes(key_size)

    out = _encrypt_cbc(content, certificate, content_key, AES(content_key), algorithm_oid, AES_Block_Size)
    return out

# ################################################################################################################################

def _encrypt_3des(content:'bytes', certificate:'Certificate') -> 'bytes':
    """ Builds a CMS EnvelopedData structure with 3DES-CBC content encryption per RFC 5652 -
    the outbound path for partners that cannot decrypt AES.
    """
    # A fresh content encryption key for every message, with the parity bits DES keys require.
    content_key = _new_3des_key()

    out = _encrypt_cbc(content, certificate, content_key, TripleDES(content_key), OID.DES_EDE3_CBC, DES_Block_Size)
    return out

# ################################################################################################################################

def encrypt(
    part:'SMIMEPart',
    certificate:'Certificate',
    algorithm:'str' = Default.Encryption_Algorithm,
    force_base64:'bool' = False,
    prevent_canonicalization:'bool' = False,
    ) -> 'SMIMEPart':
    """ Encrypts an entity to the recipient's certificate, producing an application/pkcs7-mime
    entity with smime-type=enveloped-data (CBC) or its AuthEnvelopedData sibling (GCM).
    """
    content = serialize_part(part, prevent_canonicalization)

    # The AES-CBC baseline is built in-house because the library's envelope builder only ever
    # produces AES-128-CBC and offers no way to pick another algorithm ..
    if key_size := AES_CBC_Key_Size_By_Name.get(algorithm):
        envelope = _encrypt_aes_cbc(content, certificate, key_size, AES_CBC_OID_By_Name[algorithm])

    # .. the GCM opt-in is built in-house because the library has no AuthEnvelopedData support ..
    elif key_size := GCM_Key_Size_By_Name.get(algorithm):
        envelope = _encrypt_gcm(content, certificate, algorithm, key_size)

    # .. 3DES for partners that cannot decrypt AES is built in-house
    # because the library refuses to produce it ..
    elif algorithm == EncryptionAlgorithm.DES_EDE3_CBC:
        envelope = _encrypt_3des(content, certificate)

    # .. and anything else is not an algorithm outgoing messages may use.
    else:
        raise AS2Exception(f'Unsupported encryption algorithm `{algorithm}`')

    # Our response to produce
    out = SMIMEPart()

    out.content_type = 'application/pkcs7-mime; smime-type=enveloped-data; name="smime.p7m"'

    if force_base64:
        out.data = encode_base64_lines(envelope)
        out.content_transfer_encoding = 'base64'
    else:
        out.data = envelope
        out.content_transfer_encoding = 'binary'

    return out

# ################################################################################################################################
# ################################################################################################################################
