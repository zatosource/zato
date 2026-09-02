# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.fhir import Encounter
from zato.hl7.mappings.codes import lookup
from zato.hl7.mappings.concepts import cwe_to_codeable_concept
from zato.hl7.mappings.datatypes import cx_to_identifier, dtm_to_datetime, ei_to_identifier
from zato.hl7.mappings.segments.common import Default_Encounter_Class, Default_Encounter_Status, \
    Finished_Encounter_Status, No_Consumed_Fields, Participation_Type_System, add_location, add_practitioner, \
    append_to_list_field, preserve_unmapped, preserve_value

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict
    from zato.hl7.mappings.context import ConversionContext
    from zato.hl7.mappings.fields import SegmentAccessor
    ConversionContext = ConversionContext
    SegmentAccessor = SegmentAccessor
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# Which field positions each mapper consumes - anything else that carries data is preserved as an extension.
_PV1_Handled = frozenset({1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 17, 19, 36, 44, 45, 50})
_PV2_Handled = frozenset({3, 12})
_ROL_Handled = frozenset({1, 3, 4})

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

    # The assigned, prior and temporary locations become Location resources.
    locations:'anylist' = []

    for position in (3, 6, 11):
        location_repetition = accessor.first(position)

        if reference := add_location(location_repetition, context):
            locations.append({'location': reference})

    if locations:
        out.location = locations

    # The admission type expresses the encounter's priority.
    admission_type_repetition = accessor.first(4)

    if priority := cwe_to_codeable_concept(admission_type_repetition, config):
        out.priority = priority

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

    # The admit source and the discharge disposition end up under hospitalization.
    hospitalization:'stranydict' = {}

    admit_source_repetition = accessor.first(14)

    if admit_source := cwe_to_codeable_concept(admit_source_repetition, config):
        hospitalization['admitSource'] = admit_source

    disposition_repetition = accessor.first(36)

    if disposition := cwe_to_codeable_concept(disposition_repetition, config):
        hospitalization['dischargeDisposition'] = disposition

    if hospitalization:
        out.hospitalization = hospitalization

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
    admit_time = dtm_to_datetime(admit_value, config)

    if admit_time:
        period['start'] = admit_time

    discharge_datetime = dtm_to_datetime(discharge_time, config)
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
    config = context.config

    if encounter:

        # The current period comes from the serialized form, reading the typed field would auto-vivify it.
        encounter_dict = encounter.to_dict()

        period = encounter_dict.get('period')
        if period is None:
            period = {}

        if 'start' not in period:

            start_value = accessor.value(6)
            if not start_value:
                start_value = accessor.value(2)

            if start := dtm_to_datetime(start_value, config):
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
