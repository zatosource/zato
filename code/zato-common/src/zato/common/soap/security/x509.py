# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone
from os import urandom
from uuid import uuid4

# cryptography
from cryptography.hazmat.primitives.asymmetric.padding import MGF1, OAEP
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import Encoding

# lxml
from lxml import etree

# Zato
from zato.common.soap.common import NS, SOAPSecurityException
from zato.common.soap.envelope import get_body, get_security_header
from zato.common.typing_ import cast_
from zato.common.util.xml_.constants import Algorithm, TokenType
from zato.common.util.xml_.core import qname, to_timestamp, XMLSecurityException
from zato.common.util.xml_.wssec import add_binary_security_token, add_element_reference, add_key_info_token_reference, \
    compute_signature_value, extract_signer_chain, recover_content_key, validate_certificate_chain, verify_one_reference, \
    verify_signature_value
from zato.common.util.xml_.xmlsec import decode_base64, encode_base64

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
    from cryptography.x509 import Certificate
    from zato.common.typing_ import any_
    from zato.common.util.xml_.keystore import Keystore
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_wsu_id = f'{{{NS.WSU}}}Id'

# How long a wsu:Timestamp stays valid.
Timestamp_TTL_Seconds = 300

# AES-128-GCM parameters for body encryption.
_content_key_size_bytes = 16
_gcm_nonce_size_bytes   = 12

# The XML Encryption type of encrypted element content.
_xenc_content_type = 'http://www.w3.org/2001/04/xmlenc#Content'

_signature_nsmap = {
    'ds': NS.DS,
}

_xenc_nsmap = {
    'xenc':   NS.XENC,
    'xenc11': NS.XENC11,
    'ds':     NS.DS,
}

# ################################################################################################################################
# ################################################################################################################################

def _utc_pair(ttl_seconds:'int') -> 'tuple[str, str]':
    """ Returns the created and expires timestamps of a wsu:Timestamp, ttl seconds apart.
    """
    now = datetime.now(timezone.utc)
    expires = now + timedelta(seconds=ttl_seconds)

    out = (to_timestamp(now), to_timestamp(expires))
    return out

# ################################################################################################################################

def add_timestamp(envelope:'any_', ttl_seconds:'int'=Timestamp_TTL_Seconds) -> 'str':
    """ Adds a wsu:Timestamp to the security header and returns its wsu:Id
    so signatures can cover it.
    """
    security = get_security_header(envelope)
    timestamp_id = f'TS-{uuid4().hex}'

    created_text, expires_text = _utc_pair(ttl_seconds)

    timestamp = etree.SubElement(security, qname(NS.WSU, 'Timestamp'))
    timestamp.set(_wsu_id, timestamp_id)

    created = etree.SubElement(timestamp, qname(NS.WSU, 'Created'))
    created.text = created_text

    expires = etree.SubElement(timestamp, qname(NS.WSU, 'Expires'))
    expires.text = expires_text

    out = timestamp_id
    return out

# ################################################################################################################################

def sign(
    envelope:'any_',
    keystore:'Keystore',
    signature_algorithm:'str'=Algorithm.RSA_SHA256,
    token_type:'str'=TokenType.X509v3,
    ) -> 'any_':
    """ Signs an envelope in place following the WS-Security X.509 token profile -
    a wsu:Timestamp and the SOAP body are covered by a ds:Signature whose certificate
    travels in a BinarySecurityToken. Returns the ds:Signature element.
    """
    # The body needs a wsu:Id for its signature reference.
    body = get_body(envelope)
    body_id = body.get(_wsu_id)

    if body_id is None:
        body_id = f'Body-{uuid4().hex}'
        body.set(_wsu_id, body_id)

    timestamp_id = add_timestamp(envelope)

    security = get_security_header(envelope)
    token_id = add_binary_security_token(security, keystore, token_type)

    signature = etree.SubElement(security, qname(NS.DS, 'Signature'), nsmap=_signature_nsmap)
    signature.set('Id', f'SIG-{uuid4().hex}')

    # The signed info lists everything the signature covers ..
    signed_info = etree.SubElement(signature, qname(NS.DS, 'SignedInfo'))

    canonicalization_method = etree.SubElement(signed_info, qname(NS.DS, 'CanonicalizationMethod'))
    canonicalization_method.set('Algorithm', Algorithm.C14N_Exclusive)

    signature_method = etree.SubElement(signed_info, qname(NS.DS, 'SignatureMethod'))
    signature_method.set('Algorithm', signature_algorithm)

    # .. which is the timestamp and the body.
    add_element_reference(signed_info, envelope, timestamp_id)
    add_element_reference(signed_info, envelope, body_id)

    # Now that all the references are in place, the signed info itself can be signed.
    signature_bytes = compute_signature_value(signed_info, keystore, signature_algorithm)

    signature_value = etree.SubElement(signature, qname(NS.DS, 'SignatureValue'))
    signature_value.text = encode_base64(signature_bytes)

    add_key_info_token_reference(signature, token_id, token_type)

    return signature

# ################################################################################################################################

def verify(envelope:'any_', keystore:'Keystore') -> 'any_':
    """ Verifies the WS-Security signature of an incoming envelope -
    every reference digest, the signature value and the trust in the signer.
    Returns the signer's certificate.
    """
    security = get_security_header(envelope)
    signature = security.find(qname(NS.DS, 'Signature'))

    if signature is None:
        raise SOAPSecurityException('Message is not signed')

    # Any failure of the shared primitives surfaces as one SOAP security exception.
    try:

        # First recover who signed this and decide whether we trust them ..
        chain = extract_signer_chain(signature, security)
        validate_certificate_chain(chain, keystore)

        # .. then check that nothing signed was tampered with ..
        signed_info = signature.find(qname(NS.DS, 'SignedInfo'))

        for reference in signed_info.findall(qname(NS.DS, 'Reference')):
            verify_one_reference(reference, envelope, [])

        # .. and finally that the signature value itself is genuine.
        verify_signature_value(signature, chain)

    except XMLSecurityException as e:
        raise SOAPSecurityException(e.args[0])

    out = chain[0]
    return out

# ################################################################################################################################
# ################################################################################################################################

def encrypt_body(envelope:'any_', keystore:'Keystore') -> 'None':
    """ Encrypts the contents of the SOAP body in place with a fresh AES-128-GCM key,
    wrapping that key for the recipient's RSA certificate with RSA-OAEP.
    """
    body = get_body(envelope)

    # The plaintext is the serialized content of the body - all its children.
    plaintext = b''
    for child in body:
        plaintext += etree.tostring(child)

    content_key = urandom(_content_key_size_bytes)
    nonce = urandom(_gcm_nonce_size_bytes)

    # Per XML Encryption 1.1 the cipher value is the nonce, the ciphertext and the tag.
    ciphertext = nonce + AESGCM(content_key).encrypt(nonce, plaintext, None)

    # The EncryptedData replaces everything the body held ..
    for child in list(body):
        body.remove(child)

    encrypted_data_id = f'ED-{uuid4().hex}'

    encrypted_data = etree.SubElement(body, qname(NS.XENC, 'EncryptedData'), nsmap=_xenc_nsmap)
    encrypted_data.set('Id', encrypted_data_id)
    encrypted_data.set('Type', _xenc_content_type)

    encryption_method = etree.SubElement(encrypted_data, qname(NS.XENC, 'EncryptionMethod'))
    encryption_method.set('Algorithm', Algorithm.AES128_GCM)

    cipher_data = etree.SubElement(encrypted_data, qname(NS.XENC, 'CipherData'))
    cipher_value = etree.SubElement(cipher_data, qname(NS.XENC, 'CipherValue'))
    cipher_value.text = encode_base64(ciphertext)

    # .. and the wrapped content key goes into the security header.
    security = get_security_header(envelope)

    encrypted_key = etree.Element(qname(NS.XENC, 'EncryptedKey'), nsmap=_xenc_nsmap)
    encrypted_key.set('Id', f'EK-{uuid4().hex}')

    encryption_method = etree.SubElement(encrypted_key, qname(NS.XENC, 'EncryptionMethod'))
    encryption_method.set('Algorithm', Algorithm.RSA_OAEP)

    digest_method = etree.SubElement(encryption_method, qname(NS.DS, 'DigestMethod'))
    digest_method.set('Algorithm', Algorithm.SHA256)

    mgf = etree.SubElement(encryption_method, qname(NS.XENC11, 'MGF'))
    mgf.set('Algorithm', Algorithm.MGF1_SHA256)

    # The recipient's certificate says which key decrypts this.
    certificate = cast_('Certificate', keystore.peer_encryption_certificate)

    key_info = etree.SubElement(encrypted_key, qname(NS.DS, 'KeyInfo'))
    x509_data = etree.SubElement(key_info, qname(NS.DS, 'X509Data'))
    x509_certificate = etree.SubElement(x509_data, qname(NS.DS, 'X509Certificate'))
    x509_certificate.text = encode_base64(certificate.public_bytes(Encoding.DER))

    public_key = cast_('RSAPublicKey', certificate.public_key())
    oaep_padding = OAEP(mgf=MGF1(SHA256()), algorithm=SHA256(), label=None)
    wrapped_key = public_key.encrypt(content_key, oaep_padding)

    cipher_data = etree.SubElement(encrypted_key, qname(NS.XENC, 'CipherData'))
    cipher_value = etree.SubElement(cipher_data, qname(NS.XENC, 'CipherValue'))
    cipher_value.text = encode_base64(wrapped_key)

    reference_list = etree.SubElement(encrypted_key, qname(NS.XENC, 'ReferenceList'))
    data_reference = etree.SubElement(reference_list, qname(NS.XENC, 'DataReference'))
    data_reference.set('URI', f'#{encrypted_data_id}')

    # The key goes first in the security header so receivers process it before anything else.
    security.insert(0, encrypted_key)

# ################################################################################################################################

def decrypt_body(envelope:'any_', keystore:'Keystore') -> 'None':
    """ Decrypts the contents of the SOAP body in place, reversing encrypt_body.
    """
    security = get_security_header(envelope)
    encrypted_key = security.find(qname(NS.XENC, 'EncryptedKey'))

    if encrypted_key is None:
        raise SOAPSecurityException('Message has no EncryptedKey')

    try:
        content_key = recover_content_key(encrypted_key, keystore)
    except XMLSecurityException as e:
        raise SOAPSecurityException(e.args[0])

    body = get_body(envelope)
    encrypted_data = body.find(qname(NS.XENC, 'EncryptedData'))

    if encrypted_data is None:
        raise SOAPSecurityException('Body has no EncryptedData')

    cipher_data = encrypted_data.find(qname(NS.XENC, 'CipherData'))
    cipher_value = cipher_data.find(qname(NS.XENC, 'CipherValue'))
    cipher_bytes = decode_base64(cipher_value.text)

    # Per XML Encryption 1.1 the GCM nonce is prefixed to the ciphertext.
    nonce = cipher_bytes[:_gcm_nonce_size_bytes]
    ciphertext = cipher_bytes[_gcm_nonce_size_bytes:]

    try:
        plaintext = AESGCM(content_key).decrypt(nonce, ciphertext, None)
    except Exception:
        raise SOAPSecurityException('Could not decrypt the body')

    # The decrypted children replace the EncryptedData element.
    body.remove(encrypted_data)

    # The plaintext is a sequence of sibling elements, so it needs a wrapper to parse.
    wrapper = etree.fromstring(b'<wrapper>' + plaintext + b'</wrapper>')

    for child in wrapper:
        body.append(child)

# ################################################################################################################################
# ################################################################################################################################
