# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from unittest.mock import patch

# Zato
from zato.common.pubsub.delivery import deliver_with_policy, DeliveryExhausted, SendRejected
from zato.common.typing_ import list_
from zato.common.util.retry import RetryPolicy

# ################################################################################################################################
# ################################################################################################################################

# The waits a round made, in seconds
floatlist = list_[float]

# ################################################################################################################################
# ################################################################################################################################

_cid = 'test-cid-policy-001'
_conn_name = 'Order Intake'

# A policy allowing two more attempts after the first one, with no waiting worth the name between them
_policy = RetryPolicy(
    max_retries=2,
    sleep_time=1,
    backoff_threshold=100,
    backoff_multiplier=1,
    max_sleep_time=1,
    jitter_percent=0,
)

# The ceiling on a single wait of a policy built with the defaults of outgoing connections
_max_sleep_time = 8

# What the endpoint answers with
_refused_error = 'HTTP 400 Bad Request'
_rejected_error = 'HTTP 503 Service Unavailable'
_timeout_error = 'Timeout error: the endpoint did not answer'

# ################################################################################################################################
# ################################################################################################################################

class _Attempt:
    """ An attempt that fails the same way every time it is made.
    """

    def __init__(self, error:'Exception') -> 'None':
        self.error = error
        self.calls = 0

    def __call__(self) -> 'None':
        self.calls += 1
        raise self.error

# ################################################################################################################################
# ################################################################################################################################

class DeliverWithPolicyTestCase(unittest.TestCase):
    """ What a round of delivery does with each kind of failure.
    """

    def setUp(self) -> 'None':

        # Every wait the round makes, recorded rather than slept through
        self.sleeps:'floatlist' = []

        def _sleep(seconds:'float') -> 'None':
            self.sleeps.append(seconds)

        self.sleep_patch = patch('zato.common.pubsub.delivery.sleep', _sleep)
        _ = self.sleep_patch.start()

    def tearDown(self) -> 'None':
        self.sleep_patch.stop()

# ################################################################################################################################

    def test_a_message_turned_down_for_now_is_tried_as_often_as_the_policy_allows(self) -> 'None':

        attempt = _Attempt(SendRejected(_rejected_error, is_permanent=False))

        with self.assertRaises(DeliveryExhausted) as raised:
            deliver_with_policy(_policy, 0, _cid, _conn_name, attempt)

        self.assertEqual(attempt.calls, 3)
        self.assertEqual(raised.exception.attempts, 3)
        self.assertEqual(raised.exception.error_class, 'SendRejected')
        self.assertEqual(len(self.sleeps), 2)

# ################################################################################################################################

    def test_a_message_the_endpoint_could_not_be_reached_with_is_tried_as_often_as_the_policy_allows(self) -> 'None':

        attempt = _Attempt(Exception(_timeout_error))

        with self.assertRaises(DeliveryExhausted) as raised:
            deliver_with_policy(_policy, 0, _cid, _conn_name, attempt)

        self.assertEqual(attempt.calls, 3)
        self.assertEqual(raised.exception.error, _timeout_error)
        self.assertEqual(len(self.sleeps), 2)

# ################################################################################################################################

    def test_a_message_turned_down_for_good_is_not_tried_again(self) -> 'None':
        """ The endpoint said the message itself is wrong, which no further attempt can get past,
        so the round is over at once with the attempts the policy would have allowed unused.
        """
        attempt = _Attempt(SendRejected(_refused_error, is_permanent=True))

        with self.assertRaises(DeliveryExhausted) as raised:
            deliver_with_policy(_policy, 0, _cid, _conn_name, attempt)

        self.assertEqual(attempt.calls, 1)
        self.assertEqual(raised.exception.attempts, 1)
        self.assertEqual(raised.exception.error, _refused_error)
        self.assertEqual(raised.exception.error_class, 'SendRejected')
        self.assertEqual(self.sleeps, [])

# ################################################################################################################################

    def test_a_refusal_for_good_ends_a_round_that_was_already_under_way(self) -> 'None':
        """ Attempts already made are counted in, and the refusal still ends the round at once.
        """
        attempt = _Attempt(SendRejected(_refused_error, is_permanent=True))

        with self.assertRaises(DeliveryExhausted) as raised:
            deliver_with_policy(_policy, 1, _cid, _conn_name, attempt)

        self.assertEqual(attempt.calls, 1)
        self.assertEqual(raised.exception.attempts, 2)

        # The one wait made was the one before the attempt, as every attempt after the first has
        self.assertEqual(len(self.sleeps), 1)

# ################################################################################################################################

    def test_the_first_wait_of_a_round_is_held_under_the_ceiling_on_a_single_wait(self) -> 'None':

        policy = RetryPolicy(
            max_retries=0,
            sleep_time=13,
            backoff_threshold=12,
            backoff_multiplier=0,
            max_sleep_time=_max_sleep_time,
            jitter_percent=0,
        )

        attempt = _Attempt(Exception(_timeout_error))

        with self.assertRaises(DeliveryExhausted):
            deliver_with_policy(policy, 1, _cid, _conn_name, attempt)

        self.assertEqual(self.sleeps, [_max_sleep_time])

# ################################################################################################################################

    def test_the_first_wait_of_a_round_is_held_under_the_threshold(self) -> 'None':

        policy = RetryPolicy(
            max_retries=6,
            sleep_time=12,
            backoff_threshold=1,
            backoff_multiplier=4,
            max_sleep_time=_max_sleep_time,
            jitter_percent=0,
        )

        attempt = _Attempt(SendRejected(_rejected_error, is_permanent=False))

        with self.assertRaises(DeliveryExhausted):
            deliver_with_policy(policy, 1, _cid, _conn_name, attempt)

        self.assertEqual(self.sleeps, [1])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
