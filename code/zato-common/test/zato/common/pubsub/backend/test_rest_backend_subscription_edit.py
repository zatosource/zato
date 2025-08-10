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

class RESTBackendSubscriptionEditTestCase(TestCase):

    def setUp(self):
        self.rest_server = Mock()
        self.rest_server.users = {}
        self.broker_client = Mock()
        self.broker_client.cluster_id = 'test-cluster'

        self.broker_client.invoke_sync.return_value = [
            {'username': 'test_user', 'name': 'test_user_sec'},
            {'username': 'edit_user', 'name': 'edit_user_sec'},
            {'username': 'user1', 'name': 'user1_sec'},
            {'username': 'user2', 'name': 'user2_sec'},
            {'username': 'same_user', 'name': 'same_user_sec'},
            {'username': 'invalid_user', 'name': 'invalid_user_sec'},
            {'username': 'multi_user', 'name': 'multi_user_sec'},
            {'username': 'user_one', 'name': 'user_one_sec'},
            {'username': 'user_two', 'name': 'user_two_sec'},
            {'username': 'nonexistent_user', 'name': 'nonexistent_user_sec'},
            {'username': 'overlap_user', 'name': 'overlap_user_sec'},
            {'username': 'create_user', 'name': 'create_user_sec'},
            {'username': 'empty_user', 'name': 'empty_user_sec'},
            {'username': 'reduce_user', 'name': 'reduce_user_sec'},
            {'username': 'cleanup_user', 'name': 'cleanup_user_sec'}
        ]

        self.backend = RESTBackend(self.rest_server, self.broker_client)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT_single_topic_to_single_topic(self):

        # Create initial subscription
        initial_msg = {
            'cid': 'setup-cid',
            'sub_key': 'sk-test-123',
            'sec_name': 'test_user_sec',
            'topic_name_list': ['orders.old']
        }
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(initial_msg)

        # Edit subscription to new topic
        edit_msg = {
            'cid': 'edit-cid-123',
            'sub_key': 'sk-test-123',
            'sec_name': 'test_user_sec',
            'topic_name_list': ['orders.new']
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT(edit_msg)

        # Assert old subscription was removed
        self.assertNotIn('orders.old', self.backend.subs_by_topic)

        # Assert new subscription was created
        self.assertIn('orders.new', self.backend.subs_by_topic)
        self.assertIn('test_user_sec', self.backend.subs_by_topic['orders.new'])

        subscription = self.backend.subs_by_topic['orders.new']['test_user_sec']
        self.assertEqual(subscription.topic_name, 'orders.new')
        self.assertEqual(subscription.sec_name, 'test_user_sec')
        self.assertEqual(subscription.sub_key, 'sk-test-123')

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT_single_topic_to_multiple_topics(self):

        # Create initial subscription
        initial_msg = {
            'cid': 'setup-cid',
            'sub_key': 'sk-multi-456',
            'sec_name': 'multi_user_sec',
            'topic_name_list': ['orders.original']
        }
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(initial_msg)

        # Edit subscription to multiple topics
        edit_msg = {
            'cid': 'edit-cid-456',
            'sub_key': 'sk-multi-456',
            'sec_name': 'multi_user_sec',
            'topic_name_list': ['orders.new1', 'orders.new2', 'orders.new3']
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT(edit_msg)

        # Assert old subscription was removed
        self.assertNotIn('orders.original', self.backend.subs_by_topic)

        # Assert all new subscriptions were created
        for topic_name in ['orders.new1', 'orders.new2', 'orders.new3']:
            self.assertIn(topic_name, self.backend.subs_by_topic)
            self.assertIn('multi_user_sec', self.backend.subs_by_topic[topic_name])

            subscription = self.backend.subs_by_topic[topic_name]['multi_user_sec']
            self.assertEqual(subscription.topic_name, topic_name)
            self.assertEqual(subscription.sec_name, 'multi_user_sec')
            self.assertEqual(subscription.sub_key, 'sk-multi-456')

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT_multiple_topics_to_single_topic(self):

        # Create initial subscription to multiple topics
        initial_msg = {
            'cid': 'setup-cid',
            'sub_key': 'sk-reduce-789',
            'sec_name': 'reduce_user_sec',
            'topic_name_list': ['orders.first', 'orders.second', 'orders.third']
        }
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(initial_msg)

        # Edit subscription to single topic
        edit_msg = {
            'cid': 'edit-cid-789',
            'sub_key': 'sk-reduce-789',
            'sec_name': 'reduce_user_sec',
            'topic_name_list': ['orders.single']
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT(edit_msg)

        # Assert old subscriptions were removed
        for topic_name in ['orders.first', 'orders.second', 'orders.third']:
            self.assertNotIn(topic_name, self.backend.subs_by_topic)

        # Assert new subscription was created
        self.assertIn('orders.single', self.backend.subs_by_topic)
        self.assertIn('reduce_user_sec', self.backend.subs_by_topic['orders.single'])

        subscription = self.backend.subs_by_topic['orders.single']['reduce_user_sec']
        self.assertEqual(subscription.topic_name, 'orders.single')
        self.assertEqual(subscription.sec_name, 'reduce_user_sec')
        self.assertEqual(subscription.sub_key, 'sk-reduce-789')

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT_preserves_other_users_subscriptions(self):

        # Create subscriptions for multiple users on same topic
        user1_msg = {
            'cid': 'setup-cid-1',
            'sub_key': 'sk-user1-111',
            'sec_name': 'user_one_sec',
            'topic_name_list': ['shared.topic']
        }
        user2_msg = {
            'cid': 'setup-cid-2',
            'sub_key': 'sk-user2-222',
            'sec_name': 'user_two_sec',
            'topic_name_list': ['shared.topic']
        }

        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(user1_msg)
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(user2_msg)

        # Edit only user_one's subscription
        edit_msg = {
            'cid': 'edit-cid-user1',
            'sub_key': 'sk-user1-111',
            'sec_name': 'user_one_sec',
            'topic_name_list': ['different.topic']
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT(edit_msg)

        # Assert user_two's subscription is preserved
        self.assertIn('shared.topic', self.backend.subs_by_topic)
        self.assertIn('user_two_sec', self.backend.subs_by_topic['shared.topic'])
        self.assertNotIn('user_one_sec', self.backend.subs_by_topic['shared.topic'])

        # Assert user_one's new subscription exists
        self.assertIn('different.topic', self.backend.subs_by_topic)
        self.assertIn('user_one_sec', self.backend.subs_by_topic['different.topic'])

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT_cleans_up_empty_topics(self):

        # Create subscription
        initial_msg = {
            'cid': 'setup-cid',
            'sub_key': 'sk-cleanup-444',
            'sec_name': 'cleanup_user_sec',
            'topic_name_list': ['cleanup.topic']
        }
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(initial_msg)

        # Verify topic exists
        self.assertIn('cleanup.topic', self.backend.subs_by_topic)

        # Edit subscription to different topic
        edit_msg = {
            'cid': 'edit-cid-cleanup',
            'sub_key': 'sk-cleanup-444',
            'sec_name': 'cleanup_user_sec',
            'topic_name_list': ['new.topic']
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT(edit_msg)

        # Assert old topic was cleaned up (removed from subs_by_topic)
        self.assertNotIn('cleanup.topic', self.backend.subs_by_topic)

        # Assert new topic exists
        self.assertIn('new.topic', self.backend.subs_by_topic)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT_creates_topics_if_missing(self):

        # Create initial subscription
        initial_msg = {
            'cid': 'setup-cid',
            'sub_key': 'sk-create-555',
            'sec_name': 'create_user_sec',
            'topic_name_list': ['existing.topic']
        }
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(initial_msg)

        # Edit subscription to non-existing topics
        edit_msg = {
            'cid': 'edit-cid-create',
            'sub_key': 'sk-create-555',
            'sec_name': 'create_user_sec',
            'topic_name_list': ['new.topic.one', 'new.topic.two']
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT(edit_msg)

        # Assert new topics were created
        self.assertIn('new.topic.one', self.backend.topics)
        self.assertIn('new.topic.two', self.backend.topics)

        # Assert subscriptions were created
        self.assertIn('new.topic.one', self.backend.subs_by_topic)
        self.assertIn('new.topic.two', self.backend.subs_by_topic)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT_empty_topic_list(self):

        # Create initial subscription
        initial_msg = {
            'cid': 'setup-cid',
            'sub_key': 'sk-empty-666',
            'sec_name': 'empty_user_sec',
            'topic_name_list': ['remove.topic']
        }
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(initial_msg)

        # Edit subscription to empty topic list
        edit_msg = {
            'cid': 'edit-cid-empty',
            'sub_key': 'sk-empty-666',
            'sec_name': 'empty_user_sec',
            'topic_name_list': []
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT(edit_msg)

        # Assert old subscription was removed
        self.assertNotIn('remove.topic', self.backend.subs_by_topic)

        # Assert no new subscriptions were created
        for subs_by_sec_name in self.backend.subs_by_topic.values():
            self.assertNotIn('empty_user', subs_by_sec_name)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT_nonexistent_subscription(self):

        # Try to edit a subscription that doesn't exist
        edit_msg = {
            'cid': 'edit-cid-nonexistent',
            'sub_key': 'sk-nonexistent-777',
            'sec_name': 'nonexistent_user_sec',
            'topic_name_list': ['new.topic']
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT(edit_msg)

        # Assert new subscription was created anyway
        self.assertIn('new.topic', self.backend.subs_by_topic)
        self.assertIn('nonexistent_user_sec', self.backend.subs_by_topic['new.topic'])

        subscription = self.backend.subs_by_topic['new.topic']['nonexistent_user_sec']
        self.assertEqual(subscription.sub_key, 'sk-nonexistent-777')

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT_same_topics(self):

        # Create initial subscription
        initial_msg = {
            'cid': 'setup-cid',
            'sub_key': 'sk-same-111',
            'sec_name': 'same_user_sec',
            'topic_name_list': ['topic.alpha', 'topic.beta']
        }
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(initial_msg)

        # Edit subscription to same topics
        edit_msg = {
            'cid': 'edit-cid-same',
            'sub_key': 'sk-same-111',
            'sec_name': 'same_user_sec',
            'topic_name_list': ['topic.alpha', 'topic.beta']
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT(edit_msg)

        # Assert subscriptions still exist
        self.assertIn('topic.alpha', self.backend.subs_by_topic)
        self.assertIn('topic.beta', self.backend.subs_by_topic)
        self.assertIn('same_user_sec', self.backend.subs_by_topic['topic.alpha'])
        self.assertIn('same_user_sec', self.backend.subs_by_topic['topic.beta'])

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT_partial_overlap(self):

        # Create initial subscription
        initial_msg = {
            'cid': 'setup-cid',
            'sub_key': 'sk-overlap-222',
            'sec_name': 'overlap_user_sec',
            'topic_name_list': ['topic.keep', 'topic.remove']
        }
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(initial_msg)

        # Edit subscription with partial overlap
        edit_msg = {
            'cid': 'edit-cid-overlap',
            'sub_key': 'sk-overlap-222',
            'sec_name': 'overlap_user_sec',
            'topic_name_list': ['topic.keep', 'topic.add']
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT(edit_msg)

        # Assert removed topic is gone
        self.assertNotIn('topic.remove', self.backend.subs_by_topic)

        # Assert kept and added topics exist
        self.assertIn('topic.keep', self.backend.subs_by_topic)
        self.assertIn('topic.add', self.backend.subs_by_topic)
        self.assertIn('overlap_user_sec', self.backend.subs_by_topic['topic.keep'])
        self.assertIn('overlap_user_sec', self.backend.subs_by_topic['topic.add'])

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT_with_invalid_topic_names(self):

        # Create initial subscription
        initial_msg = {
            'cid': 'setup-cid',
            'sub_key': 'sk-invalid-333',
            'sec_name': 'invalid_user_sec',
            'topic_name_list': ['valid.topic']
        }
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(initial_msg)

        # Edit subscription with invalid topic names
        edit_msg = {
            'cid': 'edit-cid-invalid',
            'sub_key': 'sk-invalid-333',
            'sec_name': 'invalid_user_sec',
            'topic_name_list': ['', None, 'valid.topic', '   ', 'topic with spaces']
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT(edit_msg)

        # Assert only valid topics were processed
        valid_topics = []
        for topic in edit_msg['topic_name_list']:
            if topic:
                topic = topic.strip()
                if topic:
                    valid_topics.append(topic)

        for topic in valid_topics:
            self.assertIn(topic, self.backend.subs_by_topic)
            self.assertIn('invalid_user_sec', self.backend.subs_by_topic[topic])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
