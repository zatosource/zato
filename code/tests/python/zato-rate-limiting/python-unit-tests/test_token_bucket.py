# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import datetime
from unittest import main, TestCase

# Zato
from zato.common.rate_limiting.common import Microseconds_Per_Second
from zato.common.rate_limiting.token_bucket import CheckResult, TokenBucketConfig, TokenBucketRegistry

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

class CheckResultTestCase(TestCase):

    def test_check_result_allowed(self) -> 'None':
        """ An allowed result reports is_allowed True and retry_after_us 0.
        """
        result = CheckResult()
        result.is_allowed       = True
        result.tokens_remaining = 5
        result.retry_after_us   = 0

        self.assertTrue(result.is_allowed)
        self.assertEqual(result.retry_after_us, 0)

# ################################################################################################################################

    def test_check_result_denied(self) -> 'None':
        """ A denied result reports is_allowed False and retry_after_us > 0.
        """
        result = CheckResult()
        result.is_allowed       = False
        result.tokens_remaining = 0
        result.retry_after_us   = 1234

        self.assertFalse(result.is_allowed)
        self.assertEqual(result.retry_after_us, 1234)

# ################################################################################################################################
# ################################################################################################################################

class TokenBucketConfigTestCase(TestCase):

    def test_token_bucket_config_from_parts(self) -> 'None':
        """ from_parts stores rate and burst correctly.
        """
        config = TokenBucketConfig.from_parts(100, 5)
        self.assertEqual(config.rate, 100)
        self.assertEqual(config.burst_allowed, 5)

# ################################################################################################################################
# ################################################################################################################################

class TokenBucketRegistryTestCase(TestCase):

    def setUp(self) -> 'None':
        self.now_us = _to_us(2023, 11, 14, 22, 13, 20)

    def test_allow_exactly_burst_then_deny(self) -> 'None':
        """ Exactly burst_allowed requests pass, then the next is denied.
        """
        registry = TokenBucketRegistry()
        config   = TokenBucketConfig.from_parts(100, 5)

        for idx in range(5):
            result = registry.check_inner('test_key', config, self.now_us)
            self.assertTrue(result.is_allowed, f'Request {idx} of 5 must be allowed')
            self.assertEqual(result.tokens_remaining, 4 - idx)

        denied = registry.check_inner('test_key', config, self.now_us)
        self.assertFalse(denied.is_allowed)
        self.assertEqual(denied.tokens_remaining, 0)

# ################################################################################################################################

    def test_retry_after_is_positive_on_deny(self) -> 'None':
        """ A denied request has a positive retry_after_us.
        """
        registry = TokenBucketRegistry()
        config   = TokenBucketConfig.from_parts(1, 1)

        _ = registry.check_inner('test_key', config, self.now_us)
        denied = registry.check_inner('test_key', config, self.now_us)
        self.assertFalse(denied.is_allowed)
        self.assertGreater(denied.retry_after_us, 0)

# ################################################################################################################################

    def test_refill_restores_tokens(self) -> 'None':
        """ After enough time passes, tokens refill and requests are allowed again.
        """
        registry = TokenBucketRegistry()
        config   = TokenBucketConfig.from_parts(10, 1)

        _ = registry.check_inner('test_key', config, self.now_us)
        denied = registry.check_inner('test_key', config, self.now_us)
        self.assertFalse(denied.is_allowed)

        later = self.now_us + 200_000
        restored = registry.check_inner('test_key', config, later)
        self.assertTrue(restored.is_allowed)

# ################################################################################################################################

    def test_separate_keys_are_independent(self) -> 'None':
        """ Exhausting one key does not affect another.
        """
        registry = TokenBucketRegistry()
        config   = TokenBucketConfig.from_parts(1, 1)

        _ = registry.check_inner('key_a', config, self.now_us)
        denied = registry.check_inner('key_a', config, self.now_us)
        self.assertFalse(denied.is_allowed)

        other = registry.check_inner('key_b', config, self.now_us)
        self.assertTrue(other.is_allowed)

# ################################################################################################################################

    def test_burst_cap_after_long_idle(self) -> 'None':
        """ After a long idle period, tokens refill only up to burst_allowed.
        """
        registry = TokenBucketRegistry()
        config   = TokenBucketConfig.from_parts(10, 3)

        _ = registry.check_inner('test_key', config, self.now_us)

        much_later = self.now_us + 999_000_000_000
        result = registry.check_inner('test_key', config, much_later)
        self.assertTrue(result.is_allowed)
        self.assertEqual(result.tokens_remaining, 2)

# ################################################################################################################################

    def test_remove_clears_bucket(self) -> 'None':
        """ After removing a key, the next check starts fresh.
        """
        registry = TokenBucketRegistry()
        config   = TokenBucketConfig.from_parts(1, 1)

        _ = registry.check_inner('test_key', config, self.now_us)
        denied = registry.check_inner('test_key', config, self.now_us)
        self.assertFalse(denied.is_allowed)

        registry.remove('test_key')

        fresh = registry.check_inner('test_key', config, self.now_us)
        self.assertTrue(fresh.is_allowed)

# ################################################################################################################################

    def test_clear_removes_all_buckets(self) -> 'None':
        """ clear() empties the entire registry.
        """
        registry = TokenBucketRegistry()
        config   = TokenBucketConfig.from_parts(10, 5)

        _ = registry.check_inner('key_a', config, self.now_us)
        _ = registry.check_inner('key_b', config, self.now_us)
        self.assertEqual(len(registry), 2)

        registry.remove('key_a')
        self.assertEqual(len(registry), 1)

        registry.clear()
        self.assertTrue(registry.is_empty())

# ################################################################################################################################

    def test_basic_allow_and_deny(self) -> 'None':
        """ Sequential checks consume tokens until denied, with correct remaining counts.
        """
        registry = TokenBucketRegistry()
        config   = TokenBucketConfig.from_parts(10, 3)

        result = registry.check_inner('test_key', config, self.now_us)
        self.assertTrue(result.is_allowed)
        self.assertEqual(result.tokens_remaining, 2)

        result = registry.check_inner('test_key', config, self.now_us)
        self.assertTrue(result.is_allowed)
        self.assertEqual(result.tokens_remaining, 1)

        result = registry.check_inner('test_key', config, self.now_us)
        self.assertTrue(result.is_allowed)
        self.assertEqual(result.tokens_remaining, 0)

        result = registry.check_inner('test_key', config, self.now_us)
        self.assertFalse(result.is_allowed)
        self.assertEqual(result.tokens_remaining, 0)
        self.assertGreater(result.retry_after_us, 0)

# ################################################################################################################################

    def test_refill_after_time_passes(self) -> 'None':
        """ After exhausting tokens, waiting long enough allows a new request.
        """
        registry = TokenBucketRegistry()
        config   = TokenBucketConfig.from_parts(10, 3)

        for _ in range(3):
            _ = registry.check_inner('test_key', config, self.now_us)

        result = registry.check_inner('test_key', config, self.now_us)
        self.assertFalse(result.is_allowed)

        later = self.now_us + 500_000
        result = registry.check_inner('test_key', config, later)
        self.assertTrue(result.is_allowed)

# ################################################################################################################################

    def test_burst_cap(self) -> 'None':
        """ After a long idle period, remaining never exceeds burst_allowed - 1.
        """
        registry = TokenBucketRegistry()
        config   = TokenBucketConfig.from_parts(10, 5)

        result = registry.check_inner('test_key', config, self.now_us)
        self.assertTrue(result.is_allowed)
        self.assertEqual(result.tokens_remaining, 4)

        _ = registry.check_inner('test_key', config, self.now_us)
        _ = registry.check_inner('test_key', config, self.now_us)
        _ = registry.check_inner('test_key', config, self.now_us)
        _ = registry.check_inner('test_key', config, self.now_us)

        much_later = self.now_us + 100_000_000_000
        result = registry.check_inner('test_key', config, much_later)
        self.assertTrue(result.is_allowed)
        self.assertEqual(result.tokens_remaining, 4)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()
