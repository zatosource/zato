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
from zato.common.pubsub.models import Topic, Subscription
from zato.common.test import TestCase

# ################################################################################################################################
# ################################################################################################################################

class RESTBackendTopicDeleteTestCase(TestCase):

    def setUp(self):
        self.rest_server = Mock()
        self.rest_server.users = []
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

    def test_on_broker_msg_PUBSUB_TOPIC_DELETE_removes_permissions(self):

        # Create a topic
        topic_name = 'test.topic.name'

        topic = Topic()
        topic.name = topic_name
        topic.creation_time = None
        self.backend._add_topic(topic_name, topic)

        # Add some permissions to the pattern matcher
        username = 'test_user'
        self.rest_server.users = [username]
        permissions = [{'pattern': topic_name, 'access_type': 'publisher'}]
        self.backend.pattern_matcher.add_client(username, permissions)

        # Verify permissions exist for the topic
        result_before = self.backend.pattern_matcher.evaluate(username, topic_name, 'publish')
        self.assertTrue(result_before.is_ok)

        # Create the broker message
        msg = {
            'cid': 'test-cid',
            'topic_name': topic_name
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_TOPIC_DELETE(msg)

        # Assert topic was removed
        self.assertFalse(self.backend._has_topic(topic_name))

        # Assert permissions are removed correctly
        # User should no longer have permission for the deleted topic
        result_after = self.backend.pattern_matcher.evaluate(username, topic_name, 'publish')
        self.assertFalse(result_after.is_ok)  # Permission no longer exists

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
