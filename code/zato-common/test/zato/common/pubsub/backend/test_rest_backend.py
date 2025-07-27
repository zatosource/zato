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

class RESTBackendTestCase(TestCase):

    def setUp(self):
        self.rest_server = Mock()
        self.broker_client = Mock()
        self.backend = RESTBackend(self.rest_server, self.broker_client)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_TOPIC_EDIT_updates_topic_name(self):

        # Create a topic with the old name
        old_topic_name = 'old.topic.name'
        new_topic_name = 'new.topic.name'

        topic = Topic()
        topic.name = old_topic_name
        self.backend.topics[old_topic_name] = topic

        # Create subscriptions for the old topic
        sub1 = Subscription()
        sub1.topic_name = old_topic_name
        sub1.sec_name = 'user1'

        sub2 = Subscription()
        sub2.topic_name = old_topic_name
        sub2.sec_name = 'user2'

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
        self.assertNotIn(old_topic_name, self.backend.topics)
        self.assertIn(new_topic_name, self.backend.topics)
        self.assertEqual(self.backend.topics[new_topic_name], topic)

        # Assert subscriptions were moved to new topic name
        self.assertNotIn(old_topic_name, self.backend.subs_by_topic)
        self.assertIn(new_topic_name, self.backend.subs_by_topic)

        # Assert subscription objects were updated with new topic name
        updated_subs = self.backend.subs_by_topic[new_topic_name]
        self.assertEqual(updated_subs['user1'].topic_name, new_topic_name)
        self.assertEqual(updated_subs['user2'].topic_name, new_topic_name)

        # Assert the same subscription objects are still there
        self.assertEqual(updated_subs['user1'], sub1)
        self.assertEqual(updated_subs['user2'], sub2)

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
        self.assertEqual(len(self.backend.topics), 0)
        self.assertEqual(len(self.backend.subs_by_topic), 0)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_TOPIC_EDIT_handles_topic_without_subscriptions(self):

        # Create a topic with no subscriptions
        old_topic_name = 'old.topic.name'
        new_topic_name = 'new.topic.name'

        topic = Topic()
        topic.name = old_topic_name
        self.backend.topics[old_topic_name] = topic

        # Create the broker message
        msg = {
            'new_topic_name': new_topic_name,
            'old_topic_name': old_topic_name
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_TOPIC_EDIT(msg)

        # Assert topic was moved to new name
        self.assertNotIn(old_topic_name, self.backend.topics)
        self.assertIn(new_topic_name, self.backend.topics)
        self.assertEqual(self.backend.topics[new_topic_name], topic)

        # Assert no subscriptions were affected
        self.assertEqual(len(self.backend.subs_by_topic), 0)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
