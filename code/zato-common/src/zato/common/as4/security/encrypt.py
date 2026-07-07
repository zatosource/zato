# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from os import urandom
from uuid import uuid4

# cryptography
from cryptography.hazmat.primitives.asymmetric.padding import MGF1, OAEP
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.keywrap import aes_key_wrap
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

# lxml
from lxml import etree

# Zato
from zato.common.as4.common import CryptoSuite, NS
from zato.common.as4.security.sign import get_security_header
from zato.common.typing_ import cast_
from zato.common.util.xml_.constants import Algorithm, Transform
from zato.common.util.xml_.core import qname
from zato.common.util.xml_.mime_ import part_list
from zato.common.util.xml_.wssec import derive_key_encryption_key
from zato.common.util.xml_.xmlsec import encode_base64

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
    from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PublicKey
    from cryptography.x509 import Certificate
    from zato.common.as4.pmode import SecurityConfig
    from zato.common.typing_ import any_, strlist
    from zato.common.util.xml_.keystore import Keystore
    any_ = any_
    strlist = strlist
    Certificate = Certificate
    RSAPublicKey = RSAPublicKey
    X25519PublicKey = X25519PublicKey

# ################################################################################################################################
# ################################################################################################################################

# AES-128-GCM parameters - a 128-bit content encryption key and the 96-bit nonce that GCM expects.
_content_key_size_bytes = 16
_gcm_nonce_size_bytes   = 12

# The HKDF info string for eDelivery 2.0 key derivation - both sides must use the same value.
HKDF_Info = b'zato-as4-edelivery2'

_xenc_nsmap = {
    'xenc':   NS.XENC,
    'xenc11': NS.XENC11,
    'ds':     NS.DS,
    'ds11':   NS.XMLDSIG11,
}

# ################################################################################################################################
# ################################################################################################################################

def _encrypt_part_data(content_key:'bytes', part_data:'bytes') -> 'bytes':
    """ Encrypts one attachment body with AES-128-GCM. Per XML Encryption 1.1
    the cipher bytes are the nonce, the ciphertext and the authentication tag, in that order.
    """
    nonce = urandom(_gcm_nonce_size_bytes)
    ciphertext = AESGCM(content_key).encrypt(nonce, part_data, None)

    out = nonce + ciphertext
    return out

# ################################################################################################################################

def _add_encrypted_data(security:'any_', part_content_id:'str') -> 'str':
    """ Adds one xenc:EncryptedData element describing an encrypted attachment.
    The cipher bytes stay in the MIME part - the element points at them
    through a CipherReference with the SwA ciphertext transform. Returns the element id.
    """
    encrypted_data_id = f'ED-{uuid4().hex}'

    encrypted_data = etree.SubElement(security, qname(NS.XENC, 'EncryptedData'), nsmap=_xenc_nsmap)
    encrypted_data.set('Id', encrypted_data_id)
    encrypted_data.set('Type', Transform.Attachment_Ciphertext)
    encrypted_data.set('MimeType', 'application/octet-stream')

    encryption_method = etree.SubElement(encrypted_data, qname(NS.XENC, 'EncryptionMethod'))
    encryption_method.set('Algorithm', Algorithm.AES128_GCM)

    cipher_data = etree.SubElement(encrypted_data, qname(NS.XENC, 'CipherData'))
    cipher_reference = etree.SubElement(cipher_data, qname(NS.XENC, 'CipherReference'))
    cipher_reference.set('URI', f'cid:{part_content_id}')

    transforms = etree.SubElement(cipher_reference, qname(NS.XENC, 'Transforms'))
    transform = etree.SubElement(transforms, qname(NS.DS, 'Transform'))
    transform.set('Algorithm', Transform.Attachment_Ciphertext)

    out = encrypted_data_id
    return out

# ################################################################################################################################

def _add_recipient_certificate(parent:'any_', keystore:'Keystore') -> 'None':
    """ Adds a ds:KeyInfo with the recipient's certificate so they know which key decrypts this.
    """
    certificate = cast_('Certificate', keystore.peer_encryption_certificate)

    key_info = etree.SubElement(parent, qname(NS.DS, 'KeyInfo'))
    x509_data = etree.SubElement(key_info, qname(NS.DS, 'X509Data'))
    x509_certificate = etree.SubElement(x509_data, qname(NS.DS, 'X509Certificate'))
    x509_certificate.text = encode_base64(certificate.public_bytes(Encoding.DER))

# ################################################################################################################################

def _add_encrypted_key_rsa(
    security:'any_',
    content_key:'bytes',
    keystore:'Keystore',
    config:'SecurityConfig',
    reference_ids:'strlist',
    ) -> 'None':
    """ Adds an xenc:EncryptedKey that wraps the content key with RSA-OAEP
    for the recipient's RSA certificate - the eDelivery 1.x key transport.
    """
    encrypted_key = etree.Element(qname(NS.XENC, 'EncryptedKey'), nsmap=_xenc_nsmap)
    encrypted_key.set('Id', f'EK-{uuid4().hex}')

    encryption_method = etree.SubElement(encrypted_key, qname(NS.XENC, 'EncryptionMethod'))
    encryption_method.set('Algorithm', config.key_transport_algorithm)

    digest_method = etree.SubElement(encryption_method, qname(NS.DS, 'DigestMethod'))
    digest_method.set('Algorithm', config.key_transport_digest)

    mgf = etree.SubElement(encryption_method, qname(NS.XENC11, 'MGF'))
    mgf.set('Algorithm', config.key_transport_mgf)

    _add_recipient_certificate(encrypted_key, keystore)

    # Wrap the content key for the recipient ..
    peer_certificate = cast_('Certificate', keystore.peer_encryption_certificate)
    public_key = cast_('RSAPublicKey', peer_certificate.public_key())
    oaep_padding = OAEP(mgf=MGF1(SHA256()), algorithm=SHA256(), label=None)
    wrapped_key = public_key.encrypt(content_key, oaep_padding)

    cipher_data = etree.SubElement(encrypted_key, qname(NS.XENC, 'CipherData'))
    cipher_value = etree.SubElement(cipher_data, qname(NS.XENC, 'CipherValue'))
    cipher_value.text = encode_base64(wrapped_key)

    # .. and point at every EncryptedData this key unlocks.
    reference_list = etree.SubElement(encrypted_key, qname(NS.XENC, 'ReferenceList'))

    for reference_id in reference_ids:
        data_reference = etree.SubElement(reference_list, qname(NS.XENC, 'DataReference'))
        data_reference.set('URI', f'#{reference_id}')

    # The key goes first in the security header so receivers process it before the signature.
    security.insert(0, encrypted_key)

# ################################################################################################################################

def _add_encrypted_key_ecdh(
    security:'any_',
    content_key:'bytes',
    keystore:'Keystore',
    reference_ids:'strlist',
    ) -> 'None':
    """ Adds an xenc:EncryptedKey for the eDelivery 2.0 suite: an ephemeral X25519 key
    agrees on a shared secret with the recipient's static key, HKDF derives a key
    encryption key from it, and that key wraps the content key with AES key wrap.
    """
    # Agree on a shared secret with a fresh ephemeral key ..
    peer_certificate = cast_('Certificate', keystore.peer_encryption_certificate)
    recipient_public_key = cast_('X25519PublicKey', peer_certificate.public_key())

    ephemeral_key = X25519PrivateKey.generate()
    shared_secret = ephemeral_key.exchange(recipient_public_key)

    # .. derive the key encryption key and wrap the content key with it.
    key_encryption_key = derive_key_encryption_key(shared_secret, HKDF_Info)
    wrapped_key = aes_key_wrap(key_encryption_key, content_key)

    encrypted_key = etree.Element(qname(NS.XENC, 'EncryptedKey'), nsmap=_xenc_nsmap)
    encrypted_key.set('Id', f'EK-{uuid4().hex}')

    encryption_method = etree.SubElement(encrypted_key, qname(NS.XENC, 'EncryptionMethod'))
    encryption_method.set('Algorithm', Algorithm.AES128_KeyWrap)

    # The agreement method tells the recipient how the wrapping key came to be -
    # it carries our ephemeral public key and names the derivation function.
    key_info = etree.SubElement(encrypted_key, qname(NS.DS, 'KeyInfo'))
    agreement_method = etree.SubElement(key_info, qname(NS.XENC, 'AgreementMethod'))
    agreement_method.set('Algorithm', Algorithm.ECDH_ES)

    key_derivation = etree.SubElement(agreement_method, qname(NS.XENC11, 'KeyDerivationMethod'))
    key_derivation.set('Algorithm', Algorithm.HKDF)

    originator = etree.SubElement(agreement_method, qname(NS.XENC, 'OriginatorKeyInfo'))
    ephemeral_public_bytes = ephemeral_key.public_key().public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
    key_value = etree.SubElement(originator, qname(NS.DS, 'KeyValue'))
    der_key_value = etree.SubElement(key_value, qname(NS.XMLDSIG11, 'DEREncodedKeyValue'))
    der_key_value.text = encode_base64(ephemeral_public_bytes)

    recipient = etree.SubElement(agreement_method, qname(NS.XENC, 'RecipientKeyInfo'))
    x509_data = etree.SubElement(recipient, qname(NS.DS, 'X509Data'))
    x509_certificate = etree.SubElement(x509_data, qname(NS.DS, 'X509Certificate'))
    x509_certificate.text = encode_base64(peer_certificate.public_bytes(Encoding.DER))

    cipher_data = etree.SubElement(encrypted_key, qname(NS.XENC, 'CipherData'))
    cipher_value = etree.SubElement(cipher_data, qname(NS.XENC, 'CipherValue'))
    cipher_value.text = encode_base64(wrapped_key)

    reference_list = etree.SubElement(encrypted_key, qname(NS.XENC, 'ReferenceList'))

    for reference_id in reference_ids:
        data_reference = etree.SubElement(reference_list, qname(NS.XENC, 'DataReference'))
        data_reference.set('URI', f'#{reference_id}')

    security.insert(0, encrypted_key)

# ################################################################################################################################

def encrypt_parts(
    envelope:'any_',
    parts:'part_list',
    keystore:'Keystore',
    config:'SecurityConfig',
    ) -> 'None':
    """ Encrypts every attachment of an AS4 message in place with a fresh AES-128-GCM key
    and records the encryption in the wsse:Security header. Must run after signing -
    the signature covers the plaintext, encryption covers the wire.
    """
    # Nothing to do for messages without payloads, such as signals.
    if not parts:
        return

    security = get_security_header(envelope)
    content_key = urandom(_content_key_size_bytes)

    reference_ids:'strlist' = []

    # Encrypt each attachment and describe it in the header ..
    for part in parts:
        part.data = _encrypt_part_data(content_key, part.data)
        part.content_type = 'application/octet-stream'

        encrypted_data_id = _add_encrypted_data(security, part.content_id)
        reference_ids.append(encrypted_data_id)

    # .. then record how the content key itself is protected.
    if config.crypto_suite == CryptoSuite.EdDSA:
        _add_encrypted_key_ecdh(security, content_key, keystore, reference_ids)
    else:
        _add_encrypted_key_rsa(security, content_key, keystore, config, reference_ids)

# ################################################################################################################################
# ################################################################################################################################
