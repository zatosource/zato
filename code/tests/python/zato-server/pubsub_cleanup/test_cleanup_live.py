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
from zato.common.test import pubsub_db
from zato.common.test.base_cleanup_live import BaseCleanupLiveTestCase

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_push.cleanup_live')

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

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
