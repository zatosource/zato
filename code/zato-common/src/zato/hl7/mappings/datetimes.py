# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import date
from typing import NamedTuple

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strnone
    from zato.hl7.mappings.config import FHIRMappingConfig
    FHIRMappingConfig = FHIRMappingConfig

# ################################################################################################################################
# ################################################################################################################################

# How many digits each DTM precision level has
_DTM_Year_Length   = 4
_DTM_Month_Length  = 6
_DTM_Day_Length    = 8
_DTM_Hour_Length   = 10
_DTM_Minute_Length = 12
_DTM_Second_Length = 14

# How many digits a TM value has at minute and at second precision
_TM_Minute_Length = 4
_TM_Second_Length = 6

# The digit counts a DTM may have
_DTM_Lengths = frozenset({
    _DTM_Year_Length,
    _DTM_Month_Length,
    _DTM_Day_Length,
    _DTM_Hour_Length,
    _DTM_Minute_Length,
    _DTM_Second_Length,
})

# The digit counts an HL7 offset may have - +HHMM or +HH
_Offset_Full_Length  = 4
_Offset_Hours_Length = 2

# The minutes an offset gets when it spells out only hours
_Offset_Zero_Minutes = '00'

# The seconds a time gets when it spells out only hours and minutes
_Zero_Seconds = '00'

# The bounds FHIR puts on each part of a date/time
_Min_Month  = 1
_Max_Month  = 12
_Min_Day    = 1
_Max_Day    = 31
_Max_Hour   = 23
_Max_Minute = 59
_Max_Second = 60

# The bounds FHIR puts on a timezone offset
Max_Offset_Hours   = 14
Max_Offset_Minutes = 59

# ################################################################################################################################
# ################################################################################################################################

class _DTMParts(NamedTuple):
    """ A DTM value split into what FHIR needs from it.
    """
    digits:'str'
    fraction:'str'
    offset:'str'

# ################################################################################################################################
# ################################################################################################################################

def _is_valid_offset(offset:'str') -> 'bool':
    """ Says whether a FHIR-shaped offset stays within the bounds FHIR allows.
    """
    hours = offset[1:3]
    hours = int(hours)

    minutes = offset[4:6]
    minutes = int(minutes)

    if hours > Max_Offset_Hours:
        return False

    if minutes > Max_Offset_Minutes:
        return False

    return True

# ################################################################################################################################

def _are_valid_digits(digits:'str') -> 'bool':
    """ Says whether the date and time digits of a DTM spell out a real calendar date and a time within bounds.
    """
    length = len(digits)

    # The digit count must match one of the DTM precision levels ..
    if length not in _DTM_Lengths:
        return False

    # .. a bare year is always fine ..
    if length == _DTM_Year_Length:
        return True

    year = digits[:4]
    year = int(year)

    month = digits[4:6]
    month = int(month)

    if month < _Min_Month:
        return False

    if month > _Max_Month:
        return False

    if length == _DTM_Month_Length:
        return True

    # .. a day has to exist in its month, which the calendar decides ..
    day = digits[6:8]
    day = int(day)

    if day < _Min_Day:
        return False

    if day > _Max_Day:
        return False

    try:
        _ = date(year, month, day)
    except ValueError:
        return False

    if length == _DTM_Day_Length:
        return True

    # .. and each time part stays within its bounds.
    hour = digits[8:10]
    hour = int(hour)

    if hour > _Max_Hour:
        return False

    if length == _DTM_Hour_Length:
        return True

    minute = digits[10:12]
    minute = int(minute)

    if minute > _Max_Minute:
        return False

    if length == _DTM_Minute_Length:
        return True

    second = digits[12:14]
    second = int(second)

    if second > _Max_Second:
        return False

    return True

# ################################################################################################################################

def _split_dtm(value:'strnone') -> '_DTMParts | None':
    """ Splits a DTM into its digits, fractional seconds and FHIR-shaped offset,
    returning None for anything that is not a well-formed DTM or is out of bounds.
    """
    if not value:
        return None

    value = value.strip()
    if not value:
        return None

    # Split off the timezone offset if the value carries one ..
    offset = ''

    for sign in ('+', '-'):
        sign_index = value.find(sign)
        if sign_index > 0:
            raw_offset = value[sign_index:]
            value = value[:sign_index]

            offset_sign = raw_offset[0]
            offset_digits = raw_offset[1:]
            digit_count = len(offset_digits)

            # .. an offset must be all digits ..
            if not offset_digits.isdigit():
                return None

            # .. and spell out either hours and minutes or hours alone ..
            if digit_count == _Offset_Full_Length:
                offset_hours = offset_digits[:2]
                offset_minutes = offset_digits[2:]
            elif digit_count == _Offset_Hours_Length:
                offset_hours = offset_digits
                offset_minutes = _Offset_Zero_Minutes

            # .. anything else is not an offset we can make sense of ..
            else:
                return None

            offset = f'{offset_sign}{offset_hours}:{offset_minutes}'

            # .. and stays within what FHIR allows ..
            if not _is_valid_offset(offset):
                return None

            break

    # .. split off fractional seconds, FHIR keeps them after the seconds part ..
    fraction = ''
    dot_index = value.find('.')

    if dot_index > 0:
        fraction = value[dot_index:]
        value = value[:dot_index]

        fraction_digits = fraction[1:]

        if not fraction_digits.isdigit():
            return None

    # .. what remains must be digits only ..
    if not value.isdigit():
        return None

    # .. spelling out a date and time that exist.
    if not _are_valid_digits(value):
        return None

    out = _DTMParts(value, fraction, offset)
    return out

# ################################################################################################################################

def dtm_to_datetime(value:'strnone', config:'FHIRMappingConfig') -> 'strnone':
    """ Converts an HL7 DTM value of any precision to a FHIR dateTime string.
    Values with a time part but no timezone offset of their own receive the config's default one.
    """
    parts = _split_dtm(value)
    if not parts:
        return None

    digits = parts.digits
    length = len(digits)

    year   = digits[:4]
    month  = digits[4:6]
    day    = digits[6:8]
    hour   = digits[8:10]
    minute = digits[10:12]
    second = digits[12:14]

    # A bare year, year-month or full date has no time part and no offset ..
    if length == _DTM_Year_Length:

        out = year
        return out

    if length == _DTM_Month_Length:

        out = f'{year}-{month}'
        return out

    if length == _DTM_Day_Length:

        out = f'{year}-{month}-{day}'
        return out

    # .. anything longer carries a time and needs an offset, defaulting to the configured one ..
    offset = parts.offset

    if not offset:
        offset = config.default_timezone

    date_part = f'{year}-{month}-{day}'

    if length == _DTM_Hour_Length:
        time_part = f'{hour}:00:00'
    elif length == _DTM_Minute_Length:
        time_part = f'{hour}:{minute}:00'
    elif length == _DTM_Second_Length:
        time_part = f'{hour}:{minute}:{second}{parts.fraction}'

    # .. anything else is not a value we can make sense of.
    else:
        return None

    out = f'{date_part}T{time_part}{offset}'
    return out

# ################################################################################################################################

def dtm_to_instant(value:'strnone', config:'FHIRMappingConfig') -> 'strnone':
    """ Converts an HL7 DTM value to a FHIR instant string - a full date, time and offset.
    A value without a time part is not an instant and yields None.
    """
    out = dtm_to_datetime(value, config)
    if not out:
        return None

    # A dateTime without a time part cannot serve as an instant.
    if 'T' not in out:
        return None

    return out

# ################################################################################################################################

def dtm_to_date(value:'strnone') -> 'strnone':
    """ Converts an HL7 DTM value to a FHIR date string, dropping any time part.
    """
    parts = _split_dtm(value)
    if not parts:
        return None

    digits = parts.digits
    length = len(digits)

    year  = digits[:4]
    month = digits[4:6]
    day   = digits[6:8]

    if length >= _DTM_Day_Length:

        out = f'{year}-{month}-{day}'
        return out

    if length == _DTM_Month_Length:

        out = f'{year}-{month}'
        return out

    if length == _DTM_Year_Length:

        out = year
        return out

    return None

# ################################################################################################################################

def tm_to_time(value:'strnone') -> 'strnone':
    """ Converts an HL7 TM value - HHMM or HHMMSS, with any fraction or offset ignored - to a FHIR time string.
    A value shorter than hours and minutes is not a time FHIR can carry and yields None.
    """
    if not value:
        return None

    # Only the leading digits count - a fraction or an offset can follow them.
    digits = value[:_TM_Second_Length]

    if not digits.isdigit():
        return None

    length = len(digits)

    if length < _TM_Minute_Length:
        return None

    # Anything between minute and second precision is not a TM.
    if length != _TM_Minute_Length:
        if length != _TM_Second_Length:
            return None

    hour = digits[:2]
    minute = digits[2:4]
    second = digits[4:6]

    hour_number = int(hour)

    if hour_number > _Max_Hour:
        return None

    minute_number = int(minute)

    if minute_number > _Max_Minute:
        return None

    if length == _TM_Minute_Length:
        second = _Zero_Seconds

    else:
        second_number = int(second)

        if second_number > _Max_Second:
            return None

    out = f'{hour}:{minute}:{second}'
    return out

# ################################################################################################################################
# ################################################################################################################################
