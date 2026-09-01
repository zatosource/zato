# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7.mappings.codes import coding_system_to_uri, lookup
from zato.hl7.mappings.config import Authority_URN_Prefix, Land_Identifier_Systems, Practitioner_Authority_Systems
from zato.hl7.mappings.datetimes import dtm_to_date, dtm_to_datetime
from zato.hl7.mappings.fields import component_value, subcomponent_value

# For flake8
dtm_to_date = dtm_to_date
dtm_to_datetime = dtm_to_datetime

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, stranydict, strlist, strnone, strstrdict
    from zato.hl7.mappings.config import FHIRMappingConfig
    FHIRMappingConfig = FHIRMappingConfig

# ################################################################################################################################
# ################################################################################################################################

# Type aliases
dictnone = 'stranydict | None'
value_pair = tuple[str, 'stranydict | str']

# The identifier type code system of all CX-5 and XCN-13 values
Identifier_Type_System = 'http://terminology.hl7.org/CodeSystem/v2-0203'

# The system that marks an equipment type as mapping to ContactPoint.use rather than .system
_Contact_Point_Use_System = 'http://hl7.org/fhir/contact-point-use'

# The system a telephone-carrying contact point gets when nothing else decides one
_Default_Contact_System = 'phone'

# The longest value XTN-8 can hold and still be an extension - anything longer
# is a whole telephone number that arrived in that slot.
_Max_Extension_Length = 5

# The system spoken-language codes belong to
Language_Coding_System = 'urn:ietf:bcp:47'

# The lengths ISO 639 language codes come in - two-letter 639-1 and three-letter 639-2 codes.
_ISO_639_Lengths = (2, 3)

# ################################################################################################################################
# ################################################################################################################################

def hd_to_system(
    namespace:'strnone',
    universal_id:'strnone',
    universal_id_type:'strnone',
    config:'FHIRMappingConfig',
    authority_systems:'strstrdict | None' = None,
    ) -> 'strnone':
    """ Derives an identifier system URI from an HD - assigning authority - value.
    """
    if universal_id:
        if universal_id_type == 'ISO':

            out = f'urn:oid:{universal_id}'
            return out

        if universal_id_type == 'UUID':
            universal_id_lower = universal_id.lower()

            out = f'urn:uuid:{universal_id_lower}'
            return out

    if namespace:
        namespace = namespace.strip()

    if not namespace:
        return None

    # A configured system URI for this authority wins ..
    if configured_system := config.identifier_systems.get(namespace):

        out = configured_system
        return out

    # .. an authority whose registry depends on who holds the identifier
    # .. resolves through the caller's holder-specific map ..
    if authority_systems:
        if holder_system := authority_systems.get(namespace):

            out = holder_system
            return out

    # .. a land authority maps to its official system URI ..
    if land_system := Land_Identifier_Systems.get(namespace):

        out = land_system
        return out

    # .. otherwise the authority name becomes a stable URN.
    out = Authority_URN_Prefix + namespace
    return out

# ################################################################################################################################

def cx_to_identifier(
    repetition:'anylist',
    config:'FHIRMappingConfig',
    authority_systems:'strstrdict | None' = None,
    ) -> 'dictnone':
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

    system = hd_to_system(namespace, universal_id, universal_id_type, config, authority_systems)
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

def fn_to_family_name(repetition:'anylist', component:'int') -> 'strnone':
    """ Builds the family name of an FN - family name - component. The full surname
    subcomponent wins when present, otherwise the name is composed from the own-surname
    and partner-surname subcomponents the FN type defines.
    """
    surname = subcomponent_value(repetition, component, 1)
    if surname:

        out = surname
        return out

    parts:'strlist' = []

    # FN.2 to FN.5 - own surname prefix, own surname, partner surname prefix, partner surname.
    for subcomponent in (2, 3, 4, 5):
        part = subcomponent_value(repetition, component, subcomponent)
        if part:
            parts.append(part)

    if parts:

        out = ' '.join(parts)
        return out

    return None

# ################################################################################################################################

def xpn_to_human_name(repetition:'anylist', config:'FHIRMappingConfig') -> 'dictnone':
    """ Converts an XPN - extended person name - repetition to a FHIR HumanName.
    """

    # Our response to produce
    out:'stranydict' = {}

    # The family name is an FN component.
    family = fn_to_family_name(repetition, 1)
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

    # .. and the prefix stays a prefix.
    prefix = component_value(repetition, 5)
    if prefix:
        out['prefix'] = [prefix]

    # The name type code maps to HumanName.use.
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

def xtn_to_contact_points(repetition:'anylist', config:'FHIRMappingConfig', default_use:'strnone' = None) -> 'anylist':
    """ Converts an XTN - extended telecommunication number - repetition to a list of FHIR ContactPoints.
    One repetition can carry both a telephone number and an email address, each becomes its own point.
    """

    # Our response to produce
    out:'anylist' = []

    # The equipment type decides the system - and for a cellular phone the use -
    # ahead of any guessing from where the value sits.
    equipment_type = component_value(repetition, 3)
    equipment = lookup('telecom_equipment_type', equipment_type, config)

    equipment_system = None
    equipment_use = None

    if equipment:
        if equipment['system'] == _Contact_Point_Use_System:
            equipment_use = equipment['code']
            equipment_system = _Default_Contact_System
        else:
            equipment_system = equipment['code']

    email = component_value(repetition, 4)
    telephone = component_value(repetition, 1)

    # Equipment codes can arrive in the email and number components -
    # those refine the system or the use instead of becoming values or number parts.
    def _as_equipment(value:'str') -> 'bool':
        nonlocal equipment_system, equipment_use

        shifted_equipment = lookup('telecom_equipment_type', value, config)
        if not shifted_equipment:
            return False

        if shifted_equipment['system'] == _Contact_Point_Use_System:
            equipment_use = shifted_equipment['code']
            if not equipment_system:
                equipment_system = _Default_Contact_System
        else:
            equipment_system = shifted_equipment['code']

        return True

    if email:
        if _as_equipment(email):
            email = None

    # The telephone number is XTN-1 when populated, otherwise it is built
    # from the country code, area code, local number and extension components.
    phone_value = telephone

    if not phone_value:
        parts:'anylist' = []

        country_code = component_value(repetition, 5)
        if country_code:
            if not _as_equipment(country_code):
                prefixed_country_code = f'+{country_code}'
                parts.append(prefixed_country_code)

        area_code = component_value(repetition, 6)
        if area_code:
            if not _as_equipment(area_code):
                parts.append(area_code)

        local_number = component_value(repetition, 7)
        if local_number:
            if not _as_equipment(local_number):
                parts.append(local_number)

        # An extension only makes sense after a number and is short - anything longer
        # is a whole telephone number that arrived in this slot, and stays a number.
        extension = component_value(repetition, 8)
        if extension:
            extension_length = len(extension)
            if parts:
                if extension_length <= _Max_Extension_Length:
                    marked_extension = f'x{extension}'
                    parts.append(marked_extension)
                else:
                    parts.append(extension)
            else:
                parts.append(extension)

        if parts:
            phone_value = ' '.join(parts)

    # The telecommunication use code from XTN-2 applies to every point of the repetition.
    use = None

    use_code = component_value(repetition, 2)
    if use_entry := lookup('telecom_use', use_code, config):
        use = use_entry['code']
    elif default_use:
        use = default_use

    if phone_value:
        phone_point:'stranydict' = {'value': phone_value}

        if use:
            phone_point['use'] = use

        # A cellular phone's equipment type overrides the generic use code.
        if equipment_use:
            phone_point['use'] = equipment_use

        # With an email alongside, an internet equipment type describes the email,
        # not the telephone number.
        phone_system = equipment_system

        if email:
            if phone_system == 'email':
                phone_system = _Default_Contact_System

        if not phone_system:
            phone_system = _Default_Contact_System

        phone_point['system'] = phone_system

        out.append(phone_point)

    if email:
        email_point:'stranydict' = {'value': email}

        if use:
            email_point['use'] = use

        # Alongside a telephone number XTN-4 is a real email - on its own it takes
        # the equipment type as-is, since plain telephone numbers arrive there too.
        if phone_value:
            email_point['system'] = 'email'
        else:
            if equipment_use:
                email_point['use'] = equipment_use

            if equipment_system:
                email_point['system'] = equipment_system
            else:
                email_point['system'] = 'email'

        out.append(email_point)

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

        # An XCN always identifies a person, so person-registry authorities apply.
        system = hd_to_system(namespace, universal_id, universal_id_type, config, Practitioner_Authority_Systems)
        if system:
            identifier['system'] = system

        identifier_type = component_value(repetition, 13)
        if identifier_type:
            identifier['type'] = {'coding': [{'system': Identifier_Type_System, 'code': identifier_type}]}

        out['identifier'] = identifier

    # .. and the name components build a HumanName the same way an XPN does.
    name:'stranydict' = {}

    family = fn_to_family_name(repetition, 2)
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
