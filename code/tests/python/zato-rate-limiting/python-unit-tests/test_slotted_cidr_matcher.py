# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.rate_limiting.cidr import SlottedCIDRMatcher

# ################################################################################################################################
# ################################################################################################################################

_rule_10 = {
    'cidr_list': ['10.0.0.0/8'],
    'time_range': [
        {'is_all_day': True, 'disabled': False, 'disallowed': False,
         'rate': 10, 'burst': 20, 'limit': 100, 'limit_unit': 'minute'},
    ],
}

_rule_192 = {
    'cidr_list': ['192.168.0.0/16'],
    'time_range': [
        {'is_all_day': True, 'disabled': False, 'disallowed': False,
         'rate': 50, 'burst': 100, 'limit': 500, 'limit_unit': 'hour'},
    ],
}

_rule_catchall = {
    'cidr_list': ['0.0.0.0/0', '::/0'],
    'time_range': [
        {'is_all_day': True, 'disabled': False, 'disallowed': False,
         'rate': 100, 'burst': 50, 'limit': 1000, 'limit_unit': 'day'},
    ],
}

_rule_with_disabled_range = {
    'cidr_list': ['10.0.0.0/8'],
    'time_range': [
        {'is_all_day': True, 'disabled': False, 'disallowed': False,
         'rate': 10, 'burst': 20, 'limit': 100, 'limit_unit': 'minute'},
        {'is_all_day': False, 'disabled': True, 'disallowed': False,
         'time_from': '09:00', 'time_to': '17:00',
         'rate': 5, 'burst': 10, 'limit': 50, 'limit_unit': 'minute'},
    ],
}

# ################################################################################################################################
# ################################################################################################################################

class SlottedCIDRMatcherResolveTestCase(TestCase):

    def test_resolve_single_rule(self) -> 'None':
        """ A single rule resolves when the IP matches.
        """
        matcher = SlottedCIDRMatcher()
        matcher.replace_all([_rule_10])

        match = matcher.resolve('10.1.2.3')

        self.assertIsNotNone(match)
        self.assertEqual(match.key, '10.0.0.0/8') # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################

    def test_resolve_no_match(self) -> 'None':
        """ Returns None when no rule matches the IP.
        """
        matcher = SlottedCIDRMatcher()
        matcher.replace_all([_rule_10])

        match = matcher.resolve('192.168.1.1')

        self.assertIsNone(match)

# ################################################################################################################################

    def test_resolve_first_rule_wins(self) -> 'None':
        """ When multiple rules match, the first one in order wins.
        """
        matcher = SlottedCIDRMatcher()
        matcher.replace_all([_rule_10, _rule_catchall])

        match = matcher.resolve('10.1.2.3')

        self.assertIsNotNone(match)
        self.assertEqual(match.key, '10.0.0.0/8') # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################

    def test_resolve_second_rule(self) -> 'None':
        """ An IP that does not match the first rule can match the second.
        """
        matcher = SlottedCIDRMatcher()
        matcher.replace_all([_rule_10, _rule_192])

        match = matcher.resolve('192.168.1.1')

        self.assertIsNotNone(match)
        self.assertEqual(match.key, '192.168.0.0/16') # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################

    def test_resolve_empty_matcher(self) -> 'None':
        """ An empty matcher returns None for any IP.
        """
        matcher = SlottedCIDRMatcher()

        match = matcher.resolve('10.1.2.3')

        self.assertIsNone(match)

# ################################################################################################################################
# ################################################################################################################################

class SlottedCIDRMatcherReplaceAllTestCase(TestCase):

    def test_replace_all_swaps_rules(self) -> 'None':
        """ replace_all replaces the existing rules entirely.
        """
        matcher = SlottedCIDRMatcher()
        matcher.replace_all([_rule_10])

        self.assertEqual(len(matcher), 1)

        # .. replace with two rules.
        matcher.replace_all([_rule_10, _rule_192])

        self.assertEqual(len(matcher), 2)

# ################################################################################################################################

    def test_replace_all_empty_clears(self) -> 'None':
        """ replace_all with an empty list clears the matcher.
        """
        matcher = SlottedCIDRMatcher()
        matcher.replace_all([_rule_10])
        matcher.replace_all([])

        self.assertEqual(len(matcher), 0)
        self.assertTrue(matcher.is_empty())

# ################################################################################################################################
# ################################################################################################################################

class SlottedCIDRMatcherToListTestCase(TestCase):

    def test_to_list_round_trip(self) -> 'None':
        """ to_list produces dicts that can be fed back into replace_all.
        """
        matcher = SlottedCIDRMatcher()
        matcher.replace_all([_rule_10, _rule_192])

        result = matcher.to_list()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['cidr_list'], ['10.0.0.0/8'])
        self.assertEqual(result[1]['cidr_list'], ['192.168.0.0/16'])

# ################################################################################################################################

    def test_to_list_empty(self) -> 'None':
        """ to_list on an empty matcher returns an empty list.
        """
        matcher = SlottedCIDRMatcher()

        result = matcher.to_list()

        self.assertEqual(result, [])

# ################################################################################################################################

    def test_to_list_preserves_time_ranges(self) -> 'None':
        """ to_list preserves all time range entries including disabled ones.
        """
        matcher = SlottedCIDRMatcher()
        matcher.replace_all([_rule_with_disabled_range])

        result = matcher.to_list()

        self.assertEqual(len(result[0]['time_range']), 2)
        self.assertTrue(result[0]['time_range'][1]['disabled'])

# ################################################################################################################################

    def test_full_round_trip(self) -> 'None':
        """ Rules survive a full replace_all -> to_list -> replace_all cycle.
        """
        matcher = SlottedCIDRMatcher()
        matcher.replace_all([_rule_10, _rule_catchall])

        serialized = matcher.to_list()

        matcher_2 = SlottedCIDRMatcher()
        matcher_2.replace_all(serialized)

        result = matcher_2.to_list()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['cidr_list'], ['10.0.0.0/8'])
        self.assertEqual(result[1]['cidr_list'], ['0.0.0.0/0', '::/0'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()
