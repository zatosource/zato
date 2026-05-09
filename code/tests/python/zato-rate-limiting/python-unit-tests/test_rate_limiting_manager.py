# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.rate_limiting.manager import RateLimitingManager

# ################################################################################################################################
# ################################################################################################################################

def _make_rule_dicts(rate=10, burst=20, limit=100, limit_unit='minute', cidr='10.0.0.0/8'):
    return [{
        'cidr_list': [cidr],
        'time_range': [{
            'is_all_day': True,
            'disabled': False,
            'disallowed': False,
            'rate': rate,
            'burst': burst,
            'limit': limit,
            'limit_unit': limit_unit,
        }]
    }]

# ################################################################################################################################
# ################################################################################################################################

class RateLimitingManagerSetConfigTestCase(unittest.TestCase):

    def test_set_channel_config_registers_channel(self):
        manager = RateLimitingManager()
        manager.set_channel_config(1, _make_rule_dicts())
        self.assertTrue(manager.has_channel(1))

    def test_set_channel_config_replaces_existing(self):
        manager = RateLimitingManager()
        manager.set_channel_config(1, _make_rule_dicts(rate=5))
        manager.set_channel_config(1, _make_rule_dicts(rate=99))
        self.assertTrue(manager.has_channel(1))

    def test_has_channel_false_for_unknown(self):
        manager = RateLimitingManager()
        self.assertFalse(manager.has_channel(999))

    def test_remove_channel(self):
        manager = RateLimitingManager()
        manager.set_channel_config(1, _make_rule_dicts())
        manager.remove_channel(1)
        self.assertFalse(manager.has_channel(1))

    def test_remove_channel_unknown_is_noop(self):
        manager = RateLimitingManager()
        manager.remove_channel(999)

# ################################################################################################################################
# ################################################################################################################################

class RateLimitingManagerCheckAllowTestCase(unittest.TestCase):

    def test_check_returns_none_for_unknown_channel(self):
        manager = RateLimitingManager()
        result = manager.check(1, '10.0.0.1', 1_000_000)
        self.assertIsNone(result)

    def test_check_returns_none_for_no_matching_ip(self):
        manager = RateLimitingManager()
        manager.set_channel_config(1, _make_rule_dicts(cidr='192.168.0.0/16'))
        result = manager.check(1, '10.0.0.1', 1_000_000)
        self.assertIsNone(result)

    def test_check_allows_matching_ip(self):
        manager = RateLimitingManager()
        manager.set_channel_config(1, _make_rule_dicts())
        result = manager.check(1, '10.0.0.1', 1_000_000)
        self.assertIsNotNone(result)
        self.assertTrue(result.is_allowed)
        self.assertFalse(result.is_disallowed)

# ################################################################################################################################
# ################################################################################################################################

class RateLimitingManagerCheckDenyTestCase(unittest.TestCase):

    def test_check_denies_when_token_bucket_exhausted(self):
        manager = RateLimitingManager()
        manager.set_channel_config(1, _make_rule_dicts(rate=1, burst=1))

        now_us = 1_000_000

        result1 = manager.check(1, '10.0.0.1', now_us)
        self.assertTrue(result1.is_allowed)

        result2 = manager.check(1, '10.0.0.1', now_us)
        self.assertFalse(result2.is_allowed)
        self.assertFalse(result2.is_disallowed)
        self.assertGreater(result2.retry_after_us, 0)

# ################################################################################################################################
# ################################################################################################################################

class RateLimitingManagerCheckDisallowedTestCase(unittest.TestCase):

    def test_check_disallowed_returns_is_disallowed(self):
        rule_dicts = [{
            'cidr_list': ['10.0.0.0/8'],
            'time_range': [{
                'is_all_day': True,
                'disabled': False,
                'disallowed': True,
                'rate': 0,
                'burst': 0,
                'limit': 0,
                'limit_unit': 'minute',
            }]
        }]
        manager = RateLimitingManager()
        manager.set_channel_config(1, rule_dicts)
        result = manager.check(1, '10.0.0.1', 1_000_000)
        self.assertIsNotNone(result)
        self.assertTrue(result.is_disallowed)
        self.assertFalse(result.is_allowed)

# ################################################################################################################################
# ################################################################################################################################

class RateLimitingManagerReplaceConfigTestCase(unittest.TestCase):

    def test_replacing_config_resets_matcher(self):
        manager = RateLimitingManager()

        # First config allows 10.0.0.0/8
        manager.set_channel_config(1, _make_rule_dicts(cidr='10.0.0.0/8'))
        result = manager.check(1, '10.0.0.1', 1_000_000)
        self.assertIsNotNone(result)

        # Replace with config that only allows 192.168.0.0/16
        manager.set_channel_config(1, _make_rule_dicts(cidr='192.168.0.0/16'))
        result = manager.check(1, '10.0.0.1', 1_000_000)
        self.assertIsNone(result)

        result = manager.check(1, '192.168.1.1', 1_000_000)
        self.assertIsNotNone(result)
        self.assertTrue(result.is_allowed)

# ################################################################################################################################
# ################################################################################################################################

class RateLimitingManagerMultiChannelTestCase(unittest.TestCase):

    def test_channels_have_independent_counters(self):
        manager = RateLimitingManager()
        manager.set_channel_config(1, _make_rule_dicts(rate=1, burst=1))
        manager.set_channel_config(2, _make_rule_dicts(rate=1, burst=1))

        now_us = 1_000_000

        manager.check(1, '10.0.0.1', now_us, 'rest1:')
        result_ch1 = manager.check(1, '10.0.0.1', now_us, 'rest1:')
        self.assertFalse(result_ch1.is_allowed)

        result_ch2 = manager.check(2, '10.0.0.1', now_us, 'rest2:')
        self.assertTrue(result_ch2.is_allowed)

# ################################################################################################################################
# ################################################################################################################################

class SecDefSetConfigTestCase(unittest.TestCase):

    def test_set_sec_def_config_registers(self):
        manager = RateLimitingManager()
        manager.set_sec_def_config(1, _make_rule_dicts())
        self.assertTrue(manager.has_sec_def(1))

    def test_set_sec_def_config_replaces_existing(self):
        manager = RateLimitingManager()
        manager.set_sec_def_config(1, _make_rule_dicts(rate=5))
        manager.set_sec_def_config(1, _make_rule_dicts(rate=99))
        self.assertTrue(manager.has_sec_def(1))

    def test_has_sec_def_false_for_unknown(self):
        manager = RateLimitingManager()
        self.assertFalse(manager.has_sec_def(999))

    def test_remove_sec_def(self):
        manager = RateLimitingManager()
        manager.set_sec_def_config(1, _make_rule_dicts())
        manager.remove_sec_def(1)
        self.assertFalse(manager.has_sec_def(1))

    def test_remove_sec_def_unknown_is_noop(self):
        manager = RateLimitingManager()
        manager.remove_sec_def(999)

# ################################################################################################################################
# ################################################################################################################################

class SecDefCheckAllowTestCase(unittest.TestCase):

    def test_check_sec_def_returns_none_for_unknown(self):
        manager = RateLimitingManager()
        result = manager.check_sec_def(1, '10.0.0.1', 1_000_000)
        self.assertIsNone(result)

    def test_check_sec_def_returns_none_for_no_matching_ip(self):
        manager = RateLimitingManager()
        manager.set_sec_def_config(1, _make_rule_dicts(cidr='192.168.0.0/16'))
        result = manager.check_sec_def(1, '10.0.0.1', 1_000_000)
        self.assertIsNone(result)

    def test_check_sec_def_allows_matching_ip(self):
        manager = RateLimitingManager()
        manager.set_sec_def_config(1, _make_rule_dicts())
        result = manager.check_sec_def(1, '10.0.0.1', 1_000_000)
        self.assertIsNotNone(result)
        self.assertTrue(result.is_allowed)
        self.assertFalse(result.is_disallowed)

# ################################################################################################################################
# ################################################################################################################################

class SecDefCheckDenyTestCase(unittest.TestCase):

    def test_check_sec_def_denies_when_exhausted(self):
        manager = RateLimitingManager()
        manager.set_sec_def_config(1, _make_rule_dicts(rate=1, burst=1))

        now_us = 1_000_000

        result1 = manager.check_sec_def(1, '10.0.0.1', now_us)
        self.assertTrue(result1.is_allowed)

        result2 = manager.check_sec_def(1, '10.0.0.1', now_us)
        self.assertFalse(result2.is_allowed)
        self.assertFalse(result2.is_disallowed)
        self.assertGreater(result2.retry_after_us, 0)

# ################################################################################################################################
# ################################################################################################################################

class SecDefCheckDisallowedTestCase(unittest.TestCase):

    def test_check_sec_def_disallowed(self):
        rule_dicts = [{
            'cidr_list': ['10.0.0.0/8'],
            'time_range': [{
                'is_all_day': True,
                'disabled': False,
                'disallowed': True,
                'rate': 0,
                'burst': 0,
                'limit': 0,
                'limit_unit': 'minute',
            }]
        }]
        manager = RateLimitingManager()
        manager.set_sec_def_config(1, rule_dicts)
        result = manager.check_sec_def(1, '10.0.0.1', 1_000_000)
        self.assertIsNotNone(result)
        self.assertTrue(result.is_disallowed)
        self.assertFalse(result.is_allowed)

# ################################################################################################################################
# ################################################################################################################################

class SecDefIndependenceTestCase(unittest.TestCase):

    def test_channel_and_sec_def_are_independent(self):
        manager = RateLimitingManager()
        manager.set_channel_config(1, _make_rule_dicts(rate=1, burst=1))
        manager.set_sec_def_config(1, _make_rule_dicts(rate=1, burst=1))

        now_us = 1_000_000

        # Exhaust channel 1
        manager.check(1, '10.0.0.1', now_us, 'rest1:')
        result_ch = manager.check(1, '10.0.0.1', now_us, 'rest1:')
        self.assertFalse(result_ch.is_allowed)

        # Sec def 1 must still allow
        result_sd = manager.check_sec_def(1, '10.0.0.1', now_us, 'basic1:')
        self.assertTrue(result_sd.is_allowed)

    def test_sec_defs_have_independent_counters(self):
        manager = RateLimitingManager()
        manager.set_sec_def_config(1, _make_rule_dicts(rate=1, burst=1))
        manager.set_sec_def_config(2, _make_rule_dicts(rate=1, burst=1))

        now_us = 1_000_000

        manager.check_sec_def(1, '10.0.0.1', now_us, 'basic1:')
        result1 = manager.check_sec_def(1, '10.0.0.1', now_us, 'basic1:')
        self.assertFalse(result1.is_allowed)

        result2 = manager.check_sec_def(2, '10.0.0.1', now_us, 'basic2:')
        self.assertTrue(result2.is_allowed)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    unittest.main()
