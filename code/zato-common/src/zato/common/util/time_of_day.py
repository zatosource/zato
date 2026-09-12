# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The time of day as ranges of HH:MM - what rate limiting slots and alerting time slots
# are both built on. A range may cross midnight, 23:00-02:00 being the three hours around it,
# and every reading is in minutes since midnight, UTC.

# stdlib
from datetime import datetime, timezone

# ################################################################################################################################
# ################################################################################################################################

Minutes_Per_Hour = 60
Hours_Per_Day = 24
Microseconds_Per_Second = 1_000_000

# The length of an HH:MM string and where its colon sits
Time_Pattern_Length = 5
Time_Colon_Index = 2

Max_Hour = 23
Max_Minute = 59

# ################################################################################################################################
# ################################################################################################################################

def validate_hh_mm(value:'str', field_name:'str') -> 'None':
    """ Raises ValueError unless the value is an HH:MM time of day.
    """

    # Must be exactly five characters, HH:MM ..
    if len(value) != Time_Pattern_Length:
        raise ValueError(f'{field_name} must be in HH:MM format, got: {value}')

    # .. the colon must be where HH:MM has it ..
    if value[Time_Colon_Index] != ':':
        raise ValueError(f'{field_name} must be in HH:MM format, got: {value}')

    hours_str = value[:Time_Colon_Index]
    minutes_str = value[Time_Colon_Index + 1:]

    # .. hours and minutes must be digits ..
    if not hours_str.isdigit() or not minutes_str.isdigit():
        raise ValueError(f'{field_name} must be in HH:MM format, got: {value}')

    hours = int(hours_str)
    minutes = int(minutes_str)

    # .. hours must fit a day ..
    if hours > Max_Hour:
        raise ValueError(f'{field_name} hours out of range: {value}')

    # .. and minutes an hour.
    if minutes > Max_Minute:
        raise ValueError(f'{field_name} minutes out of range: {value}')

# ################################################################################################################################

def hh_mm_to_minutes(value:'str') -> 'int':
    """ An HH:MM string as minutes since midnight.
    """
    hours_str = value[:Time_Colon_Index]
    minutes_str = value[Time_Colon_Index + 1:]

    hours = int(hours_str)
    minutes = int(minutes_str)

    out = hours * Minutes_Per_Hour + minutes
    return out

# ################################################################################################################################

def time_in_range(now_minutes:'int', from_minutes:'int', to_minutes:'int') -> 'bool':
    """ Whether now falls within [from, to), all in minutes since midnight. A range whose start
    is after its end crosses midnight, 23:00-02:00 being 1380 to 120.
    """

    # A range within one day, 09:00-17:00 ..
    if from_minutes <= to_minutes:
        out = from_minutes <= now_minutes < to_minutes

    # .. or one crossing midnight, 23:00-02:00.
    else:
        out = now_minutes >= from_minutes or now_minutes < to_minutes

    return out

# ################################################################################################################################

def datetime_to_minutes(value:'datetime') -> 'int':
    """ The time of day of a datetime as minutes since midnight - a naive datetime is taken as UTC.
    """
    out = value.hour * Minutes_Per_Hour + value.minute
    return out

# ################################################################################################################################

def now_us_to_minutes(now_us:'int') -> 'int':
    """ A microseconds-since-epoch timestamp as minutes since midnight, UTC.
    """
    now_secs = now_us // Microseconds_Per_Second
    now_dt = datetime.fromtimestamp(now_secs, tz=timezone.utc)

    out = datetime_to_minutes(now_dt)
    return out

# ################################################################################################################################
# ################################################################################################################################
