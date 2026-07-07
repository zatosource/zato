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
from zato.common.util.xml_.core import qname, utc_timestamp

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# The header version the SBDH specification defines - there has only ever been one.
_header_version = '1.0'

_nsmap = {
    'sbdh': NS.SBDH,
}

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SBDHInfo:
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
    root = etree.Element(qname(NS.SBDH, 'StandardBusinessDocument'), nsmap=_nsmap)
    header = etree.SubElement(root, qname(NS.SBDH, 'StandardBusinessDocumentHeader'))

    version = etree.SubElement(header, qname(NS.SBDH, 'HeaderVersion'))
    version.text = _header_version

    # Who sends this document ..
    sender = etree.SubElement(header, qname(NS.SBDH, 'Sender'))
    sender_identifier = etree.SubElement(sender, qname(NS.SBDH, 'Identifier'))
    sender_identifier.set('Authority', sender_scheme)
    sender_identifier.text = sender_id

    # .. who is to receive it ..
    receiver = etree.SubElement(header, qname(NS.SBDH, 'Receiver'))
    receiver_identifier = etree.SubElement(receiver, qname(NS.SBDH, 'Identifier'))
    receiver_identifier.set('Authority', receiver_scheme)
    receiver_identifier.text = receiver_id

    # .. what kind of document it is ..
    document_identification = etree.SubElement(header, qname(NS.SBDH, 'DocumentIdentification'))

    standard = etree.SubElement(document_identification, qname(NS.SBDH, 'Standard'))
    standard.text = document_standard

    type_version = etree.SubElement(document_identification, qname(NS.SBDH, 'TypeVersion'))
    type_version.text = document_type_version

    instance = etree.SubElement(document_identification, qname(NS.SBDH, 'InstanceIdentifier'))
    instance.text = instance_identifier

    type_element = etree.SubElement(document_identification, qname(NS.SBDH, 'Type'))
    type_element.text = business_document.tag.split('}')[-1]

    creation = etree.SubElement(document_identification, qname(NS.SBDH, 'CreationDateAndTime'))
    creation.text = utc_timestamp()

    # .. and the Peppol business scope - the document type and process this belongs to.
    business_scope = etree.SubElement(header, qname(NS.SBDH, 'BusinessScope'))

    scope_document = etree.SubElement(business_scope, qname(NS.SBDH, 'Scope'))
    scope_document_type = etree.SubElement(scope_document, qname(NS.SBDH, 'Type'))
    scope_document_type.text = 'DOCUMENTID'
    scope_document_id = etree.SubElement(scope_document, qname(NS.SBDH, 'InstanceIdentifier'))
    scope_document_id.text = document_type
    scope_document_identifier = etree.SubElement(scope_document, qname(NS.SBDH, 'Identifier'))
    scope_document_identifier.text = document_standard

    scope_process = etree.SubElement(business_scope, qname(NS.SBDH, 'Scope'))
    scope_process_type = etree.SubElement(scope_process, qname(NS.SBDH, 'Type'))
    scope_process_type.text = 'PROCESSID'
    scope_process_id = etree.SubElement(scope_process, qname(NS.SBDH, 'InstanceIdentifier'))
    scope_process_id.text = process_id
    scope_process_identifier = etree.SubElement(scope_process, qname(NS.SBDH, 'Identifier'))
    scope_process_identifier.text = process_scheme

    # The business document itself goes after the header, unchanged.
    root.append(business_document)

    out = etree.tostring(root, xml_declaration=True, encoding='UTF-8')
    return out

# ################################################################################################################################

def parse_sbdh(data:'bytes') -> 'tuple[SBDHInfo, any_]':
    """ Extracts the header identifiers and the business document from
    a StandardBusinessDocument. Returns the header info and the document element.
    """
    try:
        root = etree.fromstring(data)
    except Exception as e:
        raise AS4ProtocolException(EbMSError.Value_Not_Recognized, f'Could not parse the SBDH document -> {e}')

    header = root.find(qname(NS.SBDH, 'StandardBusinessDocumentHeader'))

    if header is None:
        raise AS4ProtocolException(EbMSError.Value_Not_Recognized, 'Document has no StandardBusinessDocumentHeader')

    info = SBDHInfo()

    sender = header.find(qname(NS.SBDH, 'Sender'))
    sender_identifier = sender.find(qname(NS.SBDH, 'Identifier'))
    info.sender_id = sender_identifier.text or ''
    info.sender_scheme = sender_identifier.get('Authority') or ''

    receiver = header.find(qname(NS.SBDH, 'Receiver'))
    receiver_identifier = receiver.find(qname(NS.SBDH, 'Identifier'))
    info.receiver_id = receiver_identifier.text or ''
    info.receiver_scheme = receiver_identifier.get('Authority') or ''

    document_identification = header.find(qname(NS.SBDH, 'DocumentIdentification'))
    instance = document_identification.find(qname(NS.SBDH, 'InstanceIdentifier'))
    info.instance_identifier = instance.text or ''

    # The business scope carries the Peppol document type and process identifiers.
    business_scope = header.find(qname(NS.SBDH, 'BusinessScope'))
    if business_scope is not None:
        for scope in business_scope.findall(qname(NS.SBDH, 'Scope')):
            scope_type = scope.find(qname(NS.SBDH, 'Type'))
            scope_value = scope.find(qname(NS.SBDH, 'InstanceIdentifier'))

            if scope_type.text == 'DOCUMENTID':
                info.document_type = scope_value.text or ''
            elif scope_type.text == 'PROCESSID':
                info.process_id = scope_value.text or ''

    # The business document is the first element that is not the header.
    business_document = None

    for child in root:
        if child.tag != qname(NS.SBDH, 'StandardBusinessDocumentHeader'):
            business_document = child
            break

    if business_document is None:
        raise AS4ProtocolException(EbMSError.Value_Not_Recognized, 'Document has no business payload after the header')

    out = (info, business_document)
    return out

# ################################################################################################################################
# ################################################################################################################################
