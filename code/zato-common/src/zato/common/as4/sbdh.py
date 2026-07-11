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
from zato.common.as4.common import AS4ProtocolException, EbMSError, NS
from zato.common.util.xml_.core import element_attribute, element_text, qname, utc_timestamp

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
sbdh_parse_result = tuple['SBDHDetails', 'any_']

# ################################################################################################################################
# ################################################################################################################################

# The header version the SBDH specification defines - there has only ever been one.
_header_version = '1.0'

# The scope type names Peppol uses in the business scope.
_scope_type_document = 'DOCUMENTID'
_scope_type_process  = 'PROCESSID'

_nsmap = {
    'sbdh': NS.SBDH,
}

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SBDHDetails:
    """ The identifiers carried in one Standard Business Document Header.
    """
    sender_id:     str = ''
    sender_scheme: str = ''

    receiver_id:     str = ''
    receiver_scheme: str = ''

    document_type: str = ''
    process_id:    str = ''

    instance_identifier: str = ''

# ################################################################################################################################
# ################################################################################################################################

def build_sbdh(
    sender_scheme:'str',
    sender_id:'str',
    receiver_scheme:'str',
    receiver_id:'str',
    document_type:'str',
    process_id:'str',
    process_scheme:'str',
    document_standard:'str',
    document_type_version:'str',
    instance_identifier:'str',
    business_document:'any_',
    ) -> 'bytes':
    """ Wraps a business document in a StandardBusinessDocument envelope, the way
    Peppol requires every payload to travel. Returns the serialized document.
    """
    document_name = qname(NS.SBDH, 'StandardBusinessDocument')
    header_name = qname(NS.SBDH, 'StandardBusinessDocumentHeader')
    header_version_name = qname(NS.SBDH, 'HeaderVersion')
    sender_name = qname(NS.SBDH, 'Sender')
    receiver_name = qname(NS.SBDH, 'Receiver')
    identifier_name = qname(NS.SBDH, 'Identifier')
    document_identification_name = qname(NS.SBDH, 'DocumentIdentification')
    standard_name = qname(NS.SBDH, 'Standard')
    type_version_name = qname(NS.SBDH, 'TypeVersion')
    instance_identifier_name = qname(NS.SBDH, 'InstanceIdentifier')
    type_name = qname(NS.SBDH, 'Type')
    creation_name = qname(NS.SBDH, 'CreationDateAndTime')
    business_scope_name = qname(NS.SBDH, 'BusinessScope')
    scope_name = qname(NS.SBDH, 'Scope')

    root = etree.Element(document_name, nsmap=_nsmap)
    header = etree.SubElement(root, header_name)

    version = etree.SubElement(header, header_version_name)
    version.text = _header_version

    # Who sends this document ..
    sender = etree.SubElement(header, sender_name)
    sender_identifier = etree.SubElement(sender, identifier_name)
    sender_identifier.set('Authority', sender_scheme)
    sender_identifier.text = sender_id

    # .. who is to receive it ..
    receiver = etree.SubElement(header, receiver_name)
    receiver_identifier = etree.SubElement(receiver, identifier_name)
    receiver_identifier.set('Authority', receiver_scheme)
    receiver_identifier.text = receiver_id

    # .. what kind of document it is ..
    document_identification = etree.SubElement(header, document_identification_name)

    standard = etree.SubElement(document_identification, standard_name)
    standard.text = document_standard

    type_version = etree.SubElement(document_identification, type_version_name)
    type_version.text = document_type_version

    instance = etree.SubElement(document_identification, instance_identifier_name)
    instance.text = instance_identifier

    # The document type is the local part of the business document's root tag.
    tag_parts = business_document.tag.split('}')
    local_name = tag_parts[-1]

    type_element = etree.SubElement(document_identification, type_name)
    type_element.text = local_name

    creation = etree.SubElement(document_identification, creation_name)
    creation.text = utc_timestamp()

    # .. and the Peppol business scope - the document type and process this belongs to.
    business_scope = etree.SubElement(header, business_scope_name)

    scope_document = etree.SubElement(business_scope, scope_name)
    scope_document_type = etree.SubElement(scope_document, type_name)
    scope_document_type.text = _scope_type_document
    scope_document_id = etree.SubElement(scope_document, instance_identifier_name)
    scope_document_id.text = document_type
    scope_document_identifier = etree.SubElement(scope_document, identifier_name)
    scope_document_identifier.text = document_standard

    scope_process = etree.SubElement(business_scope, scope_name)
    scope_process_type = etree.SubElement(scope_process, type_name)
    scope_process_type.text = _scope_type_process
    scope_process_id = etree.SubElement(scope_process, instance_identifier_name)
    scope_process_id.text = process_id
    scope_process_identifier = etree.SubElement(scope_process, identifier_name)
    scope_process_identifier.text = process_scheme

    # The business document itself goes after the header, unchanged.
    root.append(business_document)

    out = etree.tostring(root, xml_declaration=True, encoding='UTF-8')
    return out

# ################################################################################################################################

def parse_sbdh(data:'bytes') -> 'sbdh_parse_result':
    """ Extracts the header identifiers and the business document from
    a StandardBusinessDocument. Returns the header details and the document element.
    """
    try:
        root = etree.fromstring(data)
    except etree.XMLSyntaxError as e:
        raise AS4ProtocolException(EbMSError.Value_Not_Recognized, f'Could not parse the SBDH document -> {e}')

    header_name = qname(NS.SBDH, 'StandardBusinessDocumentHeader')
    sender_name = qname(NS.SBDH, 'Sender')
    receiver_name = qname(NS.SBDH, 'Receiver')
    identifier_name = qname(NS.SBDH, 'Identifier')
    document_identification_name = qname(NS.SBDH, 'DocumentIdentification')
    instance_identifier_name = qname(NS.SBDH, 'InstanceIdentifier')
    business_scope_name = qname(NS.SBDH, 'BusinessScope')
    scope_name = qname(NS.SBDH, 'Scope')
    type_name = qname(NS.SBDH, 'Type')

    header = root.find(header_name)

    if header is None:
        raise AS4ProtocolException(EbMSError.Value_Not_Recognized, 'Document has no StandardBusinessDocumentHeader')

    details = SBDHDetails()

    sender = header.find(sender_name)

    if sender is None:
        raise AS4ProtocolException(EbMSError.Value_Not_Recognized, 'Header has no Sender element')

    sender_identifier = sender.find(identifier_name)

    if sender_identifier is None:
        raise AS4ProtocolException(EbMSError.Value_Not_Recognized, 'Sender has no Identifier element')

    details.sender_id = element_text(sender_identifier)
    details.sender_scheme = element_attribute(sender_identifier, 'Authority')

    receiver = header.find(receiver_name)

    if receiver is None:
        raise AS4ProtocolException(EbMSError.Value_Not_Recognized, 'Header has no Receiver element')

    receiver_identifier = receiver.find(identifier_name)

    if receiver_identifier is None:
        raise AS4ProtocolException(EbMSError.Value_Not_Recognized, 'Receiver has no Identifier element')

    details.receiver_id = element_text(receiver_identifier)
    details.receiver_scheme = element_attribute(receiver_identifier, 'Authority')

    document_identification = header.find(document_identification_name)

    if document_identification is None:
        raise AS4ProtocolException(EbMSError.Value_Not_Recognized, 'Header has no DocumentIdentification element')

    instance = document_identification.find(instance_identifier_name)

    if instance is None:
        raise AS4ProtocolException(EbMSError.Value_Not_Recognized, 'DocumentIdentification has no InstanceIdentifier')

    details.instance_identifier = element_text(instance)

    # The business scope carries the Peppol document type and process identifiers.
    business_scope = header.find(business_scope_name)
    if business_scope is not None:

        scopes = business_scope.findall(scope_name)

        for scope in scopes:
            scope_type = scope.find(type_name)
            scope_value = scope.find(instance_identifier_name)

            # A scope of another kind can genuinely travel without these two elements.
            if scope_type is None:
                continue

            if scope_value is None:
                continue

            if scope_type.text == _scope_type_document:
                details.document_type = element_text(scope_value)
            elif scope_type.text == _scope_type_process:
                details.process_id = element_text(scope_value)

    # The business document is the first element that is not the header ..
    for child in root:
        if child.tag != header_name:
            business_document = child
            break

    # .. and a document without one has no payload to hand over.
    else:
        raise AS4ProtocolException(EbMSError.Value_Not_Recognized, 'Document has no business payload after the header')

    out = (details, business_document)
    return out

# ################################################################################################################################
# ################################################################################################################################
