# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.rate_limiting.common import RateLimitError, TimeRange

# ################################################################################################################################
# ################################################################################################################################

class FromDictTestCase(TestCase):

    def test_all_day_round_trip(self) -> 'None':
        """ An all-day dict round-trips through from_dict and to_dict.
        """
        data = {
            'is_all_day': True,
            'disabled': False,
            'disallowed': False,
            'rate': 10,
            'burst': 20,
            'limit': 100,
            'limit_unit': 'minute',
        }

        time_range = TimeRange.from_dict(data)

        self.assertTrue(time_range.is_all_day)
        self.assertFalse(time_range.disabled)
        self.assertFalse(time_range.disallowed)
        self.assertEqual(time_range.time_from, '')
        self.assertEqual(time_range.time_to, '')
        self.assertEqual(time_range.rate, 10)
        self.assertEqual(time_range.burst, 20)
        self.assertEqual(time_range.limit, 100)
        self.assertEqual(time_range.limit_unit, 'minute')

        result = time_range.to_dict()

        self.assertTrue(result['is_all_day'])
        self.assertNotIn('time_from', result)
        self.assertNotIn('time_to', result)
        self.assertEqual(result['rate'], 10)

# ################################################################################################################################

    def test_range_round_trip(self) -> 'None':
        """ A non-all-day dict round-trips through from_dict and to_dict.
        """
        data = {
            'is_all_day': False,
            'disabled': False,
            'disallowed': False,
            'time_from': '01:00',
            'time_to': '02:00',
            'rate': 5,
            'burst': 10,
            'limit': 50,
            'limit_unit': 'minute',
        }

        time_range = TimeRange.from_dict(data)

        self.assertFalse(time_range.is_all_day)
        self.assertEqual(time_range.time_from, '01:00')
        self.assertEqual(time_range.time_to, '02:00')
        self.assertEqual(time_range.rate, 5)

        result = time_range.to_dict()

        self.assertFalse(result['is_all_day'])
        self.assertEqual(result['time_from'], '01:00')
        self.assertEqual(result['time_to'], '02:00')

# ################################################################################################################################

    def test_disabled_round_trip(self) -> 'None':
        """ A disabled range preserves its state through serialization.
        """
        data = {
            'is_all_day': False,
            'disabled': True,
            'disallowed': False,
            'time_from': '05:00',
            'time_to': '06:00',
            'rate': 2,
            'burst': 5,
            'limit': 20,
            'limit_unit': 'hour',
        }

        time_range = TimeRange.from_dict(data)
        result = time_range.to_dict()

        self.assertTrue(result['disabled'])
        self.assertFalse(result['disallowed'])

# ################################################################################################################################

    def test_disallowed_round_trip(self) -> 'None':
        """ A disallowed range preserves its state through serialization.
        """
        data = {
            'is_all_day': False,
            'disabled': False,
            'disallowed': True,
            'time_from': '03:00',
            'time_to': '04:00',
            'rate': 0,
            'burst': 0,
            'limit': 0,
            'limit_unit': 'minute',
        }

        time_range = TimeRange.from_dict(data)
        result = time_range.to_dict()

        self.assertFalse(result['disabled'])
        self.assertTrue(result['disallowed'])

# ################################################################################################################################

    def test_string_rate_burst_limit_converted(self) -> 'None':
        """ Rate, burst, and limit are converted from strings (as sent by UI) to ints.
        """
        data = {
            'is_all_day': True,
            'disabled': False,
            'disallowed': False,
            'rate': '10',
            'burst': '20',
            'limit': '100',
            'limit_unit': 'second',
        }

        time_range = TimeRange.from_dict(data)

        self.assertEqual(time_range.rate, 10)
        self.assertEqual(time_range.burst, 20)
        self.assertEqual(time_range.limit, 100)

# ################################################################################################################################

    def test_all_day_with_time_from_raises(self) -> 'None':
        """ An all-day entry that also has time_from in the dict is still rejected by validation.
        """
        data = {
            'is_all_day': True,
            'disabled': False,
            'disallowed': False,
            'time_from': '01:00',
            'time_to': '02:00',
            'rate': 10,
            'burst': 20,
            'limit': 100,
            'limit_unit': 'minute',
        }

        with self.assertRaises(RateLimitError):
            TimeRange.from_dict(data)

# ################################################################################################################################

    def test_missing_is_all_day_raises(self) -> 'None':
        """ A dict without is_all_day raises KeyError.
        """
        data = {
            'disabled': False,
            'disallowed': False,
            'rate': 10,
            'burst': 20,
            'limit': 100,
            'limit_unit': 'minute',
        }

        with self.assertRaises(KeyError):
            TimeRange.from_dict(data)

# ################################################################################################################################

    def test_invalid_limit_unit_raises(self) -> 'None':
        """ An invalid limit_unit in the dict raises RateLimitError during from_dict.
        """
        data = {
            'is_all_day': True,
            'disabled': False,
            'disallowed': False,
            'rate': 10,
            'burst': 20,
            'limit': 100,
            'limit_unit': 'invalid_unit',
        }

        with self.assertRaises(RateLimitError):
            TimeRange.from_dict(data)

# ################################################################################################################################

    def test_range_missing_time_from_raises(self) -> 'None':
        """ A non-all-day entry without time_from raises KeyError.
        """
        data = {
            'is_all_day': False,
            'disabled': False,
            'disallowed': False,
            'time_to': '02:00',
            'rate': 5,
            'burst': 10,
            'limit': 50,
            'limit_unit': 'minute',
        }

        with self.assertRaises(KeyError):
            TimeRange.from_dict(data)

# ################################################################################################################################

    def test_range_missing_time_to_raises(self) -> 'None':
        """ A non-all-day entry without time_to raises KeyError.
        """
        data = {
            'is_all_day': False,
            'disabled': False,
            'disallowed': False,
            'time_from': '01:00',
            'rate': 5,
            'burst': 10,
            'limit': 50,
            'limit_unit': 'minute',
        }

        with self.assertRaises(KeyError):
            TimeRange.from_dict(data)

# ################################################################################################################################

    def test_invalid_time_from_format_raises(self) -> 'None':
        """ A non-all-day entry with badly formatted time_from raises RateLimitError.
        """
        data = {
            'is_all_day': False,
            'disabled': False,
            'disallowed': False,
            'time_from': '2500',
            'time_to': '02:00',
            'rate': 5,
            'burst': 10,
            'limit': 50,
            'limit_unit': 'minute',
        }

        with self.assertRaises(RateLimitError):
            TimeRange.from_dict(data)

# ################################################################################################################################

    def test_midnight_crossing_range_round_trip(self) -> 'None':
        """ A midnight-crossing range (23:00-02:00) round-trips correctly.
        """
        data = {
            'is_all_day': False,
            'disabled': False,
            'disallowed': False,
            'time_from': '23:00',
            'time_to': '02:00',
            'rate': 3,
            'burst': 6,
            'limit': 30,
            'limit_unit': 'hour',
        }

        time_range = TimeRange.from_dict(data)
        result = time_range.to_dict()

        self.assertEqual(result['time_from'], '23:00')
        self.assertEqual(result['time_to'], '02:00')
        self.assertEqual(result['rate'], 3)

# ################################################################################################################################

    def test_to_dict_all_limit_units(self) -> 'None':
        """ All valid limit units survive the round trip.
        """
        for unit in ('second', 'minute', 'hour', 'day', 'month'):
            data = {
                'is_all_day': True,
                'disabled': False,
                'disallowed': False,
                'rate': 1,
                'burst': 1,
                'limit': 1,
                'limit_unit': unit,
            }

            time_range = TimeRange.from_dict(data)
            result = time_range.to_dict()

            self.assertEqual(result['limit_unit'], unit)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()
