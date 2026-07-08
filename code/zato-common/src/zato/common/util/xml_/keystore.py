# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# cryptography
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.x509 import Certificate, load_pem_x509_certificates

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes
    from zato.common.typing_ import bytesnone
    bytesnone = bytesnone

# ################################################################################################################################
# ################################################################################################################################

certificate_list = list[Certificate]

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Keystore:
    """ All keys and certificates one party needs for secure XML exchanges.

    For RSA suites the signing key doubles as the decryption key unless a separate one
    is configured. For EdDSA suites signing uses an Ed25519 key and decryption uses
    a separate X25519 key agreement key, because neither of those curves can do both jobs.
    """
    # Our own private key used to sign outgoing messages, with its certificate chain -
    # the leaf certificate first, any intermediates after it. Assigned by new_keystore.
    signing_key: 'PrivateKeyTypes | None' = None
    signing_certificate_chain: 'certificate_list'

    # Our own private key used to decrypt incoming messages - for RSA key transport
    # this is an RSA key, for X25519 key agreement it is an X25519 key.
    decryption_key: 'PrivateKeyTypes | None' = None

    # The other side's certificates - one to encrypt to and one to verify their signatures with.
    # The verification certificate is optional because with token-based key identification
    # the certificate arrives inside the message itself.
    peer_encryption_certificate: 'Certificate | None' = None
    peer_signing_certificate:    'Certificate | None' = None

    # Certificates that incoming signing certificates must chain up to. When empty,
    # trust is pinned to peer_signing_certificate instead. Assigned by new_keystore.
    trust_anchors: 'certificate_list'

    # An externally issued SAML 2.0 assertion travelling as the message's security token
    # instead of a certificate - security token services such as the Australian SBR's
    # VANguard hand these out, confirming the holder of the signing key below.
    saml_assertion: 'bytesnone' = None

# ################################################################################################################################

    @property
    def signing_certificate(self) -> 'Certificate':
        out = self.signing_certificate_chain[0]
        return out

# ################################################################################################################################
# ################################################################################################################################

def new_keystore() -> 'Keystore':
    """ Returns a fresh keystore with its list fields in place.
    """

    # Our response to produce
    out = Keystore()

    out.signing_certificate_chain = []
    out.trust_anchors = []

    return out

# ################################################################################################################################
# ################################################################################################################################

def load_private_key_pem(data:'bytes', password:'bytesnone'=None) -> 'PrivateKeyTypes':
    """ Loads a PEM private key of any of the supported types (RSA, Ed25519, X25519).
    """
    out = load_pem_private_key(data, password)
    return out

# ################################################################################################################################

def load_certificates_pem(data:'bytes') -> 'certificate_list':
    """ Loads one or more PEM certificates, preserving their order.
    """
    out = load_pem_x509_certificates(data)
    return out

# ################################################################################################################################
# ################################################################################################################################
