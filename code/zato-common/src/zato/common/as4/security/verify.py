# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from io import BytesIO

# cryptography
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.padding import MGF1, OAEP, PKCS1v15
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.keywrap import aes_key_unwrap
from cryptography.hazmat.primitives.serialization import load_der_public_key

# lxml
from lxml import etree

# Zato
from zato.common.as4.common import Algorithm, AS4SecurityException, EbMSError, NS, TokenType
from zato.common.as4.ebms import qname
from zato.common.as4.keystore import certificate_list
from zato.common.as4.mime_ import part_list
from zato.common.as4.security.encrypt import derive_key_encryption_key
from zato.common.as4.security.token import parse_pkipath, parse_x509v3
from zato.common.as4.security.xmlsec import decode_base64, digest_bytes, find_by_wsu_id
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
    from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
    from cryptography.x509 import Certificate
    from zato.common.as4.keystore import Keystore
    from zato.common.typing_ import any_, anylist
    any_ = any_
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

_wsu_id = f'{{{NS.WSU}}}Id'
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

def _find_by_any_id(root:'any_', element_id:'str') -> 'any_':
    """ Returns the element carrying the given id either as wsu:Id or as a plain Id attribute.
    """
    out = find_by_wsu_id(root, element_id)

    if out is None:
        for element in root.iter():
            if element.get('Id') == element_id:
                out = element
                break

    return out

# ################################################################################################################################

def _canonicalize_for_reference(element:'any_', transform:'any_') -> 'bytes':
    """ Canonicalizes an element the way its ds:Transform element prescribes,
    honoring an InclusiveNamespaces PrefixList when one is present.
    """
    inclusive_prefixes = None

    if transform is not None:
        inclusive_namespaces = transform.find(f'{{{Algorithm.C14N_Exclusive}}}InclusiveNamespaces')
        if inclusive_namespaces is not None:
            if prefix_list := inclusive_namespaces.get('PrefixList'):
                inclusive_prefixes = prefix_list.split()

    buffer = BytesIO()
    tree = etree.ElementTree(element)
    tree.write_c14n(buffer, exclusive=True, with_comments=False, inclusive_ns_prefixes=inclusive_prefixes)

    out = buffer.getvalue()
    return out

# ################################################################################################################################

def _find_part(parts:'part_list', content_id:'str') -> 'any_':
    """ Returns the MIME part matching a cid: reference, or None.
    """
    for part in parts:
        if part.content_id == content_id:
            out = part
            break
    else:
        out = None

    return out

# ################################################################################################################################

def _verify_one_reference(reference:'any_', envelope:'any_', parts:'part_list') -> 'None':
    """ Recomputes the digest of one ds:Reference and compares it with the declared value.
    """
    uri = reference.get('URI') or ''

    digest_value_element = reference.find(qname(NS.DS, 'DigestValue'))
    expected_digest = ''.join((digest_value_element.text or '').split())

    transform = None
    transforms = reference.find(qname(NS.DS, 'Transforms'))
    if transforms is not None:
        transform = transforms.find(qname(NS.DS, 'Transform'))

    # An attachment reference hashes the raw bytes of the MIME part ..
    if uri.startswith('cid:'):
        content_id = uri[4:]
        part = _find_part(parts, content_id)

        if part is None:
            raise AS4SecurityException(EbMSError.Failed_Authentication, f'Signed part `{content_id}` is missing')

        actual_digest = digest_bytes(part.data)

    # .. an element reference canonicalizes the element and hashes that.
    else:
        element_id = uri[1:]
        element = _find_by_any_id(envelope, element_id)

        if element is None:
            raise AS4SecurityException(EbMSError.Failed_Authentication, f'Signed element `{element_id}` is missing')

        canonical = _canonicalize_for_reference(element, transform)
        actual_digest = digest_bytes(canonical)

    if actual_digest != expected_digest:
        raise AS4SecurityException(EbMSError.Failed_Authentication, f'Digest mismatch for reference `{uri}`')

# ################################################################################################################################

def _extract_signer_chain(signature:'any_', security:'any_') -> 'certificate_list':
    """ Resolves the signature's key info to the certificate chain carried
    in the referenced BinarySecurityToken, leaf certificate first.
    """
    key_info = signature.find(qname(NS.DS, 'KeyInfo'))
    token_reference = key_info.find(qname(NS.WSSE, 'SecurityTokenReference'))

    if token_reference is None:
        raise AS4SecurityException(EbMSError.Failed_Authentication, 'Signature has no SecurityTokenReference')

    reference = token_reference.find(qname(NS.WSSE, 'Reference'))

    if reference is None:
        raise AS4SecurityException(EbMSError.Failed_Authentication, 'SecurityTokenReference has no Reference')

    token_id = (reference.get('URI') or '')[1:]
    token = find_by_wsu_id(security, token_id)

    if token is None:
        raise AS4SecurityException(EbMSError.Failed_Authentication, f'BinarySecurityToken `{token_id}` is missing')

    token_bytes = decode_base64(token.text or '')
    value_type = token.get('ValueType')

    # A PKIPath token carries the whole chain, an X509v3 one just the leaf.
    if value_type == TokenType.PKIPath:
        out = parse_pkipath(token_bytes)
    else:
        leaf = parse_x509v3(token_bytes)
        out = [leaf]

    return out

# ################################################################################################################################

def _validate_certificate_chain(chain:'certificate_list', keystore:'Keystore') -> 'None':
    """ Establishes trust in the signer's certificate. With trust anchors configured,
    the chain must lead from the leaf to one of them with valid signatures and periods.
    Without anchors, the leaf must equal the pinned peer certificate, when one is pinned.
    """
    # Pinned-certificate mode - the exact certificate must have been configured beforehand.
    if not keystore.trust_anchors:
        if pinned := keystore.peer_signing_certificate:
            leaf = chain[0]
            if leaf != pinned:
                raise AS4SecurityException(EbMSError.Failed_Authentication, 'Signer certificate does not match the pinned one')
        return

    now = datetime.now(timezone.utc)

    # Walk from the leaf upwards - each certificate must be within its validity period
    # and signed either by the next chain element or directly by a trust anchor.
    anchors_by_subject = {}
    for anchor in keystore.trust_anchors:
        anchors_by_subject[anchor.subject.rfc4514_string()] = anchor

    current = chain[0]
    remaining = chain[1:]

    while True:
        if now < current.not_valid_before_utc:
            raise AS4SecurityException(EbMSError.Failed_Authentication, f'Certificate `{current.subject}` is not yet valid')

        if now > current.not_valid_after_utc:
            raise AS4SecurityException(EbMSError.Failed_Authentication, f'Certificate `{current.subject}` has expired')

        issuer_name = current.issuer.rfc4514_string()

        # The current certificate chains directly to a trust anchor - verify and we are done.
        if anchor := anchors_by_subject.get(issuer_name):
            current.verify_directly_issued_by(anchor)
            break

        # Otherwise the next chain element must be the issuer.
        if not remaining:
            raise AS4SecurityException(
                EbMSError.Failed_Authentication, f'No trust anchor found for issuer `{issuer_name}`')

        issuer = remaining[0]
        remaining = remaining[1:]
        current.verify_directly_issued_by(issuer)
        current = issuer

# ################################################################################################################################

def _verify_signature_value(signature:'any_', chain:'certificate_list') -> 'None':
    """ Canonicalizes ds:SignedInfo and checks the signature value against the leaf public key.
    """
    signed_info = signature.find(qname(NS.DS, 'SignedInfo'))

    signature_method = signed_info.find(qname(NS.DS, 'SignatureMethod'))
    algorithm = signature_method.get('Algorithm')

    # The canonicalization of SignedInfo may carry its own PrefixList.
    canonicalization_method = signed_info.find(qname(NS.DS, 'CanonicalizationMethod'))
    canonical = _canonicalize_for_reference(signed_info, canonicalization_method)

    signature_value_element = signature.find(qname(NS.DS, 'SignatureValue'))
    signature_bytes = decode_base64(signature_value_element.text or '')

    leaf = chain[0]
    public_key = leaf.public_key()

    try:
        if algorithm == Algorithm.Ed25519:
            ed25519_key = cast_('Ed25519PublicKey', public_key)
            ed25519_key.verify(signature_bytes, canonical)
        elif algorithm == Algorithm.RSA_SHA256:
            rsa_key = cast_('RSAPublicKey', public_key)
            rsa_key.verify(signature_bytes, canonical, PKCS1v15(), SHA256())
        else:
            raise AS4SecurityException(EbMSError.Policy_Noncompliance, f'Unsupported signature algorithm `{algorithm}`')
    except InvalidSignature:
        raise AS4SecurityException(EbMSError.Failed_Authentication, 'Signature value does not verify')

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

    # First recover who signed this and decide whether we trust them ..
    chain = _extract_signer_chain(signature, security)
    _validate_certificate_chain(chain, keystore)

    # .. then check that nothing signed was tampered with ..
    signed_info = signature.find(qname(NS.DS, 'SignedInfo'))

    for reference in signed_info.findall(qname(NS.DS, 'Reference')):
        _verify_one_reference(reference, envelope, parts)
        out.signed_references.append(deepcopy(reference))

    # .. and finally that the signature value itself is genuine.
    _verify_signature_value(signature, chain)

    out.signer_certificate = chain[0]
    out.signer_chain = chain

    return out

# ################################################################################################################################
# ################################################################################################################################

def _recover_content_key(encrypted_key:'any_', keystore:'Keystore') -> 'bytes':
    """ Recovers the AES content key from an xenc:EncryptedKey, whichever
    of the two suites protected it.
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

        out = rsa_key.decrypt(wrapped_key, oaep_padding)
        return out

    # AES key wrap after X25519 agreement - rebuild the shared secret
    # from the sender's ephemeral public key, derive the wrapping key, unwrap.
    if algorithm == Algorithm.AES128_KeyWrap:
        key_info = encrypted_key.find(qname(NS.DS, 'KeyInfo'))
        agreement_method = key_info.find(qname(NS.XENC, 'AgreementMethod'))
        originator = agreement_method.find(qname(NS.XENC, 'OriginatorKeyInfo'))
        key_value = originator.find(qname(NS.DS, 'KeyValue'))
        der_key_value = key_value.find(qname(NS.XMLDSIG11, 'DEREncodedKeyValue'))

        ephemeral_bytes = decode_base64(der_key_value.text or '')
        ephemeral_public_key = cast_('X25519PublicKey', load_der_public_key(ephemeral_bytes))

        x25519_key = cast_('X25519PrivateKey', keystore.decryption_key)
        shared_secret = x25519_key.exchange(ephemeral_public_key)
        key_encryption_key = derive_key_encryption_key(shared_secret)

        out = aes_key_unwrap(key_encryption_key, wrapped_key)
        return out

    raise AS4SecurityException(EbMSError.Failed_Decryption, f'Unsupported key transport algorithm `{algorithm}`')

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

    content_key = _recover_content_key(encrypted_key, keystore)

    # Each EncryptedData names the attachment its cipher bytes live in.
    for encrypted_data in security.findall(qname(NS.XENC, 'EncryptedData')):
        cipher_data = encrypted_data.find(qname(NS.XENC, 'CipherData'))
        cipher_reference = cipher_data.find(qname(NS.XENC, 'CipherReference'))
        uri = cipher_reference.get('URI') or ''
        content_id = uri[4:]

        part = _find_part(parts, content_id)

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
