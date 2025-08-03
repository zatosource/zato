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
from zato.common.pubsub.models import Topic, Subscription
from zato.common.test import TestCase

# ################################################################################################################################
# ################################################################################################################################

class RESTBackendTopicDeleteTestCase(TestCase):

    def setUp(self):
        self.rest_server = Mock()
        self.rest_server.users = {}
        self.broker_client = Mock()
        self.backend = RESTBackend(self.rest_server, self.broker_client)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_TOPIC_DELETE_removes_topic_and_subscriptions(self):

        # Create a topic with subscriptions
        topic_name = 'test.topic.name'

        topic = Topic()
        topic.name = topic_name
        topic.creation_time = None
        self.backend._add_topic(topic_name, topic)

        # Create subscriptions for the topic
        sub1 = Subscription()
        sub1.topic_name = topic_name
        sub1.username = 'user1'
        sub1.sub_key = 'sub1_key'
        sub1.creation_time = None

        sub2 = Subscription()
        sub2.topic_name = topic_name
        sub2.username = 'user2'
        sub2.sub_key = 'sub2_key'
        sub2.creation_time = None

        self.backend.subs_by_topic[topic_name] = {
            'user1': sub1,
            'user2': sub2
        }

        # Mock the unregister_subscription method
        self.backend.unregister_subscription = Mock()

        # Create the broker message
        msg = {
            'cid': 'test-cid',
            'topic_name': topic_name
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_TOPIC_DELETE(msg)

        # Assert topic was removed
        self.assertFalse(self.backend._has_topic(topic_name))

        # Assert subscriptions were removed
        self.assertNotIn(topic_name, self.backend.subs_by_topic)

        # Assert unregister_subscription was called for each user
        expected_calls = [
            ('test-cid', topic_name),
            ('test-cid', topic_name)
        ]

        actual_calls = [call.args[:2] for call in self.backend.unregister_subscription.call_args_list]
        self.assertEqual(len(actual_calls), 2)

        for call_args in actual_calls:
            self.assertIn(call_args, expected_calls)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_TOPIC_DELETE_handles_missing_topic(self):

        # Create the broker message for a topic that doesn't exist
        msg = {
            'cid': 'test-cid',
            'topic_name': 'nonexistent.topic'
        }

        # Call the method under test - should not raise an exception
        self.backend.on_broker_msg_PUBSUB_TOPIC_DELETE(msg)

        # Assert no topics were modified
        topics_count = len(self.backend.topics)
        subs_count = len(self.backend.subs_by_topic)

        self.assertEqual(topics_count, 0)
        self.assertEqual(subs_count, 0)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_TOPIC_DELETE_handles_topic_without_subscriptions(self):

        # Create a topic with no subscriptions
        topic_name = 'test.topic.name'

        topic = Topic()
        topic.name = topic_name
        topic.creation_time = None
        self.backend._add_topic(topic_name, topic)

        # Create the broker message
        msg = {
            'cid': 'test-cid',
            'topic_name': topic_name
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_TOPIC_DELETE(msg)

        # Assert topic was removed
        self.assertFalse(self.backend._has_topic(topic_name))

        # Assert no subscriptions were affected (there were none)
        subs_count = len(self.backend.subs_by_topic)
        self.assertEqual(subs_count, 0)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_TOPIC_DELETE_removes_publisher_permissions_two_users(self):

        # Create a topic
        topic_name = 'test.topic.name'

        topic = Topic()
        topic.name = topic_name
        topic.creation_time = None
        self.backend._add_topic(topic_name, topic)

        # Add two users with different permissions
        user1 = 'affected_user'
        user2 = 'unaffected_user'
        self.rest_server.users[user1] = 'password1'
        self.rest_server.users[user2] = 'password2'

        # User1 has exact permission for the topic being deleted
        permissions1 = [{'pattern': topic_name, 'access_type': 'publisher'}]
        self.backend.pattern_matcher.add_client(user1, permissions1)

        # User2 has different permissions that should not be affected
        permissions2 = [{'pattern': 'other.topic', 'access_type': 'publisher'}]
        self.backend.pattern_matcher.add_client(user2, permissions2)

        # Verify initial permissions
        result_user1_topic = self.backend.pattern_matcher.evaluate(user1, topic_name, 'publish')
        result_user2_other = self.backend.pattern_matcher.evaluate(user2, 'other.topic', 'publish')
        self.assertTrue(result_user1_topic.is_ok)
        self.assertTrue(result_user2_other.is_ok)

        # Create the broker message
        msg = {
            'cid': 'test-cid',
            'topic_name': topic_name
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_TOPIC_DELETE(msg)

        # Assert topic was removed
        self.assertFalse(self.backend._has_topic(topic_name))

        # Assert user1 permissions are removed
        result_user1_after = self.backend.pattern_matcher.evaluate(user1, topic_name, 'publish')
        self.assertFalse(result_user1_after.is_ok)  # Permission no longer exists

        # Assert user2 permissions are unchanged
        result_user2_other_after = self.backend.pattern_matcher.evaluate(user2, 'other.topic', 'publish')
        self.assertTrue(result_user2_other_after.is_ok)  # Other permissions unchanged

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_TOPIC_DELETE_removes_subscriber_permissions_two_users(self):

        # Create a topic
        topic_name = 'test.topic.name'

        topic = Topic()
        topic.name = topic_name
        topic.creation_time = None
        self.backend._add_topic(topic_name, topic)

        # Add two users with different permissions
        user1 = 'affected_user'
        user2 = 'unaffected_user'
        self.rest_server.users[user1] = 'password1'
        self.rest_server.users[user2] = 'password2'

        # User1 has exact subscriber permission for the topic being deleted
        permissions1 = [{'pattern': topic_name, 'access_type': 'subscriber'}]
        self.backend.pattern_matcher.add_client(user1, permissions1)

        # User2 has different permissions that should not be affected
        permissions2 = [{'pattern': 'other.topic', 'access_type': 'subscriber'}]
        self.backend.pattern_matcher.add_client(user2, permissions2)

        # Verify initial permissions
        result_user1_topic = self.backend.pattern_matcher.evaluate(user1, topic_name, 'subscribe')
        result_user2_other = self.backend.pattern_matcher.evaluate(user2, 'other.topic', 'subscribe')
        self.assertTrue(result_user1_topic.is_ok)
        self.assertTrue(result_user2_other.is_ok)

        # Create the broker message
        msg = {
            'cid': 'test-cid',
            'topic_name': topic_name
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_TOPIC_DELETE(msg)

        # Assert topic was removed
        self.assertFalse(self.backend._has_topic(topic_name))

        # Assert user1 permissions are removed
        result_user1_after = self.backend.pattern_matcher.evaluate(user1, topic_name, 'subscribe')
        self.assertFalse(result_user1_after.is_ok)  # Permission no longer exists

        # Assert user2 permissions are unchanged
        result_user2_other_after = self.backend.pattern_matcher.evaluate(user2, 'other.topic', 'subscribe')
        self.assertTrue(result_user2_other_after.is_ok)  # Other permissions unchanged

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_TOPIC_DELETE_wildcard_permissions_unchanged_two_users(self):

        # Create a topic
        topic_name = 'exact.topic'

        topic = Topic()
        topic.name = topic_name
        topic.creation_time = None
        self.backend._add_topic(topic_name, topic)

        # Add two users with different permission types
        user1 = 'exact_user'
        user2 = 'wildcard_user'
        self.rest_server.users[user1] = 'password1'
        self.rest_server.users[user2] = 'password2'

        # User1 has exact permission for the topic being deleted
        permissions1 = [{'pattern': topic_name, 'access_type': 'publisher'}]
        self.backend.pattern_matcher.add_client(user1, permissions1)

        # User2 has wildcard permissions that should not be affected
        permissions2 = [{'pattern': 'wildcard.*', 'access_type': 'publisher'}]
        self.backend.pattern_matcher.add_client(user2, permissions2)

        # Verify initial permissions
        result_user1_exact = self.backend.pattern_matcher.evaluate(user1, topic_name, 'publish')
        result_user2_wildcard = self.backend.pattern_matcher.evaluate(user2, 'wildcard.test', 'publish')
        self.assertTrue(result_user1_exact.is_ok)
        self.assertTrue(result_user2_wildcard.is_ok)

        # Create the broker message
        msg = {
            'cid': 'test-cid',
            'topic_name': topic_name
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_TOPIC_DELETE(msg)

        # Assert topic was removed
        self.assertFalse(self.backend._has_topic(topic_name))

        # Assert user1 exact permissions are removed
        result_user1_after = self.backend.pattern_matcher.evaluate(user1, topic_name, 'publish')
        self.assertFalse(result_user1_after.is_ok)  # Exact permission no longer exists

        # Assert user2 wildcard permissions are unchanged
        result_user2_wildcard_after = self.backend.pattern_matcher.evaluate(user2, 'wildcard.test', 'publish')
        self.assertTrue(result_user2_wildcard_after.is_ok)  # Wildcard permissions unchanged

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
