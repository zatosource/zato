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
from zato.common.pubsub.cleanup import PubSubCleanup

# test
from _base import BaseUnsubCleanupTestCase

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class TestExpirySweepCleansAll(BaseUnsubCleanupTestCase):
    """ Publish 1 message with short TTL, 2 subs, neither acks, wait for expiry, run cleanup sweep -
        pending:{data_ref} gone, both sub_pending sets no longer contain data_ref, pending_expiry empty, file deleted.
    """

    def test_expiry_sweep_removes_everything(self) -> 'None':

        # Subscribe two consumers ..
        sub_key_a = f'sk_unsub_a_{self._run_id}'
        sub_key_b = f'sk_unsub_b_{self._run_id}'

        self.subscribe(sub_key_a)
        self.subscribe(sub_key_b)

        # .. publish a message with a very short TTL (already expired) ..
        _ = self.publish()
        data_ref = self.get_data_ref_from_stream()

        # .. override the expiry score to be in the past so the sweep picks it up ..
        past_timestamp = time.time() - 10
        _ = self.redis.zadd('zato:pubsub:pending_expiry', {data_ref: past_timestamp})

        # .. confirm state before sweep ..
        has_a = self.has_pending_member(data_ref, sub_key_a)
        self.assertTrue(has_a)

        has_b = self.has_pending_member(data_ref, sub_key_b)
        self.assertTrue(has_b)

        has_ref_a = self.has_sub_pending_member(sub_key_a, data_ref)
        self.assertTrue(has_ref_a)

        has_ref_b = self.has_sub_pending_member(sub_key_b, data_ref)
        self.assertTrue(has_ref_b)

        file_present = self.file_exists(data_ref)
        self.assertTrue(file_present)

        # .. create the cleanup instance and run a single sweep ..
        cleanup = PubSubCleanup(
            redis_client=self.redis,
            disk_store=self.disk_store,
        )

        deleted_count = cleanup.sweep_once()
        self.assertEqual(deleted_count, 1)

        # .. pending:{data_ref} is gone ..
        pending_count = self.get_pending_count(data_ref)
        self.assertEqual(pending_count, 0)

        # .. sub_pending:{sub_a} no longer contains data_ref ..
        has_ref_a = self.has_sub_pending_member(sub_key_a, data_ref)
        self.assertFalse(has_ref_a)

        # .. sub_pending:{sub_b} no longer contains data_ref ..
        has_ref_b = self.has_sub_pending_member(sub_key_b, data_ref)
        self.assertFalse(has_ref_b)

        # .. pending_expiry is empty for this data_ref ..
        has_expiry = self.has_expiry_entry(data_ref)
        self.assertFalse(has_expiry)

        # .. and the file is deleted.
        file_present = self.file_exists(data_ref)
        self.assertFalse(file_present)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
