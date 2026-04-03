# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
from base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

class TestMultipleTopicSubscriptions(BaseTestCase):

    def test_subscribe_to_multiple_topics(self) -> 'None':
        """ Test that a client can subscribe to multiple topics simultaneously.
        """
        client = self.get_client()
        topic1 = 'demo.1'
        topic2 = 'demo.2'

        result1 = client.subscribe(topic1)
        self.assertTrue(result1.get('is_ok'), 'Subscribe to topic1 should succeed')

        result2 = client.subscribe(topic2)
        self.assertTrue(result2.get('is_ok'), 'Subscribe to topic2 should succeed')

        client.publish(topic1, 'message for topic1')
        client.publish(topic2, 'message for topic2')

        result = client.get_messages()
        self.assertTrue(result.get('is_ok'), 'Get messages should succeed')

        messages = result.get('messages', [])
        self.assertGreaterEqual(len(messages), 2, 'Should have messages from both topics')

        topic_names = [m.get('meta', {}).get('topic_name') for m in messages]
        self.assertIn('demo.1', topic_names, 'Should have message from topic1')
        self.assertIn('demo.2', topic_names, 'Should have message from topic2')

        client.unsubscribe(topic1)
        client.unsubscribe(topic2)

# ################################################################################################################################
# ################################################################################################################################

class TestResubscribeAfterUnsubscribe(BaseTestCase):

    def test_resubscribe_same_topic(self) -> 'None':
        """ Test that a client can re-subscribe to a topic after unsubscribing.
        """
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'First subscribe should succeed')

        result = client.unsubscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Unsubscribe should succeed')

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Re-subscribe should succeed')

        client.publish(topic, 'message after resubscribe')

        result = client.get_messages()
        self.assertTrue(result.get('is_ok'), 'Get messages should succeed')

        messages = result.get('messages', [])
        self.assertGreaterEqual(len(messages), 1, 'Should receive message after resubscribe')

        client.unsubscribe(topic)

# ################################################################################################################################

    def test_multiple_subscribe_unsubscribe_cycles(self) -> 'None':
        """ Test multiple subscribe/unsubscribe cycles on the same topic.
        """
        client = self.get_client()
        topic = self.config.topic_allowed

        for i in range(3):
            result = client.subscribe(topic)
            self.assertTrue(result.get('is_ok'), f'Subscribe cycle {i+1} should succeed')

            client.publish(topic, f'message cycle {i+1}')

            result = client.get_messages()
            self.assertTrue(result.get('is_ok'), f'Get messages cycle {i+1} should succeed')

            messages = result.get('messages', [])
            self.assertGreaterEqual(len(messages), 1, f'Should have message in cycle {i+1}')

            result = client.unsubscribe(topic)
            self.assertTrue(result.get('is_ok'), f'Unsubscribe cycle {i+1} should succeed')

# ################################################################################################################################
# ################################################################################################################################

class TestSubscriptionKeyReuse(BaseTestCase):

    def test_sub_key_returned_on_subscribe(self) -> 'None':
        """ Test that subscription returns a sub_key.
        """
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Subscribe should succeed')

        sub_key = result.get('sub_key')
        self.assertIsNotNone(sub_key, 'Subscribe should return a sub_key')
        self.assertTrue(sub_key.startswith('zpsk.'), 'sub_key should have correct prefix')

        client.unsubscribe(topic)

# ################################################################################################################################

    def test_sub_key_consistent_across_subscriptions(self) -> 'None':
        """ Test that the same sub_key is used for subsequent subscriptions.
        """
        client = self.get_client()
        topic1 = 'demo.1'
        topic2 = 'demo.2'

        result1 = client.subscribe(topic1)
        self.assertTrue(result1.get('is_ok'), 'Subscribe to topic1 should succeed')
        sub_key1 = result1.get('sub_key')

        result2 = client.subscribe(topic2)
        self.assertTrue(result2.get('is_ok'), 'Subscribe to topic2 should succeed')
        sub_key2 = result2.get('sub_key')

        self.assertEqual(sub_key1, sub_key2, 'Same sub_key should be used for both subscriptions')

        client.unsubscribe(topic1)
        client.unsubscribe(topic2)

# ################################################################################################################################
# ################################################################################################################################

class TestConcurrentClientSubscriptions(BaseTestCase):

    def test_two_clients_same_topic_independent_messages(self) -> 'None':
        """ Test that two clients subscribed to the same topic receive independent message copies.
        """
        client1 = self.get_client()
        client2 = self.get_client2()
        topic = self.config.topic_allowed

        result1 = client1.subscribe(topic)
        self.assertTrue(result1.get('is_ok'), 'Client1 subscribe should succeed')

        result2 = client2.subscribe(topic)
        self.assertTrue(result2.get('is_ok'), 'Client2 subscribe should succeed')

        client1.publish(topic, 'shared message')

        result1 = client1.get_messages()
        self.assertTrue(result1.get('is_ok'), 'Client1 get messages should succeed')
        messages1 = result1.get('messages', [])
        self.assertGreaterEqual(len(messages1), 1, 'Client1 should receive the message')

        result2 = client2.get_messages()
        self.assertTrue(result2.get('is_ok'), 'Client2 get messages should succeed')
        messages2 = result2.get('messages', [])
        self.assertGreaterEqual(len(messages2), 1, 'Client2 should receive the message')

        client1.unsubscribe(topic)
        client2.unsubscribe(topic)

# ################################################################################################################################

    def test_client_receives_only_own_subscribed_topics(self) -> 'None':
        """ Test that a client only receives messages from topics it subscribed to.
        """
        client1 = self.get_client()
        client2 = self.get_client2()
        topic1 = 'demo.3'
        topic2 = 'orders.processed'

        result = client1.subscribe(topic1)
        self.assertTrue(result.get('is_ok'), 'Client1 subscribe to topic1 should succeed')

        result = client2.subscribe(topic2)
        self.assertTrue(result.get('is_ok'), 'Client2 subscribe to topic2 should succeed')

        client1.publish(topic1, 'message for topic1')
        client1.publish(topic2, 'message for topic2')

        result1 = client1.get_messages()
        self.assertTrue(result1.get('is_ok'), 'Client1 get messages should succeed')
        messages1 = result1.get('messages', [])

        result2 = client2.get_messages()
        self.assertTrue(result2.get('is_ok'), 'Client2 get messages should succeed')
        messages2 = result2.get('messages', [])

        topics1 = [m.get('meta', {}).get('topic_name') for m in messages1]
        topics2 = [m.get('meta', {}).get('topic_name') for m in messages2]

        self.assertIn('demo.3', topics1, 'Client1 should receive topic1 message')
        self.assertNotIn('orders.processed', topics1, 'Client1 should not receive topic2 message')

        self.assertIn('orders.processed', topics2, 'Client2 should receive topic2 message')
        self.assertNotIn('demo.3', topics2, 'Client2 should not receive topic1 message')

        client1.unsubscribe(topic1)
        client2.unsubscribe(topic2)

# ################################################################################################################################
# ################################################################################################################################

class TestSubscriptionPersistence(BaseTestCase):

    def test_subscription_persists_across_requests(self) -> 'None':
        """ Test that subscription persists across multiple HTTP requests.
        """
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Subscribe should succeed')

        client.publish(topic, 'message 1')

        result = client.get_messages()
        self.assertTrue(result.get('is_ok'), 'First get messages should succeed')
        messages1 = result.get('messages', [])
        self.assertGreaterEqual(len(messages1), 1, 'Should receive first message')

        client.publish(topic, 'message 2')

        result = client.get_messages()
        self.assertTrue(result.get('is_ok'), 'Second get messages should succeed')
        messages2 = result.get('messages', [])
        self.assertGreaterEqual(len(messages2), 1, 'Should receive second message')

        client.unsubscribe(topic)

# ################################################################################################################################

    def test_messages_not_received_after_unsubscribe(self) -> 'None':
        """ Test that messages published after unsubscribe are not received.
        """
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Subscribe should succeed')

        client.publish(topic, 'message before unsubscribe')

        result = client.get_messages()
        messages_before = result.get('messages', [])
        self.assertGreaterEqual(len(messages_before), 1, 'Should receive message before unsubscribe')

        result = client.unsubscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Unsubscribe should succeed')

        client.publish(topic, 'message after unsubscribe')

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Re-subscribe should succeed')

        result = client.get_messages()
        messages_after = result.get('messages', [])

        data_list = [m.get('data') for m in messages_after]
        self.assertNotIn('message after unsubscribe', data_list,
            'Should not receive message published while unsubscribed')

        client.unsubscribe(topic)

# ################################################################################################################################
# ################################################################################################################################
