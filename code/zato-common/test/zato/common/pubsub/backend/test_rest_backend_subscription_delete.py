# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase
from unittest.mock import Mock

# Zato
from zato.common.pubsub.backend.rest_backend import RESTBackend

# ################################################################################################################################
# ################################################################################################################################

class RESTBackendSubscriptionDeleteTestCase(TestCase):

    def setUp(self):
        self.rest_server = Mock()
        self.rest_server.users = {}
        self.broker_client = Mock()
        self.backend = RESTBackend(self.rest_server, self.broker_client)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE_single_topic_single_user(self):

        # Create initial subscription
        initial_msg = {
            'cid': 'setup-cid',
            'sub_key': 'sk-delete-123',
            'sec_name': 'test_user',
            'topic_name_list': ['orders.test']
        }
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(initial_msg)

        # Verify subscription exists
        self.assertIn('orders.test', self.backend.subs_by_topic)
        self.assertIn('test_user', self.backend.subs_by_topic['orders.test'])

        # Delete subscription
        delete_msg = {
            'cid': 'delete-cid-123',
            'sub_key': 'sk-delete-123',
            'sec_name': 'test_user',
            'topic_name': 'orders.test'
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE(delete_msg)

        # Assert subscription was removed
        self.assertNotIn('orders.test', self.backend.subs_by_topic)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE_multiple_users_same_topic(self):

        # Create subscriptions for multiple users on same topic
        for i, user in enumerate(['user1', 'user2', 'user3']):
            initial_msg = {
                'cid': f'setup-cid-{i}',
                'sub_key': f'sk-multi-{i}',
                'sec_name': user,
                'topic_name_list': ['shared.topic']
            }
            self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(initial_msg)

        # Verify all subscriptions exist
        self.assertIn('shared.topic', self.backend.subs_by_topic)
        for user in ['user1', 'user2', 'user3']:
            self.assertIn(user, self.backend.subs_by_topic['shared.topic'])

        # Delete subscription for user2
        delete_msg = {
            'cid': 'delete-cid-multi',
            'sub_key': 'sk-multi-1',
            'sec_name': 'user2',
            'topic_name': 'shared.topic'
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE(delete_msg)

        # Assert user2 subscription was removed but others remain
        self.assertIn('shared.topic', self.backend.subs_by_topic)
        self.assertIn('user1', self.backend.subs_by_topic['shared.topic'])
        self.assertNotIn('user2', self.backend.subs_by_topic['shared.topic'])
        self.assertIn('user3', self.backend.subs_by_topic['shared.topic'])

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE_user_with_multiple_topics(self):

        # Create subscriptions for one user on multiple topics
        topics = ['orders.new', 'invoices.paid', 'alerts.critical']
        for i, topic in enumerate(topics):
            initial_msg = {
                'cid': f'setup-cid-{i}',
                'sub_key': f'sk-topic-{i}',
                'sec_name': 'multi_topic_user',
                'topic_name_list': [topic]
            }
            self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(initial_msg)

        # Verify all subscriptions exist
        for topic in topics:
            self.assertIn(topic, self.backend.subs_by_topic)
            self.assertIn('multi_topic_user', self.backend.subs_by_topic[topic])

        # Delete subscription for one topic
        delete_msg = {
            'cid': 'delete-cid-one-topic',
            'sub_key': 'sk-topic-1',
            'sec_name': 'multi_topic_user',
            'topic_name': 'invoices.paid'
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE(delete_msg)

        # Assert only the specified subscription was removed
        self.assertIn('orders.new', self.backend.subs_by_topic)
        self.assertIn('multi_topic_user', self.backend.subs_by_topic['orders.new'])

        self.assertNotIn('invoices.paid', self.backend.subs_by_topic)

        self.assertIn('alerts.critical', self.backend.subs_by_topic)
        self.assertIn('multi_topic_user', self.backend.subs_by_topic['alerts.critical'])

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE_nonexistent_subscription(self):

        # Try to delete a subscription that doesn't exist
        delete_msg = {
            'cid': 'delete-cid-nonexistent',
            'sub_key': 'sk-nonexistent-999',
            'sec_name': 'nonexistent_user',
            'topic_name': 'nonexistent.topic'
        }

        # Call the method under test - should not raise an exception
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE(delete_msg)

        # Assert no topics were affected
        self.assertEqual(len(self.backend.subs_by_topic), 0)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE_wrong_user_for_subscription(self):

        # Create subscription for user1
        initial_msg = {
            'cid': 'setup-cid',
            'sub_key': 'sk-wrong-user-123',
            'sec_name': 'user1',
            'topic_name_list': ['test.topic']
        }
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(initial_msg)

        # Verify subscription exists
        self.assertIn('test.topic', self.backend.subs_by_topic)
        self.assertIn('user1', self.backend.subs_by_topic['test.topic'])

        # Try to delete with wrong user
        delete_msg = {
            'cid': 'delete-cid-wrong-user',
            'sub_key': 'sk-wrong-user-123',
            'sec_name': 'user2',
            'topic_name': 'test.topic'
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE(delete_msg)

        # Assert original subscription still exists
        self.assertIn('test.topic', self.backend.subs_by_topic)
        self.assertIn('user1', self.backend.subs_by_topic['test.topic'])

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE_cleans_up_empty_topics(self):

        # Create subscription
        initial_msg = {
            'cid': 'setup-cid',
            'sub_key': 'sk-cleanup-456',
            'sec_name': 'cleanup_user',
            'topic_name_list': ['cleanup.topic']
        }
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(initial_msg)

        # Verify subscription exists
        self.assertIn('cleanup.topic', self.backend.subs_by_topic)
        self.assertIn('cleanup_user', self.backend.subs_by_topic['cleanup.topic'])

        # Delete the only subscription for this topic
        delete_msg = {
            'cid': 'delete-cid-cleanup',
            'sub_key': 'sk-cleanup-456',
            'sec_name': 'cleanup_user',
            'topic_name': 'cleanup.topic'
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE(delete_msg)

        # Assert topic was completely removed from subs_by_topic
        self.assertNotIn('cleanup.topic', self.backend.subs_by_topic)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE_preserves_topic_object(self):

        # Create topic first
        self.backend.create_topic('test-cid', 'test', 'preserve.topic')

        # Create subscription
        initial_msg = {
            'cid': 'setup-cid',
            'sub_key': 'sk-preserve-789',
            'sec_name': 'preserve_user',
            'topic_name_list': ['preserve.topic']
        }
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(initial_msg)

        # Verify topic and subscription exist
        self.assertIn('preserve.topic', self.backend.topics)
        self.assertIn('preserve.topic', self.backend.subs_by_topic)

        # Delete subscription
        delete_msg = {
            'cid': 'delete-cid-preserve',
            'sub_key': 'sk-preserve-789',
            'sec_name': 'preserve_user',
            'topic_name': 'preserve.topic'
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE(delete_msg)

        # Assert topic object still exists but subscription is gone
        self.assertIn('preserve.topic', self.backend.topics)
        self.assertNotIn('preserve.topic', self.backend.subs_by_topic)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE_with_empty_topic_name(self):

        # Try to delete with empty topic name
        delete_msg = {
            'cid': 'delete-cid-empty',
            'sub_key': 'sk-empty-000',
            'sec_name': 'empty_user',
            'topic_name': ''
        }

        # Call the method under test - should not raise an exception
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE(delete_msg)

        # Assert no topics were affected
        self.assertEqual(len(self.backend.subs_by_topic), 0)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE_with_none_topic_name(self):

        # Try to delete with None topic name
        delete_msg = {
            'cid': 'delete-cid-none',
            'sub_key': 'sk-none-000',
            'sec_name': 'none_user',
            'topic_name': None
        }

        # Call the method under test - should not raise an exception
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE(delete_msg)

        # Assert no topics were affected
        self.assertEqual(len(self.backend.subs_by_topic), 0)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE_complex_scenario(self):

        # Create complex subscription scenario
        users = ['alice', 'bob', 'charlie']
        topics = ['orders.new', 'orders.paid', 'alerts.high']

        # Create subscriptions for all users on all topics
        sub_key_counter = 0
        for user in users:
            for topic in topics:
                initial_msg = {
                    'cid': f'setup-cid-{sub_key_counter}',
                    'sub_key': f'sk-complex-{sub_key_counter}',
                    'sec_name': user,
                    'topic_name_list': [topic]
                }
                self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(initial_msg)
                sub_key_counter += 1

        # Verify all subscriptions exist
        for topic in topics:
            self.assertIn(topic, self.backend.subs_by_topic)
            for user in users:
                self.assertIn(user, self.backend.subs_by_topic[topic])

        # Delete alice's subscription to orders.new
        delete_msg = {
            'cid': 'delete-cid-complex',
            'sub_key': 'sk-complex-0',
            'sec_name': 'alice',
            'topic_name': 'orders.new'
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE(delete_msg)

        # Assert alice's subscription to orders.new was removed
        self.assertIn('orders.new', self.backend.subs_by_topic)
        self.assertNotIn('alice', self.backend.subs_by_topic['orders.new'])
        self.assertIn('bob', self.backend.subs_by_topic['orders.new'])
        self.assertIn('charlie', self.backend.subs_by_topic['orders.new'])

        # Assert alice's other subscriptions remain
        self.assertIn('orders.paid', self.backend.subs_by_topic)
        self.assertIn('alice', self.backend.subs_by_topic['orders.paid'])

        self.assertIn('alerts.high', self.backend.subs_by_topic)
        self.assertIn('alice', self.backend.subs_by_topic['alerts.high'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
