# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.fhir import Location, Organization, Practitioner
from zato.hl7.mappings.datatypes import xcn_to_name_and_identifier
from zato.hl7.mappings.fields import component_value, subcomponent_value

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict, strlist, strnone
    from zato.hl7.mappings.context import ConversionContext
    from zato.hl7.mappings.fields import SegmentAccessor
    ConversionContext = ConversionContext
    SegmentAccessor = SegmentAccessor
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

# Type aliases
dictnone  = 'stranydict | None'
intfrozen = frozenset[int]

# The empty set of consumed fields, for segments that are preserved whole
No_Consumed_Fields:'intfrozen' = frozenset()

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

# The status a ServiceRequest gets when ORC-1 and ORC-5 are empty or carry unknown codes
Default_Order_Status = 'unknown'

# The status a DiagnosticReport gets when OBR-25 is empty or carries an unknown code
Default_Report_Status = 'unknown'

# The status an Appointment gets when SCH-25 is empty or carries an unknown code
Default_Appointment_Status = 'booked'

# The status an Appointment built from an ARQ - a request - always starts with
Requested_Appointment_Status = 'proposed'

# The status an Immunization gets when RXA-20 is empty or carries an unknown code
Default_Immunization_Status = 'completed'

# The status a MedicationAdministration gets when RXA-20 is empty or carries an unknown code
Default_Administration_Status = 'completed'

# The status a MedicationRequest derived from RXE or RXG always has
Medication_Request_Status = 'active'

# The status a MedicationDispense derived from RXD always has
Medication_Dispense_Status = 'completed'

# The intent a MedicationRequest derived from RXE has
Medication_Order_Intent = 'order'

# The intent a MedicationRequest derived from RXG - a single planned give - has
Medication_Give_Intent = 'instance-order'

# The intent a MedicationRequest derived from RXO - the prescriber's original request - has
Medication_Original_Order_Intent = 'original-order'

# The status a Procedure derived from PR1 always has - the procedure was performed
Procedure_Status = 'completed'

# The status a Coverage derived from IN1 always has
Coverage_Status = 'active'

# The status a DocumentReference gets when TXA-19 is empty or carries an unknown code
Document_Status = 'current'

# The status a ChargeItem gets when FT1-6 is empty or carries an unknown code
Default_Charge_Status = 'billable'

# The severity an OperationOutcome issue gets when ERR-4 is empty or carries an unknown code
Default_Issue_Severity = 'error'

# The issue type an OperationOutcome issue gets when ERR-3 is empty or carries an unknown code
Default_Issue_Type = 'processing'

# The endpoint a MessageHeader source or destination gets when MSH carries no usable value
Default_Message_Endpoint = 'urn:zato:hl7v2:unknown'

# The system of Encounter participant type codes
Participation_Type_System = 'http://terminology.hl7.org/CodeSystem/v3-ParticipationType'

# The system of message event codes
Message_Event_System = 'http://terminology.hl7.org/CodeSystem/v2-0003'

# The system of Coverage class type codes
Coverage_Class_System = 'http://terminology.hl7.org/CodeSystem/coverage-class'

# The extension all birth places go to
Birth_Place_Extension_URL = 'http://hl7.org/fhir/StructureDefinition/patient-birthPlace'

# The extension a mother's maiden name goes to
Mothers_Maiden_Name_Extension_URL = 'http://hl7.org/fhir/StructureDefinition/patient-mothersMaidenName'

# The extension a patient's religion goes to
Religion_Extension_URL = 'http://hl7.org/fhir/StructureDefinition/patient-religion'

# The US Core extension a CDC-coded race goes to
Race_Extension_URL = 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-race'

# The US Core extension a CDC-coded ethnic group goes to
Ethnicity_Extension_URL = 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity'

# The escape character free text is decoded with - MSH-2 declares it and the parser
# only tokenizes messages whose delimiters are the standard set, where it is a backslash.
Escape_Char = '\\'

# The repetition separator of the standard delimiter set - each repetition
# of a free-text value is a line of its own.
Repetition_Char = '~'

# The OBX value types whose content is plain text
Text_Value_Types = ('ST', 'TX', 'FT')

# The OBX value types that become CodeableConcepts
Coded_Value_Types = ('CE', 'CWE', 'CNE', 'CF', 'IS')

# The OBX value types that become dateTimes
Datetime_Value_Types = ('DT', 'DTM', 'TS')

# The OBX value type that carries encapsulated data - a document or an image
Encapsulated_Value_Type = 'ED'

# The OBX value type that points at data kept elsewhere
Reference_Pointer_Value_Type = 'RP'

# The IN1-17 codes that say the insured person is the patient
Self_Relationship_Codes = ('SEL', 'SELF')

# The extension that states a required field carries no value
Data_Absent_Extension_URL = 'http://hl7.org/fhir/StructureDefinition/data-absent-reason'

# ################################################################################################################################
# ################################################################################################################################

def absent_subject_reference() -> 'stranydict':
    """ Returns a fresh subject reference stating there is no patient - FHIR requires
    a subject on some resources even when the message carries no PID at all.
    """
    out = {'extension': [{'url': Data_Absent_Extension_URL, 'valueCode': 'unknown'}]}
    return out

# ################################################################################################################################

def append_to_list_field(resource:'any_', field_name:'str', item:'stranydict') -> 'None':
    """ Appends one item to a list field of a typed resource, keeping what is already there.
    Reading an unset list field would auto-vivify an empty element, so the current state
    comes from the resource's serialized form instead.
    """
    current = resource.to_dict()

    items = current.get(field_name)
    if items is None:
        items = []

    _ = items.append(item)
    setattr(resource, field_name, items)

# ################################################################################################################################

def preserve_value(
    resource:'any_',
    context:'ConversionContext',
    segment_id:'str',
    position:'int',
    value:'str',
    ) -> 'None':
    """ Preserves one field's raw value as an extension on a resource.
    """
    base_url = context.config.extension_base_url
    extension = {'url': f'{base_url}/unmapped/{segment_id}-{position}', 'valueString': value}

    append_to_list_field(resource, 'extension', extension)

# ################################################################################################################################

def preserve_unmapped(
    accessor:'SegmentAccessor',
    handled:'intfrozen',
    resource:'any_',
    context:'ConversionContext',
    ) -> 'None':
    """ Preserves every populated field the mapper did not consume as an extension on a resource.
    """
    populated = accessor.populated_positions()
    unmapped = populated - handled

    for position in sorted(unmapped):
        value = accessor.serialize(position)
        preserve_value(resource, context, accessor.segment_id, position, value)

# ################################################################################################################################

def add_practitioner(repetition:'anylist', context:'ConversionContext') -> 'dictnone':
    """ Builds a Practitioner from an XCN repetition, adds it to the bundle and returns a reference.
    Identical practitioners referenced from different fields collapse into one resource.
    """
    parts = xcn_to_name_and_identifier(repetition, context.config)
    if not parts:
        return None

    practitioner = Practitioner()

    if identifier := parts.get('identifier'):
        practitioner.identifier = [identifier]

    if name := parts.get('name'):
        practitioner.name = [name]

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

    # A spelled-out facility name can arrive in the universal ID subcomponent.
    facility_universal_id = subcomponent_value(repetition, 4, 2)
    if facility_universal_id:
        parts.append(facility_universal_id)

    # PL-9 spells out what the location is.
    description = component_value(repetition, 9)

    if not parts:
        if not description:
            return None

    location = Location()

    if parts:
        location.name = '-'.join(parts)
    else:
        location.name = description

    if description:
        location.description = description

    out = context.add(location)
    return out

# ################################################################################################################################

def add_hd_organization(repetition:'anylist', context:'ConversionContext') -> 'dictnone':
    """ Builds an Organization from an HD - a facility - repetition, adds it to the bundle
    and returns a reference. The namespace is the name, the universal ID an identifier.
    """
    name = component_value(repetition, 1)
    universal_id = component_value(repetition, 2)

    if not name:
        if not universal_id:
            return None

    organization = Organization()

    if name:
        organization.name = name

    if universal_id:
        organization.identifier = [{'value': universal_id}]

    out = context.add(organization)
    return out

# ################################################################################################################################

def add_named_organization(name:'str', context:'ConversionContext', identifier_value:'str' = '') -> 'stranydict':
    """ Builds an Organization carrying a name and an optional identifier, adds it to the bundle and returns a reference.
    """
    organization = Organization()
    organization.name = name

    if identifier_value:
        organization.identifier = [{'value': identifier_value}]

    out = context.add(organization)
    return out

# ################################################################################################################################
# ################################################################################################################################
