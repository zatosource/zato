# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64encode

# Zato
from zato.fhir import DocumentReference
from zato.hl7.mappings.codes import lookup
from zato.hl7.mappings.concepts import cwe_to_codeable_concept
from zato.hl7.mappings.datatypes import ei_to_identifier
from zato.hl7.mappings.segments.common import Document_Status, add_practitioner, append_to_list_field, \
    preserve_other_components, preserve_unmapped, preserve_value

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, stranydict
    from zato.hl7.mappings.context import ConversionContext
    from zato.hl7.mappings.fields import SegmentAccessor
    ConversionContext = ConversionContext
    SegmentAccessor = SegmentAccessor

# ################################################################################################################################
# ################################################################################################################################

# Which field positions the mapper consumes - anything else that carries data is preserved as an extension.
_TXA_Handled = frozenset({1, 2, 3, 4, 5, 9, 12, 16, 17, 19, 22})

# The content type the document text gathered from OBX segments is stored under
_Text_Content_Type = 'text/plain'

# What the TXA-3 document content presentation codes stand for as a MIME type - the HL7 table codes
# and the shorthands that arrive in their place.
_Presentation_Content_Types = {
    'TX': _Text_Content_Type,
    'TEXT': _Text_Content_Type,
    'FT': _Text_Content_Type,
    'AP': 'application/octet-stream',
    'PD': 'application/pdf',
    'PDF': 'application/pdf',
}

# What separates a MIME type from its subtype
_Mime_Separator = '/'

# Which components of TXA-3 the presentation consumes - the code, its display and its table
_Presentation_Code_Component    = 1
_Presentation_Display_Component = 2
_Presentation_Table_Component   = 3
_Presentation_Consumed = frozenset({
    _Presentation_Code_Component,
    _Presentation_Display_Component,
    _Presentation_Table_Component,
})

# ################################################################################################################################
# ################################################################################################################################

def _presentation_content_type(
    accessor:'SegmentAccessor',
    context:'ConversionContext',
    document:'DocumentReference',
    ) -> 'str':
    """ Reads the content type the document is presented in from TXA-3 - the text type when there is none,
    a presentation that is neither a known code nor a MIME type is preserved whole on the document.
    """

    # Our response to produce
    out = _Text_Content_Type

    # An empty presentation leaves the text type in place ..
    code = accessor.component(3, _Presentation_Code_Component)

    if not code:
        return out

    # .. a code with a subtype separator already is a MIME type, anything else goes through the table ..
    if _Mime_Separator in code:
        content_type = code
    else:
        code_upper = code.upper()
        content_type = _Presentation_Content_Types.get(code_upper)

    # .. and a presentation the table does not know is preserved whole.
    if content_type:
        out = content_type
        preserve_other_components(accessor, 3, _Presentation_Consumed, document, context)
    else:
        serialized = accessor.serialize(3)
        preserve_value(document, context, 'TXA', 3, serialized)

    return out

# ################################################################################################################################

def map_txa(accessor:'SegmentAccessor', context:'ConversionContext') -> 'DocumentReference':
    """ Converts TXA to a DocumentReference. The document body itself arrives later,
    from the OBX segments that follow, through set_document_text or add_document_attachment.
    """
    config = context.config

    # Our response to produce
    out = DocumentReference()

    if context.patient_reference:
        out.subject = context.patient_reference

    # The availability status decides the document status, unknown values
    # map to the default and are preserved as-is ..
    availability_code = accessor.value(19)

    if availability := lookup('document_availability_status', availability_code, config):
        out.status = availability['code']
    else:
        out.status = Document_Status

        if availability_code:
            preserve_value(out, context, 'TXA', 19, availability_code)

    # .. the completion status maps to the composition status ..
    completion_code = accessor.value(17)

    if completion := lookup('document_completion_status', completion_code, config):
        out.docStatus = completion['code']
    else:
        if completion_code:
            preserve_value(out, context, 'TXA', 17, completion_code)

    # .. the document type keeps its coding ..
    type_repetition = accessor.first(2)

    if document_type := cwe_to_codeable_concept(type_repetition, config):
        out.type_ = document_type

    # .. the activity time is the document date ..
    activity_value = accessor.value(4)
    activity_time = context.instant(activity_value, 'TXA', 4)

    if activity_time:
        out.date = activity_time
    elif activity_value:
        preserve_value(out, context, 'TXA', 4, activity_value)

    # .. the activity providers and the originators become authors ..
    authors:'anylist' = []

    for position in (5, 9):
        for repetition in accessor.repetitions(position):
            if reference := add_practitioner(repetition, context):
                if reference not in authors:
                    authors.append(reference)

    if authors:
        out.author = authors

    # .. the authenticating person signs the document off ..
    authenticator_repetition = accessor.first(22)

    if authenticator := add_practitioner(authenticator_repetition, context):
        out.authenticator = authenticator

    # .. the unique document number is the master identifier ..
    document_number_repetition = accessor.first(12)

    if master_identifier := ei_to_identifier(document_number_repetition, config):
        out.masterIdentifier = master_identifier

    # .. and the content starts out empty, in the presentation type, titled by the unique file name,
    # .. to be filled in from the following OBX segments.
    content_type = _presentation_content_type(accessor, context, out)
    attachment:'stranydict' = {'contentType': content_type}

    file_name = accessor.component(16, 1)
    if file_name:
        attachment['title'] = file_name

    out.content = [{'attachment': attachment}]

    preserve_unmapped(accessor, _TXA_Handled, out, context)

    return out

# ################################################################################################################################

def set_document_text(document:'DocumentReference', text:'str') -> 'None':
    """ Stores the document text - gathered from OBX segments - in the DocumentReference,
    keeping whatever the first attachment already carries.
    """
    text_bytes = text.encode('utf8')
    encoded_bytes = b64encode(text_bytes)
    encoded = encoded_bytes.decode('ascii')

    # The current content comes from the serialized form, reading the typed field would auto-vivify it.
    document_dict = document.to_dict()
    content = document_dict['content']

    first_entry = content[0]
    first_attachment = first_entry['attachment']

    # A first attachment that already carries data - an OBX-provided one - stays
    # intact and the text becomes an attachment of its own.
    if 'data' in first_attachment:
        text_attachment = {'contentType': _Text_Content_Type, 'data': encoded}
        content.append({'attachment': text_attachment})
    else:
        first_attachment['contentType'] = _Text_Content_Type
        first_attachment['data'] = encoded

    document.content = content

# ################################################################################################################################

def add_document_attachment(document:'DocumentReference', attachment:'stranydict') -> 'None':
    """ Adds one attachment - encapsulated data from an OBX - to the DocumentReference.
    An empty first content entry - the placeholder map_txa starts with - gives way to real data.
    """
    document_dict = document.to_dict()
    content = document_dict['content']

    first_entry = content[0]
    first_attachment = first_entry['attachment']

    if 'data' not in first_attachment:

        placeholder_title = first_attachment.get('title')
        attachment_title = attachment.get('title')

        # When both carry titles the placeholder stays and the attachment is appended below ..
        replace_placeholder = True

        if placeholder_title:
            if attachment_title:
                replace_placeholder = False

        # .. otherwise the first real attachment takes the placeholder's place,
        # inheriting its title when the attachment brings none of its own.
        if replace_placeholder:

            if placeholder_title:
                attachment['title'] = placeholder_title

            content[0] = {'attachment': attachment}
            document.content = content
            return

    append_to_list_field(document, 'content', {'attachment': attachment})

# ################################################################################################################################
# ################################################################################################################################
