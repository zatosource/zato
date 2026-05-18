# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
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

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class BaseCleanupTestCase(unittest.TestCase):
    """ Shared setUp, tearDown, and helpers for all cleanup tests.
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
        logger.info('store_message -> message_id:%s, topic_name:%s, data_ref:%s', message_id, topic_name, data_ref)

        return data_ref

# ################################################################################################################################

    def add_expiry_entry(self, data_ref:'str', expiration_timestamp:'float') -> 'None':
        """ Adds a data_ref to the expiry sorted set with the given timestamp.
        """
        result = self.redis.zadd(_Pending_Expiry_Key, {data_ref: expiration_timestamp})
        logger.info('add_expiry_entry -> data_ref:%s, timestamp:%s, zadd_result:%s', data_ref, expiration_timestamp, result)

# ################################################################################################################################

    def add_pending_subscriber(self, data_ref:'str', sub_key:'str') -> 'None':
        """ Adds a subscriber to the pending set for a given data_ref.
        """
        pending_key = f'{_Pending_Prefix}{data_ref}'
        result = self.redis.sadd(pending_key, sub_key)
        logger.info('add_pending_subscriber -> data_ref:%s, sub_key:%s, sadd_result:%s', data_ref, sub_key, result)

# ################################################################################################################################

    def get_pending_count(self, data_ref:'str') -> 'int':
        """ Returns the number of subscribers still in the pending set.
        """
        pending_key = f'{_Pending_Prefix}{data_ref}'

        out = self.redis.scard(pending_key)
        logger.info('get_pending_count -> data_ref:%s, count:%s', data_ref, out)

        return out # pyright: ignore[reportReturnType]

# ################################################################################################################################

    def has_expiry_entry(self, data_ref:'str') -> 'bool':
        """ Returns True if the data_ref is still in the expiry sorted set.
        """
        score = self.redis.zscore(_Pending_Expiry_Key, data_ref)
        logger.info('has_expiry_entry -> data_ref:%s, score:%s', data_ref, score)

        out = score is not None
        return out

# ################################################################################################################################

    def has_pending_set(self, data_ref:'str') -> 'bool':
        """ Returns True if the pending set key exists in Redis.
        """
        pending_key = f'{_Pending_Prefix}{data_ref}'
        exists_result = self.redis.exists(pending_key)
        logger.info('has_pending_set -> data_ref:%s, exists_result:%s', data_ref, exists_result)

        out = exists_result > 0 # pyright: ignore[reportOperatorIssue]
        return out

# ################################################################################################################################

    def file_exists(self, data_ref:'str') -> 'bool':
        """ Returns True if the disk file for the given data_ref exists.
        """
        absolute_path = os.path.join(self.test_dir, data_ref)

        out = os.path.exists(absolute_path)
        logger.info('file_exists -> data_ref:%s, path:%s, exists:%s', data_ref, absolute_path, out)

        return out

# ################################################################################################################################
# ################################################################################################################################

class TestCleanupSweepNoExpired(BaseCleanupTestCase):
    """ No expired entries - sweep returns 0, no files deleted.
    """

    def test_sweep_returns_zero_when_nothing_expired(self) -> 'None':
        """ Sweep should return 0 and leave all files and keys intact.
        """

        # Store a message with a far-future expiry ..
        message_id = 'zpsm.20260518-080000-1234-aabbccdd11223344'
        data_ref = self.store_message(message_id, 'test.cleanup.no_expired')

        self.add_expiry_entry(data_ref, 4_000_000_000.0)
        self.add_pending_subscriber(data_ref, 'sub.test_subscriber')

        # .. run the sweep ..
        deleted_count = self.cleanup.sweep_once()

        # .. verify nothing was deleted ..
        self.assertEqual(deleted_count, 0)

        # .. verify the disk file still exists ..
        file_exists = self.file_exists(data_ref)
        self.assertTrue(file_exists)

        # .. verify the pending set still exists ..
        pending_set_exists = self.has_pending_set(data_ref)
        self.assertTrue(pending_set_exists)

        # .. and verify the expiry entry still exists.
        expiry_entry_exists = self.has_expiry_entry(data_ref)
        self.assertTrue(expiry_entry_exists)

# ################################################################################################################################
# ################################################################################################################################

class TestCleanupSweepOneExpired(BaseCleanupTestCase):
    """ One expired entry - sweep deletes the pending set, expiry entry, and disk file.
    """

    def test_sweep_deletes_expired_entry(self) -> 'None':
        """ Sweep should delete exactly 1 expired message and all its associated state.
        """

        # Store a message with a past expiry ..
        message_id = 'zpsm.20260518-080100-5678-eeff001122334455'
        data_ref = self.store_message(message_id, 'test.cleanup.one_expired')

        self.add_expiry_entry(data_ref, 1.0)
        self.add_pending_subscriber(data_ref, 'sub.subscriber_a')
        self.add_pending_subscriber(data_ref, 'sub.subscriber_b')

        # .. run the sweep ..
        deleted_count = self.cleanup.sweep_once()

        # .. verify exactly one entry was cleaned up ..
        self.assertEqual(deleted_count, 1)

        # .. verify the disk file is gone ..
        file_exists = self.file_exists(data_ref)
        self.assertFalse(file_exists)

        # .. verify the pending set is gone ..
        pending_set_exists = self.has_pending_set(data_ref)
        self.assertFalse(pending_set_exists)

        # .. and verify the expiry entry is gone.
        expiry_entry_exists = self.has_expiry_entry(data_ref)
        self.assertFalse(expiry_entry_exists)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
