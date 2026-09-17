# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads
from typing import NamedTuple

# Zato
from zato.common.alerting.config_map import Silence_Slots_Field_Name, Silence_Window_Field_Name
from zato.common.util.time_of_day import datetime_to_minutes, hh_mm_to_minutes, time_in_range, TimeOfDayError, \
    validate_hh_mm

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.typing_ import anydict, anylist
    anydict = anydict
    anylist = anylist
    datetime = datetime

# ################################################################################################################################
# ################################################################################################################################

# The keys of one slot in the list
Slot_Time_From = 'time_from'
Slot_Time_To   = 'time_to'
Slot_Is_On     = 'is_on'
Slot_Seconds   = 'silence_seconds'

# The switch of the all-day slot
Traffic_Expected_Field_Name = 'traffic_expected'

# The least a slot's silence may be
Min_Silence_Seconds = 1

# ################################################################################################################################
# ################################################################################################################################

class TimeSlotsError(Exception):
    """ A list of time slots that is not valid.
    """

# ################################################################################################################################
# ################################################################################################################################

class SilenceResult(NamedTuple):
    is_on: bool
    seconds: int

# ################################################################################################################################
# ################################################################################################################################

def validate_silence_slots(text:'str') -> 'anylist':
    """ The slots a JSON list holds, each checked. Raises TimeSlotsError.
    """
    try:
        out = loads(text)
    except ValueError:
        raise TimeSlotsError(f'Time slots must be a JSON list, got: {text!r}')

    if not isinstance(out, list):
        raise TimeSlotsError(f'Time slots must be a JSON list, got: {text!r}')

    for index, slot in enumerate(out, 1):

        if not isinstance(slot, dict):
            raise TimeSlotsError(f'Time slot {index} must be an object, got: {slot!r}')

        for key in (Slot_Time_From, Slot_Time_To, Slot_Is_On, Slot_Seconds):
            if key not in slot:
                raise TimeSlotsError(f'Time slot {index} has no {key}')

        try:
            validate_hh_mm(slot[Slot_Time_From], f'Time slot {index} {Slot_Time_From}')
            validate_hh_mm(slot[Slot_Time_To], f'Time slot {index} {Slot_Time_To}')
        except TimeOfDayError as e:
            raise TimeSlotsError(e.args[0])

        if not isinstance(slot[Slot_Is_On], bool):
            raise TimeSlotsError(f'Time slot {index} {Slot_Is_On} must be true or false, got: {slot[Slot_Is_On]!r}')

        seconds = slot[Slot_Seconds]

        if not isinstance(seconds, int):
            raise TimeSlotsError(f'Time slot {index} {Slot_Seconds} must be a number of at least {Min_Silence_Seconds}, got: {seconds!r}')

        if isinstance(seconds, bool):
            raise TimeSlotsError(f'Time slot {index} {Slot_Seconds} must be a number of at least {Min_Silence_Seconds}, got: {seconds!r}')

        if seconds < Min_Silence_Seconds:
            raise TimeSlotsError(f'Time slot {index} {Slot_Seconds} must be a number of at least {Min_Silence_Seconds}, got: {seconds!r}')

    return out

# ################################################################################################################################

def resolve_silence(values:'anydict', now:'datetime') -> 'SilenceResult':
    """ The switch and the seconds of the first time slot containing the time of day, the all-day ones when none does.
    """
    now_minutes = datetime_to_minutes(now)

    slots = loads(values[Silence_Slots_Field_Name])

    for slot in slots:
        from_minutes = hh_mm_to_minutes(slot[Slot_Time_From])
        to_minutes = hh_mm_to_minutes(slot[Slot_Time_To])

        if time_in_range(now_minutes, from_minutes, to_minutes):
            out = SilenceResult(slot[Slot_Is_On], slot[Slot_Seconds])
            break
    else:
        out = SilenceResult(values[Traffic_Expected_Field_Name], values[Silence_Window_Field_Name])

    return out

# ################################################################################################################################
# ################################################################################################################################
