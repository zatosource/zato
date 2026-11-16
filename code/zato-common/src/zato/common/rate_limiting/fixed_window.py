# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import datetime
from dataclasses import dataclass

# Zato
from zato.common.rate_limiting.common import December, January, Microseconds_Per_Second, RateLimitError, \
    Seconds_Per_Day, Seconds_Per_Hour, Seconds_Per_Minute, validate_window_unit, Window_Unit_Day, \
    Window_Unit_Hour, Window_Unit_Minute, Window_Unit_Month, Window_Unit_Second

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

@dataclass(init=False)
class FixedWindowConfig:
    """ Configuration for a fixed-window counter.
    """
    limit:              'int'
    parsed_window_unit: 'str'

    @classmethod
    def from_parts(class_, limit:'int', window_unit:'str') -> 'FixedWindowConfig': # pyright: ignore[reportSelfClsParameterName]
        """ Creates a config from a limit and a window unit string.
        """
        out = class_()
        out.limit              = limit
        out.parsed_window_unit = validate_window_unit(window_unit)

        return out

# ################################################################################################################################

    def unit(self) -> 'str':
        """ Returns the parsed window unit string.
        """
        return self.parsed_window_unit

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class FixedWindowCheckResult:
    """ Result of a fixed-window counter check.
    """
    is_allowed:     'bool'
    remaining:      'int'
    retry_after_us: 'int'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class _WindowState:
    """ Internal per-key state for a fixed-window counter.
    """
    count:         'int'
    window_end_us: 'int'

# ################################################################################################################################
# ################################################################################################################################

def _check_state(
    state:'_WindowState',
    config:'FixedWindowConfig',
    now_us:'int',
    ) -> 'FixedWindowCheckResult':
    """ Increments the counter if the window is still open and the limit has not been reached,
    or resets the window if it has expired, then returns an allowed-or-denied result.
    """

    # Our response to produce
    out = FixedWindowCheckResult()

    #  If the current window has expired, start a fresh one ..
    if now_us >= state.window_end_us:
        state.count         = 0
        state.window_end_us = compute_window_end_us(config.unit(), now_us)

    # .. check whether there is room left in this window ..
    if state.count < config.limit:
        state.count += 1

        out.is_allowed     = True
        out.remaining      = config.limit - state.count
        out.retry_after_us = 0

    # .. otherwise the limit is already reached, so deny and report how long until the window resets.
    else:
        retry_after = state.window_end_us - now_us

        out.is_allowed     = False
        out.remaining      = 0
        out.retry_after_us = max(0, retry_after)

    return out

# ################################################################################################################################
# ################################################################################################################################

class FixedWindowRegistry:
    """ Top-level registry holding fixed-window counters for all keys.
    """

    def __init__(self) -> 'None':
        self._windows:'dict[str, _WindowState]' = {}

# ################################################################################################################################

    def __len__(self) -> 'int':
        return len(self._windows)

# ################################################################################################################################

    def check_inner(self, key:'str', config:'FixedWindowConfig', now_us:'int') -> 'FixedWindowCheckResult':
        """ Core check logic, separated from any framework wrapper for testability.
        """

        #  Look up or create the per-key window state ..
        state = self._windows.get(key)

        if state is None:
            state = _WindowState()
            state.count         = 0
            state.window_end_us = compute_window_end_us(config.unit(), now_us)
            self._windows[key] = state

        # .. and decide whether the request is allowed.
        out = _check_state(state, config, now_us)

        return out

# ################################################################################################################################

    def remove(self, key:'str') -> 'None':
        """ Removes the window state for the given key, if any.
        """
        _ = self._windows.pop(key, None)

# ################################################################################################################################

    def is_empty(self) -> 'bool':
        """ Returns True if no windows are registered.
        """
        return not self._windows

# ################################################################################################################################

    def remove_by_prefix(self, prefix:'str') -> 'None':
        """ Removes all window states whose key starts with the given prefix.
        """
        keys_to_remove = [key for key in self._windows if key.startswith(prefix)]
        for key in keys_to_remove:
            del self._windows[key]

# ################################################################################################################################

    def clear(self) -> 'None':
        """ Removes all window states.
        """
        self._windows.clear()

# ################################################################################################################################
# ################################################################################################################################
