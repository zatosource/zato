# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.fhir import Patient, RelatedPerson
from zato.hl7.mappings.codes import lookup
from zato.hl7.mappings.concepts import cwe_to_codeable_concept, cwe_to_language_concept, tag_coding_systems
from zato.hl7.mappings.datatypes import Identifier_Type_System, cx_to_identifier, xad_to_address, xpn_to_human_name, \
    xtn_to_contact_points
from zato.hl7.mappings.fields import component_value, serialize_repetition
from zato.hl7.mappings.segments.common import Birth_Place_Extension_URL, Ethnicity_Extension_URL, \
    Mothers_Maiden_Name_Extension_URL, No_Consumed_Fields, Race_Extension_URL, Religion_Extension_URL, \
    add_named_organization, add_practitioner, append_to_list_field, patient_or_absent_reference, preserve_unmapped, \
    preserve_value

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
_PID_Handled = frozenset({
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 29, 30,
})
_PD1_Handled = frozenset({3, 4})
_NK1_Handled = frozenset({1, 2, 3, 4, 5, 6, 7, 8, 9, 15, 16})
_MRG_Handled = frozenset({1, 7})
_GT1_Handled = frozenset({1, 2, 3, 5, 6, 7, 8, 9, 11})

# The personal relationship code a mother has to the patient
_Mother_Relationship_Code = 'MTH'

# The type of the link from the patient to the mother's RelatedPerson
Mother_Link_Type = 'seealso'

# The identifier type code a driver's license number carries
_Drivers_License_Type = 'DL'

# The values an HL7 yes/no indicator may take
_Yes_Indicator     = 'Y'
_Yes_No_Indicators = ('Y', 'N')

# The CDC Race and Ethnicity vocabulary PID-10 and PID-22 codes come from
_CDC_Coding_System_Name = 'CDCREC'
_CDC_Coding_System_URI = 'urn:oid:2.16.840.1.113883.6.238'

# The OMB top-level categories - all the other CDC codes go to the detailed sub-extension
_OMB_Race_Categories = frozenset({'1002-5', '2028-9', '2054-5', '2076-8', '2106-3'})
_OMB_Ethnicity_Categories = frozenset({'2135-2', '2186-5'})

# ################################################################################################################################
# ################################################################################################################################

def _add_cdc_extension(
    accessor:'SegmentAccessor',
    position:'int',
    extension_url:'str',
    omb_categories:'frozenset',
    patient:'Patient',
    ) -> 'bool':
    """ Builds a US Core race or ethnicity extension from a CDC-coded CWE field.
    Returns True only when every populated repetition carries the CDC vocabulary,
    otherwise the whole field stays with the caller to preserve as-is.
    """
    repetitions = accessor.repetitions(position)
    if not repetitions:
        return False

    sub_extensions:'anylist' = []
    texts:'anylist' = []

    for repetition in repetitions:
        code = component_value(repetition, 1)
        display = component_value(repetition, 2)
        system_name = component_value(repetition, 3)

        # A repetition outside the CDC vocabulary keeps the whole field unmapped.
        if system_name != _CDC_Coding_System_Name:
            return False

        if not code:
            return False

        coding = {'system': _CDC_Coding_System_URI, 'code': code}

        if display:
            coding['display'] = display
            texts.append(display)
        else:
            texts.append(code)

        # An OMB top-level category goes to its own sub-extension, anything else is a detailed code.
        if code in omb_categories:
            url = 'ombCategory'
        else:
            url = 'detailed'

        sub_extensions.append({'url': url, 'valueCoding': coding})

    # The text sub-extension is required and gathers all the displays.
    text = ', '.join(texts)
    sub_extensions.append({'url': 'text', 'valueString': text})

    extension = {'url': extension_url, 'extension': sub_extensions}
    append_to_list_field(patient, 'extension', extension)

    return True

# ################################################################################################################################

def _add_text_extension(
    accessor:'SegmentAccessor',
    position:'int',
    extension_url:'str',
    patient:'Patient',
    ) -> 'None':
    """ Builds a US Core race or ethnicity extension carrying text only, from a CWE field
    coded in any vocabulary but the CDC one. A code outside the CDC vocabulary becomes
    text next to its display.
    """

    # Each repetition contributes what it has - a display, a code, or both ..
    texts:'anylist' = []

    for repetition in accessor.repetitions(position):
        code = component_value(repetition, 1)
        display = component_value(repetition, 2)

        if display:
            if code:
                if code != display:
                    both = f'{display} ({code})'
                    texts.append(both)
                else:
                    texts.append(display)
            else:
                texts.append(display)
        elif code:
            texts.append(code)

    # .. a field with nothing in it builds no extension ..
    if not texts:
        return

    # .. and everything gathered goes in as one text.
    text = ', '.join(texts)
    sub_extensions = [{'url': 'text', 'valueString': text}]

    extension = {'url': extension_url, 'extension': sub_extensions}
    append_to_list_field(patient, 'extension', extension)

# ################################################################################################################################

def map_pid_mother(
    accessor:'SegmentAccessor',
    context:'ConversionContext',
    patient:'Patient',
    ) -> 'RelatedPerson | None':
    """ Turns the mother's identifiers in PID-21 into a RelatedPerson - the mother - of the patient.
    Returns None when the field is empty, an identifier that does not read as a CX is preserved on the patient.
    """
    # Our response to produce
    out = RelatedPerson()

    config = context.config

    # An empty PID-21 names no mother ..
    repetitions = accessor.repetitions(21)

    if not repetitions:
        return None

    # .. each repetition that reads as a CX is one of her identifiers,
    # .. anything else is preserved on the patient ..
    identifiers:'anylist' = []

    for repetition in repetitions:
        if identifier := cx_to_identifier(repetition, config):
            identifiers.append(identifier)
        else:
            serialized = serialize_repetition(repetition)
            preserve_value(patient, context, 'PID', 21, serialized)

    if not identifiers:
        return None

    # .. and the mother relates to the patient as her child's mother.
    out.patient = patient_or_absent_reference(context)
    out.identifier = identifiers

    if relationship := lookup('personal_relationship', _Mother_Relationship_Code, config):
        coding = {'system': relationship['system'], 'code': relationship['code']}
        out.relationship = [{'coding': [coding]}]

    return out

# ################################################################################################################################

def map_pid(accessor:'SegmentAccessor', context:'ConversionContext') -> 'Patient':
    """ Converts PID to a Patient.
    """
    config = context.config

    # Our response to produce
    out = Patient()

    # Every patient identifier becomes a FHIR identifier ..
    identifiers:'anylist' = []

    for position in (3, 2, 4):
        for repetition in accessor.repetitions(position):
            if identifier := cx_to_identifier(repetition, config):
                if identifier not in identifiers:
                    identifiers.append(identifier)

    # .. including the patient account number ..
    for repetition in accessor.repetitions(18):
        if identifier := cx_to_identifier(repetition, config):
            identifiers.append(identifier)

    # .. the social security number - the field carries a bare value with no authority,
    # .. so the identifier gets the SS type code and no system of its own ..
    ssn = accessor.value(19)
    if ssn:
        ssn_identifier = {
            'value': ssn,
            'type': {'coding': [{'system': Identifier_Type_System, 'code': 'SS'}]},
        }
        identifiers.append(ssn_identifier)

    # .. and the driver's license number - a populated assigning authority or type code
    # .. means the slot holds a whole CX identifier instead.
    license_repetition = accessor.first(20)
    drivers_license = component_value(license_repetition, 1)

    if drivers_license:
        license_authority = component_value(license_repetition, 4)
        license_type_code = component_value(license_repetition, 5)

        if license_authority:
            is_cx_shaped = True
        elif license_type_code:
            is_cx_shaped = True
        else:
            is_cx_shaped = False

        if is_cx_shaped:
            if identifier := cx_to_identifier(license_repetition, config):
                identifiers.append(identifier)
        else:
            license_identifier:'stranydict' = {
                'value': drivers_license,
                'type': {'coding': [{'system': Identifier_Type_System, 'code': _Drivers_License_Type}]},
            }

            # The issuing state names the license's assigner ..
            issuing_state = component_value(license_repetition, 2)
            if issuing_state:
                license_identifier['assigner'] = {'display': issuing_state}

            # .. and the expiration date closes its validity period - a value that
            # .. is not a date at all is preserved whole instead of being dropped.
            expiration = component_value(license_repetition, 3)
            if expiration:
                if expiration_date := context.date(expiration, 'PID', 20):
                    license_identifier['period'] = {'end': expiration_date}
                else:
                    serialized_license = accessor.serialize(20)
                    preserve_value(out, context, 'PID', 20, serialized_license)

            identifiers.append(license_identifier)

    if identifiers:
        out.identifier = identifiers

    # Every repetition of the name field becomes a HumanName, with aliases from PID-9 after them.
    names:'anylist' = []

    for position in (5, 9):
        for repetition in accessor.repetitions(position):
            if name := xpn_to_human_name(repetition, config):
                names.append(name)

    if names:
        out.name = names

    # The birth date drops any time part, per FHIR's Patient.birthDate being a date.
    birth_value = accessor.value(7)
    birth_date = context.date(birth_value, 'PID', 7)

    if birth_date:
        out.birthDate = birth_date

    # The administrative sex maps to the gender code, unknown codes are preserved as-is.
    sex_code = accessor.value(8)
    if sex_code:
        if gender := lookup('administrative_sex', sex_code, config):
            out.gender = gender['code']
        else:
            preserve_value(out, context, 'PID', 8, sex_code)

    # Addresses map one to one.
    addresses:'anylist' = []

    for repetition in accessor.repetitions(11):
        if address := xad_to_address(repetition, config):
            addresses.append(address)

    if addresses:
        out.address = addresses

    # Home and business telecoms merge into one list, each with its use filled in.
    telecoms:'anylist' = []

    for repetition in accessor.repetitions(13):
        for telecom in xtn_to_contact_points(repetition, config, default_use='home'):
            telecoms.append(telecom)

    for repetition in accessor.repetitions(14):
        for telecom in xtn_to_contact_points(repetition, config, default_use='work'):
            telecoms.append(telecom)

    if telecoms:
        out.telecom = telecoms

    # The primary language becomes a communication entry.
    language_repetition = accessor.first(15)

    if language := cwe_to_language_concept(language_repetition, config):
        out.communication = [{'language': language, 'preferred': True}]

    # The marital status maps through the standard table, unknown codes are preserved as-is.
    marital_code = accessor.value(16)
    if marital_code:
        if marital_status := lookup('marital_status', marital_code, config):
            coding = {'system': marital_status['system'], 'code': marital_status['code']}
            out.maritalStatus = {'coding': [coding]}
        else:
            preserve_value(out, context, 'PID', 16, marital_code)

    # The mother's maiden name and the religion go to their standard extensions ..
    maiden_name = accessor.component(6, 1)
    if maiden_name:
        maiden_extension = {'url': Mothers_Maiden_Name_Extension_URL, 'valueString': maiden_name}
        append_to_list_field(out, 'extension', maiden_extension)

    religion_repetition = accessor.first(17)

    if religion := cwe_to_codeable_concept(religion_repetition, config):
        religion_extension = {'url': Religion_Extension_URL, 'valueCodeableConcept': religion}
        append_to_list_field(out, 'extension', religion_extension)

    # .. and so does the birth place.
    birth_place = accessor.value(23)
    if birth_place:
        birth_place_extension = {'url': Birth_Place_Extension_URL, 'valueAddress': {'text': birth_place}}
        append_to_list_field(out, 'extension', birth_place_extension)

    # Multiple-birth data prefers the order number over the yes/no indicator,
    # an order that is not a number and an indicator that is neither yes nor no are preserved as-is.
    birth_order     = accessor.value(25)
    multiple_birth  = accessor.value(24)
    has_birth_order = False

    if birth_order:
        if birth_order.isdigit():
            out.multipleBirthInteger = int(birth_order)
            has_birth_order = True
        else:
            preserve_value(out, context, 'PID', 25, birth_order)

    if not has_birth_order:
        if multiple_birth:
            if multiple_birth in _Yes_No_Indicators:
                out.multipleBirthBoolean = multiple_birth == _Yes_Indicator
            else:
                preserve_value(out, context, 'PID', 24, multiple_birth)

    # Death data prefers the timestamp over the yes/no indicator, a timestamp that
    # is not a date/time at all and an indicator that is neither yes nor no are preserved as-is.
    death_value = accessor.value(29)
    death_datetime = context.datetime(death_value, 'PID', 29)
    death_indicator = accessor.value(30)

    if death_datetime:
        out.deceasedDateTime = death_datetime
    else:
        if death_value:
            preserve_value(out, context, 'PID', 29, death_value)

        if death_indicator:
            if death_indicator in _Yes_No_Indicators:
                out.deceasedBoolean = death_indicator == _Yes_Indicator
            else:
                preserve_value(out, context, 'PID', 30, death_indicator)

    # The race and the ethnic group map to their US Core extensions - fully coded when they
    # come from the CDC vocabulary, as text when they come from any other.
    if not _add_cdc_extension(accessor, 10, Race_Extension_URL, _OMB_Race_Categories, out):
        _add_text_extension(accessor, 10, Race_Extension_URL, out)

    if not _add_cdc_extension(accessor, 22, Ethnicity_Extension_URL, _OMB_Ethnicity_Categories, out):
        _add_text_extension(accessor, 22, Ethnicity_Extension_URL, out)

    preserve_unmapped(accessor, _PID_Handled, out, context)

    return out

# ################################################################################################################################

def enrich_pd1(accessor:'SegmentAccessor', context:'ConversionContext', patient:'Patient') -> 'None':
    """ Adds the primary care provider and primary facility from PD1 to an existing Patient.
    """
    general_practitioners:'anylist' = []

    # The patient's primary facility becomes an Organization, keeping its XON-3 identifier ..
    for repetition in accessor.repetitions(3):
        organization_name = component_value(repetition, 1)
        if organization_name:
            organization_id = component_value(repetition, 3)
            if organization_id is None:
                organization_id = ''
            reference = add_named_organization(organization_name, context, organization_id)
            general_practitioners.append(reference)

    # .. and the primary care provider becomes a Practitioner.
    for repetition in accessor.repetitions(4):
        if reference := add_practitioner(repetition, context):
            general_practitioners.append(reference)

    if general_practitioners:
        patient.generalPractitioner = general_practitioners

    preserve_unmapped(accessor, _PD1_Handled, patient, context)

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

def apply_mrg(accessor:'SegmentAccessor', context:'ConversionContext', patient:'Patient') -> 'None':
    """ Turns MRG into an inactive Patient carrying the prior identifiers,
    linked from the surviving Patient as the record it replaces.
    """
    config = context.config

    old_patient = Patient()
    old_patient.active = False

    identifiers:'anylist' = []

    for repetition in accessor.repetitions(1):
        if identifier := cx_to_identifier(repetition, config):
            identifiers.append(identifier)

    if identifiers:
        old_patient.identifier = identifiers

    names:'anylist' = []

    for repetition in accessor.repetitions(7):
        if name := xpn_to_human_name(repetition, config):
            names.append(name)

    if names:
        old_patient.name = names

    preserve_unmapped(accessor, _MRG_Handled, old_patient, context)

    old_reference = context.add(old_patient)

    # The surviving patient records that it replaces the prior one.
    link = {'other': old_reference, 'type': 'replaces'}
    append_to_list_field(patient, 'link', link)

# ################################################################################################################################

def apply_pda(accessor:'SegmentAccessor', context:'ConversionContext', patient:'Patient') -> 'None':
    """ Applies PDA - the patient death advice - to the Patient. The segment's presence
    marks the patient as deceased unless PID already said when, and every populated
    field is preserved as-is.
    """
    current = patient.to_dict()

    # PID-29 and PID-30 take precedence over the advice's mere presence.
    if 'deceasedDateTime' not in current:
        if 'deceasedBoolean' not in current:
            patient.deceasedBoolean = True

    preserve_unmapped(accessor, No_Consumed_Fields, patient, context)

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
