# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# lxml
from lxml.etree import SubElement

# Zato
from zato.common.b2b.ebms2.common import Actor, EbMS2Exception, ErrorCode, Max_Sequence_Number, new_party_id, NS, \
    SequenceStatus
from zato.common.b2b.ebms2.xml_ import add_body_element, add_description, add_eb, add_header_block, check_extension, \
    eb_tag, find_all_eb, find_eb, get_eb_attribute, location, optional_eb_text, parse_boolean, parse_timestamp, require_eb, \
    require_eb_attribute, require_eb_text, require_text, set_eb_attribute, SOAP_Actor, XML_Lang
from zato.common.util.xml_.core import qname, to_timestamp

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.b2b.ebms2.common import party_id_list
    from zato.common.typing_ import any_, dtnone
    any_ = any_
    datetime = datetime
    dtnone = dtnone
    party_id_list = party_id_list

# ################################################################################################################################
# ################################################################################################################################

_xlink_href = qname(NS.XLINK, 'href')
_xlink_role = qname(NS.XLINK, 'role')
_xlink_type = qname(NS.XLINK, 'type')

# The fixed value of xlink:type on a manifest reference.
_xlink_type_simple = 'simple'

# Receivers match the attributes of a manifest reference by their prefixed names, such as xlink:href.
_reference_nsmap = {'xlink': NS.XLINK}
_reference_tag = eb_tag('Reference')

_sequence_statuses = {SequenceStatus.Reset, SequenceStatus.Continue}

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Description:
    text:     str
    language: str

description_list = list[Description]

# ################################################################################################################################

@dataclass(init=False)
class HeaderParty:
    """ The From or the To of a message header.
    """
    party_ids: 'party_id_list'
    role:      str = ''

# ################################################################################################################################

@dataclass(init=False)
class MessageData:
    message_id:        str
    timestamp:         'datetime'
    ref_to_message_id: str = ''
    time_to_live:      'dtnone' = None

# ################################################################################################################################

@dataclass(init=False)
class MessageHeader:
    from_party:      'HeaderParty'
    to_party:        'HeaderParty'
    cpa_id:          str
    conversation_id: str
    service:         str
    service_type:    str = ''
    action:          str
    message_data:    'MessageData'

    duplicate_elimination: bool = False
    descriptions: 'description_list'

    def __init__(self) -> 'None':
        self.descriptions = []

# ################################################################################################################################

@dataclass(init=False)
class AckRequested:
    signed: bool = False
    actor:  str = Actor.To_Party_MSH

# ################################################################################################################################

@dataclass(init=False)
class MessageOrder:
    sequence_number: int
    status:          str = SequenceStatus.Continue

# ################################################################################################################################

@dataclass(init=False)
class ManifestSchema:
    location: str
    version:  str = ''

manifest_schema_list = list[ManifestSchema]

# ################################################################################################################################

@dataclass(init=False)
class ManifestReference:
    """ One eb:Reference of a manifest - a payload in a MIME part, when href is a cid: URI, or a document elsewhere.
    """
    href:         str
    reference_id: str = ''
    role:         str = ''
    schemas:      'manifest_schema_list'
    descriptions: 'description_list'

    def __init__(self) -> 'None':
        self.schemas = []
        self.descriptions = []

manifest_reference_list = list[ManifestReference]

# ################################################################################################################################

@dataclass(init=False)
class Manifest:
    references: 'manifest_reference_list'

    def __init__(self) -> 'None':
        self.references = []

# ################################################################################################################################
# ################################################################################################################################

def _add_party(parent:'any_', name:'str', party:'HeaderParty') -> 'None':
    element = add_eb(parent, name)

    for party_id in party.party_ids:
        party_id_element = add_eb(element, 'PartyId', party_id.value)
        set_eb_attribute(party_id_element, 'type', party_id.id_type)

    if party.role:
        _ = add_eb(element, 'Role', party.role)

# ################################################################################################################################

def add_message_header(soap_header:'any_', header:'MessageHeader') -> 'any_':
    """ Appends an eb:MessageHeader to a SOAP header.
    """
    out = add_header_block(soap_header, 'MessageHeader')

    _add_party(out, 'From', header.from_party)
    _add_party(out, 'To', header.to_party)

    _ = add_eb(out, 'CPAId', header.cpa_id)
    _ = add_eb(out, 'ConversationId', header.conversation_id)

    service = add_eb(out, 'Service', header.service)
    set_eb_attribute(service, 'type', header.service_type)

    _ = add_eb(out, 'Action', header.action)

    message_data = header.message_data
    timestamp = to_timestamp(message_data.timestamp)

    message_data_element = add_eb(out, 'MessageData')
    _ = add_eb(message_data_element, 'MessageId', message_data.message_id)
    _ = add_eb(message_data_element, 'Timestamp', timestamp)

    if message_data.ref_to_message_id:
        _ = add_eb(message_data_element, 'RefToMessageId', message_data.ref_to_message_id)

    if message_data.time_to_live:
        time_to_live = to_timestamp(message_data.time_to_live)
        _ = add_eb(message_data_element, 'TimeToLive', time_to_live)

    if header.duplicate_elimination:
        _ = add_eb(out, 'DuplicateElimination')

    for description in header.descriptions:
        add_description(out, description.text, description.language)

    return out

# ################################################################################################################################

def add_ack_requested(soap_header:'any_', ack_requested:'AckRequested') -> 'None':
    element = add_header_block(soap_header, 'AckRequested')
    element.set(SOAP_Actor, ack_requested.actor)

    if ack_requested.signed:
        signed = 'true'
    else:
        signed = 'false'

    set_eb_attribute(element, 'signed', signed)

# ################################################################################################################################

def add_sync_reply(soap_header:'any_') -> 'None':
    element = add_header_block(soap_header, 'SyncReply')
    element.set(SOAP_Actor, Actor.SOAP_Next)

# ################################################################################################################################

def add_message_order(soap_header:'any_', message_order:'MessageOrder') -> 'None':
    element = add_header_block(soap_header, 'MessageOrder')
    sequence_number = str(message_order.sequence_number)

    sequence_element = add_eb(element, 'SequenceNumber', sequence_number)
    set_eb_attribute(sequence_element, 'status', message_order.status)

# ################################################################################################################################

def add_manifest(soap_body:'any_', manifest:'Manifest') -> 'None':
    element = add_body_element(soap_body, 'Manifest')

    for reference in manifest.references:

        reference_element = SubElement(element, _reference_tag, nsmap=_reference_nsmap)
        set_eb_attribute(reference_element, 'id', reference.reference_id)
        reference_element.set(_xlink_type, _xlink_type_simple)
        reference_element.set(_xlink_href, reference.href)

        if reference.role:
            reference_element.set(_xlink_role, reference.role)

        for schema in reference.schemas:
            schema_element = add_eb(reference_element, 'Schema')
            set_eb_attribute(schema_element, 'location', schema.location)
            set_eb_attribute(schema_element, 'version', schema.version)

        for description in reference.descriptions:
            add_description(reference_element, description.text, description.language)

# ################################################################################################################################
# ################################################################################################################################

def _parse_descriptions(element:'any_', where:'str') -> 'description_list':

    out:'description_list' = []

    for description_element in find_all_eb(element, 'Description'):

        if (language := description_element.get(XML_Lang)) is None:
            raise EbMS2Exception(ErrorCode.Inconsistent, 'Attribute `xml:lang` is missing', where)

        description = Description()
        description.text = require_text(description_element, where)
        description.language = language
        out.append(description)

    return out

# ################################################################################################################################

def parse_header_party(party_element:'any_', where:'str') -> 'HeaderParty':
    """ Parses an eb:From or an eb:To.
    """
    out = HeaderParty()
    out.party_ids = []

    for party_id_element in find_all_eb(party_element, 'PartyId'):

        value = require_text(party_id_element, where)

        if (id_type := get_eb_attribute(party_id_element, 'type')) is None:
            id_type = ''

        party_id = new_party_id(value, id_type)
        out.party_ids.append(party_id)

    if not out.party_ids:
        raise EbMS2Exception(ErrorCode.Inconsistent, 'Element `PartyId` is missing', where)

    out.role = optional_eb_text(party_element, 'Role', where)

    return out

# ################################################################################################################################

def _parse_party(element:'any_', name:'str') -> 'HeaderParty':

    where = location('MessageHeader', name)
    party_element = require_eb(element, name, where)

    out = parse_header_party(party_element, where)
    return out

# ################################################################################################################################

def parse_message_header(element:'any_') -> 'MessageHeader':
    """ Parses an eb:MessageHeader.
    """
    where = location('MessageHeader')
    check_extension(element, where, is_header=True)

    service_where = location('MessageHeader', 'Service')
    service = require_eb(element, 'Service', service_where)

    data_where = location('MessageHeader', 'MessageData')
    message_data_element = require_eb(element, 'MessageData', data_where)

    timestamp_where = location('MessageHeader', 'MessageData', 'Timestamp')
    timestamp = require_eb_text(message_data_element, 'Timestamp', timestamp_where)

    message_data = MessageData()
    message_data.message_id = require_eb_text(message_data_element, 'MessageId', data_where)
    message_data.timestamp = parse_timestamp(timestamp, timestamp_where)
    message_data.ref_to_message_id = optional_eb_text(message_data_element, 'RefToMessageId', data_where)

    if time_to_live := optional_eb_text(message_data_element, 'TimeToLive', data_where):
        time_to_live_where = location('MessageHeader', 'MessageData', 'TimeToLive')
        message_data.time_to_live = parse_timestamp(time_to_live, time_to_live_where)

    out = MessageHeader()
    out.from_party = _parse_party(element, 'From')
    out.to_party = _parse_party(element, 'To')
    out.cpa_id = require_eb_text(element, 'CPAId', where)
    out.conversation_id = require_eb_text(element, 'ConversationId', where)
    out.service = require_text(service, service_where)
    out.action = require_eb_text(element, 'Action', where)
    out.message_data = message_data
    out.descriptions = _parse_descriptions(element, where)

    if (service_type := get_eb_attribute(service, 'type')) is not None:
        out.service_type = service_type

    out.duplicate_elimination = find_eb(element, 'DuplicateElimination') is not None

    return out

# ################################################################################################################################

def parse_ack_requested(element:'any_') -> 'AckRequested':

    where = location('AckRequested')
    check_extension(element, where, is_header=True)

    signed = require_eb_attribute(element, 'signed', where)

    out = AckRequested()
    out.signed = parse_boolean(signed, where)

    if actor := element.get(SOAP_Actor):
        out.actor = actor

    return out

# ################################################################################################################################

def parse_sync_reply(element:'any_') -> 'None':
    """ Checks an eb:SyncReply, which says nothing beyond being present.
    """
    where = location('SyncReply')
    check_extension(element, where, is_header=True)

    actor = element.get(SOAP_Actor)

    if actor != Actor.SOAP_Next:
        raise EbMS2Exception(ErrorCode.Inconsistent, f'Attribute `SOAP:actor` is `{actor}`', where)

# ################################################################################################################################

def parse_message_order(element:'any_') -> 'MessageOrder':

    where = location('MessageOrder', 'SequenceNumber')
    check_extension(element, where, is_header=True)

    sequence_element = require_eb(element, 'SequenceNumber', where)
    sequence_text = require_text(sequence_element, where)

    if not sequence_text.isdigit():
        raise EbMS2Exception(ErrorCode.Inconsistent, f'Not a sequence number -> `{sequence_text}`', where)

    sequence_number = int(sequence_text)

    if sequence_number > Max_Sequence_Number:
        raise EbMS2Exception(ErrorCode.Inconsistent, f'Sequence number is above {Max_Sequence_Number}', where)

    out = MessageOrder()
    out.sequence_number = sequence_number

    if status := get_eb_attribute(sequence_element, 'status'):
        if status not in _sequence_statuses:
            raise EbMS2Exception(ErrorCode.Inconsistent, f'Unknown sequence status `{status}`', where)
        out.status = status

    return out

# ################################################################################################################################

def parse_manifest(element:'any_') -> 'Manifest':

    where = location('Manifest')
    check_extension(element, where, is_header=False)

    out = Manifest()

    for reference_element in find_all_eb(element, 'Reference'):

        reference_where = location('Manifest', 'Reference')

        if (href := reference_element.get(_xlink_href)) is None:
            raise EbMS2Exception(ErrorCode.Inconsistent, 'Attribute `xlink:href` is missing', reference_where)

        reference = ManifestReference()
        reference.href = href
        reference.descriptions = _parse_descriptions(reference_element, reference_where)

        if (reference_id := get_eb_attribute(reference_element, 'id')) is not None:
            reference.reference_id = reference_id

        if role := reference_element.get(_xlink_role):
            reference.role = role

        for schema_element in find_all_eb(reference_element, 'Schema'):
            schema = ManifestSchema()
            schema.location = require_eb_attribute(schema_element, 'location', reference_where)
            if (version := get_eb_attribute(schema_element, 'version')) is not None:
                schema.version = version
            reference.schemas.append(schema)

        out.references.append(reference)

    if not out.references:
        raise EbMS2Exception(ErrorCode.Inconsistent, 'Element `Reference` is missing', where)

    return out

# ################################################################################################################################
# ################################################################################################################################
