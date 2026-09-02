# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.fhir import Basic, Practitioner
from zato.hl7.mappings.concepts import cwe_to_codeable_concept
from zato.hl7.mappings.datatypes import cx_to_identifier, xad_to_address, xpn_to_human_name, xtn_to_contact_points
from zato.hl7.mappings.fields import serialize_field
from zato.hl7.mappings.segments.common import add_practitioner, append_to_list_field, preserve_unmapped, preserve_value

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist
    from zato.hl7.mappings.context import ConversionContext
    from zato.hl7.mappings.fields import SegmentAccessor
    ConversionContext = ConversionContext
    SegmentAccessor = SegmentAccessor
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# Which field positions each mapper consumes - anything else that carries data is preserved as an extension.
_STF_Handled = frozenset({1, 2, 3, 7, 10, 11})
_PRA_Handled = frozenset({1, 5, 6})
_PRT_Handled = frozenset({5})

# What STF-7 says about a staff member who is active or inactive
_Staff_Active = 'A'
_Staff_Inactive = 'I'

# ################################################################################################################################
# ################################################################################################################################

def map_segment_to_basic(raw_segment:'any_', context:'ConversionContext') -> 'Basic | None':
    """ Converts a segment without a FHIR mapping of its own - a Z-segment or an
    administrative one - to a Basic resource whose extensions carry every populated field.
    """
    base_url = context.config.extension_base_url
    segment_id = raw_segment.segment_id

    extensions:'anylist' = []

    # Every populated field becomes one extension, named after its position ..
    for field_index, field_data in enumerate(raw_segment.fields):
        value = serialize_field(field_data)
        if value:
            field_position = field_index + 1
            extensions.append({'url': f'{base_url}/{segment_id}/{field_position}', 'valueString': value})

    if not extensions:
        return None

    # .. and the resource itself says which segment it preserves.
    out = Basic()
    out.code = {'coding': [{'system': f'{base_url}/segment', 'code': segment_id}]}
    out.extension = extensions

    if context.patient_reference:
        out.subject = context.patient_reference

    return out

# ################################################################################################################################

def map_stf(accessor:'SegmentAccessor', context:'ConversionContext') -> 'Practitioner':
    """ Converts STF - staff identification from a master file notification - to a Practitioner.
    """
    config = context.config

    # Our response to produce
    out = Practitioner()

    # The primary key and the staff identifiers all become identifiers ..
    identifiers:'anylist' = []

    primary_key = accessor.component(1, 1)
    if primary_key:
        identifiers.append({'value': primary_key})

    for repetition in accessor.repetitions(2):
        if identifier := cx_to_identifier(repetition, config):
            identifiers.append(identifier)

    if identifiers:
        out.identifier = identifiers

    # .. every repetition of the name field becomes a HumanName ..
    names:'anylist' = []

    for repetition in accessor.repetitions(3):
        if name := xpn_to_human_name(repetition, config):
            names.append(name)

    if names:
        out.name = names

    # .. the active/inactive flag maps when it uses the standard codes,
    # .. anything else is preserved as-is ..
    active_flag = accessor.value(7)

    if active_flag == _Staff_Active:
        out.active = True
    elif active_flag == _Staff_Inactive:
        out.active = False
    else:
        if active_flag:
            preserve_value(out, context, 'STF', 7, active_flag)

    # .. and the phones and the office addresses complete the picture.
    telecoms:'anylist' = []

    for repetition in accessor.repetitions(10):
        for telecom in xtn_to_contact_points(repetition, config, default_use='work'):
            telecoms.append(telecom)

    if telecoms:
        out.telecom = telecoms

    addresses:'anylist' = []

    for repetition in accessor.repetitions(11):
        if address := xad_to_address(repetition, config):
            addresses.append(address)

    if addresses:
        out.address = addresses

    preserve_unmapped(accessor, _STF_Handled, out, context)

    return out

# ################################################################################################################################

def apply_pra(accessor:'SegmentAccessor', context:'ConversionContext', practitioner:'Practitioner') -> 'None':
    """ Adds the specialties and practitioner ID numbers from PRA to an existing Practitioner.
    """
    config = context.config

    # Each specialty becomes a qualification ..
    for repetition in accessor.repetitions(5):
        if specialty := cwe_to_codeable_concept(repetition, config):
            qualification = {'code': specialty}
            append_to_list_field(practitioner, 'qualification', qualification)

    # .. and each practitioner ID number becomes an identifier.
    for repetition in accessor.repetitions(6):
        if identifier := cx_to_identifier(repetition, config):
            append_to_list_field(practitioner, 'identifier', identifier)

    preserve_unmapped(accessor, _PRA_Handled, practitioner, context)

# ################################################################################################################################

def apply_prt(accessor:'SegmentAccessor', context:'ConversionContext', target:'any_') -> 'bool':
    """ Applies PRT - a participation - to the resource the participation is about.
    The participating person becomes a Practitioner the resource points at and every
    other populated field is preserved on that resource. Tells the caller whether
    the segment was consumed - a PRT with no person or no resource stays whole.
    """
    if target is None:
        return False

    provider_repetition = accessor.first(5)

    reference = add_practitioner(provider_repetition, context)
    if not reference:
        return False

    target_dict = target.to_dict()
    resource_type = target_dict['resourceType']

    # An Encounter records the person as a participant ..
    if resource_type == 'Encounter':
        participant = {'individual': reference}
        append_to_list_field(target, 'participant', participant)

    # .. a document records them as an author ..
    elif resource_type == 'DocumentReference':
        append_to_list_field(target, 'author', reference)

    # .. and an order, a report or an observation records them as a performer.
    else:
        append_to_list_field(target, 'performer', reference)

    preserve_unmapped(accessor, _PRT_Handled, target, context)

    return True

# ################################################################################################################################
# ################################################################################################################################
