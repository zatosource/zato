# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import time

# local
from base import BasePullTestCase
from config import _active_endpoints

# ################################################################################################################################
# ################################################################################################################################

class TestPullDelivery(BasePullTestCase):
    """ Pull delivery tests using the puller user's subscription across all active topics.
    """

    def test_pull_single_topic(self) -> 'None':
        """ Publishing to the first active topic and pulling must return the message.
        """
        topic_name = _active_endpoints[0]
        data = {'pull_test': 'single_topic', 'topic': topic_name}

        result = self.publish(topic_name, data)
        self.assertTrue(result['is_ok'])

        # Give the server a moment to process
        time.sleep(2)

        pull_result = self.pull_messages()
        self.assertTrue(pull_result['is_ok'])

        message_count = pull_result['message_count']
        self.assertGreaterEqual(message_count, 1)

        serialized = json.dumps(pull_result['messages'])
        self.assertIn('single_topic', serialized)

# ################################################################################################################################

    def test_pull_multiple_topics(self) -> 'None':
        """ Publishing to all active topics and pulling must return messages from all of them.
        """

        # Publish one message per active topic ..
        for topic_name in _active_endpoints:
            data = {'pull_test': 'multi_topic', 'source_topic': topic_name}
            result = self.publish(topic_name, data)
            self.assertTrue(result['is_ok'])

        # Give the server a moment to process
        time.sleep(2)

        pull_result = self.pull_messages()
        self.assertTrue(pull_result['is_ok'])

        message_count = pull_result['message_count']
        active_count = len(_active_endpoints)
        self.assertGreaterEqual(message_count, active_count)

# ################################################################################################################################

    def test_pull_consume_once(self) -> 'None':
        """ After pulling messages, a second pull must return zero messages.
        """
        topic_name = _active_endpoints[0]
        data = {'pull_test': 'consume_once'}

        result = self.publish(topic_name, data)
        self.assertTrue(result['is_ok'])

        # Give the server a moment to process
        time.sleep(2)

        # First pull should get the message
        first_pull = self.pull_messages()
        self.assertTrue(first_pull['is_ok'])

        first_count = first_pull['message_count']
        self.assertGreaterEqual(first_count, 1)

        # Second pull should get zero
        second_pull = self.pull_messages()
        self.assertTrue(second_pull['is_ok'])

        second_count = second_pull['message_count']
        self.assertEqual(second_count, 0)

# ################################################################################################################################

    def test_pull_metadata_fields(self) -> 'None':
        """ Pulled messages must contain standard pub/sub metadata fields.
        """
        topic_name = _active_endpoints[0]
        data = {'pull_test': 'metadata_check', 'value': 42}

        result = self.publish(topic_name, data)
        self.assertTrue(result['is_ok'])

        # Give the server a moment to process
        time.sleep(2)

        pull_result = self.pull_messages()
        self.assertTrue(pull_result['is_ok'])

        message_count = pull_result['message_count']
        self.assertGreaterEqual(message_count, 1)

        first_message = pull_result['messages'][0]

        # The message must have data and meta sections ..
        self.assertIn('data', first_message)
        self.assertIn('meta', first_message)

        meta = first_message['meta']

        # .. verify standard metadata fields are present.
        self.assertIn('topic_name', meta)
        self.assertIn('msg_id', meta)
        self.assertIn('correl_id', meta)
        self.assertIn('sub_key', meta)
        self.assertIn('priority', meta)

# ################################################################################################################################

    def test_expired_message_not_pulled(self) -> 'None':
        """ A message published with a 1-second TTL must not be available
        for pull after the TTL expires.
        """
        topic_name = _active_endpoints[0]

        data = {'pull_test': 'ttl_expiration', 'marker': 'should-expire'}

        # Drain the pull queue immediately before publishing
        # so we have a clean baseline ..
        _ = self.pull_messages()

        result = self.publish(topic_name, data, expiration=1)
        self.assertTrue(result['is_ok'])

        # Wait for the message to expire ..
        time.sleep(3)

        pull_result = self.pull_messages()
        self.assertTrue(pull_result['is_ok'])

        message_count = pull_result['message_count']
        self.assertEqual(message_count, 0)

# ################################################################################################################################
# ################################################################################################################################
