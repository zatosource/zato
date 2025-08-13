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

class RESTBackendSubscriptionCreateTestCase(TestCase):

    def setUp(self):
        self.rest_server = Mock()
        self.rest_server.users = {}
        self.broker_client = Mock()
        self.broker_client.cluster_id = 'test-cluster'

        # Mock response for invoke_service_with_pubsub with test users
        def mock_invoke_sync(service, request, timeout=20, needs_root_elem=False):
            if needs_root_elem:
                return {'error': None}
            return [
                {'username': 'test_user', 'name': 'test_user_sec'},
                {'username': 'multi_user', 'name': 'multi_user_sec'},
                {'username': 'topic_creator', 'name': 'topic_creator_sec'},
                {'username': 'user_one', 'name': 'user_one_sec'},
                {'username': 'user_two', 'name': 'user_two_sec'},
                {'username': 'empty_user', 'name': 'empty_user_sec'},
                {'username': 'existing_user', 'name': 'existing_user_sec'}
            ]

        self.broker_client.invoke_sync.side_effect = mock_invoke_sync

        self.backend = RESTBackend(self.rest_server, self.broker_client)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE_single_topic(self):

        # Create the broker message
        msg = {
            'cid': 'test-cid-123',
            'sub_key': 'sk-test-123',
            'sec_name': 'test_user_sec',
            'topic_name_list': ['orders.new']
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(msg)

        # Assert subscription was created
        self.assertIn('orders.new', self.backend.subs_by_topic)
        self.assertIn('test_user_sec', self.backend.subs_by_topic['orders.new'])

        subscription = self.backend.subs_by_topic['orders.new']['test_user_sec']
        self.assertEqual(subscription.topic_name, 'orders.new')
        self.assertEqual(subscription.sec_name, 'test_user_sec')
        self.assertEqual(subscription.sub_key, 'sk-test-123')

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE_multiple_topics(self):

        # Create the broker message
        msg = {
            'cid': 'test-cid-456',
            'sub_key': 'sk-multi-456',
            'sec_name': 'multi_user_sec',
            'topic_name_list': ['orders.new', 'invoices.paid', 'alerts.critical']
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(msg)

        # Assert all subscriptions were created
        for topic_name in ['orders.new', 'invoices.paid', 'alerts.critical']:
            self.assertIn(topic_name, self.backend.subs_by_topic)
            self.assertIn('multi_user_sec', self.backend.subs_by_topic[topic_name])

            subscription = self.backend.subs_by_topic[topic_name]['multi_user_sec']
            self.assertEqual(subscription.topic_name, topic_name)
            self.assertEqual(subscription.sec_name, 'multi_user_sec')
            self.assertEqual(subscription.sub_key, 'sk-multi-456')

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE_creates_topics_if_missing(self):

        # Ensure topics don't exist initially
        self.assertEqual(len(self.backend.topics), 0)

        # Create the broker message
        msg = {
            'cid': 'test-cid-789',
            'sub_key': 'sk-creator-789',
            'sec_name': 'topic_creator_sec',
            'topic_name_list': ['new.topic.one', 'new.topic.two']
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(msg)

        # Assert topics were created
        self.assertIn('new.topic.one', self.backend.topics)
        self.assertIn('new.topic.two', self.backend.topics)

        # Assert subscriptions were created
        self.assertIn('new.topic.one', self.backend.subs_by_topic)
        self.assertIn('new.topic.two', self.backend.subs_by_topic)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE_multiple_users_same_topic(self):

        # Create subscriptions for multiple users to the same topic
        msg1 = {
            'cid': 'test-cid-user1',
            'sub_key': 'sk-user1',
            'sec_name': 'user_one_sec',
            'topic_name_list': ['shared.topic']
        }

        msg2 = {
            'cid': 'test-cid-user2',
            'sub_key': 'sk-user2',
            'sec_name': 'user_two_sec',
            'topic_name_list': ['shared.topic']
        }

        # Call the method under test for both users
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(msg1)
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(msg2)

        # Assert both subscriptions exist
        self.assertIn('shared.topic', self.backend.subs_by_topic)
        self.assertIn('user_one_sec', self.backend.subs_by_topic['shared.topic'])
        self.assertIn('user_two_sec', self.backend.subs_by_topic['shared.topic'])

        # Assert subscription details are correct
        sub1 = self.backend.subs_by_topic['shared.topic']['user_one_sec']
        sub2 = self.backend.subs_by_topic['shared.topic']['user_two_sec']

        self.assertEqual(sub1.sec_name, 'user_one_sec')
        self.assertEqual(sub1.sub_key, 'sk-user1')
        self.assertEqual(sub2.sec_name, 'user_two_sec')
        self.assertEqual(sub2.sub_key, 'sk-user2')

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE_overwrites_existing_subscription(self):

        # Create initial subscription
        msg1 = {
            'cid': 'test-cid-initial',
            'sub_key': 'sk-initial',
            'sec_name': 'test_user_sec',
            'topic_name_list': ['test.topic']
        }

        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(msg1)

        # Create new subscription for same user and topic
        msg2 = {
            'cid': 'test-cid-overwrite',
            'sub_key': 'sk-new',
            'sec_name': 'test_user_sec',
            'topic_name_list': ['test.topic']
        }

        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(msg2)

        # Assert the subscription was not overwritten (existing behavior)
        subscription = self.backend.subs_by_topic['test.topic']['test_user_sec']
        self.assertEqual(subscription.sub_key, 'sk-initial')

        # Assert there's still only one subscription for this user/topic
        self.assertEqual(len(self.backend.subs_by_topic['test.topic']), 1)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE_empty_topic_list(self):

        # Create the broker message with empty topic list
        msg = {
            'cid': 'test-cid-empty',
            'sub_key': 'sk-empty',
            'sec_name': 'empty_user_sec',
            'topic_name_list': []
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(msg)

        # Assert no subscriptions were created
        self.assertEqual(len(self.backend.subs_by_topic), 0)
        self.assertEqual(len(self.backend.topics), 0)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE_preserves_existing_topics(self):

        # Create a topic manually first
        self.backend.create_topic('setup-cid', 'test', 'existing.topic')
        initial_topic_count = len(self.backend.topics)

        # Create subscription to existing topic
        msg = {
            'cid': 'test-cid-existing',
            'sub_key': 'sk-existing',
            'sec_name': 'existing_user_sec',
            'topic_name_list': ['existing.topic']
        }

        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(msg)

        # Assert topic count didn't change (no duplicate creation)
        self.assertEqual(len(self.backend.topics), initial_topic_count)

        # Assert subscription was still created
        self.assertIn('existing.topic', self.backend.subs_by_topic)
        self.assertIn('existing_user_sec', self.backend.subs_by_topic['existing.topic'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
