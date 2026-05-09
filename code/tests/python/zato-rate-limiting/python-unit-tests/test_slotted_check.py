# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.rate_limiting.cidr import SlottedCIDRMatcher, SlottedCheckResult
from zato.common.rate_limiting.common import Window_Unit_Second
from zato.common.rate_limiting.fixed_window import FixedWindowRegistry
from zato.common.rate_limiting.token_bucket import TokenBucketRegistry

# ################################################################################################################################
# ################################################################################################################################

def _build_matcher_with_rules(rule_dicts):
    matcher = SlottedCIDRMatcher()
    matcher.replace_all(rule_dicts)
    return matcher

# ################################################################################################################################

def _all_day_range(**overrides):
    out = {
        'is_all_day':  True,
        'disabled':    False,
        'disallowed':  False,
        'rate':        100,
        'burst':       200,
        'limit':       1000,
        'limit_unit':  Window_Unit_Second,
    }
    out.update(overrides)
    return out

# ################################################################################################################################

def _specific_range(time_from, time_to, **overrides):
    out = {
        'is_all_day':  False,
        'disabled':    False,
        'disallowed':  False,
        'time_from':   time_from,
        'time_to':     time_to,
        'rate':        10,
        'burst':       20,
        'limit':       50,
        'limit_unit':  Window_Unit_Second,
    }
    out.update(overrides)
    return out

# ################################################################################################################################

# One microsecond-since-epoch value that lands at 10:30 UTC
# 2025-01-15 10:30:00 UTC
_now_us_10_30 = 1_736_935_800 * 1_000_000

# 2025-01-15 03:00:00 UTC
_now_us_03_00 = 1_736_908_800 * 1_000_000

# ################################################################################################################################
# ################################################################################################################################

class SlottedCheckAllowTestCase(unittest.TestCase):

    def test_allow_single_rule(self):
        """ A matching IP with generous limits is allowed.
        """
        rule = {
            'cidr_list': ['10.0.0.0/8'],
            'time_range': [_all_day_range(rate=100, burst=200, limit=1000)],
        }

        matcher  = _build_matcher_with_rules([rule])
        tb_reg   = TokenBucketRegistry()
        fw_reg   = FixedWindowRegistry()
        result   = matcher.check('10.0.0.1', tb_reg, fw_reg, _now_us_10_30)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, SlottedCheckResult)
        self.assertFalse(result.is_disallowed)
        self.assertTrue(result.is_allowed)
        self.assertEqual(result.retry_after_us, 0)

    def test_no_match_returns_none(self):
        """ An IP that does not match any rule returns None.
        """
        rule = {
            'cidr_list': ['10.0.0.0/8'],
            'time_range': [_all_day_range()],
        }

        matcher  = _build_matcher_with_rules([rule])
        tb_reg   = TokenBucketRegistry()
        fw_reg   = FixedWindowRegistry()
        result   = matcher.check('192.168.1.1', tb_reg, fw_reg, _now_us_10_30)

        self.assertIsNone(result)

# ################################################################################################################################
# ################################################################################################################################

class SlottedCheckDisallowedTestCase(unittest.TestCase):

    def test_disallowed_all_day(self):
        """ A disallowed all-day range returns is_disallowed=True immediately.
        """
        rule = {
            'cidr_list': ['10.0.0.0/8'],
            'time_range': [_all_day_range(disallowed=True)],
        }

        matcher  = _build_matcher_with_rules([rule])
        tb_reg   = TokenBucketRegistry()
        fw_reg   = FixedWindowRegistry()
        result   = matcher.check('10.0.0.1', tb_reg, fw_reg, _now_us_10_30)

        self.assertIsNotNone(result)
        self.assertTrue(result.is_disallowed)
        self.assertFalse(result.is_allowed)
        self.assertEqual(result.retry_after_us, 0)

    def test_disallowed_specific_range(self):
        """ A disallowed specific range that covers now returns is_disallowed=True.
        """
        rule = {
            'cidr_list': ['10.0.0.0/8'],
            'time_range': [
                _all_day_range(),
                _specific_range('10:00', '11:00', disallowed=True),
            ],
        }

        matcher  = _build_matcher_with_rules([rule])
        tb_reg   = TokenBucketRegistry()
        fw_reg   = FixedWindowRegistry()

        # 10:30 falls within 10:00-11:00
        result   = matcher.check('10.0.0.1', tb_reg, fw_reg, _now_us_10_30)

        self.assertIsNotNone(result)
        self.assertTrue(result.is_disallowed)
        self.assertFalse(result.is_allowed)

    def test_disallowed_range_not_active(self):
        """ A disallowed range that does not cover now is not returned; the all-day default is used instead.
        """
        rule = {
            'cidr_list': ['10.0.0.0/8'],
            'time_range': [
                _all_day_range(),
                _specific_range('10:00', '11:00', disallowed=True),
            ],
        }

        matcher  = _build_matcher_with_rules([rule])
        tb_reg   = TokenBucketRegistry()
        fw_reg   = FixedWindowRegistry()

        # 03:00 does not fall within 10:00-11:00, so the all-day default applies
        result   = matcher.check('10.0.0.1', tb_reg, fw_reg, _now_us_03_00)

        self.assertIsNotNone(result)
        self.assertFalse(result.is_disallowed)
        self.assertTrue(result.is_allowed)

# ################################################################################################################################
# ################################################################################################################################

class SlottedCheckTokenBucketDenyTestCase(unittest.TestCase):

    def test_token_bucket_exhausted(self):
        """ After exhausting the token bucket, is_allowed is False.
        """
        rule = {
            'cidr_list': ['10.0.0.0/8'],
            'time_range': [_all_day_range(rate=1, burst=1, limit=1000)],
        }

        matcher  = _build_matcher_with_rules([rule])
        tb_reg   = TokenBucketRegistry()
        fw_reg   = FixedWindowRegistry()

        # First check should be allowed
        result1 = matcher.check('10.0.0.1', tb_reg, fw_reg, _now_us_10_30)
        self.assertTrue(result1.is_allowed)

        # Second check at the same microsecond exhausts the bucket
        result2 = matcher.check('10.0.0.1', tb_reg, fw_reg, _now_us_10_30)
        self.assertFalse(result2.is_allowed)
        self.assertFalse(result2.is_disallowed)
        self.assertGreater(result2.retry_after_us, 0)

# ################################################################################################################################
# ################################################################################################################################

class SlottedCheckFixedWindowDenyTestCase(unittest.TestCase):

    def test_fixed_window_exhausted(self):
        """ After exhausting the fixed window limit, is_allowed is False.
        """
        rule = {
            'cidr_list': ['10.0.0.0/8'],
            'time_range': [_all_day_range(rate=1000, burst=1000, limit=2)],
        }

        matcher  = _build_matcher_with_rules([rule])
        tb_reg   = TokenBucketRegistry()
        fw_reg   = FixedWindowRegistry()

        # Two checks to exhaust the limit of 2
        matcher.check('10.0.0.1', tb_reg, fw_reg, _now_us_10_30)
        matcher.check('10.0.0.1', tb_reg, fw_reg, _now_us_10_30)

        # Third check exceeds the limit
        result = matcher.check('10.0.0.1', tb_reg, fw_reg, _now_us_10_30)
        self.assertFalse(result.is_allowed)
        self.assertFalse(result.is_disallowed)
        self.assertGreater(result.retry_after_us, 0)

# ################################################################################################################################
# ################################################################################################################################

class SlottedCheckDisabledRangeTestCase(unittest.TestCase):

    def test_disabled_range_falls_through_to_all_day_default(self):
        """ A disabled specific range is skipped and the all-day default is used.
        """
        rule = {
            'cidr_list': ['10.0.0.0/8'],
            'time_range': [
                _all_day_range(rate=100, burst=200, limit=1000),
                _specific_range('10:00', '11:00', rate=1, burst=1, limit=1, disabled=True),
            ],
        }

        matcher  = _build_matcher_with_rules([rule])
        tb_reg   = TokenBucketRegistry()
        fw_reg   = FixedWindowRegistry()

        # 10:30 would match the specific range, but it is disabled,
        # so the all-day default (generous limits) applies
        result = matcher.check('10.0.0.1', tb_reg, fw_reg, _now_us_10_30)
        self.assertTrue(result.is_allowed)

        # The composite key should reference index 0 (the all-day default)
        self.assertIn(':0', result.matched_key)

    def test_disabled_all_day_returns_none(self):
        """ A disabled all-day default means no rate limiting applies at all.
        """
        rule = {
            'cidr_list': ['10.0.0.0/8'],
            'time_range': [_all_day_range(disabled=True)],
        }

        matcher  = _build_matcher_with_rules([rule])
        tb_reg   = TokenBucketRegistry()
        fw_reg   = FixedWindowRegistry()

        result = matcher.check('10.0.0.1', tb_reg, fw_reg, _now_us_10_30)
        self.assertIsNone(result)

    def test_disabled_all_day_does_not_enforce_limits(self):
        """ Even if counters were previously exhausted, disabling the rule means requests pass through.
        """
        rule_dict = {
            'cidr_list': ['10.0.0.0/8'],
            'time_range': [_all_day_range(rate=1, burst=1, limit=1)],
        }

        matcher  = _build_matcher_with_rules([rule_dict])
        tb_reg   = TokenBucketRegistry()
        fw_reg   = FixedWindowRegistry()

        # Exhaust the limit while enabled
        matcher.check('10.0.0.1', tb_reg, fw_reg, _now_us_10_30)
        result_denied = matcher.check('10.0.0.1', tb_reg, fw_reg, _now_us_10_30)
        self.assertFalse(result_denied.is_allowed)

        # Now rebuild the matcher with the rule disabled
        rule_dict_disabled = {
            'cidr_list': ['10.0.0.0/8'],
            'time_range': [_all_day_range(rate=1, burst=1, limit=1, disabled=True)],
        }
        matcher.replace_all([rule_dict_disabled])

        # The request should pass through - no rate limiting
        result = matcher.check('10.0.0.1', tb_reg, fw_reg, _now_us_10_30)
        self.assertIsNone(result)

    def test_all_ranges_disabled_returns_none(self):
        """ When all ranges (all-day and specific) are disabled, no rate limiting applies.
        """
        rule = {
            'cidr_list': ['10.0.0.0/8'],
            'time_range': [
                _all_day_range(disabled=True),
                _specific_range('10:00', '11:00', disabled=True),
            ],
        }

        matcher  = _build_matcher_with_rules([rule])
        tb_reg   = TokenBucketRegistry()
        fw_reg   = FixedWindowRegistry()

        result = matcher.check('10.0.0.1', tb_reg, fw_reg, _now_us_10_30)
        self.assertIsNone(result)

# ################################################################################################################################
# ################################################################################################################################

class SlottedCheckCompositeKeyTestCase(unittest.TestCase):

    def test_composite_key_uses_time_range_index(self):
        """ The composite key includes the time range index so each range has independent counters.
        """
        rule = {
            'cidr_list': ['10.0.0.0/8'],
            'time_range': [
                _all_day_range(),
                _specific_range('10:00', '11:00'),
            ],
        }

        matcher  = _build_matcher_with_rules([rule])
        tb_reg   = TokenBucketRegistry()
        fw_reg   = FixedWindowRegistry()

        # 10:30 matches the specific range at index 1
        result = matcher.check('10.0.0.1', tb_reg, fw_reg, _now_us_10_30)
        self.assertIn(':1', result.matched_key)

        # 03:00 does not match the specific range, so the all-day default at index 0 applies
        result2 = matcher.check('10.0.0.1', tb_reg, fw_reg, _now_us_03_00)
        self.assertIn(':0', result2.matched_key)

    def test_different_time_ranges_have_separate_counters(self):
        """ Exhausting the counter for one time range does not affect another.
        """
        rule = {
            'cidr_list': ['10.0.0.0/8'],
            'time_range': [
                _all_day_range(rate=1000, burst=1000, limit=1000),
                _specific_range('10:00', '11:00', rate=1, burst=1, limit=1),
            ],
        }

        matcher  = _build_matcher_with_rules([rule])
        tb_reg   = TokenBucketRegistry()
        fw_reg   = FixedWindowRegistry()

        # Exhaust the specific range (index 1) at 10:30
        result1 = matcher.check('10.0.0.1', tb_reg, fw_reg, _now_us_10_30)
        self.assertTrue(result1.is_allowed)

        result2 = matcher.check('10.0.0.1', tb_reg, fw_reg, _now_us_10_30)
        self.assertFalse(result2.is_allowed)

        # The all-day default (index 0) at 03:00 should still be allowed
        result3 = matcher.check('10.0.0.1', tb_reg, fw_reg, _now_us_03_00)
        self.assertTrue(result3.is_allowed)

# ################################################################################################################################
# ################################################################################################################################

class SlottedCheckEmptyCIDRListTestCase(unittest.TestCase):

    def test_empty_cidr_matches_ipv4(self):
        """ An empty CIDR list means match all IPs - IPv4 addresses should match.
        """
        rule = {
            'cidr_list': [],
            'time_range': [_all_day_range(rate=100, burst=200, limit=1000)],
        }

        matcher  = _build_matcher_with_rules([rule])
        tb_reg   = TokenBucketRegistry()
        fw_reg   = FixedWindowRegistry()
        result   = matcher.check('192.168.1.1', tb_reg, fw_reg, _now_us_10_30)

        self.assertIsNotNone(result)
        self.assertTrue(result.is_allowed)

    def test_empty_cidr_matches_localhost(self):
        """ An empty CIDR list should match 127.0.0.1.
        """
        rule = {
            'cidr_list': [],
            'time_range': [_all_day_range(rate=100, burst=200, limit=1000)],
        }

        matcher  = _build_matcher_with_rules([rule])
        tb_reg   = TokenBucketRegistry()
        fw_reg   = FixedWindowRegistry()
        result   = matcher.check('127.0.0.1', tb_reg, fw_reg, _now_us_10_30)

        self.assertIsNotNone(result)
        self.assertTrue(result.is_allowed)

    def test_empty_cidr_disallowed(self):
        """ An empty CIDR list with disallowed=True should disallow all IPs.
        """
        rule = {
            'cidr_list': [],
            'time_range': [_all_day_range(disallowed=True)],
        }

        matcher  = _build_matcher_with_rules([rule])
        tb_reg   = TokenBucketRegistry()
        fw_reg   = FixedWindowRegistry()
        result   = matcher.check('10.0.0.1', tb_reg, fw_reg, _now_us_10_30)

        self.assertIsNotNone(result)
        self.assertTrue(result.is_disallowed)
        self.assertFalse(result.is_allowed)

    def test_empty_cidr_disabled(self):
        """ An empty CIDR list with disabled=True should skip rate limiting entirely.
        """
        rule = {
            'cidr_list': [],
            'time_range': [_all_day_range(disabled=True)],
        }

        matcher  = _build_matcher_with_rules([rule])
        tb_reg   = TokenBucketRegistry()
        fw_reg   = FixedWindowRegistry()
        result   = matcher.check('10.0.0.1', tb_reg, fw_reg, _now_us_10_30)

        self.assertIsNone(result)

    def test_empty_cidr_exhausts_limit(self):
        """ An empty CIDR list with a tight limit should deny after exhaustion.
        """
        rule = {
            'cidr_list': [],
            'time_range': [_all_day_range(rate=1, burst=1, limit=1)],
        }

        matcher  = _build_matcher_with_rules([rule])
        tb_reg   = TokenBucketRegistry()
        fw_reg   = FixedWindowRegistry()

        result1 = matcher.check('10.0.0.1', tb_reg, fw_reg, _now_us_10_30)
        self.assertTrue(result1.is_allowed)

        result2 = matcher.check('10.0.0.1', tb_reg, fw_reg, _now_us_10_30)
        self.assertFalse(result2.is_allowed)

    def test_empty_cidr_uses_synthetic_key(self):
        """ An empty CIDR list uses 0.0.0.0/0 as the matched key.
        """
        rule = {
            'cidr_list': [],
            'time_range': [_all_day_range()],
        }

        matcher  = _build_matcher_with_rules([rule])
        tb_reg   = TokenBucketRegistry()
        fw_reg   = FixedWindowRegistry()
        result   = matcher.check('192.168.1.1', tb_reg, fw_reg, _now_us_10_30)

        self.assertIn('0.0.0.0/0', result.matched_key)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    unittest.main()
