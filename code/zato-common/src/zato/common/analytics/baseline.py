# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The anomaly marker - explainable and dependency-free. The baseline for Tuesday 14:00
# is the median of recent Tuesday-14:00 values from the hourly rows, the band is a few
# median absolute deviations, and a point outside the band gets a marker on the trend
# charts. It is a chart annotation, not a paging system - alerting stays with the
# Prometheus metrics endpoint.

# stdlib
from datetime import datetime
from statistics import median

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

    # Dummy assignments to satisfy type checkers
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
period_value_dict = dict[str, float]
period_set = set[str]

# ################################################################################################################################
# ################################################################################################################################

# How many weeks back the baseline of one hour-of-week reaches
Baseline_Weeks = 8

# How many same-hour-of-week values a point needs before it can have a baseline at all -
# with fewer, there are no markers and never an error.
_min_history = 3

# How many median absolute deviations wide the band is
_mad_multiplier = 3.0

# The band is never narrower than this, so constant series do not mark every wobble
_min_band = 1.0

# How many hours one day and one week have
_hours_per_day = 24
Hours_Per_Week = 7 * _hours_per_day

# ################################################################################################################################
# ################################################################################################################################

def _hour_of_week(period:'str') -> 'int':
    """ Returns which hour of the week an hourly period is, e.g. Tuesday 14:00
    and the Tuesday 14:00 one week later share the same hour of the week.
    """
    when = datetime.fromisoformat(period)

    out = when.weekday() * _hours_per_day + when.hour
    return out

# ################################################################################################################################

def get_anomaly_periods(series:'period_value_dict', periods_to_check:'strlist') -> 'period_set':
    """ Returns which of the given periods are anomalies against their own hour-of-week
    baseline. The series maps hourly periods to values and should reach back
    Baseline_Weeks before the earliest period checked - a point whose history
    is too short to have a baseline is never marked.
    """

    # Our response to produce
    out:'period_set' = set()

    # Group the whole series by hour of the week, keeping each group sorted by period,
    # so the history of any point is a slice of its own group.
    groups:'dict[int, list]' = {}

    for period in sorted(series):
        hour_of_week = _hour_of_week(period)

        if group := groups.get(hour_of_week):
            pass
        else:
            group = []
            groups[hour_of_week] = group

        value = series[period]
        group.append((period, value))

    for period in periods_to_check:

        # A period the series knows nothing about has no value to judge
        if period not in series:
            continue

        value = series[period]
        hour_of_week = _hour_of_week(period)
        group = groups[hour_of_week]

        # The baseline is built out of the same hour of the week in earlier weeks only
        history = []

        for earlier_period, earlier_value in group:
            if earlier_period < period:
                history.append(earlier_value)

        history_len = len(history)
        has_enough_history = history_len >= _min_history

        # Too short a history means no baseline and no marker ..
        if not has_enough_history:
            continue

        # .. the baseline is the median of what this hour of the week usually does ..
        baseline = median(history)

        # .. the band is a few median absolute deviations around it ..
        deviations = []

        for history_value in history:
            deviations.append(abs(history_value - baseline))

        mad = median(deviations)
        band = _mad_multiplier * mad

        if band < _min_band:
            band = _min_band

        # .. and a point outside the band is an anomaly.
        deviation = abs(value - baseline)

        if deviation > band:
            out.add(period)

    return out

# ################################################################################################################################
# ################################################################################################################################
