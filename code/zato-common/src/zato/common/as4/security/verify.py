# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from dataclasses import dataclass

# cryptography
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Zato
from zato.common.as4.common import AS4SecurityException, EbMSError, NS
from zato.common.as4.security.encrypt import HKDF_Info
from zato.common.util.xml_.core import qname, XMLSecurityException, XMLSecurityUnsupportedAlgorithm
from zato.common.util.xml_.keystore import certificate_list
from zato.common.util.xml_.mime_ import part_list
from zato.common.util.xml_.wssec import extract_signer_chain, find_part, recover_content_key, validate_certificate_chain, \
    verify_one_reference, verify_signature_value

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.x509 import Certificate
    from zato.common.typing_ import any_, anylist
    from zato.common.util.xml_.keystore import Keystore
    any_ = any_
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

_gcm_nonce_size_bytes = 12

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class VerifyResult:
    """ What signature verification of an incoming message established.
    """
    # The certificate the message was signed with, plus any further chain certificates
    # if they travelled inside the message as a PKIPath.
    signer_certificate: 'Certificate | None' = None
    signer_chain: 'certificate_list'

    # Deep copies of the verified ds:Reference elements - receipts echo these back
    # as their non-repudiation information.
    signed_references: 'anylist'

# ################################################################################################################################
# ################################################################################################################################

def verify_envelope(envelope:'any_', parts:'part_list', keystore:'Keystore') -> 'VerifyResult':
    """ Verifies the WS-Security signature of an incoming message: every reference digest,
    the signature value itself and the trust in the signing certificate.
    """
    out = VerifyResult()
    out.signer_chain = []
    out.signed_references = []

    header = envelope.find(qname(NS.SOAP, 'Header'))
    security = header.find(qname(NS.WSSE, 'Security'))

    if security is None:
        raise AS4SecurityException(EbMSError.Policy_Noncompliance, 'Message has no wsse:Security header')

    signature = security.find(qname(NS.DS, 'Signature'))

    if signature is None:
        raise AS4SecurityException(EbMSError.Policy_Noncompliance, 'Message is not signed')

    # Any failure of the shared primitives surfaces as EBMS:0101, except an algorithm
    # we do not support, which is a policy matter and surfaces as EBMS:0103.
    try:

        # First recover who signed this and decide whether we trust them ..
        chain = extract_signer_chain(signature, security)
        validate_certificate_chain(chain, keystore)

        # .. then check that nothing signed was tampered with ..
        signed_info = signature.find(qname(NS.DS, 'SignedInfo'))

        for reference in signed_info.findall(qname(NS.DS, 'Reference')):
            verify_one_reference(reference, envelope, parts)
            out.signed_references.append(deepcopy(reference))

        # .. and finally that the signature value itself is genuine.
        verify_signature_value(signature, chain)

    except XMLSecurityUnsupportedAlgorithm as e:
        raise AS4SecurityException(EbMSError.Policy_Noncompliance, e.args[0])

    except XMLSecurityException as e:
        raise AS4SecurityException(EbMSError.Failed_Authentication, e.args[0])

    out.signer_certificate = chain[0]
    out.signer_chain = chain

    return out

# ################################################################################################################################
# ################################################################################################################################

def decrypt_parts(envelope:'any_', parts:'part_list', keystore:'Keystore') -> 'None':
    """ Decrypts the attachments of an incoming message in place. Messages
    without an xenc:EncryptedKey are passed through untouched.
    """
    header = envelope.find(qname(NS.SOAP, 'Header'))
    security = header.find(qname(NS.WSSE, 'Security'))

    if security is None:
        return

    encrypted_key = security.find(qname(NS.XENC, 'EncryptedKey'))

    if encrypted_key is None:
        return

    # Whatever goes wrong with key recovery is a decryption failure - EBMS:0102.
    try:
        content_key = recover_content_key(encrypted_key, keystore, HKDF_Info)
    except XMLSecurityException as e:
        raise AS4SecurityException(EbMSError.Failed_Decryption, e.args[0])

    # Each EncryptedData names the attachment its cipher bytes live in.
    for encrypted_data in security.findall(qname(NS.XENC, 'EncryptedData')):
        cipher_data = encrypted_data.find(qname(NS.XENC, 'CipherData'))
        cipher_reference = cipher_data.find(qname(NS.XENC, 'CipherReference'))
        uri = cipher_reference.get('URI') or ''
        content_id = uri[4:]

        part = find_part(parts, content_id)

        if part is None:
            raise AS4SecurityException(EbMSError.Failed_Decryption, f'Encrypted part `{content_id}` is missing')

        # Per XML Encryption 1.1 the GCM nonce is prefixed to the ciphertext.
        nonce = part.data[:_gcm_nonce_size_bytes]
        ciphertext = part.data[_gcm_nonce_size_bytes:]

        try:
            part.data = AESGCM(content_key).decrypt(nonce, ciphertext, None)
        except Exception:
            raise AS4SecurityException(EbMSError.Failed_Decryption, f'Could not decrypt part `{content_id}`')

# ################################################################################################################################
# ################################################################################################################################
