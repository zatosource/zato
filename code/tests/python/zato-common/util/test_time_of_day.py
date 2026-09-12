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
from zato.common.util.time_of_day import datetime_to_minutes, hh_mm_to_minutes, now_us_to_minutes, time_in_range, \
    validate_hh_mm

# ################################################################################################################################
# ################################################################################################################################

def _at(hh_mm:'str') -> 'datetime':
    hours, minutes = hh_mm.split(':')
    out = datetime(2026, 9, 12, int(hours), int(minutes), tzinfo=timezone.utc)
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

        assert time_in_range(hh_mm_to_minutes('09:00'), from_minutes, to_minutes)
        assert time_in_range(hh_mm_to_minutes('12:00'), from_minutes, to_minutes)
        assert not time_in_range(hh_mm_to_minutes('17:00'), from_minutes, to_minutes)
        assert not time_in_range(hh_mm_to_minutes('03:00'), from_minutes, to_minutes)

# ################################################################################################################################

    def test_range_crossing_midnight(self) -> 'None':
        from_minutes = hh_mm_to_minutes('23:00')
        to_minutes = hh_mm_to_minutes('02:00')

        assert time_in_range(hh_mm_to_minutes('23:30'), from_minutes, to_minutes)
        assert time_in_range(hh_mm_to_minutes('01:00'), from_minutes, to_minutes)
        assert not time_in_range(hh_mm_to_minutes('12:00'), from_minutes, to_minutes)

# ################################################################################################################################

    def test_validate_hh_mm(self) -> 'None':
        validate_hh_mm('08:15', 'from')

        for bad in ('8:15', '24:00', '08:60', '08-15', 'ab:cd'):
            with pytest.raises(ValueError):
                validate_hh_mm(bad, 'from')

# ################################################################################################################################

    def test_datetime_to_minutes(self) -> 'None':
        assert datetime_to_minutes(_at('10:45')) == hh_mm_to_minutes('10:45')

# ################################################################################################################################

    def test_now_us_to_minutes(self) -> 'None':
        moment = _at('10:45')
        now_us = int(moment.timestamp()) * 1_000_000
        assert now_us_to_minutes(now_us) == hh_mm_to_minutes('10:45')

# ################################################################################################################################
# ################################################################################################################################
