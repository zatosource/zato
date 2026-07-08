# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
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
from zato.common.soap.common import NS, SOAPException, SOAPSecurityException, SOAPVersion
from zato.common.soap.envelope import build_envelope, get_body, get_header, set_must_understand
from zato.common.typing_ import cast_
from zato.common.util.xml_.constants import Algorithm, Transform
from zato.common.util.xml_.core import qname, utc_timestamp, XMLSecurityException
from zato.common.util.xml_.mime_ import part_list
from zato.common.util.xml_.token import parse_x509v3
from zato.common.util.xml_.wssec import compute_signature_value, recover_content_key, validate_certificate_chain, \
    verify_signature_value
from zato.common.util.xml_.xmlsec import decode_base64, digest_bytes, encode_base64

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
    from cryptography.x509 import Certificate
    from zato.common.typing_ import any_, strnone
    from zato.common.util.xml_.keystore import Keystore
    from zato.common.util.xml_.mime_ import Part
    any_ = any_
    Certificate = Certificate
    Keystore = Keystore
    Part = Part
    RSAPublicKey = RSAPublicKey
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

# The eb:version attribute every ebMS 2.0 element carries.
_ebxml_version = '2.0'

_eb_nsmap = {
    'eb': NS.EBXML2,
}

_xlink_href = f'{{{NS.XLINK}}}href'
_xlink_type = f'{{{NS.XLINK}}}type'

# AES-128-GCM parameters for payload encryption, matching the WS-Security body cipher.
_content_key_size_bytes = 16
_gcm_nonce_size_bytes   = 12

# The XML Encryption type of an encrypted MIME part - a whole element's worth of octets.
_xenc_element_type = 'http://www.w3.org/2001/04/xmlenc#Element'

_ds_nsmap = {
    'ds': NS.DS,
}

_xenc_nsmap = {
    'xenc':   NS.XENC,
    'xenc11': NS.XENC11,
    'ds':     NS.DS,
}

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class EbXMLInfo:
    """ The addressing details of an ebMS 2.0 message, either to be built
    into an outgoing one or as read from an incoming one.
    """
    from_party:    'str' = ''
    to_party:      'str' = ''
    cpa_id:        'str' = ''
    conversation_id: 'str' = ''
    service:       'str' = ''
    action:        'str' = ''
    message_id:    'strnone' = None
    ref_to_message_id: 'strnone' = None

    # Optional PartyId type attributes, e.g. urn:nhs:names:partyType:ocs+serviceInstance.
    from_party_type: 'strnone' = None
    to_party_type:   'strnone' = None

# ################################################################################################################################
# ################################################################################################################################

def new_message_id(suffix:'str'='zato') -> 'str':
    """ Returns a fresh eb:MessageId, unique per RFC 2822 msg-id conventions.
    """
    out = f'{uuid4()}@{suffix}'
    return out

# ################################################################################################################################

def _add_party(parent:'any_', tag:'str', party_id:'str', party_type:'strnone') -> 'None':
    """ Adds one eb:From or eb:To block with its eb:PartyId.
    """
    element = etree.SubElement(parent, qname(NS.EBXML2, tag))

    party = etree.SubElement(element, qname(NS.EBXML2, 'PartyId'))
    party.text = party_id

    # The ebMS 2.0 schema is attributeFormDefault="qualified", so this is eb:type.
    if party_type:
        party.set(qname(NS.EBXML2, 'type'), party_type)

# ################################################################################################################################

def build_message(info:'EbXMLInfo', parts:'part_list') -> 'any_':
    """ Returns a new SOAP 1.1 envelope carrying an ebMS 2.0 MessageHeader
    and a Manifest that references each attachment by its Content-ID.
    """
    envelope = build_envelope(SOAPVersion.V11)
    header = get_header(envelope)

    # The message header carries who talks to whom about what ..
    message_header = etree.SubElement(header, qname(NS.EBXML2, 'MessageHeader'), nsmap=_eb_nsmap)
    message_header.set(qname(NS.EBXML2, 'version'), _ebxml_version)
    set_must_understand(message_header, SOAPVersion.V11)

    _add_party(message_header, 'From', info.from_party, info.from_party_type)
    _add_party(message_header, 'To', info.to_party, info.to_party_type)

    cpa_id = etree.SubElement(message_header, qname(NS.EBXML2, 'CPAId'))
    cpa_id.text = info.cpa_id

    conversation_id = etree.SubElement(message_header, qname(NS.EBXML2, 'ConversationId'))
    conversation_id.text = info.conversation_id

    service = etree.SubElement(message_header, qname(NS.EBXML2, 'Service'))
    service.text = info.service

    action = etree.SubElement(message_header, qname(NS.EBXML2, 'Action'))
    action.text = info.action

    # .. the message data identifies this very message ..
    if not info.message_id:
        info.message_id = new_message_id()

    message_data = etree.SubElement(message_header, qname(NS.EBXML2, 'MessageData'))

    message_id = etree.SubElement(message_data, qname(NS.EBXML2, 'MessageId'))
    message_id.text = info.message_id

    timestamp = etree.SubElement(message_data, qname(NS.EBXML2, 'Timestamp'))
    timestamp.text = utc_timestamp()

    if info.ref_to_message_id:
        ref_to = etree.SubElement(message_data, qname(NS.EBXML2, 'RefToMessageId'))
        ref_to.text = info.ref_to_message_id

    # .. and the manifest in the body points at each SwA attachment.
    if parts:
        body = get_body(envelope)

        manifest = etree.SubElement(body, qname(NS.EBXML2, 'Manifest'), nsmap=_eb_nsmap)
        manifest.set(qname(NS.EBXML2, 'version'), _ebxml_version)

        for part in parts:
            reference = etree.SubElement(manifest, qname(NS.EBXML2, 'Reference'))
            reference.set(_xlink_type, 'simple')
            reference.set(_xlink_href, f'cid:{part.content_id}')

    return envelope

# ################################################################################################################################

def _find_text(parent:'any_', tag:'str') -> 'str':
    """ Returns the text of one required eb element.
    """
    element = parent.find(qname(NS.EBXML2, tag))

    if element is None:
        raise SOAPException(f'MessageHeader has no `{tag}` element')

    out = element.text
    return out

# ################################################################################################################################

def parse_message_header(envelope:'any_') -> 'EbXMLInfo':
    """ Reads the ebMS 2.0 MessageHeader of an incoming message.
    """
    header = get_header(envelope)
    message_header = header.find(qname(NS.EBXML2, 'MessageHeader'))

    if message_header is None:
        raise SOAPException('Message has no ebMS 2.0 MessageHeader')

    # Our response to produce
    out = EbXMLInfo()

    from_element = message_header.find(qname(NS.EBXML2, 'From'))
    from_party = from_element.find(qname(NS.EBXML2, 'PartyId'))
    out.from_party = from_party.text
    out.from_party_type = from_party.get(qname(NS.EBXML2, 'type'))

    to_element = message_header.find(qname(NS.EBXML2, 'To'))
    to_party = to_element.find(qname(NS.EBXML2, 'PartyId'))
    out.to_party = to_party.text
    out.to_party_type = to_party.get(qname(NS.EBXML2, 'type'))

    out.cpa_id          = _find_text(message_header, 'CPAId')
    out.conversation_id = _find_text(message_header, 'ConversationId')
    out.service         = _find_text(message_header, 'Service')
    out.action          = _find_text(message_header, 'Action')

    message_data = message_header.find(qname(NS.EBXML2, 'MessageData'))
    out.message_id = _find_text(message_data, 'MessageId')

    ref_to = message_data.find(qname(NS.EBXML2, 'RefToMessageId'))
    if ref_to is not None:
        out.ref_to_message_id = ref_to.text

    return out

# ################################################################################################################################

def get_manifest_references(envelope:'any_') -> 'list[str]':
    """ Returns the Content-IDs the body's Manifest references, without their cid: prefixes.
    """
    body = get_body(envelope)
    manifest = body.find(qname(NS.EBXML2, 'Manifest'))

    # Our response to produce
    out:'list[str]' = []

    if manifest is None:
        return out

    for reference in manifest.findall(qname(NS.EBXML2, 'Reference')):
        href = reference.get(_xlink_href)
        if href and href.startswith('cid:'):
            out.append(href[4:])

    return out

# ################################################################################################################################
# ################################################################################################################################

def sign_payload(part:'Part', keystore:'Keystore', signature_algorithm:'str'=Algorithm.RSA_SHA256) -> 'any_':
    """ Signs one MIME payload with a detached ds:Signature that covers the raw part bytes
    through the SwA content transform - the enterprise-certificate signing ebXML health
    frameworks put on their payloads. Returns the ds:Signature element to travel with the message.
    """
    signature = etree.Element(qname(NS.DS, 'Signature'), nsmap=_ds_nsmap)

    signed_info = etree.SubElement(signature, qname(NS.DS, 'SignedInfo'))

    canonicalization_method = etree.SubElement(signed_info, qname(NS.DS, 'CanonicalizationMethod'))
    canonicalization_method.set('Algorithm', Algorithm.C14N_Exclusive)

    signature_method = etree.SubElement(signed_info, qname(NS.DS, 'SignatureMethod'))
    signature_method.set('Algorithm', signature_algorithm)

    # The reference covers the raw octets of the part, addressed by its Content-ID.
    reference = etree.SubElement(signed_info, qname(NS.DS, 'Reference'))
    reference.set('URI', f'cid:{part.content_id}')

    transforms = etree.SubElement(reference, qname(NS.DS, 'Transforms'))
    transform = etree.SubElement(transforms, qname(NS.DS, 'Transform'))
    transform.set('Algorithm', Transform.Attachment_Content)

    digest_method = etree.SubElement(reference, qname(NS.DS, 'DigestMethod'))
    digest_method.set('Algorithm', Algorithm.SHA256)

    digest_value = etree.SubElement(reference, qname(NS.DS, 'DigestValue'))
    digest_value.text = digest_bytes(part.data)

    signature_bytes = compute_signature_value(signed_info, keystore, signature_algorithm)

    signature_value = etree.SubElement(signature, qname(NS.DS, 'SignatureValue'))
    signature_value.text = encode_base64(signature_bytes)

    # The signer's certificate travels inline so verifiers can pin it or chain it to an anchor.
    key_info = etree.SubElement(signature, qname(NS.DS, 'KeyInfo'))
    x509_data = etree.SubElement(key_info, qname(NS.DS, 'X509Data'))
    x509_certificate = etree.SubElement(x509_data, qname(NS.DS, 'X509Certificate'))
    x509_certificate.text = encode_base64(keystore.signing_certificate.public_bytes(Encoding.DER))

    return signature

# ################################################################################################################################

def verify_payload(signature:'any_', part:'Part', keystore:'Keystore') -> 'any_':
    """ Verifies a detached payload signature - the reference digest over the part bytes,
    the signature value and the trust in the signer. Returns the signer's certificate.
    """
    try:
        key_info = signature.find(qname(NS.DS, 'KeyInfo'))
        x509_certificate = key_info.find(f'.//{qname(NS.DS, "X509Certificate")}')

        if x509_certificate is None:
            raise XMLSecurityException('Payload signature has no X509Certificate')

        chain = [parse_x509v3(decode_base64(x509_certificate.text or ''))]
        validate_certificate_chain(chain, keystore)

        signed_info = signature.find(qname(NS.DS, 'SignedInfo'))
        reference = signed_info.find(qname(NS.DS, 'Reference'))
        digest_value_element = reference.find(qname(NS.DS, 'DigestValue'))
        expected_digest = ''.join((digest_value_element.text or '').split())

        if digest_bytes(part.data) != expected_digest:
            raise XMLSecurityException('Payload digest mismatch')

        verify_signature_value(signature, chain)

    except XMLSecurityException as e:
        raise SOAPSecurityException(e.args[0])

    out = chain[0]
    return out

# ################################################################################################################################

def encrypt_payload(part:'Part', keystore:'Keystore') -> 'any_':
    """ Encrypts a MIME payload in place with a fresh AES-128-GCM key, wrapping that key
    for the recipient's RSA certificate with RSA-OAEP. Returns the xenc:EncryptedKey element
    that carries the wrapped key and points back at the part.
    """
    content_key = urandom(_content_key_size_bytes)
    nonce = urandom(_gcm_nonce_size_bytes)

    # Per XML Encryption 1.1 the cipher value is the nonce, the ciphertext and the tag.
    part.data = nonce + AESGCM(content_key).encrypt(nonce, part.data, None)

    encrypted_key = etree.Element(qname(NS.XENC, 'EncryptedKey'), nsmap=_xenc_nsmap)
    encrypted_key.set('Id', f'EK-{uuid4().hex}')

    encryption_method = etree.SubElement(encrypted_key, qname(NS.XENC, 'EncryptionMethod'))
    encryption_method.set('Algorithm', Algorithm.RSA_OAEP)

    digest_method = etree.SubElement(encryption_method, qname(NS.DS, 'DigestMethod'))
    digest_method.set('Algorithm', Algorithm.SHA256)

    mgf = etree.SubElement(encryption_method, qname(NS.XENC11, 'MGF'))
    mgf.set('Algorithm', Algorithm.MGF1_SHA256)

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

    # The reference names the part these bytes belong to, mirroring the manifest's cid addressing.
    reference_list = etree.SubElement(encrypted_key, qname(NS.XENC, 'ReferenceList'))
    data_reference = etree.SubElement(reference_list, qname(NS.XENC, 'DataReference'))
    data_reference.set('URI', f'cid:{part.content_id}')
    data_reference.set('Type', _xenc_element_type)

    return encrypted_key

# ################################################################################################################################

def decrypt_payload(encrypted_key:'any_', part:'Part', keystore:'Keystore') -> 'None':
    """ Decrypts a MIME payload in place, reversing encrypt_payload.
    """
    try:
        content_key = recover_content_key(encrypted_key, keystore)
    except XMLSecurityException as e:
        raise SOAPSecurityException(e.args[0])

    # Per XML Encryption 1.1 the GCM nonce is prefixed to the ciphertext.
    nonce = part.data[:_gcm_nonce_size_bytes]
    ciphertext = part.data[_gcm_nonce_size_bytes:]

    try:
        part.data = AESGCM(content_key).decrypt(nonce, ciphertext, None)
    except Exception:
        raise SOAPSecurityException('Could not decrypt the payload')

# ################################################################################################################################
# ################################################################################################################################
