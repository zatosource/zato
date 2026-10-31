# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import time
import unittest

# Zato
from zato.common.pubsub.sql.config import ModuleCtx
from zato.common.test import pubsub_db
from zato.common.test.base_cleanup_live import BaseCleanupLiveTestCase
from zato.common.util.time_ import datetime_to_ms, utcnow

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_push.cleanup_live')

# How long messages that must not expire during a test live, in seconds.
_long_ttl_seconds = 3600

# How far in the past an aged trace is placed - past the default retention of seven days.
_aged_days = 30

# How many milliseconds one day has.
_ms_per_day = 24 * 60 * 60 * 1000

# How long the write lock is held, in seconds - longer than the busy timeout of 5 seconds,
# so the first attempt of the sweep cannot obtain the lock.
_lock_hold_seconds = 7

# What the cleanup process logs each time it postpones a sweep.
_postponed_message = 'Sweep postponed, the database is locked'

# ################################################################################################################################
# ################################################################################################################################

class TestCleanupExpiredViaAPI(BaseCleanupLiveTestCase):
    """ Publish 5 messages with 1-second TTL via the REST API, run cleanup, verify all gone.
    """

    def test_cleanup_removes_expired_messages(self) -> 'None':

        topic_name = 'iam.user.created'
        ttl_seconds = 1

        # Publish 5 messages with short TTL - the topic's pull subscriber never pulls,
        # so the messages keep their payloads and stay pending until they expire ..
        msg_ids = self.publish_messages(topic_name, 5, ttl_seconds)

        # .. verify the rows and payloads exist in the database ..
        self.assert_all_present(msg_ids)

        # .. wait for the messages to expire ..
        time.sleep(ttl_seconds + 1)

        # .. run the cleanup ..
        self._run_cleanup_once()

        # .. and verify everything is gone.
        self.assert_all_cleaned(msg_ids)

# ################################################################################################################################
# ################################################################################################################################

class TestCleanupMixedExpiry(BaseCleanupLiveTestCase):
    """ Publish 5 messages with 1-second TTL and 5 with 1-hour TTL, run cleanup,
    verify only the expired 5 are cleaned up, the live 5 are untouched.
    """

    def test_cleanup_only_removes_expired_leaves_live(self) -> 'None':

        topic_name = 'iam.user.deleted'
        short_ttl = 1
        long_ttl = 3600

        # Publish 5 messages with short TTL ..
        expired_ids = self.publish_messages(topic_name, 5, short_ttl)

        # .. publish 5 messages with 1-hour TTL ..
        live_ids = self.publish_messages(topic_name, 5, long_ttl)

        # .. wait for the short-lived messages to expire ..
        time.sleep(short_ttl + 1)

        # .. run the cleanup ..
        self._run_cleanup_once()

        # .. verify expired messages are gone ..
        self.assert_all_cleaned(expired_ids)

        # .. and live messages are still present.
        self.assert_all_present(live_ids)

# ################################################################################################################################
# ################################################################################################################################

class TestCleanupAfterSubscriptionDeleted(BaseCleanupLiveTestCase):
    """ Publish a message with short TTL, remove the topic's subscription rows behind
    the server's back, wait for expiry, run cleanup - the expiry sweep removes the message
    even though no subscriber is left to ever acknowledge it.
    """

    def test_cleanup_handles_deleted_subscription(self) -> 'None':

        topic_name = 'iam.role.assigned'
        ttl_seconds = 1

        # Publish a message with short TTL ..
        msg_ids = self.publish_messages(topic_name, 1, ttl_seconds)

        # .. verify the row and its payload exist ..
        self.assert_all_present(msg_ids)

        # .. remove all subscribers from the topic so no delivery can happen ..
        pubsub_db.remove_topic_subscriptions(topic_name)
        logger.info('Removed subscription rows -> %s', topic_name)

        # .. wait for expiry ..
        time.sleep(ttl_seconds + 1)

        # .. run cleanup - the expiry sweep should remove the message.
        self._run_cleanup_once()

        # .. and verify everything is gone.
        self.assert_all_cleaned(msg_ids)

# ################################################################################################################################
# ################################################################################################################################

class TestCleanupAgedTraces(BaseCleanupLiveTestCase):
    """ Fully delivered messages older than the retention age are removed,
    while a fully delivered message within the retention age is kept.
    """

    def test_cleanup_removes_aged_traces(self) -> 'None':

        topic_name = 'iam.password.changed'

        # Publish three messages that will age and one that will not ..
        aged_ids = self.publish_messages(topic_name, 3, _long_ttl_seconds)
        recent_ids = self.publish_messages(topic_name, 1, _long_ttl_seconds)

        all_ids = aged_ids + recent_ids

        # .. both subscribers acknowledge all of them, which leaves their traces ..
        self.drain_puller()
        self.wait_until_delivered(all_ids)

        trace_count = pubsub_db.count_message_rows(all_ids)
        self.assertEqual(trace_count, len(all_ids))

        # .. three of the traces move past the retention age ..
        now_ms = int(datetime_to_ms(utcnow()))
        aged_ms = now_ms - _aged_days * _ms_per_day
        pubsub_db.set_pub_time_ms(aged_ids, aged_ms)

        # .. run the cleanup ..
        self._run_cleanup_once()

        # .. and only the aged traces are gone.
        self.assert_all_cleaned(aged_ids)

        recent_count = pubsub_db.count_message_rows(recent_ids)
        self.assertEqual(recent_count, len(recent_ids))

# ################################################################################################################################
# ################################################################################################################################

class TestCleanupOverCapTraces(BaseCleanupLiveTestCase):
    """ With the per-topic cap of fully delivered messages lowered to one,
    only the newest trace of the topic is kept.
    """

    def test_cleanup_removes_over_cap_traces(self) -> 'None':

        topic_name = 'iam.login.failed'

        # Publish three messages ..
        msg_ids = self.publish_messages(topic_name, 3, _long_ttl_seconds)

        # .. both subscribers acknowledge all of them ..
        self.drain_puller()
        self.wait_until_delivered(msg_ids)

        # .. run the cleanup with a cap of one trace per topic ..
        extra_env = {
            ModuleCtx.Env_Delivered_Max_Messages: '1',
        }
        self._run_cleanup_once(extra_env)

        # .. and only the newest trace remains.
        self.assert_all_cleaned(msg_ids[:2])

        newest_count = pubsub_db.count_message_rows(msg_ids[2:])
        self.assertEqual(newest_count, 1)

# ################################################################################################################################
# ################################################################################################################################

class TestCleanupEmptyCounts(BaseCleanupLiveTestCase):
    """ The count rows that dropped to zero once every message was delivered are removed.
    """

    def test_cleanup_removes_empty_count_rows(self) -> 'None':

        topic_name = 'customer.registered'

        # Publish two messages ..
        msg_ids = self.publish_messages(topic_name, 2, _long_ttl_seconds)

        # .. both subscribers acknowledge them, which brings their queue depths down to zero ..
        self.drain_puller()
        self.wait_until_delivered(msg_ids)

        empty_count = pubsub_db.count_empty_count_rows()
        self.assertGreater(empty_count, 0)

        # .. run the cleanup ..
        self._run_cleanup_once()

        # .. and no count row of zero remains.
        empty_count = pubsub_db.count_empty_count_rows()
        self.assertEqual(empty_count, 0)

# ################################################################################################################################
# ################################################################################################################################

class TestCleanupLockedDatabase(BaseCleanupLiveTestCase):
    """ Another connection holds the write lock for longer than the busy timeout while the cleanup runs -
    the cleanup postpones its sweep instead of ending, and completes it once the lock is released.
    """

    def test_cleanup_outlasts_locked_database(self) -> 'None':

        topic_name = 'customer.updated'
        ttl_seconds = 1

        # Publish messages with a short TTL that the pull subscriber never pulls ..
        msg_ids = self.publish_messages(topic_name, 2, ttl_seconds)
        self.assert_all_present(msg_ids)

        # .. wait for them to expire ..
        time.sleep(ttl_seconds + 1)

        # .. run the cleanup while the database is locked ..
        output = self._run_cleanup_while_locked(_lock_hold_seconds)

        # .. the sweep was postponed at least once ..
        self.assertIn(_postponed_message, output)

        # .. and it completed nonetheless.
        self.assert_all_cleaned(msg_ids)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
