# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The time slots of an object's silence alert - ranges of the day, each with a switch and
# a duration of its own, kept as one JSON list next to the all-day switch and duration.
# The list is what the Alerts tab's time slots popover writes and what the sweep resolves
# against the time of day, the first matching range winning and the all-day slot answering
# when none does, the way a rate limit's slots are resolved.

# stdlib
from json import loads

# Zato
from zato.common.alerting.config_map import Silence_Slots_Field_Name, Silence_Window_Field_Name
from zato.common.util.time_of_day import datetime_to_minutes, hh_mm_to_minutes, time_in_range, validate_hh_mm

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
Slot_Time_To = 'time_to'
Slot_Is_On = 'is_on'
Slot_Seconds = 'silence_seconds'

# The switch of the all-day slot - what the object's own toggle is called
Traffic_Expected_Field_Name = 'traffic_expected'

# A silence shorter than this makes no sense to measure
Min_Silence_Seconds = 1

# ################################################################################################################################
# ################################################################################################################################

def validate_silence_slots(text:'str') -> 'anylist':
    """ The slots a JSON list holds, each checked - both ends of the range as HH:MM, a switch that is a boolean
    and a number of seconds of at least one. Raises ValueError naming the slot at fault.
    """
    try:
        out = loads(text)
    except ValueError:
        raise ValueError(f'Time slots must be a JSON list, got: {text!r}')

    if not isinstance(out, list):
        raise ValueError(f'Time slots must be a JSON list, got: {text!r}')

    for index, slot in enumerate(out, 1):

        if not isinstance(slot, dict):
            raise ValueError(f'Time slot {index} must be an object, got: {slot!r}')

        for key in (Slot_Time_From, Slot_Time_To, Slot_Is_On, Slot_Seconds):
            if key not in slot:
                raise ValueError(f'Time slot {index} has no {key}')

        validate_hh_mm(slot[Slot_Time_From], f'Time slot {index} {Slot_Time_From}')
        validate_hh_mm(slot[Slot_Time_To], f'Time slot {index} {Slot_Time_To}')

        if not isinstance(slot[Slot_Is_On], bool):
            raise ValueError(f'Time slot {index} {Slot_Is_On} must be true or false, got: {slot[Slot_Is_On]!r}')

        seconds = slot[Slot_Seconds]

        if not isinstance(seconds, int) or isinstance(seconds, bool) or seconds < Min_Silence_Seconds:
            raise ValueError(f'Time slot {index} {Slot_Seconds} must be a number of at least {Min_Silence_Seconds}, got: {seconds!r}')

    return out

# ################################################################################################################################

def resolve_silence(values:'anydict', now:'datetime') -> 'tuple[bool, int]':
    """ Whether an object's silence alert is on right now and after how many seconds of silence it raises -
    the first time slot containing the time of day answers, the all-day switch and duration when none does.
    """
    now_minutes = datetime_to_minutes(now)

    slots = loads(values[Silence_Slots_Field_Name])

    for slot in slots:
        from_minutes = hh_mm_to_minutes(slot[Slot_Time_From])
        to_minutes = hh_mm_to_minutes(slot[Slot_Time_To])

        # The first range the moment falls in decides, in the order the slots were kept in
        if time_in_range(now_minutes, from_minutes, to_minutes):
            out = (slot[Slot_Is_On], slot[Slot_Seconds])
            return out

    out = (values[Traffic_Expected_Field_Name], values[Silence_Window_Field_Name])
    return out

# ################################################################################################################################
# ################################################################################################################################
