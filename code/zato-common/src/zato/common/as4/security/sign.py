# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from uuid import uuid4

# cryptography
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import Encoding

# lxml
from lxml import etree

# Zato
from zato.common.as4.common import Algorithm, NS, TokenType, Transform
from zato.common.as4.ebms import Body_Element_ID, Messaging_Element_ID, qname
from zato.common.as4.mime_ import part_list
from zato.common.as4.security.token import build_pkipath
from zato.common.as4.security.xmlsec import canonicalize_exclusive, digest_bytes, digest_element, encode_base64, \
    find_by_wsu_id
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
    from zato.common.as4.keystore import Keystore
    from zato.common.as4.pmode import SecurityConfig
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_wsu_id = f'{{{NS.WSU}}}Id'

_security_nsmap = {
    'wsse':   NS.WSSE,
    'wsse11': NS.WSSE11,
    'wsu':    NS.WSU,
}

_signature_nsmap = {
    'ds': NS.DS,
}

# ################################################################################################################################
# ################################################################################################################################

def get_security_header(envelope:'any_') -> 'any_':
    """ Returns the wsse:Security header of an envelope, creating it if needed.
    """
    header = envelope.find(qname(NS.SOAP, 'Header'))
    security = header.find(qname(NS.WSSE, 'Security'))

    if security is None:
        security = etree.SubElement(header, qname(NS.WSSE, 'Security'), nsmap=_security_nsmap)
        security.set(qname(NS.SOAP, 'mustUnderstand'), 'true')

    return security

# ################################################################################################################################

def _add_binary_security_token(security:'any_', keystore:'Keystore', token_type:'str') -> 'str':
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

def _add_element_reference(signed_info:'any_', root:'any_', wsu_id:'str') -> 'None':
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

def _add_attachment_reference(signed_info:'any_', content_id:'str', data:'bytes') -> 'None':
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

def _compute_signature_value(signed_info:'any_', keystore:'Keystore', signature_algorithm:'str') -> 'bytes':
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

def sign_envelope(
    envelope:'any_',
    parts:'part_list',
    keystore:'Keystore',
    config:'SecurityConfig',
    ) -> 'any_':
    """ Signs an AS4 envelope in place: covers the eb:Messaging header, the SOAP body
    and every MIME attachment, and appends the resulting ds:Signature with its
    BinarySecurityToken to the wsse:Security header. Returns the ds:Signature element.

    This must run after compression and before encryption - the signature covers
    the compressed plaintext, which is also the order in which receivers reverse it.
    """
    security = get_security_header(envelope)
    token_id = _add_binary_security_token(security, keystore, config.token_type)

    signature = etree.SubElement(security, qname(NS.DS, 'Signature'), nsmap=_signature_nsmap)
    signature.set('Id', f'SIG-{uuid4().hex}')

    # The signed info lists everything the signature covers ..
    signed_info = etree.SubElement(signature, qname(NS.DS, 'SignedInfo'))

    canonicalization_method = etree.SubElement(signed_info, qname(NS.DS, 'CanonicalizationMethod'))
    canonicalization_method.set('Algorithm', Algorithm.C14N_Exclusive)

    signature_method = etree.SubElement(signed_info, qname(NS.DS, 'SignatureMethod'))
    signature_method.set('Algorithm', config.signature_algorithm)

    # .. the ebMS header and the (empty) SOAP body ..
    _add_element_reference(signed_info, envelope, Messaging_Element_ID)
    _add_element_reference(signed_info, envelope, Body_Element_ID)

    # .. and each attachment through the SwA content transform.
    for part in parts:
        _add_attachment_reference(signed_info, part.content_id, part.data)

    # Now that all the references are in place, the signed info itself can be signed.
    signature_bytes = _compute_signature_value(signed_info, keystore, config.signature_algorithm)

    signature_value = etree.SubElement(signature, qname(NS.DS, 'SignatureValue'))
    signature_value.text = encode_base64(signature_bytes)

    # The key info points back at the token so verifiers know which certificate signed this.
    key_info = etree.SubElement(signature, qname(NS.DS, 'KeyInfo'))
    token_reference = etree.SubElement(key_info, qname(NS.WSSE, 'SecurityTokenReference'))
    reference = etree.SubElement(token_reference, qname(NS.WSSE, 'Reference'))
    reference.set('URI', f'#{token_id}')
    reference.set('ValueType', config.token_type)

    return signature

# ################################################################################################################################
# ################################################################################################################################
