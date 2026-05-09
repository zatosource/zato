# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ipaddress
from unittest import main, TestCase

# Zato
from zato.common.rate_limiting.cidr import SlottedCIDRRule
from zato.common.rate_limiting.common import hh_mm_to_minutes, RateLimitError, TimeRange

# ################################################################################################################################
# ################################################################################################################################

def _make_all_day_range() -> 'TimeRange':
    """ Builds a valid all-day TimeRange for testing.
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

def _make_specific_range(time_from:'str'='01:00', time_to:'str'='02:00') -> 'TimeRange':
    """ Builds a valid non-all-day TimeRange for testing.
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
# ################################################################################################################################

class SlottedCIDRRuleConstructionTestCase(TestCase):

    def test_valid_construction(self) -> 'None':
        """ A rule with a valid all-day first entry can be constructed.
        """
        all_day = _make_all_day_range()

        rule = SlottedCIDRRule.from_parts(['10.0.0.0/8'], [all_day])

        self.assertEqual(len(rule.entries), 1)
        self.assertEqual(len(rule.time_range), 1)
        self.assertEqual(rule.entries[0].key, '10.0.0.0/8')

# ################################################################################################################################

    def test_multiple_cidrs(self) -> 'None':
        """ A rule can have multiple CIDR entries.
        """
        all_day = _make_all_day_range()

        rule = SlottedCIDRRule.from_parts(['10.0.0.0/8', '192.168.0.0/16'], [all_day])

        self.assertEqual(len(rule.entries), 2)
        self.assertEqual(rule.entries[0].key, '10.0.0.0/8')
        self.assertEqual(rule.entries[1].key, '192.168.0.0/16')

# ################################################################################################################################

    def test_multiple_time_ranges(self) -> 'None':
        """ A rule can have multiple time ranges after the all-day entry.
        """
        all_day  = _make_all_day_range()
        range_1  = _make_specific_range('01:00', '02:00')
        range_2  = _make_specific_range('03:00', '04:00')

        rule = SlottedCIDRRule.from_parts(['10.0.0.0/8'], [all_day, range_1, range_2])

        self.assertEqual(len(rule.time_range), 3)
        self.assertTrue(rule.time_range[0].is_all_day)
        self.assertEqual(rule.time_range[1].time_from, '01:00')
        self.assertEqual(rule.time_range[2].time_from, '03:00')

# ################################################################################################################################

    def test_empty_time_range_raises(self) -> 'None':
        """ An empty time_range list raises RateLimitError.
        """
        with self.assertRaises(RateLimitError):
            SlottedCIDRRule.from_parts(['10.0.0.0/8'], [])

# ################################################################################################################################

    def test_first_entry_not_all_day_raises(self) -> 'None':
        """ A time_range list whose first entry is not all-day raises RateLimitError.
        """
        specific = _make_specific_range()

        with self.assertRaises(RateLimitError):
            SlottedCIDRRule.from_parts(['10.0.0.0/8'], [specific])

# ################################################################################################################################

    def test_invalid_cidr_raises(self) -> 'None':
        """ An invalid CIDR string raises RateLimitError.
        """
        all_day = _make_all_day_range()

        with self.assertRaises(RateLimitError):
            SlottedCIDRRule.from_parts(['not-a-cidr'], [all_day])

# ################################################################################################################################
# ################################################################################################################################

class SlottedCIDRRuleMatchTestCase(TestCase):

    def test_match_ipv4(self) -> 'None':
        """ An IPv4 address inside the CIDR range matches.
        """
        all_day = _make_all_day_range()
        rule    = SlottedCIDRRule.from_parts(['10.0.0.0/8'], [all_day])
        address = ipaddress.ip_address('10.1.2.3')

        entry = rule.match(address)

        self.assertIsNotNone(entry)
        self.assertEqual(entry.key, '10.0.0.0/8') # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################

    def test_no_match_ipv4(self) -> 'None':
        """ An IPv4 address outside all CIDR ranges returns None.
        """
        all_day = _make_all_day_range()
        rule    = SlottedCIDRRule.from_parts(['10.0.0.0/8'], [all_day])
        address = ipaddress.ip_address('192.168.1.1')

        entry = rule.match(address)

        self.assertIsNone(entry)

# ################################################################################################################################

    def test_match_first_of_multiple(self) -> 'None':
        """ When multiple CIDRs match, the first one wins.
        """
        all_day = _make_all_day_range()
        rule    = SlottedCIDRRule.from_parts(['10.0.0.0/8', '10.1.0.0/16'], [all_day])
        address = ipaddress.ip_address('10.1.2.3')

        entry = rule.match(address)

        self.assertIsNotNone(entry)
        self.assertEqual(entry.key, '10.0.0.0/8') # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################

    def test_match_ipv6(self) -> 'None':
        """ An IPv6 address inside the CIDR range matches.
        """
        all_day = _make_all_day_range()
        rule    = SlottedCIDRRule.from_parts(['fd00::/8'], [all_day])
        address = ipaddress.ip_address('fd00::1')

        entry = rule.match(address)

        self.assertIsNotNone(entry)
        self.assertEqual(entry.key, 'fd00::/8') # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################

    def test_mixed_ipv4_ipv6_skips_wrong_family(self) -> 'None':
        """ An IPv4 address does not match an IPv6 CIDR entry, and vice versa.
        """
        all_day = _make_all_day_range()
        rule    = SlottedCIDRRule.from_parts(['fd00::/8', '10.0.0.0/8'], [all_day])

        # IPv4 address should skip the IPv6 entry and match the IPv4 entry ..
        address_v4 = ipaddress.ip_address('10.1.2.3')
        entry_v4   = rule.match(address_v4)

        self.assertIsNotNone(entry_v4)
        self.assertEqual(entry_v4.key, '10.0.0.0/8') # pyright: ignore[reportOptionalMemberAccess]

        # .. IPv6 address should skip the IPv4 entry and match the IPv6 entry.
        address_v6 = ipaddress.ip_address('fd00::1')
        entry_v6   = rule.match(address_v6)

        self.assertIsNotNone(entry_v6)
        self.assertEqual(entry_v6.key, 'fd00::/8') # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################
# ################################################################################################################################

class ResolveTimeRangeBasicTestCase(TestCase):

    def test_single_range_matches(self) -> 'None':
        """ A single specific range is returned when the current time falls inside it.
        """
        all_day = _make_all_day_range()
        range_1 = _make_specific_range('09:00', '17:00')
        rule    = SlottedCIDRRule.from_parts(['10.0.0.0/8'], [all_day, range_1])

        now_minutes = hh_mm_to_minutes('10:00')
        result      = rule.resolve_time_range(now_minutes)

        self.assertFalse(result.is_all_day)
        self.assertEqual(result.time_from, '09:00')

# ################################################################################################################################

    def test_single_range_no_match_returns_all_day(self) -> 'None':
        """ When no specific range matches, the all-day default is returned.
        """
        all_day = _make_all_day_range()
        range_1 = _make_specific_range('09:00', '17:00')
        rule    = SlottedCIDRRule.from_parts(['10.0.0.0/8'], [all_day, range_1])

        now_minutes = hh_mm_to_minutes('20:00')
        result      = rule.resolve_time_range(now_minutes)

        self.assertTrue(result.is_all_day)

# ################################################################################################################################

    def test_first_matching_range_wins(self) -> 'None':
        """ When multiple ranges cover the current time, the first one in user order wins.
        """
        all_day = _make_all_day_range()
        range_1 = _make_specific_range('08:00', '12:00')
        range_2 = _make_specific_range('10:00', '14:00')
        rule    = SlottedCIDRRule.from_parts(['10.0.0.0/8'], [all_day, range_1, range_2])

        now_minutes = hh_mm_to_minutes('11:00')
        result      = rule.resolve_time_range(now_minutes)

        self.assertEqual(result.time_from, '08:00')

# ################################################################################################################################

    def test_only_all_day_entry(self) -> 'None':
        """ When only the all-day entry exists, it is always returned.
        """
        all_day = _make_all_day_range()
        rule    = SlottedCIDRRule.from_parts(['10.0.0.0/8'], [all_day])

        now_minutes = hh_mm_to_minutes('12:00')
        result      = rule.resolve_time_range(now_minutes)

        self.assertTrue(result.is_all_day)

# ################################################################################################################################
# ################################################################################################################################

class ResolveTimeRangeDisabledTestCase(TestCase):

    def test_disabled_entry_skipped(self) -> 'None':
        """ A disabled range is skipped even if its time window matches.
        """
        all_day = _make_all_day_range()
        range_1 = _make_specific_range('09:00', '17:00')
        range_2 = _make_specific_range('09:00', '17:00')

        range_1.disabled = True

        rule = SlottedCIDRRule.from_parts(['10.0.0.0/8'], [all_day, range_1, range_2])

        now_minutes = hh_mm_to_minutes('10:00')
        result      = rule.resolve_time_range(now_minutes)

        # .. range_1 is disabled, so range_2 should be picked.
        self.assertIs(result, range_2)

# ################################################################################################################################

    def test_all_specific_disabled_returns_all_day(self) -> 'None':
        """ When all non-all-day entries are disabled, the all-day default is returned.
        """
        all_day = _make_all_day_range()
        range_1 = _make_specific_range('09:00', '17:00')
        range_2 = _make_specific_range('10:00', '14:00')

        range_1.disabled = True
        range_2.disabled = True

        rule = SlottedCIDRRule.from_parts(['10.0.0.0/8'], [all_day, range_1, range_2])

        now_minutes = hh_mm_to_minutes('11:00')
        result      = rule.resolve_time_range(now_minutes)

        self.assertTrue(result.is_all_day)

# ################################################################################################################################

    def test_disabled_all_day_still_returned_as_default(self) -> 'None':
        """ A disabled all-day entry is still returned as the default when no specific range matches.
        """
        all_day = _make_all_day_range()
        all_day.disabled = True

        range_1 = _make_specific_range('09:00', '10:00')
        rule    = SlottedCIDRRule.from_parts(['10.0.0.0/8'], [all_day, range_1])

        # .. time outside range_1, so the all-day default is returned even though it is disabled.
        now_minutes = hh_mm_to_minutes('20:00')
        result      = rule.resolve_time_range(now_minutes)

        self.assertIs(result, all_day)
        self.assertTrue(result.disabled)

# ################################################################################################################################
# ################################################################################################################################

class ResolveTimeRangeDisallowedAndMidnightTestCase(TestCase):

    def test_disallowed_entry_returned_when_matching(self) -> 'None':
        """ A disallowed range is returned as-is when its time window matches.
        """
        all_day = _make_all_day_range()
        range_1 = _make_specific_range('03:00', '04:00')
        range_1.disallowed = True

        rule = SlottedCIDRRule.from_parts(['10.0.0.0/8'], [all_day, range_1])

        now_minutes = hh_mm_to_minutes('03:30')
        result      = rule.resolve_time_range(now_minutes)

        self.assertIs(result, range_1)
        self.assertTrue(result.disallowed)

# ################################################################################################################################

    def test_disallowed_entry_not_returned_when_not_matching(self) -> 'None':
        """ A disallowed range is not returned when the current time is outside its window.
        """
        all_day = _make_all_day_range()
        range_1 = _make_specific_range('03:00', '04:00')
        range_1.disallowed = True

        rule = SlottedCIDRRule.from_parts(['10.0.0.0/8'], [all_day, range_1])

        now_minutes = hh_mm_to_minutes('12:00')
        result      = rule.resolve_time_range(now_minutes)

        self.assertTrue(result.is_all_day)

# ################################################################################################################################

    def test_midnight_crossing_before_midnight(self) -> 'None':
        """ A midnight-crossing range (23:00-02:00) matches a time before midnight.
        """
        all_day = _make_all_day_range()
        range_1 = _make_specific_range('23:00', '02:00')

        rule = SlottedCIDRRule.from_parts(['10.0.0.0/8'], [all_day, range_1])

        now_minutes = hh_mm_to_minutes('23:30')
        result      = rule.resolve_time_range(now_minutes)

        self.assertIs(result, range_1)

# ################################################################################################################################

    def test_midnight_crossing_after_midnight(self) -> 'None':
        """ A midnight-crossing range (23:00-02:00) matches a time after midnight.
        """
        all_day = _make_all_day_range()
        range_1 = _make_specific_range('23:00', '02:00')

        rule = SlottedCIDRRule.from_parts(['10.0.0.0/8'], [all_day, range_1])

        now_minutes = hh_mm_to_minutes('01:00')
        result      = rule.resolve_time_range(now_minutes)

        self.assertIs(result, range_1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()
