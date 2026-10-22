# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.util.xml_.keystore import new_keystore

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes
    from cryptography.x509 import Certificate
    from zato.common.util.xml_.keystore import certificate_list, Keystore
    Certificate = Certificate
    certificate_list = certificate_list
    Keystore = Keystore
    PrivateKeyTypes = PrivateKeyTypes

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class LocalKeys:
    """ The private key material of our own party. An agreement has only public certificates,
    so the signing key is always supplied separately from it.
    """
    # Our own private key used to sign outgoing messages and receipts.
    signing_key: 'PrivateKeyTypes | None' = None

    # The certificate chain of the signing key, the leaf certificate first.
    signing_certificate_chain: 'certificate_list'

    # Certificates the signing certificates of our partners must chain up to, in addition to
    # the trust anchors that the agreement itself names.
    trust_anchors: 'certificate_list'

    def __init__(self) -> 'None':
        self.signing_certificate_chain = []
        self.trust_anchors = []

# ################################################################################################################################

    @property
    def signing_certificate(self) -> 'Certificate':
        out = self.signing_certificate_chain[0]
        return out

# ################################################################################################################################
# ################################################################################################################################

def local_keys_from_keystore(keystore:'Keystore') -> 'LocalKeys':
    """ Returns the local keys of a keystore, which is how the WS-Security definitions hold them.
    """
    out = LocalKeys()
    out.signing_key = keystore.signing_key
    out.signing_certificate_chain = keystore.signing_certificate_chain
    out.trust_anchors = keystore.trust_anchors

    return out

# ################################################################################################################################

def signing_keystore(local_keys:'LocalKeys') -> 'Keystore':
    """ Returns a keystore that signs with the local keys.
    """
    out = new_keystore()
    out.signing_key = local_keys.signing_key
    out.signing_certificate_chain = local_keys.signing_certificate_chain

    return out

# ################################################################################################################################

def verification_keystore(
    local_keys:'LocalKeys',
    agreement_anchors:'certificate_list',
    peer_certificate:'Certificate | None',
    ) -> 'Keystore':
    """ Returns a keystore that validates the signing certificate of a partner. With trust anchors
    from either the local keys or the agreement, the partner's chain is to lead to one of them.
    Without any, the partner's certificate is pinned to the one the agreement names.
    """
    out = new_keystore()
    out.peer_signing_certificate = peer_certificate

    for anchor in local_keys.trust_anchors:
        out.trust_anchors.append(anchor)

    for anchor in agreement_anchors:
        out.trust_anchors.append(anchor)

    return out

# ################################################################################################################################
# ################################################################################################################################
