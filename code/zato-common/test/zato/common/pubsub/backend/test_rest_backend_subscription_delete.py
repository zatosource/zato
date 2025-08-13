# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Must come first
from gevent import monkey;
_ = monkey.patch_all()

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
        self.broker_client.cluster_id = 'test-cluster'

        def mock_invoke_sync(service, request, timeout=20, needs_root_elem=False):
            if needs_root_elem:
                return {'error': None}
            return [
                {'username': 'test_user', 'name': 'test_user_sec'},
                {'username': 'user_one', 'name': 'user_one_sec'},
                {'username': 'user_two', 'name': 'user_two_sec'},
                {'username': 'multi_user', 'name': 'multi_user_sec'},
                {'username': 'wrong_user', 'name': 'wrong_user_sec'},
                {'username': 'user1', 'name': 'user1_sec'},
                {'username': 'user2', 'name': 'user2_sec'},
                {'username': 'multi_topic_user', 'name': 'multi_topic_user_sec'},
                {'username': 'preserve_user', 'name': 'preserve_user_sec'},
                {'username': 'alice', 'name': 'alice_sec'},
                {'username': 'bob', 'name': 'bob_sec'},
                {'username': 'charlie', 'name': 'charlie_sec'},
                {'username': 'cleanup_user', 'name': 'cleanup_user_sec'},
                {'username': 'user3', 'name': 'user3_sec'},
                {'username': 'nonexistent_user', 'name': 'nonexistent_user_sec'},
                {'username': 'empty_user', 'name': 'empty_user_sec'},
                {'username': 'none_user', 'name': 'none_user_sec'}
            ]

        self.broker_client.invoke_sync.side_effect = mock_invoke_sync

        self.backend = RESTBackend(self.rest_server, self.broker_client)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE_single_topic_single_user(self):

        # Create initial subscription
        initial_msg = {
            'cid': 'setup-cid',
            'sub_key': 'sk-delete-123',
            'sec_name': 'test_user_sec',
            'topic_name_list': ['orders.test']
        }
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(initial_msg)

        # Verify subscription exists
        self.assertIn('orders.test', self.backend.subs_by_topic)
        self.assertIn('test_user_sec', self.backend.subs_by_topic['orders.test'])

        # Delete subscription
        delete_msg = {
            'cid': 'delete-cid-123',
            'sub_key': 'sk-delete-123',
            'sec_name': 'test_user_sec'
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE(delete_msg)

        # Assert subscription was removed and topic cleaned up
        self.assertNotIn('orders.test', self.backend.subs_by_topic)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE_multiple_users_same_topic(self):

        # Create subscriptions for multiple users on same topic
        for i, user in enumerate(['user1_sec', 'user2_sec', 'user3_sec']):
            initial_msg = {
                'cid': f'setup-cid-{i}',
                'sub_key': f'sk-multi-{i}',
                'sec_name': user,
                'topic_name_list': ['shared.topic']
            }
            self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(initial_msg)

        # Verify all subscriptions exist
        self.assertIn('shared.topic', self.backend.subs_by_topic)
        for user in ['user1_sec', 'user2_sec', 'user3_sec']:
            self.assertIn(user, self.backend.subs_by_topic['shared.topic'])

        # Delete subscription for user2
        delete_msg = {
            'cid': 'delete-cid-multi',
            'sub_key': 'sk-multi-0',
            'sec_name': 'user1_sec'
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE(delete_msg)

        # Assert user2's subscription was removed
        self.assertIn('shared.topic', self.backend.subs_by_topic)
        self.assertIn('user2_sec', self.backend.subs_by_topic['shared.topic'])
        self.assertIn('user3_sec', self.backend.subs_by_topic['shared.topic'])

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE_user_with_multiple_topics(self):

        # Create subscriptions for one user on multiple topics
        for idx, topic in enumerate(['invoices.paid', 'alerts.critical']):
            initial_msg = {
                'cid': f'setup-cid-{idx}',
                'sub_key': f'sk-topic-{idx}',
                'sec_name': 'multi_topic_user_sec',
                'topic_name_list': [topic]
            }
            self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(initial_msg)

        # Verify all subscriptions exist
        for topic in ['invoices.paid', 'alerts.critical']:
            self.assertIn(topic, self.backend.subs_by_topic)
            self.assertIn('multi_topic_user_sec', self.backend.subs_by_topic[topic])

        # Delete subscription for orders.new
        delete_msg = {
            'cid': 'delete-cid-topics',
            'sub_key': 'sk-topic-0',
            'sec_name': 'multi_topic_user_sec'
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE(delete_msg)

        # Assert only invoices.paid was cleaned up (empty), alerts.critical remains
        self.assertNotIn('invoices.paid', self.backend.subs_by_topic)

        self.assertIn('alerts.critical', self.backend.subs_by_topic)
        self.assertIn('multi_topic_user_sec', self.backend.subs_by_topic['alerts.critical'])

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE_nonexistent_subscription(self):

        # Try to delete nonexistent subscription
        delete_msg = {
            'cid': 'delete-cid-nonexistent',
            'sub_key': 'sk-nonexistent-999',
            'sec_name': 'nonexistent_user_sec'
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
            'sec_name': 'user1_sec',
            'topic_name_list': ['test.topic']
        }
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(initial_msg)

        # Verify subscription exists
        self.assertIn('test.topic', self.backend.subs_by_topic)
        self.assertIn('user1_sec', self.backend.subs_by_topic['test.topic'])

        # Try to delete with wrong user
        delete_msg = {
            'cid': 'delete-cid-wrong-user',
            'sub_key': 'sk-wrong-user-123',
            'sec_name': 'user2_sec'
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE(delete_msg)

        # Assert original subscription still exists
        self.assertIn('test.topic', self.backend.subs_by_topic)
        self.assertIn('user1_sec', self.backend.subs_by_topic['test.topic'])

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE_cleans_up_empty_topics(self):

        # Create subscription
        initial_msg = {
            'cid': 'setup-cid',
            'sub_key': 'sk-cleanup-456',
            'sec_name': 'cleanup_user_sec',
            'topic_name_list': ['cleanup.topic']
        }
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(initial_msg)

        # Verify subscription exists
        self.assertIn('cleanup.topic', self.backend.subs_by_topic)
        self.assertIn('cleanup_user_sec', self.backend.subs_by_topic['cleanup.topic'])

        # Delete the only subscription for this topic
        delete_msg = {
            'cid': 'delete-cid-cleanup',
            'sub_key': 'sk-cleanup-456',
            'sec_name': 'cleanup_user_sec'
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE(delete_msg)

        # Assert topic was cleaned up from subs_by_topic
        self.assertNotIn('cleanup.topic', self.backend.subs_by_topic)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE_preserves_topic_object(self):

        # Create topic first
        self.backend.create_topic('test-cid', 'test', 'preserve.topic')

        # Create subscription
        initial_msg = {
            'cid': 'setup-cid',
            'sub_key': 'sk-preserve-789',
            'sec_name': 'preserve_user_sec',
            'topic_name_list': ['preserve.topic']
        }
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(initial_msg)

        # Verify topic and subscription exist
        self.assertIn('preserve.topic', self.backend.topics)
        self.assertIn('preserve.topic', self.backend.subs_by_topic)

        # Delete subscription for preserve_user
        delete_msg = {
            'cid': 'delete-cid-preserve',
            'sub_key': 'sk-preserve-789',
            'sec_name': 'preserve_user_sec'
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
            'sec_name': 'empty_user_sec'
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
            'sec_name': 'none_user_sec'
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
                    'sec_name': f'{user}_sec',
                    'topic_name_list': [topic]
                }
                self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(initial_msg)
                sub_key_counter += 1

        # Verify all subscriptions exist
        for topic in topics:
            self.assertIn(topic, self.backend.subs_by_topic)
            for user in users:
                self.assertIn(f'{user}_sec', self.backend.subs_by_topic[topic])

        # Delete alice's subscription to orders.new
        delete_msg = {
            'cid': 'delete-cid-complex',
            'sub_key': 'sk-complex-0',
            'sec_name': 'alice_sec'
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE(delete_msg)

        # Assert alice's subscription to orders.new was removed
        self.assertIn('orders.new', self.backend.subs_by_topic)
        self.assertNotIn('alice_sec', self.backend.subs_by_topic['orders.new'])
        self.assertIn('bob_sec', self.backend.subs_by_topic['orders.new'])
        self.assertIn('charlie_sec', self.backend.subs_by_topic['orders.new'])

        # Assert alice's other subscriptions remain
        self.assertIn('orders.paid', self.backend.subs_by_topic)
        self.assertIn('alice_sec', self.backend.subs_by_topic['orders.paid'])
        self.assertIn('bob_sec', self.backend.subs_by_topic['orders.paid'])
        self.assertIn('charlie_sec', self.backend.subs_by_topic['orders.paid'])

        self.assertIn('alerts.high', self.backend.subs_by_topic)
        self.assertIn('alice_sec', self.backend.subs_by_topic['alerts.high'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
