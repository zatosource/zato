# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.as4.common import AS4ProtocolException, Default, EbMSError, NS
from zato.common.as4.ebms.names import Agreement_Ref_Name, Body_Name, Collaboration_Information_Name, \
    Error_Detail_Name, Error_Name, From_Name, Header_Name, Message_Information_Name, Message_Properties_Name, \
    Messaging_Name, Part_Information_Name, Part_Properties_Name, Party_Id_Name, Party_Information_Name, \
    Payload_Information_Name, Property_Name, Pull_Request_Name, Receipt_Name, Reference_Name, Ref_To_Message_Id_Name, \
    Service_Name, Signal_Message_Name, To_Name, User_Message_Name
from zato.common.util.xml_.core import element_attribute, element_text, qname

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, strnone, strstrdict
    any_ = any_
    anylist = anylist
    strnone = strnone
    strstrdict = strstrdict

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

def _require(parent:'any_', element_name:'str', description:'str') -> 'any_':
    """ Returns a child element that the ebMS 3.0 schema makes mandatory, or raises EBMS:0009,
    which is the error code the specification assigns to a malformed header.
    """
    out = parent.find(element_name)

    if out is None:
        raise AS4ProtocolException(EbMSError.Invalid_Header, f'Message has no {description}')

    return out

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

    message_information = _require(user_message, Message_Information_Name, 'eb:MessageInfo')
    out.message_id = _text_of(message_information, 'MessageId')
    out.timestamp = _text_of(message_information, 'Timestamp')

    party_information = _require(user_message, Party_Information_Name, 'eb:PartyInfo')

    from_element = _require(party_information, From_Name, 'eb:From')
    from_party_id = _require(from_element, Party_Id_Name, 'eb:From/eb:PartyId')
    out.from_party = element_text(from_party_id)
    out.from_party_type = from_party_id.get('type')
    out.from_role = _text_of(from_element, 'Role')

    to_element = _require(party_information, To_Name, 'eb:To')
    to_party_id = _require(to_element, Party_Id_Name, 'eb:To/eb:PartyId')
    out.to_party = element_text(to_party_id)
    out.to_party_type = to_party_id.get('type')
    out.to_role = _text_of(to_element, 'Role')

    collaboration_information = _require(user_message, Collaboration_Information_Name, 'eb:CollaborationInfo')

    agreement_ref = collaboration_information.find(Agreement_Ref_Name)
    if agreement_ref is not None:
        out.agreement = agreement_ref.text

    service = _require(collaboration_information, Service_Name, 'eb:Service')
    out.service = element_text(service)
    out.service_type = service.get('type')
    out.action = _text_of(collaboration_information, 'Action')
    out.conversation_id = _text_of(collaboration_information, 'ConversationId')

    message_properties = user_message.find(Message_Properties_Name)
    if message_properties is not None:

        property_elements = message_properties.findall(Property_Name)

        for property_element in property_elements:

            # A property without a name is not something the schema allows - skip it.
            name = property_element.get('name')
            if name is None:
                continue

            out.message_properties[name] = element_text(property_element)

    payload_information = user_message.find(Payload_Information_Name)
    if payload_information is not None:

        part_elements = payload_information.findall(Part_Information_Name)

        for part_element in part_elements:
            item = PartDetails()
            item.properties = {}
            item.href = element_attribute(part_element, 'href')

            part_properties = part_element.find(Part_Properties_Name)
            if part_properties is not None:

                property_elements = part_properties.findall(Property_Name)

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

    message_information = _require(signal, Message_Information_Name, 'eb:MessageInfo')
    out.message_id = _text_of(message_information, 'MessageId')
    out.timestamp = _text_of(message_information, 'Timestamp')

    ref_element = message_information.find(Ref_To_Message_Id_Name)
    if ref_element is not None:
        out.ref_to_message_id = ref_element.text

    receipt = signal.find(Receipt_Name)
    if receipt is not None:
        out.is_receipt = True

        # Collect the echoed ds:Reference elements no matter how deeply
        # the ebbp structure nests them.
        for reference in receipt.iter(Reference_Name):
            out.receipt_references.append(reference)

    pull_request = signal.find(Pull_Request_Name)
    if pull_request is not None:

        # A pull request without an explicit mpc pulls from the default channel.
        pull_mpc = pull_request.get('mpc')
        if pull_mpc is None:
            pull_mpc = Default.MPC

        out.pull_mpc = pull_mpc

    error_elements = signal.findall(Error_Name)

    for error_element in error_elements:
        error_details = ErrorDetails()
        error_details.error_code = element_attribute(error_element, 'errorCode')
        error_details.severity = element_attribute(error_element, 'severity')
        error_details.short_description = element_attribute(error_element, 'shortDescription')
        error_details.ref_to_message_id = error_element.get('refToMessageInError')

        detail_element = error_element.find(Error_Detail_Name)
        if detail_element is not None:
            error_details.detail = element_text(detail_element)

        out.errors.append(error_details)

    return out

# ################################################################################################################################

def find_messaging(envelope:'any_') -> 'any_':
    """ Returns the eb:Messaging header block of an envelope. Every caller that needs it comes here,
    so that they all resolve to the same element and can compare it for identity.
    """
    header = _require(envelope, Header_Name, 'SOAP Header')

    out = _require(header, Messaging_Name, 'eb:Messaging header block')
    return out

# ################################################################################################################################

def find_body(envelope:'any_') -> 'any_':
    """ Returns the SOAP Body of an envelope. The one place that locates it, as with find_messaging.
    """
    out = _require(envelope, Body_Name, 'SOAP Body')
    return out

# ################################################################################################################################

def parse_messaging(envelope:'any_') -> 'MessagingDetails':
    """ Parses the eb:Messaging block of an incoming envelope into plain dataclasses.
    """

    # Our response to produce
    out = MessagingDetails()
    out.user_messages = []
    out.signals = []

    messaging = find_messaging(envelope)

    user_messages = messaging.findall(User_Message_Name)

    # The AS4 profile allows exactly one user message per header block.
    user_message_count = len(user_messages)

    if user_message_count > 1:
        raise AS4ProtocolException(
            EbMSError.Value_Not_Recognized, f'Message carries {user_message_count} eb:UserMessage elements, expected one')

    for user_message in user_messages:
        parsed_user_message = _parse_user_message(user_message)
        out.user_messages.append(parsed_user_message)

    signals = messaging.findall(Signal_Message_Name)

    for signal in signals:
        parsed_signal = _parse_signal(signal)
        out.signals.append(parsed_signal)

    return out

# ################################################################################################################################
# ################################################################################################################################
