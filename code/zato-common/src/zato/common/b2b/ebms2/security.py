# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.b2b.common.keys import verification_keystore
from zato.common.b2b.ebms2.common import EbMS2Exception, EbMS2SecurityException
from zato.common.b2b.ebms2.signature import verify_envelope
from zato.common.util.xml_.core import XMLSecurityException
from zato.common.util.xml_.trust import validate_certificate_chain

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.x509 import Certificate
    from zato.common.b2b.common.keys import LocalKeys
    from zato.common.b2b.ebms2.agreement import Binding, NonRepudiation
    from zato.common.b2b.ebms2.packaging import payload_list
    from zato.common.b2b.ebms2.signature import VerifiedSignature
    from zato.common.typing_ import any_
    from zato.common.util.xml_.keystore import certificate_list
    any_ = any_
    Binding = Binding
    Certificate = Certificate
    certificate_list = certificate_list
    LocalKeys = LocalKeys
    NonRepudiation = NonRepudiation
    payload_list = payload_list
    VerifiedSignature = VerifiedSignature

# ################################################################################################################################
# ################################################################################################################################

# The value of BusinessTransactionCharacteristics/isNonRepudiationRequired that requires a signature.
_true_values = {'true', '1'}

# ################################################################################################################################
# ################################################################################################################################

def sender_non_repudiation(binding:'Binding') -> 'NonRepudiation | None':
    """ Returns the signing requirements of the sender of a message, if it has any.
    """
    if sender_binding := binding.sender_binding:
        out = sender_binding.non_repudiation
    else:
        out = None

    return out

# ################################################################################################################################

def receiver_non_repudiation(binding:'Binding') -> 'NonRepudiation | None':
    """ Returns the signature validation requirements of the receiver of a message, if it has any.
    """
    if receiver_binding := binding.receiver_binding:
        out = receiver_binding.non_repudiation
    else:
        out = None

    return out

# ################################################################################################################################

def is_signature_required(binding:'Binding') -> 'bool':
    """ Says whether the messages exchanged under a binding are to be signed - which they are when the sender has
    non-repudiation requirements, or when the business transaction requires non-repudiation.
    """
    if sender_non_repudiation(binding):
        out = True

    elif send_binding := binding.send_binding:
        value = send_binding.characteristics.get('isNonRepudiationRequired')
        out = value in _true_values

    else:
        out = False

    return out

# ################################################################################################################################

def _expected_certificate(binding:'Binding') -> 'Certificate | None':
    """ Returns the certificate the agreement says the sender signs with, if it names one.
    """
    out = None

    if non_repudiation := sender_non_repudiation(binding):
        if cert_id := non_repudiation.signing_certificate_id:
            try:
                certificate = binding.agreement.get_certificate(cert_id)
            except EbMS2Exception as e:
                raise EbMS2SecurityException(e.detail)
            out = certificate.leaf

    return out

# ################################################################################################################################

def _agreement_anchors(binding:'Binding') -> 'certificate_list':
    """ Returns the trust anchors the agreement says the receiver validates the sender's certificate against.
    """
    out:'certificate_list' = []

    if non_repudiation := receiver_non_repudiation(binding):
        if security_id := non_repudiation.signing_security_details_id:
            out = binding.agreement.get_anchor_certificates(security_id)

    return out

# ################################################################################################################################

def verify_message_signature(
    binding:'Binding',
    local_keys:'LocalKeys',
    envelope:'any_',
    signature:'any_',
    payloads:'payload_list',
    ) -> 'VerifiedSignature | None':
    """ Verifies the signature of a message exchanged under a binding and establishes trust in its certificate.
    Returns None for an unsigned message the binding does not require to be signed.
    """

    # Our response to produce
    out = None

    if signature is None:
        if is_signature_required(binding):
            raise EbMS2SecurityException('The message is not signed and the agreement requires a signature')

    else:

        expected_certificate = _expected_certificate(binding)
        agreement_anchors = _agreement_anchors(binding)

        out = verify_envelope(envelope, signature, payloads, expected_certificate)

        # The chain is to lead to a trust anchor, or the certificate is to be the one the agreement names ..
        keystore = verification_keystore(local_keys, agreement_anchors, expected_certificate)

        try:
            validate_certificate_chain(out.chain, keystore)
        except XMLSecurityException as e:
            raise EbMS2SecurityException(f'The signer\'s certificate is not trusted -> {e}')

        # .. and with trust anchors, a certificate the agreement names is still the only one accepted.
        if expected_certificate:
            if out.certificate != expected_certificate:
                raise EbMS2SecurityException('The signer\'s certificate is not the one the agreement names')

    return out

# ################################################################################################################################
# ################################################################################################################################
