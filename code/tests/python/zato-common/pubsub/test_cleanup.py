# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import tempfile
import unittest

# redis
from redis import Redis

# Zato
from zato.common.pubsub.cleanup import PubSubCleanup, _Pending_Expiry_Key, _Pending_Prefix
from zato.common.pubsub.disk_store import DiskMessageStore

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

_test_redis_host = 'localhost'
_test_redis_port = 6379
_test_redis_db   = 0

# ################################################################################################################################
# ################################################################################################################################

class BaseCleanupTestCase(unittest.TestCase):
    """ Shared setUp and tearDown for all cleanup tests.
    """

    def setUp(self) -> 'None':

        # Set up a real Redis connection ..
        self.redis = Redis(host=_test_redis_host, port=_test_redis_port, db=_test_redis_db, decode_responses=True)

        # .. set up a temp directory for disk store ..
        self.test_dir = tempfile.mkdtemp()
        self.disk_store = DiskMessageStore(self.test_dir)

        # .. create the cleanup instance ..
        self.cleanup = PubSubCleanup(
            redis_client=self.redis,
            disk_store=self.disk_store,
            batch_size=100,
        )

        # .. track all data_refs created during the test for cleanup.
        self.created_data_refs:'strlist' = []

# ################################################################################################################################

    def tearDown(self) -> 'None':

        # Clean up all Redis keys created during the test ..
        for data_ref in self.created_data_refs:
            pending_key = f'{_Pending_Prefix}{data_ref}'
            _ = self.redis.delete(pending_key)
            _ = self.redis.zrem(_Pending_Expiry_Key, data_ref)

        # .. and the temp directory.
        shutil.rmtree(self.test_dir)

# ################################################################################################################################

    def store_message(self, message_id:'str', topic_name:'str', data:'str'='test payload') -> 'str':
        """ Stores a message on disk and registers its data_ref for cleanup.
        """
        data_ref = self.disk_store.store(message_id, topic_name, data, '')
        self.created_data_refs.append(data_ref)

        return data_ref

# ################################################################################################################################
# ################################################################################################################################

class TestCleanupSweepNoExpired(BaseCleanupTestCase):
    """ No expired entries - sweep returns 0, no files deleted.
    """

    def test_sweep_returns_zero_when_nothing_expired(self) -> 'None':
        """ Sweep should return 0 and leave all files and keys intact.
        """

        # Store a message and add it to the expiry index with a far-future timestamp ..
        message_id = 'zpsm.20260518-080000-1234-aabbccdd11223344'
        data_ref = self.store_message(message_id, 'test.cleanup.no_expired')

        future_timestamp = 4_000_000_000.0
        _ = self.redis.zadd(_Pending_Expiry_Key, {data_ref: future_timestamp})

        pending_key = f'{_Pending_Prefix}{data_ref}'
        _ = self.redis.sadd(pending_key, 'sub.test_subscriber')

        # .. run the sweep ..
        deleted_count = self.cleanup.sweep_once()

        # .. verify nothing was deleted ..
        self.assertEqual(deleted_count, 0)

        # .. verify the disk file still exists ..
        absolute_path = os.path.join(self.test_dir, data_ref)
        self.assertTrue(os.path.exists(absolute_path))

        # .. verify the pending set still exists ..
        pending_count = self.redis.scard(pending_key)
        self.assertEqual(pending_count, 1)

        # .. and verify the expiry entry still exists.
        score = self.redis.zscore(_Pending_Expiry_Key, data_ref)
        self.assertIsNotNone(score)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
