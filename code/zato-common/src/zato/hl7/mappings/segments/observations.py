# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64encode

# Zato
from zato.fhir import Device, Observation, Specimen
from zato.hl7.mappings.codes import lookup
from zato.hl7.mappings.concepts import cwe_to_codeable_concept, sn_to_observation_value
from zato.hl7.mappings.datatypes import dtm_to_datetime, ei_to_identifier
from zato.hl7.mappings.fields import component_value, serialize_field, serialize_repetition, subcomponent_value
from zato.hl7.mappings.segments.common import Coded_Value_Types, Datetime_Value_Types, Default_Observation_Status, \
    Encapsulated_Value_Type, Escape_Char, Reference_Pointer_Value_Type, Repetition_Char, Text_Value_Types, \
    Unknown_Code, add_named_organization, add_practitioner, append_to_list_field, preserve_unmapped, preserve_value
from zato.hl7v2_rs import decode_escapes

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict, strlist, strnone
    from zato.hl7.mappings.context import ConversionContext
    from zato.hl7.mappings.fields import SegmentAccessor
    ConversionContext = ConversionContext
    SegmentAccessor = SegmentAccessor
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# Type aliases
dictnone = 'stranydict | None'

# Which field positions each mapper consumes - anything else that carries data is preserved as an extension.
_OBX_Handled = frozenset({1, 2, 3, 5, 6, 7, 8, 11, 14, 15, 16, 17, 18})
_OBX_Attachment_Handled = frozenset({1, 2, 3, 5, 11})
_SPM_Handled = frozenset({1, 2, 4, 7, 8, 14, 17, 18})
_SAC_Handled = frozenset({3})

# What the ED type-of-data codes stand for in a MIME content type - both the HL7 table codes
# and the spelled-out media type words that can arrive in ED-2 directly.
_ED_Media_Types = {
    'AP': 'application',
    'AU': 'audio',
    'IM': 'image',
    'TX': 'text',
    'TEXT': 'text',
    'FT': 'text',
    'APPLICATION': 'application',
    'AUDIO': 'audio',
    'IMAGE': 'image',
    'VIDEO': 'video',
    'MODEL': 'model',
    'MULTIPART': 'multipart',
}

# The content type an ED value gets when its type and subtype spell out no known MIME pair
_Default_Content_Type = 'application/octet-stream'

# The ED encoding whose data is already transported as base64
_Base64_Encoding = 'BASE64'

# ################################################################################################################################
# ################################################################################################################################

def map_obx(accessor:'SegmentAccessor', context:'ConversionContext') -> 'Observation':
    """ Converts OBX to an Observation, routing the value by the declared value type.
    """
    config = context.config

    # Our response to produce
    out = Observation()

    if context.patient_reference:
        out.subject = context.patient_reference

    if context.encounter_reference:
        out.encounter = context.encounter_reference

    # The observation identifier is the code, which FHIR requires ..
    code_repetition = accessor.first(3)

    if code := cwe_to_codeable_concept(code_repetition, config):
        out.code = code
    else:
        out.code = Unknown_Code

    # .. the result status is required, unknown codes map to the default and are preserved as-is ..
    status_code = accessor.value(11)

    if status := lookup('observation_result_status', status_code, config):
        out.status = status['code']
    else:
        out.status = Default_Observation_Status

        if status_code:
            preserve_value(out, context, 'OBX', 11, status_code)

    # .. and the value routes by the declared value type.
    value_type = accessor.value(2)
    value_repetitions = accessor.repetitions(5)

    units_repetition = accessor.first(6)
    units = cwe_to_codeable_concept(units_repetition, config)

    if value_repetitions:
        serialized_value = accessor.serialize(5)
        _set_observation_value(out, value_type, value_repetitions, serialized_value, units, context)

    # The reference range is a display string.
    reference_range = accessor.value(7)
    if reference_range:
        out.referenceRange = [{'text': reference_range}]

    # Abnormal flags become interpretations, unknown codes are preserved as-is.
    interpretations:'anylist' = []

    for repetition in accessor.repetitions(8):
        flag_code = component_value(repetition, 1)
        if interpretation := lookup('abnormal_flags', flag_code, config):
            coding = {'system': interpretation['system'], 'code': interpretation['code']}
            interpretations.append({'coding': [coding]})
        else:
            if flag_code:
                preserve_value(out, context, 'OBX', 8, flag_code)

    if interpretations:
        out.interpretation = interpretations

    # The observation time maps to the effective time. Other values can arrive
    # in this slot with shifted vendor feeds - those are preserved as-is.
    effective_value = accessor.value(14)
    effective_time = dtm_to_datetime(effective_value, config)

    if effective_time:
        out.effectiveDateTime = effective_time
    elif effective_value:
        preserve_value(out, context, 'OBX', 14, effective_value)

    # The producer and the responsible observer become performers.
    performers:'anylist' = []

    producer_repetition = accessor.first(15)
    producer_name = component_value(producer_repetition, 2)

    if not producer_name:
        producer_name = component_value(producer_repetition, 1)

    if producer_name:
        producer_reference = add_named_organization(producer_name, context)
        performers.append(producer_reference)

    for repetition in accessor.repetitions(16):
        if reference := add_practitioner(repetition, context):
            performers.append(reference)

    if performers:
        out.performer = performers

    # The observation method keeps its coding.
    method_repetition = accessor.first(17)

    if method := cwe_to_codeable_concept(method_repetition, config):
        out.method = method

    # The equipment instance becomes a Device.
    equipment_repetition = accessor.first(18)

    if equipment := ei_to_identifier(equipment_repetition, config):
        device = Device()
        device.identifier = [equipment]

        out.device = context.add(device)

    preserve_unmapped(accessor, _OBX_Handled, out, context)

    return out

# ################################################################################################################################

def _quantity_from_units(value:'str', units:'dictnone') -> 'stranydict':
    """ Builds a FHIR Quantity from a numeric string and an optional units concept.
    """

    value_number = float(value)

    # Our response to produce
    out:'stranydict' = {'value': value_number}

    if units:
        if coding_list := units.get('coding'):
            first_coding = coding_list[0]
            out['code'] = first_coding['code']

            if coding_system := first_coding.get('system'):
                out['system'] = coding_system

        if unit_text := units.get('text'):
            out['unit'] = unit_text

    return out

# ################################################################################################################################

def ed_to_attachment(repetition:'anylist') -> 'stranydict':
    """ Converts an ED - encapsulated data - repetition to a FHIR Attachment.
    """

    # Our response to produce
    out:'stranydict' = {'contentType': _Default_Content_Type}

    type_of_data = component_value(repetition, 2)
    subtype = component_value(repetition, 3)
    encoding = component_value(repetition, 4)
    data = subcomponent_value(repetition, 5, 1)

    # The type and subtype spell out the MIME content type when both are recognizable.
    if subtype:
        if '/' in subtype:

            # Some senders put a complete MIME type into the subtype already.
            out['contentType'] = subtype.lower()

        elif type_of_data:
            type_upper = type_of_data.upper()

            if media_type := _ED_Media_Types.get(type_upper):
                subtype_lower = subtype.lower()
                out['contentType'] = f'{media_type}/{subtype_lower}'

    if data:

        # Base64-encoded payloads travel as-is, anything else is encoded here.
        if encoding:
            is_base64 = encoding.upper() == _Base64_Encoding
        else:
            is_base64 = False

        if is_base64:
            out['data'] = data
        else:
            data_bytes = data.encode('utf8')
            encoded_bytes = b64encode(data_bytes)
            out['data'] = encoded_bytes.decode('ascii')

    return out

# ################################################################################################################################

def obx_attachment(accessor:'SegmentAccessor', context:'ConversionContext', target:'any_') -> 'stranydict':
    """ Converts a whole ED-carrying OBX to an Attachment, titling it with the observation code
    and preserving whatever else the segment carries on the target resource.
    """

    value_repetition = accessor.first(5)

    # Our response to produce
    out = ed_to_attachment(value_repetition)

    # The observation identifier titles the attachment.
    title = accessor.component(3, 2)
    if not title:
        title = accessor.component(3, 1)

    if title:
        out['title'] = title

    preserve_unmapped(accessor, _OBX_Attachment_Handled, target, context)

    return out

# ################################################################################################################################

def _set_observation_value(
    observation:'Observation',
    value_type:'strnone',
    repetitions:'anylist',
    serialized_field:'str',
    units:'dictnone',
    context:'ConversionContext',
    ) -> 'None':
    """ Fills in the right Observation.value[x] field for one OBX value.
    """
    config = context.config

    # Most value types carry one repetition, coded ones may carry several.
    repetition = repetitions[0]

    # A numeric value becomes a Quantity with the units from OBX-6,
    # values that fail to parse as numbers stay strings ..
    if value_type == 'NM':
        value = component_value(repetition, 1)
        if value:
            try:
                observation.valueQuantity = _quantity_from_units(value, units)
            except ValueError:
                observation.valueString = value
        return

    # .. text stays text - each repetition is a line of its own, empty ones
    # .. included so paragraph breaks survive, and the wire form is split
    # .. before decoding because a decoded \R\ is text, not a separator,
    # .. while unescaped component separators are part of the text itself ..
    if value_type in Text_Value_Types:
        lines = []

        for line in serialized_field.split(Repetition_Char):
            lines.append(decode_escapes(line, Escape_Char))

        value = '\n'.join(lines)

        if value:
            observation.valueString = value
        return

    # .. coded values become CodeableConcepts, every repetition
    # .. contributing its codings to the one concept ..
    if value_type in Coded_Value_Types:
        if concept := cwe_to_codeable_concept(repetition, config):

            for extra_repetition in repetitions[1:]:
                if extra_concept := cwe_to_codeable_concept(extra_repetition, config):
                    if extra_codings := extra_concept.get('coding'):

                        # A text-only first repetition starts with no codings of its own.
                        codings = concept.get('coding')
                        if codings is None:
                            codings = []
                            concept['coding'] = codings

                        _ = codings.extend(extra_codings)

            observation.valueCodeableConcept = concept
        return

    # .. structured numerics go through their six-way branch ..
    if value_type == 'SN':
        if routed := sn_to_observation_value(repetition, config, units):
            field_name, field_value = routed
            setattr(observation, field_name, field_value)
        return

    # .. dates and times keep their precision ..
    if value_type in Datetime_Value_Types:
        value = component_value(repetition, 1)
        if datetime_value := dtm_to_datetime(value, config):
            observation.valueDateTime = datetime_value
        return

    if value_type == 'TM':
        value = component_value(repetition, 1)
        if value:
            time_length = len(value)
            hour = value[:2]
            minute = value[2:4]
            second = value[4:6]

            if time_length >= 6:
                observation.valueTime = f'{hour}:{minute}:{second}'
            elif time_length == 4:
                observation.valueTime = f'{hour}:{minute}:00'
        return

    # .. encapsulated data becomes an attachment extension, R4 observations
    # .. have no attachment value of their own ..
    if value_type == Encapsulated_Value_Type:
        attachment = ed_to_attachment(repetition)

        base_url = config.extension_base_url
        extension = {'url': f'{base_url}/attachment', 'valueAttachment': attachment}
        append_to_list_field(observation, 'extension', extension)
        return

    # .. a reference pointer keeps its wire form as a string - the whole field,
    # .. because a URL's escape sequences can parse into extra repetitions
    # .. that would otherwise be dropped ..
    if value_type == Reference_Pointer_Value_Type:
        observation.valueString = serialize_field(repetitions)
        return

    # .. a missing value type with a value present is taken as text ..
    if not value_type:
        value = component_value(repetition, 1)
        if value:
            observation.valueString = decode_escapes(value, Escape_Char)
        return

    # .. and any other value type is preserved as-is, together with its value.
    serialized_value = serialize_repetition(repetition)

    preserve_value(observation, context, 'OBX', 2, value_type)
    preserve_value(observation, context, 'OBX', 5, serialized_value)

# ################################################################################################################################

def map_spm(accessor:'SegmentAccessor', context:'ConversionContext') -> 'Specimen':
    """ Converts SPM to a Specimen.
    """
    config = context.config

    # Our response to produce
    out = Specimen()

    if context.patient_reference:
        out.subject = context.patient_reference

    # The specimen ID's placer part becomes the identifier ..
    specimen_id_repetition = accessor.first(2)
    specimen_id = subcomponent_value(specimen_id_repetition, 1, 1)

    if specimen_id:
        out.identifier = [{'value': specimen_id}]

    # .. the specimen type keeps its coding ..
    type_repetition = accessor.first(4)

    if specimen_type := cwe_to_codeable_concept(type_repetition, config):
        out.type_ = specimen_type

    # .. the collection method, body site and time make the collection ..
    collection:'stranydict' = {}

    method_repetition = accessor.first(7)

    if method := cwe_to_codeable_concept(method_repetition, config):
        collection['method'] = method

    site_repetition = accessor.first(8)

    if site := cwe_to_codeable_concept(site_repetition, config):
        collection['bodySite'] = site

    collected_value = accessor.value(17)
    collected = dtm_to_datetime(collected_value, config)

    if collected:
        collection['collectedDateTime'] = collected

    if collection:
        out.collection = collection

    # .. the description becomes a note ..
    description = accessor.value(14)
    if description:
        out.note = [{'text': description}]

    # .. and the received time completes the picture.
    received_value = accessor.value(18)
    received = dtm_to_datetime(received_value, config)

    if received:
        out.receivedTime = received

    preserve_unmapped(accessor, _SPM_Handled, out, context)

    return out

# ################################################################################################################################

def apply_sac(accessor:'SegmentAccessor', context:'ConversionContext', specimen:'Specimen') -> 'None':
    """ Adds the container from SAC to an existing Specimen.
    """
    config = context.config

    container_repetition = accessor.first(3)

    if container_id := ei_to_identifier(container_repetition, config):
        container = {'identifier': [container_id]}
        append_to_list_field(specimen, 'container', container)

    preserve_unmapped(accessor, _SAC_Handled, specimen, context)

# ################################################################################################################################

def gather_obx_text(accessor:'SegmentAccessor', context:'ConversionContext', document:'any_') -> 'strnone':
    """ Collects the text lines of one document-carrying OBX, joining all the repetitions of its value.
    Whatever else the segment carries is preserved on the document.
    """
    parts:'strlist' = []

    # Each line is a text value, so it is serialized whole - unescaped component
    # separators inside it are part of the text itself, while escape
    # sequences like \.br\ become the characters they stand for.
    for repetition in accessor.repetitions(5):
        line = serialize_repetition(repetition)
        if line:
            line = decode_escapes(line, Escape_Char)
            parts.append(line)

    preserve_unmapped(accessor, _OBX_Attachment_Handled, document, context)

    if parts:

        out = '\n'.join(parts)
        return out

    return None

# ################################################################################################################################

def nte_text(accessor:'SegmentAccessor') -> 'strnone':
    """ Joins all the comment repetitions of an NTE into one text. The comment is a text
    field, so unescaped component separators inside it are part of the text itself
    and each repetition is serialized whole.
    """
    parts:'strlist' = []

    for repetition in accessor.repetitions(3):
        comment = serialize_repetition(repetition)
        if comment:
            parts.append(comment)

    if parts:

        out = '\n'.join(parts)
        return out

    return None

# ################################################################################################################################
# ################################################################################################################################
