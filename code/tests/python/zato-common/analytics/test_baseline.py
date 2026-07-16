# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta

# Zato
from zato.common.analytics.baseline import get_anomaly_periods

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

    # Dummy assignments to satisfy type checkers
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# A Tuesday at 14:00 - the anchor of all the weekly series below
_anchor = datetime(2026, 1, 6, 14)

# How periods are written in the analytics store
_period_format = '%Y-%m-%dT%H'

# ################################################################################################################################
# ################################################################################################################################

def _weekly_periods(count:'int') -> 'strlist':
    """ The same hour of the week over consecutive weeks, e.g. every Tuesday 14:00.
    """

    # Our response to produce
    out:'strlist' = []

    for week in range(count):
        when = _anchor + timedelta(weeks=week)
        out.append(when.strftime(_period_format))

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_baseline_spike_is_marked() -> 'None':
    """ A value far outside what this hour of the week usually does gets a marker,
    and an ordinary value does not.
    """
    periods = _weekly_periods(10)

    series = {}

    for period in periods:
        series[period] = 100.0

    spike_period = periods[-1]
    ordinary_period = periods[-2]

    series[spike_period] = 500.0

    anomalies = get_anomaly_periods(series, [ordinary_period, spike_period])

    assert anomalies == {spike_period}

# ################################################################################################################################

def test_baseline_constant_series_never_marks() -> 'None':
    """ A perfectly constant series has no anomalies - the minimum band width
    keeps a zero-deviation baseline from marking every wobble.
    """
    periods = _weekly_periods(10)

    series = {}

    for period in periods:
        series[period] = 100.0

    anomalies = get_anomaly_periods(series, periods)

    assert anomalies == set()

# ################################################################################################################################

def test_baseline_minimum_band_width() -> 'None':
    """ With a zero median absolute deviation the band is one unit wide - a value
    one unit off stays inside it, a value two units off is out.
    """
    periods = _weekly_periods(10)

    series = {}

    for period in periods:
        series[period] = 100.0

    inside_period = periods[-1]
    series[inside_period] = 101.0

    anomalies = get_anomaly_periods(series, [inside_period])
    assert anomalies == set()

    series[inside_period] = 102.0

    anomalies = get_anomaly_periods(series, [inside_period])
    assert anomalies == {inside_period}

# ################################################################################################################################

def test_baseline_short_history_never_marks() -> 'None':
    """ A point whose same-hour-of-week history is too short has no baseline
    and is never marked, and never an error either.
    """
    periods = _weekly_periods(3)

    series = {
        periods[0]: 100.0,
        periods[1]: 100.0,
        periods[2]: 900.0,
    }

    # The last point has two earlier values only, which is below the minimum history
    anomalies = get_anomaly_periods(series, [periods[2]])

    assert anomalies == set()

# ################################################################################################################################

def test_baseline_other_hours_do_not_pollute() -> 'None':
    """ The baseline of Tuesday 14:00 is built out of earlier Tuesdays at 14:00 only -
    huge values at other hours change nothing.
    """
    periods = _weekly_periods(10)

    series = {}

    for period in periods:
        series[period] = 100.0

    # Enormous traffic an hour later, every week
    for week in range(10):
        other_hour = _anchor + timedelta(weeks=week, hours=1)
        series[other_hour.strftime(_period_format)] = 100000.0

    checked_period = periods[-1]

    anomalies = get_anomaly_periods(series, [checked_period])

    assert anomalies == set()

# ################################################################################################################################

def test_baseline_unknown_period_is_skipped() -> 'None':
    """ Asking about a period the series knows nothing about is not an error.
    """
    periods = _weekly_periods(10)

    series = {}

    for period in periods:
        series[period] = 100.0

    anomalies = get_anomaly_periods(series, ['2030-01-01T00'])

    assert anomalies == set()

# ################################################################################################################################
# ################################################################################################################################
