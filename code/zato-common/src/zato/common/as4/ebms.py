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
from zato.common.as4.common import Default, NS, Severity
from zato.common.util.xml_.core import qname, utc_timestamp
from zato.common.util.xml_.mime_ import part_list

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as4.pmode import PMode
    from zato.common.typing_ import any_, anylist, strnone, strstrdict
    any_ = any_
    anylist = anylist
    strnone = strnone
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

# Fixed element ids used in signature references.
Messaging_Element_ID = '_zato-as4-messaging'
Body_Element_ID      = '_zato-as4-body'

_nsmap = {
    's12':  NS.SOAP,
    'eb':   NS.EBMS,
    'wsu':  NS.WSU,
    'ebbp': NS.EBBP,
    'ds':   NS.DS,
}

_wsu_id = f'{{{NS.WSU}}}Id'
_xml_lang = '{http://www.w3.org/XML/1998/namespace}lang'

# ################################################################################################################################
# ################################################################################################################################

def new_message_id(suffix:'str'='zato') -> 'str':
    """ Returns a fresh eb:MessageId, unique per RFC 2822 msg-id conventions.
    """
    out = f'{uuid4()}@{suffix}'
    return out

# ################################################################################################################################
# ################################################################################################################################

def build_envelope() -> 'any_':
    """ Returns a new SOAP 1.2 envelope with an empty header and an empty body.
    The body carries a wsu:Id so it can be covered by the signature -
    in AS4 the body is always empty because payloads travel as MIME parts.
    """
    envelope = etree.Element(qname(NS.SOAP, 'Envelope'), nsmap=_nsmap)
    _ = etree.SubElement(envelope, qname(NS.SOAP, 'Header'))

    body = etree.SubElement(envelope, qname(NS.SOAP, 'Body'))
    body.set(_wsu_id, Body_Element_ID)

    return envelope

# ################################################################################################################################

def _add_messaging(envelope:'any_') -> 'any_':
    """ Adds the eb:Messaging header block to an envelope and returns it.
    """
    header = envelope.find(qname(NS.SOAP, 'Header'))

    messaging = etree.SubElement(header, qname(NS.EBMS, 'Messaging'))
    messaging.set(_wsu_id, Messaging_Element_ID)
    messaging.set(qname(NS.SOAP, 'mustUnderstand'), 'true')

    return messaging

# ################################################################################################################################

def _add_message_info(parent:'any_', message_id:'str', ref_to_message_id:'strnone'=None) -> 'None':
    """ Adds the eb:MessageInfo block that both user messages and signals begin with.
    """
    message_info = etree.SubElement(parent, qname(NS.EBMS, 'MessageInfo'))

    timestamp = etree.SubElement(message_info, qname(NS.EBMS, 'Timestamp'))
    timestamp.text = utc_timestamp()

    message_id_element = etree.SubElement(message_info, qname(NS.EBMS, 'MessageId'))
    message_id_element.text = message_id

    if ref_to_message_id:
        ref_element = etree.SubElement(message_info, qname(NS.EBMS, 'RefToMessageId'))
        ref_element.text = ref_to_message_id

# ################################################################################################################################

def _add_property(parent:'any_', name:'str', value:'str', type_:'strnone'=None) -> 'None':
    """ Adds one eb:Property element to a properties container.
    """
    property_element = etree.SubElement(parent, qname(NS.EBMS, 'Property'))
    property_element.set('name', name)
    property_element.text = value

    if type_:
        property_element.set('type', type_)

# ################################################################################################################################

def build_user_message(
    envelope:'any_',
    pmode:'PMode',
    parts:'part_list',
    message_id:'str',
    conversation_id:'str',
    ) -> 'any_':
    """ Adds an eb:Messaging block with one eb:UserMessage describing the given payload parts.
    Returns the eb:Messaging element so the caller can pass it to the signing layer.
    """
    messaging = _add_messaging(envelope)
    user_message = etree.SubElement(messaging, qname(NS.EBMS, 'UserMessage'))

    # The mpc attribute is only present when a non-default channel is used -
    # the Peppol profile requires omitting it for the default one.
    if pmode.mpc != Default.MPC:
        user_message.set('mpc', pmode.mpc)

    _add_message_info(user_message, message_id)

    # Who this message is from and for ..
    party_info = etree.SubElement(user_message, qname(NS.EBMS, 'PartyInfo'))

    from_element = etree.SubElement(party_info, qname(NS.EBMS, 'From'))
    from_party_id = etree.SubElement(from_element, qname(NS.EBMS, 'PartyId'))
    from_party_id.text = pmode.initiator.party_id
    if pmode.initiator.party_type:
        from_party_id.set('type', pmode.initiator.party_type)
    from_role = etree.SubElement(from_element, qname(NS.EBMS, 'Role'))
    from_role.text = pmode.initiator.role

    to_element = etree.SubElement(party_info, qname(NS.EBMS, 'To'))
    to_party_id = etree.SubElement(to_element, qname(NS.EBMS, 'PartyId'))
    to_party_id.text = pmode.responder.party_id
    if pmode.responder.party_type:
        to_party_id.set('type', pmode.responder.party_type)
    to_role = etree.SubElement(to_element, qname(NS.EBMS, 'Role'))
    to_role.text = pmode.responder.role

    # .. which business exchange it belongs to ..
    collaboration_info = etree.SubElement(user_message, qname(NS.EBMS, 'CollaborationInfo'))

    if pmode.agreement:
        agreement_ref = etree.SubElement(collaboration_info, qname(NS.EBMS, 'AgreementRef'))
        agreement_ref.text = pmode.agreement
        if pmode.agreement_type:
            agreement_ref.set('type', pmode.agreement_type)

    service = etree.SubElement(collaboration_info, qname(NS.EBMS, 'Service'))
    service.text = pmode.service
    if pmode.service_type:
        service.set('type', pmode.service_type)

    action = etree.SubElement(collaboration_info, qname(NS.EBMS, 'Action'))
    action.text = pmode.action

    conversation_id_element = etree.SubElement(collaboration_info, qname(NS.EBMS, 'ConversationId'))
    conversation_id_element.text = conversation_id

    # .. the four-corner properties when the profile uses them ..
    has_original_sender = bool(pmode.original_sender)
    has_final_recipient = bool(pmode.final_recipient)

    if has_original_sender or has_final_recipient:
        message_properties = etree.SubElement(user_message, qname(NS.EBMS, 'MessageProperties'))

        if pmode.original_sender:
            _add_property(message_properties, 'originalSender', pmode.original_sender, pmode.original_sender_type)

        if pmode.final_recipient:
            _add_property(message_properties, 'finalRecipient', pmode.final_recipient, pmode.final_recipient_type)

    # .. and finally, which MIME parts carry the payloads.
    payload_info = etree.SubElement(user_message, qname(NS.EBMS, 'PayloadInfo'))

    for part in parts:
        part_info = etree.SubElement(payload_info, qname(NS.EBMS, 'PartInfo'))
        part_info.set('href', f'cid:{part.content_id}')

        part_properties = etree.SubElement(part_info, qname(NS.EBMS, 'PartProperties'))
        _add_property(part_properties, 'MimeType', part.mime_type)

        if part.character_set:
            _add_property(part_properties, 'CharacterSet', part.character_set)

        if part.compressed:
            _add_property(part_properties, 'CompressionType', part.content_type)

    return messaging

# ################################################################################################################################

def build_receipt(
    envelope:'any_',
    ref_to_message_id:'str',
    signed_references:'anylist',
    ) -> 'any_':
    """ Adds an eb:Messaging block with a receipt signal for the given message.
    When the original message was signed, its ds:Reference elements are echoed back
    inside ebbp:NonRepudiationInformation, which is what makes the receipt non-repudiable.
    Returns the eb:Messaging element.
    """
    messaging = _add_messaging(envelope)
    signal = etree.SubElement(messaging, qname(NS.EBMS, 'SignalMessage'))

    _add_message_info(signal, new_message_id(), ref_to_message_id)

    receipt = etree.SubElement(signal, qname(NS.EBMS, 'Receipt'))
    non_repudiation = etree.SubElement(receipt, qname(NS.EBBP, 'NonRepudiationInformation'))

    for reference in signed_references:
        part_information = etree.SubElement(non_repudiation, qname(NS.EBBP, 'MessagePartNRInformation'))
        part_information.append(reference)

    return messaging

# ################################################################################################################################

def build_error(
    envelope:'any_',
    ref_to_message_id:'strnone',
    error_code:'str',
    short_description:'str',
    detail:'str',
    severity:'str'=Severity.Failure,
    ) -> 'any_':
    """ Adds an eb:Messaging block with an error signal. Returns the eb:Messaging element.
    """
    messaging = _add_messaging(envelope)
    signal = etree.SubElement(messaging, qname(NS.EBMS, 'SignalMessage'))

    _add_message_info(signal, new_message_id(), ref_to_message_id)

    error = etree.SubElement(signal, qname(NS.EBMS, 'Error'))
    error.set('errorCode', error_code)
    error.set('severity', severity)
    error.set('shortDescription', short_description)
    error.set('origin', 'ebMS')
    error.set('category', 'Communication')

    if ref_to_message_id:
        error.set('refToMessageInError', ref_to_message_id)

    description = etree.SubElement(error, qname(NS.EBMS, 'Description'))
    description.set(_xml_lang, 'en')
    description.text = short_description

    error_detail = etree.SubElement(error, qname(NS.EBMS, 'ErrorDetail'))
    error_detail.text = detail

    return messaging

# ################################################################################################################################

def build_pull_request(envelope:'any_', mpc:'str') -> 'any_':
    """ Adds an eb:Messaging block with a pull request signal for the given message partition channel.
    Returns the eb:Messaging element.
    """
    messaging = _add_messaging(envelope)
    signal = etree.SubElement(messaging, qname(NS.EBMS, 'SignalMessage'))

    _add_message_info(signal, new_message_id())

    pull_request = etree.SubElement(signal, qname(NS.EBMS, 'PullRequest'))
    pull_request.set('mpc', mpc)

    return messaging

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PartInfo:
    """ One eb:PartInfo entry parsed from an incoming user message.
    """
    href:       str = ''
    properties: 'strstrdict'

# ################################################################################################################################
# ################################################################################################################################

part_info_list = list[PartInfo]

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class UserMessageInfo:
    """ The relevant contents of one incoming eb:UserMessage.
    """
    message_id:      str = ''
    timestamp:       str = ''
    conversation_id: str = ''
    mpc:             str = Default.MPC

    from_party:      str = ''
    from_party_type: 'strnone' = None
    from_role:       str = ''
    to_party:        str = ''
    to_party_type:   'strnone' = None
    to_role:         str = ''

    agreement:    'strnone' = None
    service:      str = ''
    service_type: 'strnone' = None
    action:       str = ''

    message_properties: 'strstrdict'
    part_infos: 'part_info_list'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ErrorInfo:
    """ One eb:Error parsed from an incoming signal.
    """
    error_code:        str = ''
    severity:          str = ''
    short_description: str = ''
    detail:            str = ''
    ref_to_message_id: 'strnone' = None

# ################################################################################################################################
# ################################################################################################################################

error_info_list = list[ErrorInfo]

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SignalInfo:
    """ The relevant contents of one incoming eb:SignalMessage.
    """
    message_id:        str = ''
    timestamp:         str = ''
    ref_to_message_id: 'strnone' = None

    # Present when the signal is a receipt - the ds:Reference elements
    # from the ebbp non-repudiation block, as parsed lxml elements.
    is_receipt: bool = False
    receipt_references: 'anylist'

    # Present when the signal is a pull request.
    pull_mpc: 'strnone' = None

    # Present when the signal carries errors.
    errors: 'error_info_list'

# ################################################################################################################################
# ################################################################################################################################

signal_info_list = list[SignalInfo]
user_message_info_list = list[UserMessageInfo]

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class MessagingInfo:
    """ Everything parsed out of one eb:Messaging header block.
    """
    user_messages: 'user_message_info_list'
    signals:       'signal_info_list'

# ################################################################################################################################
# ################################################################################################################################

def _text_of(parent:'any_', tag:'str') -> 'str':
    """ Returns the text of a child element in the ebMS namespace, or an empty string if absent.
    """
    element = parent.find(qname(NS.EBMS, tag))

    if element is None:
        out = ''
    else:
        out = element.text or ''

    return out

# ################################################################################################################################

def _parse_user_message(user_message:'any_') -> 'UserMessageInfo':
    """ Extracts the fields of one eb:UserMessage element.
    """
    out = UserMessageInfo()
    out.message_properties = {}
    out.part_infos = []

    if mpc := user_message.get('mpc'):
        out.mpc = mpc

    message_info = user_message.find(qname(NS.EBMS, 'MessageInfo'))
    out.message_id = _text_of(message_info, 'MessageId')
    out.timestamp = _text_of(message_info, 'Timestamp')

    party_info = user_message.find(qname(NS.EBMS, 'PartyInfo'))

    from_element = party_info.find(qname(NS.EBMS, 'From'))
    from_party_id = from_element.find(qname(NS.EBMS, 'PartyId'))
    out.from_party = from_party_id.text or ''
    out.from_party_type = from_party_id.get('type')
    out.from_role = _text_of(from_element, 'Role')

    to_element = party_info.find(qname(NS.EBMS, 'To'))
    to_party_id = to_element.find(qname(NS.EBMS, 'PartyId'))
    out.to_party = to_party_id.text or ''
    out.to_party_type = to_party_id.get('type')
    out.to_role = _text_of(to_element, 'Role')

    collaboration_info = user_message.find(qname(NS.EBMS, 'CollaborationInfo'))

    agreement_ref = collaboration_info.find(qname(NS.EBMS, 'AgreementRef'))
    if agreement_ref is not None:
        out.agreement = agreement_ref.text

    service = collaboration_info.find(qname(NS.EBMS, 'Service'))
    out.service = service.text or ''
    out.service_type = service.get('type')
    out.action = _text_of(collaboration_info, 'Action')
    out.conversation_id = _text_of(collaboration_info, 'ConversationId')

    message_properties = user_message.find(qname(NS.EBMS, 'MessageProperties'))
    if message_properties is not None:
        for property_element in message_properties.findall(qname(NS.EBMS, 'Property')):
            out.message_properties[property_element.get('name')] = property_element.text or ''

    payload_info = user_message.find(qname(NS.EBMS, 'PayloadInfo'))
    if payload_info is not None:
        for part_info_element in payload_info.findall(qname(NS.EBMS, 'PartInfo')):
            part_info = PartInfo()
            part_info.properties = {}
            part_info.href = part_info_element.get('href') or ''

            part_properties = part_info_element.find(qname(NS.EBMS, 'PartProperties'))
            if part_properties is not None:
                for property_element in part_properties.findall(qname(NS.EBMS, 'Property')):
                    part_info.properties[property_element.get('name')] = property_element.text or ''

            out.part_infos.append(part_info)

    return out

# ################################################################################################################################

def _parse_signal(signal:'any_') -> 'SignalInfo':
    """ Extracts the fields of one eb:SignalMessage element.
    """
    out = SignalInfo()
    out.receipt_references = []
    out.errors = []

    message_info = signal.find(qname(NS.EBMS, 'MessageInfo'))
    out.message_id = _text_of(message_info, 'MessageId')
    out.timestamp = _text_of(message_info, 'Timestamp')

    ref_element = message_info.find(qname(NS.EBMS, 'RefToMessageId'))
    if ref_element is not None:
        out.ref_to_message_id = ref_element.text

    receipt = signal.find(qname(NS.EBMS, 'Receipt'))
    if receipt is not None:
        out.is_receipt = True

        # Collect the echoed ds:Reference elements no matter how deeply
        # the ebbp structure nests them.
        for reference in receipt.iter(qname(NS.DS, 'Reference')):
            out.receipt_references.append(reference)

    pull_request = signal.find(qname(NS.EBMS, 'PullRequest'))
    if pull_request is not None:
        out.pull_mpc = pull_request.get('mpc') or Default.MPC

    for error_element in signal.findall(qname(NS.EBMS, 'Error')):
        error_info = ErrorInfo()
        error_info.error_code = error_element.get('errorCode') or ''
        error_info.severity = error_element.get('severity') or ''
        error_info.short_description = error_element.get('shortDescription') or ''
        error_info.ref_to_message_id = error_element.get('refToMessageInError')

        detail_element = error_element.find(qname(NS.EBMS, 'ErrorDetail'))
        if detail_element is not None:
            error_info.detail = detail_element.text or ''

        out.errors.append(error_info)

    return out

# ################################################################################################################################

def parse_messaging(envelope:'any_') -> 'MessagingInfo':
    """ Parses the eb:Messaging block of an incoming envelope into plain dataclasses.
    """
    out = MessagingInfo()
    out.user_messages = []
    out.signals = []

    header = envelope.find(qname(NS.SOAP, 'Header'))
    messaging = header.find(qname(NS.EBMS, 'Messaging'))

    for user_message in messaging.findall(qname(NS.EBMS, 'UserMessage')):
        parsed_user_message = _parse_user_message(user_message)
        out.user_messages.append(parsed_user_message)

    for signal in messaging.findall(qname(NS.EBMS, 'SignalMessage')):
        parsed_signal = _parse_signal(signal)
        out.signals.append(parsed_signal)

    return out

# ################################################################################################################################
# ################################################################################################################################
