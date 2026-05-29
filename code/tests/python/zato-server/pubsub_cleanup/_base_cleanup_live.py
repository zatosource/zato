# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import subprocess
import sys
import unittest

# redis
from redis import Redis

# Zato
from zato.common.typing_ import cast_

# local
from zato.common.test.client import PublishClient
from config import TestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_push.base_cleanup_live')

_test_redis_host = 'localhost'
_test_redis_port = 6379
_test_redis_db   = 0

_python_bin = sys.executable

_Pending_Prefix     = 'zato:pubsub:pending:'
_Pending_Expiry_Key = 'zato:pubsub:pending_expiry'
_Stream_Prefix      = 'zato:pubsub:stream:'

_cleanup_module = 'zato.common.pubsub.cleanup'

# ################################################################################################################################
# ################################################################################################################################

class BaseCleanupLiveTestCase(unittest.TestCase):
    """ Shared setup and helpers for all live cleanup tests that publish via the REST API
    and run the cleanup subprocess against the real server directory.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.publisher = PublishClient(
            TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
        class_.redis = Redis(host=_test_redis_host, port=_test_redis_port, db=_test_redis_db, decode_responses=True)

# ################################################################################################################################

    def _get_disk_store_dir(self) -> 'str':
        """ Returns the path to the server's pubsub-messages directory.
        """
        out = os.path.join(TestConfig.server_directory, 'work', 'pubsub-messages')
        return out

# ################################################################################################################################

    def _find_file_on_disk(self, data_ref:'str') -> 'bool':
        """ Checks whether a file for the given data_ref exists on disk.
        """
        disk_store_dir = self._get_disk_store_dir()
        full_path = os.path.join(disk_store_dir, data_ref)

        if os.path.exists(full_path):
            logger.info('_find_file_on_disk -> found %s', full_path)
            return True

        return False

# ################################################################################################################################

    def _get_published_data_refs(self, topic_name:'str', count:'int') -> 'strlist':
        """ Reads the last N data_refs from the stream for the given topic.
        """
        stream_key = f'{_Stream_Prefix}{topic_name}'
        entries:'anylist' = cast_('anylist', self.redis.xrevrange(stream_key, count=count))

        data_refs:'strlist' = []

        for entry in entries:
            _, message_data = entry
            data_ref = message_data['data_ref']
            data_refs.append(data_ref)

        logger.info('_get_published_data_refs -> topic:%s, count:%d, refs:%s', topic_name, len(data_refs), data_refs)
        return data_refs

# ################################################################################################################################

    def _run_cleanup_once(self) -> 'None':
        """ Runs the cleanup subprocess in --once mode against the real server directory.
        """
        server_directory = TestConfig.server_directory

        cleanup_command = [
            _python_bin, '-m', _cleanup_module,
            server_directory,
            '--interval', '1',
            '--batch-size', '100',
            '--redis-host', _test_redis_host,
            '--redis-port', str(_test_redis_port),
            '--redis-db', str(_test_redis_db),
            '--once',
        ]

        result = subprocess.run(cleanup_command, capture_output=True, text=True, check=False, timeout=30)
        logger.info('Cleanup process exited -> returncode:%d, stdout:%s', result.returncode, result.stdout)

        self.assertEqual(result.returncode, 0)

# ################################################################################################################################

    def assert_files_exist(self, data_refs:'strlist') -> 'None':
        """ Asserts that all given data_refs have corresponding files on disk.
        """
        for data_ref in data_refs:
            found = self._find_file_on_disk(data_ref)
            self.assertTrue(found, f'Expected file for {data_ref} to exist')

# ################################################################################################################################

    def assert_files_gone(self, data_refs:'strlist') -> 'None':
        """ Asserts that none of the given data_refs have files on disk.
        """
        for data_ref in data_refs:
            found = self._find_file_on_disk(data_ref)
            self.assertFalse(found, f'Expected file for {data_ref} to be deleted')

# ################################################################################################################################

    def assert_pending_gone(self, data_refs:'strlist') -> 'None':
        """ Asserts that none of the given data_refs have pending sets in Redis.
        """
        for data_ref in data_refs:
            pending_key = f'{_Pending_Prefix}{data_ref}'
            exists = cast_('int', self.redis.exists(pending_key))
            self.assertEqual(exists, 0)

# ################################################################################################################################

    def assert_expiry_gone(self, data_refs:'strlist') -> 'None':
        """ Asserts that none of the given data_refs have expiry entries in Redis.
        """
        for data_ref in data_refs:
            score = self.redis.zscore(_Pending_Expiry_Key, data_ref)
            self.assertIsNone(score)

# ################################################################################################################################

    def assert_all_cleaned(self, data_refs:'strlist') -> 'None':
        """ Asserts that files, pending sets, and expiry entries are all gone for the given data_refs.
        """
        self.assert_files_gone(data_refs)
        self.assert_pending_gone(data_refs)
        self.assert_expiry_gone(data_refs)

# ################################################################################################################################

    def assert_all_present(self, data_refs:'strlist') -> 'None':
        """ Asserts that files, pending sets, and expiry entries all exist for the given data_refs.
        """
        self.assert_files_exist(data_refs)

        for data_ref in data_refs:
            pending_key = f'{_Pending_Prefix}{data_ref}'
            exists = cast_('int', self.redis.exists(pending_key))
            self.assertGreater(exists, 0)

            score = self.redis.zscore(_Pending_Expiry_Key, data_ref)
            self.assertIsNotNone(score)

# ################################################################################################################################
# ################################################################################################################################
