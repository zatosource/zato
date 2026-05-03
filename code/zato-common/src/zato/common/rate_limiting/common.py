# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from dataclasses import dataclass

if 0:
    from zato.common.typing_ import stranydict

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

client_address_headers = ['HTTP_X_ZATO_FORWARDED_FOR', 'HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR']

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

_time_pattern_length = 5

# ################################################################################################################################

def _validate_hh_mm(value:'str', field_name:'str') -> 'None':
    """ Raises RateLimitError if the value is not a valid HH:MM string.
    """

    # Must be exactly 5 characters: HH:MM ..
    if len(value) != _time_pattern_length:
        raise RateLimitError(f'{field_name} must be in HH:MM format, got: {value}')

    # .. the colon must be in the right place ..
    if value[2] != ':':
        raise RateLimitError(f'{field_name} must be in HH:MM format, got: {value}')

    hours_str = value[:2]
    minutes_str = value[3:]

    # .. hours and minutes must be digits ..
    if not hours_str.isdigit() or not minutes_str.isdigit():
        raise RateLimitError(f'{field_name} must be in HH:MM format, got: {value}')

    hours   = int(hours_str)
    minutes = int(minutes_str)

    # .. hours must be 0-23 ..
    if hours > 23:
        raise RateLimitError(f'{field_name} hours out of range: {value}')

    # .. minutes must be 0-59.
    if minutes > 59:
        raise RateLimitError(f'{field_name} minutes out of range: {value}')

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class TimeRange:
    """ A single time range entry within a rate limiting rule.

    Either is_all_day is True (no time_from/time_to) or is_all_day is False
    with time_from and time_to set to HH:MM strings. Never both.
    """

    is_all_day:  'bool'
    disabled:    'bool'
    disallowed:  'bool'
    time_from:   'str'
    time_to:     'str'
    rate:        'int'
    burst:       'int'
    limit:       'int'
    limit_unit:  'str'

# ################################################################################################################################

    @classmethod
    def from_dict(
        class_:'type[TimeRange]', # pyright: ignore[reportSelfClsParameterName]
        data:'stranydict',
        ) -> 'TimeRange':
        """ Builds a TimeRange from a dict as received from the UI or read from opaque1.
        """

        # Our response to produce
        out = class_()

        # Extract is_all_day first - it drives which other fields are expected ..
        out.is_all_day = data['is_all_day']
        out.disabled   = data['disabled']
        out.disallowed = data['disallowed']

        # .. all-day entries must not have time boundaries ..
        if out.is_all_day:
            if 'time_from' in data or 'time_to' in data:
                raise RateLimitError('All-day time range must not have time_from or time_to in input')
            out.time_from = ''
            out.time_to   = ''

        # .. range entries must have both.
        else:
            out.time_from = data['time_from']
            out.time_to   = data['time_to']

        out.rate       = int(data['rate'])
        out.burst      = int(data['burst'])
        out.limit      = int(data['limit'])
        out.limit_unit = data['limit_unit']

        # .. validate the whole thing before returning.
        validate_time_range(out)

        return out

# ################################################################################################################################

    def to_dict(self) -> 'stranydict':
        """ Serializes this TimeRange to a dict suitable for JSON storage.
        """

        # Our response to produce
        out:'stranydict' = {
            'is_all_day':  self.is_all_day,
            'disabled':    self.disabled,
            'disallowed':  self.disallowed,
            'rate':        self.rate,
            'burst':       self.burst,
            'limit':       self.limit,
            'limit_unit':  self.limit_unit,
        }

        # .. non-all-day entries include time boundaries.
        if not self.is_all_day:
            out['time_from'] = self.time_from
            out['time_to']   = self.time_to

        return out

# ################################################################################################################################
# ################################################################################################################################

def validate_time_range(time_range:'TimeRange') -> 'None':
    """ Validates that a TimeRange is internally consistent. Raises RateLimitError on any problem.
    """

    # All-day entries must not have time_from/time_to ..
    if time_range.is_all_day:
        if time_range.time_from or time_range.time_to:
            raise RateLimitError('All-day time range must not have time_from or time_to')

    # .. non-all-day entries must have both ..
    else:
        if not time_range.time_from:
            raise RateLimitError('Non-all-day time range must have time_from')

        if not time_range.time_to:
            raise RateLimitError('Non-all-day time range must have time_to')

        # .. and they must be valid HH:MM strings.
        _validate_hh_mm(time_range.time_from, 'time_from')
        _validate_hh_mm(time_range.time_to, 'time_to')

    # .. limit_unit must be valid.
    _ = validate_window_unit(time_range.limit_unit)

# ################################################################################################################################

def time_in_range(now_minutes:'int', from_minutes:'int', to_minutes:'int') -> 'bool':
    """ Returns True if now_minutes falls within the [from_minutes, to_minutes) range.

    All arguments are minutes since midnight (0-1439).
    Handles midnight-crossing ranges where from_minutes > to_minutes,
    e.g. 23:00-02:00 means from_minutes=1380, to_minutes=120.
    """

    # Non-crossing range: e.g. 09:00-17:00 ..
    if from_minutes <= to_minutes:
        out = from_minutes <= now_minutes < to_minutes

    # .. midnight-crossing range: e.g. 23:00-02:00.
    else:
        out = now_minutes >= from_minutes or now_minutes < to_minutes

    return out

# ################################################################################################################################

def hh_mm_to_minutes(value:'str') -> 'int':
    """ Converts an HH:MM string to minutes since midnight.
    """
    hours_str   = value[:2]
    minutes_str = value[3:]

    hours   = int(hours_str)
    minutes = int(minutes_str)

    out = hours * Seconds_Per_Minute + minutes
    return out

# ################################################################################################################################
# ################################################################################################################################
