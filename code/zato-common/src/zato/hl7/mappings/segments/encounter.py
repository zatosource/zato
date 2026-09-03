# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.fhir import Encounter, Location
from zato.hl7.mappings.codes import lookup
from zato.hl7.mappings.concepts import cwe_to_codeable_concept
from zato.hl7.mappings.datatypes import cx_to_identifier, ei_to_identifier
from zato.hl7.mappings.fields import component_value, subcomponent_value
from zato.hl7.mappings.segments.common import Default_Encounter_Class, Default_Encounter_Status, \
    Financial_Class_System, Finished_Encounter_Status, Location_Instance_Mode, No_Consumed_Fields, \
    Participation_Type_System, add_location, add_practitioner, append_to_list_field, preserve_other_components, \
    preserve_unmapped, preserve_value

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, dictnone, stranydict
    from zato.hl7.mappings.context import ConversionContext
    from zato.hl7.mappings.fields import SegmentAccessor
    ConversionContext = ConversionContext
    SegmentAccessor = SegmentAccessor
    any_ = any_
    dictnone = dictnone

# ################################################################################################################################
# ################################################################################################################################

# Which field positions each mapper consumes - anything else that carries data is preserved as an extension.
_PV1_Handled = frozenset({
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 36, 37, 38, 40, 42, 43, 44, 45, 50,
})
_PV2_Handled = frozenset({3, 12})
_ROL_Handled = frozenset({1, 3, 4})

# Which FC - financial class - component names the class, the other one is its effective date.
_FC_Class_Component = 1
_FC_Consumed        = frozenset({_FC_Class_Component})

# The status an Encounter location gets when the patient is still to move there
_Planned_Location_Status = 'planned'

# The status an Encounter location gets when the patient has left it
_Completed_Location_Status = 'completed'

# Which DLD - discharge location - component names the place, the other one is its effective date.
_DLD_Location_Component = 1
_DLD_Consumed           = frozenset({_DLD_Location_Component})

# EVN repeats what MSH-9 and MSH-7 already say, its recorded and occurred times back the Encounter period up.
_EVN_Handled = frozenset({1, 2, 6})

# ZBE-1 movement IDs become the encounter's identifiers, the remaining movement details are preserved as extensions.
_ZBE_Handled = frozenset({1})

# ################################################################################################################################
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

def _coded_list_items(
    accessor:'SegmentAccessor',
    position:'int',
    map_name:'str',
    encounter:'Encounter',
    context:'ConversionContext',
    ) -> 'anylist':
    """ Maps every repetition of one coded PV1 field through a vocabulary map into CodeableConcepts,
    preserving the codes the map does not cover.
    """
    config = context.config

    # Our response to produce
    out:'anylist' = []

    for repetition in accessor.repetitions(position):
        code = component_value(repetition, 1)

        if entry := lookup(map_name, code, config):
            coding = {'system': entry['system'], 'code': entry['code']}
            out.append({'coding': [coding]})

        elif code:
            preserve_value(encounter, context, 'PV1', position, code)

    return out

# ################################################################################################################################

def _add_discharge_location(
    accessor:'SegmentAccessor',
    context:'ConversionContext',
    encounter:'Encounter',
    ) -> 'dictnone':
    """ Builds the Location a DLD - discharged to location - names, adds it to the bundle and returns a reference.
    The location is a CWE packed into the first component, so its code and text are subcomponents.
    """

    # A DLD with neither a code nor a text names no place ..
    repetition = accessor.first(37)

    code = subcomponent_value(repetition, _DLD_Location_Component, 1)
    text = subcomponent_value(repetition, _DLD_Location_Component, 2)

    if not code:
        if not text:
            return None

    location = Location()
    location.mode = Location_Instance_Mode

    # .. the text is the name, with the code standing in for it when there is none ..
    if text:
        location.name = text
    else:
        location.name = code

    # .. and the code is an identifier when the text already took the name ..
    if code:
        if text:
            location.identifier = [{'value': code}]

    # .. the effective date has no place on a Location and is preserved on the Encounter.
    preserve_other_components(accessor, 37, _DLD_Consumed, encounter, context)

    out = context.add(location)
    return out

# ################################################################################################################################

def map_pv1(accessor:'SegmentAccessor', context:'ConversionContext') -> 'Encounter':
    """ Converts PV1 to an Encounter with its practitioners and locations.
    """
    config = context.config

    # Our response to produce
    out = Encounter()

    if context.patient_reference:
        out.subject = context.patient_reference

    # The patient class decides both the encounter class and its status,
    # unknown codes map to the required defaults and are preserved as-is ..
    class_code = accessor.value(2)

    if encounter_class := lookup('patient_class', class_code, config):
        out.class_ = {'system': encounter_class['system'], 'code': encounter_class['code']}
    else:
        out.class_ = Default_Encounter_Class

        if class_code:
            preserve_value(out, context, 'PV1', 2, class_code)

    # .. where a discharge time always means the encounter is over.
    discharge_time = accessor.value(45)

    if discharge_time:
        out.status = Finished_Encounter_Status
    elif status := lookup('patient_class_status', class_code, config):
        out.status = status['code']
    else:
        out.status = Default_Encounter_Status

    # The bed status describes the assigned bed, unknown codes are preserved as-is ..
    bed_status_code = accessor.value(40)
    bed_status      = None

    if bed_status_entry := lookup('bed_status', bed_status_code, config):
        bed_status = {'system': bed_status_entry['system'], 'code': bed_status_entry['code']}
    elif bed_status_code:
        preserve_value(out, context, 'PV1', 40, bed_status_code)

    # .. the assigned location becomes a Location resource, its bed carrying that status ..
    locations:'anylist' = []

    assigned_repetition = accessor.first(3)

    if reference := add_location(assigned_repetition, context, bed_status):
        locations.append({'location': reference})

    # .. a bed status with no bed to describe is preserved on the encounter ..
    elif bed_status:
        serialized_status = accessor.serialize(40)
        preserve_value(out, context, 'PV1', 40, serialized_status)

    # .. and so does the prior location, already left, the temporary one, the pending one,
    # .. still to be moved to, and the prior temporary one, already left as well.
    prior_repetition = accessor.first(6)

    if reference := add_location(prior_repetition, context):
        locations.append({'location': reference, 'status': _Completed_Location_Status})

    temporary_repetition = accessor.first(11)

    if reference := add_location(temporary_repetition, context):
        locations.append({'location': reference})

    pending_repetition = accessor.first(42)

    if reference := add_location(pending_repetition, context):
        locations.append({'location': reference, 'status': _Planned_Location_Status})

    prior_temporary_repetition = accessor.first(43)

    if reference := add_location(prior_temporary_repetition, context):
        locations.append({'location': reference, 'status': _Completed_Location_Status})

    if locations:
        out.location = locations

    # The admission type expresses the encounter's priority.
    admission_type_repetition = accessor.first(4)

    if priority := cwe_to_codeable_concept(admission_type_repetition, config):
        out.priority = priority

    # The patient type is the encounter's type.
    patient_type_repetition = accessor.first(18)

    if patient_type := cwe_to_codeable_concept(patient_type_repetition, config):
        out.type_ = [patient_type]

    # Each kind of caregiver becomes a participant with the proper type.
    participants:'anylist' = []

    _add_encounter_participant(accessor, 7, 'ATND', participants, context)
    _add_encounter_participant(accessor, 8, 'REF', participants, context)
    _add_encounter_participant(accessor, 9, 'CON', participants, context)
    _add_encounter_participant(accessor, 17, 'ADM', participants, context)

    if participants:
        out.participant = participants

    # The hospital service maps to the service type.
    hospital_service_repetition = accessor.first(10)

    if service_type := cwe_to_codeable_concept(hospital_service_repetition, config):
        out.serviceType = service_type

    # The admit source and the discharge disposition end up under hospitalization ..
    hospitalization:'stranydict' = {}

    admit_source_repetition = accessor.first(14)

    if admit_source := cwe_to_codeable_concept(admit_source_repetition, config):
        hospitalization['admitSource'] = admit_source

    disposition_repetition = accessor.first(36)

    if disposition := cwe_to_codeable_concept(disposition_repetition, config):
        hospitalization['dischargeDisposition'] = disposition

    # .. as do the discharge location, the re-admission indicator, the ambulatory statuses,
    # .. the VIP indicator and the diet type.
    if destination := _add_discharge_location(accessor, context, out):
        hospitalization['destination'] = destination

    if readmissions := _coded_list_items(accessor, 13, 'readmission_indicator', out, context):
        hospitalization['reAdmission'] = readmissions[0]

    if arrangements := _coded_list_items(accessor, 15, 'ambulatory_status', out, context):
        hospitalization['specialArrangement'] = arrangements

    if courtesies := _coded_list_items(accessor, 16, 'vip_indicator', out, context):
        hospitalization['specialCourtesy'] = courtesies

    diet_repetition = accessor.first(38)

    if diet := cwe_to_codeable_concept(diet_repetition, config):
        hospitalization['dietPreference'] = [diet]

    if hospitalization:
        out.hospitalization = hospitalization

    # The financial class is kept for the Coverages that follow,
    # the effective date and any further classes are preserved.
    financial_class_code = accessor.component(20, _FC_Class_Component)

    if financial_class_code:
        coding = {'system': Financial_Class_System, 'code': financial_class_code}
        context.financial_class = {'coding': [coding]}

        preserve_other_components(accessor, 20, _FC_Consumed, out, context)

    # The visit, preadmit and alternate visit numbers become the encounter's identifiers.
    identifiers:'anylist' = []

    for position in (19, 5, 50):
        number_repetition = accessor.first(position)

        if identifier := cx_to_identifier(number_repetition, config):
            identifiers.append(identifier)

    if identifiers:
        out.identifier = identifiers

    # Admit and discharge times bound the encounter's period.
    period:'stranydict' = {}

    admit_value = accessor.value(44)
    admit_time = context.datetime(admit_value, 'PV1', 44)

    if admit_time:
        period['start'] = admit_time

    discharge_datetime = context.datetime(discharge_time, 'PV1', 45)

    if discharge_datetime:
        period['end'] = discharge_datetime

    if period:
        out.period = period

    preserve_unmapped(accessor, _PV1_Handled, out, context)

    return out

# ################################################################################################################################

def enrich_pv2(accessor:'SegmentAccessor', context:'ConversionContext', encounter:'Encounter') -> 'None':
    """ Adds the admit reason and the visit description from PV2 to an existing Encounter.
    """
    config = context.config

    reasons:'anylist' = []

    admit_reason_repetition = accessor.first(3)

    if admit_reason := cwe_to_codeable_concept(admit_reason_repetition, config):
        reasons.append(admit_reason)

    visit_description = accessor.value(12)
    if visit_description:
        reasons.append({'text': visit_description})

    for reason in reasons:
        append_to_list_field(encounter, 'reasonCode', reason)

    preserve_unmapped(accessor, _PV2_Handled, encounter, context)

# ################################################################################################################################

def apply_evn(
    accessor:'SegmentAccessor',
    context:'ConversionContext',
    encounter:'Encounter | None',
    default_target:'any_',
    ) -> 'None':
    """ Backs the Encounter period up with EVN's times - the event occurred time first,
    the recorded time second - when PV1-44 provided no start. Everything else EVN
    carries beyond the standard fields is preserved on the default target resource.
    """
    if encounter:

        # The current period comes from the serialized form, reading the typed field would auto-vivify it.
        encounter_dict = encounter.to_dict()

        period = encounter_dict.get('period')
        if period is None:
            period = {}

        if 'start' not in period:

            start_value    = accessor.value(6)
            start_position = 6

            if not start_value:
                start_value    = accessor.value(2)
                start_position = 2

            if start := context.datetime(start_value, 'EVN', start_position):
                period['start'] = start
                encounter.period = period

    # Whatever EVN carries beyond the standard fields survives as extensions.
    if encounter:
        target = encounter
    else:
        target = default_target

    preserve_unmapped(accessor, _EVN_Handled, target, context)

# ################################################################################################################################

def apply_zbe(accessor:'SegmentAccessor', context:'ConversionContext', encounter:'Encounter') -> 'None':
    """ Attaches ZBE - the IHE PAM movement segment - to an existing Encounter.
    The movement IDs become the encounter's identifiers, the movement times, action,
    trigger and responsible units survive as extensions on the Encounter itself.
    """
    config = context.config

    for repetition in accessor.repetitions(1):
        if identifier := ei_to_identifier(repetition, config):
            append_to_list_field(encounter, 'identifier', identifier)

    preserve_unmapped(accessor, _ZBE_Handled, encounter, context)

# ################################################################################################################################

def apply_rol(
    accessor:'SegmentAccessor',
    context:'ConversionContext',
    encounter:'Encounter | None',
    default_target:'any_',
    ) -> 'None':
    """ Turns ROL into an Encounter participant - the role person as a Practitioner,
    the role code as the participation type.
    """
    config = context.config

    # The Practitioner is only created once there is an Encounter to attach it to.
    if encounter:
        person_repetition = accessor.first(4)
        reference = add_practitioner(person_repetition, context)

        if reference:
            role_repetition = accessor.first(3)
            role = cwe_to_codeable_concept(role_repetition, config)

            participant:'stranydict' = {'individual': reference}

            if role:
                participant['type'] = [role]

            append_to_list_field(encounter, 'participant', participant)

            preserve_unmapped(accessor, _ROL_Handled, encounter, context)
            return

    # Without an encounter or a person there is nothing to attach the role to,
    # so the whole segment is preserved on the default target resource.
    preserve_unmapped(accessor, No_Consumed_Fields, default_target, context)

# ################################################################################################################################
# ################################################################################################################################
