# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone
from io import BytesIO
from uuid import uuid4

# cryptography
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.padding import MGF1, OAEP, PKCS1v15
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.keywrap import aes_key_unwrap
from cryptography.hazmat.primitives.serialization import Encoding, load_der_public_key

# lxml
from lxml import etree

# Zato
from zato.common.typing_ import cast_
from zato.common.util.xml_.constants import Algorithm, NS, TokenType, Transform
from zato.common.util.xml_.core import qname, XMLSecurityException, XMLSecurityUnsupportedAlgorithm
from zato.common.util.xml_.keystore import certificate_list
from zato.common.util.xml_.mime_ import part_list
from zato.common.util.xml_.token import build_pkipath, parse_pkipath, parse_x509v3
from zato.common.util.xml_.xmlsec import canonicalize_exclusive, decode_base64, digest_bytes, digest_element, encode_base64, \
    find_by_wsu_id

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
    from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
    from zato.common.typing_ import any_, bytesnone
    from zato.common.util.xml_.keystore import Keystore
    any_ = any_
    bytesnone = bytesnone
    Ed25519PrivateKey = Ed25519PrivateKey
    Ed25519PublicKey = Ed25519PublicKey
    RSAPrivateKey = RSAPrivateKey
    RSAPublicKey = RSAPublicKey
    X25519PrivateKey = X25519PrivateKey
    X25519PublicKey = X25519PublicKey

# ################################################################################################################################
# ################################################################################################################################

_wsu_id = f'{{{NS.WSU}}}Id'

# AES key sizes used by the key derivation and recovery helpers.
_content_key_size_bytes = 16

# ################################################################################################################################
# ################################################################################################################################

def add_binary_security_token(security:'any_', keystore:'Keystore', token_type:'str') -> 'str':
    """ Adds the BinarySecurityToken carrying our signing certificate (or the whole chain
    for PKIPath) and returns its wsu:Id for the signature to reference.
    """
    token_id = f'X509-{uuid4().hex}'

    # A PKIPath token carries the entire chain, the X509v3 one just the leaf certificate.
    if token_type == TokenType.PKIPath:
        token_bytes = build_pkipath(keystore.signing_certificate_chain)
    else:
        token_bytes = keystore.signing_certificate.public_bytes(Encoding.DER)

    token = etree.SubElement(security, qname(NS.WSSE, 'BinarySecurityToken'))
    token.set('EncodingType', TokenType.Base64Binary)
    token.set('ValueType', token_type)
    token.set(_wsu_id, token_id)
    token.text = encode_base64(token_bytes)

    out = token_id
    return out

# ################################################################################################################################

def add_element_reference(signed_info:'any_', root:'any_', wsu_id:'str') -> 'None':
    """ Adds a ds:Reference over an element identified by its wsu:Id -
    the element is canonicalized exclusively and hashed with SHA-256.
    """
    element = find_by_wsu_id(root, wsu_id)

    reference = etree.SubElement(signed_info, qname(NS.DS, 'Reference'))
    reference.set('URI', f'#{wsu_id}')

    transforms = etree.SubElement(reference, qname(NS.DS, 'Transforms'))
    transform = etree.SubElement(transforms, qname(NS.DS, 'Transform'))
    transform.set('Algorithm', Algorithm.C14N_Exclusive)

    digest_method = etree.SubElement(reference, qname(NS.DS, 'DigestMethod'))
    digest_method.set('Algorithm', Algorithm.SHA256)

    digest_value = etree.SubElement(reference, qname(NS.DS, 'DigestValue'))
    digest_value.text = digest_element(element)

# ################################################################################################################################

def add_attachment_reference(signed_info:'any_', content_id:'str', data:'bytes') -> 'None':
    """ Adds a ds:Reference over a MIME attachment using the SwA content transform -
    for binary content the transform is simply a SHA-256 hash over the raw part bytes.
    """
    reference = etree.SubElement(signed_info, qname(NS.DS, 'Reference'))
    reference.set('URI', f'cid:{content_id}')

    transforms = etree.SubElement(reference, qname(NS.DS, 'Transforms'))
    transform = etree.SubElement(transforms, qname(NS.DS, 'Transform'))
    transform.set('Algorithm', Transform.Attachment_Content)

    digest_method = etree.SubElement(reference, qname(NS.DS, 'DigestMethod'))
    digest_method.set('Algorithm', Algorithm.SHA256)

    digest_value = etree.SubElement(reference, qname(NS.DS, 'DigestValue'))
    digest_value.text = digest_bytes(data)

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

def add_key_info_token_reference(signature:'any_', token_id:'str', token_type:'str') -> 'None':
    """ Appends the ds:KeyInfo that points a signature back at its BinarySecurityToken,
    so verifiers know which certificate signed the message.
    """
    key_info = etree.SubElement(signature, qname(NS.DS, 'KeyInfo'))
    token_reference = etree.SubElement(key_info, qname(NS.WSSE, 'SecurityTokenReference'))
    reference = etree.SubElement(token_reference, qname(NS.WSSE, 'Reference'))
    reference.set('URI', f'#{token_id}')
    reference.set('ValueType', token_type)

# ################################################################################################################################
# ################################################################################################################################

def find_by_any_id(root:'any_', element_id:'str') -> 'any_':
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

def canonicalize_for_reference(element:'any_', transform:'any_') -> 'bytes':
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

def find_part(parts:'part_list', content_id:'str') -> 'any_':
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

def verify_one_reference(reference:'any_', envelope:'any_', parts:'part_list') -> 'None':
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
        part = find_part(parts, content_id)

        if part is None:
            raise XMLSecurityException(f'Signed part `{content_id}` is missing')

        actual_digest = digest_bytes(part.data)

    # .. an element reference canonicalizes the element and hashes that.
    else:
        element_id = uri[1:]
        element = find_by_any_id(envelope, element_id)

        if element is None:
            raise XMLSecurityException(f'Signed element `{element_id}` is missing')

        # The enveloped-signature transform means the digest was computed
        # with the ds:Signature element itself removed from the picture.
        if _has_enveloped_transform(transforms):
            element = _without_signature(element)

        canonical = canonicalize_for_reference(element, transform)
        actual_digest = digest_bytes(canonical)

    if actual_digest != expected_digest:
        raise XMLSecurityException(f'Digest mismatch for reference `{uri}`')

# ################################################################################################################################

def _has_enveloped_transform(transforms:'any_') -> 'bool':
    """ Returns True if a ds:Transforms element carries the enveloped-signature transform.
    """
    if transforms is None:
        return False

    for transform in transforms.findall(qname(NS.DS, 'Transform')):
        if transform.get('Algorithm') == Transform.Enveloped:
            return True

    return False

# ################################################################################################################################

def _without_signature(element:'any_') -> 'any_':
    """ Returns a copy of an element with its immediate ds:Signature child removed,
    which is how the enveloped-signature transform is applied.
    """
    # Serializing and reparsing gives a copy that is safe to prune.
    out = etree.fromstring(etree.tostring(element))

    signature = out.find(qname(NS.DS, 'Signature'))
    if signature is not None:
        out.remove(signature)

    return out

# ################################################################################################################################

def extract_signer_chain(signature:'any_', security:'any_') -> 'certificate_list':
    """ Resolves the signature's key info to the certificate chain carried
    in the referenced BinarySecurityToken, leaf certificate first.
    """
    key_info = signature.find(qname(NS.DS, 'KeyInfo'))
    token_reference = key_info.find(qname(NS.WSSE, 'SecurityTokenReference'))

    if token_reference is None:
        raise XMLSecurityException('Signature has no SecurityTokenReference')

    reference = token_reference.find(qname(NS.WSSE, 'Reference'))

    if reference is None:
        raise XMLSecurityException('SecurityTokenReference has no Reference')

    token_id = (reference.get('URI') or '')[1:]
    token = find_by_wsu_id(security, token_id)

    if token is None:
        raise XMLSecurityException(f'BinarySecurityToken `{token_id}` is missing')

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

def validate_certificate_chain(chain:'certificate_list', keystore:'Keystore') -> 'None':
    """ Establishes trust in the signer's certificate. With trust anchors configured,
    the chain must lead from the leaf to one of them with valid signatures and periods.
    Without anchors, the leaf must equal the pinned peer certificate, when one is pinned.
    """
    # Pinned-certificate mode - the exact certificate must have been configured beforehand.
    if not keystore.trust_anchors:
        if pinned := keystore.peer_signing_certificate:
            leaf = chain[0]
            if leaf != pinned:
                raise XMLSecurityException('Signer certificate does not match the pinned one')
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
            raise XMLSecurityException(f'Certificate `{current.subject}` is not yet valid')

        if now > current.not_valid_after_utc:
            raise XMLSecurityException(f'Certificate `{current.subject}` has expired')

        issuer_name = current.issuer.rfc4514_string()

        # The current certificate chains directly to a trust anchor - verify and we are done.
        if anchor := anchors_by_subject.get(issuer_name):
            current.verify_directly_issued_by(anchor)
            break

        # Otherwise the next chain element must be the issuer.
        if not remaining:
            raise XMLSecurityException(f'No trust anchor found for issuer `{issuer_name}`')

        issuer = remaining[0]
        remaining = remaining[1:]
        current.verify_directly_issued_by(issuer)
        current = issuer

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
            raise XMLSecurityUnsupportedAlgorithm(f'Unsupported signature algorithm `{algorithm}`')
    except InvalidSignature:
        raise XMLSecurityException('Signature value does not verify')

# ################################################################################################################################
# ################################################################################################################################

def derive_key_encryption_key(shared_secret:'bytes', info:'bytes') -> 'bytes':
    """ Derives an AES key-wrapping key from an X25519 shared secret with HKDF-SHA256.
    """
    hkdf = HKDF(algorithm=SHA256(), length=_content_key_size_bytes, salt=None, info=info)

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

        out = rsa_key.decrypt(wrapped_key, oaep_padding)
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
