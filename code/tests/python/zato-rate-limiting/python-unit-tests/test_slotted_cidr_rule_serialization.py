# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.rate_limiting.cidr import SlottedCIDRRule
from zato.common.rate_limiting.common import RateLimitError

# ################################################################################################################################
# ################################################################################################################################

class SlottedCIDRRuleFromDictTestCase(TestCase):

    def test_all_day_only_round_trip(self) -> 'None':
        """ A rule with only the all-day entry round-trips through from_dict and to_dict.
        """
        data = {
            'cidr_list': ['10.0.0.0/8'],
            'time_range': [
                {'is_all_day': True, 'disabled': False, 'disallowed': False,
                 'rate': 10, 'burst': 20, 'limit': 100, 'limit_unit': 'minute'},
            ],
        }

        rule   = SlottedCIDRRule.from_dict(data)
        result = rule.to_dict()

        self.assertEqual(result['cidr_list'], ['10.0.0.0/8'])
        self.assertEqual(len(result['time_range']), 1)
        self.assertTrue(result['time_range'][0]['is_all_day'])

# ################################################################################################################################

    def test_multiple_time_ranges_round_trip(self) -> 'None':
        """ A rule with multiple time ranges round-trips correctly.
        """
        data = {
            'cidr_list': ['10.0.0.0/8'],
            'time_range': [
                {'is_all_day': True, 'disabled': False, 'disallowed': False,
                 'rate': 10, 'burst': 20, 'limit': 100, 'limit_unit': 'minute'},
                {'is_all_day': False, 'disabled': False, 'disallowed': False,
                 'time_from': '01:00', 'time_to': '02:00',
                 'rate': 5, 'burst': 10, 'limit': 50, 'limit_unit': 'minute'},
                {'is_all_day': False, 'disabled': False, 'disallowed': True,
                 'time_from': '03:00', 'time_to': '04:00',
                 'rate': 0, 'burst': 0, 'limit': 0, 'limit_unit': 'minute'},
            ],
        }

        rule   = SlottedCIDRRule.from_dict(data)
        result = rule.to_dict()

        self.assertEqual(len(result['time_range']), 3)
        self.assertFalse(result['time_range'][1]['is_all_day'])
        self.assertEqual(result['time_range'][1]['time_from'], '01:00')
        self.assertTrue(result['time_range'][2]['disallowed'])

# ################################################################################################################################

    def test_multiple_cidrs_round_trip(self) -> 'None':
        """ A rule with multiple CIDR entries round-trips correctly.
        """
        data = {
            'cidr_list': ['10.0.0.0/8', '192.168.0.0/16'],
            'time_range': [
                {'is_all_day': True, 'disabled': False, 'disallowed': False,
                 'rate': 10, 'burst': 20, 'limit': 100, 'limit_unit': 'minute'},
            ],
        }

        rule   = SlottedCIDRRule.from_dict(data)
        result = rule.to_dict()

        self.assertEqual(result['cidr_list'], ['10.0.0.0/8', '192.168.0.0/16'])

# ################################################################################################################################

    def test_string_rate_values_converted(self) -> 'None':
        """ String rate/burst/limit from the UI are converted to ints in the round trip.
        """
        data = {
            'cidr_list': ['10.0.0.0/8'],
            'time_range': [
                {'is_all_day': True, 'disabled': False, 'disallowed': False,
                 'rate': '10', 'burst': '20', 'limit': '100', 'limit_unit': 'second'},
            ],
        }

        rule   = SlottedCIDRRule.from_dict(data)
        result = rule.to_dict()

        self.assertEqual(result['time_range'][0]['rate'], 10)
        self.assertEqual(result['time_range'][0]['burst'], 20)
        self.assertEqual(result['time_range'][0]['limit'], 100)

# ################################################################################################################################

    def test_empty_time_range_raises(self) -> 'None':
        """ A dict with an empty time_range list raises RateLimitError.
        """
        data = {
            'cidr_list': ['10.0.0.0/8'],
            'time_range': [],
        }

        with self.assertRaises(RateLimitError):
            SlottedCIDRRule.from_dict(data)

# ################################################################################################################################

    def test_first_entry_not_all_day_raises(self) -> 'None':
        """ A dict where time_range[0] is not all-day raises RateLimitError.
        """
        data = {
            'cidr_list': ['10.0.0.0/8'],
            'time_range': [
                {'is_all_day': False, 'disabled': False, 'disallowed': False,
                 'time_from': '01:00', 'time_to': '02:00',
                 'rate': 5, 'burst': 10, 'limit': 50, 'limit_unit': 'minute'},
            ],
        }

        with self.assertRaises(RateLimitError):
            SlottedCIDRRule.from_dict(data)

# ################################################################################################################################

    def test_invalid_cidr_raises(self) -> 'None':
        """ A dict with an invalid CIDR string raises RateLimitError.
        """
        data = {
            'cidr_list': ['not-a-cidr'],
            'time_range': [
                {'is_all_day': True, 'disabled': False, 'disallowed': False,
                 'rate': 10, 'burst': 20, 'limit': 100, 'limit_unit': 'minute'},
            ],
        }

        with self.assertRaises(RateLimitError):
            SlottedCIDRRule.from_dict(data)

# ################################################################################################################################

    def test_invalid_time_range_raises(self) -> 'None':
        """ A dict with an invalid time range entry raises RateLimitError.
        """
        data = {
            'cidr_list': ['10.0.0.0/8'],
            'time_range': [
                {'is_all_day': True, 'disabled': False, 'disallowed': False,
                 'rate': 10, 'burst': 20, 'limit': 100, 'limit_unit': 'minute'},
                {'is_all_day': False, 'disabled': False, 'disallowed': False,
                 'time_from': '25:00', 'time_to': '02:00',
                 'rate': 5, 'burst': 10, 'limit': 50, 'limit_unit': 'minute'},
            ],
        }

        with self.assertRaises(RateLimitError):
            SlottedCIDRRule.from_dict(data)

# ################################################################################################################################

    def test_disabled_entry_preserved(self) -> 'None':
        """ A disabled time range entry is preserved through the round trip.
        """
        data = {
            'cidr_list': ['10.0.0.0/8'],
            'time_range': [
                {'is_all_day': True, 'disabled': False, 'disallowed': False,
                 'rate': 10, 'burst': 20, 'limit': 100, 'limit_unit': 'minute'},
                {'is_all_day': False, 'disabled': True, 'disallowed': False,
                 'time_from': '05:00', 'time_to': '06:00',
                 'rate': 2, 'burst': 5, 'limit': 20, 'limit_unit': 'hour'},
            ],
        }

        rule   = SlottedCIDRRule.from_dict(data)
        result = rule.to_dict()

        self.assertTrue(result['time_range'][1]['disabled'])

# ################################################################################################################################

    def test_cidr_normalised(self) -> 'None':
        """ A CIDR like 10.0.0.5/8 is normalised to 10.0.0.0/8 in the round trip.
        """
        data = {
            'cidr_list': ['10.0.0.5/8'],
            'time_range': [
                {'is_all_day': True, 'disabled': False, 'disallowed': False,
                 'rate': 10, 'burst': 20, 'limit': 100, 'limit_unit': 'minute'},
            ],
        }

        rule   = SlottedCIDRRule.from_dict(data)
        result = rule.to_dict()

        self.assertEqual(result['cidr_list'], ['10.0.0.0/8'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()
