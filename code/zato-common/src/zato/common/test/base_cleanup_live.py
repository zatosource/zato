# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import sqlite3
import subprocess
import sys
import time
import unittest

# Zato
from zato.common.pubsub.sql.config import get_pubsub_db_path
from zato.common.test import pubsub_db

# local
from zato.common.test.client import PublishClient, PullClient
from zato.common.test.config_pubsub_push import TestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_push.base_cleanup_live')

_python_bin = sys.executable

_cleanup_module = 'zato.common.pubsub.sql.cleanup'

_cleanup_command = [_python_bin, '-m', _cleanup_module, '--once']

# How long a test waits at most for every subscriber to acknowledge its messages, in seconds.
_delivery_timeout_seconds = 30

# How often a test checks whether its messages were acknowledged, in seconds.
_delivery_poll_seconds = 0.2

# ################################################################################################################################
# ################################################################################################################################

class BaseCleanupLiveTestCase(unittest.TestCase):
    """ Shared setup and helpers for all live cleanup tests that publish via the REST API
    and run the cleanup subprocess against the same pub/sub database the server uses.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.publisher = PublishClient(
            TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
        class_.puller = PullClient(
            TestConfig.base_url, TestConfig.puller_username, TestConfig.puller_password)

# ################################################################################################################################

    def publish_messages(self, topic_name:'str', count:'int', expiration:'int') -> 'strlist':
        """ Publishes the requested number of messages and returns their msg_ids.
        """
        out:'strlist' = []

        for _ in range(count):
            result = self.publisher.publish(topic_name, 'cleanup test payload', expiration=expiration)
            msg_id = result['msg_id']
            out.append(msg_id)

        logger.info('publish_messages -> topic:%s, count:%d, msg_ids:%s', topic_name, len(out), out)
        return out

# ################################################################################################################################

    def _run_cleanup_once(self, extra_env:'strstrdict | None'=None) -> 'None':
        """ Runs the cleanup subprocess in --once mode against the shared pub/sub database.
        Zato_PubSub_DB_Path is inherited from this test process's environment,
        and extra_env adds the settings that one test needs.
        """
        env = dict(os.environ)

        if extra_env:
            env.update(extra_env)

        result = subprocess.run(_cleanup_command, capture_output=True, text=True, check=False, timeout=30, env=env)
        logger.info('Cleanup process exited -> returncode:%d, stderr:%s', result.returncode, result.stderr)

        self.assertEqual(result.returncode, 0, result.stderr)

# ################################################################################################################################

    def _run_cleanup_while_locked(self, lock_seconds:'float') -> 'str':
        """ Runs the cleanup subprocess in --once mode while another connection holds the write lock
        of the shared pub/sub database for the given time, and returns what the subprocess logged.
        """
        db_path = get_pubsub_db_path()

        lock_connection = sqlite3.connect(db_path, isolation_level=None)
        _ = lock_connection.execute('begin immediate')

        process = subprocess.Popen(_cleanup_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        # The lock is held while the cleanup process runs ..
        time.sleep(lock_seconds)

        # .. and released, after which the sweep may complete.
        _ = lock_connection.execute('rollback')
        lock_connection.close()

        output, _ = process.communicate(timeout=30)
        logger.info('Cleanup process exited -> returncode:%d, output:%s', process.returncode, output)

        self.assertEqual(process.returncode, 0, output)

        return output

# ################################################################################################################################

    def drain_puller(self) -> 'None':
        """ Pulls and acknowledges everything pending for the pull subscriber of all the topics.
        """
        self.puller.drain()

# ################################################################################################################################

    def wait_until_delivered(self, msg_ids:'strlist') -> 'None':
        """ Waits until every subscriber has acknowledged the given messages, which drops their payloads.
        """
        deadline = time.monotonic() + _delivery_timeout_seconds

        while True:
            payload_count = pubsub_db.count_messages_with_payload(msg_ids)
            if payload_count == 0:
                break
            self.assertLess(time.monotonic(), deadline, f'{payload_count} of {msg_ids} not delivered')
            time.sleep(_delivery_poll_seconds)

# ################################################################################################################################

    def assert_all_cleaned(self, msg_ids:'strlist') -> 'None':
        """ Asserts that none of the given messages have any rows left in the database.
        """
        row_count = pubsub_db.count_message_rows(msg_ids)
        self.assertEqual(row_count, 0, f'Expected no message rows for {msg_ids}, found {row_count}')

# ################################################################################################################################

    def assert_all_present(self, msg_ids:'strlist') -> 'None':
        """ Asserts that all the given messages still have their rows and payloads.
        """
        expected_count = len(msg_ids)

        row_count = pubsub_db.count_message_rows(msg_ids)
        self.assertEqual(row_count, expected_count, f'Expected {expected_count} message rows, found {row_count}')

        payload_count = pubsub_db.count_messages_with_payload(msg_ids)
        self.assertEqual(payload_count, expected_count, f'Expected {expected_count} payloads, found {payload_count}')

# ################################################################################################################################
# ################################################################################################################################
