# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
import unittest

# local
from _helpers import get_client, Jitter_Fraction, publish, Slack_Seconds, TestConfig, Topic_REST, wait_for_empty_queue

# ################################################################################################################################
# ################################################################################################################################

# The sleep the test asks for between two attempts, in seconds.
_sleep_time = 1

# How long the publication and the receiver's own bookkeeping may add to the measured time, in seconds.
_delivery_overhead_seconds = 1.0

# How long to wait for the delivery at most, in seconds.
_delivery_timeout_seconds = 30.0

# ################################################################################################################################
# ################################################################################################################################

class RESTPushRetryTestCase(unittest.TestCase):
    """ A publication to a topic whose subscriber is a REST endpoint is retried under the same policy.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.client = get_client()

# ################################################################################################################################

    def test_a_rest_push_subscription_retries_under_the_same_policy(self) -> 'None':
        """ The receiver answers 503 once and 200 after that - two requests about a second apart.
        """
        receiver = TestConfig.receiver
        receiver.behavior.set_reject_503(auto_recover_after=1)

        start_time = time.monotonic()

        _ = publish(self.client, Topic_REST, {'order_id': 'rest-retried'}, max_retries=1, retry_sleep_time=_sleep_time)

        messages = receiver.wait_for_delivery(expected_count=1, timeout=_delivery_timeout_seconds)
        elapsed = time.monotonic() - start_time

        # The message arrived once, after one refusal ..
        self.assertEqual(len(messages), 1, messages)
        self.assertEqual(receiver.behavior.reject_count, 1)

        # .. and it arrived about a retry_sleep_time after the refusal.
        lower = _sleep_time - Slack_Seconds
        upper = _sleep_time + _sleep_time * Jitter_Fraction + Slack_Seconds + _delivery_overhead_seconds

        self.assertGreaterEqual(elapsed, lower, elapsed)
        self.assertLessEqual(elapsed, upper, elapsed)

        pending = wait_for_empty_queue(self.client, Topic_REST)
        self.assertEqual(pending, 0)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
