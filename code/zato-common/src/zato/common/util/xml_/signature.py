# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# cryptography
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.hashes import SHA256

# Zato
from zato.common.typing_ import cast_
from zato.common.util.xml_.constants import Algorithm, NS
from zato.common.util.xml_.core import qname, XMLSecurityException, XMLSecurityUnsupportedAlgorithm
from zato.common.util.xml_.keystore import certificate_list
from zato.common.util.xml_.references import canonicalize_for_reference
from zato.common.util.xml_.xmlsec import canonicalize_exclusive, decode_base64

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
    from zato.common.typing_ import any_
    from zato.common.util.xml_.keystore import Keystore
    any_ = any_
    Ed25519PrivateKey = Ed25519PrivateKey
    Ed25519PublicKey = Ed25519PublicKey
    Keystore = Keystore
    RSAPrivateKey = RSAPrivateKey
    RSAPublicKey = RSAPublicKey

# ################################################################################################################################
# ################################################################################################################################

# The smallest RSA modulus accepted when verifying a signature. The algorithm identifier says nothing
# about key size, so the size is checked separately.
Minimum_RSA_Key_Size_Bits = 2048

# ################################################################################################################################
# ################################################################################################################################

def compute_signature_value(signed_info:'any_', keystore:'Keystore', signature_algorithm:'str') -> 'bytes':
    """ Canonicalizes ds:SignedInfo and signs it with our private key.
    """
    canonical = canonicalize_exclusive(signed_info)

    # Ed25519 keys sign the bytes directly, RSA uses PKCS#1 v1.5 with SHA-256
    # as mandated by the rsa-sha256 algorithm identifier.
    if signature_algorithm == Algorithm.Ed25519:
        ed25519_key = cast_('Ed25519PrivateKey', keystore.signing_key)
        out = ed25519_key.sign(canonical)
    else:
        rsa_key = cast_('RSAPrivateKey', keystore.signing_key)
        out = rsa_key.sign(canonical, PKCS1v15(), SHA256())

    return out

# ################################################################################################################################

# ################################################################################################################################

def verify_signature_value(signature:'any_', chain:'certificate_list') -> 'None':
    """ Canonicalizes ds:SignedInfo and checks the signature value against the leaf public key.
    """
    signed_info = signature.find(qname(NS.DS, 'SignedInfo'))

    signature_method = signed_info.find(qname(NS.DS, 'SignatureMethod'))
    algorithm = signature_method.get('Algorithm')

    # The canonicalization of SignedInfo may carry its own PrefixList.
    canonicalization_method = signed_info.find(qname(NS.DS, 'CanonicalizationMethod'))
    canonical = canonicalize_for_reference(signed_info, canonicalization_method)

    signature_value_element = signature.find(qname(NS.DS, 'SignatureValue'))
    signature_bytes = decode_base64(signature_value_element.text or '')

    verify_signature_bytes(signature_bytes, canonical, algorithm, chain)

# ################################################################################################################################

def verify_signature_bytes(
    signature_bytes:'bytes',
    canonical:'bytes',
    algorithm:'str',
    chain:'certificate_list',
    ) -> 'None':
    """ Checks a signature over already canonicalized bytes against the leaf public key of a chain.
    Only Ed25519 and RSA-SHA256 are recognized, and RSA keys have a minimum size.
    """
    leaf = chain[0]
    public_key = leaf.public_key()

    try:
        if algorithm == Algorithm.Ed25519:
            ed25519_key = cast_('Ed25519PublicKey', public_key)
            ed25519_key.verify(signature_bytes, canonical)
        elif algorithm == Algorithm.RSA_SHA256:
            rsa_key = cast_('RSAPublicKey', public_key)

            # The size is checked before the signature is verified, not after.
            if rsa_key.key_size < Minimum_RSA_Key_Size_Bits:
                raise XMLSecurityException(
                    f'RSA key of {rsa_key.key_size} bits is below the minimum of {Minimum_RSA_Key_Size_Bits}')

            rsa_key.verify(signature_bytes, canonical, PKCS1v15(), SHA256())
        else:
            raise XMLSecurityUnsupportedAlgorithm(f'Unsupported signature algorithm `{algorithm}`')
    except InvalidSignature:
        raise XMLSecurityException('Signature value does not verify')

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################
