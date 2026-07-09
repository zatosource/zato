# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64encode

# Zato
from zato.fhir import AllergyIntolerance, Appointment, Basic, Condition, Coverage, DiagnosticReport, DocumentReference, \
    Encounter, Immunization, Location, MessageHeader, Observation, Organization, Patient, Practitioner, Procedure, \
    RelatedPerson, ServiceRequest, Specimen
from zato.hl7.mappings.codes import lookup
from zato.hl7.mappings.datatypes import Identifier_Type_System, cwe_to_codeable_concept, cx_to_identifier, dtm_to_date, \
    dtm_to_datetime, ei_to_identifier, hd_to_system, sn_to_observation_value, xad_to_address, xcn_to_name_and_identifier, \
    xpn_to_human_name, xtn_to_contact_point
from zato.hl7.mappings.fields import component_value, subcomponent_value

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict, strlist, strnone
    from zato.hl7.mappings.context import ConversionContext
    from zato.hl7.mappings.fields import SegmentAccessor
    ConversionContext = ConversionContext
    SegmentAccessor = SegmentAccessor

# ################################################################################################################################
# ################################################################################################################################

# Type aliases
dictnone = 'stranydict | None'
intfrozen = frozenset[int]

# The status an Encounter gets when the patient class does not say otherwise
Default_Encounter_Status = 'in-progress'

# The class an Encounter gets when PV1-2 is empty or carries an unknown code - FHIR requires one
Default_Encounter_Class = {'system': 'http://terminology.hl7.org/CodeSystem/v3-NullFlavor', 'code': 'UNK'}

# The code an Observation or DiagnosticReport gets when the message carries none - FHIR requires one
Unknown_Code = {'text': 'unknown'}

# The name the payor Organization gets when IN1 does not identify the insurance company
Unknown_Payor_Name = 'unknown'

# The status an Encounter gets once a discharge time is present
Finished_Encounter_Status = 'finished'

# The status an Observation gets when OBX-11 is empty or carries an unknown code
Default_Observation_Status = 'unknown'

# The status a ServiceRequest gets when ORC-5 is empty or carries an unknown code
Default_Order_Status = 'unknown'

# The status a DiagnosticReport gets when OBR-25 is empty or carries an unknown code
Default_Report_Status = 'unknown'

# The status an Appointment gets when SCH-25 is empty or carries an unknown code
Default_Appointment_Status = 'booked'

# The status an Immunization gets when RXA-20 is empty or carries an unknown code
Default_Immunization_Status = 'completed'

# The status a Procedure derived from PR1 always has - the procedure was performed
Procedure_Status = 'completed'

# The status a Coverage derived from IN1 always has
Coverage_Status = 'active'

# The status a DocumentReference derived from TXA always has
Document_Status = 'current'

# The endpoint a MessageHeader source or destination gets when MSH carries no usable value
Default_Message_Endpoint = 'urn:zato:hl7v2:unknown'

# The identifier system United States social security numbers live in
SSN_System = 'http://hl7.org/fhir/sid/us-ssn'

# Where Encounter participant type codes live
Participation_Type_System = 'http://terminology.hl7.org/CodeSystem/v3-ParticipationType'

# Where message event codes live
Message_Event_System = 'http://terminology.hl7.org/CodeSystem/v2-0003'

# Where Coverage class type codes live
Coverage_Class_System = 'http://terminology.hl7.org/CodeSystem/coverage-class'

# The extension all birth places go to
Birth_Place_Extension_URL = 'http://hl7.org/fhir/StructureDefinition/patient-birthPlace'

# The OBX value types whose content is plain text
Text_Value_Types = ('ST', 'TX', 'FT')

# The OBX value types that become CodeableConcepts
Coded_Value_Types = ('CE', 'CWE', 'CNE', 'CF', 'IS')

# The OBX value types that become dateTimes
Datetime_Value_Types = ('DT', 'DTM', 'TS')

# The IN1-17 code that says the insured person is the patient
Self_Relationship_Code = 'SEL'

# ################################################################################################################################
# ################################################################################################################################

# Which field positions each mapper consumes - anything else that carries data produces a warning
_MSH_Handled = frozenset({1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12})
_EVN_Handled = frozenset({1, 2, 3, 4, 5, 6, 7})
_PID_Handled = frozenset({1, 3, 5, 7, 8, 11, 13, 14, 15, 16, 18, 19, 23, 24, 25, 29, 30})
_PD1_Handled = frozenset({3, 4})
_NK1_Handled = frozenset({1, 2, 3, 4, 5, 6})
_PV1_Handled = frozenset({1, 2, 3, 4, 6, 7, 8, 9, 10, 14, 17, 19, 44, 45})
_PV2_Handled = frozenset({3})
_OBX_Handled = frozenset({1, 2, 3, 5, 6, 7, 8, 11, 14, 16})
_AL1_Handled = frozenset({1, 2, 3, 4, 5})
_DG1_Handled = frozenset({1, 3, 5, 6, 15, 19})
_PR1_Handled = frozenset({1, 3, 5, 11})
_IN1_Handled = frozenset({1, 2, 3, 4, 8, 12, 13, 15, 16, 17, 36})
_ORC_Handled = frozenset({1, 2, 3, 9, 12})
_OBR_Handled = frozenset({1, 2, 3, 4, 7, 16, 22, 25})
_SPM_Handled = frozenset({1, 2, 4, 17})
_SCH_Handled = frozenset({1, 2, 6, 8, 9, 10, 11, 25})
_AIS_Handled = frozenset({1, 2, 3})
_AIG_Handled = frozenset({1, 2, 3, 4})
_AIL_Handled = frozenset({1, 2, 3, 4})
_AIP_Handled = frozenset({1, 2, 3, 4})
_OBX_Text_Handled = frozenset({1, 2, 3, 5, 11, 14})
_RXA_Handled = frozenset({1, 2, 3, 5, 6, 7, 10, 15, 16, 17, 20})
_RXR_Handled = frozenset({1, 2})
_TXA_Handled = frozenset({1, 2, 12})

# ################################################################################################################################
# ################################################################################################################################

def append_to_list_field(resource:'any_', field_name:'str', item:'stranydict') -> 'None':
    """ Appends one item to a list field of a typed resource, keeping what is already there.
    Reading an unset list field would auto-vivify an empty element, so the current state
    comes from the resource's serialized form instead.
    """
    current = resource.to_dict()

    if field_name in current:
        items = current[field_name]
    else:
        items = []

    items.append(item)
    setattr(resource, field_name, items)

# ################################################################################################################################

def warn_unmapped(accessor:'SegmentAccessor', handled:'intfrozen', context:'ConversionContext') -> 'None':
    """ Records a warning for every populated field the mapper did not consume.
    """
    populated = accessor.populated_positions()
    unmapped = populated - handled

    for position in sorted(unmapped):
        context.warn(f'{accessor.segment_id}-{position} not mapped')

# ################################################################################################################################

def mark_evn_handled(accessor:'SegmentAccessor', context:'ConversionContext') -> 'None':
    """ EVN produces no resource of its own - its recorded time repeats what MSH-7 already says -
    but any field beyond the standard ones still deserves a warning.
    """
    warn_unmapped(accessor, _EVN_Handled, context)

# ################################################################################################################################

def add_practitioner(repetition:'anylist', context:'ConversionContext') -> 'dictnone':
    """ Builds a Practitioner from an XCN repetition, adds it to the bundle and returns a reference.
    Identical practitioners referenced from different fields collapse into one resource.
    """
    parts = xcn_to_name_and_identifier(repetition, context.config)
    if not parts:
        return None

    practitioner = Practitioner()

    if 'identifier' in parts:
        practitioner.identifier = [parts['identifier']]

    if 'name' in parts:
        practitioner.name = [parts['name']]

    out = context.add(practitioner)
    return out

# ################################################################################################################################

def add_location(repetition:'anylist', context:'ConversionContext') -> 'dictnone':
    """ Builds a Location from a PL repetition, adds it to the bundle and returns a reference.
    The location's name spells out the point of care, room, bed and facility.
    """
    parts:'strlist' = []

    point_of_care = component_value(repetition, 1)
    if point_of_care:
        parts.append(point_of_care)

    room = component_value(repetition, 2)
    if room:
        parts.append(room)

    bed = component_value(repetition, 3)
    if bed:
        parts.append(bed)

    facility = subcomponent_value(repetition, 4, 1)
    if facility:
        parts.append(facility)

    if not parts:
        return None

    location = Location()
    location.name = '-'.join(parts)

    out = context.add(location)
    return out

# ################################################################################################################################

def map_msh(accessor:'SegmentAccessor', context:'ConversionContext') -> 'MessageHeader':
    """ Converts MSH to a MessageHeader with the sending and receiving systems.
    """
    config = context.config

    # Our response to produce
    out = MessageHeader()

    # The trigger event identifies what kind of message this is ..
    event_code = accessor.component(9, 2)
    if not event_code:
        event_code = accessor.component(9, 1)

    event_coding:'stranydict' = {'system': Message_Event_System}
    if event_code:
        event_coding['code'] = event_code

    out.eventCoding = event_coding

    # .. the sending application and facility become the source ..
    source:'stranydict' = {}

    sending_application = accessor.component(3, 1)
    sending_universal_id = accessor.component(3, 2)
    sending_universal_id_type = accessor.component(3, 3)

    if sending_application:
        source['name'] = sending_application

    source_endpoint = hd_to_system(sending_application, sending_universal_id, sending_universal_id_type, config)
    if not source_endpoint:
        source_endpoint = Default_Message_Endpoint

    source['endpoint'] = source_endpoint
    out.source = source

    # .. and the receiving application and facility become the destination.
    destination:'stranydict' = {}

    receiving_application = accessor.component(5, 1)
    receiving_universal_id = accessor.component(5, 2)
    receiving_universal_id_type = accessor.component(5, 3)

    if receiving_application:
        destination['name'] = receiving_application

    destination_endpoint = hd_to_system(receiving_application, receiving_universal_id, receiving_universal_id_type, config)
    if not destination_endpoint:
        destination_endpoint = Default_Message_Endpoint

    destination['endpoint'] = destination_endpoint
    out.destination = [destination]

    warn_unmapped(accessor, _MSH_Handled, context)

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

    for repetition in accessor.repetitions(3):
        if identifier := cx_to_identifier(repetition, config):
            identifiers.append(identifier)

    # .. including the patient account number ..
    for repetition in accessor.repetitions(18):
        if identifier := cx_to_identifier(repetition, config):
            identifiers.append(identifier)

    # .. and the social security number.
    ssn = accessor.value(19)
    if ssn:
        ssn_identifier = {
            'value': ssn,
            'system': SSN_System,
            'type': {'coding': [{'system': Identifier_Type_System, 'code': 'SS'}]},
        }
        identifiers.append(ssn_identifier)

    if identifiers:
        out.identifier = identifiers

    # Every repetition of the name field becomes a HumanName
    names:'anylist' = []

    for repetition in accessor.repetitions(5):
        if name := xpn_to_human_name(repetition, config):
            names.append(name)

    if names:
        out.name = names

    # The birth date drops any time part, per FHIR's Patient.birthDate being a date
    birth_value = accessor.value(7)
    birth_date = dtm_to_date(birth_value)

    if birth_date:
        out.birthDate = birth_date

    # The administrative sex maps to the gender code
    sex_code = accessor.value(8)
    if sex_code:
        if gender := lookup('administrative_sex', sex_code, config):
            out.gender = gender['code']
        else:
            context.warn(f'PID-8 code `{sex_code}` not mapped')

    # Addresses map one to one
    addresses:'anylist' = []

    for repetition in accessor.repetitions(11):
        if address := xad_to_address(repetition, config):
            addresses.append(address)

    if addresses:
        out.address = addresses

    # Home and business telecoms merge into one list, each with its use filled in
    telecoms:'anylist' = []

    for repetition in accessor.repetitions(13):
        if telecom := xtn_to_contact_point(repetition, config, default_use='home'):
            telecoms.append(telecom)

    for repetition in accessor.repetitions(14):
        if telecom := xtn_to_contact_point(repetition, config, default_use='work'):
            telecoms.append(telecom)

    if telecoms:
        out.telecom = telecoms

    # The primary language becomes a communication entry
    language_repetition = accessor.first(15)

    if language := cwe_to_codeable_concept(language_repetition, config):
        out.communication = [{'language': language, 'preferred': True}]

    # The marital status maps through the standard table
    marital_code = accessor.value(16)
    if marital_code:
        if marital_status := lookup('marital_status', marital_code, config):
            coding = {'system': marital_status['system'], 'code': marital_status['code']}
            out.maritalStatus = {'coding': [coding]}
        else:
            context.warn(f'PID-16 code `{marital_code}` not mapped')

    # The birth place is preserved in the standard extension
    birth_place = accessor.value(23)
    if birth_place:
        out.extension = [{'url': Birth_Place_Extension_URL, 'valueAddress': {'text': birth_place}}]

    # Multiple-birth data prefers the order number over the yes/no indicator
    birth_order = accessor.value(25)
    multiple_birth = accessor.value(24)

    if birth_order:
        if birth_order.isdigit():
            out.multipleBirthInteger = int(birth_order)
    elif multiple_birth == 'Y':
        out.multipleBirthBoolean = True

    # Death data prefers the timestamp over the yes/no indicator
    death_value = accessor.value(29)
    death_datetime = dtm_to_datetime(death_value, config)
    death_indicator = accessor.value(30)

    if death_datetime:
        out.deceasedDateTime = death_datetime
    elif death_indicator == 'Y':
        out.deceasedBoolean = True

    warn_unmapped(accessor, _PID_Handled, context)

    return out

# ################################################################################################################################

def enrich_pd1(accessor:'SegmentAccessor', context:'ConversionContext', patient:'Patient') -> 'None':
    """ Adds the primary care provider and primary facility from PD1 to an existing Patient.
    """
    general_practitioners:'anylist' = []

    # The patient's primary facility becomes an Organization ..
    for repetition in accessor.repetitions(3):
        organization_name = component_value(repetition, 1)
        if organization_name:
            organization = Organization()
            organization.name = organization_name

            reference = context.add(organization)
            general_practitioners.append(reference)

    # .. and the primary care provider becomes a Practitioner.
    for repetition in accessor.repetitions(4):
        if reference := add_practitioner(repetition, context):
            general_practitioners.append(reference)

    if general_practitioners:
        patient.generalPractitioner = general_practitioners

    warn_unmapped(accessor, _PD1_Handled, context)

# ################################################################################################################################

def map_nk1(accessor:'SegmentAccessor', context:'ConversionContext') -> 'RelatedPerson | None':
    """ Converts NK1 to a RelatedPerson tied to the current patient.
    """
    config = context.config

    # Our response to produce
    out = RelatedPerson()

    if context.patient_reference:
        out.patient = context.patient_reference

    names:'anylist' = []

    for repetition in accessor.repetitions(2):
        if name := xpn_to_human_name(repetition, config):
            names.append(name)

    if names:
        out.name = names

    # The relationship keeps its v2 coding
    relationship_repetition = accessor.first(3)

    if relationship := cwe_to_codeable_concept(relationship_repetition, config):
        out.relationship = [relationship]

    addresses:'anylist' = []

    for repetition in accessor.repetitions(4):
        if address := xad_to_address(repetition, config):
            addresses.append(address)

    if addresses:
        out.address = addresses

    telecoms:'anylist' = []

    for repetition in accessor.repetitions(5):
        if telecom := xtn_to_contact_point(repetition, config, default_use='home'):
            telecoms.append(telecom)

    for repetition in accessor.repetitions(6):
        if telecom := xtn_to_contact_point(repetition, config, default_use='work'):
            telecoms.append(telecom)

    if telecoms:
        out.telecom = telecoms

    warn_unmapped(accessor, _NK1_Handled, context)

    # A next-of-kin without a name or relationship carries nothing to build a person from
    if not names:
        if not relationship_repetition:
            return None

    return out

# ################################################################################################################################

def _add_encounter_participant(
    accessor:'SegmentAccessor',
    position:'int',
    type_code:'str',
    participants:'anylist',
    context:'ConversionContext',
    ) -> 'None':
    """ Turns one PV1 practitioner field into Encounter participants of the given type.
    """
    for repetition in accessor.repetitions(position):
        if reference := add_practitioner(repetition, context):
            participant_type = {'coding': [{'system': Participation_Type_System, 'code': type_code}]}
            participants.append({'type': [participant_type], 'individual': reference})

# ################################################################################################################################

def map_pv1(accessor:'SegmentAccessor', context:'ConversionContext') -> 'Encounter':
    """ Converts PV1 to an Encounter with its practitioners and locations.
    """
    config = context.config

    # Our response to produce
    out = Encounter()

    if context.patient_reference:
        out.subject = context.patient_reference

    # The patient class decides both the encounter class and its status ..
    class_code = accessor.value(2)

    if encounter_class := lookup('patient_class', class_code, config):
        out.class_ = {'system': encounter_class['system'], 'code': encounter_class['code']}
    else:
        if class_code:
            context.warn(f'PV1-2 code `{class_code}` not mapped')
        out.class_ = Default_Encounter_Class

    # .. where a discharge time always means the encounter is over.
    discharge_time = accessor.value(45)

    if discharge_time:
        out.status = Finished_Encounter_Status
    elif status := lookup('patient_class_status', class_code, config):
        out.status = status['code']
    else:
        out.status = Default_Encounter_Status

    # The assigned and prior locations become Location resources
    locations:'anylist' = []

    for position in (3, 6):
        location_repetition = accessor.first(position)

        if reference := add_location(location_repetition, context):
            locations.append({'location': reference})

    if locations:
        out.location = locations

    # The admission type expresses the encounter's priority
    admission_type_repetition = accessor.first(4)

    if priority := cwe_to_codeable_concept(admission_type_repetition, config):
        out.priority = priority

    # Each kind of caregiver becomes a participant with the proper type
    participants:'anylist' = []

    _add_encounter_participant(accessor, 7, 'ATND', participants, context)
    _add_encounter_participant(accessor, 8, 'REF', participants, context)
    _add_encounter_participant(accessor, 9, 'CON', participants, context)
    _add_encounter_participant(accessor, 17, 'ADM', participants, context)

    if participants:
        out.participant = participants

    # The hospital service maps to the service type
    hospital_service_repetition = accessor.first(10)

    if service_type := cwe_to_codeable_concept(hospital_service_repetition, config):
        out.serviceType = service_type

    # The admit source ends up under hospitalization
    admit_source_repetition = accessor.first(14)

    if admit_source := cwe_to_codeable_concept(admit_source_repetition, config):
        out.hospitalization = {'admitSource': admit_source}

    # The visit number becomes the encounter's identifier
    visit_number_repetition = accessor.first(19)

    if identifier := cx_to_identifier(visit_number_repetition, config):
        out.identifier = [identifier]

    # Admit and discharge times bound the encounter's period
    period:'stranydict' = {}

    admit_value = accessor.value(44)
    admit_time = dtm_to_datetime(admit_value, config)

    if admit_time:
        period['start'] = admit_time

    discharge_datetime = dtm_to_datetime(discharge_time, config)
    if discharge_datetime:
        period['end'] = discharge_datetime

    if period:
        out.period = period

    warn_unmapped(accessor, _PV1_Handled, context)

    return out

# ################################################################################################################################

def enrich_pv2(accessor:'SegmentAccessor', context:'ConversionContext', encounter:'Encounter') -> 'None':
    """ Adds the admit reason from PV2 to an existing Encounter.
    """
    config = context.config

    admit_reason_repetition = accessor.first(3)

    if admit_reason := cwe_to_codeable_concept(admit_reason_repetition, config):
        encounter.reasonCode = [admit_reason]

    warn_unmapped(accessor, _PV2_Handled, context)

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
        context.warn('OBX-3 is empty, the observation code is unknown')
        out.code = Unknown_Code

    # .. the result status is required, with a constant default ..
    status_code = accessor.value(11)

    if status := lookup('observation_result_status', status_code, config):
        out.status = status['code']
    else:
        if status_code:
            context.warn(f'OBX-11 code `{status_code}` not mapped')
        out.status = Default_Observation_Status

    # .. and the value routes by the declared value type.
    value_type = accessor.value(2)
    value_repetition = accessor.first(5)

    units_repetition = accessor.first(6)
    units = cwe_to_codeable_concept(units_repetition, config)

    if value_repetition:
        _set_observation_value(out, value_type, value_repetition, units, context)

    # The reference range is a display string
    reference_range = accessor.value(7)
    if reference_range:
        out.referenceRange = [{'text': reference_range}]

    # Abnormal flags become interpretations
    interpretations:'anylist' = []

    for repetition in accessor.repetitions(8):
        flag_code = component_value(repetition, 1)
        if interpretation := lookup('abnormal_flags', flag_code, config):
            coding = {'system': interpretation['system'], 'code': interpretation['code']}
            interpretations.append({'coding': [coding]})
        else:
            if flag_code:
                context.warn(f'OBX-8 code `{flag_code}` not mapped')

    if interpretations:
        out.interpretation = interpretations

    # The observation time maps to the effective time
    effective_value = accessor.value(14)
    effective_time = dtm_to_datetime(effective_value, config)

    if effective_time:
        out.effectiveDateTime = effective_time

    # The responsible observer becomes a performer
    performers:'anylist' = []

    for repetition in accessor.repetitions(16):
        if reference := add_practitioner(repetition, context):
            performers.append(reference)

    if performers:
        out.performer = performers

    warn_unmapped(accessor, _OBX_Handled, context)

    return out

# ################################################################################################################################

def _quantity_from_units(value:'str', units:'dictnone') -> 'stranydict':
    """ Builds a FHIR Quantity from a numeric string and an optional units concept.
    """

    # Our response to produce
    out:'stranydict' = {'value': float(value)}

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

def _set_observation_value(
    observation:'Observation',
    value_type:'strnone',
    repetition:'anylist',
    units:'dictnone',
    context:'ConversionContext',
    ) -> 'None':
    """ Fills in the right Observation.value[x] field for one OBX value.
    """
    config = context.config

    # A numeric value becomes a Quantity with the units from OBX-6 ..
    if value_type == 'NM':
        value = component_value(repetition, 1)
        if value:
            observation.valueQuantity = _quantity_from_units(value, units)
        return

    # .. text stays text ..
    if value_type in Text_Value_Types:
        value = component_value(repetition, 1)
        if value:
            observation.valueString = value
        return

    # .. coded values become CodeableConcepts ..
    if value_type in Coded_Value_Types:
        if concept := cwe_to_codeable_concept(repetition, config):
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
            if time_length >= 6:
                observation.valueTime = f'{value[:2]}:{value[2:4]}:{value[4:6]}'
            elif time_length == 4:
                observation.valueTime = f'{value[:2]}:{value[2:4]}:00'
        return

    # .. a missing value type with a value present is taken as text ..
    if not value_type:
        value = component_value(repetition, 1)
        if value:
            observation.valueString = value
        return

    # .. and anything else is not a value we can route.
    context.warn(f'OBX-2 value type `{value_type}` not mapped')

# ################################################################################################################################

def map_al1(accessor:'SegmentAccessor', context:'ConversionContext') -> 'AllergyIntolerance':
    """ Converts AL1 to an AllergyIntolerance.
    """
    config = context.config

    # Our response to produce
    out = AllergyIntolerance()

    if context.patient_reference:
        out.patient = context.patient_reference

    # The allergen code is the substance ..
    allergen_repetition = accessor.first(3)

    if code := cwe_to_codeable_concept(allergen_repetition, config):
        out.code = code

    # .. the allergy type decides both the category and the type ..
    type_code = accessor.value(2)

    category = lookup('allergy_category', type_code, config)
    allergy_type = lookup('allergy_type', type_code, config)

    if category:
        out.category = [category['code']]

    if allergy_type:
        out.type_ = allergy_type['code']

    if type_code:
        if not category:
            if not allergy_type:
                context.warn(f'AL1-2 code `{type_code}` not mapped')

    # .. the severity decides the criticality ..
    severity_code = accessor.value(4)

    if criticality := lookup('allergy_criticality', severity_code, config):
        out.criticality = criticality['code']

    # .. and the reaction text becomes a manifestation, with the severity when it maps.
    severity = lookup('allergy_severity', severity_code, config)
    reactions:'anylist' = []

    for repetition in accessor.repetitions(5):
        reaction_text = component_value(repetition, 1)
        if reaction_text:
            reaction:'stranydict' = {'manifestation': [{'text': reaction_text}]}

            if severity:
                reaction['severity'] = severity['code']

            reactions.append(reaction)

    if reactions:
        out.reaction = reactions

    warn_unmapped(accessor, _AL1_Handled, context)

    return out

# ################################################################################################################################

def map_dg1(accessor:'SegmentAccessor', context:'ConversionContext', encounter:'Encounter | None') -> 'Condition':
    """ Converts DG1 to a Condition, also recording it as an encounter diagnosis.
    The Condition adds itself to the bundle so the encounter can point at it.
    """
    config = context.config

    # Our response to produce
    out = Condition()

    if context.patient_reference:
        out.subject = context.patient_reference

    if context.encounter_reference:
        out.encounter = context.encounter_reference

    diagnosis_repetition = accessor.first(3)

    if code := cwe_to_codeable_concept(diagnosis_repetition, config):
        out.code = code

    onset_value = accessor.value(5)
    onset_datetime = dtm_to_datetime(onset_value, config)

    if onset_datetime:
        out.onsetDateTime = onset_datetime

    recorded_value = accessor.value(19)
    recorded_date = dtm_to_datetime(recorded_value, config)

    if recorded_date:
        out.recordedDate = recorded_date

    condition_reference = context.add(out)

    # The diagnosis also joins the encounter, with its role and priority when present
    if encounter:
        diagnosis:'stranydict' = {'condition': condition_reference}

        diagnosis_type_code = accessor.value(6)
        if diagnosis_role := lookup('diagnosis_type', diagnosis_type_code, config):
            coding = {'system': diagnosis_role['system'], 'code': diagnosis_role['code']}
            diagnosis['use'] = {'coding': [coding]}

        priority = accessor.value(15)
        if priority:
            if priority.isdigit():
                diagnosis['rank'] = int(priority)

        append_to_list_field(encounter, 'diagnosis', diagnosis)

    warn_unmapped(accessor, _DG1_Handled, context)

    return out

# ################################################################################################################################

def map_pr1(accessor:'SegmentAccessor', context:'ConversionContext') -> 'Procedure':
    """ Converts PR1 to a Procedure.
    """
    config = context.config

    # Our response to produce
    out = Procedure()

    out.status = Procedure_Status

    if context.patient_reference:
        out.subject = context.patient_reference

    if context.encounter_reference:
        out.encounter = context.encounter_reference

    procedure_repetition = accessor.first(3)

    if code := cwe_to_codeable_concept(procedure_repetition, config):
        out.code = code

    performed_value = accessor.value(5)
    performed = dtm_to_datetime(performed_value, config)

    if performed:
        out.performedDateTime = performed

    performers:'anylist' = []

    for repetition in accessor.repetitions(11):
        if reference := add_practitioner(repetition, context):
            performers.append({'actor': reference})

    if performers:
        out.performer = performers

    warn_unmapped(accessor, _PR1_Handled, context)

    return out

# ################################################################################################################################

def map_in1(accessor:'SegmentAccessor', context:'ConversionContext') -> 'Coverage':
    """ Converts IN1 to a Coverage with its payor Organization.
    """
    config = context.config

    # Our response to produce
    out = Coverage()

    out.status = Coverage_Status

    if context.patient_reference:
        out.beneficiary = context.patient_reference

    # The insurance company becomes the payor Organization ..
    organization = Organization()
    has_organization = False

    company_name_repetition = accessor.first(4)
    company_name = subcomponent_value(company_name_repetition, 1, 1)

    if company_name:
        organization.name = company_name
        has_organization = True

    company_identifiers:'anylist' = []

    for repetition in accessor.repetitions(3):
        if identifier := cx_to_identifier(repetition, config):
            company_identifiers.append(identifier)

    if company_identifiers:
        organization.identifier = company_identifiers
        has_organization = True

    # FHIR requires a payor even when IN1 does not identify the insurance company
    if not has_organization:
        context.warn('IN1-3 and IN1-4 are empty, the payor is unknown')
        organization.name = Unknown_Payor_Name

    payor_reference = context.add(organization)
    out.payor = [payor_reference]

    # .. the plan type maps to the coverage type ..
    plan_type_repetition = accessor.first(15)

    if coverage_type := cwe_to_codeable_concept(plan_type_repetition, config):
        out.type_ = coverage_type

    # .. the plan itself and the group number become class entries ..
    classes:'anylist' = []

    plan_id = accessor.value(2)
    if plan_id:
        plan_class = {
            'type': {'coding': [{'system': Coverage_Class_System, 'code': 'plan'}]},
            'value': plan_id,
        }
        classes.append(plan_class)

    group_number = accessor.value(8)
    if group_number:
        group_class = {
            'type': {'coding': [{'system': Coverage_Class_System, 'code': 'group'}]},
            'value': group_number,
        }
        classes.append(group_class)

    if classes:
        out.class_ = classes

    # .. the plan dates bound the coverage period ..
    period:'stranydict' = {}

    effective_value = accessor.value(12)
    effective_date = dtm_to_date(effective_value)

    if effective_date:
        period['start'] = effective_date

    expiration_value = accessor.value(13)
    expiration_date = dtm_to_date(expiration_value)

    if expiration_date:
        period['end'] = expiration_date

    if period:
        out.period = period

    # .. the insured's relationship decides who the subscriber is ..
    relationship_code = accessor.value(17)
    relationship_repetition = accessor.first(17)

    if relationship := cwe_to_codeable_concept(relationship_repetition, config):
        out.relationship = relationship

    if relationship_code == Self_Relationship_Code:
        if context.patient_reference:
            out.subscriber = context.patient_reference

    # .. and the policy number doubles as the identifier and the subscriber ID.
    policy_number = accessor.value(36)
    if policy_number:
        out.identifier = [{'value': policy_number}]
        out.subscriberId = policy_number

    warn_unmapped(accessor, _IN1_Handled, context)

    return out

# ################################################################################################################################

def map_orc_obr_to_service_request(
    orc_accessor:'SegmentAccessor | None',
    obr_accessor:'SegmentAccessor | None',
    context:'ConversionContext',
    ) -> 'ServiceRequest':
    """ Converts an ORC/OBR pair - either may be absent - to a ServiceRequest.
    """
    config = context.config

    # Our response to produce
    out = ServiceRequest()

    out.intent = 'order'

    if context.patient_reference:
        out.subject = context.patient_reference

    if context.encounter_reference:
        out.encounter = context.encounter_reference

    # The order control code decides the request status ..
    status_code = None
    if orc_accessor:
        status_code = orc_accessor.value(1)

    if status := lookup('order_status', status_code, config):
        out.status = status['code']
    else:
        if status_code:
            context.warn(f'ORC-1 code `{status_code}` not mapped')
        out.status = Default_Order_Status

    # .. placer and filler order numbers become identifiers, wherever they appear ..
    identifiers:'anylist' = []

    for source_accessor, position in ((orc_accessor, 2), (orc_accessor, 3), (obr_accessor, 2), (obr_accessor, 3)):
        if source_accessor:
            order_number_repetition = source_accessor.first(position)

            if identifier := ei_to_identifier(order_number_repetition, config):
                if identifier not in identifiers:
                    identifiers.append(identifier)

    if identifiers:
        out.identifier = identifiers

    # .. the universal service identifier is the requested code ..
    if obr_accessor:
        service_repetition = obr_accessor.first(4)

        if code := cwe_to_codeable_concept(service_repetition, config):
            out.code = code

    # .. the transaction time is when the order was authored ..
    if orc_accessor:
        authored_value = orc_accessor.value(9)
        authored = dtm_to_datetime(authored_value, config)

        if authored:
            out.authoredOn = authored

        # .. and the ordering provider is the requester.
        provider_repetition = orc_accessor.first(12)

        if requester := add_practitioner(provider_repetition, context):
            out.requester = requester

        warn_unmapped(orc_accessor, _ORC_Handled, context)

    # Without an ORC, the ordering provider comes from the OBR itself
    if obr_accessor:
        if not orc_accessor:
            provider_repetition = obr_accessor.first(16)

            if requester := add_practitioner(provider_repetition, context):
                out.requester = requester

    return out

# ################################################################################################################################

def map_obr_to_diagnostic_report(
    obr_accessor:'SegmentAccessor',
    context:'ConversionContext',
    service_request_reference:'dictnone',
    ) -> 'DiagnosticReport':
    """ Converts OBR to a DiagnosticReport that the following observations attach to.
    """
    config = context.config

    # Our response to produce
    out = DiagnosticReport()

    if context.patient_reference:
        out.subject = context.patient_reference

    if context.encounter_reference:
        out.encounter = context.encounter_reference

    if service_request_reference:
        out.basedOn = [service_request_reference]

    # The result status is required, with a constant default ..
    status_code = obr_accessor.value(25)

    if status := lookup('result_status', status_code, config):
        out.status = status['code']
    else:
        if status_code:
            context.warn(f'OBR-25 code `{status_code}` not mapped')
        out.status = Default_Report_Status

    # .. the universal service identifier is the report code, which FHIR requires ..
    service_repetition = obr_accessor.first(4)

    if code := cwe_to_codeable_concept(service_repetition, config):
        out.code = code
    else:
        context.warn('OBR-4 is empty, the report code is unknown')
        out.code = Unknown_Code

    # .. placer and filler order numbers become identifiers ..
    identifiers:'anylist' = []

    for position in (2, 3):
        order_number_repetition = obr_accessor.first(position)

        if identifier := ei_to_identifier(order_number_repetition, config):
            identifiers.append(identifier)

    if identifiers:
        out.identifier = identifiers

    # .. the observation time is the effective time ..
    effective_value = obr_accessor.value(7)
    effective_time = dtm_to_datetime(effective_value, config)

    if effective_time:
        out.effectiveDateTime = effective_time

    # .. and the results-reported time is when the report was issued.
    issued_value = obr_accessor.value(22)
    issued = dtm_to_datetime(issued_value, config)

    if issued:
        out.issued = issued

    warn_unmapped(obr_accessor, _OBR_Handled, context)

    return out

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

    # .. and the collection time completes the picture.
    collected_value = accessor.value(17)
    collected = dtm_to_datetime(collected_value, config)

    if collected:
        out.collection = {'collectedDateTime': collected}

    warn_unmapped(accessor, _SPM_Handled, context)

    return out

# ################################################################################################################################

def nte_text(accessor:'SegmentAccessor') -> 'strnone':
    """ Joins all the comment repetitions of an NTE into one text.
    """
    parts:'strlist' = []

    for repetition in accessor.repetitions(3):
        comment = component_value(repetition, 1)
        if comment:
            parts.append(comment)

    if parts:

        out = '\n'.join(parts)
        return out

    return None

# ################################################################################################################################

def map_sch(accessor:'SegmentAccessor', context:'ConversionContext') -> 'Appointment':
    """ Converts SCH to an Appointment.
    """
    config = context.config

    # Our response to produce
    out = Appointment()

    # The filler status decides the appointment status, with a constant default ..
    status_code = accessor.component(25, 1)

    if status := lookup('filler_status', status_code, config):
        out.status = status['code']
    else:
        if status_code:
            context.warn(f'SCH-25 code `{status_code}` not mapped')
        out.status = Default_Appointment_Status

    # .. placer and filler appointment IDs become identifiers ..
    identifiers:'anylist' = []

    for position in (1, 2):
        appointment_id_repetition = accessor.first(position)

        if identifier := ei_to_identifier(appointment_id_repetition, config):
            identifiers.append(identifier)

    if identifiers:
        out.identifier = identifiers

    # .. the event reason is why the appointment exists ..
    reason_repetition = accessor.first(6)

    if reason := cwe_to_codeable_concept(reason_repetition, config):
        out.reasonCode = [reason]

    # .. the appointment type keeps its coding ..
    type_repetition = accessor.first(8)

    if appointment_type := cwe_to_codeable_concept(type_repetition, config):
        out.appointmentType = appointment_type

    # .. the duration takes its unit at face value when it counts minutes ..
    duration = accessor.value(9)
    duration_units = accessor.component(10, 1)

    if duration:
        if duration.isdigit():
            if duration_units:
                duration_units_lower = duration_units.lower()
                if duration_units_lower.startswith('min') or duration_units_lower == 'm':
                    out.minutesDuration = int(duration)

    # .. and the timing quantity carries the start and end times.
    start_value = accessor.component(11, 4)
    start_time = dtm_to_datetime(start_value, config)

    if start_time:
        out.start = start_time

    end_value = accessor.component(11, 5)
    end_time = dtm_to_datetime(end_value, config)

    if end_time:
        out.end = end_time

    warn_unmapped(accessor, _SCH_Handled, context)

    return out

# ################################################################################################################################

def enrich_ais(accessor:'SegmentAccessor', context:'ConversionContext', appointment:'Appointment') -> 'None':
    """ Adds the requested service from AIS to an existing Appointment.
    """
    config = context.config

    service_repetition = accessor.first(3)

    if service_type := cwe_to_codeable_concept(service_repetition, config):
        appointment.serviceType = [service_type]

    warn_unmapped(accessor, _AIS_Handled, context)

# ################################################################################################################################

def aig_participant(accessor:'SegmentAccessor', context:'ConversionContext') -> 'dictnone':
    """ Turns AIG - a general scheduled resource - into an Appointment participant with a display name.
    """
    display = accessor.component(3, 2)
    if not display:
        display = accessor.component(3, 1)

    warn_unmapped(accessor, _AIG_Handled, context)

    if not display:
        return None

    out = {'actor': {'display': display}, 'status': 'accepted'}
    return out

# ################################################################################################################################

def ail_participant(accessor:'SegmentAccessor', context:'ConversionContext') -> 'dictnone':
    """ Turns AIL - a scheduled location - into an Appointment participant backed by a Location resource.
    """
    location_repetition = accessor.first(3)
    reference = add_location(location_repetition, context)

    warn_unmapped(accessor, _AIL_Handled, context)

    if not reference:
        return None

    out = {'actor': reference, 'status': 'accepted'}
    return out

# ################################################################################################################################

def aip_participant(accessor:'SegmentAccessor', context:'ConversionContext') -> 'dictnone':
    """ Turns AIP - scheduled personnel - into an Appointment participant backed by a Practitioner resource.
    """
    person_repetition = accessor.first(3)
    reference = add_practitioner(person_repetition, context)

    warn_unmapped(accessor, _AIP_Handled, context)

    if not reference:
        return None

    out = {'actor': reference, 'status': 'accepted'}
    return out

# ################################################################################################################################

def gather_obx_text(accessor:'SegmentAccessor', context:'ConversionContext') -> 'strnone':
    """ Collects the text lines of one document-carrying OBX, joining all the repetitions of its value.
    """
    parts:'strlist' = []

    for repetition in accessor.repetitions(5):
        line = component_value(repetition, 1)
        if line:
            parts.append(line)

    warn_unmapped(accessor, _OBX_Text_Handled, context)

    if parts:

        out = '\n'.join(parts)
        return out

    return None

# ################################################################################################################################

def map_rxa(
    accessor:'SegmentAccessor',
    orc_accessor:'SegmentAccessor | None',
    context:'ConversionContext',
    ) -> 'Immunization':
    """ Converts RXA - with its optional ORC - to an Immunization.
    """
    config = context.config

    # Our response to produce
    out = Immunization()

    if context.patient_reference:
        out.patient = context.patient_reference

    # The completion status is required, with a constant default ..
    status_code = accessor.value(20)

    if status := lookup('completion_status', status_code, config):
        out.status = status['code']
    else:
        if status_code:
            context.warn(f'RXA-20 code `{status_code}` not mapped')
        out.status = Default_Immunization_Status

    # .. the administered code is the vaccine ..
    vaccine_repetition = accessor.first(5)

    if vaccine_code := cwe_to_codeable_concept(vaccine_repetition, config):
        out.vaccineCode = vaccine_code

    # .. the administration time is required by FHIR ..
    occurrence_value = accessor.value(3)
    occurrence = dtm_to_datetime(occurrence_value, config)

    if occurrence:
        out.occurrenceDateTime = occurrence

    # .. the administered amount and units make the dose ..
    amount = accessor.value(6)
    if amount:

        units_repetition = accessor.first(7)
        units = cwe_to_codeable_concept(units_repetition, config)

        out.doseQuantity = _quantity_from_units(amount, units)

    # .. the administering provider performs the immunization ..
    provider_repetition = accessor.first(10)

    if performer := add_practitioner(provider_repetition, context):
        out.performer = [{'actor': performer}]

    # .. the lot number and expiration date carry over directly ..
    lot_number = accessor.value(15)
    if lot_number:
        out.lotNumber = lot_number

    expiration_value = accessor.value(16)
    expiration_date = dtm_to_date(expiration_value)

    if expiration_date:
        out.expirationDate = expiration_date

    # .. and the manufacturer becomes an Organization.
    manufacturer_name = accessor.component(17, 2)
    if not manufacturer_name:
        manufacturer_name = accessor.component(17, 1)

    if manufacturer_name:
        organization = Organization()
        organization.name = manufacturer_name

        out.manufacturer = context.add(organization)

    # The filler order number identifies the immunization
    if orc_accessor:
        filler_repetition = orc_accessor.first(3)

        if identifier := ei_to_identifier(filler_repetition, config):
            out.identifier = [identifier]

        warn_unmapped(orc_accessor, _ORC_Handled, context)

    warn_unmapped(accessor, _RXA_Handled, context)

    return out

# ################################################################################################################################

def enrich_rxr(accessor:'SegmentAccessor', context:'ConversionContext', immunization:'Immunization') -> 'None':
    """ Adds the route and site from RXR to an existing Immunization.
    """
    config = context.config

    route_repetition = accessor.first(1)

    if route := cwe_to_codeable_concept(route_repetition, config):
        immunization.route = route

    site_repetition = accessor.first(2)

    if site := cwe_to_codeable_concept(site_repetition, config):
        immunization.site = site

    warn_unmapped(accessor, _RXR_Handled, context)

# ################################################################################################################################

def map_txa(accessor:'SegmentAccessor', context:'ConversionContext') -> 'DocumentReference':
    """ Converts TXA to a DocumentReference. The document text itself arrives later,
    from the OBX segments that follow, through set_document_text.
    """
    config = context.config

    # Our response to produce
    out = DocumentReference()

    out.status = Document_Status

    if context.patient_reference:
        out.subject = context.patient_reference

    # The document type keeps its coding ..
    type_repetition = accessor.first(2)

    if document_type := cwe_to_codeable_concept(type_repetition, config):
        out.type_ = document_type

    # .. the unique document number is the master identifier ..
    document_number_repetition = accessor.first(12)

    if master_identifier := ei_to_identifier(document_number_repetition, config):
        out.masterIdentifier = master_identifier

    # .. and the content starts out empty, to be filled in from the following OBX segments.
    out.content = [{'attachment': {'contentType': 'text/plain'}}]

    warn_unmapped(accessor, _TXA_Handled, context)

    return out

# ################################################################################################################################

def set_document_text(document:'DocumentReference', text:'str') -> 'None':
    """ Stores the document text - gathered from OBX segments - in the DocumentReference.
    """
    text_bytes = text.encode('utf8')
    encoded_bytes = b64encode(text_bytes)
    encoded = encoded_bytes.decode('ascii')

    document.content = [{'attachment': {'contentType': 'text/plain', 'data': encoded}}]

# ################################################################################################################################

def _serialize_raw_field(field_data:'any_') -> 'str':
    """ Serializes one raw field back to its wire form, with all its separators.
    """
    repetition_strings:'strlist' = []

    for repetition in field_data:
        component_strings:'strlist' = []

        for component in repetition:
            joined_subcomponents = '&'.join(component)
            component_strings.append(joined_subcomponents)

        joined_components = '^'.join(component_strings)
        repetition_strings.append(joined_components)

    out = '~'.join(repetition_strings)
    return out

# ################################################################################################################################

def map_z_segment(raw_segment:'any_', context:'ConversionContext') -> 'Basic | None':
    """ Converts a Z-segment to a Basic resource whose extensions carry every populated field,
    so that site-specific data is never lost.
    """
    base_url = context.config.extension_base_url
    segment_id = raw_segment.segment_id

    extensions:'anylist' = []

    # Every populated field becomes one extension, named after its position ..
    for field_index, field_data in enumerate(raw_segment.fields):
        value = _serialize_raw_field(field_data)
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
# ################################################################################################################################
