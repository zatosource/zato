# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ipaddress
from unittest import main, TestCase

# Zato
from zato.common.rate_limiting.cidr import CIDREntry, CIDRMatch, CIDRMatcher, CIDRRule, parse_cidr, parse_client_ip
from zato.common.rate_limiting.common import RateLimitError
from zato.common.rate_limiting.fixed_window import FixedWindowConfig, FixedWindowRegistry
from zato.common.rate_limiting.token_bucket import TokenBucketConfig, TokenBucketRegistry

# ################################################################################################################################
# ################################################################################################################################

class ParseCIDRTestCase(TestCase):

    def test_parse_cidr_ipv4_host(self) -> 'None':
        """ A bare IPv4 address parses as a /32 host network.
        """
        result = parse_cidr('10.0.0.5')
        self.assertEqual(result, ipaddress.IPv4Network('10.0.0.5/32'))

# ################################################################################################################################

    def test_parse_cidr_ipv4_subnet(self) -> 'None':
        """ A standard IPv4 subnet parses correctly.
        """
        result = parse_cidr('10.0.0.0/24')
        self.assertEqual(result, ipaddress.IPv4Network('10.0.0.0/24'))

# ################################################################################################################################

    def test_parse_cidr_ipv4_non_strict(self) -> 'None':
        """ Host bits are silently masked when strict=False.
        """
        result = parse_cidr('10.0.0.5/24')
        self.assertEqual(result, ipaddress.IPv4Network('10.0.0.0/24'))

# ################################################################################################################################

    def test_parse_cidr_ipv6(self) -> 'None':
        """ A bare IPv6 address parses as a /128 host network.
        """
        result = parse_cidr('::1')
        self.assertEqual(result, ipaddress.IPv6Network('::1/128'))

# ################################################################################################################################

    def test_parse_cidr_invalid(self) -> 'None':
        """ An invalid string raises RateLimitError.
        """
        with self.assertRaises(RateLimitError):
            _ = parse_cidr('not-an-ip')

# ################################################################################################################################
# ################################################################################################################################

class ParseClientIPTestCase(TestCase):

    def test_parse_client_ip_ipv4(self) -> 'None':
        """ A valid IPv4 address parses correctly.
        """
        result = parse_client_ip('10.0.0.5')
        self.assertEqual(result, ipaddress.IPv4Address('10.0.0.5'))

# ################################################################################################################################

    def test_parse_client_ip_ipv6(self) -> 'None':
        """ A valid IPv6 address parses correctly.
        """
        result = parse_client_ip('::1')
        self.assertEqual(result, ipaddress.IPv6Address('::1'))

# ################################################################################################################################

    def test_parse_client_ip_invalid(self) -> 'None':
        """ An invalid string raises RateLimitError.
        """
        with self.assertRaises(RateLimitError):
            _ = parse_client_ip('not-a-valid-address')

# ################################################################################################################################
# ################################################################################################################################

class CIDREntryTestCase(TestCase):

    def test_cidr_entry_from_string_ipv4(self) -> 'None':
        """ An IPv4 CIDR string produces the correct normalised key.
        """
        entry = CIDREntry.from_string('10.0.0.0/24')
        self.assertEqual(entry.key, '10.0.0.0/24')
        self.assertEqual(entry.network, ipaddress.IPv4Network('10.0.0.0/24'))

# ################################################################################################################################

    def test_cidr_entry_from_string_ipv6(self) -> 'None':
        """ An IPv6 address produces a /128 key.
        """
        entry = CIDREntry.from_string('::1')
        self.assertEqual(entry.key, '::1/128')
        self.assertEqual(entry.network, ipaddress.IPv6Network('::1/128'))

# ################################################################################################################################

    def test_cidr_entry_from_string_invalid(self) -> 'None':
        """ An invalid string raises RateLimitError.
        """
        with self.assertRaises(RateLimitError):
            _ = CIDREntry.from_string('not-a-cidr')

# ################################################################################################################################
# ################################################################################################################################

class CIDRRuleTestCase(TestCase):

    def setUp(self) -> 'None':
        self.token_bucket_config = TokenBucketConfig.from_parts(rate=100, burst_allowed=10)
        self.fixed_window_config = FixedWindowConfig.from_parts(limit=500, window_unit='minute')

# ################################################################################################################################

    def test_cidr_rule_match_found(self) -> 'None':
        """ An address inside one of the blocks returns the matching entry.
        """
        rule  = CIDRRule.from_parts(['10.0.0.0/24'], self.token_bucket_config, self.fixed_window_config)
        match = rule.match(ipaddress.IPv4Address('10.0.0.5'))
        self.assertIsNotNone(match)
        self.assertEqual(match.key, '10.0.0.0/24') # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################

    def test_cidr_rule_match_not_found(self) -> 'None':
        """ An address outside all blocks returns None.
        """
        rule  = CIDRRule.from_parts(['10.0.0.0/24'], self.token_bucket_config, self.fixed_window_config)
        match = rule.match(ipaddress.IPv4Address('192.168.1.1'))
        self.assertIsNone(match)

# ################################################################################################################################

    def test_cidr_rule_match_returns_correct_entry(self) -> 'None':
        """ When a rule has three blocks, the entry for the matching block is returned.
        """
        rule  = CIDRRule.from_parts(['10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16'], self.token_bucket_config, self.fixed_window_config)
        match = rule.match(ipaddress.IPv4Address('172.16.5.1'))
        self.assertIsNotNone(match)
        self.assertEqual(match.key, '172.16.0.0/12') # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################

    def test_cidr_rule_match_skips_wrong_family(self) -> 'None':
        """ An IPv4 address does not crash against an IPv6-only rule, returns None.
        """
        rule  = CIDRRule.from_parts(['fd00::/16'], self.token_bucket_config, self.fixed_window_config)
        match = rule.match(ipaddress.IPv4Address('10.0.0.1'))
        self.assertIsNone(match)

# ################################################################################################################################

    def test_cidr_rule_stores_both_configs(self) -> 'None':
        """ Both the token bucket and fixed window configs are accessible on the rule.
        """
        rule = CIDRRule.from_parts(['10.0.0.0/8'], self.token_bucket_config, self.fixed_window_config)
        self.assertIs(rule.token_bucket_config, self.token_bucket_config)
        self.assertIs(rule.fixed_window_config, self.fixed_window_config)

# ################################################################################################################################
# ################################################################################################################################

class CIDRMatchTestCase(TestCase):

    def test_cidr_match_key_is_entry_key(self) -> 'None':
        """ CIDRMatch.key returns the entry's key.
        """
        entry = CIDREntry.from_string('10.0.0.0/24')

        match = CIDRMatch()
        match.rule  = CIDRRule.from_parts(
            ['10.0.0.0/24'],
            TokenBucketConfig.from_parts(rate=10, burst_allowed=5),
            FixedWindowConfig.from_parts(limit=100, window_unit='minute'),
        )
        match.entry = entry

        self.assertEqual(match.key, '10.0.0.0/24')

# ################################################################################################################################
# ################################################################################################################################

class CIDRMatcherAddRuleTestCase(TestCase):

    def setUp(self) -> 'None':
        self.token_bucket_config = TokenBucketConfig.from_parts(rate=100, burst_allowed=10)
        self.fixed_window_config = FixedWindowConfig.from_parts(limit=500, window_unit='minute')

# ################################################################################################################################

    def test_add_rule_increases_length(self) -> 'None':
        """ Adding a rule increases the internal list size.
        """
        matcher = CIDRMatcher()
        matcher.add_rule(['10.0.0.0/8'], self.token_bucket_config, self.fixed_window_config)
        self.assertEqual(len(matcher._rules), 1)

# ################################################################################################################################

    def test_add_multiple_rules(self) -> 'None':
        """ Three rules added, list has three entries.
        """
        matcher = CIDRMatcher()
        matcher.add_rule(['10.0.0.0/8'], self.token_bucket_config, self.fixed_window_config)
        matcher.add_rule(['172.16.0.0/12'], self.token_bucket_config, self.fixed_window_config)
        matcher.add_rule(['192.168.0.0/16'], self.token_bucket_config, self.fixed_window_config)
        self.assertEqual(len(matcher._rules), 3)

# ################################################################################################################################
# ################################################################################################################################

class CIDRMatcherResolveTestCase(TestCase):

    def setUp(self) -> 'None':
        self.token_bucket_config = TokenBucketConfig.from_parts(rate=100, burst_allowed=10)
        self.fixed_window_config = FixedWindowConfig.from_parts(limit=500, window_unit='minute')

# ################################################################################################################################

    def test_resolve_single_rule_match(self) -> 'None':
        """ An IP inside the rule's blocks resolves with the correct key.
        """
        matcher = CIDRMatcher()
        matcher.add_rule(['10.0.0.0/8'], self.token_bucket_config, self.fixed_window_config)

        result = matcher.resolve('10.0.0.5')
        self.assertIsNotNone(result)
        self.assertEqual(result.key, '10.0.0.0/8') # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################

    def test_resolve_no_match(self) -> 'None':
        """ An IP outside all rules returns None.
        """
        matcher = CIDRMatcher()
        matcher.add_rule(['10.0.0.0/8'], self.token_bucket_config, self.fixed_window_config)

        result = matcher.resolve('192.168.1.1')
        self.assertIsNone(result)

# ################################################################################################################################

    def test_resolve_returns_correct_entry_key(self) -> 'None':
        """ When a rule has multiple blocks, the key of the specific matching block is returned.
        """
        matcher = CIDRMatcher()
        matcher.add_rule(['10.0.0.0/8', '172.16.0.0/12'], self.token_bucket_config, self.fixed_window_config)

        result = matcher.resolve('172.16.5.1')
        self.assertIsNotNone(result)
        self.assertEqual(result.key, '172.16.0.0/12') # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################
# ################################################################################################################################

class CIDRMatcherResolveOrderTestCase(TestCase):

    def test_resolve_first_match_wins(self) -> 'None':
        """ Two overlapping rules - the first one in list order wins.
        """
        config_a = TokenBucketConfig.from_parts(rate=1000, burst_allowed=100)
        config_b = TokenBucketConfig.from_parts(rate=50, burst_allowed=5)
        fixed_window_config = FixedWindowConfig.from_parts(limit=500, window_unit='minute')

        matcher = CIDRMatcher()
        matcher.add_rule(['10.0.0.0/8'], config_a, fixed_window_config)
        matcher.add_rule(['10.0.0.0/24'], config_b, fixed_window_config)

        result = matcher.resolve('10.0.0.5')
        self.assertIsNotNone(result)
        self.assertEqual(result.key, '10.0.0.0/8') # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################

    def test_resolve_same_rules_reordered_different_result(self) -> 'None':
        """ Same two rules in different order produce different matches for the same IP.
        """
        config_a = TokenBucketConfig.from_parts(rate=1000, burst_allowed=100)
        config_b = TokenBucketConfig.from_parts(rate=50, burst_allowed=5)
        fixed_window_config = FixedWindowConfig.from_parts(limit=500, window_unit='minute')

        # Matcher 1: broad rule first, narrow rule second
        matcher_1 = CIDRMatcher()
        matcher_1.add_rule(['10.0.0.0/8'], config_a, fixed_window_config)
        matcher_1.add_rule(['10.0.0.0/24'], config_b, fixed_window_config)

        # Matcher 2: narrow rule first, broad rule second
        matcher_2 = CIDRMatcher()
        matcher_2.add_rule(['10.0.0.0/24'], config_b, fixed_window_config)
        matcher_2.add_rule(['10.0.0.0/8'], config_a, fixed_window_config)

        result_1 = matcher_1.resolve('10.0.0.5')
        result_2 = matcher_2.resolve('10.0.0.5')

        self.assertIsNotNone(result_1)
        self.assertIsNotNone(result_2)

        # Matcher 1 hits the /8, matcher 2 hits the /24
        self.assertEqual(result_1.key, '10.0.0.0/8')   # pyright: ignore[reportOptionalMemberAccess]
        self.assertEqual(result_2.key, '10.0.0.0/24')  # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################

    def test_resolve_catch_all_last(self) -> 'None':
        """ A specific rule first and 0.0.0.0/0 last - specific IPs hit the first rule, others hit the catch-all.
        """
        token_bucket_config = TokenBucketConfig.from_parts(rate=100, burst_allowed=10)
        fixed_window_config = FixedWindowConfig.from_parts(limit=500, window_unit='minute')

        matcher = CIDRMatcher()
        matcher.add_rule(['10.0.0.0/8'], token_bucket_config, fixed_window_config)
        matcher.add_rule(['0.0.0.0/0'], token_bucket_config, fixed_window_config)

        # Internal IP hits the specific rule
        result_internal = matcher.resolve('10.0.0.5')
        self.assertIsNotNone(result_internal)
        self.assertEqual(result_internal.key, '10.0.0.0/8') # pyright: ignore[reportOptionalMemberAccess]

        # External IP falls through to the catch-all
        result_external = matcher.resolve('8.8.8.8')
        self.assertIsNotNone(result_external)
        self.assertEqual(result_external.key, '0.0.0.0/0') # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################

    def test_resolve_catch_all_first_shadows_everything(self) -> 'None':
        """ 0.0.0.0/0 added first shadows all subsequent rules.
        """
        token_bucket_config = TokenBucketConfig.from_parts(rate=100, burst_allowed=10)
        fixed_window_config = FixedWindowConfig.from_parts(limit=500, window_unit='minute')

        matcher = CIDRMatcher()
        matcher.add_rule(['0.0.0.0/0'], token_bucket_config, fixed_window_config)
        matcher.add_rule(['10.0.0.0/8'], token_bucket_config, fixed_window_config)

        # Even an internal IP matches the catch-all because it comes first
        result = matcher.resolve('10.0.0.5')
        self.assertIsNotNone(result)
        self.assertEqual(result.key, '0.0.0.0/0') # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################
# ################################################################################################################################

class CIDRMatcherResolveIPv6TestCase(TestCase):

    def setUp(self) -> 'None':
        self.token_bucket_config = TokenBucketConfig.from_parts(rate=100, burst_allowed=10)
        self.fixed_window_config = FixedWindowConfig.from_parts(limit=500, window_unit='minute')

# ################################################################################################################################

    def test_resolve_ipv6_match(self) -> 'None':
        """ An IPv6 loopback matches a rule with ::1/128.
        """
        matcher = CIDRMatcher()
        matcher.add_rule(['::1/128'], self.token_bucket_config, self.fixed_window_config)

        result = matcher.resolve('::1')
        self.assertIsNotNone(result)
        self.assertEqual(result.key, '::1/128') # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################

    def test_resolve_ipv6_subnet(self) -> 'None':
        """ An IPv6 address matches its containing subnet.
        """
        matcher = CIDRMatcher()
        matcher.add_rule(['fd00::/16'], self.token_bucket_config, self.fixed_window_config)

        result = matcher.resolve('fd00::5')
        self.assertIsNotNone(result)
        self.assertEqual(result.key, 'fd00::/16') # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################

    def test_resolve_ipv4_does_not_match_ipv6_rule(self) -> 'None':
        """ An IPv4 address does not match an IPv6-only rule.
        """
        matcher = CIDRMatcher()
        matcher.add_rule(['fd00::/16'], self.token_bucket_config, self.fixed_window_config)

        result = matcher.resolve('10.0.0.5')
        self.assertIsNone(result)

# ################################################################################################################################

    def test_resolve_mixed_rules(self) -> 'None':
        """ IPv4 and IPv6 rules coexist, each resolves correctly.
        """
        matcher = CIDRMatcher()
        matcher.add_rule(['10.0.0.0/8'], self.token_bucket_config, self.fixed_window_config)
        matcher.add_rule(['fd00::/16'], self.token_bucket_config, self.fixed_window_config)

        result_v4 = matcher.resolve('10.0.0.5')
        self.assertIsNotNone(result_v4)
        self.assertEqual(result_v4.key, '10.0.0.0/8') # pyright: ignore[reportOptionalMemberAccess]

        result_v6 = matcher.resolve('fd00::5')
        self.assertIsNotNone(result_v6)
        self.assertEqual(result_v6.key, 'fd00::/16') # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################
# ################################################################################################################################

class CIDRMatcherHousekeepingTestCase(TestCase):

    def setUp(self) -> 'None':
        self.token_bucket_config = TokenBucketConfig.from_parts(rate=100, burst_allowed=10)
        self.fixed_window_config = FixedWindowConfig.from_parts(limit=500, window_unit='minute')

# ################################################################################################################################

    def test_cidr_matcher_len_and_is_empty(self) -> 'None':
        """ len and is_empty reflect the number of rules.
        """
        matcher = CIDRMatcher()
        self.assertEqual(len(matcher), 0)
        self.assertTrue(matcher.is_empty())

        matcher.add_rule(['10.0.0.0/8'], self.token_bucket_config, self.fixed_window_config)
        self.assertEqual(len(matcher), 1)
        self.assertFalse(matcher.is_empty())

# ################################################################################################################################

    def test_cidr_matcher_remove_rule(self) -> 'None':
        """ Removing a rule by index shrinks the list.
        """
        matcher = CIDRMatcher()
        matcher.add_rule(['10.0.0.0/8'], self.token_bucket_config, self.fixed_window_config)
        matcher.add_rule(['172.16.0.0/12'], self.token_bucket_config, self.fixed_window_config)
        self.assertEqual(len(matcher), 2)

        matcher.remove_rule(0)
        self.assertEqual(len(matcher), 1)

        # The remaining rule is the second one
        result = matcher.resolve('172.16.5.1')
        self.assertIsNotNone(result)
        self.assertEqual(result.key, '172.16.0.0/12') # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################

    def test_cidr_matcher_remove_rule_out_of_bounds(self) -> 'None':
        """ An out-of-bounds index raises IndexError.
        """
        matcher = CIDRMatcher()
        with self.assertRaises(IndexError):
            matcher.remove_rule(0)

# ################################################################################################################################

    def test_cidr_matcher_clear(self) -> 'None':
        """ clear removes all rules.
        """
        matcher = CIDRMatcher()
        matcher.add_rule(['10.0.0.0/8'], self.token_bucket_config, self.fixed_window_config)
        matcher.add_rule(['172.16.0.0/12'], self.token_bucket_config, self.fixed_window_config)
        self.assertEqual(len(matcher), 2)

        matcher.clear()
        self.assertEqual(len(matcher), 0)
        self.assertTrue(matcher.is_empty())

# ################################################################################################################################

    def test_cidr_matcher_replace_all(self) -> 'None':
        """ replace_all swaps the entire rule list atomically.
        """
        matcher = CIDRMatcher()
        matcher.add_rule(['10.0.0.0/8'], self.token_bucket_config, self.fixed_window_config)
        self.assertEqual(len(matcher), 1)

        # Replace with two new rules
        matcher.replace_all([
            (['172.16.0.0/12'], self.token_bucket_config, self.fixed_window_config),
            (['192.168.0.0/16'], self.token_bucket_config, self.fixed_window_config),
        ])
        self.assertEqual(len(matcher), 2)

        # The old rule no longer matches
        self.assertIsNone(matcher.resolve('10.0.0.5'))

        # The new rules do
        result = matcher.resolve('172.16.5.1')
        self.assertIsNotNone(result)
        self.assertEqual(result.key, '172.16.0.0/12') # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################
# ################################################################################################################################

class CIDRMatcherCheckAllowTestCase(TestCase):

    def setUp(self) -> 'None':
        self.token_bucket_config  = TokenBucketConfig.from_parts(rate=100, burst_allowed=10)
        self.fixed_window_config  = FixedWindowConfig.from_parts(limit=500, window_unit='minute')
        self.token_bucket_registry = TokenBucketRegistry()
        self.fixed_window_registry = FixedWindowRegistry()

        self.matcher = CIDRMatcher()
        self.matcher.add_rule(['10.0.0.0/8'], self.token_bucket_config, self.fixed_window_config)

# ################################################################################################################################

    def test_check_both_limiters_allow(self) -> 'None':
        """ Both limiters allow, result is allowed with the correct matched key.
        """
        now_us = 1_700_000_000_000_000

        result = self.matcher.check('10.0.0.5', self.token_bucket_registry, self.fixed_window_registry, now_us)
        self.assertIsNotNone(result)
        self.assertTrue(result.is_allowed)          # pyright: ignore[reportOptionalMemberAccess]
        self.assertEqual(result.matched_key, '10.0.0.0/8') # pyright: ignore[reportOptionalMemberAccess]
        self.assertTrue(result.token_bucket_result.is_allowed)  # pyright: ignore[reportOptionalMemberAccess]
        self.assertTrue(result.fixed_window_result.is_allowed)  # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################

    def test_check_no_matching_rule(self) -> 'None':
        """ An IP outside all rules returns None.
        """
        now_us = 1_700_000_000_000_000

        result = self.matcher.check('192.168.1.1', self.token_bucket_registry, self.fixed_window_registry, now_us)
        self.assertIsNone(result)

# ################################################################################################################################

    def test_check_invalid_ip_raises(self) -> 'None':
        """ An invalid IP string raises RateLimitError.
        """
        now_us = 1_700_000_000_000_000

        with self.assertRaises(RateLimitError):
            _ = self.matcher.check('not-a-valid-address', self.token_bucket_registry, self.fixed_window_registry, now_us)

# ################################################################################################################################
# ################################################################################################################################

class CIDRMatcherCheckDenyTestCase(TestCase):

    def setUp(self) -> 'None':
        self.now_us = 1_700_000_000_000_000

# ################################################################################################################################

    def test_check_token_bucket_denies(self) -> 'None':
        """ Token bucket denies (burst exhausted), fixed window allows, result is denied.
        """
        token_bucket_config    = TokenBucketConfig.from_parts(rate=1, burst_allowed=1)
        fixed_window_config    = FixedWindowConfig.from_parts(limit=100, window_unit='minute')
        token_bucket_registry  = TokenBucketRegistry()
        fixed_window_registry  = FixedWindowRegistry()

        matcher = CIDRMatcher()
        matcher.add_rule(['10.0.0.0/8'], token_bucket_config, fixed_window_config)

        # First call consumes the single token ..
        result_1 = matcher.check('10.0.0.5', token_bucket_registry, fixed_window_registry, self.now_us)
        self.assertIsNotNone(result_1)
        self.assertTrue(result_1.is_allowed) # pyright: ignore[reportOptionalMemberAccess]

        # .. second call at the same instant is denied by the token bucket.
        result_2 = matcher.check('10.0.0.5', token_bucket_registry, fixed_window_registry, self.now_us)
        self.assertIsNotNone(result_2)
        self.assertFalse(result_2.is_allowed)                        # pyright: ignore[reportOptionalMemberAccess]
        self.assertFalse(result_2.token_bucket_result.is_allowed)    # pyright: ignore[reportOptionalMemberAccess]
        self.assertTrue(result_2.fixed_window_result.is_allowed)     # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################

    def test_check_fixed_window_denies(self) -> 'None':
        """ Fixed window denies (limit exhausted), token bucket allows, result is denied.
        """
        token_bucket_config    = TokenBucketConfig.from_parts(rate=100, burst_allowed=100)
        fixed_window_config    = FixedWindowConfig.from_parts(limit=1, window_unit='minute')
        token_bucket_registry  = TokenBucketRegistry()
        fixed_window_registry  = FixedWindowRegistry()

        matcher = CIDRMatcher()
        matcher.add_rule(['10.0.0.0/8'], token_bucket_config, fixed_window_config)

        # First call fills the single-request window ..
        result_1 = matcher.check('10.0.0.5', token_bucket_registry, fixed_window_registry, self.now_us)
        self.assertIsNotNone(result_1)
        self.assertTrue(result_1.is_allowed) # pyright: ignore[reportOptionalMemberAccess]

        # .. second call is denied by the fixed window.
        result_2 = matcher.check('10.0.0.5', token_bucket_registry, fixed_window_registry, self.now_us)
        self.assertIsNotNone(result_2)
        self.assertFalse(result_2.is_allowed)                        # pyright: ignore[reportOptionalMemberAccess]
        self.assertTrue(result_2.token_bucket_result.is_allowed)     # pyright: ignore[reportOptionalMemberAccess]
        self.assertFalse(result_2.fixed_window_result.is_allowed)    # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################

    def test_check_both_deny(self) -> 'None':
        """ Both limiters deny, result is denied, both sub-results available.
        """
        token_bucket_config    = TokenBucketConfig.from_parts(rate=1, burst_allowed=1)
        fixed_window_config    = FixedWindowConfig.from_parts(limit=1, window_unit='minute')
        token_bucket_registry  = TokenBucketRegistry()
        fixed_window_registry  = FixedWindowRegistry()

        matcher = CIDRMatcher()
        matcher.add_rule(['10.0.0.0/8'], token_bucket_config, fixed_window_config)

        # First call consumes both limits ..
        result_1 = matcher.check('10.0.0.5', token_bucket_registry, fixed_window_registry, self.now_us)
        self.assertIsNotNone(result_1)
        self.assertTrue(result_1.is_allowed) # pyright: ignore[reportOptionalMemberAccess]

        # .. second call is denied by both.
        result_2 = matcher.check('10.0.0.5', token_bucket_registry, fixed_window_registry, self.now_us)
        self.assertIsNotNone(result_2)
        self.assertFalse(result_2.is_allowed)                        # pyright: ignore[reportOptionalMemberAccess]
        self.assertFalse(result_2.token_bucket_result.is_allowed)    # pyright: ignore[reportOptionalMemberAccess]
        self.assertFalse(result_2.fixed_window_result.is_allowed)    # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################
# ################################################################################################################################

class CIDRMatcherIntegrationTestCase(TestCase):

    def test_internal_vs_external_different_limits(self) -> 'None':
        """ Internal IPs get a generous limit, external IPs get a tight limit.
        """
        now_us = 1_700_000_000_000_000

        token_bucket_registry  = TokenBucketRegistry()
        fixed_window_registry  = FixedWindowRegistry()

        matcher = CIDRMatcher()

        # Internal: 100 tokens burst, 1000/min
        matcher.add_rule(
            ['10.0.0.0/8'],
            TokenBucketConfig.from_parts(rate=100, burst_allowed=100),
            FixedWindowConfig.from_parts(limit=1000, window_unit='minute'),
        )

        # External: 2 tokens burst, 100/min
        matcher.add_rule(
            ['0.0.0.0/0'],
            TokenBucketConfig.from_parts(rate=2, burst_allowed=2),
            FixedWindowConfig.from_parts(limit=100, window_unit='minute'),
        )

        # Internal IP gets through easily
        result = matcher.check('10.0.0.5', token_bucket_registry, fixed_window_registry, now_us)
        self.assertIsNotNone(result)
        self.assertTrue(result.is_allowed) # pyright: ignore[reportOptionalMemberAccess]

        # External IP: first two calls succeed, third is denied by the token bucket
        result_1 = matcher.check('8.8.8.8', token_bucket_registry, fixed_window_registry, now_us)
        result_2 = matcher.check('8.8.8.8', token_bucket_registry, fixed_window_registry, now_us)
        result_3 = matcher.check('8.8.8.8', token_bucket_registry, fixed_window_registry, now_us)

        self.assertIsNotNone(result_1)
        self.assertIsNotNone(result_2)
        self.assertIsNotNone(result_3)
        self.assertTrue(result_1.is_allowed)  # pyright: ignore[reportOptionalMemberAccess]
        self.assertTrue(result_2.is_allowed)  # pyright: ignore[reportOptionalMemberAccess]
        self.assertFalse(result_3.is_allowed) # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################

    def test_two_ips_same_subnet_share_counter(self) -> 'None':
        """ Two different IPs in the same /24 share the same rate limit counter.
        """
        now_us = 1_700_000_000_000_000

        token_bucket_registry  = TokenBucketRegistry()
        fixed_window_registry  = FixedWindowRegistry()

        matcher = CIDRMatcher()
        matcher.add_rule(
            ['10.0.0.0/24'],
            TokenBucketConfig.from_parts(rate=1, burst_allowed=1),
            FixedWindowConfig.from_parts(limit=100, window_unit='minute'),
        )

        # First IP consumes the single token ..
        result_1 = matcher.check('10.0.0.1', token_bucket_registry, fixed_window_registry, now_us)
        self.assertIsNotNone(result_1)
        self.assertTrue(result_1.is_allowed) # pyright: ignore[reportOptionalMemberAccess]

        # .. second IP in the same /24 shares the counter, so it is denied.
        result_2 = matcher.check('10.0.0.2', token_bucket_registry, fixed_window_registry, now_us)
        self.assertIsNotNone(result_2)
        self.assertFalse(result_2.is_allowed) # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################

    def test_fallback_rule_catches_unmatched(self) -> 'None':
        """ 0.0.0.0/0 as the last rule catches IPs not covered by earlier rules.
        """
        now_us = 1_700_000_000_000_000

        token_bucket_registry  = TokenBucketRegistry()
        fixed_window_registry  = FixedWindowRegistry()

        matcher = CIDRMatcher()
        matcher.add_rule(
            ['10.0.0.0/8'],
            TokenBucketConfig.from_parts(rate=100, burst_allowed=100),
            FixedWindowConfig.from_parts(limit=1000, window_unit='minute'),
        )
        matcher.add_rule(
            ['0.0.0.0/0'],
            TokenBucketConfig.from_parts(rate=10, burst_allowed=10),
            FixedWindowConfig.from_parts(limit=100, window_unit='minute'),
        )

        # An unmatched IP hits the catch-all
        result = matcher.check('203.0.113.50', token_bucket_registry, fixed_window_registry, now_us)
        self.assertIsNotNone(result)
        self.assertTrue(result.is_allowed)                  # pyright: ignore[reportOptionalMemberAccess]
        self.assertEqual(result.matched_key, '0.0.0.0/0')  # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################

    def test_rule_order_determines_rate_limit(self) -> 'None':
        """ Same rules reordered: one matcher allows, the other denies the same IP.
        """
        now_us = 1_700_000_000_000_000

        generous_token_bucket = TokenBucketConfig.from_parts(rate=100, burst_allowed=100)
        generous_fixed_window = FixedWindowConfig.from_parts(limit=1000, window_unit='minute')
        tight_token_bucket    = TokenBucketConfig.from_parts(rate=1, burst_allowed=1)
        tight_fixed_window    = FixedWindowConfig.from_parts(limit=1, window_unit='minute')

        # Matcher 1: generous rule first (10.0.0.0/8), tight catch-all second
        matcher_1              = CIDRMatcher()
        token_bucket_registry_1 = TokenBucketRegistry()
        fixed_window_registry_1 = FixedWindowRegistry()

        matcher_1.add_rule(['10.0.0.0/8'], generous_token_bucket, generous_fixed_window)
        matcher_1.add_rule(['0.0.0.0/0'], tight_token_bucket, tight_fixed_window)

        # Matcher 2: tight catch-all first, generous rule second (never reached for 10.x)
        matcher_2              = CIDRMatcher()
        token_bucket_registry_2 = TokenBucketRegistry()
        fixed_window_registry_2 = FixedWindowRegistry()

        matcher_2.add_rule(['0.0.0.0/0'], tight_token_bucket, tight_fixed_window)
        matcher_2.add_rule(['10.0.0.0/8'], generous_token_bucket, generous_fixed_window)

        # First call succeeds on both
        result_1a = matcher_1.check('10.0.0.5', token_bucket_registry_1, fixed_window_registry_1, now_us)
        result_2a = matcher_2.check('10.0.0.5', token_bucket_registry_2, fixed_window_registry_2, now_us)

        self.assertIsNotNone(result_1a)
        self.assertIsNotNone(result_2a)
        self.assertTrue(result_1a.is_allowed) # pyright: ignore[reportOptionalMemberAccess]
        self.assertTrue(result_2a.is_allowed) # pyright: ignore[reportOptionalMemberAccess]

        # Second call: matcher 1 still allowed (generous), matcher 2 denied (tight catch-all)
        result_1b = matcher_1.check('10.0.0.5', token_bucket_registry_1, fixed_window_registry_1, now_us)
        result_2b = matcher_2.check('10.0.0.5', token_bucket_registry_2, fixed_window_registry_2, now_us)

        self.assertIsNotNone(result_1b)
        self.assertIsNotNone(result_2b)
        self.assertTrue(result_1b.is_allowed)  # pyright: ignore[reportOptionalMemberAccess]
        self.assertFalse(result_2b.is_allowed) # pyright: ignore[reportOptionalMemberAccess]

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()
