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
        """ Pulled messages must contain all documented pub/sub metadata fields.
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

        # .. verify all documented metadata fields are present.
        self.assertIn('topic_name', meta)
        self.assertIn('msg_id', meta)
        self.assertIn('correl_id', meta)
        self.assertIn('sub_key', meta)
        self.assertIn('priority', meta)
        self.assertIn('size', meta)
        self.assertIn('expiration', meta)
        self.assertIn('pub_time_iso', meta)
        self.assertIn('recv_time_iso', meta)
        self.assertIn('expiration_time_iso', meta)

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

    def test_priority_value_round_trips(self) -> 'None':
        """ Publishing with priority=9 must result in the pulled message
        having meta.priority equal to 9.
        """
        topic_name = _active_endpoints[0]
        data = {'pull_test': 'priority_round_trip'}

        result = self.publish(topic_name, data, priority=9)
        self.assertTrue(result['is_ok'])

        time.sleep(2)

        pull_result = self.pull_messages()
        self.assertTrue(pull_result['is_ok'])

        message_count = pull_result['message_count']
        self.assertGreaterEqual(message_count, 1)

        meta = pull_result['messages'][0]['meta']
        self.assertEqual(meta['priority'], 9)

# ################################################################################################################################

    def test_priority_ordering(self) -> 'None':
        """ Messages published with different priorities must be pulled
        in descending priority order (highest first).
        """
        topic_name = _active_endpoints[0]

        # Drain the queue before the test ..
        _ = self.pull_messages()

        # Publish three messages: low priority first, then high, then mid ..
        result_low = self.publish(topic_name, {'pull_test': 'priority_order', 'level': 'low'}, priority=1)
        self.assertTrue(result_low['is_ok'])

        result_high = self.publish(topic_name, {'pull_test': 'priority_order', 'level': 'high'}, priority=9)
        self.assertTrue(result_high['is_ok'])

        result_mid = self.publish(topic_name, {'pull_test': 'priority_order', 'level': 'mid'}, priority=5)
        self.assertTrue(result_mid['is_ok'])

        time.sleep(2)

        # Pull all three and verify they come back in 9, 5, 1 order ..
        pull_result = self.pull_messages()
        self.assertTrue(pull_result['is_ok'])

        message_count = pull_result['message_count']
        self.assertGreaterEqual(message_count, 3)

        messages = pull_result['messages']

        first_priority = messages[0]['meta']['priority']
        second_priority = messages[1]['meta']['priority']
        third_priority = messages[2]['meta']['priority']

        self.assertEqual(first_priority, 9)
        self.assertEqual(second_priority, 5)
        self.assertEqual(third_priority, 1)

# ################################################################################################################################

    def test_publish_with_correl_id(self) -> 'None':
        """ Publishing with a custom correl_id must result in the pulled
        message having that same correl_id in its metadata.
        """
        topic_name = _active_endpoints[0]
        data = {'pull_test': 'correl_id_check'}

        result = self.publish(topic_name, data, correl_id='test-correl-123')
        self.assertTrue(result['is_ok'])

        time.sleep(2)

        pull_result = self.pull_messages()
        self.assertTrue(pull_result['is_ok'])

        message_count = pull_result['message_count']
        self.assertGreaterEqual(message_count, 1)

        meta = pull_result['messages'][0]['meta']
        self.assertEqual(meta['correl_id'], 'test-correl-123')

# ################################################################################################################################

    def test_publish_with_in_reply_to(self) -> 'None':
        """ Publishing with in_reply_to must result in the pulled message
        having that value in its metadata.
        """
        topic_name = _active_endpoints[0]
        data = {'pull_test': 'in_reply_to_check'}

        result = self.publish(topic_name, data, in_reply_to='zpsm-original-001')
        self.assertTrue(result['is_ok'])

        time.sleep(2)

        pull_result = self.pull_messages()
        self.assertTrue(pull_result['is_ok'])

        message_count = pull_result['message_count']
        self.assertGreaterEqual(message_count, 1)

        meta = pull_result['messages'][0]['meta']
        self.assertEqual(meta['in_reply_to'], 'zpsm-original-001')

# ################################################################################################################################

    def test_publish_with_ext_client_id(self) -> 'None':
        """ Publishing with ext_client_id must result in the pulled message
        having that value in its metadata.
        """
        topic_name = _active_endpoints[0]
        data = {'pull_test': 'ext_client_id_check'}

        result = self.publish(topic_name, data, ext_client_id='external-system-42')
        self.assertTrue(result['is_ok'])

        time.sleep(2)

        pull_result = self.pull_messages()
        self.assertTrue(pull_result['is_ok'])

        message_count = pull_result['message_count']
        self.assertGreaterEqual(message_count, 1)

        meta = pull_result['messages'][0]['meta']
        self.assertEqual(meta['ext_client_id'], 'external-system-42')

# ################################################################################################################################

    def test_publish_with_pub_time(self) -> 'None':
        """ Publishing with a custom pub_time must result in the pulled
        message reflecting that timestamp in its metadata.
        """
        topic_name = _active_endpoints[0]
        data = {'pull_test': 'pub_time_check'}

        result = self.publish(topic_name, data, pub_time='2025-06-01T12:00:00+00:00')
        self.assertTrue(result['is_ok'])

        time.sleep(2)

        pull_result = self.pull_messages()
        self.assertTrue(pull_result['is_ok'])

        message_count = pull_result['message_count']
        self.assertGreaterEqual(message_count, 1)

        meta = pull_result['messages'][0]['meta']
        pub_time_iso = meta['pub_time_iso']
        self.assertTrue(pub_time_iso.startswith('2025-06-01'), f'Expected pub_time_iso to start with 2025-06-01, got {pub_time_iso}')

# ################################################################################################################################

    def test_pull_max_messages(self) -> 'None':
        """ Pulling with max_messages=2 when 5 messages are enqueued
        must return exactly 2.
        """
        topic_name = _active_endpoints[0]

        # Drain the queue ..
        _ = self.pull_messages()

        # Publish 5 messages ..
        for message_index in range(5):
            data = {'pull_test': 'max_messages', 'index': message_index}
            result = self.publish(topic_name, data)
            self.assertTrue(result['is_ok'])

        time.sleep(2)

        # Pull with max_messages=2 ..
        pull_result = self.pull_messages(max_messages=2)
        self.assertTrue(pull_result['is_ok'])

        message_count = pull_result['message_count']
        self.assertEqual(message_count, 2)

# ################################################################################################################################

    def test_pull_max_len(self) -> 'None':
        """ Pulling with a very small max_len must limit the number of
        messages returned based on their cumulative data size.
        """
        topic_name = _active_endpoints[0]

        # Drain the queue ..
        _ = self.pull_messages()

        # Publish a message with a 1000-byte payload ..
        large_value = 'x' * 1000
        data = {'pull_test': 'max_len', 'payload': large_value}

        result = self.publish(topic_name, data)
        self.assertTrue(result['is_ok'])

        time.sleep(2)

        # Pull with max_len=100 - the message exceeds max_len
        # so the server should return 0 messages ..
        pull_result = self.pull_messages(max_len=100)
        self.assertTrue(pull_result['is_ok'])

        message_count = pull_result['message_count']
        self.assertEqual(message_count, 0)

# ################################################################################################################################
# ################################################################################################################################
