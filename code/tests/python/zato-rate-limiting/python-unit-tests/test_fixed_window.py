# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import datetime
from unittest import main, TestCase

# Zato
from zato.common.rate_limiting.common import Microseconds_Per_Second, Window_Unit_Second, Window_Unit_Minute, \
    Window_Unit_Hour, Window_Unit_Day, Window_Unit_Month
from zato.common.rate_limiting.fixed_window import compute_window_end_us, FixedWindowConfig, \
    FixedWindowCheckResult, FixedWindowRegistry

# ################################################################################################################################
# ################################################################################################################################

_utc = datetime.timezone.utc

def _to_us(year:'int', month:'int', day:'int', hour:'int'=0, minute:'int'=0, second:'int'=0) -> 'int':
    """ Converts a UTC date/time to microseconds since epoch.
    """
    now = datetime.datetime(year, month, day, hour, minute, second, tzinfo=_utc)
    out = int(now.timestamp()) * Microseconds_Per_Second
    return out

# ################################################################################################################################
# ################################################################################################################################

class ComputeWindowEndSecondTestCase(TestCase):

    def setUp(self) -> 'None':
        self.base_us = _to_us(2023, 11, 14, 22, 13, 20)
        self.mid_us  = self.base_us + 500_000
        self.last_us = self.base_us + 999_999
        self.next_us = self.base_us + Microseconds_Per_Second

    def test_second_boundary_mid_second(self) -> 'None':
        """ Mid-second timestamp rounds up to the next second boundary.
        """
        result = compute_window_end_us(Window_Unit_Second, self.mid_us)
        self.assertEqual(result, self.next_us)

# ################################################################################################################################

    def test_second_boundary_exact_second(self) -> 'None':
        """ Exact second boundary produces the next second.
        """
        result = compute_window_end_us(Window_Unit_Second, self.base_us)
        self.assertEqual(result, self.next_us)

# ################################################################################################################################

    def test_second_boundary_last_microsecond(self) -> 'None':
        """ Last microsecond of a second still falls in the same window.
        """
        result = compute_window_end_us(Window_Unit_Second, self.last_us)
        self.assertEqual(result, self.next_us)

# ################################################################################################################################
# ################################################################################################################################

class ComputeWindowEndMinuteTestCase(TestCase):

    def setUp(self) -> 'None':
        self.start_us = _to_us(2023, 11, 14, 22, 13, 0)
        self.mid_us   = _to_us(2023, 11, 14, 22, 13, 25)
        self.last_us  = _to_us(2023, 11, 14, 22, 13, 59) + 999_000
        self.next_us  = _to_us(2023, 11, 14, 22, 14, 0)

    def test_minute_boundary_mid_minute(self) -> 'None':
        """ Mid-minute timestamp rounds up to the next minute boundary.
        """
        result = compute_window_end_us(Window_Unit_Minute, self.mid_us)
        self.assertEqual(result, self.next_us)

# ################################################################################################################################

    def test_minute_boundary_start_of_minute(self) -> 'None':
        """ Start of a minute produces the next minute boundary.
        """
        result = compute_window_end_us(Window_Unit_Minute, self.start_us)
        self.assertEqual(result, self.next_us)

# ################################################################################################################################

    def test_minute_boundary_last_second(self) -> 'None':
        """ Last second of a minute still falls in the same window.
        """
        result = compute_window_end_us(Window_Unit_Minute, self.last_us)
        self.assertEqual(result, self.next_us)

# ################################################################################################################################
# ################################################################################################################################

class ComputeWindowEndHourTestCase(TestCase):

    def setUp(self) -> 'None':
        self.start_us = _to_us(2023, 11, 14, 22, 0, 0)
        self.mid_us   = _to_us(2023, 11, 14, 22, 13, 20)
        self.last_us  = _to_us(2023, 11, 14, 22, 59, 59) + 999_000
        self.next_us  = _to_us(2023, 11, 14, 23, 0, 0)

    def test_hour_boundary_mid_hour(self) -> 'None':
        """ Mid-hour timestamp rounds up to the next hour boundary.
        """
        result = compute_window_end_us(Window_Unit_Hour, self.mid_us)
        self.assertEqual(result, self.next_us)

# ################################################################################################################################

    def test_hour_boundary_start_of_hour(self) -> 'None':
        """ Start of an hour produces the next hour boundary.
        """
        result = compute_window_end_us(Window_Unit_Hour, self.start_us)
        self.assertEqual(result, self.next_us)

# ################################################################################################################################

    def test_hour_boundary_last_second(self) -> 'None':
        """ Last second of an hour still falls in the same window.
        """
        result = compute_window_end_us(Window_Unit_Hour, self.last_us)
        self.assertEqual(result, self.next_us)

# ################################################################################################################################
# ################################################################################################################################

class ComputeWindowEndDayTestCase(TestCase):

    def setUp(self) -> 'None':
        self.start_us = _to_us(2023, 11, 14)
        self.mid_us   = _to_us(2023, 11, 14, 22, 13, 20)
        self.last_us  = _to_us(2023, 11, 14, 23, 59, 59) + 999_000
        self.next_us  = _to_us(2023, 11, 15)

    def test_day_boundary_mid_day(self) -> 'None':
        """ Mid-day timestamp rounds up to the next day boundary.
        """
        result = compute_window_end_us(Window_Unit_Day, self.mid_us)
        self.assertEqual(result, self.next_us)

# ################################################################################################################################

    def test_day_boundary_start_of_day(self) -> 'None':
        """ Start of a day produces the next day boundary.
        """
        result = compute_window_end_us(Window_Unit_Day, self.start_us)
        self.assertEqual(result, self.next_us)

# ################################################################################################################################

    def test_day_boundary_last_second(self) -> 'None':
        """ Last second of a day still falls in the same window.
        """
        result = compute_window_end_us(Window_Unit_Day, self.last_us)
        self.assertEqual(result, self.next_us)

# ################################################################################################################################
# ################################################################################################################################

class ComputeWindowEndMonthTestCase(TestCase):

    def test_month_boundary_february(self) -> 'None':
        """ Feb 15 2023 00:00:00 UTC -> next = Mar 1 2023.
        """
        now_us = _to_us(2023, 2, 15)
        expected = _to_us(2023, 3, 1)
        result = compute_window_end_us(Window_Unit_Month, now_us)
        self.assertEqual(result, expected)

# ################################################################################################################################

    def test_month_boundary_february_leap(self) -> 'None':
        """ Feb 15 2024 00:00:00 UTC (leap year) -> next = Mar 1 2024.
        """
        now_us = _to_us(2024, 2, 15)
        expected = _to_us(2024, 3, 1)
        result = compute_window_end_us(Window_Unit_Month, now_us)
        self.assertEqual(result, expected)

# ################################################################################################################################

    def test_month_boundary_december(self) -> 'None':
        """ Dec 15 2023 00:00:00 UTC -> next = Jan 1 2024.
        """
        now_us = _to_us(2023, 12, 15)
        expected = _to_us(2024, 1, 1)
        result = compute_window_end_us(Window_Unit_Month, now_us)
        self.assertEqual(result, expected)

# ################################################################################################################################

    def test_month_boundary_january(self) -> 'None':
        """ Jan 20 2024 00:00:00 UTC -> next = Feb 1 2024.
        """
        now_us = _to_us(2024, 1, 20)
        expected = _to_us(2024, 2, 1)
        result = compute_window_end_us(Window_Unit_Month, now_us)
        self.assertEqual(result, expected)

# ################################################################################################################################

    def test_month_boundary_last_day(self) -> 'None':
        """ Mar 31 2024 23:59:59 UTC -> next = Apr 1 2024.
        """
        now_us = _to_us(2024, 3, 31, 23, 59, 59)
        expected = _to_us(2024, 4, 1)
        result = compute_window_end_us(Window_Unit_Month, now_us)
        self.assertEqual(result, expected)

# ################################################################################################################################
# ################################################################################################################################

class FixedWindowConfigTestCase(TestCase):

    def test_fixed_window_config_from_parts(self) -> 'None':
        """ from_parts stores limit and unit correctly.
        """
        config = FixedWindowConfig.from_parts(100, Window_Unit_Minute)
        self.assertEqual(config.limit, 100)
        self.assertEqual(config.unit(), Window_Unit_Minute)

# ################################################################################################################################

    def test_fixed_window_config_from_parts_all_units(self) -> 'None':
        """ from_parts accepts all known window units.
        """
        all_units = [
            (Window_Unit_Second, 'second'),
            (Window_Unit_Minute, 'minute'),
            (Window_Unit_Hour,   'hour'),
            (Window_Unit_Day,    'day'),
            (Window_Unit_Month,  'month'),
        ]
        for unit, label in all_units:
            config = FixedWindowConfig.from_parts(50, unit)
            self.assertEqual(config.unit(), unit)
            self.assertEqual(config.unit(), label)

# ################################################################################################################################
# ################################################################################################################################

class FixedWindowCheckResultTestCase(TestCase):

    def test_fixed_window_check_result_allowed(self) -> 'None':
        """ An allowed result reports is_allowed True and retry_after_us 0.
        """
        result = FixedWindowCheckResult()
        result.is_allowed     = True
        result.remaining      = 99
        result.retry_after_us = 0

        self.assertTrue(result.is_allowed)
        self.assertEqual(result.remaining, 99)
        self.assertEqual(result.retry_after_us, 0)

# ################################################################################################################################

    def test_fixed_window_check_result_denied(self) -> 'None':
        """ A denied result reports is_allowed False and retry_after_us > 0.
        """
        result = FixedWindowCheckResult()
        result.is_allowed     = False
        result.remaining      = 0
        result.retry_after_us = 5000

        self.assertFalse(result.is_allowed)
        self.assertEqual(result.remaining, 0)
        self.assertEqual(result.retry_after_us, 5000)

# ################################################################################################################################
# ################################################################################################################################

class FixedWindowSecondTestCase(TestCase):

    def setUp(self) -> 'None':
        self.base_us = _to_us(2023, 11, 14, 22, 13, 20)
        self.mid_us  = self.base_us + 500_000
        self.next_us = self.base_us + Microseconds_Per_Second

    def test_fixed_window_second_allow_up_to_limit_then_deny(self) -> 'None':
        """ Exactly limit requests pass within the same second, then the next is denied.
        """
        registry = FixedWindowRegistry()
        config   = FixedWindowConfig.from_parts(3, Window_Unit_Second)

        for idx in range(3):
            result = registry.check_inner('test_key', config, self.mid_us)
            self.assertTrue(result.is_allowed, f'Request {idx} of 3 must be allowed')

        denied = registry.check_inner('test_key', config, self.mid_us)
        self.assertFalse(denied.is_allowed)

# ################################################################################################################################

    def test_fixed_window_second_zero_limit_always_denies(self) -> 'None':
        """ A limit of zero denies the very first request.
        """
        registry = FixedWindowRegistry()
        config   = FixedWindowConfig.from_parts(0, Window_Unit_Second)

        result = registry.check_inner('test_key', config, self.mid_us)
        self.assertFalse(result.is_allowed)
        self.assertEqual(result.remaining, 0)

# ################################################################################################################################

    def test_fixed_window_second_remaining_decrements(self) -> 'None':
        """ Each allowed request decrements the remaining count.
        """
        registry = FixedWindowRegistry()
        config   = FixedWindowConfig.from_parts(3, Window_Unit_Second)

        result = registry.check_inner('test_key', config, self.mid_us)
        self.assertEqual(result.remaining, 2)

        result = registry.check_inner('test_key', config, self.mid_us)
        self.assertEqual(result.remaining, 1)

        result = registry.check_inner('test_key', config, self.mid_us)
        self.assertEqual(result.remaining, 0)

# ################################################################################################################################

    def test_fixed_window_second_window_reset(self) -> 'None':
        """ After the window expires, a new request is allowed again.
        """
        registry = FixedWindowRegistry()
        config   = FixedWindowConfig.from_parts(1, Window_Unit_Second)

        # .. exhaust the limit in the current second ..
        result = registry.check_inner('test_key', config, self.mid_us)
        self.assertTrue(result.is_allowed)

        denied = registry.check_inner('test_key', config, self.mid_us)
        self.assertFalse(denied.is_allowed)

        # .. move to the next second, the window resets ..
        fresh = registry.check_inner('test_key', config, self.next_us)
        self.assertTrue(fresh.is_allowed)

# ################################################################################################################################

    def test_fixed_window_second_retry_after_is_correct(self) -> 'None':
        """ retry_after_us equals the distance from now to the window boundary.
        """
        registry = FixedWindowRegistry()
        config   = FixedWindowConfig.from_parts(1, Window_Unit_Second)

        _ = registry.check_inner('test_key', config, self.mid_us)
        denied = registry.check_inner('test_key', config, self.mid_us)

        expected_retry = self.next_us - self.mid_us
        self.assertEqual(denied.retry_after_us, expected_retry)

# ################################################################################################################################
# ################################################################################################################################

class FixedWindowMinuteTestCase(TestCase):

    def setUp(self) -> 'None':
        self.mid_us  = _to_us(2023, 11, 14, 22, 13, 25)
        self.next_us = _to_us(2023, 11, 14, 22, 14, 0)

    def test_fixed_window_minute_window_reset_allows_again(self) -> 'None':
        """ After the minute boundary, the counter resets and requests are allowed again.
        """
        registry = FixedWindowRegistry()
        config   = FixedWindowConfig.from_parts(1, Window_Unit_Minute)

        result = registry.check_inner('test_key', config, self.mid_us)
        self.assertTrue(result.is_allowed)

        denied = registry.check_inner('test_key', config, self.mid_us)
        self.assertFalse(denied.is_allowed)

        fresh = registry.check_inner('test_key', config, self.next_us)
        self.assertTrue(fresh.is_allowed)

# ################################################################################################################################

    def test_fixed_window_minute_retry_after_is_correct(self) -> 'None':
        """ retry_after_us equals the distance from now to the next minute boundary.
        """
        registry = FixedWindowRegistry()
        config   = FixedWindowConfig.from_parts(1, Window_Unit_Minute)

        _ = registry.check_inner('test_key', config, self.mid_us)
        denied = registry.check_inner('test_key', config, self.mid_us)

        expected_retry = self.next_us - self.mid_us
        self.assertEqual(denied.retry_after_us, expected_retry)

# ################################################################################################################################
# ################################################################################################################################

class FixedWindowHourTestCase(TestCase):

    def setUp(self) -> 'None':
        self.mid_us  = _to_us(2023, 11, 14, 22, 13, 20)
        self.next_us = _to_us(2023, 11, 14, 23, 0, 0)

    def test_fixed_window_hour_window_reset_allows_again(self) -> 'None':
        """ After the hour boundary, the counter resets and requests are allowed again.
        """
        registry = FixedWindowRegistry()
        config   = FixedWindowConfig.from_parts(1, Window_Unit_Hour)

        result = registry.check_inner('test_key', config, self.mid_us)
        self.assertTrue(result.is_allowed)

        denied = registry.check_inner('test_key', config, self.mid_us)
        self.assertFalse(denied.is_allowed)

        fresh = registry.check_inner('test_key', config, self.next_us)
        self.assertTrue(fresh.is_allowed)

# ################################################################################################################################

    def test_fixed_window_hour_retry_after_is_correct(self) -> 'None':
        """ retry_after_us equals the distance from now to the next hour boundary.
        """
        registry = FixedWindowRegistry()
        config   = FixedWindowConfig.from_parts(1, Window_Unit_Hour)

        _ = registry.check_inner('test_key', config, self.mid_us)
        denied = registry.check_inner('test_key', config, self.mid_us)

        expected_retry = self.next_us - self.mid_us
        self.assertEqual(denied.retry_after_us, expected_retry)

# ################################################################################################################################
# ################################################################################################################################

class FixedWindowDayTestCase(TestCase):

    def setUp(self) -> 'None':
        self.mid_us  = _to_us(2023, 11, 14, 22, 13, 20)
        self.next_us = _to_us(2023, 11, 15)

    def test_fixed_window_day_window_reset_allows_again(self) -> 'None':
        """ After the day boundary, the counter resets and requests are allowed again.
        """
        registry = FixedWindowRegistry()
        config   = FixedWindowConfig.from_parts(1, Window_Unit_Day)

        result = registry.check_inner('test_key', config, self.mid_us)
        self.assertTrue(result.is_allowed)

        denied = registry.check_inner('test_key', config, self.mid_us)
        self.assertFalse(denied.is_allowed)

        fresh = registry.check_inner('test_key', config, self.next_us)
        self.assertTrue(fresh.is_allowed)

# ################################################################################################################################

    def test_fixed_window_day_retry_after_is_correct(self) -> 'None':
        """ retry_after_us equals the distance from now to the next day boundary.
        """
        registry = FixedWindowRegistry()
        config   = FixedWindowConfig.from_parts(1, Window_Unit_Day)

        _ = registry.check_inner('test_key', config, self.mid_us)
        denied = registry.check_inner('test_key', config, self.mid_us)

        expected_retry = self.next_us - self.mid_us
        self.assertEqual(denied.retry_after_us, expected_retry)

# ################################################################################################################################
# ################################################################################################################################

class FixedWindowMonthTestCase(TestCase):

    def setUp(self) -> 'None':
        self.mid_us  = _to_us(2023, 2, 15)
        self.next_us = _to_us(2023, 3, 1)

    def test_fixed_window_month_window_reset_allows_again(self) -> 'None':
        """ After the month boundary, the counter resets and requests are allowed again.
        """
        registry = FixedWindowRegistry()
        config   = FixedWindowConfig.from_parts(1, Window_Unit_Month)

        result = registry.check_inner('test_key', config, self.mid_us)
        self.assertTrue(result.is_allowed)

        denied = registry.check_inner('test_key', config, self.mid_us)
        self.assertFalse(denied.is_allowed)

        fresh = registry.check_inner('test_key', config, self.next_us)
        self.assertTrue(fresh.is_allowed)

# ################################################################################################################################

    def test_fixed_window_month_retry_after_is_correct(self) -> 'None':
        """ retry_after_us equals the distance from now to the next month boundary.
        """
        registry = FixedWindowRegistry()
        config   = FixedWindowConfig.from_parts(1, Window_Unit_Month)

        _ = registry.check_inner('test_key', config, self.mid_us)
        denied = registry.check_inner('test_key', config, self.mid_us)

        expected_retry = self.next_us - self.mid_us
        self.assertEqual(denied.retry_after_us, expected_retry)

# ################################################################################################################################
# ################################################################################################################################

class FixedWindowRegistryHousekeepingTestCase(TestCase):

    def setUp(self) -> 'None':
        self.now_us = _to_us(2023, 11, 14, 22, 13, 20)

    def test_fixed_window_separate_keys_independent(self) -> 'None':
        """ Exhausting one key does not affect another.
        """
        registry = FixedWindowRegistry()
        config   = FixedWindowConfig.from_parts(1, Window_Unit_Second)

        _ = registry.check_inner('key_a', config, self.now_us)
        denied = registry.check_inner('key_a', config, self.now_us)
        self.assertFalse(denied.is_allowed)

        other = registry.check_inner('key_b', config, self.now_us)
        self.assertTrue(other.is_allowed)

# ################################################################################################################################

    def test_fixed_window_remove_clears_state(self) -> 'None':
        """ After removing a key, the next check starts fresh.
        """
        registry = FixedWindowRegistry()
        config   = FixedWindowConfig.from_parts(1, Window_Unit_Second)

        _ = registry.check_inner('test_key', config, self.now_us)
        denied = registry.check_inner('test_key', config, self.now_us)
        self.assertFalse(denied.is_allowed)

        registry.remove('test_key')

        fresh = registry.check_inner('test_key', config, self.now_us)
        self.assertTrue(fresh.is_allowed)

# ################################################################################################################################

    def test_fixed_window_clear_removes_all(self) -> 'None':
        """ clear() empties the entire registry.
        """
        registry = FixedWindowRegistry()
        config   = FixedWindowConfig.from_parts(10, Window_Unit_Second)

        _ = registry.check_inner('key_a', config, self.now_us)
        _ = registry.check_inner('key_b', config, self.now_us)
        self.assertEqual(len(registry), 2)

        registry.clear()
        self.assertTrue(registry.is_empty())

# ################################################################################################################################

    def test_fixed_window_len_and_is_empty(self) -> 'None':
        """ len() and is_empty() reflect the number of registered keys.
        """
        registry = FixedWindowRegistry()
        config   = FixedWindowConfig.from_parts(10, Window_Unit_Second)

        self.assertTrue(registry.is_empty())
        self.assertEqual(len(registry), 0)

        _ = registry.check_inner('key_a', config, self.now_us)
        self.assertFalse(registry.is_empty())
        self.assertEqual(len(registry), 1)

        _ = registry.check_inner('key_b', config, self.now_us)
        self.assertEqual(len(registry), 2)

        registry.remove('key_a')
        self.assertEqual(len(registry), 1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()
