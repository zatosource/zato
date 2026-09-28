# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone
from time import time, time_ns
import logging

# Arrow
import arrow

# tzlocal
from tzlocal import get_localzone

# Python 2/3 compatibility
from zato.common.py23_.past.builtins import unicode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Date_Format = 'YYYY-MM-DD'
    Date_Time_Format = 'YYYY-MM-DDTHH:mm:ss'
    Timestamp_Format = 'YYYY-MM-DDTHH:mm:ss.SSSSSS'

# ################################################################################################################################
# ################################################################################################################################

_epoch = datetime.fromtimestamp(0, timezone.utc) # Start of UNIX epoch
local_tz = get_localzone()
local_tz_zone = str(local_tz)

# ################################################################################################################################

def utc_now():
    """ Returns current time in UTC with the timezone information included.
    """
    return datetime.now(timezone.utc)

utcnow = utc_now

# ################################################################################################################################

def native_to_utc(dt):
    """ Converts a native datetime object to a UTC one.
    """
    return dt.replace(tzinfo=timezone.utc)

# ################################################################################################################################

def datetime_to_ms(dt):
    """ Converts a datetime object to a number of milliseconds since UNIX epoch.
    """
    return (dt - _epoch).total_seconds() * 1000

# ################################################################################################################################

def datetime_to_sec(dt):
    """ Converts a datetime object to a number of seconds since UNIX epoch.
    """
    return (dt - _epoch).total_seconds()

# ################################################################################################################################

def utcnow_as_ms(_time=time):
    """ Returns current UTC time in milliseconds since epoch. As of now, uses time.time but may eventually choose
    to use alternative implementations on different systems.
    """
    return _time()

# ################################################################################################################################

def utcnow_from_ns():
    return time_ns() // 1_000_000

# ################################################################################################################################

def datetime_from_ms(ms:'float', isoformat:'bool'=True) -> 'str | datetime':
    """ Converts a number of milliseconds since UNIX epoch to a datetime object.
    """
    value = _epoch + timedelta(milliseconds=ms)
    if isoformat:
        return value.isoformat()
    else:
        return value

# ################################################################################################################################

class TimeUtil:
    """ A thin layer around Arrow's date/time handling library customized for our needs.
    Default format is always taken from ISO 8601 (so it's sorted lexicographically)
    and default timezone is always UTC.

    Each method's 'format' is the format string of the text to return, or False to return the Arrow object itself.
    """

# ################################################################################################################################

    def now(self, format:'str | bool'=ModuleCtx.Date_Time_Format, tz=local_tz_zone, delta=None) -> 'str | datetime':
        """ Returns now in a specified timezone.
        """
        now = arrow.now(tz=tz)

        if delta:
            now = now + delta

        if isinstance(format, str):
            return now.format(format)

        return now # type: ignore

# ################################################################################################################################

    def _time_from(self, value:'any_', delta:'dict', format:'str | bool'):

        value = arrow.get(value)
        value_from = value + timedelta(**delta)

        if isinstance(format, str):
            return value_from.format(format)
        else:
            return value_from

# ################################################################################################################################

    def one_day_from(self, date, format:'str | bool'=ModuleCtx.Date_Format):
        delta = {'days': 1}
        return self._time_from(date, delta, format)

# ################################################################################################################################

    def one_hour_from(self, date, format:'str | bool'=ModuleCtx.Date_Format):
        delta = {'minutes': 60}
        return self._time_from(date, delta, format)

# ################################################################################################################################

    def one_minute_from(self, date, format:'str | bool'=ModuleCtx.Date_Format):
        delta = {'minutes': 1}
        return self._time_from(date, delta, format)

# ################################################################################################################################

    def yesterday(self, format:'str | bool'=ModuleCtx.Date_Time_Format, tz=local_tz_zone):
        return self.now(format, tz, delta=timedelta(days=-1))

# ################################################################################################################################

    def tomorrow(self, format:'str | bool'=ModuleCtx.Date_Time_Format, tz=local_tz_zone):
        return self.now(format, tz, delta=timedelta(days=1))

# ################################################################################################################################

    def utcnow(self, format:'str | bool'=ModuleCtx.Date_Time_Format) -> 'any_':
        """ Returns now in UTC formatted as given in 'format'.
        """
        return self.now(format, 'UTC')

# ################################################################################################################################

    def utcnow_as_float(self) -> 'any_':
        """ Returns now in UTC as a float number.
        """
        return self.utcnow(format=False).float_timestamp

# ################################################################################################################################

    def today(self, format:'str | bool'=ModuleCtx.Date_Format, tz=local_tz_zone):
        """ Returns current day in a given timezone.
        """
        now = arrow.now(tz=tz)
        today = arrow.Arrow(year=now.year, month=now.month, day=now.day)

        if tz != 'UTC':
            today = today.to(tz)

        if isinstance(format, str):
            return today.format(format)
        else:
            return today

# ################################################################################################################################

    def isonow(self, tz=local_tz_zone, format:'str | bool'=ModuleCtx.Timestamp_Format):
        return self.now(format, tz)

# ################################################################################################################################

    def isoutcnow(self, format:'str | bool'=ModuleCtx.Timestamp_Format):
        return self.now(format, 'UTC')

# ################################################################################################################################

    def reformat(self, value, from_, to):
        """ Reformats value from one datetime format to another, for instance
        from 23-03-2013 to 03/23/13 (MM-DD-YYYY to DD/MM/YY).
        """
        try:
            # Arrow compares to str, not basestring
            value = str(value) if isinstance(value, unicode) else value
            from_ = str(from_) if isinstance(from_, unicode) else from_
            return arrow.get(value, from_).format(to)
        except Exception:
            logger.error('Could not reformat value:`%s` from:`%s` to:`%s`',
                value, from_, to)
            raise

# ################################################################################################################################
