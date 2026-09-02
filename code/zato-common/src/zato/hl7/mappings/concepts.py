# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7.mappings.codes import coding_system_to_uri, lookup
from zato.hl7.mappings.fields import component_value

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, stranydict, strnone
    from zato.hl7.mappings.config import FHIRMappingConfig
    FHIRMappingConfig = FHIRMappingConfig

# ################################################################################################################################
# ################################################################################################################################

# Type aliases
dictnone = 'stranydict | None'
value_pair = tuple[str, 'stranydict | str']

# The system spoken-language codes belong to
Language_Coding_System = 'urn:ietf:bcp:47'

# The lengths ISO 639 language codes come in - two-letter 639-1 and three-letter 639-2 codes.
_ISO_639_Lengths = (2, 3)

# ################################################################################################################################
# ################################################################################################################################

def cwe_to_codeable_concept(repetition:'anylist', config:'FHIRMappingConfig') -> 'dictnone':
    """ Converts a CWE/CE - coded element - repetition to a FHIR CodeableConcept.
    """

    # Our response to produce
    out:'stranydict' = {}

    codings:'anylist' = []

    # The primary triplet is code, display text and coding system ..
    code = component_value(repetition, 1)
    text = component_value(repetition, 2)
    system_name = component_value(repetition, 3)

    if code:
        coding:'stranydict' = {'code': code}

        if text:
            coding['display'] = text

        if system := coding_system_to_uri(system_name):
            coding['system'] = system

        codings.append(coding)

    # .. the alternate triplet is a second coding when present -
    # .. a display-only alternate, with no code of its own, still becomes one ..
    alternate_code = component_value(repetition, 4)
    alternate_text = component_value(repetition, 5)
    alternate_system_name = component_value(repetition, 6)

    alternate_coding:'stranydict' = {}

    if alternate_code:
        alternate_coding['code'] = alternate_code

    if alternate_text:
        alternate_coding['display'] = alternate_text

    if alternate_coding:
        if alternate_system := coding_system_to_uri(alternate_system_name):
            alternate_coding['system'] = alternate_system

        codings.append(alternate_coding)

    if codings:
        out['coding'] = codings

    # .. and the display or original text becomes CodeableConcept.text.
    original_text = component_value(repetition, 9)

    if original_text:
        out['text'] = original_text
    elif text:
        out['text'] = text
    elif alternate_text:
        out['text'] = alternate_text
    elif code:
        out['text'] = code

    if not out:
        return None

    return out

# ################################################################################################################################

def tag_coding_systems(concept:'stranydict', map_name:'str', config:'FHIRMappingConfig') -> 'None':
    """ Fills in the coding system of each system-less coding whose code the named vocabulary map covers.
    Codes outside the map stay exactly as they arrived.
    """
    if codings := concept.get('coding'):

        for coding in codings:

            # A coding that already names its system arrived fully specified.
            if 'system' in coding:
                continue

            # A display-only coding has no code to resolve.
            if not (code := coding.get('code')):
                continue

            if entry := lookup(map_name, code, config):
                coding['code'] = entry['code']
                coding['system'] = entry['system']

# ################################################################################################################################

def cwe_to_language_concept(repetition:'anylist', config:'FHIRMappingConfig') -> 'dictnone':
    """ Converts a CWE holding a spoken language to a FHIR CodeableConcept.
    Bare ISO 639 codes become BCP-47 codings - lowercase, under the urn:ietf:bcp:47 system.
    """
    out = cwe_to_codeable_concept(repetition, config)
    if not out:
        return None

    if codings := out.get('coding'):

        for coding in codings:

            # A coding that already names its system arrived fully specified.
            if 'system' in coding:
                continue

            # A display-only alternate coding has no code to upgrade.
            if not (code := coding.get('code')):
                continue

            # Only codes shaped like ISO 639 become BCP-47 - anything else stays as it arrived.
            code_length = len(code)

            if code_length in _ISO_639_Lengths:
                if code.isalpha():
                    coding['code'] = code.lower()
                    coding['system'] = Language_Coding_System

    return out

# ################################################################################################################################

def _quantity(value:'float', units:'dictnone') -> 'stranydict':
    """ Builds a FHIR Quantity from a number and an optional units concept.
    """

    # Our response to produce
    out:'stranydict' = {'value': value}

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

def _parse_number(value:'strnone') -> 'float | None':
    """ Parses a string as a float, returning None when it is not a number.
    """
    if not value:
        return None

    try:
        out = float(value)
    except ValueError:
        return None

    return out

# ################################################################################################################################

def sn_to_observation_value(repetition:'anylist', config:'FHIRMappingConfig', units:'dictnone') -> 'value_pair | None':
    """ Converts an SN - structured numeric - repetition to a FHIR observation value.
    Returns the value field name and its content, following the six-way branch the
    comparator, number, separator and second number combinations call for.
    """
    comparator = component_value(repetition, 1)
    first_number = component_value(repetition, 2)
    separator = component_value(repetition, 3)
    second_number = component_value(repetition, 4)

    first_amount = _parse_number(first_number)
    second_amount = _parse_number(second_number)

    # A plain number, with or without a comparator, becomes a Quantity ..
    if first_amount is not None:
        if not separator:
            quantity = _quantity(first_amount, units)

            if comparator:
                quantity['comparator'] = comparator

            out = ('valueQuantity', quantity)
            return out

        # .. a range like 3 - 5 becomes a Range ..
        if separator == '-':
            if second_amount is not None:
                low = _quantity(first_amount, units)
                high = _quantity(second_amount, units)

                out = ('valueRange', {'low': low, 'high': high})
                return out

        # .. a ratio like 1 : 128 or 1 / 128 becomes a Ratio ..
        if separator in (':', '/'):
            if second_amount is not None:
                numerator = _quantity(first_amount, units)
                denominator = _quantity(second_amount, units)

                out = ('valueRatio', {'numerator': numerator, 'denominator': denominator})
                return out

        # .. a plus after the number, like 2 +, marks categorical results and stays a string.
        if separator == '+':
            marked_number = f'{first_number}+'

            out = ('valueString', marked_number)
            return out

    # Anything else is preserved as the string the components spell out.
    parts:'anylist' = []

    for component in (comparator, first_number, separator, second_number):
        if component:
            parts.append(component)

    if parts:
        joined = ''.join(parts)

        out = ('valueString', joined)
        return out

    return None

# ################################################################################################################################
# ################################################################################################################################
