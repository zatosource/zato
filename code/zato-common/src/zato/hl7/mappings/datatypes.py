# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7.mappings.codes import coding_system_to_uri, lookup
from zato.hl7.mappings.config import Authority_URN_Prefix
from zato.hl7.mappings.fields import component_value, subcomponent_value

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

# The identifier type code system all CX-5 and XCN-13 values live in
Identifier_Type_System = 'http://terminology.hl7.org/CodeSystem/v2-0203'

# How many digits each DTM precision level has
_DTM_Year_Length   = 4
_DTM_Month_Length  = 6
_DTM_Day_Length    = 8
_DTM_Hour_Length   = 10
_DTM_Minute_Length = 12
_DTM_Second_Length = 14

# ################################################################################################################################
# ################################################################################################################################

def hd_to_system(namespace:'strnone', universal_id:'strnone', universal_id_type:'strnone', config:'FHIRMappingConfig') -> 'strnone':
    """ Derives an identifier system URI from an HD - assigning authority - value.
    ISO universal IDs become urn:oid:, UUID ones become urn:uuid:, otherwise the namespace
    resolves through the config's identifier systems or falls back to a derived URN.
    """
    if universal_id:
        if universal_id_type == 'ISO':

            out = f'urn:oid:{universal_id}'
            return out

        if universal_id_type == 'UUID':

            out = f'urn:uuid:{universal_id.lower()}'
            return out

    if namespace:
        namespace = namespace.strip()

    if not namespace:
        return None

    # A configured system URI for this authority wins ..
    if namespace in config.identifier_systems:

        out = config.identifier_systems[namespace]
        return out

    # .. otherwise the authority name becomes a stable URN.
    out = Authority_URN_Prefix + namespace
    return out

# ################################################################################################################################

def cx_to_identifier(repetition:'anylist', config:'FHIRMappingConfig') -> 'dictnone':
    """ Converts a CX - extended composite ID - repetition to a FHIR Identifier.
    """
    value = component_value(repetition, 1)
    if not value:
        return None

    # Our response to produce
    out:'stranydict' = {'value': value}

    # The assigning authority becomes the identifier system ..
    namespace = subcomponent_value(repetition, 4, 1)
    universal_id = subcomponent_value(repetition, 4, 2)
    universal_id_type = subcomponent_value(repetition, 4, 3)

    system = hd_to_system(namespace, universal_id, universal_id_type, config)
    if system:
        out['system'] = system

    # .. and the identifier type code becomes a v2-0203 coding.
    type_code = component_value(repetition, 5)
    if type_code:
        out['type'] = {'coding': [{'system': Identifier_Type_System, 'code': type_code}]}

    return out

# ################################################################################################################################

def ei_to_identifier(repetition:'anylist', config:'FHIRMappingConfig') -> 'dictnone':
    """ Converts an EI - entity identifier - repetition to a FHIR Identifier.
    """
    value = component_value(repetition, 1)
    if not value:
        return None

    # Our response to produce
    out:'stranydict' = {'value': value}

    namespace = component_value(repetition, 2)
    universal_id = component_value(repetition, 3)
    universal_id_type = component_value(repetition, 4)

    system = hd_to_system(namespace, universal_id, universal_id_type, config)
    if system:
        out['system'] = system

    return out

# ################################################################################################################################

def xpn_to_human_name(repetition:'anylist', config:'FHIRMappingConfig') -> 'dictnone':
    """ Converts an XPN - extended person name - repetition to a FHIR HumanName.
    """

    # Our response to produce
    out:'stranydict' = {}

    # The family name is the first subcomponent of the first component
    family = subcomponent_value(repetition, 1, 1)
    if family:
        out['family'] = family

    # Given names collect the given name and any further given names ..
    given:'anylist' = []

    given_name = component_value(repetition, 2)
    if given_name:
        given.append(given_name)

    further_given = component_value(repetition, 3)
    if further_given:
        given.append(further_given)

    if given:
        out['given'] = given

    # .. the suffix and the academic degree both become FHIR suffixes ..
    suffix:'anylist' = []

    name_suffix = component_value(repetition, 4)
    if name_suffix:
        suffix.append(name_suffix)

    degree = component_value(repetition, 6)
    if degree:
        suffix.append(degree)

    if suffix:
        out['suffix'] = suffix

    prefix = component_value(repetition, 5)
    if prefix:
        out['prefix'] = [prefix]

    # The name type code maps to HumanName.use
    name_type_code = component_value(repetition, 7)
    if use := lookup('name_type', name_type_code, config):
        out['use'] = use['code']

    if not out:
        return None

    return out

# ################################################################################################################################

def xad_to_address(repetition:'anylist', config:'FHIRMappingConfig') -> 'dictnone':
    """ Converts an XAD - extended address - repetition to a FHIR Address.
    """

    # Our response to produce
    out:'stranydict' = {}

    # Address lines collect the street address and the other-designation component ..
    lines:'anylist' = []

    street = subcomponent_value(repetition, 1, 1)
    if street:
        lines.append(street)

    other_designation = component_value(repetition, 2)
    if other_designation:
        lines.append(other_designation)

    if lines:
        out['line'] = lines

    # .. the city, state, postal code and country map one to one ..
    city = component_value(repetition, 3)
    if city:
        out['city'] = city.strip()

    state = component_value(repetition, 4)
    if state:
        out['state'] = state

    postal_code = component_value(repetition, 5)
    if postal_code:
        out['postalCode'] = postal_code

    country = component_value(repetition, 6)
    if country:
        out['country'] = country

    # .. and the address type maps to Address.use.
    address_type_code = component_value(repetition, 7)
    if use := lookup('address_type', address_type_code, config):
        out['use'] = use['code']

    if not out:
        return None

    return out

# ################################################################################################################################

def xtn_to_contact_point(repetition:'anylist', config:'FHIRMappingConfig', default_use:'strnone' = None) -> 'dictnone':
    """ Converts an XTN - extended telecommunication number - repetition to a FHIR ContactPoint.
    """

    # Our response to produce
    out:'stranydict' = {}

    # The value is the email address when there is one, otherwise the full
    # telephone number from XTN-1, otherwise a number built from the area code,
    # local number and extension components.
    email = component_value(repetition, 4)
    telephone = component_value(repetition, 1)

    if email:
        out['value'] = email
        out['system'] = 'email'
    elif telephone:
        out['value'] = telephone
    else:
        parts:'anylist' = []

        country_code = component_value(repetition, 5)
        if country_code:
            parts.append(f'+{country_code}')

        area_code = component_value(repetition, 6)
        if area_code:
            parts.append(area_code)

        local_number = component_value(repetition, 7)
        if local_number:
            parts.append(local_number)

        extension = component_value(repetition, 8)
        if extension:
            parts.append(f'x{extension}')

        if parts:
            out['value'] = ' '.join(parts)

    if not out:
        return None

    # The telecommunication use code maps to ContactPoint.use ..
    use_code = component_value(repetition, 2)
    if use := lookup('telecom_use', use_code, config):
        out['use'] = use['code']
    elif default_use:
        out['use'] = default_use

    # .. and the equipment type maps to ContactPoint.system, unless the value already is an email.
    if 'system' not in out:
        equipment_type = component_value(repetition, 3)
        if system := lookup('telecom_equipment_type', equipment_type, config):
            out['system'] = system['code']
        else:
            out['system'] = 'phone'

    return out

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

    # .. the alternate triplet is a second coding when present ..
    alternate_code = component_value(repetition, 4)
    alternate_text = component_value(repetition, 5)
    alternate_system_name = component_value(repetition, 6)

    if alternate_code:
        alternate_coding:'stranydict' = {'code': alternate_code}

        if alternate_text:
            alternate_coding['display'] = alternate_text

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
    elif code:
        out['text'] = code

    if not out:
        return None

    return out

# ################################################################################################################################

def xcn_to_name_and_identifier(repetition:'anylist', config:'FHIRMappingConfig') -> 'dictnone':
    """ Converts an XCN - extended composite name and ID - repetition to the parts a Practitioner is built from.
    Returns a dict with optional 'identifier' and 'name' keys or None when the repetition is empty.
    """

    # Our response to produce
    out:'stranydict' = {}

    # The person identifier pairs up with the assigning authority from XCN-9 ..
    id_number = component_value(repetition, 1)

    if id_number:
        identifier:'stranydict' = {'value': id_number}

        namespace = subcomponent_value(repetition, 9, 1)
        universal_id = subcomponent_value(repetition, 9, 2)
        universal_id_type = subcomponent_value(repetition, 9, 3)

        system = hd_to_system(namespace, universal_id, universal_id_type, config)
        if system:
            identifier['system'] = system

        identifier_type = component_value(repetition, 13)
        if identifier_type:
            identifier['type'] = {'coding': [{'system': Identifier_Type_System, 'code': identifier_type}]}

        out['identifier'] = identifier

    # .. and the name components build a HumanName the same way an XPN does.
    name:'stranydict' = {}

    family = subcomponent_value(repetition, 2, 1)
    if family:
        name['family'] = family

    given:'anylist' = []

    given_name = component_value(repetition, 3)
    if given_name:
        given.append(given_name)

    further_given = component_value(repetition, 4)
    if further_given:
        given.append(further_given)

    if given:
        name['given'] = given

    suffix:'anylist' = []

    name_suffix = component_value(repetition, 5)
    if name_suffix:
        suffix.append(name_suffix)

    degree = component_value(repetition, 7)
    if degree:
        suffix.append(degree)

    if suffix:
        name['suffix'] = suffix

    prefix = component_value(repetition, 6)
    if prefix:
        name['prefix'] = [prefix]

    if name:
        out['name'] = name

    if not out:
        return None

    return out

# ################################################################################################################################

def dtm_to_datetime(value:'strnone', config:'FHIRMappingConfig') -> 'strnone':
    """ Converts an HL7 DTM value of any precision to a FHIR dateTime string.
    Values without their own timezone offset receive the config's default one.
    """
    if not value:
        return None

    value = value.strip()
    if not value:
        return None

    # Split off the timezone offset if the value carries one ..
    offset = ''

    for sign in ('+', '-'):
        sign_index = value.find(sign)
        if sign_index > 0:
            raw_offset = value[sign_index:]
            value = value[:sign_index]

            # An HL7 offset is +HHMM, a FHIR one is +HH:MM
            offset_digits = raw_offset[1:]
            if len(offset_digits) == 4:
                offset = f'{raw_offset[0]}{offset_digits[:2]}:{offset_digits[2:]}'
            break

    # .. split off fractional seconds, FHIR keeps them after the seconds part ..
    fraction = ''
    dot_index = value.find('.')

    if dot_index > 0:
        fraction = value[dot_index:]
        value = value[:dot_index]

    length = len(value)

    # .. a bare year, year-month or full date has no time part and no offset ..
    if length == _DTM_Year_Length:
        out = value
        return out

    if length == _DTM_Month_Length:
        out = f'{value[:4]}-{value[4:6]}'
        return out

    if length == _DTM_Day_Length:
        out = f'{value[:4]}-{value[4:6]}-{value[6:8]}'
        return out

    # .. anything longer carries a time and needs an offset, defaulting to the configured one ..
    if not offset:
        offset = config.default_timezone

    date_part = f'{value[:4]}-{value[4:6]}-{value[6:8]}'

    if length == _DTM_Hour_Length:
        time_part = f'{value[8:10]}:00:00'
    elif length == _DTM_Minute_Length:
        time_part = f'{value[8:10]}:{value[10:12]}:00'
    elif length >= _DTM_Second_Length:
        time_part = f'{value[8:10]}:{value[10:12]}:{value[12:14]}{fraction}'

    # .. anything else is not a value we can make sense of.
    else:
        return None

    out = f'{date_part}T{time_part}{offset}'
    return out

# ################################################################################################################################

def dtm_to_date(value:'strnone') -> 'strnone':
    """ Converts an HL7 DTM value to a FHIR date string, dropping any time part.
    """
    if not value:
        return None

    value = value.strip()
    if not value:
        return None

    length = len(value)

    if length >= _DTM_Day_Length:
        out = f'{value[:4]}-{value[4:6]}-{value[6:8]}'
        return out

    if length == _DTM_Month_Length:
        out = f'{value[:4]}-{value[4:6]}'
        return out

    if length == _DTM_Year_Length:
        out = value
        return out

    return None

# ################################################################################################################################

def _quantity(value:'float', units:'dictnone') -> 'stranydict':
    """ Builds a FHIR Quantity from a number and an optional units concept.
    """

    # Our response to produce
    out:'stranydict' = {'value': value}

    if units:
        coding_list = units.get('coding')
        if coding_list:
            first_coding = coding_list[0]

            out['code'] = first_coding['code']
            if 'system' in first_coding:
                out['system'] = first_coding['system']

        if 'text' in units:
            out['unit'] = units['text']

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

def sn_to_observation_value(repetition:'anylist', config:'FHIRMappingConfig', units:'dictnone') -> 'tuple[str, stranydict | str] | None':
    """ Converts an SN - structured numeric - repetition to a FHIR observation value.
    Returns the value field name and its content, following the six-way branch the
    comparator, number, separator and second number combinations call for.
    """
    comparator = component_value(repetition, 1)
    first_number = component_value(repetition, 2)
    separator = component_value(repetition, 3)
    second_number = component_value(repetition, 4)

    first_value = _parse_number(first_number)
    second_value = _parse_number(second_number)

    # A plain number, with or without a comparator, becomes a Quantity ..
    if first_value is not None:
        if not separator:
            quantity = _quantity(first_value, units)

            if comparator:
                quantity['comparator'] = comparator

            out = ('valueQuantity', quantity)
            return out

        # .. a range like 3 - 5 becomes a Range ..
        if separator == '-':
            if second_value is not None:
                low = _quantity(first_value, units)
                high = _quantity(second_value, units)

                out = ('valueRange', {'low': low, 'high': high})
                return out

        # .. a ratio like 1 : 128 or 1 / 128 becomes a Ratio ..
        if separator in (':', '/'):
            if second_value is not None:
                numerator = _quantity(first_value, units)
                denominator = _quantity(second_value, units)

                out = ('valueRatio', {'numerator': numerator, 'denominator': denominator})
                return out

        # .. a plus after the number, like 2 +, marks categorical results and stays a string.
        if separator == '+':
            out = ('valueString', f'{first_number}+')
            return out

    # Anything else is preserved as the string the components spell out
    parts:'anylist' = []

    for component in (comparator, first_number, separator, second_number):
        if component:
            parts.append(component)

    if parts:
        out = ('valueString', ''.join(parts))
        return out

    return None

# ################################################################################################################################
# ################################################################################################################################
