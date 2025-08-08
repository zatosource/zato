# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Must come first
from gevent import monkey;
_ = monkey.patch_all()

# stdlib
import warnings
from unittest import main, TestCase

# Zato
from zato.common.pubsub.backend.rest_backend import RESTBackend
from zato.common.pubsub.models import Subscription
from zato.common.pubsub.server.rest import PubSubRESTServer

# ################################################################################################################################
# ################################################################################################################################

class BrokerClientHelper:
    """ Test broker client that captures publish calls without mocking.
    """

    def __init__(self):
        self.published_messages = []
        self.published_exchanges = []
        self.published_routing_keys = []

    def publish(self, message, exchange, routing_key):
        """ Capture publish parameters for verification.
        """
        self.published_messages.append(message)
        self.published_exchanges.append(exchange)
        self.published_routing_keys.append(routing_key)

# ################################################################################################################################
# ################################################################################################################################

class RESTFindUserSubKeyTestCase(TestCase):

    def setUp(self):

        # Suppress ResourceWarnings from gevent
        warnings.filterwarnings('ignore', category=ResourceWarning)

        # Create a test broker client that captures publish calls
        self.broker_client = BrokerClientHelper()
        self.rest_server = PubSubRESTServer('localhost', 8080, should_init_broker_client=False)
        self.rest_server.backend = RESTBackend(self.rest_server, self.broker_client) # type: ignore

        # Test data constants
        self.test_cid = 'test-cid-123'
        self.test_username = 'test_user'
        self.test_topic = 'test.topic'
        self.test_sub_key = 'test_sub_key_123'

        # Set up test subscription
        subscription = Subscription()
        subscription.topic_name = self.test_topic
        subscription.sec_name = self.test_username
        subscription.sub_key = self.test_sub_key

        self.rest_server.subs_by_topic = {}
        self.rest_server.subs_by_topic[self.test_topic] = {
            self.test_username: subscription
        }

# ################################################################################################################################

    def test_find_user_sub_key_returns_key_when_found(self):
        """ _find_user_sub_key returns subscription key when user has subscription.
        """
        sub_key, topic_name = self.rest_server._find_user_sub_key(self.test_cid, self.test_username)

        self.assertEqual(sub_key, self.test_sub_key)
        self.assertEqual(topic_name, self.test_topic)

# ################################################################################################################################

    def test_find_user_sub_key_returns_none_when_not_found(self):
        """ _find_user_sub_key returns None when user has no subscription.
        """
        sub_key, topic_name = self.rest_server._find_user_sub_key(self.test_cid, 'nonexistent_user')

        self.assertIsNone(sub_key)
        self.assertIsNone(topic_name)

# ################################################################################################################################

    def test_find_user_sub_key_searches_all_topics(self):
        """ _find_user_sub_key searches across all topics.
        """
        # Add subscription in different topic
        other_topic = 'other.topic'
        other_sub_key = 'other_sub_key_456'
        other_user = 'other_user'

        subscription = Subscription()
        subscription.topic_name = other_topic
        subscription.sec_name = other_user
        subscription.sub_key = other_sub_key

        self.rest_server.subs_by_topic[other_topic] = {
            other_user: subscription
        }

        sub_key, topic_name = self.rest_server._find_user_sub_key(self.test_cid, other_user)

        self.assertEqual(sub_key, other_sub_key)
        self.assertEqual(topic_name, other_topic)

# ################################################################################################################################

    def test_find_user_sub_key_returns_first_match_when_multiple_subscriptions(self):
        """ _find_user_sub_key returns first subscription key when user has multiple.
        """
        # Add same user to another topic
        other_topic = 'other.topic'
        other_sub_key = 'other_sub_key_456'

        subscription = Subscription()
        subscription.topic_name = other_topic
        subscription.sec_name = self.test_username
        subscription.sub_key = other_sub_key

        self.rest_server.subs_by_topic[other_topic] = {
            self.test_username: subscription
        }

        sub_key, topic_name = self.rest_server._find_user_sub_key(self.test_cid, self.test_username)

        # Should return one of the keys (implementation returns first found)
        self.assertIn(sub_key, [self.test_sub_key, other_sub_key])
        self.assertIn(topic_name, [self.test_topic, other_topic])

# ################################################################################################################################

    def test_find_user_sub_key_with_empty_topics(self):
        """ _find_user_sub_key returns None when no topics exist.
        """
        # Clear all topics
        self.rest_server.subs_by_topic.clear()

        sub_key, topic_name = self.rest_server._find_user_sub_key(self.test_cid, self.test_username)

        self.assertIsNone(sub_key)
        self.assertIsNone(topic_name)

# ################################################################################################################################

    def test_find_user_sub_key_with_empty_subscriptions_in_topic(self):
        """ _find_user_sub_key returns None when topic has no subscriptions.
        """
        # Clear subscriptions but keep topic
        self.rest_server.subs_by_topic[self.test_topic] = {}

        sub_key, topic_name = self.rest_server._find_user_sub_key(self.test_cid, self.test_username)

        self.assertIsNone(sub_key)
        self.assertIsNone(topic_name)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
