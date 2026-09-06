# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.fhir import RelatedPerson
from zato.hl7.mappings.codes import lookup
from zato.hl7.mappings.concepts import cwe_to_codeable_concept, tag_coding_systems
from zato.hl7.mappings.datatypes import cx_to_identifier, xad_to_address, xpn_to_human_name, xtn_to_contact_points
from zato.hl7.mappings.segments.common import patient_or_absent_reference, preserve_unmapped, preserve_value

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

# Which field positions each mapper consumes - anything else that carries data is preserved as an extension.
_NK1_Handled = frozenset({1, 2, 3, 4, 5, 6, 7, 8, 9, 15, 16})
_GT1_Handled = frozenset({1, 2, 3, 5, 6, 7, 8, 9, 11})

# ################################################################################################################################
# ################################################################################################################################

def map_nk1(accessor:'SegmentAccessor', context:'ConversionContext') -> 'RelatedPerson | None':
    """ Converts NK1 to a RelatedPerson tied to the current patient.
    """
    config = context.config

    # Our response to produce
    out = RelatedPerson()

    # FHIR requires the patient a related person relates to.
    out.patient = patient_or_absent_reference(context)

    names:'anylist' = []

    for repetition in accessor.repetitions(2):
        if name := xpn_to_human_name(repetition, config):
            names.append(name)

    if names:
        out.name = names

    # The relationship and the contact role both keep their v2 codes,
    # with standard table codes gaining their table's system.
    relationships:'anylist' = []

    relationship_repetition = accessor.first(3)

    if relationship := cwe_to_codeable_concept(relationship_repetition, config):
        tag_coding_systems(relationship, 'personal_relationship', config)
        relationships.append(relationship)

    role_repetition = accessor.first(7)

    if role := cwe_to_codeable_concept(role_repetition, config):
        tag_coding_systems(role, 'contact_role', config)
        relationships.append(role)

    if relationships:
        out.relationship = relationships

    addresses:'anylist' = []

    for repetition in accessor.repetitions(4):
        if address := xad_to_address(repetition, config):
            addresses.append(address)

    if addresses:
        out.address = addresses

    telecoms:'anylist' = []

    for repetition in accessor.repetitions(5):
        for telecom in xtn_to_contact_points(repetition, config, default_use='home'):
            telecoms.append(telecom)

    for repetition in accessor.repetitions(6):
        for telecom in xtn_to_contact_points(repetition, config, default_use='work'):
            telecoms.append(telecom)

    if telecoms:
        out.telecom = telecoms

    # The relationship's start and end dates bound the period.
    period:'stranydict' = {}

    start_value = accessor.value(8)
    start_date = context.date(start_value, 'NK1', 8)

    if start_date:
        period['start'] = start_date

    end_value = accessor.value(9)
    end_date = context.date(end_value, 'NK1', 9)

    if end_date:
        period['end'] = end_date

    if period:
        out.period = period

    # The administrative sex maps to the gender code, unknown codes are preserved as-is.
    sex_code = accessor.value(15)
    if sex_code:
        if gender := lookup('administrative_sex', sex_code, config):
            out.gender = gender['code']
        else:
            preserve_value(out, context, 'NK1', 15, sex_code)

    # The date of birth drops any time part.
    birth_value = accessor.value(16)
    birth_date = context.date(birth_value, 'NK1', 16)

    if birth_date:
        out.birthDate = birth_date

    preserve_unmapped(accessor, _NK1_Handled, out, context)

    # A next-of-kin with no data at all carries nothing to build a person from.
    content = out.to_dict()
    all_keys = set(content)
    content_keys = all_keys - {'resourceType', 'patient'}

    if not content_keys:
        return None

    return out

# ################################################################################################################################

def map_gt1(accessor:'SegmentAccessor', context:'ConversionContext') -> 'RelatedPerson':
    """ Converts GT1 - the guarantor - to a RelatedPerson tied to the current patient.
    """
    config = context.config

    # Our response to produce
    out = RelatedPerson()

    # FHIR requires the patient a guarantor relates to.
    out.patient = patient_or_absent_reference(context)

    identifiers:'anylist' = []

    for repetition in accessor.repetitions(2):
        if identifier := cx_to_identifier(repetition, config):
            identifiers.append(identifier)

    if identifiers:
        out.identifier = identifiers

    names:'anylist' = []

    for repetition in accessor.repetitions(3):
        if name := xpn_to_human_name(repetition, config):
            names.append(name)

    if names:
        out.name = names

    addresses:'anylist' = []

    for repetition in accessor.repetitions(5):
        if address := xad_to_address(repetition, config):
            addresses.append(address)

    if addresses:
        out.address = addresses

    telecoms:'anylist' = []

    for repetition in accessor.repetitions(6):
        for telecom in xtn_to_contact_points(repetition, config, default_use='home'):
            telecoms.append(telecom)

    for repetition in accessor.repetitions(7):
        for telecom in xtn_to_contact_points(repetition, config, default_use='work'):
            telecoms.append(telecom)

    if telecoms:
        out.telecom = telecoms

    # The date of birth drops any time part.
    birth_value = accessor.value(8)
    birth_date = context.date(birth_value, 'GT1', 8)

    if birth_date:
        out.birthDate = birth_date

    # The administrative sex maps to the gender code, unknown codes are preserved as-is.
    sex_code = accessor.value(9)
    if sex_code:
        if gender := lookup('administrative_sex', sex_code, config):
            out.gender = gender['code']
        else:
            preserve_value(out, context, 'GT1', 9, sex_code)

    # The guarantor's relationship to the patient keeps its v2 code,
    # with standard table codes gaining their table's system.
    relationship_repetition = accessor.first(11)

    if relationship := cwe_to_codeable_concept(relationship_repetition, config):
        tag_coding_systems(relationship, 'personal_relationship', config)
        out.relationship = [relationship]

    preserve_unmapped(accessor, _GT1_Handled, out, context)

    return out

# ################################################################################################################################
# ################################################################################################################################
