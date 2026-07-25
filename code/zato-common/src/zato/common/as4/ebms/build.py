# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# lxml
from lxml import etree

# Zato
from zato.common.as4.common import Default, Severity
from zato.common.as4.ebms.names import Action_Name, Agreement_Ref_Name, Body_Element_ID, Body_Name, \
    Collaboration_Information_Name, Conversation_Id_Name, Description_Name, Envelope_Name, Error_Detail_Name, \
    Error_Name, From_Name, Header_Name, Message_Id_Name, Message_Information_Name, Message_Properties_Name, \
    Messaging_Element_ID, Messaging_Name, Must_Understand_Name, Nsmap, Non_Repudiation_Name, Part_Information_Name, \
    Part_NR_Information_Name, Part_Properties_Name, Party_Id_Name, Party_Information_Name, Payload_Information_Name, \
    Property_Name, Pull_Request_Name, Receipt_Name, Ref_To_Message_Id_Name, Role_Name, Service_Name, \
    Signal_Message_Name, Timestamp_Name, To_Name, User_Message_Name, WSU_ID, XML_Lang
from zato.common.crypto.api import CryptoManager
from zato.common.util.xml_.core import utc_timestamp

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as4.pmode import PMode
    from zato.common.typing_ import any_, anylist, strnone
    from zato.common.util.xml_.mime_ import part_list
    any_ = any_
    anylist = anylist
    part_list = part_list
    PMode = PMode
    strnone = strnone

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
    out = etree.Element(Envelope_Name, nsmap=Nsmap)

    _ = etree.SubElement(out, Header_Name)

    body = etree.SubElement(out, Body_Name)
    body.set(WSU_ID, Body_Element_ID)

    return out

# ################################################################################################################################

def _add_messaging(envelope:'any_') -> 'any_':
    """ Adds the eb:Messaging header block to an envelope and returns it.
    """
    header = envelope.find(Header_Name)

    # Our response to produce
    out = etree.SubElement(header, Messaging_Name)

    out.set(WSU_ID, Messaging_Element_ID)
    out.set(Must_Understand_Name, 'true')

    return out

# ################################################################################################################################

def _add_message_information(parent:'any_', message_id:'str', ref_to_message_id:'strnone'=None) -> 'None':
    """ Adds the eb:MessageInfo block that both user messages and signals begin with.
    """
    message_information = etree.SubElement(parent, Message_Information_Name)

    timestamp = etree.SubElement(message_information, Timestamp_Name)
    timestamp.text = utc_timestamp()

    message_id_element = etree.SubElement(message_information, Message_Id_Name)
    message_id_element.text = message_id

    if ref_to_message_id:
        ref_element = etree.SubElement(message_information, Ref_To_Message_Id_Name)
        ref_element.text = ref_to_message_id

# ################################################################################################################################

def _add_property(parent:'any_', name:'str', value:'str', type_:'strnone'=None) -> 'None':
    """ Adds one eb:Property element to a properties container.
    """
    property_element = etree.SubElement(parent, Property_Name)
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

    user_message = etree.SubElement(out, User_Message_Name)

    # The mpc attribute is only present when a non-default channel is used -
    # the Peppol profile requires omitting it for the default one.
    if pmode.mpc != Default.MPC:
        user_message.set('mpc', pmode.mpc)

    _add_message_information(user_message, message_id)

    # Who this message is from and for ..
    party_information = etree.SubElement(user_message, Party_Information_Name)

    from_element = etree.SubElement(party_information, From_Name)
    from_party_id = etree.SubElement(from_element, Party_Id_Name)
    from_party_id.text = pmode.initiator.party_id

    if pmode.initiator.party_type:
        from_party_id.set('type', pmode.initiator.party_type)

    from_role = etree.SubElement(from_element, Role_Name)
    from_role.text = pmode.initiator.role

    to_element = etree.SubElement(party_information, To_Name)
    to_party_id = etree.SubElement(to_element, Party_Id_Name)
    to_party_id.text = pmode.responder.party_id

    if pmode.responder.party_type:
        to_party_id.set('type', pmode.responder.party_type)

    to_role = etree.SubElement(to_element, Role_Name)
    to_role.text = pmode.responder.role

    # .. which business exchange it belongs to ..
    collaboration_information = etree.SubElement(user_message, Collaboration_Information_Name)

    if pmode.agreement:
        agreement_ref = etree.SubElement(collaboration_information, Agreement_Ref_Name)
        agreement_ref.text = pmode.agreement

        if pmode.agreement_type:
            agreement_ref.set('type', pmode.agreement_type)

    service = etree.SubElement(collaboration_information, Service_Name)
    service.text = pmode.service

    if pmode.service_type:
        service.set('type', pmode.service_type)

    action = etree.SubElement(collaboration_information, Action_Name)
    action.text = pmode.action

    conversation_id_element = etree.SubElement(collaboration_information, Conversation_Id_Name)
    conversation_id_element.text = conversation_id

    # .. the four-corner properties when the profile uses them ..
    has_original_sender = bool(pmode.original_sender)
    has_final_recipient = bool(pmode.final_recipient)

    if has_original_sender or has_final_recipient:
        message_properties = etree.SubElement(user_message, Message_Properties_Name)

        if pmode.original_sender:
            _add_property(message_properties, 'originalSender', pmode.original_sender, pmode.original_sender_type)

        if pmode.final_recipient:
            _add_property(message_properties, 'finalRecipient', pmode.final_recipient, pmode.final_recipient_type)

    # .. and finally, which MIME parts carry the payloads.
    payload_information = etree.SubElement(user_message, Payload_Information_Name)

    for part in parts:
        part_element = etree.SubElement(payload_information, Part_Information_Name)
        part_element.set('href', f'cid:{part.content_id}')

        part_properties = etree.SubElement(part_element, Part_Properties_Name)
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

    signal = etree.SubElement(out, Signal_Message_Name)

    message_id = new_message_id()
    _add_message_information(signal, message_id, ref_to_message_id)

    receipt = etree.SubElement(signal, Receipt_Name)
    non_repudiation = etree.SubElement(receipt, Non_Repudiation_Name)

    for reference in signed_references:
        part_information = etree.SubElement(non_repudiation, Part_NR_Information_Name)
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

    signal = etree.SubElement(out, Signal_Message_Name)

    message_id = new_message_id()
    _add_message_information(signal, message_id, ref_to_message_id)

    error = etree.SubElement(signal, Error_Name)
    error.set('errorCode', error_code)
    error.set('severity', severity)
    error.set('shortDescription', short_description)
    error.set('origin', 'ebMS')
    error.set('category', 'Communication')

    if ref_to_message_id:
        error.set('refToMessageInError', ref_to_message_id)

    description = etree.SubElement(error, Description_Name)
    description.set(XML_Lang, 'en')
    description.text = short_description

    error_detail = etree.SubElement(error, Error_Detail_Name)
    error_detail.text = detail

    return out

# ################################################################################################################################

def build_pull_request(envelope:'any_', mpc:'str') -> 'any_':
    """ Adds an eb:Messaging block with a pull request signal for the given message partition channel.
    Returns the eb:Messaging element.
    """

    # Our response to produce
    out = _add_messaging(envelope)

    signal = etree.SubElement(out, Signal_Message_Name)

    message_id = new_message_id()
    _add_message_information(signal, message_id)

    pull_request = etree.SubElement(signal, Pull_Request_Name)
    pull_request.set('mpc', mpc)

    return out

# ################################################################################################################################
# ################################################################################################################################
