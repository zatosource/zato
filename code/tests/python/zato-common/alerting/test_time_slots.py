# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone
from json import dumps

# pytest
import pytest

# Zato
from zato.common.alerting.time_slots import resolve_silence, SilenceResult, TimeSlotsError, validate_silence_slots

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist
    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

def _at(hh_mm:'str') -> 'datetime':
    hours, minutes = hh_mm.split(':')

    hours = int(hours)
    minutes = int(minutes)

    out = datetime(2026, 9, 12, hours, minutes, tzinfo=timezone.utc)
    return out

# ################################################################################################################################

def _values(slots:'anylist', traffic_expected:'bool'=True, silence_window:'int'=3600) -> 'anydict':
    out = {
        'traffic_expected': traffic_expected,
        'silence_window': silence_window,
        'silence_slots': dumps(slots),
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSilenceSlots:

    def test_first_matching_range_wins(self) -> 'None':

        slots = [
            {'time_from': '08:00', 'time_to': '18:00', 'is_on': True, 'silence_seconds': 900},
            {'time_from': '12:00', 'time_to': '14:00', 'is_on': False, 'silence_seconds': 60},
        ]

        values = _values(slots)
        now = _at('13:00')

        assert resolve_silence(values, now) == SilenceResult(True, 900)

# ################################################################################################################################

    def test_all_day_answers_outside_every_range(self) -> 'None':

        slots = [
            {'time_from': '08:00', 'time_to': '18:00', 'is_on': True, 'silence_seconds': 900},
        ]

        values = _values(slots, traffic_expected=False, silence_window=7200)
        empty_values = _values([])
        now = _at('20:00')

        assert resolve_silence(values, now) == SilenceResult(False, 7200)
        assert resolve_silence(empty_values, now) == SilenceResult(True, 3600)

# ################################################################################################################################

    def test_range_crossing_midnight_switched_off(self) -> 'None':

        slots = [
            {'time_from': '22:00', 'time_to': '06:00', 'is_on': False, 'silence_seconds': 3600},
        ]

        values = _values(slots)

        late_evening = _at('23:30')
        after_midnight = _at('01:00')
        morning = _at('09:00')

        assert resolve_silence(values, late_evening) == SilenceResult(False, 3600)
        assert resolve_silence(values, after_midnight) == SilenceResult(False, 3600)
        assert resolve_silence(values, morning) == SilenceResult(True, 3600)

# ################################################################################################################################

    def test_validation_accepts_a_good_list(self) -> 'None':

        slots = [
            {'time_from': '08:00', 'time_to': '18:00', 'is_on': True, 'silence_seconds': 900},
        ]

        text = dumps(slots)

        assert validate_silence_slots(text) == slots
        assert validate_silence_slots('[]') == []

# ################################################################################################################################

    def test_validation_names_the_slot_at_fault(self) -> 'None':

        good = {'time_from': '08:00', 'time_to': '18:00', 'is_on': True, 'silence_seconds': 900}

        cases = [
            ('not json', 'must be a JSON list'),
            ('{}', 'must be a JSON list'),
            (dumps([good, 'text']), 'Time slot 2 must be an object'),
            (dumps([dict(good, time_to='18:60')]), 'Time slot 1 time_to minutes out of range'),
            (dumps([{'time_from': '08:00', 'is_on': True, 'silence_seconds': 900}]), 'Time slot 1 has no time_to'),
            (dumps([dict(good, is_on='yes')]), 'Time slot 1 is_on must be true or false'),
            (dumps([dict(good, silence_seconds=0)]), 'Time slot 1 silence_seconds must be a number of at least 1'),
            (dumps([dict(good, silence_seconds=True)]), 'Time slot 1 silence_seconds must be a number of at least 1'),
        ]

        for text, message in cases:
            with pytest.raises(TimeSlotsError) as raised:
                _ = validate_silence_slots(text)
            assert message in raised.value.args[0], text

# ################################################################################################################################
# ################################################################################################################################
