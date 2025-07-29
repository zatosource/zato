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

# ################################################################################################################################
# ################################################################################################################################

class RESTBackendTopicEditTestCase(TestCase):

    def setUp(self):
        self.rest_server = Mock()
        self.rest_server.users = ['user1', 'user2']
        self.broker_client = Mock()
        self.backend = RESTBackend(self.rest_server, self.broker_client)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_TOPIC_EDIT_updates_topic_name(self):

        # Create a topic with the old name
        old_topic_name = 'old.topic.name'
        new_topic_name = 'new.topic.name'

        topic = Topic()
        topic.name = old_topic_name
        topic.creation_time = None
        self.backend._add_topic(old_topic_name, topic)

        # Create subscriptions for the old topic
        sub1 = Subscription()
        sub1.topic_name = old_topic_name
        sub1.username = 'user1'
        sub1.sub_key = 'sub1_key'
        sub1.creation_time = None

        sub2 = Subscription()
        sub2.topic_name = old_topic_name
        sub2.username = 'user2'
        sub2.sub_key = 'sub2_key'
        sub2.creation_time = None

        self.backend.subs_by_topic[old_topic_name] = {
            'user1': sub1,
            'user2': sub2
        }

        # Create the broker message
        msg = {
            'new_topic_name': new_topic_name,
            'old_topic_name': old_topic_name
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_TOPIC_EDIT(msg)

        # Assert topic was moved to new name
        self.assertFalse(self.backend._has_topic(old_topic_name))
        self.assertTrue(self.backend._has_topic(new_topic_name))

        retrieved_topic = self.backend.topics[new_topic_name]
        self.assertEqual(retrieved_topic, topic)

        # Assert subscriptions were moved to new topic name
        self.assertNotIn(old_topic_name, self.backend.subs_by_topic)
        self.assertIn(new_topic_name, self.backend.subs_by_topic)

        # Assert subscription objects were updated with new topic name
        updated_subs = self.backend.subs_by_topic[new_topic_name]
        user1_sub = updated_subs['user1']
        user2_sub = updated_subs['user2']

        self.assertEqual(user1_sub.topic_name, new_topic_name)
        self.assertEqual(user2_sub.topic_name, new_topic_name)

        # Assert the same subscription objects are still there
        self.assertEqual(user1_sub, sub1)
        self.assertEqual(user2_sub, sub2)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_TOPIC_EDIT_handles_missing_topic(self):

        # Create the broker message for a topic that doesn't exist
        msg = {
            'new_topic_name': 'new.topic.name',
            'old_topic_name': 'nonexistent.topic'
        }

        # Call the method under test - should not raise an exception
        self.backend.on_broker_msg_PUBSUB_TOPIC_EDIT(msg)

        # Assert no topics were created or modified
        topics_count = len(self.backend.topics)
        subs_count = len(self.backend.subs_by_topic)

        self.assertEqual(topics_count, 0)
        self.assertEqual(subs_count, 0)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_TOPIC_EDIT_handles_topic_without_subscriptions(self):

        # Create a topic with no subscriptions
        old_topic_name = 'old.topic.name'
        new_topic_name = 'new.topic.name'

        topic = Topic()
        topic.name = old_topic_name
        topic.creation_time = None
        self.backend._add_topic(old_topic_name, topic)

        # Create the broker message
        msg = {
            'new_topic_name': new_topic_name,
            'old_topic_name': old_topic_name
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_TOPIC_EDIT(msg)

        # Assert topic was moved to new name
        self.assertFalse(self.backend._has_topic(old_topic_name))
        self.assertTrue(self.backend._has_topic(new_topic_name))

        retrieved_topic = self.backend.topics[new_topic_name]
        self.assertEqual(retrieved_topic, topic)

        # Assert no subscriptions were affected
        subs_count = len(self.backend.subs_by_topic)
        self.assertEqual(subs_count, 0)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_TOPIC_EDIT_updates_publisher_permissions_two_users(self):

        # Create a topic with the old name
        old_topic_name = 'old.topic.name'
        new_topic_name = 'new.topic.name'

        topic = Topic()
        topic.name = old_topic_name
        topic.creation_time = None
        self.backend._add_topic(old_topic_name, topic)

        # Add two users with different permissions
        user1 = 'affected_user'
        user2 = 'unaffected_user'
        self.rest_server.users = [user1, user2]

        # User1 has exact permission for the topic being renamed
        permissions1 = [{'pattern': old_topic_name, 'access_type': 'publisher'}]
        self.backend.pattern_matcher.add_client(user1, permissions1)

        # User2 has different permissions that should not be affected
        permissions2 = [{'pattern': 'other.topic', 'access_type': 'publisher'}]
        self.backend.pattern_matcher.add_client(user2, permissions2)

        # Verify initial permissions
        result_user1_old = self.backend.pattern_matcher.evaluate(user1, old_topic_name, 'publish')
        result_user2_other = self.backend.pattern_matcher.evaluate(user2, 'other.topic', 'publish')
        self.assertTrue(result_user1_old.is_ok)
        self.assertTrue(result_user2_other.is_ok)

        # Create the broker message
        msg = {
            'new_topic_name': new_topic_name,
            'old_topic_name': old_topic_name
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_TOPIC_EDIT(msg)

        # Assert topic was moved to new name
        self.assertFalse(self.backend._has_topic(old_topic_name))
        self.assertTrue(self.backend._has_topic(new_topic_name))

        # Assert user1 permissions are updated
        result_user1_old_after = self.backend.pattern_matcher.evaluate(user1, old_topic_name, 'publish')
        result_user1_new_after = self.backend.pattern_matcher.evaluate(user1, new_topic_name, 'publish')
        self.assertFalse(result_user1_old_after.is_ok)  # Old permission no longer exists
        self.assertTrue(result_user1_new_after.is_ok)  # New topic has permission

        # Assert user2 permissions are unchanged
        result_user2_other_after = self.backend.pattern_matcher.evaluate(user2, 'other.topic', 'publish')
        self.assertTrue(result_user2_other_after.is_ok)  # Other permissions unchanged

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_TOPIC_EDIT_updates_subscriber_permissions_two_users(self):

        # Create a topic with the old name
        old_topic_name = 'old.topic.name'
        new_topic_name = 'new.topic.name'

        topic = Topic()
        topic.name = old_topic_name
        topic.creation_time = None
        self.backend._add_topic(old_topic_name, topic)

        # Add two users with different permissions
        user1 = 'affected_user'
        user2 = 'unaffected_user'
        self.rest_server.users = [user1, user2]

        # User1 has exact subscriber permission for the topic being renamed
        permissions1 = [{'pattern': old_topic_name, 'access_type': 'subscriber'}]
        self.backend.pattern_matcher.add_client(user1, permissions1)

        # User2 has different permissions that should not be affected
        permissions2 = [{'pattern': 'other.topic', 'access_type': 'subscriber'}]
        self.backend.pattern_matcher.add_client(user2, permissions2)

        # Verify initial permissions
        result_user1_old = self.backend.pattern_matcher.evaluate(user1, old_topic_name, 'subscribe')
        result_user2_other = self.backend.pattern_matcher.evaluate(user2, 'other.topic', 'subscribe')
        self.assertTrue(result_user1_old.is_ok)
        self.assertTrue(result_user2_other.is_ok)

        # Create the broker message
        msg = {
            'new_topic_name': new_topic_name,
            'old_topic_name': old_topic_name
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_TOPIC_EDIT(msg)

        # Assert topic was moved to new name
        self.assertFalse(self.backend._has_topic(old_topic_name))
        self.assertTrue(self.backend._has_topic(new_topic_name))

        # Assert user1 permissions are updated
        result_user1_old_after = self.backend.pattern_matcher.evaluate(user1, old_topic_name, 'subscribe')
        result_user1_new_after = self.backend.pattern_matcher.evaluate(user1, new_topic_name, 'subscribe')
        self.assertFalse(result_user1_old_after.is_ok)  # Old permission no longer exists
        self.assertTrue(result_user1_new_after.is_ok)  # New topic has permission

        # Assert user2 permissions are unchanged
        result_user2_other_after = self.backend.pattern_matcher.evaluate(user2, 'other.topic', 'subscribe')
        self.assertTrue(result_user2_other_after.is_ok)  # Other permissions unchanged

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_TOPIC_EDIT_wildcard_permissions_unchanged_two_users(self):

        # Create a topic with the old name
        old_topic_name = 'exact.topic'
        new_topic_name = 'renamed.topic'

        topic = Topic()
        topic.name = old_topic_name
        topic.creation_time = None
        self.backend._add_topic(old_topic_name, topic)

        # Add two users with different permission types
        user1 = 'exact_user'
        user2 = 'wildcard_user'
        self.rest_server.users = [user1, user2]

        # User1 has exact permission for the topic being renamed
        permissions1 = [{'pattern': old_topic_name, 'access_type': 'publisher'}]
        self.backend.pattern_matcher.add_client(user1, permissions1)

        # User2 has wildcard permissions that should not be affected
        permissions2 = [{'pattern': 'wildcard.*', 'access_type': 'publisher'}]
        self.backend.pattern_matcher.add_client(user2, permissions2)

        # Verify initial permissions
        result_user1_exact = self.backend.pattern_matcher.evaluate(user1, old_topic_name, 'publish')
        result_user2_wildcard = self.backend.pattern_matcher.evaluate(user2, 'wildcard.test', 'publish')
        self.assertTrue(result_user1_exact.is_ok)
        self.assertTrue(result_user2_wildcard.is_ok)

        # Create the broker message
        msg = {
            'new_topic_name': new_topic_name,
            'old_topic_name': old_topic_name
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_TOPIC_EDIT(msg)

        # Assert topic was moved to new name
        self.assertFalse(self.backend._has_topic(old_topic_name))
        self.assertTrue(self.backend._has_topic(new_topic_name))

        # Assert user1 exact permissions are updated
        result_user1_old_after = self.backend.pattern_matcher.evaluate(user1, old_topic_name, 'publish')
        result_user1_new_after = self.backend.pattern_matcher.evaluate(user1, new_topic_name, 'publish')
        self.assertFalse(result_user1_old_after.is_ok)  # Old exact permission no longer exists
        self.assertTrue(result_user1_new_after.is_ok)  # New exact permission exists

        # Assert user2 wildcard permissions are unchanged
        result_user2_wildcard_after = self.backend.pattern_matcher.evaluate(user2, 'wildcard.test', 'publish')
        self.assertTrue(result_user2_wildcard_after.is_ok)  # Wildcard permissions unchanged

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
