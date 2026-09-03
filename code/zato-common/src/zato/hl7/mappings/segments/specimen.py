# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.fhir import Specimen
from zato.hl7.mappings.concepts import cwe_to_codeable_concept, parse_number, quantity
from zato.hl7.mappings.datatypes import ei_to_identifier
from zato.hl7.mappings.fields import component_as_repetition, component_value, populated_components, \
    serialize_component, subcomponent_value
from zato.hl7.mappings.segments.common import append_to_list_field, preserve_inexact_number, preserve_unmapped, \
    preserve_value

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import dictnone, stranydict
    from zato.hl7.mappings.context import ConversionContext
    from zato.hl7.mappings.fields import SegmentAccessor
    ConversionContext = ConversionContext
    SegmentAccessor = SegmentAccessor
    dictnone = dictnone

# ################################################################################################################################
# ################################################################################################################################

# Which field positions each mapper consumes - anything else that carries data is preserved as an extension.
_SPM_Handled = frozenset({1, 2, 4, 7, 8, 14, 17, 18})
_SAC_Handled = frozenset({3, 21, 22, 24, 27})

# Which SPS - specimen source - components the OBR-15 specimen consumes
_SPS_Source_Component    = 1
_SPS_Additive_Component  = 2
_SPS_Method_Component    = 3
_SPS_Body_Site_Component = 4
_SPS_Consumed = frozenset({
    _SPS_Source_Component,
    _SPS_Additive_Component,
    _SPS_Method_Component,
    _SPS_Body_Site_Component,
})

# Which SAC fields carry the container volumes and their common units
_SAC_Container_Volume = 21
_SAC_Available_Volume = 22
_SAC_Volume_Units     = 24
_SAC_Additive         = 27

# The whole Specimen elements an OBR's specimen source feeds, as they appear in the serialized form
_Merged_Source_Fields = ('type', 'container')

# How the serialized element names read as attributes of the typed Specimen
_Typed_Field_Names = {
    'type': 'type_',
    'container': 'container',
}

# ################################################################################################################################
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
    collected = context.datetime(collected_value, 'SPM', 17)

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
    received = context.datetime(received_value, 'SPM', 18)

    if received:
        out.receivedTime = received

    preserve_unmapped(accessor, _SPM_Handled, out, context)

    return out

# ################################################################################################################################

def specimen_from_obr(obr_accessor:'SegmentAccessor', context:'ConversionContext') -> 'Specimen | None':
    """ Builds a Specimen from what an OBR says about it - the specimen source in OBR-15,
    the received time in OBR-14 and the observation time in OBR-7 as the collection time.
    Returns None when OBR-15 carries nothing, the OBR then describes no specimen of its own.
    """
    # Our response to produce
    out = Specimen()

    config = context.config

    # An OBR with no specimen source describes no specimen ..
    source_repetition = obr_accessor.first(15)

    if not source_repetition:
        return None

    if context.patient_reference:
        out.subject = context.patient_reference

    # The specimen source name is the type ..
    source_cwe = component_as_repetition(source_repetition, _SPS_Source_Component)

    if specimen_type := cwe_to_codeable_concept(source_cwe, config):
        out.type_ = specimen_type

    # .. the collection method, body site and the observation time make the collection ..
    collection:'stranydict' = {}

    method_text = component_value(source_repetition, _SPS_Method_Component)
    if method_text:
        collection['method'] = {'text': method_text}

    site_cwe = component_as_repetition(source_repetition, _SPS_Body_Site_Component)

    if site := cwe_to_codeable_concept(site_cwe, config):
        collection['bodySite'] = site

    collected_value = obr_accessor.value(7)
    collected = context.datetime(collected_value, 'OBR', 7)

    if collected:
        collection['collectedDateTime'] = collected

    if collection:
        out.collection = collection

    # .. an additive becomes the container the specimen sits in ..
    additive_text = component_value(source_repetition, _SPS_Additive_Component)
    if additive_text:
        out.container = [{'additiveCodeableConcept': {'text': additive_text}}]

    # .. the received time completes the picture ..
    received_value = obr_accessor.value(14)
    received = context.datetime(received_value, 'OBR', 14)

    if received:
        out.receivedTime = received
    elif received_value:
        preserve_value(out, context, 'OBR', 14, received_value)

    # .. and whatever else the specimen source carries is preserved on the specimen.
    populated = populated_components(source_repetition)
    unconsumed = populated - _SPS_Consumed

    for position in sorted(unconsumed):
        value = serialize_component(source_repetition, position)
        preserve_value(out, context, 'SPS', position, value)

    return out

# ################################################################################################################################

def merge_obr_specimen(obr_accessor:'SegmentAccessor', specimen:'Specimen', context:'ConversionContext') -> 'None':
    """ Folds what an OBR says about its specimen into the Specimen the group's SPM produced.
    The SPM is the authoritative description, so the OBR fills in only what the SPM left empty,
    and an OBR value the SPM contradicts is preserved as-is.
    """
    obr_specimen = specimen_from_obr(obr_accessor, context)
    if not obr_specimen:
        return

    obr_dict = obr_specimen.to_dict()
    spm_dict = specimen.to_dict()

    # The source description conflicts when the type or the container it fed disagree ..
    source_conflict = False

    for field_name in _Merged_Source_Fields:
        obr_value = obr_dict.get(field_name)

        if obr_value is None:
            continue

        spm_value = spm_dict.get(field_name)

        if spm_value is None:
            typed_name = _Typed_Field_Names[field_name]
            setattr(specimen, typed_name, obr_value)
        elif spm_value != obr_value:
            source_conflict = True

    # .. the collection merges element by element, the collection time is not a conflict ..
    if obr_collection := obr_dict.get('collection'):
        spm_collection = spm_dict.get('collection')

        if spm_collection is None:
            spm_collection = {}

        for element_name, obr_element in obr_collection.items():
            if element_name not in spm_collection:
                spm_collection[element_name] = obr_element
            elif spm_collection[element_name] != obr_element:
                if element_name != 'collectedDateTime':
                    source_conflict = True

        specimen.collection = spm_collection

    if source_conflict:
        serialized_source = obr_accessor.serialize(15)
        preserve_value(specimen, context, 'OBR', 15, serialized_source)

    # .. the received time is its own field ..
    obr_received = obr_dict.get('receivedTime')

    if obr_received:
        spm_received = spm_dict.get('receivedTime')

        if spm_received is None:
            specimen.receivedTime = obr_received
        elif spm_received != obr_received:
            received_value = obr_accessor.value(14)
            preserve_value(specimen, context, 'OBR', 14, received_value)

    # .. and whatever the OBR specimen preserved travels along.
    if extensions := obr_dict.get('extension'):
        for extension in extensions:
            append_to_list_field(specimen, 'extension', extension)

# ################################################################################################################################

def _volume_quantity(
    accessor:'SegmentAccessor',
    position:'int',
    units:'dictnone',
    specimen:'Specimen',
    context:'ConversionContext',
    ) -> 'dictnone':
    """ Builds a Quantity from one SAC volume field, keeping the digits a float cannot carry exactly.
    """

    # An empty volume builds no quantity ..
    value = accessor.value(position)

    if not value:
        return None

    # .. a volume that is not a number is preserved as-is ..
    number = parse_number(value)

    if not number:
        preserve_value(specimen, context, 'SAC', position, value)
        return None

    # .. and a number the float cannot carry exactly keeps its digits as an extension.
    if not number.is_exact:
        preserve_inexact_number(specimen, context, 'SAC', position, value)

    out = quantity(number.value, units)
    return out

# ################################################################################################################################

def apply_sac(accessor:'SegmentAccessor', context:'ConversionContext', specimen:'Specimen') -> 'None':
    """ Adds the container from SAC to an existing Specimen - its identifier, its volumes and its additive.
    """
    config = context.config

    container:'stranydict' = {}

    # The container identifier ..
    container_repetition = accessor.first(3)

    if container_id := ei_to_identifier(container_repetition, config):
        container['identifier'] = [container_id]

    # .. the container volume is its capacity and the available specimen volume
    # .. what it holds, both in the volume units ..
    units_repetition = accessor.first(_SAC_Volume_Units)
    units = cwe_to_codeable_concept(units_repetition, config)
    units_used = False

    if capacity := _volume_quantity(accessor, _SAC_Container_Volume, units, specimen, context):
        container['capacity'] = capacity
        units_used = True

    if specimen_quantity := _volume_quantity(accessor, _SAC_Available_Volume, units, specimen, context):
        container['specimenQuantity'] = specimen_quantity
        units_used = True

    # .. units with no volume to qualify are preserved as-is ..
    if units:
        if not units_used:
            serialized_units = accessor.serialize(_SAC_Volume_Units)
            preserve_value(specimen, context, 'SAC', _SAC_Volume_Units, serialized_units)

    # .. and the additive keeps its coding.
    additive_repetition = accessor.first(_SAC_Additive)

    if additive := cwe_to_codeable_concept(additive_repetition, config):
        container['additiveCodeableConcept'] = additive

    if container:
        append_to_list_field(specimen, 'container', container)

    preserve_unmapped(accessor, _SAC_Handled, specimen, context)

# ################################################################################################################################
# ################################################################################################################################
