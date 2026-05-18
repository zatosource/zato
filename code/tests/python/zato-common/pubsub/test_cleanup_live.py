# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

# redis
from redis import Redis

# Zato
from zato.common.pubsub.cleanup import _Pending_Expiry_Key, _Pending_Prefix
from zato.common.pubsub.disk_store import DiskMessageStore

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_test_redis_host = 'localhost'
_test_redis_port = 6379
_test_redis_db   = 0

_cleanup_module = 'zato.common.pubsub.cleanup'
_python_bin     = sys.executable

# ################################################################################################################################
# ################################################################################################################################

class BaseCleanupLiveTestCase(unittest.TestCase):
    """ Shared setup for live cleanup tests that run the cleanup process as a subprocess.
    """

    def setUp(self) -> 'None':

        # Set up a real Redis connection ..
        self.redis = Redis(host=_test_redis_host, port=_test_redis_port, db=_test_redis_db, decode_responses=True)

        # .. create a temp directory that mimics a server's work/pubsub-messages structure ..
        self.server_directory = tempfile.mkdtemp(prefix='zato_cleanup_live_')
        self.disk_store_dir = os.path.join(self.server_directory, 'work', 'pubsub-messages')
        os.makedirs(self.disk_store_dir)

        self.disk_store = DiskMessageStore(self.disk_store_dir)

        # .. track all data_refs created during the test for cleanup ..
        self.created_data_refs:'strlist' = []
        self._message_counter = 0

        # .. track the subprocess.
        self.cleanup_process:'subprocess.Popen[bytes] | None' = None

# ################################################################################################################################

    def tearDown(self) -> 'None':

        # Stop the cleanup process if running ..
        if self.cleanup_process:
            if self.cleanup_process.poll() is None:
                self.cleanup_process.terminate()
                _ = self.cleanup_process.wait(timeout=5)
                logger.info('Terminated cleanup process -> pid:%d', self.cleanup_process.pid)

        # .. clean up all Redis keys ..
        for data_ref in self.created_data_refs:
            pending_key = f'{_Pending_Prefix}{data_ref}'
            _ = self.redis.delete(pending_key)
            _ = self.redis.zrem(_Pending_Expiry_Key, data_ref)

        key_count = len(self.created_data_refs)
        suffix = 'key' if key_count == 1 else 'keys'
        logger.info('Cleaned up %d Redis %s', key_count, suffix)

        # .. and remove the temp directory.
        shutil.rmtree(self.server_directory)
        logger.info('Removed temp directory -> %s', self.server_directory)

# ################################################################################################################################

    def store_message(self, topic_name:'str', data:'str'='test payload') -> 'str':
        """ Stores a message on disk with an auto-generated ID and registers its data_ref for cleanup.
        """
        self._message_counter += 1
        now_int = int(time.time())
        message_id = f'zpsm.{now_int}-{self._message_counter:08d}-aabbccdd11223344'

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
        absolute_path = os.path.join(self.disk_store_dir, data_ref)

        out = os.path.exists(absolute_path)
        logger.info('file_exists -> data_ref:%s, path:%s, exists:%s', data_ref, absolute_path, out)

        return out

# ################################################################################################################################

    def start_cleanup_process(self, interval:'int'=2, batch_size:'int'=100) -> 'None':
        """ Starts the cleanup process as a subprocess pointing at the test server directory.
        """
        command = [
            _python_bin, '-m', _cleanup_module,
            self.server_directory,
            '--interval', str(interval),
            '--batch-size', str(batch_size),
            '--redis-host', _test_redis_host,
            '--redis-port', str(_test_redis_port),
            '--redis-db', str(_test_redis_db),
        ]

        self.cleanup_process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        logger.info('Started cleanup process -> pid:%d, interval:%d, batch_size:%d',
            self.cleanup_process.pid, interval, batch_size)

# ################################################################################################################################
# ################################################################################################################################

class TestCleanupLiveExpiredMessages(BaseCleanupLiveTestCase):
    """ Start cleanup process, publish 5 messages with 1-second TTL, wait for expiry + cleanup interval,
    verify all disk files and pending sets are gone.
    """

    def test_cleanup_removes_expired_messages(self) -> 'None':
        """ The cleanup process should remove all 5 expired messages within a few sweep cycles.
        """

        # Create 5 messages that are already expired ..
        expiration_timestamp = time.time() - 1.0
        data_refs:'strlist' = []

        for _ in range(5):
            data_ref = self.store_message('test.cleanup_live.expired')
            self.add_expiry_entry(data_ref, expiration_timestamp)
            self.add_pending_subscriber(data_ref, 'sub.live_test_subscriber')
            data_refs.append(data_ref)

        # .. start the cleanup process with a 1-second interval ..
        self.start_cleanup_process(interval=1)

        # .. wait for the cleanup to run ..
        time.sleep(3)

        # .. verify all files, pending sets, and expiry entries are gone.
        for data_ref in data_refs:

            file_exists = self.file_exists(data_ref)
            self.assertFalse(file_exists)

            pending_set_exists = self.has_pending_set(data_ref)
            self.assertFalse(pending_set_exists)

            expiry_entry_exists = self.has_expiry_entry(data_ref)
            self.assertFalse(expiry_entry_exists)

# ################################################################################################################################
# ################################################################################################################################

class TestCleanupLiveMixedExpiry(BaseCleanupLiveTestCase):
    """ Publish 5 messages with 1-second TTL and 5 with 1-hour TTL, wait for cleanup,
    verify only the expired 5 are cleaned up, the live 5 are untouched.
    """

    def test_cleanup_only_removes_expired_leaves_live(self) -> 'None':

        # Create 5 messages that are already expired ..
        expired_timestamp = time.time() - 1.0
        expired_refs:'strlist' = []

        for _ in range(5):
            data_ref = self.store_message('test.cleanup_live.expired')
            self.add_expiry_entry(data_ref, expired_timestamp)
            self.add_pending_subscriber(data_ref, 'sub.live_test_subscriber')
            expired_refs.append(data_ref)

        # .. create 5 messages that expire in 1 hour (still live) ..
        live_timestamp = time.time() + 3600
        live_refs:'strlist' = []

        for _ in range(5):
            data_ref = self.store_message('test.cleanup_live.live')
            self.add_expiry_entry(data_ref, live_timestamp)
            self.add_pending_subscriber(data_ref, 'sub.live_test_subscriber')
            live_refs.append(data_ref)

        # .. start the cleanup process with a 1-second interval ..
        self.start_cleanup_process(interval=1)

        # .. wait for the cleanup to run ..
        time.sleep(3)

        # .. verify all expired files, pending sets, and expiry entries are gone ..
        for data_ref in expired_refs:

            file_exists = self.file_exists(data_ref)
            self.assertFalse(file_exists)

            pending_set_exists = self.has_pending_set(data_ref)
            self.assertFalse(pending_set_exists)

            expiry_entry_exists = self.has_expiry_entry(data_ref)
            self.assertFalse(expiry_entry_exists)

        # .. and all live files, pending sets, and expiry entries are still present.
        for data_ref in live_refs:

            file_exists = self.file_exists(data_ref)
            self.assertTrue(file_exists)

            pending_set_exists = self.has_pending_set(data_ref)
            self.assertTrue(pending_set_exists)

            expiry_entry_exists = self.has_expiry_entry(data_ref)
            self.assertTrue(expiry_entry_exists)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
