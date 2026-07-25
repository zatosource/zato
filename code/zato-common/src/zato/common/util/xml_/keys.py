# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# cryptography
from cryptography.hazmat.primitives.asymmetric.padding import MGF1, OAEP
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.keywrap import aes_key_unwrap
from cryptography.hazmat.primitives.serialization import load_der_public_key

# Zato
from zato.common.typing_ import cast_
from zato.common.util.xml_.constants import Algorithm, NS
from zato.common.util.xml_.core import qname, XMLSecurityException, XMLSecurityUnsupportedAlgorithm
from zato.common.util.xml_.xmlsec import decode_base64

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
    from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
    from zato.common.typing_ import any_, bytesnone
    from zato.common.util.xml_.keystore import Keystore
    any_ = any_
    bytesnone = bytesnone
    Keystore = Keystore
    RSAPrivateKey = RSAPrivateKey
    X25519PrivateKey = X25519PrivateKey
    X25519PublicKey = X25519PublicKey

# ################################################################################################################################
# ################################################################################################################################

# The AES content key size used by the key derivation and recovery helpers.
_content_key_size_bytes = 16

# ################################################################################################################################
# ################################################################################################################################

def derive_key_encryption_key(shared_secret:'bytes', hkdf_info:'bytes') -> 'bytes':
    """ Derives an AES key-wrapping key from an X25519 shared secret with HKDF-SHA256.
    """
    hkdf = HKDF(algorithm=SHA256(), length=_content_key_size_bytes, salt=None, info=hkdf_info)

    out = hkdf.derive(shared_secret)
    return out

# ################################################################################################################################

def recover_content_key(encrypted_key:'any_', keystore:'Keystore', hkdf_info:'bytesnone'=None) -> 'bytes':
    """ Recovers the AES content key from an xenc:EncryptedKey, whichever
    of the two supported key transport mechanisms protected it.
    """
    encryption_method = encrypted_key.find(qname(NS.XENC, 'EncryptionMethod'))
    algorithm = encryption_method.get('Algorithm')

    cipher_data = encrypted_key.find(qname(NS.XENC, 'CipherData'))
    cipher_value = cipher_data.find(qname(NS.XENC, 'CipherValue'))
    wrapped_key = decode_base64(cipher_value.text or '')

    # RSA-OAEP key transport - our RSA key decrypts the wrapped key directly.
    if algorithm == Algorithm.RSA_OAEP:
        oaep_padding = OAEP(mgf=MGF1(SHA256()), algorithm=SHA256(), label=None)
        rsa_key = cast_('RSAPrivateKey', keystore.decryption_key)

        # Every failure reason collapses into the same message, as it does on the AES-GCM path.
        try:
            out = rsa_key.decrypt(wrapped_key, oaep_padding)
        except Exception:
            raise XMLSecurityException('Could not recover the content key')

        return out

    # AES key wrap after X25519 agreement - rebuild the shared secret
    # from the sender's ephemeral public key, derive the wrapping key, unwrap.
    if algorithm == Algorithm.AES128_KeyWrap:

        # The derivation info string is protocol-specific, so without one this mechanism is unavailable.
        if hkdf_info is None:
            raise XMLSecurityUnsupportedAlgorithm('Key agreement requires an HKDF info string')

        key_info = encrypted_key.find(qname(NS.DS, 'KeyInfo'))
        agreement_method = key_info.find(qname(NS.XENC, 'AgreementMethod'))
        originator = agreement_method.find(qname(NS.XENC, 'OriginatorKeyInfo'))
        key_value = originator.find(qname(NS.DS, 'KeyValue'))
        der_key_value = key_value.find(qname(NS.XMLDSIG11, 'DEREncodedKeyValue'))

        ephemeral_bytes = decode_base64(der_key_value.text or '')
        ephemeral_public_key = cast_('X25519PublicKey', load_der_public_key(ephemeral_bytes))

        x25519_key = cast_('X25519PrivateKey', keystore.decryption_key)
        shared_secret = x25519_key.exchange(ephemeral_public_key)
        key_encryption_key = derive_key_encryption_key(shared_secret, hkdf_info)

        out = aes_key_unwrap(key_encryption_key, wrapped_key)
        return out

    raise XMLSecurityUnsupportedAlgorithm(f'Unsupported key transport algorithm `{algorithm}`')

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################
