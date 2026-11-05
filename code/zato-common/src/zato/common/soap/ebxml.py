# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from dataclasses import dataclass

# cryptography
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import Encoding

# lxml
from lxml import etree

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.soap.common import NS, SOAPException, SOAPVersion
from zato.common.soap.envelope import build_envelope, find_header, get_body, get_header, set_must_understand
from zato.common.typing_ import cast_
from zato.common.util.xml_.constants import Algorithm, Transform
from zato.common.util.xml_.core import Id_Size_Bits, qname, utc_timestamp
from zato.common.util.xml_.mime_ import part_list
from zato.common.util.xml_.xmlsec import canonicalize_inclusive, digest_bytes, encode_base64

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
    from zato.common.typing_ import any_, anytuple, intlist, strlist, strnone
    from zato.common.util.xml_.keystore import Keystore
    any_ = any_
    anytuple = anytuple
    intlist = intlist
    Keystore = Keystore
    RSAPrivateKey = RSAPrivateKey
    strlist = strlist
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

# The eb:version attribute every ebMS 2.0 element carries.
_ebxml_version = '2.0'

_eb_nsmap = {
    'eb': NS.EBXML2,
}

_ds_nsmap = {
    'ds': NS.DS,
}

_xlink_href = f'{{{NS.XLINK}}}href'
_xlink_type = f'{{{NS.XLINK}}}type'

_soap_actor = qname(NS.SOAP11, 'actor')

# ################################################################################################################################
# ################################################################################################################################

class Actor:
    """ The SOAP actors of the ebMS 2.0 header blocks.
    """
    To_Party_MSH = 'urn:oasis:names:tc:ebxml-msg:actor:toPartyMSH'
    Next_MSH     = 'urn:oasis:names:tc:ebxml-msg:actor:nextMSH'
    SOAP_Next    = 'http://schemas.xmlsoap.org/soap/actor/next'

# The XPath filter transform of the ebMS 2.0 signature profile.
XPath_Transform = 'http://www.w3.org/TR/1999/REC-xpath-19991116'

# The prefix the XPath expression binds to the SOAP 1.1 envelope namespace.
_xpath_soap_prefix = 'SOAP'

_xpath_nsmap = {
    _xpath_soap_prefix: NS.SOAP11,
}

# The XPath expression leaves out the header blocks addressed to the next message service handler,
# because an intermediary may change them in transit.
_xpath_next_msh  = f'ancestor-or-self::node()[@{_xpath_soap_prefix}:actor="{Actor.Next_MSH}"]'
_xpath_soap_next = f'ancestor-or-self::node()[@{_xpath_soap_prefix}:actor="{Actor.SOAP_Next}"]'
XPath_Expression = f'not({_xpath_next_msh} | {_xpath_soap_next})'

# The actors whose header blocks the XPath filter leaves out.
_excluded_actors = {Actor.Next_MSH, Actor.SOAP_Next}

# The eb:Action of the message service handler's error messages.
_action_message_error = 'MessageError'

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

    # The eb:Role of each party, the roles the agreement binds the parties to.
    from_role: 'strnone' = None
    to_role:   'strnone' = None

    # The eb:type of the service. A service that is not an absolute URI requires it.
    service_type: 'strnone' = None

    # The MIME payload parts of an incoming message, in the order they arrived, empty when the
    # message carries none. An ebXML message keeps its business document in a payload part rather
    # than in the body, so for anything other than a bare acknowledgement this is the message -
    # the Manifest in the body only points at what is here.
    #
    # A message being built leaves this empty, the parts to send being passed separately.
    attachments: 'part_list'

    def __init__(self) -> 'None':
        self.attachments = []

# ################################################################################################################################
# ################################################################################################################################

def new_message_id(suffix:'str'='zato') -> 'str':
    """ Returns a fresh eb:MessageId, unique per RFC 2822 msg-id conventions.
    """
    out = f'{CryptoManager.generate_hex_string(Id_Size_Bits)}@{suffix}'
    return out

# ################################################################################################################################

def _add_party(parent:'any_', tag:'str', party_id:'str', party_type:'strnone', role:'strnone') -> 'None':
    """ Adds one eb:From or eb:To block with its eb:PartyId and, if given, its eb:Role.
    """
    element = etree.SubElement(parent, qname(NS.EBXML2, tag))

    party = etree.SubElement(element, qname(NS.EBXML2, 'PartyId'))
    party.text = party_id

    # The ebMS 2.0 schema is attributeFormDefault="qualified", so this is eb:type.
    if party_type:
        party.set(qname(NS.EBXML2, 'type'), party_type)

    if role:
        role_element = etree.SubElement(element, qname(NS.EBXML2, 'Role'))
        role_element.text = role

# ################################################################################################################################

def _add_header_block(header:'any_', tag:'str', actor:'str') -> 'any_':
    """ Adds one mandatory ebMS 2.0 header block addressed to the given actor.
    """
    out = etree.SubElement(header, qname(NS.EBXML2, tag), nsmap=_eb_nsmap)
    out.set(qname(NS.EBXML2, 'version'), _ebxml_version)
    out.set(_soap_actor, actor)
    set_must_understand(out, SOAPVersion.V11)

    return out

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

    _add_party(message_header, 'From', info.from_party, info.from_party_type, info.from_role)
    _add_party(message_header, 'To', info.to_party, info.to_party_type, info.to_role)

    cpa_id = etree.SubElement(message_header, qname(NS.EBXML2, 'CPAId'))
    cpa_id.text = info.cpa_id

    conversation_id = etree.SubElement(message_header, qname(NS.EBXML2, 'ConversationId'))
    conversation_id.text = info.conversation_id

    service = etree.SubElement(message_header, qname(NS.EBXML2, 'Service'))
    service.text = info.service

    if info.service_type:
        service.set(qname(NS.EBXML2, 'type'), info.service_type)

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

def request_sync_acknowledgment(envelope:'any_') -> 'None':
    """ Asks the receiving message service handler for an unsigned acknowledgment returned
    in the HTTP response to this very request. The receiver reads its header blocks in order,
    and eb:SyncReply after eb:AckRequested is what makes the acknowledgment synchronous.
    """
    header = get_header(envelope)

    ack_requested = _add_header_block(header, 'AckRequested', Actor.To_Party_MSH)
    ack_requested.set(qname(NS.EBXML2, 'signed'), 'false')

    _ = _add_header_block(header, 'SyncReply', Actor.SOAP_Next)

# ################################################################################################################################
# ################################################################################################################################

def _index_path(element:'any_') -> 'intlist':
    """ Returns the position of an element as the indexes of it and its ancestors under their parents.
    """
    out:'intlist' = []

    while (parent := element.getparent()) is not None:
        index = parent.index(element)
        out.insert(0, index)
        element = parent

    return out

# ################################################################################################################################

def _remove(element:'any_') -> 'None':
    """ Removes an element and everything under it, leaving the text that follows it in place.
    """
    parent = element.getparent()

    if tail := element.tail:

        if (previous := element.getprevious()) is not None:
            if previous.tail is None:
                previous.tail = tail
            else:
                previous.tail = previous.tail + tail

        else:
            if parent.text is None:
                parent.text = tail
            else:
                parent.text = parent.text + tail

    parent.remove(element)

# ################################################################################################################################

def _canonicalize_envelope(envelope:'any_', signature:'any_') -> 'bytes':
    """ Returns the canonical form of the envelope that a reference with an empty URI covers - without the
    signature, which is the enveloped-signature transform, and without the header blocks addressed
    to the next message service handler, which is the XPath filter transform.
    """
    copy = deepcopy(envelope)

    # The signature is in the document when it is verified, but not yet when it is computed ..
    if signature is not None:
        path = _index_path(signature)
        signature_copy = copy

        for index in path:
            signature_copy = signature_copy[index]

        _remove(signature_copy)

    # .. and the header blocks that intermediaries may change are left out ..
    excluded = []

    for element in copy.iter():
        if not isinstance(element.tag, str):
            continue
        if element.get(_soap_actor) in _excluded_actors:
            excluded.append(element)

    # .. with an excluded element under another excluded element removed along with its ancestor.
    for element in excluded:
        if element.getparent() is not None:
            _remove(element)

    out = canonicalize_inclusive(copy)
    return out

# ################################################################################################################################

def _add_reference(signed_info:'any_', uri:'str', digest_value:'str') -> 'any_':
    """ Adds one SHA-256 ds:Reference to a ds:SignedInfo.
    """
    out = etree.SubElement(signed_info, qname(NS.DS, 'Reference'))
    out.set('URI', uri)

    digest_method = etree.SubElement(out, qname(NS.DS, 'DigestMethod'))
    digest_method.set('Algorithm', Algorithm.SHA256)

    digest_value_element = etree.SubElement(out, qname(NS.DS, 'DigestValue'))
    digest_value_element.text = digest_value

    return out

# ################################################################################################################################

def sign_message(envelope:'any_', parts:'part_list', keystore:'Keystore') -> 'any_':
    """ Signs an envelope and its payloads with the ebMS 2.0 XMLDSig profile - one ds:Signature directly
    in the SOAP Header, its first reference covering the envelope and each next one a payload by its cid: URI,
    with the signer's certificate inline in ds:KeyInfo. Returns the ds:Signature element.
    """
    signing_key = cast_('RSAPrivateKey', keystore.signing_key)

    # The envelope is digested before the signature goes into it, which is what the enveloped transform yields ..
    canonical_envelope = _canonicalize_envelope(envelope, None)
    envelope_digest = digest_bytes(canonical_envelope)

    header = get_header(envelope)
    out = etree.SubElement(header, qname(NS.DS, 'Signature'), nsmap=_ds_nsmap)

    signed_info = etree.SubElement(out, qname(NS.DS, 'SignedInfo'))

    canonicalization_method = etree.SubElement(signed_info, qname(NS.DS, 'CanonicalizationMethod'))
    canonicalization_method.set('Algorithm', Algorithm.C14N)

    signature_method = etree.SubElement(signed_info, qname(NS.DS, 'SignatureMethod'))
    signature_method.set('Algorithm', Algorithm.RSA_SHA256)

    envelope_reference = _add_reference(signed_info, '', envelope_digest)

    # .. the transforms of a reference precede its digest method ..
    transforms = etree.Element(qname(NS.DS, 'Transforms'))
    envelope_reference.insert(0, transforms)

    enveloped = etree.SubElement(transforms, qname(NS.DS, 'Transform'))
    enveloped.set('Algorithm', Transform.Enveloped)

    xpath_transform = etree.SubElement(transforms, qname(NS.DS, 'Transform'))
    xpath_transform.set('Algorithm', XPath_Transform)

    xpath = etree.SubElement(xpath_transform, qname(NS.DS, 'XPath'), nsmap=_xpath_nsmap)
    xpath.text = XPath_Expression

    c14n = etree.SubElement(transforms, qname(NS.DS, 'Transform'))
    c14n.set('Algorithm', Algorithm.C14N)

    # .. each payload is digested over the octets of its MIME part, with no transforms ..
    for part in parts:
        payload_digest = digest_bytes(part.data)
        _ = _add_reference(signed_info, f'cid:{part.content_id}', payload_digest)

    # .. the SignedInfo is canonicalized where it stands, with the namespace context it is verified in ..
    canonical_signed_info = canonicalize_inclusive(signed_info)
    signature_bytes = signing_key.sign(canonical_signed_info, PKCS1v15(), SHA256())

    signature_value = etree.SubElement(out, qname(NS.DS, 'SignatureValue'))
    signature_value.text = encode_base64(signature_bytes)

    # .. and the certificate is inline so that the receiver can match it against the agreement.
    key_info = etree.SubElement(out, qname(NS.DS, 'KeyInfo'))
    x509_data = etree.SubElement(key_info, qname(NS.DS, 'X509Data'))

    for certificate in keystore.signing_certificate_chain:
        certificate_element = etree.SubElement(x509_data, qname(NS.DS, 'X509Certificate'))
        certificate_element.text = encode_base64(certificate.public_bytes(Encoding.DER))

    return out

# ################################################################################################################################
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

def _read_party(message_header:'any_', tag:'str') -> 'anytuple':
    """ Returns the PartyId, its type and the role of an eb:From or eb:To block.
    """
    element = message_header.find(qname(NS.EBXML2, tag))
    party = element.find(qname(NS.EBXML2, 'PartyId'))
    role = element.find(qname(NS.EBXML2, 'Role'))

    party_type = party.get(qname(NS.EBXML2, 'type'))

    if role is None:
        role_text = None
    else:
        role_text = role.text

    out = (party.text, party_type, role_text)
    return out

# ################################################################################################################################

def parse_message_header(envelope:'any_') -> 'EbXMLInfo':
    """ Reads the ebMS 2.0 MessageHeader of an incoming message.
    """
    header = find_header(envelope)

    if header is None:
        raise SOAPException('Message has no ebMS 2.0 MessageHeader')

    message_header = header.find(qname(NS.EBXML2, 'MessageHeader'))

    if message_header is None:
        raise SOAPException('Message has no ebMS 2.0 MessageHeader')

    # Our response to produce
    out = EbXMLInfo()

    out.from_party, out.from_party_type, out.from_role = _read_party(message_header, 'From')
    out.to_party, out.to_party_type, out.to_role = _read_party(message_header, 'To')

    out.cpa_id          = _find_text(message_header, 'CPAId')
    out.conversation_id = _find_text(message_header, 'ConversationId')
    out.service         = _find_text(message_header, 'Service')
    out.action          = _find_text(message_header, 'Action')

    service = message_header.find(qname(NS.EBXML2, 'Service'))
    out.service_type = service.get(qname(NS.EBXML2, 'type'))

    message_data = message_header.find(qname(NS.EBXML2, 'MessageData'))
    out.message_id = _find_text(message_data, 'MessageId')

    ref_to = message_data.find(qname(NS.EBXML2, 'RefToMessageId'))
    if ref_to is not None:
        out.ref_to_message_id = ref_to.text

    return out

# ################################################################################################################################

def check_reply(envelope:'any_', info:'EbXMLInfo', message_id:'strnone') -> 'None':
    """ Raises SOAPException when a synchronous reply is an ebMS 2.0 error message
    or when it does not refer to the message it was returned for.
    """
    header = find_header(envelope)
    error_list = header.find(qname(NS.EBXML2, 'ErrorList'))

    # An error message has an eb:ErrorList with one eb:Error per problem found ..
    if error_list is not None:

        errors:'strlist' = []

        for error in error_list.findall(qname(NS.EBXML2, 'Error')):
            error_code = error.get(qname(NS.EBXML2, 'errorCode'))
            description = error.find(qname(NS.EBXML2, 'Description'))

            if description is None:
                errors.append(error_code)
            else:
                errors.append(f'{error_code} - {description.text}')

        raise SOAPException(f'Message `{message_id}` was rejected -> {errors}')

    # .. an error message without an eb:ErrorList is rejected as well ..
    if info.action == _action_message_error:
        raise SOAPException(f'Message `{message_id}` was rejected with an error message without an ErrorList')

    # .. and anything else has to refer back to what was sent.
    if info.ref_to_message_id != message_id:
        raise SOAPException(f'Reply refers to `{info.ref_to_message_id}` instead of `{message_id}`')

# ################################################################################################################################

def get_manifest_references(envelope:'any_') -> 'strlist':
    """ Returns the Content-IDs the body's Manifest references, without their cid: prefixes.
    """
    body = get_body(envelope)
    manifest = body.find(qname(NS.EBXML2, 'Manifest'))

    # Our response to produce
    out:'strlist' = []

    if manifest is None:
        return out

    for reference in manifest.findall(qname(NS.EBXML2, 'Reference')):
        href = reference.get(_xlink_href)
        if href and href.startswith('cid:'):
            out.append(href[4:])

    return out

# ################################################################################################################################
# ################################################################################################################################
