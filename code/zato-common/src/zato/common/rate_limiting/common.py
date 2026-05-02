# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# ################################################################################################################################
# ################################################################################################################################

Microseconds_Per_Second = 1_000_000
Microtokens_Per_Token = 1_000_000

Seconds_Per_Minute = 60
Seconds_Per_Hour = 3600
Seconds_Per_Day = 86400

January = 1
December = 12

Window_Unit_Second = 'second'
Window_Unit_Minute = 'minute'
Window_Unit_Hour   = 'hour'
Window_Unit_Day    = 'day'
Window_Unit_Month  = 'month'

_all_window_units = {
    Window_Unit_Second,
    Window_Unit_Minute,
    Window_Unit_Hour,
    Window_Unit_Day,
    Window_Unit_Month,
}

# ################################################################################################################################
# ################################################################################################################################

class RateLimitError(Exception):
    """ Represents a rate limiter failure: invalid configuration, arithmetic overflow, or a clock error.
    """

# ################################################################################################################################
# ################################################################################################################################

def current_time_us() -> 'int':
    """ Returns the current wall clock time in microseconds since Unix epoch.
    """
    now_seconds = time.time()

    out = int(now_seconds * Microseconds_Per_Second)
    return out

# ################################################################################################################################

def validate_window_unit(value:'str') -> 'str':
    """ Returns the value unchanged if it is a known window unit, raises RateLimitError otherwise.
    """
    if value in _all_window_units:
        out = value
        return out

    raise RateLimitError(f'Unknown window_unit: {value}')

# ################################################################################################################################
# ################################################################################################################################
