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

# Zato
from zato.common.pubsub.backend.rest_backend import RESTBackend
from zato.common.pubsub.models import Subscription
from zato.common.pubsub.server.rest import PubSubRESTServer
from zato.common.pubsub.server.rest_base import UnauthorizedException

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

# ################################################################################################################################
# ################################################################################################################################

class RESTOnMessagesGetAuthenticationTestCase(TestCase):

    def setUp(self):

        # Suppress ResourceWarnings from gevent
        warnings.filterwarnings('ignore', category=ResourceWarning)

        # Create a test broker client that captures publish calls
        self.broker_client = BrokerClientHelper()
        self.rest_server = PubSubRESTServer('localhost', 8080, should_init_broker_client=False)
        self.rest_server.backend = RESTBackend(self.rest_server, self.broker_client) # type: ignore

        # Set up subscription data
        self.rest_server.backend.subs_by_topic = {}

        # Set up test users for authentication
        self.rest_server.users = {
            'test_user': 'test_password',
            'different_user': 'different_password',
            'admin_user': 'admin_password',
            'user1': 'password1',
            'user2': 'password2'
        }

        # Set up permissions for all users
        self.rest_server.backend.pattern_matcher.add_client('test_user', [
            {'pattern': 'test.topic', 'access_type': 'subscriber'}
        ])
        self.rest_server.backend.pattern_matcher.add_client('different_user', [
            {'pattern': 'test.topic', 'access_type': 'subscriber'}
        ])
        self.rest_server.backend.pattern_matcher.add_client('admin_user', [
            {'pattern': 'test.topic', 'access_type': 'subscriber'}
        ])
        self.rest_server.backend.pattern_matcher.add_client('user1', [
            {'pattern': 'test.topic', 'access_type': 'subscriber'}
        ])
        self.rest_server.backend.pattern_matcher.add_client('user2', [
            {'pattern': 'test.topic', 'access_type': 'subscriber'}
        ])

        # Test data constants
        self.test_cid = 'test-cid-123'
        self.test_topic = 'test.topic'
        self.test_username = 'test_user'

        # Mock RabbitMQ fetch to return empty list
        def mock_fetch_from_rabbitmq(cid, api_url, rabbitmq_payload):
            return []

        self.rest_server._fetch_from_rabbitmq = mock_fetch_from_rabbitmq

        # Mock backend fetch_messages to return empty list
        def mock_fetch_messages(cid, sub_key, max_messages, max_len):
            return []

        self.rest_server.backend.fetch_messages = mock_fetch_messages

        # Mock _find_user_sub_key to return a subscription key and topic
        def mock_find_user_sub_key(cid, username):
            return 'test_sub_key_123', 'test.topic'

        self.rest_server._find_user_sub_key = mock_find_user_sub_key

        # Set up test subscription
        subscription = Subscription()
        subscription.topic_name = self.test_topic
        subscription.sec_name = self.test_username
        subscription.sub_key = 'test_sub_key_123'

        self.rest_server.backend.subs_by_topic = {
            self.test_topic: {
                self.test_username: subscription
            }
        }

    def _create_environ(self, json_data, username='test_user', password='test_password'):
        """ Helper to create WSGI environ with JSON data and HTTP Basic Auth.
        """
        json_str = json.dumps(json_data)

        # Create HTTP Basic Auth header
        credentials = f'{username}:{password}'
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('ascii')
        auth_header = f'Basic {encoded_credentials}'

        return {
            'REQUEST_METHOD': 'GET',
            'CONTENT_TYPE': 'application/json',
            'CONTENT_LENGTH': str(len(json_str)),
            'HTTP_AUTHORIZATION': auth_header,
            'PATH_INFO': '/messages',
            'wsgi.input': type('MockInput', (), {'read': lambda self, size=-1: json_str.encode('utf-8')})()
        }

# ################################################################################################################################

    def test_on_messages_get_calls_authenticate_with_correct_params(self):
        """ on_messages_get calls authenticate method with correct parameters.
        """
        # Track authentication calls
        auth_calls = []
        original_authenticate = self.rest_server.authenticate

        def track_authenticate(cid, environ):
            auth_calls.append((cid, environ))
            return original_authenticate(cid, environ)

        self.rest_server.authenticate = track_authenticate

        # Create request with valid credentials
        environ = self._create_environ({'max_messages': 1})

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify authenticate was called with correct parameters
        self.assertEqual(len(auth_calls), 1)
        self.assertEqual(auth_calls[0][0], self.test_cid)
        self.assertEqual(auth_calls[0][1], environ)

        # Verify successful authentication
        self.assertTrue(response.is_ok)

# ################################################################################################################################

    def test_on_messages_get_uses_authenticated_username(self):
        """ on_messages_get uses the username returned by authenticate.
        """
        # Set different username and credentials
        different_username = 'different_user'
        different_password = 'different_password'
        different_sub_key = 'different_sub_key_456'

        # Add subscription for different user
        subscription = Subscription()
        subscription.topic_name = self.test_topic
        subscription.sec_name = different_username
        subscription.sub_key = different_sub_key

        # Ensure the topic exists in subs_by_topic
        if self.test_topic not in self.rest_server.backend.subs_by_topic:
            self.rest_server.backend.subs_by_topic[self.test_topic] = {}
        self.rest_server.backend.subs_by_topic[self.test_topic][different_username] = subscription

        # Create request with different user credentials
        environ = self._create_environ({'max_messages': 1}, different_username, different_password)

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify the different username was used (subscription found)
        self.assertTrue(response.is_ok)

# ################################################################################################################################

    def test_on_messages_get_handles_authentication_failure(self):
        """ on_messages_get handles authentication failure properly.
        """
        # Create request with invalid credentials
        environ = self._create_environ({'max_messages': 1}, 'invalid_user', 'invalid_password')

        # Call method and expect exception
        with self.assertRaises(UnauthorizedException) as context:
            _ = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify exception details
        self.assertEqual(context.exception.cid, self.test_cid)

# ################################################################################################################################

    def test_on_messages_get_handles_missing_auth_header(self):
        """ on_messages_get handles missing authentication header properly.
        """
        # Create request without authentication header
        json_str = json.dumps({'max_messages': 1})
        environ = {
            'REQUEST_METHOD': 'GET',
            'CONTENT_TYPE': 'application/json',
            'CONTENT_LENGTH': str(len(json_str)),
            'PATH_INFO': '/messages',
            'wsgi.input': type('MockInput', (), {'read': lambda self, size=-1: json_str.encode('utf-8')})()
        }

        # Call method and expect exception
        with self.assertRaises(UnauthorizedException) as context:
            _ = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify exception details
        self.assertEqual(context.exception.cid, self.test_cid)

# ################################################################################################################################

    def test_on_messages_get_authentication_happens_before_processing(self):
        """ on_messages_get performs authentication before any other processing.
        """
        # Track method calls
        method_calls = []

        # Override methods to track calls
        original_authenticate = self.rest_server.authenticate
        original_parse_json = self.rest_server._parse_json
        original_validate_params = self.rest_server._validate_get_params

        def track_authenticate(cid, environ):
            method_calls.append('authenticate')
            return original_authenticate(cid, environ)

        def track_parse_json(cid, request):
            method_calls.append('parse_json')
            return original_parse_json(cid, request)

        def track_validate_params(data):
            method_calls.append('validate_params')
            return original_validate_params(data)

        self.rest_server.authenticate = track_authenticate
        self.rest_server._parse_json = track_parse_json
        self.rest_server._validate_get_params = track_validate_params

        # Create request
        environ = self._create_environ({'max_messages': 1})

        # Call method
        _ = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify authenticate was called first
        self.assertTrue(len(method_calls) >= 3)
        self.assertEqual(method_calls[0], 'authenticate')
        self.assertIn('parse_json', method_calls)
        self.assertIn('validate_params', method_calls)

# ################################################################################################################################

    def test_on_messages_get_stops_processing_on_auth_failure(self):
        """ on_messages_get stops processing when authentication fails.
        """
        # Track method calls
        method_calls = []

        # Override methods to track calls
        original_parse_json = self.rest_server._parse_json

        def track_parse_json(cid, request):
            method_calls.append('parse_json')
            return original_parse_json(cid, request)

        self.rest_server._parse_json = track_parse_json

        # Create request with invalid credentials
        environ = self._create_environ({'max_messages': 1}, 'invalid_user', 'invalid_password')

        # Call method and expect exception
        with self.assertRaises(UnauthorizedException):
            _ = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify no further processing occurred
        self.assertEqual(len(method_calls), 0)

# ################################################################################################################################

    def test_on_messages_get_with_different_usernames(self):
        """ on_messages_get works correctly with different authenticated usernames.
        """
        test_cases = [
            ('user1', 'password1', 'sub_key_1'),
            ('user2', 'password2', 'sub_key_2'),
            ('admin_user', 'admin_password', 'admin_sub_key'),
        ]

        for username, password, sub_key in test_cases:
            with self.subTest(username=username):
                # Set up subscription for this user
                subscription = Subscription()
                subscription.topic_name = self.test_topic
                subscription.sec_name = username
                subscription.sub_key = sub_key

                # Ensure the topic exists in subs_by_topic
                if self.test_topic not in self.rest_server.backend.subs_by_topic:
                    self.rest_server.backend.subs_by_topic[self.test_topic] = {}
                self.rest_server.backend.subs_by_topic[self.test_topic][username] = subscription

                # Create request with this user's credentials
                environ = self._create_environ({'max_messages': 1}, username, password)

                # Call method
                response = self.rest_server.on_messages_get(self.test_cid, environ, None)

                # Verify success for this user
                self.assertTrue(response.is_ok)
                self.assertEqual(response.cid, self.test_cid)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
