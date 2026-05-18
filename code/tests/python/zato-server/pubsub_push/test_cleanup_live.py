# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import time
import unittest

# local
from _base_cleanup_live import BaseCleanupLiveTestCase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

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

        # Publish 5 messages with 1-second TTL ..
        for _ in range(5):
            _ = self.publisher.publish(topic_name, 'cleanup test payload', expiration=1)

        # .. collect data_refs from the stream ..
        data_refs = self._get_published_data_refs(topic_name, 5)
        self.assertEqual(len(data_refs), 5)

        # .. verify files exist on disk ..
        self.assert_files_exist(data_refs)

        # .. wait for messages to expire ..
        time.sleep(2)

        # .. run the cleanup ..
        self._run_cleanup_once()

        # .. and verify everything is gone.
        self.assert_all_cleaned(data_refs)

# ################################################################################################################################
# ################################################################################################################################

class TestCleanupMixedExpiry(BaseCleanupLiveTestCase):
    """ Publish 5 messages with 1-second TTL and 5 with 1-hour TTL, run cleanup,
    verify only the expired 5 are cleaned up, the live 5 are untouched.
    """

    def test_cleanup_only_removes_expired_leaves_live(self) -> 'None':

        topic_name = 'iam.user.deleted'

        # Publish 5 messages with 1-second TTL ..
        for _ in range(5):
            _ = self.publisher.publish(topic_name, 'short-lived payload', expiration=1)

        expired_refs = self._get_published_data_refs(topic_name, 5)
        self.assertEqual(len(expired_refs), 5)

        # .. publish 5 messages with 1-hour TTL ..
        for _ in range(5):
            _ = self.publisher.publish(topic_name, 'long-lived payload', expiration=3600)

        all_refs = self._get_published_data_refs(topic_name, 10)
        live_refs:'strlist' = []

        for data_ref in all_refs:
            if data_ref not in expired_refs:
                live_refs.append(data_ref)

        self.assertEqual(len(live_refs), 5)

        # .. wait for the short-lived messages to expire ..
        time.sleep(2)

        # .. run the cleanup ..
        self._run_cleanup_once()

        # .. verify expired messages are gone ..
        self.assert_all_cleaned(expired_refs)

        # .. and live messages are still present.
        self.assert_all_present(live_refs)

# ################################################################################################################################
# ################################################################################################################################

class TestCleanupAfterSubscriptionDeleted(BaseCleanupLiveTestCase):
    """ Publish a message with short TTL, delete the subscription before delivery,
    wait for expiry, run cleanup - file cleaned up by the expiry sweep.
    """

    def test_cleanup_handles_deleted_subscription(self) -> 'None':

        topic_name = 'iam.role.assigned'

        # Publish a message with 1-second TTL ..
        _ = self.publisher.publish(topic_name, 'will expire undelivered', expiration=1)

        # .. collect the data_ref ..
        data_refs = self._get_published_data_refs(topic_name, 1)
        self.assertEqual(len(data_refs), 1)

        # .. verify the file exists ..
        self.assert_files_exist(data_refs)

        # .. remove all subscribers from the topic so no delivery can happen ..
        topic_subs_key = f'zato:pubsub:topic_subs:{topic_name}'
        _ = self.redis.delete(topic_subs_key)
        logger.info('Deleted topic_subs key -> %s', topic_subs_key)

        # .. wait for expiry ..
        time.sleep(2)

        # .. run cleanup - the expiry sweep should remove the file.
        self._run_cleanup_once()

        # .. and verify everything is gone.
        self.assert_all_cleaned(data_refs)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
