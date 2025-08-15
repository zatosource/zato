# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Must come first
from gevent import monkey;
_ = monkey.patch_all()

# stdlib
import base64
import json
import warnings
from unittest import main, TestCase
from unittest.mock import Mock

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

class RESTOnMessagesGetPermissionCheckingTestCase(TestCase):

    def setUp(self):

        # Suppress ResourceWarnings from gevent
        warnings.filterwarnings('ignore', category=ResourceWarning)

        # Create a test broker client that captures publish calls
        self.broker_client = BrokerClientHelper()
        self.rest_server = PubSubRESTServer('localhost', 8080, should_init_broker_client=False)
        self.rest_server.backend = RESTBackend(self.rest_server, self.broker_client) # type: ignore

        # Set up test users for authentication
        self.rest_server.users = {
            'test_user': {'sec_name': 'test_sec_def', 'password': 'test_password'},
            'allowed_user': {'sec_name': 'test_sec_def', 'password': 'allowed_password'},
            'denied_user': {'sec_name': 'test_sec_def', 'password': 'denied_password'},
            'admin_user': {'sec_name': 'test_sec_def', 'password': 'admin_password'}
        }

        # Test data constants
        self.test_cid = 'test-cid-123'
        self.test_topic = 'test.topic'
        self.restricted_topic = 'restricted.topic'

        # Set up test subscriptions
        self.rest_server.backend.subs_by_topic = {}

        for username in ['test_user', 'allowed_user', 'denied_user', 'admin_user']:
            # Subscription for test.topic
            subscription = Subscription()
            subscription.topic_name = self.test_topic
            subscription.sec_name = username
            subscription.sub_key = f'{username}_sub_key_123'

            if self.test_topic not in self.rest_server.backend.subs_by_topic:
                self.rest_server.backend.subs_by_topic[self.test_topic] = {}
            self.rest_server.backend.subs_by_topic[self.test_topic]['test_sec_def'] = subscription

            # Subscription for restricted.topic
            restricted_subscription = Subscription()
            restricted_subscription.topic_name = self.restricted_topic
            restricted_subscription.sec_name = username
            restricted_subscription.sub_key = f'{username}_restricted_sub_key_456'

            if self.restricted_topic not in self.rest_server.backend.subs_by_topic:
                self.rest_server.backend.subs_by_topic[self.restricted_topic] = {}
            self.rest_server.backend.subs_by_topic[self.restricted_topic]['test_sec_def'] = restricted_subscription

        # Clear pattern matcher and set up permissions
        self.rest_server.backend.pattern_matcher._clients = {}
        self.rest_server.backend.pattern_matcher._pattern_cache = {}

        # Add permissions for users - use correct access_type
        self.rest_server.backend.pattern_matcher.add_client('test_user', [
            {'pattern': 'test.topic', 'access_type': 'subscriber'}
        ])
        self.rest_server.backend.pattern_matcher.add_client('allowed_user', [
            {'pattern': 'test.topic', 'access_type': 'subscriber'},
            {'pattern': 'restricted.topic', 'access_type': 'subscriber'}
        ])
        self.rest_server.backend.pattern_matcher.add_client('admin_user', [
            {'pattern': 'test.topic', 'access_type': 'subscriber'},
            {'pattern': 'restricted.topic', 'access_type': 'subscriber'}
        ])
        self.rest_server.backend.pattern_matcher.add_client('denied_user', [
            {'pattern': 'other.topic', 'access_type': 'subscriber'}
        ])

        # Mock _fetch_from_rabbitmq to return empty list
        def mock_fetch_from_rabbitmq(cid, api_url, rabbitmq_payload):
            return []

        self.rest_server._fetch_from_rabbitmq = mock_fetch_from_rabbitmq

    def _create_environ(self, json_data, username='test_user', password='test_password'):
        """ Helper to create WSGI environ with JSON data and HTTP Basic Auth.
        """
        json_str = json.dumps(json_data)

        # Create HTTP Basic Auth header
        credentials = f'{username}:{password}'
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('ascii')
        auth_header = f'Basic {encoded_credentials}'

        class MockInput:
            def __init__(self, data):
                self.data = data
            def read(self, size=-1):
                return self.data

        return {
            'REQUEST_METHOD': 'GET',
            'CONTENT_TYPE': 'application/json',
            'CONTENT_LENGTH': str(len(json_str)),
            'HTTP_AUTHORIZATION': auth_header,
            'PATH_INFO': '/messages',
            'wsgi.input': MockInput(json_str.encode('utf-8'))
        }

# ################################################################################################################################

    def test_on_messages_get_allows_user_with_subscribe_permission(self):
        """ on_messages_get allows user with subscribe permission to access messages.
        """
        # Create request
        environ = self._create_environ({'max_messages': 1}, 'test_user', 'test_password')

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify success
        self.assertTrue(response.is_ok)
        self.assertEqual(response.cid, self.test_cid)

# ################################################################################################################################

    def test_on_messages_get_denies_user_without_subscribe_permission(self):
        """ on_messages_get denies user without subscribe permission.
        """
        # Clear subscriptions for denied_user to simulate no subscription
        self.rest_server.backend.subs_by_topic.clear()

        # Create request for denied_user trying to access test.topic
        environ = self._create_environ({'max_messages': 1}, 'denied_user', 'denied_password')

        # Call method and expect error response for no subscription
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)
        self.assertFalse(response.is_ok)
        self.assertIn('No subscription found for user', response.details)

# ################################################################################################################################

    def test_on_messages_get_allows_wildcard_permissions(self):
        """ on_messages_get allows users with wildcard permissions.
        """
        # Create request with user that has wildcard permissions
        environ = self._create_environ({'max_messages': 1}, 'allowed_user', 'allowed_password')

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify success
        self.assertTrue(response.is_ok)
        self.assertEqual(response.cid, self.test_cid)

# ################################################################################################################################

    def test_on_messages_get_allows_double_wildcard_permissions(self):
        """ on_messages_get allows users with double wildcard permissions.
        """
        # Create request with admin user that has double wildcard permissions
        environ = self._create_environ({'max_messages': 1}, 'admin_user', 'admin_password')

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify success
        self.assertTrue(response.is_ok)
        self.assertEqual(response.cid, self.test_cid)

# ################################################################################################################################

    def test_on_messages_get_permission_check_happens_after_subscription_lookup(self):
        """ on_messages_get performs permission check after finding subscription.
        """
        # Track method calls
        method_calls = []

        # Override methods to track calls
        original_find_user_sub_key = self.rest_server._find_user_sub_key

        def track_find_user_sub_key(cid, username):
            method_calls.append('find_user_sub_key')
            return original_find_user_sub_key(cid, username)

        self.rest_server._find_user_sub_key = track_find_user_sub_key

        # Create request
        environ = self._create_environ({'max_messages': 1}, 'test_user', 'test_password')

        # Call method
        _ = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify find_user_sub_key was called
        self.assertIn('find_user_sub_key', method_calls)

# ################################################################################################################################

    def test_on_messages_get_uses_correct_topic_name_for_permission_check(self):
        """ on_messages_get uses correct topic name from subscription for permission check.
        """
        # Create request
        environ = self._create_environ({'max_messages': 1}, 'test_user', 'test_password')

        # Call method - should succeed since user has subscription
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)
        self.assertTrue(response.is_ok)

# ################################################################################################################################

    def test_on_messages_get_permission_check_with_different_topics(self):
        """ on_messages_get permission check works with different topics.
        """
        test_cases = [
            ('test_user', 'test_password', self.test_topic, True),      # Has subscription
            ('denied_user', 'denied_password', self.test_topic, False), # No subscription
        ]

        for username, password, expected_topic, should_succeed in test_cases:
            with self.subTest(username=username, topic=expected_topic):
                if should_succeed:
                    # Create subscription for this user/topic combination
                    subscription = Mock()
                    subscription.sec_name = username
                    subscription.sub_key = f'{username}_{expected_topic}_key'

                    self.rest_server.backend.subs_by_topic[expected_topic] = {
                        'test_sec_def': subscription
                    }

                    # Create request
                    environ = self._create_environ({'max_messages': 1}, username, password)

                    # Call method and expect success
                    response = self.rest_server.on_messages_get(self.test_cid, environ, None)
                    self.assertTrue(response.is_ok)
                else:
                    # Clear subscriptions to simulate no subscription
                    self.rest_server.backend.subs_by_topic.clear()

                    # Create request
                    environ = self._create_environ({'max_messages': 1}, username, password)

                    # Call method and expect error response
                    response = self.rest_server.on_messages_get(self.test_cid, environ, None)
                    self.assertFalse(response.is_ok)
                    self.assertIn('No subscription found for user', response.details)

# ################################################################################################################################

    def test_on_messages_get_stops_processing_on_permission_failure(self):
        """ on_messages_get stops processing when permission check fails.
        """
        # Clear subscriptions to simulate no subscription
        self.rest_server.backend.subs_by_topic.clear()

        # Track method calls
        method_calls = []

        # Override methods to track calls
        original_build_rabbitmq_request = self.rest_server._build_rabbitmq_request

        def track_build_rabbitmq_request(sub_key, max_messages, max_len):
            method_calls.append('build_rabbitmq_request')
            return original_build_rabbitmq_request(sub_key, max_messages, max_len)

        self.rest_server._build_rabbitmq_request = track_build_rabbitmq_request

        # Create request for user without subscription
        environ = self._create_environ({'max_messages': 1}, 'denied_user', 'denied_password')

        # Call method and expect error response
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)
        self.assertFalse(response.is_ok)
        self.assertIn('No subscription found for user', response.details)

        # Verify no further processing occurred
        self.assertEqual(len(method_calls), 0)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
