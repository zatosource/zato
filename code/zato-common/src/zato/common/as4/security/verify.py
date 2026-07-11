# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from dataclasses import dataclass

# cryptography
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Zato
from zato.common.as4.common import AS4SecurityException, EbMSError, NS
from zato.common.as4.security.encrypt import HKDF_Info
from zato.common.typing_ import optional
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
    Certificate = Certificate

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
certificatenone = optional['Certificate']

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
    signer_certificate: 'certificatenone' = None
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
    # Our response to produce
    out = VerifyResult()
    out.signer_chain = []
    out.signed_references = []

    header_name = qname(NS.SOAP, 'Header')
    security_name = qname(NS.WSSE, 'Security')
    signature_name = qname(NS.DS, 'Signature')

    header = envelope.find(header_name)
    security = header.find(security_name)

    if security is None:
        raise AS4SecurityException(EbMSError.Policy_Noncompliance, 'Message has no wsse:Security header')

    signature = security.find(signature_name)

    if signature is None:
        raise AS4SecurityException(EbMSError.Policy_Noncompliance, 'Message is not signed')

    # Any failure of the shared primitives surfaces as EBMS:0101, except an algorithm
    # we do not support, which is a policy matter and surfaces as EBMS:0103.
    try:

        # First recover who signed this and decide whether we trust them ..
        chain = extract_signer_chain(signature, security)
        validate_certificate_chain(chain, keystore)

        # .. then check that nothing signed was tampered with ..
        signed_info_name = qname(NS.DS, 'SignedInfo')
        reference_name = qname(NS.DS, 'Reference')

        signed_info = signature.find(signed_info_name)
        references = signed_info.findall(reference_name)

        for reference in references:
            verify_one_reference(reference, envelope, parts)
            reference_copy = deepcopy(reference)
            out.signed_references.append(reference_copy)

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
    header_name = qname(NS.SOAP, 'Header')
    security_name = qname(NS.WSSE, 'Security')
    encrypted_key_name = qname(NS.XENC, 'EncryptedKey')

    header = envelope.find(header_name)
    security = header.find(security_name)

    if security is None:
        return

    encrypted_key = security.find(encrypted_key_name)

    if encrypted_key is None:
        return

    # Whatever goes wrong with key recovery is a decryption failure - EBMS:0102.
    try:
        content_key = recover_content_key(encrypted_key, keystore, HKDF_Info)
    except XMLSecurityException as e:
        raise AS4SecurityException(EbMSError.Failed_Decryption, e.args[0])

    encrypted_data_name = qname(NS.XENC, 'EncryptedData')
    cipher_data_name = qname(NS.XENC, 'CipherData')
    cipher_reference_name = qname(NS.XENC, 'CipherReference')

    # The same content key decrypts every attachment of the message.
    cipher = AESGCM(content_key)

    encrypted_data_list = security.findall(encrypted_data_name)

    # Each EncryptedData names the attachment its cipher bytes live in.
    for encrypted_data in encrypted_data_list:
        cipher_data = encrypted_data.find(cipher_data_name)
        cipher_reference = cipher_data.find(cipher_reference_name)

        # The URI can be genuinely absent from a malformed incoming message.
        uri = cipher_reference.get('URI')
        if uri is None:
            uri = ''

        content_id = uri[4:]

        part = find_part(parts, content_id)

        if part is None:
            raise AS4SecurityException(EbMSError.Failed_Decryption, f'Encrypted part `{content_id}` is missing')

        # Per XML Encryption 1.1 the GCM nonce is prefixed to the ciphertext.
        nonce = part.data[:_gcm_nonce_size_bytes]
        ciphertext = part.data[_gcm_nonce_size_bytes:]

        # A tampered or wrongly keyed ciphertext fails its authentication tag check.
        try:
            part.data = cipher.decrypt(nonce, ciphertext, None)
        except InvalidTag:
            raise AS4SecurityException(EbMSError.Failed_Decryption, f'Could not decrypt part `{content_id}`')

# ################################################################################################################################
# ################################################################################################################################
