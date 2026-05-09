# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import datetime
from unittest import main, TestCase

# Zato
from zato.common.rate_limiting.common import Microseconds_Per_Second, RateLimitError, current_time_us, \
    validate_window_unit, Window_Unit_Second, Window_Unit_Minute, Window_Unit_Hour, Window_Unit_Day, Window_Unit_Month

# ################################################################################################################################
# ################################################################################################################################

_utc = datetime.timezone.utc

#  A known past date to verify that current_time_us returns a plausible value.
_plausibility_threshold_us = int(datetime.datetime(2023, 11, 14, tzinfo=_utc).timestamp()) * Microseconds_Per_Second

# ################################################################################################################################
# ################################################################################################################################

class CommonTestCase(TestCase):

    def test_error_display(self) -> 'None':
        """ str() of a RateLimitError contains the original message.
        """
        error = RateLimitError('Test error message')
        self.assertIn('Test error message', str(error))

# ################################################################################################################################

    def test_error_is_exception(self) -> 'None':
        """ RateLimitError is a proper Exception subclass.
        """
        error = RateLimitError('Test error')
        self.assertIsInstance(error, Exception)

# ################################################################################################################################

    def test_microseconds_per_second_value(self) -> 'None':
        """ The constant has the expected value.
        """
        self.assertEqual(Microseconds_Per_Second, 1_000_000)

# ################################################################################################################################

    def test_current_time_us_returns_positive(self) -> 'None':
        """ current_time_us returns a positive integer.
        """
        now = current_time_us()
        self.assertGreater(now, 0)

# ################################################################################################################################

    def test_current_time_us_is_plausible(self) -> 'None':
        """ Timestamp must be after 2023-11-14 UTC.
        """
        now = current_time_us()
        self.assertGreater(now, _plausibility_threshold_us)

# ################################################################################################################################

    def test_validate_window_unit_all_variants(self) -> 'None':
        """ Each known unit string passes validation and is returned unchanged.
        """
        for unit in (Window_Unit_Second, Window_Unit_Minute, Window_Unit_Hour, Window_Unit_Day, Window_Unit_Month):
            result = validate_window_unit(unit)
            self.assertEqual(result, unit)

# ################################################################################################################################

    def test_validate_window_unit_invalid(self) -> 'None':
        """ An unknown unit raises RateLimitError.
        """
        with self.assertRaises(RateLimitError):
            _ = validate_window_unit('invalid_unit')

# ################################################################################################################################

    def test_validate_window_unit_error_message(self) -> 'None':
        """ The error message contains the invalid input.
        """
        with self.assertRaises(RateLimitError) as context:
            _ = validate_window_unit('invalid_unit')
        self.assertIn('invalid_unit', str(context.exception))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()
