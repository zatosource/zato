# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple

# Zato
from zato.common.api import SCHEDULER

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intnone, stranydict

# ################################################################################################################################
# ################################################################################################################################

_unit = SCHEDULER.Interval_Unit

Seconds_Per_Minute = 60
Seconds_Per_Hour   = 3600
Seconds_Per_Day    = 86400
Seconds_Per_Week   = 604800

# ################################################################################################################################
# ################################################################################################################################

class RunEveryUnit(NamedTuple):
    run_every: int
    run_unit: str

# ################################################################################################################################
# ################################################################################################################################

def interval_from_unit(run_every:'int', run_unit:'str') -> 'stranydict':
    """ Maps a run-every value and its unit to the interval fields of a scheduler job.
    """
    out = {'weeks':0, 'days':0, 'hours':0, 'minutes':0, 'seconds':0}
    out[run_unit] = run_every

    return out

# ################################################################################################################################

def unit_from_interval(
    weeks:'intnone',
    days:'intnone',
    hours:'intnone',
    minutes:'intnone',
    seconds:'intnone',
    ) -> 'RunEveryUnit':
    """ Maps the interval fields of a scheduler job back to a run-every value and its unit.
    The result uses the largest unit that divides the total evenly, e.g. 120 seconds becomes 2 minutes.
    """

    # The columns are nullable in the database and a missing value means the same as zero.
    if weeks is None:
        weeks = 0
    if days is None:
        days = 0
    if hours is None:
        hours = 0
    if minutes is None:
        minutes = 0
    if seconds is None:
        seconds = 0

    # Everything is normalized to seconds first ..
    total_seconds = weeks * Seconds_Per_Week + days * Seconds_Per_Day + hours * Seconds_Per_Hour + \
        minutes * Seconds_Per_Minute + seconds

    # .. and then expressed in the largest unit that divides the total evenly.
    if total_seconds % Seconds_Per_Day == 0:
        out = RunEveryUnit(total_seconds // Seconds_Per_Day, _unit.Days)
    elif total_seconds % Seconds_Per_Hour == 0:
        out = RunEveryUnit(total_seconds // Seconds_Per_Hour, _unit.Hours)
    elif total_seconds % Seconds_Per_Minute == 0:
        out = RunEveryUnit(total_seconds // Seconds_Per_Minute, _unit.Minutes)
    else:
        out = RunEveryUnit(total_seconds, _unit.Seconds)

    return out

# ################################################################################################################################

def interval_text(weeks:'int', days:'int', hours:'int', minutes:'int', seconds:'int') -> 'str':
    """ Returns a human-readable interval only, e.g. "10 seconds" or "3 hours 5 minutes".
    """
    parts = []

    for name, value in (('week', weeks), ('day', days), ('hour', hours), ('minute', minutes), ('second', seconds)):
        if value:
            suffix = '' if value == 1 else 's'
            parts.append(f'{value} {name}{suffix}')

    out = ' '.join(parts)
    return out

# ################################################################################################################################
# ################################################################################################################################
