# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.fhir import Appointment
from zato.hl7.mappings.codes import lookup
from zato.hl7.mappings.concepts import cwe_to_codeable_concept
from zato.hl7.mappings.datatypes import ei_to_identifier
from zato.hl7.mappings.segments.common import Default_Appointment_Status, Requested_Appointment_Status, add_location, \
    add_practitioner, preserve_other_components, preserve_unmapped, preserve_value

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, intnone, strnone
    from zato.hl7.mappings.context import ConversionContext
    from zato.hl7.mappings.fields import SegmentAccessor
    ConversionContext = ConversionContext
    SegmentAccessor = SegmentAccessor

# ################################################################################################################################
# ################################################################################################################################

# Type aliases
dictnone = 'stranydict | None'

# Which field positions each mapper consumes - anything else that carries data is preserved as an extension.
# SCH-6 and ARQ-6, the event reason, are preserved as-is.
_SCH_Handled = frozenset({1, 2, 7, 8, 9, 10, 11, 12, 16, 25})
_ARQ_Handled = frozenset({1, 2, 7, 8, 9, 10, 11, 15})
_AIS_Handled = frozenset({1, 2, 3})
_AIG_Handled = frozenset({1, 2, 3, 4})
_AIL_Handled = frozenset({1, 2, 3, 4})
_AIP_Handled = frozenset({1, 2, 3, 4})

# Which components of the SCH-11 timing quantity carry the start and end times
_SCH_Timing_Start_Component = 4
_SCH_Timing_End_Component   = 5
_SCH_Timing_Consumed        = frozenset({_SCH_Timing_Start_Component, _SCH_Timing_End_Component})

# Which components of the ARQ-11 requested range carry the start and end times
_ARQ_Range_Start_Component = 1
_ARQ_Range_End_Component   = 2
_ARQ_Range_Consumed        = frozenset({_ARQ_Range_Start_Component, _ARQ_Range_End_Component})

# ################################################################################################################################
# ################################################################################################################################

def _minutes_duration(duration:'strnone', duration_units:'strnone') -> 'intnone':
    """ Reads an appointment duration in minutes out of a duration and its units.
    """
    if not duration:
        return None

    if not duration.isdigit():
        return None

    if duration_units:
        duration_units_lower = duration_units.lower()

        # The unit spells out minutes ..
        if duration_units_lower.startswith('min'):

            out = int(duration)
            return out

        # .. or is their one-letter abbreviation.
        if duration_units_lower == 'm':

            out = int(duration)
            return out

    return None

# ################################################################################################################################

def _contact_participant(
    accessor:'SegmentAccessor',
    position:'int',
    context:'ConversionContext',
    participants:'anylist',
    ) -> 'None':
    """ Turns one XCN contact person field into an accepted Appointment participant.
    """
    for repetition in accessor.repetitions(position):
        if reference := add_practitioner(repetition, context):
            participants.append({'actor': reference, 'status': 'accepted'})

# ################################################################################################################################

def map_sch(accessor:'SegmentAccessor', context:'ConversionContext', participants:'anylist') -> 'Appointment':
    """ Converts SCH to an Appointment, adding the contact people to the participant list
    that comes together once the whole message is walked.
    """
    config = context.config

    # Our response to produce
    out = Appointment()

    # The filler status decides the appointment status, unknown codes
    # map to the default and are preserved as-is ..
    status_code = accessor.component(25, 1)

    if status := lookup('filler_status', status_code, config):
        out.status = status['code']
    else:
        out.status = Default_Appointment_Status

        if status_code:
            preserve_value(out, context, 'SCH', 25, status_code)

    # .. placer and filler appointment IDs become identifiers ..
    identifiers:'anylist' = []

    for position in (1, 2):
        appointment_id_repetition = accessor.first(position)

        if identifier := ei_to_identifier(appointment_id_repetition, config):
            identifiers.append(identifier)

    if identifiers:
        out.identifier = identifiers

    # .. the appointment reason is why the appointment exists ..
    reason_repetition = accessor.first(7)

    if reason := cwe_to_codeable_concept(reason_repetition, config):
        out.reasonCode = [reason]

    # .. the appointment type keeps its coding ..
    type_repetition = accessor.first(8)

    if appointment_type := cwe_to_codeable_concept(type_repetition, config):
        out.appointmentType = appointment_type

    # .. the duration takes its unit at face value when it counts minutes,
    # .. values that make no minutes stay preserved together with their units ..
    duration       = accessor.value(9)
    duration_units = accessor.component(10, 1)
    populated      = accessor.populated_positions()

    if minutes := _minutes_duration(duration, duration_units):
        out.minutesDuration = minutes
    else:
        if duration:
            preserve_value(out, context, 'SCH', 9, duration)

        if 10 in populated:
            units_value = accessor.serialize(10)
            preserve_value(out, context, 'SCH', 10, units_value)

    # .. the timing quantity carries the start and end times, whatever else it carries stays preserved whole ..
    start_value = accessor.component(11, _SCH_Timing_Start_Component)
    start_time = context.datetime(start_value, 'SCH', 11)

    if start_time:
        out.start = start_time

    end_value = accessor.component(11, _SCH_Timing_End_Component)
    end_time = context.datetime(end_value, 'SCH', 11)

    if end_time:
        out.end = end_time

    preserve_other_components(accessor, 11, _SCH_Timing_Consumed, out, context)

    # .. and the placer and filler contact people join the participants.
    _contact_participant(accessor, 12, context, participants)
    _contact_participant(accessor, 16, context, participants)

    preserve_unmapped(accessor, _SCH_Handled, out, context)

    return out

# ################################################################################################################################

def map_arq(accessor:'SegmentAccessor', context:'ConversionContext', participants:'anylist') -> 'Appointment':
    """ Converts ARQ - an appointment request - to a proposed Appointment.
    """
    config = context.config

    # Our response to produce
    out = Appointment()

    # A requested appointment is always a proposal.
    out.status = Requested_Appointment_Status

    # Placer and filler appointment IDs become identifiers ..
    identifiers:'anylist' = []

    for position in (1, 2):
        appointment_id_repetition = accessor.first(position)

        if identifier := ei_to_identifier(appointment_id_repetition, config):
            identifiers.append(identifier)

    if identifiers:
        out.identifier = identifiers

    # .. the appointment reason is why the appointment is asked for ..
    reason_repetition = accessor.first(7)

    if reason := cwe_to_codeable_concept(reason_repetition, config):
        out.reasonCode = [reason]

    # .. the appointment type keeps its coding ..
    type_repetition = accessor.first(8)

    if appointment_type := cwe_to_codeable_concept(type_repetition, config):
        out.appointmentType = appointment_type

    # .. the duration takes its unit at face value when it counts minutes,
    # .. values that make no minutes stay preserved together with their units ..
    duration       = accessor.value(9)
    duration_units = accessor.component(10, 1)
    populated      = accessor.populated_positions()

    if minutes := _minutes_duration(duration, duration_units):
        out.minutesDuration = minutes
    else:
        if duration:
            preserve_value(out, context, 'ARQ', 9, duration)

        if 10 in populated:
            units_value = accessor.serialize(10)
            preserve_value(out, context, 'ARQ', 10, units_value)

    # .. the requested date/time range carries the start and end times,
    # whatever else it carries stays preserved whole ..
    start_value = accessor.component(11, _ARQ_Range_Start_Component)
    start_time = context.datetime(start_value, 'ARQ', 11)

    if start_time:
        out.start = start_time

    end_value = accessor.component(11, _ARQ_Range_End_Component)
    end_time = context.datetime(end_value, 'ARQ', 11)

    if end_time:
        out.end = end_time

    preserve_other_components(accessor, 11, _ARQ_Range_Consumed, out, context)

    # .. and the placer contact person joins the participants.
    _contact_participant(accessor, 15, context, participants)

    preserve_unmapped(accessor, _ARQ_Handled, out, context)

    return out

# ################################################################################################################################

def enrich_ais(accessor:'SegmentAccessor', context:'ConversionContext', appointment:'Appointment') -> 'None':
    """ Adds the requested service from AIS to an existing Appointment.
    """
    config = context.config

    service_repetition = accessor.first(3)

    if service_type := cwe_to_codeable_concept(service_repetition, config):
        appointment.serviceType = [service_type]

    preserve_unmapped(accessor, _AIS_Handled, appointment, context)

# ################################################################################################################################

def aig_participant(accessor:'SegmentAccessor', context:'ConversionContext', appointment:'Appointment') -> 'dictnone':
    """ Turns AIG - a general scheduled resource - into an Appointment participant with a display name.
    """
    display = accessor.component(3, 2)
    if not display:
        display = accessor.component(3, 1)

    preserve_unmapped(accessor, _AIG_Handled, appointment, context)

    if not display:
        return None

    out = {'actor': {'display': display}, 'status': 'accepted'}
    return out

# ################################################################################################################################

def ail_participant(accessor:'SegmentAccessor', context:'ConversionContext', appointment:'Appointment') -> 'dictnone':
    """ Turns AIL - a scheduled location - into an Appointment participant backed by a Location resource.
    """
    location_repetition = accessor.first(3)
    reference = add_location(location_repetition, context)

    preserve_unmapped(accessor, _AIL_Handled, appointment, context)

    if not reference:
        return None

    out = {'actor': reference, 'status': 'accepted'}
    return out

# ################################################################################################################################

def aip_participant(accessor:'SegmentAccessor', context:'ConversionContext', appointment:'Appointment') -> 'dictnone':
    """ Turns AIP - scheduled personnel - into an Appointment participant backed by a Practitioner resource.
    """
    person_repetition = accessor.first(3)
    reference = add_practitioner(person_repetition, context)

    preserve_unmapped(accessor, _AIP_Handled, appointment, context)

    if not reference:
        return None

    out = {'actor': reference, 'status': 'accepted'}
    return out

# ################################################################################################################################
# ################################################################################################################################
