# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import subprocess
import sys
import unittest

# Zato
from zato.common.test import pubsub_db

# local
from zato.common.test.client import PublishClient
from zato.common.test.config_pubsub_push import TestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_push.base_cleanup_live')

_python_bin = sys.executable

_cleanup_module = 'zato.common.pubsub.sql.cleanup'

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

    def _run_cleanup_once(self) -> 'None':
        """ Runs the cleanup subprocess in --once mode against the shared pub/sub database.
        The Zato_PubSub_DB_* variables are inherited from this test process's environment.
        """
        cleanup_command = [
            _python_bin, '-m', _cleanup_module,
            '--once',
        ]

        result = subprocess.run(cleanup_command, capture_output=True, text=True, check=False, timeout=30)
        logger.info('Cleanup process exited -> returncode:%d, stdout:%s', result.returncode, result.stdout)

        self.assertEqual(result.returncode, 0)

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
