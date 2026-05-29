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
from zato.common.test.client import PublishClient, PullClient
from zato.common.test.config_pubsub_push import TestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_push.pull_delivery')

_delivery_poll_timeout  = 10
_delivery_poll_interval = 0.5

# ################################################################################################################################
# ################################################################################################################################

class TestPullDelivery(unittest.TestCase):

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
        class_.puller = PullClient(TestConfig.base_url, TestConfig.puller_username, TestConfig.puller_password)

# ################################################################################################################################

    def setUp(self) -> 'None':
        """ Drains any leftover messages before each test.
        """
        self.puller.drain()

# ################################################################################################################################

    def _poll_pull(self, expected_count:'int'=1) -> 'anydict':
        """ Polls the pull endpoint until at least expected_count messages arrive or the timeout expires.
        Retries on transient server errors.
        """
        start_time = time.monotonic()
        deadline = start_time + _delivery_poll_timeout

        while time.monotonic() < deadline:

            try:
                result = self.puller.pull(max_messages=50)
            except Exception as error:
                logger.warning('Pull attempt failed, will retry: %s', error)
                time.sleep(_delivery_poll_interval)
                continue

            message_count = result['message_count']
            if message_count >= expected_count:
                return result

            time.sleep(_delivery_poll_interval)

        # .. one final attempt after the deadline.
        out = self.puller.pull(max_messages=50)
        return out

# ################################################################################################################################

    def test_publish_one_pull_one(self) -> 'None':
        """ Publish a single message to one topic, pull it back, and verify the data matches.
        """

        # Publish a single message to the first topic ..
        topic_name = 'iam.user.created'
        publish_data = {'user_id': 'test-user-001', 'action': 'created'}

        publish_response = self.publisher.publish(topic_name, publish_data)
        logger.info('Publish response: %s', publish_response)

        # .. the publish response should contain a message ID ..
        self.assertIn('msg_id', publish_response)

        # .. pull messages and verify we get exactly one ..
        pull_response = self._poll_pull(expected_count=1)
        logger.info('Pull response: %s', pull_response)

        message_count = pull_response['message_count']
        self.assertEqual(message_count, 1, f'Expected 1 message, got {message_count}')

        # .. extract the single message ..
        messages = pull_response['messages']
        message = messages[0]
        logger.info('Pulled message: %s', message)

        # .. verify the data matches what was published.
        received_data = message['data']
        self.assertEqual(received_data, publish_data)

# ################################################################################################################################

    def test_publish_to_all_topics_pull_all(self) -> 'None':
        """ Publish one message to each of the 10 topics, pull them all, and verify all arrive.
        """

        # Publish one message per topic ..
        topic_names = [
            'iam.user.created',
            'iam.user.deleted',
            'iam.role.assigned',
            'iam.password.changed',
            'iam.login.failed',
            'customer.registered',
            'customer.updated',
            'customer.deactivated',
            'order.placed',
            'order.shipped',
        ]

        topic_count = len(topic_names)

        for topic_name in topic_names:
            publish_data = {'topic': topic_name, 'sequence': 'all-topics-test'}
            publish_response = self.publisher.publish(topic_name, publish_data)
            logger.info('Published to %s: %s', topic_name, publish_response)

        # .. pull all messages ..
        pull_response = self._poll_pull(expected_count=topic_count)
        logger.info('Pull response: %s', pull_response)

        message_count = pull_response['message_count']
        self.assertEqual(message_count, topic_count, f'Expected {topic_count} messages, got {message_count}')

        # .. verify each topic is represented exactly once ..
        messages = pull_response['messages']
        received_topics = []

        for message in messages:
            logger.info('Pulled message: %s', message)
            message_data = message['data']
            received_topics.append(message_data['topic'])

        for topic_name in topic_names:
            self.assertIn(topic_name, received_topics, f'Missing message for topic {topic_name}')

# ################################################################################################################################
# ################################################################################################################################
