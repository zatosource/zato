# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

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

# ################################################################################################################################
# ################################################################################################################################

def dtm_to_datetime(value:'strnone', config:'FHIRMappingConfig') -> 'strnone':
    """ Converts an HL7 DTM value of any precision to a FHIR dateTime string.
    Values without their own timezone offset receive the config's default one.
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

            # An HL7 offset is +HHMM, a FHIR one is +HH:MM.
            offset_digits = raw_offset[1:]
            digit_count = len(offset_digits)

            if digit_count == 4:
                offset_sign = raw_offset[0]
                offset_hours = offset_digits[:2]
                offset_minutes = offset_digits[2:]
                offset = f'{offset_sign}{offset_hours}:{offset_minutes}'
            break

    # .. split off fractional seconds, FHIR keeps them after the seconds part ..
    fraction = ''
    dot_index = value.find('.')

    if dot_index > 0:
        fraction = value[dot_index:]
        value = value[:dot_index]

    length = len(value)

    year   = value[:4]
    month  = value[4:6]
    day    = value[6:8]
    hour   = value[8:10]
    minute = value[10:12]
    second = value[12:14]

    # .. a bare year, year-month or full date has no time part and no offset ..
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
    if not offset:
        offset = config.default_timezone

    date_part = f'{year}-{month}-{day}'

    if length == _DTM_Hour_Length:
        time_part = f'{hour}:00:00'
    elif length == _DTM_Minute_Length:
        time_part = f'{hour}:{minute}:00'
    elif length >= _DTM_Second_Length:
        time_part = f'{hour}:{minute}:{second}{fraction}'

    # .. anything else is not a value we can make sense of.
    else:
        return None

    out = f'{date_part}T{time_part}{offset}'
    return out

# ################################################################################################################################

def dtm_to_date(value:'strnone') -> 'strnone':
    """ Converts an HL7 DTM value to a FHIR date string, dropping any time part.
    """
    if not value:
        return None

    value = value.strip()
    if not value:
        return None

    length = len(value)

    year  = value[:4]
    month = value[4:6]
    day   = value[6:8]

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
# ################################################################################################################################
