# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone

# ################################################################################################################################
# ################################################################################################################################

Minutes_Per_Hour = 60
Microseconds_Per_Second = 1_000_000

# The length of an HH:MM string and where its colon sits
Time_Pattern_Length = 5
Time_Colon_Index = 2

Max_Hour = 23
Max_Minute = 59

# ################################################################################################################################
# ################################################################################################################################

class TimeOfDayError(Exception):
    """ A time of day that is not an HH:MM string.
    """

# ################################################################################################################################
# ################################################################################################################################

def validate_hh_mm(value:'str', field_name:'str') -> 'None':
    """ Raises TimeOfDayError unless the value is HH:MM.
    """

    # Must be exactly five characters, HH:MM ..
    value_length = len(value)
    if value_length != Time_Pattern_Length:
        raise TimeOfDayError(f'{field_name} must be in HH:MM format, got: {value}')

    # .. the colon must be where HH:MM has it ..
    if value[Time_Colon_Index] != ':':
        raise TimeOfDayError(f'{field_name} must be in HH:MM format, got: {value}')

    hours = value[:Time_Colon_Index]
    minutes = value[Time_Colon_Index + 1:]

    # .. hours must be digits ..
    if not hours.isdigit():
        raise TimeOfDayError(f'{field_name} must be in HH:MM format, got: {value}')

    # .. and so must minutes ..
    if not minutes.isdigit():
        raise TimeOfDayError(f'{field_name} must be in HH:MM format, got: {value}')

    hours = int(hours)
    minutes = int(minutes)

    # .. hours must fit a day ..
    if hours > Max_Hour:
        raise TimeOfDayError(f'{field_name} hours out of range: {value}')

    # .. and minutes an hour.
    if minutes > Max_Minute:
        raise TimeOfDayError(f'{field_name} minutes out of range: {value}')

# ################################################################################################################################

def hh_mm_to_minutes(value:'str') -> 'int':
    """ An HH:MM string as minutes since midnight.
    """
    hours = value[:Time_Colon_Index]
    minutes = value[Time_Colon_Index + 1:]

    hours = int(hours)
    minutes = int(minutes)

    out = hours * Minutes_Per_Hour + minutes
    return out

# ################################################################################################################################

def time_in_range(now_minutes:'int', from_minutes:'int', to_minutes:'int') -> 'bool':
    """ Whether now falls within [from, to), all in minutes since midnight, a start after its end crossing midnight.
    """

    # A range within one day ..
    if from_minutes <= to_minutes:
        out = from_minutes <= now_minutes < to_minutes

    # .. or one crossing midnight.
    else:
        out = now_minutes >= from_minutes or now_minutes < to_minutes

    return out

# ################################################################################################################################

def datetime_to_minutes(value:'datetime') -> 'int':
    """ The time of day of a datetime as minutes since midnight, a naive datetime being UTC.
    """
    out = value.hour * Minutes_Per_Hour + value.minute
    return out

# ################################################################################################################################

def now_us_to_minutes(now_us:'int') -> 'int':
    """ A microseconds-since-epoch timestamp as minutes since midnight, UTC.
    """
    now_seconds = now_us // Microseconds_Per_Second
    now = datetime.fromtimestamp(now_seconds, tz=timezone.utc)

    out = datetime_to_minutes(now)
    return out

# ################################################################################################################################
# ################################################################################################################################
