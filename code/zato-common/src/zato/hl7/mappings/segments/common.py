# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple

# Zato
from zato.fhir import Location, Organization, Practitioner
from zato.hl7.mappings.datatypes import Identifier_Type_System, hd_to_system, xcn_to_name_and_identifier
from zato.hl7.mappings.fields import Explicit_Null, component_value, populated_components, serialize_component, \
    subcomponent_value

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, anylistnone, dictnone, stranydict, strnone
    from zato.hl7.mappings.context import ConversionContext
    from zato.hl7.mappings.fields import SegmentAccessor
    ConversionContext = ConversionContext
    SegmentAccessor = SegmentAccessor
    anylistnone = anylistnone
    dictnone = dictnone
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

# Type aliases
intfrozen = frozenset[int]

# The empty set of consumed fields, for segments that are preserved whole
No_Consumed_Fields:'intfrozen' = frozenset()

# The status an Encounter gets when the patient class does not say otherwise
Default_Encounter_Status = 'in-progress'

# The class an Encounter gets when PV1-2 is empty or carries an unknown code - FHIR requires one
Default_Encounter_Class = {'system': 'http://terminology.hl7.org/CodeSystem/v3-NullFlavor', 'code': 'UNK'}

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

# The user-defined table PV1-20 financial classes come from
Financial_Class_System = 'http://terminology.hl7.org/CodeSystem/v2-0064'

# The extension a financial class becomes on a Coverage whose type is already taken, or on an Encounter with no Coverage
Financial_Class_Extension = 'financial-class'

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

# The data-absent-reason code for a value the message never carried
Data_Absent_Unknown = 'unknown'

# The system of Location physical type codes
Location_Physical_Type_System = 'http://terminology.hl7.org/CodeSystem/location-physical-type'

# The mode of every Location built from a PL
Location_Instance_Mode = 'instance'

# ################################################################################################################################
# ################################################################################################################################

class _PLLevel(NamedTuple):
    """ One level of the PL location hierarchy - which component carries it and what kind of place it is.
    """
    position:'int'
    physical_type:'strnone'

# ################################################################################################################################
# ################################################################################################################################

# The PL components that make up the location hierarchy, least granular first -
# facility, building, point of care, floor, room and bed. A point of care has no physical type.
_PL_Levels = (
    _PLLevel(4, 'si'),
    _PLLevel(7, 'bu'),
    _PLLevel(1, None),
    _PLLevel(8, 'lvl'),
    _PLLevel(2, 'ro'),
    _PLLevel(3, 'bd'),
)

# The PL component that spells out what the location is
_PL_Description_Position = 9

# The PL component that carries the comprehensive location identifier
_PL_Identifier_Position = 10

# The PL components the hierarchy consumes - anything else is preserved on the most granular Location.
_PL_Handled = frozenset({1, 2, 3, 4, 7, 8, 9, 10})

# How many components a PL has
_PL_Component_Count = 11

# The XCN components a Practitioner's name and identifier consume - anything else is preserved on the Practitioner.
_XCN_Consumed = frozenset({1, 2, 3, 4, 5, 6, 7, 9, 13})

# The XON components an Organization consumes - the name, both identifier slots, the assigning
# authority and the identifier type - anything else is preserved on the Organization.
_XON_Name_Component               = 1
_XON_Identifier_Component_Pre_2_5 = 3
_XON_Authority_Component          = 6
_XON_Type_Component               = 7
_XON_Identifier_Component         = 10
_XON_Consumed = frozenset({
    _XON_Name_Component,
    _XON_Identifier_Component_Pre_2_5,
    _XON_Authority_Component,
    _XON_Type_Component,
    _XON_Identifier_Component,
})

# ################################################################################################################################
# ################################################################################################################################

def absent_value() -> 'stranydict':
    """ Returns a fresh element stating its value is unknown.
    """
    out = {'extension': [{'url': Data_Absent_Extension_URL, 'valueCode': Data_Absent_Unknown}]}
    return out

# ################################################################################################################################

def absent_subject_reference() -> 'stranydict':
    """ Returns a fresh subject reference stating there is no patient.
    """
    out = absent_value()
    return out

# ################################################################################################################################

def patient_or_absent_reference(context:'ConversionContext') -> 'stranydict':
    """ Returns the patient reference for a required element - the message's patient
    when it has one, an absent reference otherwise.
    """
    if context.patient_reference:
        out = context.patient_reference
    else:
        out = absent_subject_reference()

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

def add_financial_class_extension(resource:'any_', context:'ConversionContext', financial_class:'stranydict') -> 'None':
    """ Attaches the message's financial class to a resource as a coded extension.
    """
    base_url = context.config.extension_base_url
    extension = {'url': f'{base_url}/{Financial_Class_Extension}', 'valueCodeableConcept': financial_class}

    append_to_list_field(resource, 'extension', extension)

# ################################################################################################################################

def preserve_inexact_number(
    resource:'any_',
    context:'ConversionContext',
    segment_id:'str',
    position:'int',
    value:'str',
    ) -> 'None':
    """ Preserves the digits of a number the float in the resource cannot carry exactly and records that it happened.
    """
    preserve_value(resource, context, segment_id, position, value)

    text = f'`{value}` cannot be carried exactly as a number, its digits are preserved'
    context.warn(segment_id, position, text)

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

def _preserve_unconsumed(
    repetition:'anylist',
    consumed:'intfrozen',
    resource:'any_',
    context:'ConversionContext',
    segment_id:'str',
    ) -> 'None':
    """ Preserves every populated component of a repetition the mapper did not consume.
    """
    populated = populated_components(repetition)
    unconsumed = populated - consumed

    for position in sorted(unconsumed):
        value = serialize_component(repetition, position)
        preserve_value(resource, context, segment_id, position, value)

# ################################################################################################################################

def preserve_other_components(
    accessor:'SegmentAccessor',
    position:'int',
    consumed:'intfrozen',
    resource:'any_',
    context:'ConversionContext',
    ) -> 'None':
    """ Preserves a whole field as an extension when it carries data outside the components a mapper consumed -
    other populated components in its first repetition, or any further repetitions.
    """

    # An empty field carries nothing to preserve ..
    repetitions = accessor.repetitions(position)
    if not repetitions:
        return

    # .. a second repetition is data the mapper never looked at ..
    repetition_count = len(repetitions)
    needs_preserving = False

    if repetition_count > 1:
        needs_preserving = True

    # .. and so is any component of the first one the mapper did not consume ..
    first_repetition = repetitions[0]
    populated = populated_components(first_repetition)
    unconsumed = populated - consumed

    if unconsumed:
        needs_preserving = True

    # .. either way the whole field goes in as it arrived.
    if needs_preserving:
        value = accessor.serialize(position)
        preserve_value(resource, context, accessor.segment_id, position, value)

# ################################################################################################################################

def add_practitioner(
    repetition:'anylist',
    context:'ConversionContext',
    telecoms:'anylistnone' = None,
    ) -> 'dictnone':
    """ Builds a Practitioner from an XCN repetition, adds it to the bundle and returns a reference.
    Contact points the caller took from a neighbouring field go on the Practitioner too.
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

    if telecoms:
        practitioner.telecom = telecoms

    # Whatever the name and identifier did not consume is preserved on the practitioner.
    _preserve_unconsumed(repetition, _XCN_Consumed, practitioner, context, 'XCN')

    out = context.add(practitioner)
    return out

# ################################################################################################################################

def _pl_level_location(repetition:'anylist', level:'_PLLevel', context:'ConversionContext') -> 'Location | None':
    """ Builds the Location one PL component stands for, or None when the component is empty.
    The component is an HD - its namespace is the name, its universal ID an identifier.
    """

    # Our response to produce
    out = Location()

    config = context.config

    # A component with neither a namespace nor a universal ID names no place ..
    name = subcomponent_value(repetition, level.position, 1)
    universal_id = subcomponent_value(repetition, level.position, 2)
    universal_id_type = subcomponent_value(repetition, level.position, 3)

    if not name:
        if not universal_id:
            return None

    out.mode = Location_Instance_Mode

    # .. the namespace is the name, with the universal ID standing in for it when there is none ..
    if name:
        out.name = name
    else:
        out.name = universal_id

    # .. the universal ID is an identifier, under the system its type resolves to ..
    if universal_id:
        identifier:'stranydict' = {'value': universal_id}

        if system := hd_to_system(name, universal_id, universal_id_type, config):
            identifier['system'] = system

        out.identifier = [identifier]

    # .. and the level says what kind of place this is, where FHIR has a code for it.
    if level.physical_type:
        coding = {'system': Location_Physical_Type_System, 'code': level.physical_type}
        out.physicalType = {'coding': [coding]}

    return out

# ################################################################################################################################

def add_location(
    repetition:'anylist',
    context:'ConversionContext',
    operational_status:'dictnone' = None,
    ) -> 'dictnone':
    """ Builds the Location hierarchy a PL repetition spells out - each of the facility, building,
    point of care, floor, room and bed becomes a Location that is part of the one before it -
    adds them to the bundle and returns a reference to the most granular one, which also
    carries the operational status - a bed status coding - when one is given.
    """
    config = context.config

    # The levels present in the PL, least granular first ..
    levels:'anylist' = []

    for level in _PL_Levels:
        if location := _pl_level_location(repetition, level, context):
            levels.append(location)

    # .. a PL with no levels at all still yields a Location when it carries a description.
    description = component_value(repetition, _PL_Description_Position)

    if not levels:
        if not description:
            return None

        location = Location()
        location.mode = Location_Instance_Mode
        location.name = description
        levels.append(location)

    # The most granular Location carries the description, the comprehensive identifier
    # and whatever the hierarchy did not consume ..
    most_granular = levels[-1]

    if description:
        most_granular.description = description

    if operational_status:
        most_granular.operationalStatus = operational_status

    identifier = subcomponent_value(repetition, _PL_Identifier_Position, 1)

    if identifier:
        identifier_entry:'stranydict' = {'value': identifier}

        namespace = subcomponent_value(repetition, _PL_Identifier_Position, 2)
        universal_id = subcomponent_value(repetition, _PL_Identifier_Position, 3)
        universal_id_type = subcomponent_value(repetition, _PL_Identifier_Position, 4)

        if system := hd_to_system(namespace, universal_id, universal_id_type, config):
            identifier_entry['system'] = system

        append_to_list_field(most_granular, 'identifier', identifier_entry)

    last_position = _PL_Component_Count + 1

    for position in range(1, last_position):
        if position in _PL_Handled:
            continue

        if value := serialize_component(repetition, position):

            # An explicit null is a deletion marker, not data.
            if value != Explicit_Null:
                preserve_value(most_granular, context, 'PL', position, value)

    # .. and each level is part of the one before it, so they enter the bundle in that order.
    parent_reference = None

    for location in levels:
        if parent_reference:
            location.partOf = parent_reference

        parent_reference = context.add(location)

    out = parent_reference
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

def add_xon_organization(
    repetition:'anylist',
    context:'ConversionContext',
    telecoms:'anylistnone' = None,
    ) -> 'dictnone':
    """ Builds an Organization from an XON repetition, adds it to the bundle and returns a reference.
    The name is XON-1, the identifier XON-10 - or XON-3 in older messages - with its assigning
    authority as the system and its type code as the type. Anything else is preserved on the Organization.
    """
    config = context.config

    # An XON with neither a name nor an identifier names no organization ..
    name = component_value(repetition, _XON_Name_Component)
    identifier = component_value(repetition, _XON_Identifier_Component)

    if not identifier:
        identifier = component_value(repetition, _XON_Identifier_Component_Pre_2_5)

    if not name:
        if not identifier:
            return None

    organization = Organization()

    if name:
        organization.name = name

    # .. the identifier's system comes from the assigning authority and its type from XON-7 ..
    if identifier:
        identifier_entry:'stranydict' = {'value': identifier}

        namespace = subcomponent_value(repetition, _XON_Authority_Component, 1)
        universal_id = subcomponent_value(repetition, _XON_Authority_Component, 2)
        universal_id_type = subcomponent_value(repetition, _XON_Authority_Component, 3)

        if system := hd_to_system(namespace, universal_id, universal_id_type, config):
            identifier_entry['system'] = system

        if type_code := component_value(repetition, _XON_Type_Component):
            coding = {'system': Identifier_Type_System, 'code': type_code}
            identifier_entry['type'] = {'coding': [coding]}

        organization.identifier = [identifier_entry]

    # .. the caller's contact points belong to the organization too ..
    if telecoms:
        organization.telecom = telecoms

    # .. and whatever the name and identifier did not consume is preserved on it.
    _preserve_unconsumed(repetition, _XON_Consumed, organization, context, 'XON')

    out = context.add(organization)
    return out

# ################################################################################################################################

def add_named_organization(
    name:'str',
    context:'ConversionContext',
    identifier_value:'str' = '',
    ) -> 'stranydict':
    """ Builds an Organization carrying a name and an optional identifier, adds it to the bundle
    and returns a reference.
    """
    organization = Organization()
    organization.name = name

    if identifier_value:
        organization.identifier = [{'value': identifier_value}]

    out = context.add(organization)
    return out

# ################################################################################################################################
# ################################################################################################################################
