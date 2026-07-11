# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# lxml
from lxml import etree

# Zato
from zato.common.as4.common import Default, NS, Severity
from zato.common.crypto.api import CryptoManager
from zato.common.util.xml_.core import element_attribute, element_text, qname, utc_timestamp
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

# The fully qualified names of the SOAP elements built and read below.
_envelope_name        = qname(NS.SOAP, 'Envelope')
_header_name          = qname(NS.SOAP, 'Header')
_body_name            = qname(NS.SOAP, 'Body')
_must_understand_name = qname(NS.SOAP, 'mustUnderstand')

# The fully qualified names of the ebMS elements built and read below.
_messaging_name                 = qname(NS.EBMS, 'Messaging')
_user_message_name              = qname(NS.EBMS, 'UserMessage')
_signal_message_name            = qname(NS.EBMS, 'SignalMessage')
_message_information_name       = qname(NS.EBMS, 'MessageInfo')
_timestamp_name                 = qname(NS.EBMS, 'Timestamp')
_message_id_name                = qname(NS.EBMS, 'MessageId')
_ref_to_message_id_name         = qname(NS.EBMS, 'RefToMessageId')
_property_name                  = qname(NS.EBMS, 'Property')
_party_information_name         = qname(NS.EBMS, 'PartyInfo')
_from_name                      = qname(NS.EBMS, 'From')
_to_name                        = qname(NS.EBMS, 'To')
_party_id_name                  = qname(NS.EBMS, 'PartyId')
_role_name                      = qname(NS.EBMS, 'Role')
_collaboration_information_name = qname(NS.EBMS, 'CollaborationInfo')
_agreement_ref_name             = qname(NS.EBMS, 'AgreementRef')
_service_name                   = qname(NS.EBMS, 'Service')
_action_name                    = qname(NS.EBMS, 'Action')
_conversation_id_name           = qname(NS.EBMS, 'ConversationId')
_message_properties_name        = qname(NS.EBMS, 'MessageProperties')
_payload_information_name       = qname(NS.EBMS, 'PayloadInfo')
_part_information_name          = qname(NS.EBMS, 'PartInfo')
_part_properties_name           = qname(NS.EBMS, 'PartProperties')
_receipt_name                   = qname(NS.EBMS, 'Receipt')
_error_name                     = qname(NS.EBMS, 'Error')
_description_name               = qname(NS.EBMS, 'Description')
_error_detail_name              = qname(NS.EBMS, 'ErrorDetail')
_pull_request_name              = qname(NS.EBMS, 'PullRequest')

# The fully qualified names of the non-repudiation and signature elements.
_non_repudiation_name  = qname(NS.EBBP, 'NonRepudiationInformation')
_part_nr_information_name = qname(NS.EBBP, 'MessagePartNRInformation')
_reference_name        = qname(NS.DS, 'Reference')

# ################################################################################################################################
# ################################################################################################################################

def new_message_id(suffix:'str'='zato') -> 'str':
    """ Returns a fresh eb:MessageId, unique per RFC 2822 msg-id conventions.
    """
    unique = CryptoManager.generate_hex_string()

    out = f'{unique}@{suffix}'
    return out

# ################################################################################################################################
# ################################################################################################################################

def build_envelope() -> 'any_':
    """ Returns a new SOAP 1.2 envelope with an empty header and an empty body.
    The body carries a wsu:Id so it can be covered by the signature -
    in AS4 the body is always empty because payloads travel as MIME parts.
    """

    # Our response to produce
    out = etree.Element(_envelope_name, nsmap=_nsmap)

    _ = etree.SubElement(out, _header_name)

    body = etree.SubElement(out, _body_name)
    body.set(_wsu_id, Body_Element_ID)

    return out

# ################################################################################################################################

def _add_messaging(envelope:'any_') -> 'any_':
    """ Adds the eb:Messaging header block to an envelope and returns it.
    """
    header = envelope.find(_header_name)

    # Our response to produce
    out = etree.SubElement(header, _messaging_name)

    out.set(_wsu_id, Messaging_Element_ID)
    out.set(_must_understand_name, 'true')

    return out

# ################################################################################################################################

def _add_message_information(parent:'any_', message_id:'str', ref_to_message_id:'strnone'=None) -> 'None':
    """ Adds the eb:MessageInfo block that both user messages and signals begin with.
    """
    message_information = etree.SubElement(parent, _message_information_name)

    timestamp = etree.SubElement(message_information, _timestamp_name)
    timestamp.text = utc_timestamp()

    message_id_element = etree.SubElement(message_information, _message_id_name)
    message_id_element.text = message_id

    if ref_to_message_id:
        ref_element = etree.SubElement(message_information, _ref_to_message_id_name)
        ref_element.text = ref_to_message_id

# ################################################################################################################################

def _add_property(parent:'any_', name:'str', value:'str', type_:'strnone'=None) -> 'None':
    """ Adds one eb:Property element to a properties container.
    """
    property_element = etree.SubElement(parent, _property_name)
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

    # Our response to produce
    out = _add_messaging(envelope)

    user_message = etree.SubElement(out, _user_message_name)

    # The mpc attribute is only present when a non-default channel is used -
    # the Peppol profile requires omitting it for the default one.
    if pmode.mpc != Default.MPC:
        user_message.set('mpc', pmode.mpc)

    _add_message_information(user_message, message_id)

    # Who this message is from and for ..
    party_information = etree.SubElement(user_message, _party_information_name)

    from_element = etree.SubElement(party_information, _from_name)
    from_party_id = etree.SubElement(from_element, _party_id_name)
    from_party_id.text = pmode.initiator.party_id

    if pmode.initiator.party_type:
        from_party_id.set('type', pmode.initiator.party_type)

    from_role = etree.SubElement(from_element, _role_name)
    from_role.text = pmode.initiator.role

    to_element = etree.SubElement(party_information, _to_name)
    to_party_id = etree.SubElement(to_element, _party_id_name)
    to_party_id.text = pmode.responder.party_id

    if pmode.responder.party_type:
        to_party_id.set('type', pmode.responder.party_type)

    to_role = etree.SubElement(to_element, _role_name)
    to_role.text = pmode.responder.role

    # .. which business exchange it belongs to ..
    collaboration_information = etree.SubElement(user_message, _collaboration_information_name)

    if pmode.agreement:
        agreement_ref = etree.SubElement(collaboration_information, _agreement_ref_name)
        agreement_ref.text = pmode.agreement

        if pmode.agreement_type:
            agreement_ref.set('type', pmode.agreement_type)

    service = etree.SubElement(collaboration_information, _service_name)
    service.text = pmode.service

    if pmode.service_type:
        service.set('type', pmode.service_type)

    action = etree.SubElement(collaboration_information, _action_name)
    action.text = pmode.action

    conversation_id_element = etree.SubElement(collaboration_information, _conversation_id_name)
    conversation_id_element.text = conversation_id

    # .. the four-corner properties when the profile uses them ..
    has_original_sender = bool(pmode.original_sender)
    has_final_recipient = bool(pmode.final_recipient)

    if has_original_sender or has_final_recipient:
        message_properties = etree.SubElement(user_message, _message_properties_name)

        if pmode.original_sender:
            _add_property(message_properties, 'originalSender', pmode.original_sender, pmode.original_sender_type)

        if pmode.final_recipient:
            _add_property(message_properties, 'finalRecipient', pmode.final_recipient, pmode.final_recipient_type)

    # .. and finally, which MIME parts carry the payloads.
    payload_information = etree.SubElement(user_message, _payload_information_name)

    for part in parts:
        part_element = etree.SubElement(payload_information, _part_information_name)
        part_element.set('href', f'cid:{part.content_id}')

        part_properties = etree.SubElement(part_element, _part_properties_name)
        _add_property(part_properties, 'MimeType', part.mime_type)

        if part.character_set:
            _add_property(part_properties, 'CharacterSet', part.character_set)

        if part.compressed:
            _add_property(part_properties, 'CompressionType', part.content_type)

    return out

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

    # Our response to produce
    out = _add_messaging(envelope)

    signal = etree.SubElement(out, _signal_message_name)

    message_id = new_message_id()
    _add_message_information(signal, message_id, ref_to_message_id)

    receipt = etree.SubElement(signal, _receipt_name)
    non_repudiation = etree.SubElement(receipt, _non_repudiation_name)

    for reference in signed_references:
        part_information = etree.SubElement(non_repudiation, _part_nr_information_name)
        part_information.append(reference)

    return out

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

    # Our response to produce
    out = _add_messaging(envelope)

    signal = etree.SubElement(out, _signal_message_name)

    message_id = new_message_id()
    _add_message_information(signal, message_id, ref_to_message_id)

    error = etree.SubElement(signal, _error_name)
    error.set('errorCode', error_code)
    error.set('severity', severity)
    error.set('shortDescription', short_description)
    error.set('origin', 'ebMS')
    error.set('category', 'Communication')

    if ref_to_message_id:
        error.set('refToMessageInError', ref_to_message_id)

    description = etree.SubElement(error, _description_name)
    description.set(_xml_lang, 'en')
    description.text = short_description

    error_detail = etree.SubElement(error, _error_detail_name)
    error_detail.text = detail

    return out

# ################################################################################################################################

def build_pull_request(envelope:'any_', mpc:'str') -> 'any_':
    """ Adds an eb:Messaging block with a pull request signal for the given message partition channel.
    Returns the eb:Messaging element.
    """

    # Our response to produce
    out = _add_messaging(envelope)

    signal = etree.SubElement(out, _signal_message_name)

    message_id = new_message_id()
    _add_message_information(signal, message_id)

    pull_request = etree.SubElement(signal, _pull_request_name)
    pull_request.set('mpc', mpc)

    return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PartDetails:
    """ One eb:PartInfo entry parsed from an incoming user message.
    """
    href:       str = ''
    properties: 'strstrdict'

# ################################################################################################################################
# ################################################################################################################################

part_details_list = list[PartDetails]

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class UserMessageDetails:
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
    part_details: 'part_details_list'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ErrorDetails:
    """ One eb:Error parsed from an incoming signal.
    """
    error_code:        str = ''
    severity:          str = ''
    short_description: str = ''
    detail:            str = ''
    ref_to_message_id: 'strnone' = None

# ################################################################################################################################
# ################################################################################################################################

error_details_list = list[ErrorDetails]

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SignalDetails:
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
    errors: 'error_details_list'

# ################################################################################################################################
# ################################################################################################################################

signal_details_list = list[SignalDetails]
user_message_details_list = list[UserMessageDetails]

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class MessagingDetails:
    """ Everything parsed out of one eb:Messaging header block.
    """
    user_messages: 'user_message_details_list'
    signals:       'signal_details_list'

# ################################################################################################################################
# ################################################################################################################################

def _text_of(parent:'any_', tag:'str') -> 'str':
    """ Returns the text of a child element in the ebMS namespace, or an empty string if absent.
    """
    child_name = qname(NS.EBMS, tag)
    element = parent.find(child_name)

    if element is None:
        out = ''
    else:
        out = element_text(element)

    return out

# ################################################################################################################################

def _parse_user_message(user_message:'any_') -> 'UserMessageDetails':
    """ Extracts the fields of one eb:UserMessage element.
    """

    # Our response to produce
    out = UserMessageDetails()
    out.message_properties = {}
    out.part_details = []

    if mpc := user_message.get('mpc'):
        out.mpc = mpc

    message_information = user_message.find(_message_information_name)
    out.message_id = _text_of(message_information, 'MessageId')
    out.timestamp = _text_of(message_information, 'Timestamp')

    party_information = user_message.find(_party_information_name)

    from_element = party_information.find(_from_name)
    from_party_id = from_element.find(_party_id_name)
    out.from_party = element_text(from_party_id)
    out.from_party_type = from_party_id.get('type')
    out.from_role = _text_of(from_element, 'Role')

    to_element = party_information.find(_to_name)
    to_party_id = to_element.find(_party_id_name)
    out.to_party = element_text(to_party_id)
    out.to_party_type = to_party_id.get('type')
    out.to_role = _text_of(to_element, 'Role')

    collaboration_information = user_message.find(_collaboration_information_name)

    agreement_ref = collaboration_information.find(_agreement_ref_name)
    if agreement_ref is not None:
        out.agreement = agreement_ref.text

    service = collaboration_information.find(_service_name)
    out.service = element_text(service)
    out.service_type = service.get('type')
    out.action = _text_of(collaboration_information, 'Action')
    out.conversation_id = _text_of(collaboration_information, 'ConversationId')

    message_properties = user_message.find(_message_properties_name)
    if message_properties is not None:

        property_elements = message_properties.findall(_property_name)

        for property_element in property_elements:

            # A property without a name is not something the schema allows - skip it.
            name = property_element.get('name')
            if name is None:
                continue

            out.message_properties[name] = element_text(property_element)

    payload_information = user_message.find(_payload_information_name)
    if payload_information is not None:

        part_elements = payload_information.findall(_part_information_name)

        for part_element in part_elements:
            item = PartDetails()
            item.properties = {}
            item.href = element_attribute(part_element, 'href')

            part_properties = part_element.find(_part_properties_name)
            if part_properties is not None:

                property_elements = part_properties.findall(_property_name)

                for property_element in property_elements:

                    # A property without a name is not something the schema allows - skip it.
                    name = property_element.get('name')
                    if name is None:
                        continue

                    item.properties[name] = element_text(property_element)

            out.part_details.append(item)

    return out

# ################################################################################################################################

def _parse_signal(signal:'any_') -> 'SignalDetails':
    """ Extracts the fields of one eb:SignalMessage element.
    """

    # Our response to produce
    out = SignalDetails()
    out.receipt_references = []
    out.errors = []

    message_information = signal.find(_message_information_name)
    out.message_id = _text_of(message_information, 'MessageId')
    out.timestamp = _text_of(message_information, 'Timestamp')

    ref_element = message_information.find(_ref_to_message_id_name)
    if ref_element is not None:
        out.ref_to_message_id = ref_element.text

    receipt = signal.find(_receipt_name)
    if receipt is not None:
        out.is_receipt = True

        # Collect the echoed ds:Reference elements no matter how deeply
        # the ebbp structure nests them.
        for reference in receipt.iter(_reference_name):
            out.receipt_references.append(reference)

    pull_request = signal.find(_pull_request_name)
    if pull_request is not None:

        # A pull request without an explicit mpc pulls from the default channel.
        pull_mpc = pull_request.get('mpc')
        if pull_mpc is None:
            pull_mpc = Default.MPC

        out.pull_mpc = pull_mpc

    error_elements = signal.findall(_error_name)

    for error_element in error_elements:
        error_details = ErrorDetails()
        error_details.error_code = element_attribute(error_element, 'errorCode')
        error_details.severity = element_attribute(error_element, 'severity')
        error_details.short_description = element_attribute(error_element, 'shortDescription')
        error_details.ref_to_message_id = error_element.get('refToMessageInError')

        detail_element = error_element.find(_error_detail_name)
        if detail_element is not None:
            error_details.detail = element_text(detail_element)

        out.errors.append(error_details)

    return out

# ################################################################################################################################

def parse_messaging(envelope:'any_') -> 'MessagingDetails':
    """ Parses the eb:Messaging block of an incoming envelope into plain dataclasses.
    """

    # Our response to produce
    out = MessagingDetails()
    out.user_messages = []
    out.signals = []

    header = envelope.find(_header_name)
    messaging = header.find(_messaging_name)

    user_messages = messaging.findall(_user_message_name)

    for user_message in user_messages:
        parsed_user_message = _parse_user_message(user_message)
        out.user_messages.append(parsed_user_message)

    signals = messaging.findall(_signal_message_name)

    for signal in signals:
        parsed_signal = _parse_signal(signal)
        out.signals.append(parsed_signal)

    return out

# ################################################################################################################################
# ################################################################################################################################
