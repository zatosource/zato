# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
import unittest

# Zato
from zato.common.api import PubSub
from zato.common.audit_log.api import AuditEvent

# local
from _helpers import assert_gap_within, get_client, get_gaps, get_audit_events, get_invocations, publish, Refuse_Everything, \
    set_behaviour, Slack_Seconds, Target_Service, Topic_Service, wait_for_audit_events, wait_for_empty_queue, \
    wait_for_invocations

# ################################################################################################################################
# ################################################################################################################################

# The sleep the tests ask for between two attempts, in seconds, and the multiplier that keeps every sleep that long.
_sleep_time = 1
_flat_multiplier = 1

# The default policy's schedule for a target that refuses four times - the first sleep, then doubling up to the ceiling.
_default_gaps = [
    PubSub.Delivery.Default_Sleep_Time,
    PubSub.Delivery.Default_Sleep_Time * 2,
    PubSub.Delivery.Default_Sleep_Time * 4,
    PubSub.Delivery.Max_Sleep_Time,
]

# The longest a gap under the default policy may ever be.
_default_gap_ceiling = PubSub.Delivery.Max_Sleep_Time * (1 + PubSub.Delivery.Jitter_Percent / 100) + Slack_Seconds

# How long to keep watching for an attempt that must not come - longer than a round of an outgoing queue waits,
# so that a message wrongly kept for another round would be seen.
_quiet_period_seconds = PubSub.Delivery.Retry_Round_Wait + 2

# How long a message of the expiry test lives, in seconds, and how long after that to keep watching.
_expiration_seconds = 2
_after_expiry_seconds = 4

# ################################################################################################################################
# ################################################################################################################################

class ServicePushRetryTestCase(unittest.TestCase):
    """ A publication to a topic whose subscriber is a service is retried as the publication's own settings say,
    or as the default policy says when it has none.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.client = get_client()

# ################################################################################################################################

    def _get_acceptance(self, invocations:'list') -> 'list':
        """ Whether each invocation was accepted, in the order they were made.
        """
        out = []

        for invocation in invocations:
            out.append(invocation['is_accepted'])

        return out

# ################################################################################################################################

    def test_the_retries_run_and_the_message_arrives(self) -> 'None':
        """ Two retries a second apart and a target that refuses twice - the third attempt is the one that arrives.
        """
        set_behaviour(self.client, 2)

        result = publish(self.client, Topic_Service, {'order_id': 'retried'},
            max_retries=2, retry_sleep_time=_sleep_time, retry_backoff_multiplier=_flat_multiplier)
        msg_id = result['msg_id']

        invocations = wait_for_invocations(self.client, 3)

        self.assertEqual(len(invocations), 3, invocations)
        acceptance = self._get_acceptance(invocations)
        self.assertEqual(acceptance, [False, False, True])

        gaps = get_gaps(invocations)

        for gap in gaps:
            assert_gap_within(gap, _sleep_time)

        pending = wait_for_empty_queue(self.client, Topic_Service)
        self.assertEqual(pending, 0)

        # The audit log holds the one delivery and no failure
        delivered = wait_for_audit_events(msg_id, AuditEvent.Delivered, 1)
        self.assertEqual(len(delivered), 1, delivered)

        failed = get_audit_events(msg_id, AuditEvent.Delivery_Failed)
        self.assertEqual(len(failed), 0, failed)

# ################################################################################################################################

    def test_no_settings_means_the_default_schedule(self) -> 'None':
        """ A publication with no settings is retried after 3, 6, 12 and then 15 seconds, the ceiling.
        """
        set_behaviour(self.client, 4)

        _ = publish(self.client, Topic_Service, {'order_id': 'default-schedule'})

        invocations = wait_for_invocations(self.client, 5)

        self.assertEqual(len(invocations), 5, invocations)
        acceptance = self._get_acceptance(invocations)
        self.assertEqual(acceptance, [False, False, False, False, True])

        gaps = get_gaps(invocations)

        for gap, expected in zip(gaps, _default_gaps):
            assert_gap_within(gap, expected)
            self.assertLessEqual(gap, _default_gap_ceiling, gaps)

        pending = wait_for_empty_queue(self.client, Topic_Service)
        self.assertEqual(pending, 0)

# ################################################################################################################################

    def test_the_attempts_run_out_and_the_message_is_done(self) -> 'None':
        """ Two retries and a target that refuses three times - the message is given up on, the one behind it
        is delivered and nothing comes back for another round.
        """
        set_behaviour(self.client, 3)

        first = publish(self.client, Topic_Service, {'order_id': 'given-up'},
            max_retries=2, retry_sleep_time=_sleep_time, retry_backoff_multiplier=_flat_multiplier)
        first_msg_id = first['msg_id']

        invocations = wait_for_invocations(self.client, 3)
        acceptance = self._get_acceptance(invocations)
        self.assertEqual(acceptance, [False, False, False])

        _ = publish(self.client, Topic_Service, {'order_id': 'after-given-up'})

        invocations = wait_for_invocations(self.client, 4)
        acceptance = self._get_acceptance(invocations)
        self.assertEqual(acceptance, [False, False, False, True])

        # Nothing more arrives, the given-up message has no second round ..
        time.sleep(_quiet_period_seconds)

        invocations = get_invocations(self.client)
        self.assertEqual(len(invocations), 4, invocations)

        pending = wait_for_empty_queue(self.client, Topic_Service)
        self.assertEqual(pending, 0)

        # .. and the audit log holds the one failure, naming the three attempts, and no delivery.
        failed = wait_for_audit_events(first_msg_id, AuditEvent.Delivery_Failed, 1)
        self.assertEqual(len(failed), 1, failed)
        failure = failed[0]
        self.assertIn('3 attempts', failure['status'])

        delivered = get_audit_events(first_msg_id, AuditEvent.Delivered)
        self.assertEqual(len(delivered), 0, delivered)

# ################################################################################################################################

    def test_an_explicit_zero_is_one_attempt(self) -> 'None':
        """ No retries and a target that refuses once - one attempt and the message is done.
        """
        set_behaviour(self.client, 1)

        result = publish(self.client, Topic_Service, {'order_id': 'one-attempt'}, max_retries=0)
        msg_id = result['msg_id']

        invocations = wait_for_invocations(self.client, 1)
        acceptance = self._get_acceptance(invocations)
        self.assertEqual(acceptance, [False])

        pending = wait_for_empty_queue(self.client, Topic_Service)
        self.assertEqual(pending, 0)

        failed = wait_for_audit_events(msg_id, AuditEvent.Delivery_Failed, 1)
        self.assertEqual(len(failed), 1, failed)

        # There was no second attempt
        invocations = get_invocations(self.client)
        self.assertEqual(len(invocations), 1, invocations)

# ################################################################################################################################

    def test_the_multiplier_grows_the_sleep_and_the_threshold_ends_the_round(self) -> 'None':
        """ With a multiplier of two the second sleep is twice the first, and a threshold of three seconds
        allows no third sleep however many retries there are.
        """
        set_behaviour(self.client, Refuse_Everything)

        result = publish(self.client, Topic_Service, {'order_id': 'capped'},
            max_retries=5, retry_sleep_time=_sleep_time, retry_backoff_threshold=3, retry_backoff_multiplier=2)
        msg_id = result['msg_id']

        invocations = wait_for_invocations(self.client, 3)
        acceptance = self._get_acceptance(invocations)
        self.assertEqual(acceptance, [False, False, False])

        gaps = get_gaps(invocations)

        assert_gap_within(gaps[0], _sleep_time)
        assert_gap_within(gaps[1], _sleep_time * 2)

        pending = wait_for_empty_queue(self.client, Topic_Service)
        self.assertEqual(pending, 0)

        failed = wait_for_audit_events(msg_id, AuditEvent.Delivery_Failed, 1)
        self.assertEqual(len(failed), 1, failed)

        # There was no fourth attempt
        invocations = get_invocations(self.client)
        self.assertEqual(len(invocations), 3, invocations)

# ################################################################################################################################

    def test_a_service_name_in_place_of_a_topic(self) -> 'None':
        """ A publication to a service by name goes through the service's own topic and is retried all the same.
        """
        set_behaviour(self.client, 1)

        _ = publish(self.client, Target_Service, {'order_id': 'by-name'}, max_retries=1, retry_sleep_time=_sleep_time)

        invocations = wait_for_invocations(self.client, 2)

        self.assertEqual(len(invocations), 2, invocations)
        acceptance = self._get_acceptance(invocations)
        self.assertEqual(acceptance, [False, True])

        gaps = get_gaps(invocations)
        assert_gap_within(gaps[0], _sleep_time)

# ################################################################################################################################

    def test_expiry_ends_the_round(self) -> 'None':
        """ A message that expires while its target refuses is not attempted again once it has expired.
        """
        set_behaviour(self.client, Refuse_Everything)

        result = publish(self.client, Topic_Service, {'order_id': 'expiring'}, expiration=_expiration_seconds)
        msg_id = result['msg_id']

        invocations = wait_for_invocations(self.client, 1)
        acceptance = self._get_acceptance(invocations)
        self.assertEqual(acceptance, [False])

        expired = wait_for_audit_events(msg_id, AuditEvent.Expired, 1)
        self.assertEqual(len(expired), 1, expired)

        # The target accepts now, yet the expired message never comes
        set_behaviour(self.client, 0)

        time.sleep(_after_expiry_seconds)

        invocations = get_invocations(self.client)
        self.assertEqual(len(invocations), 0, invocations)

        pending = wait_for_empty_queue(self.client, Topic_Service)
        self.assertEqual(pending, 0)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
