# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone

# cryptography
from cryptography.x509 import BasicConstraints, ExtensionNotFound, KeyUsage

# Zato
from zato.common.util.xml_.core import XMLSecurityException
from zato.common.util.xml_.keystore import certificate_list

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from zato.common.util.xml_.keystore import Keystore
    any_ = any_
    datetime = datetime
    Keystore = Keystore

# ################################################################################################################################
# ################################################################################################################################

def _check_validity_period(certificate:'any_', now:'datetime') -> 'None':
    """ Rejects a certificate outside its validity period.
    """
    if now < certificate.not_valid_before_utc:
        raise XMLSecurityException(f'Certificate `{certificate.subject}` is not yet valid')

    if now > certificate.not_valid_after_utc:
        raise XMLSecurityException(f'Certificate `{certificate.subject}` has expired')

# ################################################################################################################################

def _check_is_certificate_authority(certificate:'any_') -> 'None':
    """ Rejects an issuer that is not marked as a certificate authority. RFC 5280 section 4.2.1.9
    allows a certificate to issue other certificates only with the cA bit of basicConstraints set.
    """
    try:
        basic_constraints = certificate.extensions.get_extension_for_class(BasicConstraints)
    except ExtensionNotFound:
        raise XMLSecurityException(f'Issuer `{certificate.subject}` carries no basicConstraints extension')

    if not basic_constraints.value.ca:
        raise XMLSecurityException(f'Issuer `{certificate.subject}` is not a certificate authority')

# ################################################################################################################################

def _check_key_usage(certificate:'any_', usage_name:'str') -> 'None':
    """ Rejects a certificate whose keyUsage extension excludes the use it is being put to.
    A certificate with the extension absent is unconstrained, which is what the specification
    says, so only an extension that is present and says no is a failure.
    """
    try:
        key_usage = certificate.extensions.get_extension_for_class(KeyUsage)
    except ExtensionNotFound:
        return

    if not getattr(key_usage.value, usage_name):
        raise XMLSecurityException(f'Certificate `{certificate.subject}` is not permitted to {usage_name.replace("_", " ")}')

# ################################################################################################################################

def validate_certificate_chain(chain:'certificate_list', keystore:'Keystore') -> 'None':
    """ Establishes trust in the signer's certificate. With trust anchors configured,
    the chain must lead from the leaf to one of them with valid signatures and periods.
    Without anchors, the leaf must equal the pinned peer certificate.
    """
    now = datetime.now(timezone.utc)
    leaf = chain[0]

    # Trust comes from what the operator configured - either anchors or a pinned certificate. With
    # neither, the certificate that arrives inside the message has nothing to be checked against, so
    # the configuration is incomplete and verification cannot proceed.
    if not keystore.trust_anchors:

        pinned = keystore.peer_signing_certificate

        if not pinned:
            raise XMLSecurityException('No trust anchors and no pinned peer certificate are configured')

        if leaf != pinned:
            raise XMLSecurityException('Signer certificate does not match the pinned one')

        # A pinned certificate still expires - the anchor-walking branch below checks this for
        # every certificate it sees and the pinned branch has to do the same.
        _check_validity_period(leaf, now)
        _check_key_usage(leaf, 'digital_signature')

        return

    # Walk from the leaf upwards - each certificate must be within its validity period
    # and signed either by the next chain element or directly by a trust anchor.
    anchors_by_subject = {}
    for anchor in keystore.trust_anchors:
        anchors_by_subject[anchor.subject.rfc4514_string()] = anchor

    _check_key_usage(leaf, 'digital_signature')

    current = leaf
    remaining = chain[1:]

    while True:
        _check_validity_period(current, now)

        issuer_name = current.issuer.rfc4514_string()

        # The current certificate chains directly to a trust anchor - verify and we are done.
        if anchor := anchors_by_subject.get(issuer_name):
            _check_validity_period(anchor, now)
            _check_is_certificate_authority(anchor)
            _check_key_usage(anchor, 'key_cert_sign')
            current.verify_directly_issued_by(anchor)
            break

        # Otherwise the next chain element must be the issuer.
        if not remaining:
            raise XMLSecurityException(f'No trust anchor found for issuer `{issuer_name}`')

        issuer = remaining[0]
        remaining = remaining[1:]

        _check_is_certificate_authority(issuer)
        _check_key_usage(issuer, 'key_cert_sign')

        current.verify_directly_issued_by(issuer)
        current = issuer

# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################
