# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

Which cryptographic algorithms this package speaks and how each of them is named - the object
identifiers naming them inside CMS structures, the RFC 5751 names naming them in MIME headers,
and the sizes their keys, blocks, nonces and tags have.
"""

# cryptography
from cryptography.hazmat.decrepit.ciphers.algorithms import TripleDES
from cryptography.hazmat.primitives.ciphers.algorithms import AES, AES128, AES256
from cryptography.hazmat.primitives.hashes import SHA1, SHA256, SHA384, SHA512

# Zato
from zato.common.as2.common import DigestAlgorithm, EncryptionAlgorithm
from zato.common.as2.smime.der import encode_oid

# ################################################################################################################################
# ################################################################################################################################

class OID:
    """ Object identifiers of the CMS structures and algorithms this package handles,
    each stored as its complete DER encoding for direct byte comparisons.
    """
    Data                = encode_oid('1.2.840.113549.1.7.1')
    Signed_Data         = encode_oid('1.2.840.113549.1.7.2')
    Enveloped_Data      = encode_oid('1.2.840.113549.1.7.3')
    Content_Type_Attr   = encode_oid('1.2.840.113549.1.9.3')
    Message_Digest      = encode_oid('1.2.840.113549.1.9.4')
    Signing_Time        = encode_oid('1.2.840.113549.1.9.5')
    Compressed_Data     = encode_oid('1.2.840.113549.1.9.16.1.9')
    Auth_Enveloped_Data = encode_oid('1.2.840.113549.1.9.16.1.23')
    Zlib                = encode_oid('1.2.840.113549.1.9.16.3.8')
    RSA_Encryption      = encode_oid('1.2.840.113549.1.1.1')
    DES_EDE3_CBC        = encode_oid('1.2.840.113549.3.7')
    AES_128_CBC         = encode_oid('2.16.840.1.101.3.4.1.2')
    AES_192_CBC         = encode_oid('2.16.840.1.101.3.4.1.22')
    AES_256_CBC         = encode_oid('2.16.840.1.101.3.4.1.42')
    AES_128_GCM         = encode_oid('2.16.840.1.101.3.4.1.6')
    AES_256_GCM         = encode_oid('2.16.840.1.101.3.4.1.46')
    SHA1                = encode_oid('1.3.14.3.2.26')
    SHA256              = encode_oid('2.16.840.1.101.3.4.2.1')
    SHA384              = encode_oid('2.16.840.1.101.3.4.2.2')
    SHA512              = encode_oid('2.16.840.1.101.3.4.2.3')

# ################################################################################################################################
# ################################################################################################################################

# The nonce and authentication tag sizes for AES-GCM content encryption (RFC 5084 section 3.2).
GCM_Nonce_Size = 12
GCM_Tag_Size = 16

# The block sizes of 3DES and AES in CBC mode, which their PKCS#7 padding is based on.
DES_Block_Size = 8
AES_Block_Size = 16

# The key and IV sizes of three-key 3DES in CBC mode.
DES_Key_Size = 24
DES_IV_Size = 8

# The low bit of every 3DES key byte is a parity bit (RFC 5652 section 6.3 key expectations).
DES_Parity_Bit = 0x01
DES_Key_Bits_Mask = 0xFE

# The key sizes in bytes of the two AES-GCM algorithms.
_aes_128_key_size = 16
_aes_256_key_size = 32

# ################################################################################################################################
# ################################################################################################################################

# Maps RFC 5751 digest names to their hash classes.
Digest_By_Name = {
    DigestAlgorithm.SHA1:   SHA1,
    DigestAlgorithm.SHA256: SHA256,
    DigestAlgorithm.SHA384: SHA384,
    DigestAlgorithm.SHA512: SHA512,
}

# Maps digest algorithm identifiers from SignerInfo back to RFC 5751 names.
Digest_Name_By_OID = {
    OID.SHA1:   DigestAlgorithm.SHA1,
    OID.SHA256: DigestAlgorithm.SHA256,
    OID.SHA384: DigestAlgorithm.SHA384,
    OID.SHA512: DigestAlgorithm.SHA512,
}

# Every micalg spelling accepted on input, mapped to the RFC 5751 spelling always used on output.
Micalg_Spelling = {
    'sha1':    DigestAlgorithm.SHA1,
    'sha-1':   DigestAlgorithm.SHA1,
    'sha256':  DigestAlgorithm.SHA256,
    'sha-256': DigestAlgorithm.SHA256,
    'sha384':  DigestAlgorithm.SHA384,
    'sha-384': DigestAlgorithm.SHA384,
    'sha512':  DigestAlgorithm.SHA512,
    'sha-512': DigestAlgorithm.SHA512,
}

# Maps outbound CBC algorithm names to the classes the envelope builder accepts.
CBC_Class_By_Name = {
    EncryptionAlgorithm.AES_128_CBC: AES128,
    EncryptionAlgorithm.AES_256_CBC: AES256,
}

# Maps inbound CBC algorithm identifiers to their cipher classes and block sizes -
# AES-192 has no size-specific class, so the size-checking is left to the generic one.
CBC_Class_By_OID = {
    OID.DES_EDE3_CBC: TripleDES,
    OID.AES_128_CBC:  AES128,
    OID.AES_192_CBC:  AES,
    OID.AES_256_CBC:  AES256,
}

CBC_Block_Size_By_OID = {
    OID.DES_EDE3_CBC: DES_Block_Size,
    OID.AES_128_CBC:  AES_Block_Size,
    OID.AES_192_CBC:  AES_Block_Size,
    OID.AES_256_CBC:  AES_Block_Size,
}

# Key sizes in bytes for the AES-GCM algorithms built in-house through AuthEnvelopedData.
GCM_Key_Size_By_Name = {
    EncryptionAlgorithm.AES_128_GCM: _aes_128_key_size,
    EncryptionAlgorithm.AES_256_GCM: _aes_256_key_size,
}

# Maps AES-GCM algorithm names to their object identifiers and back.
GCM_OID_By_Name = {
    EncryptionAlgorithm.AES_128_GCM: OID.AES_128_GCM,
    EncryptionAlgorithm.AES_256_GCM: OID.AES_256_GCM,
}

GCM_Key_Size_By_OID = {
    OID.AES_128_GCM: _aes_128_key_size,
    OID.AES_256_GCM: _aes_256_key_size,
}

# ################################################################################################################################
# ################################################################################################################################
