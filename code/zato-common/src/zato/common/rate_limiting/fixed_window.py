# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import datetime

# Zato
from zato.common.rate_limiting.common import December, January, Microseconds_Per_Second, RateLimitError, \
    Seconds_Per_Minute, Seconds_Per_Hour, Seconds_Per_Day, Window_Unit_Second, Window_Unit_Minute, \
    Window_Unit_Hour, Window_Unit_Day, Window_Unit_Month

# ################################################################################################################################
# ################################################################################################################################

_period_by_unit = {
    Window_Unit_Second: 1,
    Window_Unit_Minute: Seconds_Per_Minute,
    Window_Unit_Hour:   Seconds_Per_Hour,
    Window_Unit_Day:    Seconds_Per_Day,
}

# ################################################################################################################################
# ################################################################################################################################

def compute_window_end_us(unit:'str', now_us:'int') -> 'int':
    """ Returns the microsecond timestamp at which the current natural window ends.
    """

    #  Look up whether this is a fixed-period unit (second, minute, hour, day) ..
    period = _period_by_unit.get(unit)

    # .. if so, align to the period boundary using simple integer math ..
    if period is not None:
        now_secs        = now_us // Microseconds_Per_Second
        window_start    = now_secs - now_secs % period
        window_end_secs = window_start + period

        out = window_end_secs * Microseconds_Per_Second
        return out

    # .. months require calendar math because they vary in length ..
    elif unit == Window_Unit_Month:
        now_secs = now_us // Microseconds_Per_Second
        now = datetime.datetime.fromtimestamp(now_secs, tz=datetime.timezone.utc)

        year  = now.year
        month = now.month

        # .. roll over to January of the next year if we are in December ..
        if month == December:
            next_year  = year + 1
            next_month = January

        # .. otherwise just advance to the next month ..
        else:
            next_year  = year
            next_month = month + 1

        # .. and the boundary is midnight UTC on the 1st of that next month.
        first_of_next = datetime.datetime(next_year, next_month, 1, tzinfo=datetime.timezone.utc)
        boundary_secs = int(first_of_next.timestamp())

        out = boundary_secs * Microseconds_Per_Second
        return out

    # .. anything else is not a recognized unit.
    else:
        raise RateLimitError(f'Unknown window_unit: {unit}')

# ################################################################################################################################
# ################################################################################################################################
