# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from uuid import uuid4

# lxml
from lxml import etree

# Zato
from zato.common.soap.common import NS, SOAPException, SOAPVersion
from zato.common.soap.envelope import build_envelope, get_body, get_header, set_must_understand
from zato.common.util.xml_.core import qname, utc_timestamp
from zato.common.util.xml_.mime_ import part_list

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strnone
    any_ = any_
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

    if party_type:
        party.set('type', party_type)

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
    out.from_party_type = from_party.get('type')

    to_element = message_header.find(qname(NS.EBXML2, 'To'))
    to_party = to_element.find(qname(NS.EBXML2, 'PartyId'))
    out.to_party = to_party.text
    out.to_party_type = to_party.get('type')

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
