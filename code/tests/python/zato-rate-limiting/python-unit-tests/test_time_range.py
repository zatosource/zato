# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.rate_limiting.common import hh_mm_to_minutes, RateLimitError, time_in_range, TimeRange, \
    validate_time_range

# ################################################################################################################################
# ################################################################################################################################

class TimeRangeConstructionTestCase(TestCase):

    def test_all_day_range(self) -> 'None':
        """ An all-day TimeRange can be constructed with is_all_day=True and empty time fields.
        """
        time_range = TimeRange()
        time_range.is_all_day  = True
        time_range.disabled    = False
        time_range.disallowed  = False
        time_range.time_from   = ''
        time_range.time_to     = ''
        time_range.rate        = 10
        time_range.burst       = 20
        time_range.limit       = 100
        time_range.limit_unit  = 'minute'

        self.assertTrue(time_range.is_all_day)
        self.assertFalse(time_range.disabled)
        self.assertFalse(time_range.disallowed)
        self.assertEqual(time_range.rate, 10)
        self.assertEqual(time_range.burst, 20)
        self.assertEqual(time_range.limit, 100)
        self.assertEqual(time_range.limit_unit, 'minute')

# ################################################################################################################################

    def test_specific_range(self) -> 'None':
        """ A non-all-day TimeRange can be constructed with time_from and time_to.
        """
        time_range = TimeRange()
        time_range.is_all_day  = False
        time_range.disabled    = False
        time_range.disallowed  = False
        time_range.time_from   = '01:00'
        time_range.time_to     = '02:00'
        time_range.rate        = 5
        time_range.burst       = 10
        time_range.limit       = 50
        time_range.limit_unit  = 'minute'

        self.assertFalse(time_range.is_all_day)
        self.assertEqual(time_range.time_from, '01:00')
        self.assertEqual(time_range.time_to, '02:00')

# ################################################################################################################################

    def test_disabled_range(self) -> 'None':
        """ A disabled TimeRange has disabled=True.
        """
        time_range = TimeRange()
        time_range.is_all_day  = False
        time_range.disabled    = True
        time_range.disallowed  = False
        time_range.time_from   = '05:00'
        time_range.time_to     = '06:00'
        time_range.rate        = 2
        time_range.burst       = 5
        time_range.limit       = 20
        time_range.limit_unit  = 'hour'

        self.assertTrue(time_range.disabled)

# ################################################################################################################################

    def test_disallowed_range(self) -> 'None':
        """ A disallowed TimeRange has disallowed=True.
        """
        time_range = TimeRange()
        time_range.is_all_day  = False
        time_range.disabled    = False
        time_range.disallowed  = True
        time_range.time_from   = '03:00'
        time_range.time_to     = '04:00'
        time_range.rate        = 0
        time_range.burst       = 0
        time_range.limit       = 0
        time_range.limit_unit  = 'minute'

        self.assertTrue(time_range.disallowed)

# ################################################################################################################################
# ################################################################################################################################

class ValidateTimeRangeTestCase(TestCase):

    def _make_all_day(self) -> 'TimeRange':
        """ Helper to build a valid all-day TimeRange.
        """
        time_range = TimeRange()
        time_range.is_all_day  = True
        time_range.disabled    = False
        time_range.disallowed  = False
        time_range.time_from   = ''
        time_range.time_to     = ''
        time_range.rate        = 10
        time_range.burst       = 20
        time_range.limit       = 100
        time_range.limit_unit  = 'minute'

        return time_range

# ################################################################################################################################

    def _make_range(self, time_from:'str'='01:00', time_to:'str'='02:00') -> 'TimeRange':
        """ Helper to build a valid non-all-day TimeRange.
        """
        time_range = TimeRange()
        time_range.is_all_day  = False
        time_range.disabled    = False
        time_range.disallowed  = False
        time_range.time_from   = time_from
        time_range.time_to     = time_to
        time_range.rate        = 5
        time_range.burst       = 10
        time_range.limit       = 50
        time_range.limit_unit  = 'minute'

        return time_range

# ################################################################################################################################

    def test_valid_all_day(self) -> 'None':
        """ A valid all-day range passes validation without error.
        """
        time_range = self._make_all_day()
        validate_time_range(time_range)

# ################################################################################################################################

    def test_valid_range(self) -> 'None':
        """ A valid non-all-day range passes validation without error.
        """
        time_range = self._make_range()
        validate_time_range(time_range)

# ################################################################################################################################

    def test_all_day_with_time_from_raises(self) -> 'None':
        """ An all-day range with time_from set raises RateLimitError.
        """
        time_range = self._make_all_day()
        time_range.time_from = '01:00'

        with self.assertRaises(RateLimitError):
            validate_time_range(time_range)

# ################################################################################################################################

    def test_all_day_with_time_to_raises(self) -> 'None':
        """ An all-day range with time_to set raises RateLimitError.
        """
        time_range = self._make_all_day()
        time_range.time_to = '02:00'

        with self.assertRaises(RateLimitError):
            validate_time_range(time_range)

# ################################################################################################################################

    def test_range_missing_time_from_raises(self) -> 'None':
        """ A non-all-day range without time_from raises RateLimitError.
        """
        time_range = self._make_range()
        time_range.time_from = ''

        with self.assertRaises(RateLimitError):
            validate_time_range(time_range)

# ################################################################################################################################

    def test_range_missing_time_to_raises(self) -> 'None':
        """ A non-all-day range without time_to raises RateLimitError.
        """
        time_range = self._make_range()
        time_range.time_to = ''

        with self.assertRaises(RateLimitError):
            validate_time_range(time_range)

# ################################################################################################################################

    def test_invalid_time_from_format_raises(self) -> 'None':
        """ A time_from that is not HH:MM raises RateLimitError.
        """
        time_range = self._make_range(time_from='2500')

        with self.assertRaises(RateLimitError):
            validate_time_range(time_range)

# ################################################################################################################################

    def test_invalid_time_to_format_raises(self) -> 'None':
        """ A time_to that is not HH:MM raises RateLimitError.
        """
        time_range = self._make_range(time_to='99:99')

        with self.assertRaises(RateLimitError):
            validate_time_range(time_range)

# ################################################################################################################################

    def test_hours_out_of_range_raises(self) -> 'None':
        """ Hours above 23 raise RateLimitError.
        """
        time_range = self._make_range(time_from='24:00')

        with self.assertRaises(RateLimitError):
            validate_time_range(time_range)

# ################################################################################################################################

    def test_minutes_out_of_range_raises(self) -> 'None':
        """ Minutes above 59 raise RateLimitError.
        """
        time_range = self._make_range(time_from='12:60')

        with self.assertRaises(RateLimitError):
            validate_time_range(time_range)

# ################################################################################################################################

    def test_invalid_limit_unit_raises(self) -> 'None':
        """ An unknown limit_unit raises RateLimitError.
        """
        time_range = self._make_all_day()
        time_range.limit_unit = 'invalid_unit'

        with self.assertRaises(RateLimitError):
            validate_time_range(time_range)

# ################################################################################################################################

    def test_all_valid_limit_units(self) -> 'None':
        """ All known limit units pass validation.
        """
        for unit in ('second', 'minute', 'hour', 'day', 'month'):
            time_range = self._make_all_day()
            time_range.limit_unit = unit
            validate_time_range(time_range)

# ################################################################################################################################

    def test_non_digit_time_raises(self) -> 'None':
        """ A time value with non-digit characters raises RateLimitError.
        """
        time_range = self._make_range(time_from='ab:cd')

        with self.assertRaises(RateLimitError):
            validate_time_range(time_range)

# ################################################################################################################################

    def test_midnight_boundary(self) -> 'None':
        """ 00:00 and 23:59 are both valid times.
        """
        time_range = self._make_range(time_from='00:00', time_to='23:59')
        validate_time_range(time_range)

# ################################################################################################################################
# ################################################################################################################################

class HhMmToMinutesTestCase(TestCase):

    def test_midnight(self) -> 'None':
        """ 00:00 converts to 0 minutes.
        """
        self.assertEqual(hh_mm_to_minutes('00:00'), 0)

# ################################################################################################################################

    def test_one_am(self) -> 'None':
        """ 01:00 converts to 60 minutes.
        """
        self.assertEqual(hh_mm_to_minutes('01:00'), 60)

# ################################################################################################################################

    def test_noon(self) -> 'None':
        """ 12:00 converts to 720 minutes.
        """
        self.assertEqual(hh_mm_to_minutes('12:00'), 720)

# ################################################################################################################################

    def test_end_of_day(self) -> 'None':
        """ 23:59 converts to 1439 minutes.
        """
        self.assertEqual(hh_mm_to_minutes('23:59'), 1439)

# ################################################################################################################################

    def test_arbitrary_time(self) -> 'None':
        """ 14:30 converts to 870 minutes.
        """
        self.assertEqual(hh_mm_to_minutes('14:30'), 870)

# ################################################################################################################################
# ################################################################################################################################

class TimeInRangeTestCase(TestCase):

    def test_inside_normal_range(self) -> 'None':
        """ 10:00 is inside 09:00-17:00.
        """
        now      = hh_mm_to_minutes('10:00')
        from_min = hh_mm_to_minutes('09:00')
        to_min   = hh_mm_to_minutes('17:00')

        self.assertTrue(time_in_range(now, from_min, to_min))

# ################################################################################################################################

    def test_outside_normal_range(self) -> 'None':
        """ 08:00 is outside 09:00-17:00.
        """
        now      = hh_mm_to_minutes('08:00')
        from_min = hh_mm_to_minutes('09:00')
        to_min   = hh_mm_to_minutes('17:00')

        self.assertFalse(time_in_range(now, from_min, to_min))

# ################################################################################################################################

    def test_at_start_boundary(self) -> 'None':
        """ 09:00 is inside [09:00, 17:00).
        """
        now      = hh_mm_to_minutes('09:00')
        from_min = hh_mm_to_minutes('09:00')
        to_min   = hh_mm_to_minutes('17:00')

        self.assertTrue(time_in_range(now, from_min, to_min))

# ################################################################################################################################

    def test_at_end_boundary(self) -> 'None':
        """ 17:00 is outside [09:00, 17:00) because the end is exclusive.
        """
        now      = hh_mm_to_minutes('17:00')
        from_min = hh_mm_to_minutes('09:00')
        to_min   = hh_mm_to_minutes('17:00')

        self.assertFalse(time_in_range(now, from_min, to_min))

# ################################################################################################################################

    def test_midnight_crossing_inside_before_midnight(self) -> 'None':
        """ 23:30 is inside 23:00-02:00 (midnight-crossing range).
        """
        now      = hh_mm_to_minutes('23:30')
        from_min = hh_mm_to_minutes('23:00')
        to_min   = hh_mm_to_minutes('02:00')

        self.assertTrue(time_in_range(now, from_min, to_min))

# ################################################################################################################################

    def test_midnight_crossing_inside_after_midnight(self) -> 'None':
        """ 01:00 is inside 23:00-02:00 (midnight-crossing range).
        """
        now      = hh_mm_to_minutes('01:00')
        from_min = hh_mm_to_minutes('23:00')
        to_min   = hh_mm_to_minutes('02:00')

        self.assertTrue(time_in_range(now, from_min, to_min))

# ################################################################################################################################

    def test_midnight_crossing_outside(self) -> 'None':
        """ 12:00 is outside 23:00-02:00 (midnight-crossing range).
        """
        now      = hh_mm_to_minutes('12:00')
        from_min = hh_mm_to_minutes('23:00')
        to_min   = hh_mm_to_minutes('02:00')

        self.assertFalse(time_in_range(now, from_min, to_min))

# ################################################################################################################################

    def test_midnight_crossing_at_start(self) -> 'None':
        """ 23:00 is inside [23:00, 02:00) (at the start boundary).
        """
        now      = hh_mm_to_minutes('23:00')
        from_min = hh_mm_to_minutes('23:00')
        to_min   = hh_mm_to_minutes('02:00')

        self.assertTrue(time_in_range(now, from_min, to_min))

# ################################################################################################################################

    def test_midnight_crossing_at_end(self) -> 'None':
        """ 02:00 is outside [23:00, 02:00) because the end is exclusive.
        """
        now      = hh_mm_to_minutes('02:00')
        from_min = hh_mm_to_minutes('23:00')
        to_min   = hh_mm_to_minutes('02:00')

        self.assertFalse(time_in_range(now, from_min, to_min))

# ################################################################################################################################

    def test_single_minute_range(self) -> 'None':
        """ 01:00 is inside [01:00, 01:01).
        """
        now      = hh_mm_to_minutes('01:00')
        from_min = hh_mm_to_minutes('01:00')
        to_min   = hh_mm_to_minutes('01:01')

        self.assertTrue(time_in_range(now, from_min, to_min))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()
