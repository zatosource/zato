# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone

# pytest
import pytest

# Zato
from zato.common.util.time_of_day import datetime_to_minutes, hh_mm_to_minutes, Microseconds_Per_Second, now_us_to_minutes, \
    time_in_range, TimeOfDayError, validate_hh_mm

# ################################################################################################################################
# ################################################################################################################################

def _at(hh_mm:'str') -> 'datetime':
    hours, minutes = hh_mm.split(':')

    hours = int(hours)
    minutes = int(minutes)

    out = datetime(2026, 9, 12, hours, minutes, tzinfo=timezone.utc)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestTimeOfDay:

    def test_hh_mm_round_trip(self) -> 'None':
        assert hh_mm_to_minutes('00:00') == 0
        assert hh_mm_to_minutes('14:30') == 870
        assert hh_mm_to_minutes('23:59') == 1439

# ################################################################################################################################

    def test_range_within_a_day(self) -> 'None':
        from_minutes = hh_mm_to_minutes('09:00')
        to_minutes = hh_mm_to_minutes('17:00')

        at_start = hh_mm_to_minutes('09:00')
        at_noon = hh_mm_to_minutes('12:00')
        at_end = hh_mm_to_minutes('17:00')
        at_night = hh_mm_to_minutes('03:00')

        assert time_in_range(at_start, from_minutes, to_minutes)
        assert time_in_range(at_noon, from_minutes, to_minutes)
        assert not time_in_range(at_end, from_minutes, to_minutes)
        assert not time_in_range(at_night, from_minutes, to_minutes)

# ################################################################################################################################

    def test_range_crossing_midnight(self) -> 'None':
        from_minutes = hh_mm_to_minutes('23:00')
        to_minutes = hh_mm_to_minutes('02:00')

        late_evening = hh_mm_to_minutes('23:30')
        after_midnight = hh_mm_to_minutes('01:00')
        at_noon = hh_mm_to_minutes('12:00')

        assert time_in_range(late_evening, from_minutes, to_minutes)
        assert time_in_range(after_midnight, from_minutes, to_minutes)
        assert not time_in_range(at_noon, from_minutes, to_minutes)

# ################################################################################################################################

    def test_validate_hh_mm(self) -> 'None':
        validate_hh_mm('08:15', 'from')

        for bad in ('8:15', '24:00', '08:60', '08-15', 'ab:cd'):
            with pytest.raises(TimeOfDayError):
                validate_hh_mm(bad, 'from')

# ################################################################################################################################

    def test_datetime_to_minutes(self) -> 'None':
        moment = _at('10:45')
        expected = hh_mm_to_minutes('10:45')

        assert datetime_to_minutes(moment) == expected

# ################################################################################################################################

    def test_now_us_to_minutes(self) -> 'None':
        moment = _at('10:45')
        expected = hh_mm_to_minutes('10:45')

        now_seconds = int(moment.timestamp())
        now_us = now_seconds * Microseconds_Per_Second

        assert now_us_to_minutes(now_us) == expected

# ################################################################################################################################
# ################################################################################################################################
