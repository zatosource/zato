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
from zato.common.as4.common import AS4ProtocolException, AS4SecurityException, EbMSError, NS
from zato.common.as4.ebms import find_body, find_messaging
from zato.common.as4.mime_ import content_id_from_reference
from zato.common.as4.security.encrypt import HKDF_Info
from zato.common.typing_ import cast_
from zato.common.util.xml_.core import qname, XMLSecurityException, XMLSecurityUnsupportedAlgorithm
from zato.common.util.xml_.keystore import certificate_list
from zato.common.util.xml_.mime_ import build_part_index, part_list
from zato.common.util.xml_.keys import recover_content_key
from zato.common.util.xml_.references import build_id_index, verify_one_reference
from zato.common.util.xml_.signature import verify_signature_value
from zato.common.util.xml_.tokens import extract_signer_chain
from zato.common.util.xml_.trust import validate_certificate_chain

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.x509 import Certificate
    from zato.common.typing_ import any_, anylist, strset
    from zato.common.util.xml_.keystore import Keystore
    any_ = any_
    anylist = anylist
    Certificate = Certificate
    strset = strset

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases

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

def _is_one_of(nodes:'anylist', node:'any_') -> 'bool':
    """ Returns True if the node given is one of the nodes in the list. Compared by identity, so two
    elements that serialize alike are still two elements.
    """
    for item in nodes:
        if item is node:
            out = True
            break
    else:
        out = False

    return out

# ################################################################################################################################

def _require_coverage(
    envelope:'any_',
    parts:'part_list',
    verified_elements:'anylist',
    verified_content_ids:'strset',
    ) -> 'None':
    """ Requires the signature to cover the eb:Messaging header, the SOAP Body and every MIME part,
    which is what the AS4 profile prescribes and what sign_envelope produces.

    The two elements are looked up through the same functions that the rest of the pipeline parses
    them with, and compared by identity against the nodes the references resolved to.
    """
    messaging = find_messaging(envelope)

    if not _is_one_of(verified_elements, messaging):
        raise AS4SecurityException(EbMSError.Policy_Noncompliance, 'The signature does not cover eb:Messaging')

    body = find_body(envelope)

    if not _is_one_of(verified_elements, body):
        raise AS4SecurityException(EbMSError.Policy_Noncompliance, 'The signature does not cover the SOAP Body')

    for part in parts:
        if part.content_id not in verified_content_ids:
            raise AS4SecurityException(
                EbMSError.Policy_Noncompliance, f'The signature does not cover part `{part.content_id}`')

# ################################################################################################################################
# ################################################################################################################################

def verify_envelope(envelope:'any_', parts:'part_list', keystore:'Keystore') -> 'VerifyResult':
    """ Verifies the WS-Security signature of an incoming message: every reference digest, what the
    references cover, the signature value itself and the trust in the signing certificate.
    """
    # Our response to produce
    out = VerifyResult()
    out.signer_chain = []
    out.signed_references = []

    header_name = qname(NS.SOAP, 'Header')
    security_name = qname(NS.WSSE, 'Security')
    signature_name = qname(NS.DS, 'Signature')

    header = envelope.find(header_name)

    # An envelope with no header at all carries no security either.
    if header is None:
        raise AS4SecurityException(EbMSError.Invalid_Header, 'Message has no SOAP Header')

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

        # The index is built once for the whole document rather than once per reference, and a
        # duplicated id is an error in it rather than a choice of which element to verify.
        id_index = build_id_index(envelope)

        # The MIME parts are indexed once for the same reason.
        part_index = build_part_index(parts)

        # What the references were found to cover, kept so that coverage can be required below.
        verified_elements:'anylist' = []
        verified_content_ids:'strset' = set()

        for reference in references:
            covered_element = verify_one_reference(reference, envelope, part_index, id_index)

            reference_copy = deepcopy(reference)
            out.signed_references.append(reference_copy)

            # verify_one_reference returns the covered element for an element reference and None for
            # an attachment reference, which is the only kind whose URI carries a cid: prefix.
            if covered_element is None:
                uri = reference.get('URI')
                content_id = content_id_from_reference(cast_('str', uri))
                verified_content_ids.add(content_id)
            else:
                verified_elements.append(covered_element)

        # .. that it covers everything the profile requires it to cover ..
        _require_coverage(envelope, parts, verified_elements, verified_content_ids)

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

def decrypt_parts(envelope:'any_', parts:'part_list', keystore:'Keystore') -> 'strset':
    """ Decrypts the attachments of an incoming message in place. Messages without an
    xenc:EncryptedKey are passed through untouched. Returns the content ids that were decrypted,
    which is what tells a caller whether the message met its P-Mode's encryption policy.
    """

    # Our response to produce
    out:'strset' = set()

    header_name = qname(NS.SOAP, 'Header')
    security_name = qname(NS.WSSE, 'Security')
    encrypted_key_name = qname(NS.XENC, 'EncryptedKey')

    header = envelope.find(header_name)

    # Nothing is encrypted in an envelope that has no header to say so.
    if header is None:
        return out

    security = header.find(security_name)

    if security is None:
        return out

    encrypted_key = security.find(encrypted_key_name)

    if encrypted_key is None:
        return out

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

    part_index = build_part_index(parts)
    encrypted_data_list = security.findall(encrypted_data_name)

    # Each EncryptedData names the attachment its cipher bytes live in.
    for encrypted_data in encrypted_data_list:
        cipher_data = encrypted_data.find(cipher_data_name)
        cipher_reference = cipher_data.find(cipher_reference_name)

        # The URI can be genuinely absent from a malformed incoming message.
        uri = cipher_reference.get('URI')
        if uri is None:
            uri = ''

        try:
            content_id = content_id_from_reference(uri)
        except AS4ProtocolException as e:
            raise AS4SecurityException(EbMSError.Failed_Decryption, e.detail)

        part = part_index.get(content_id)

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

        out.add(content_id)

    return out

# ################################################################################################################################
# ################################################################################################################################
