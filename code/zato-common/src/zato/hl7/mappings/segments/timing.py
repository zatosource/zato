# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re
from typing import NamedTuple

# Zato
from zato.hl7.mappings.codes import lookup
from zato.hl7.mappings.concepts import cwe_to_codeable_concept, parse_number, quantity
from zato.hl7.mappings.datetimes import tm_to_time
from zato.hl7.mappings.fields import component_as_repetition, component_value
from zato.hl7.mappings.segments.common import preserve_inexact_number, preserve_other_components, preserve_unmapped, \
    preserve_value

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, dictnone, stranydict, strnone
    from zato.hl7.mappings.context import ConversionContext
    from zato.hl7.mappings.fields import SegmentAccessor
    ConversionContext = ConversionContext
    SegmentAccessor = SegmentAccessor
    any_ = any_
    dictnone = dictnone

# ################################################################################################################################
# ################################################################################################################################

# Which TQ1 field positions the timing mappers consume.
_TQ1_Handled = frozenset({1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14})

# Which TQ components carry the interval, the start time, the end time and the priority.
_TQ_Interval_Component = 2
_TQ_Start_Component    = 4
_TQ_End_Component      = 5
_TQ_Priority_Component = 6
_TQ_Consumed = frozenset({
    _TQ_Interval_Component,
    _TQ_Start_Component,
    _TQ_End_Component,
    _TQ_Priority_Component,
})

# The UCUM time units a duration may use, keyed by how they arrive - UCUM codes themselves and the common spellings
_Duration_Units = {
    's': 's',
    'S': 's',
    'sec': 's',
    'SEC': 's',
    'min': 'min',
    'MIN': 'min',
    'h': 'h',
    'H': 'h',
    'hr': 'h',
    'HR': 'h',
    'd': 'd',
    'D': 'd',
    'wk': 'wk',
    'WK': 'wk',
    'W': 'wk',
    'mo': 'mo',
    'MO': 'mo',
    'L': 'mo',
    'a': 'a',
    'A': 'a',
}

# How many minutes each duration unit an offset may be expressed in spans
_Minutes_Per_Unit = {
    'min': 1,
    'h': 60,
    'd': 1440,
}

# The UCUM system durations are coded in
_UCUM_System = 'http://unitsofmeasure.org'

# The repeat pattern of table HL70335 that spells out an interval - Q2H, Q30M, Q1D and the like
_Interval_Pattern = re.compile(r'^Q(\d+)([SMHDWL])$')

# The period units the interval pattern's letters stand for
_Interval_Units = {
    'S': 's',
    'M': 'min',
    'H': 'h',
    'D': 'd',
    'W': 'wk',
    'L': 'mo',
}

# The repeat patterns of table HL70335 with a fixed meaning, as Timing.repeat elements
_Fixed_Repeat_Patterns = {
    'QD': {'frequency': 1, 'period': 1, 'periodUnit': 'd'},
    'QOD': {'frequency': 1, 'period': 2, 'periodUnit': 'd'},
    'BID': {'frequency': 2, 'period': 1, 'periodUnit': 'd'},
    'TID': {'frequency': 3, 'period': 1, 'periodUnit': 'd'},
    'QID': {'frequency': 4, 'period': 1, 'periodUnit': 'd'},
    'QAM': {'frequency': 1, 'period': 1, 'periodUnit': 'd', 'when': ['MORN']},
    'QPM': {'frequency': 1, 'period': 1, 'periodUnit': 'd', 'when': ['EVE']},
    'QHS': {'frequency': 1, 'period': 1, 'periodUnit': 'd', 'when': ['HS']},
    'QAC': {'when': ['AC']},
    'QPC': {'when': ['PC']},
    'QACM': {'when': ['ACM']},
    'QACD': {'when': ['ACD']},
    'QACV': {'when': ['ACV']},
    'QPCM': {'when': ['PCM']},
    'QPCD': {'when': ['PCD']},
    'QPCV': {'when': ['PCV']},
    'ONCE': {'count': 1},
}

# The repeat pattern that says the service is given only when needed
_As_Needed_Pattern = 'PRN'

# Which CQ - composite quantity - component carries the units, a CWE of its own
_CQ_Units_Component = 2

# The repeat elements of a Timing that says nothing beyond when the service starts and ends
_Bounds_Only = frozenset({'boundsPeriod'})

# ################################################################################################################################
# ################################################################################################################################

class BuiltTiming(NamedTuple):
    """ What a TQ1 spells out - the Timing itself, or None when nothing in the segment makes one,
    and whether the repeat pattern said the service is given only as needed.
    """
    timing:'dictnone'
    as_needed:'bool'

# ################################################################################################################################

class Duration(NamedTuple):
    """ A length of time - how much of a UCUM time unit it spans.
    """
    value:'float'
    unit:'str'

# ################################################################################################################################
# ################################################################################################################################

def _cq_quantity(
    accessor:'SegmentAccessor',
    position:'int',
    target:'any_',
    context:'ConversionContext',
    ) -> 'dictnone':
    """ Builds a Quantity from a CQ - composite quantity with units - field, preserving values that are not numbers.
    """
    config = context.config
    segment_id = accessor.segment_id

    # An empty field builds no quantity ..
    amount = accessor.value(position)

    if not amount:
        return None

    # .. an amount that is not a number is preserved whole ..
    number = parse_number(amount)

    if not number:
        serialized = accessor.serialize(position)
        preserve_value(target, context, segment_id, position, serialized)
        return None

    # .. a number the float cannot carry exactly keeps its digits as an extension ..
    if not number.is_exact:
        preserve_inexact_number(target, context, segment_id, position, amount)

    # .. and the units component says what the number counts.
    repetition = accessor.first(position)
    units_cwe = component_as_repetition(repetition, _CQ_Units_Component)
    units = cwe_to_codeable_concept(units_cwe, config)

    out = quantity(number.value, units)
    return out

# ################################################################################################################################

def _cq_duration(
    accessor:'SegmentAccessor',
    position:'int',
    target:'any_',
    context:'ConversionContext',
    ) -> 'Duration | None':
    """ Reads a CQ field as a duration - a number and a UCUM time unit. A value whose unit is not
    a time unit, or which is not a number, is preserved as-is.
    """
    segment_id = accessor.segment_id

    amount = accessor.value(position)

    if not amount:
        return None

    unit_name = accessor.component(position, _CQ_Units_Component)
    unit = None

    if unit_name:
        unit = _Duration_Units.get(unit_name)

    number = parse_number(amount)
    serialized = accessor.serialize(position)

    if not number:
        preserve_value(target, context, segment_id, position, serialized)
        return None

    if not unit:
        preserve_value(target, context, segment_id, position, serialized)
        return None

    if not number.is_exact:
        preserve_inexact_number(target, context, segment_id, position, amount)

    out = Duration(number.value, unit)
    return out

# ################################################################################################################################

def _apply_repeat_pattern(
    code:'str',
    repeat:'stranydict',
    ) -> 'bool':
    """ Applies one HL70335 repeat pattern code to a Timing.repeat, telling whether the code was understood.
    """
    if fixed := _Fixed_Repeat_Patterns.get(code):
        repeat.update(fixed)
        return True

    if match := _Interval_Pattern.match(code):
        interval = match.group(1)
        unit_letter = match.group(2)

        repeat['frequency'] = 1
        repeat['period'] = int(interval)
        repeat['periodUnit'] = _Interval_Units[unit_letter]
        return True

    return False

# ################################################################################################################################

def _build_timing(
    accessor:'SegmentAccessor',
    target:'any_',
    context:'ConversionContext',
    start_time:'strnone',
    end_time:'strnone',
    ) -> 'BuiltTiming':
    """ Builds a FHIR Timing from a TQ1 - the repeat pattern, explicit times, relative offset,
    durations and occurrence count make up the repeat, the start and end its bounds.
    Values that cannot be expressed are preserved on the target.
    """
    as_needed = False
    repeat:'stranydict' = {}

    # The start and end times bound the repeat, and so does the service duration when there are none ..
    bounds:'stranydict' = {}

    if start_time:
        bounds['start'] = start_time

    if end_time:
        bounds['end'] = end_time

    if bounds:
        repeat['boundsPeriod'] = bounds

    if service_duration := _cq_duration(accessor, 6, target, context):

        if bounds:
            serialized = accessor.serialize(6)
            preserve_value(target, context, 'TQ1', 6, serialized)
        else:
            repeat['boundsDuration'] = {
                'value': service_duration.value,
                'unit': service_duration.unit,
                'system': _UCUM_System,
                'code': service_duration.unit,
            }

    # .. each repeat pattern that is understood shapes the frequency and period,
    # .. the one meaning as-needed goes to the caller through the return value ..
    for repetition in accessor.repetitions(3):
        code = component_value(repetition, 1)
        if not code:
            continue

        if code == _As_Needed_Pattern:
            as_needed = True
            continue

        if not _apply_repeat_pattern(code, repeat):
            preserve_value(target, context, 'TQ1', 3, code)

    # .. the explicit times are the times of day ..
    times_of_day:'anylist' = []

    for repetition in accessor.repetitions(4):
        value = component_value(repetition, 1)

        if time_value := tm_to_time(value):
            times_of_day.append(time_value)
        elif value:
            preserve_value(target, context, 'TQ1', 4, value)

    if times_of_day:
        repeat['timeOfDay'] = times_of_day

    # .. the relative time is the offset, in minutes ..
    if relative := _cq_duration(accessor, 5, target, context):

        if minutes_per_unit := _Minutes_Per_Unit.get(relative.unit):
            offset = relative.value * minutes_per_unit
            repeat['offset'] = int(offset)
        else:
            serialized = accessor.serialize(5)
            preserve_value(target, context, 'TQ1', 5, serialized)

    # .. the occurrence duration is how long each occurrence lasts ..
    if occurrence_duration := _cq_duration(accessor, 13, target, context):
        repeat['duration']     = occurrence_duration.value
        repeat['durationUnit'] = occurrence_duration.unit

    # .. and the total occurrences the count.
    total = accessor.value(14)

    if total:
        if total.isdigit():
            repeat['count'] = int(total)
        else:
            preserve_value(target, context, 'TQ1', 14, total)

    timing = None

    if repeat:
        timing = {'repeat': repeat}

    out = BuiltTiming(timing, as_needed)
    return out

# ################################################################################################################################

def apply_tq_timing(
    accessor:'SegmentAccessor',
    position:'int',
    service_request:'any_',
    context:'ConversionContext',
    ) -> 'None':
    """ Applies one TQ - quantity/timing - field to a ServiceRequest, the start and end
    times becoming the occurrence and the priority component the request priority.
    Whatever else the field carries is preserved whole.
    """
    config = context.config
    segment_id = accessor.segment_id

    # The start and end times bound when the service takes place ..
    start_value = accessor.component(position, _TQ_Start_Component)
    start_time  = context.datetime(start_value, segment_id, position)

    end_value = accessor.component(position, _TQ_End_Component)
    end_time  = context.datetime(end_value, segment_id, position)

    if start_time:
        if end_time:
            service_request.occurrencePeriod = {'start': start_time, 'end': end_time}
        else:
            service_request.occurrenceDateTime = start_time
    elif end_time:
        service_request.occurrencePeriod = {'end': end_time}

    # .. and the priority component says how urgent it is,
    # .. with the priority word arriving in the interval component too.
    priority_code = accessor.component(position, _TQ_Priority_Component)

    if not priority_code:
        priority_code = accessor.component(position, _TQ_Interval_Component)

    if priority := lookup('order_priority', priority_code, config):
        service_request.priority = priority['code']
    else:
        if priority_code:
            preserve_value(service_request, context, segment_id, position, priority_code)

    preserve_other_components(accessor, position, _TQ_Consumed, service_request, context)

# ################################################################################################################################

def _apply_priority(accessor:'SegmentAccessor', target:'any_', context:'ConversionContext') -> 'None':
    """ The TQ1 priority maps through the standard table onto the target, unknown codes are preserved as-is.
    """
    config = context.config

    priority_code = accessor.component(9, 1)

    if priority := lookup('order_priority', priority_code, config):
        target.priority = priority['code']
    else:
        if priority_code:
            preserve_value(target, context, 'TQ1', 9, priority_code)

# ################################################################################################################################

def _build_tq1_timing(accessor:'SegmentAccessor', context:'ConversionContext', target:'any_') -> 'BuiltTiming':
    """ Reads a TQ1's start and end times and builds the Timing the rest of the segment spells out around them.
    A segment with a bare start and end and nothing richer still yields a Timing bounded by them.
    """
    start_value = accessor.value(7)
    start_time  = context.datetime(start_value, 'TQ1', 7)

    end_value = accessor.value(8)
    end_time = context.datetime(end_value, 'TQ1', 8)

    out = _build_timing(accessor, target, context, start_time, end_time)
    return out

# ################################################################################################################################

def apply_tq1(accessor:'SegmentAccessor', context:'ConversionContext', service_request:'any_') -> 'None':
    """ Applies TQ1 to a ServiceRequest. A bare start and end become the occurrence, anything richer
    a Timing - TQ1 is the authoritative timing, so it replaces whatever ORC or OBR provided.
    The quantity becomes the request's quantity, the condition its as-needed reason.
    """
    built = _build_tq1_timing(accessor, context, service_request)
    instruction = accessor.value(11)

    # A Timing that carries nothing but its bounds becomes the occurrence itself,
    # .. anything richer - or a text instruction, which becomes the Timing's code - stays a Timing ..
    occurrence_timing:'dictnone' = None
    bounds:'dictnone'            = None

    if timing := built.timing:
        repeat:'stranydict' = timing['repeat']
        repeat_elements = frozenset(repeat)

        if repeat_elements == _Bounds_Only:
            bounds = repeat['boundsPeriod']
        else:
            occurrence_timing = timing

    if instruction:
        if not occurrence_timing:
            occurrence_timing = {}

            # The bounds go back into the Timing the instruction calls for.
            if bounds:
                occurrence_timing['repeat'] = {'boundsPeriod': bounds}

        occurrence_timing['code'] = {'text': instruction}

    # .. and whichever shape it takes replaces the occurrence ORC or OBR provided.
    if occurrence_timing:
        service_request.occurrenceDateTime = None
        service_request.occurrencePeriod   = None
        service_request.occurrenceTiming   = occurrence_timing

    elif bounds:
        service_request.occurrenceTiming = None

        if 'start' in bounds:
            if 'end' in bounds:
                service_request.occurrenceDateTime = None
                service_request.occurrencePeriod   = bounds
            else:
                service_request.occurrencePeriod   = None
                service_request.occurrenceDateTime = bounds['start']
        else:
            service_request.occurrenceDateTime = None
            service_request.occurrencePeriod   = bounds

    _apply_priority(accessor, service_request, context)

    # The quantity is how much of the service is requested ..
    if amount := _cq_quantity(accessor, 2, service_request, context):
        service_request.quantityQuantity = amount

    # .. and the condition says when it is needed, as words when there are any.
    condition = accessor.value(10)

    if condition:
        service_request.asNeededCodeableConcept = {'text': condition}
    elif built.as_needed:
        service_request.asNeededBoolean = True

    preserve_unmapped(accessor, _TQ1_Handled, service_request, context)

# ################################################################################################################################

def apply_tq1_to_dosage(accessor:'SegmentAccessor', context:'ConversionContext', medication:'any_') -> 'None':
    """ Applies TQ1 to a MedicationRequest or a MedicationDispense - the timing, the dose, the condition
    and the text instruction all go to the first dosage instruction, the priority to the resource itself.
    """

    # The current instructions come from the serialized form, reading the typed field would auto-vivify it.
    current = medication.to_dict()

    instructions = current.get('dosageInstruction')

    if instructions is None:
        instructions = [{}]

    dosage = instructions[0]

    built = _build_tq1_timing(accessor, context, medication)

    if built.timing:
        dosage['timing'] = built.timing

    # The quantity is the dose ..
    if dose := _cq_quantity(accessor, 2, medication, context):
        dosage['doseAndRate'] = [{'doseQuantity': dose}]

    # .. the condition says when the dose is needed, as words when there are any ..
    condition = accessor.value(10)

    if condition:
        dosage['asNeededCodeableConcept'] = {'text': condition}
    elif built.as_needed:
        dosage['asNeededBoolean'] = True

    # .. and the text instruction is the dosage in words.
    instruction = accessor.value(11)
    if instruction:
        dosage['text'] = instruction

    if dosage:
        medication.dosageInstruction = instructions

    # A MedicationRequest carries a priority, a MedicationDispense does not.
    if current['resourceType'] == 'MedicationRequest':
        _apply_priority(accessor, medication, context)
    else:
        if priority_code := accessor.component(9, 1):
            preserve_value(medication, context, 'TQ1', 9, priority_code)

    preserve_unmapped(accessor, _TQ1_Handled, medication, context)

# ################################################################################################################################
# ################################################################################################################################
