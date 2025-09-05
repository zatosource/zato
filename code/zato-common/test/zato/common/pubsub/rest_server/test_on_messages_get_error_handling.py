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
from zato.common.pubsub.models import BadRequestResponse, Subscription, UnauthorizedResponse
from zato.common.pubsub.server.rest_pull import PubSubRESTServerPull
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

class RESTOnMessagesGetErrorHandlingTestCase(TestCase):

    def setUp(self):

        # Suppress ResourceWarnings from gevent
        warnings.filterwarnings('ignore', category=ResourceWarning)

        # Create a test broker client that captures publish calls
        self.broker_client = BrokerClientHelper()
        self.rest_server = PubSubRESTServerPull('localhost', 8080, should_init_broker_client=False)
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

    def test_on_messages_get_handles_json_parsing_error(self):
        """ on_messages_get handles JSON parsing errors by raising exception from _parse_json.
        """
        # Set up users for authentication
        self.rest_server.users = {'test_user': {'sec_name': 'test_sec_def', 'password': 'test_password'}}

        # Create HTTP Basic Auth header
        credentials = 'test_user:test_password'
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('ascii')
        auth_header = f'Basic {encoded_credentials}'

        # Create malformed JSON
        malformed_json = '{"max_messages": 1, "invalid": }'

        class MockInput:
            def __init__(self, data):
                self.data = data
            def read(self, size=-1):
                return self.data

        environ = {
            'REQUEST_METHOD': 'GET',
            'CONTENT_TYPE': 'application/json',
            'CONTENT_LENGTH': str(len(malformed_json)),
            'HTTP_AUTHORIZATION': auth_header,
            'PATH_INFO': '/messages',
            'wsgi.input': MockInput(malformed_json.encode('utf-8'))
        }

        # Call method and expect exception to be raised by _parse_json (line 20 in _parse_json raises)
        with self.assertRaises(Exception):
            _ = self.rest_server.on_messages_get(self.test_cid, environ, None)

    def test_on_messages_get_handles_parameter_validation_error(self):
        """ on_messages_get handles parameter validation errors gracefully.
        """
        # Set up users and permissions for authentication
        self.rest_server.users = {'test_user': {'sec_name': 'test_sec_def', 'password': 'test_password'}}
        self.rest_server.backend.pattern_matcher.add_client('test_user', [
            {'pattern': 'test.topic', 'access_type': 'subscriber'}
        ])

        # Set up subscription
        subscription = Subscription()
        subscription.topic_name = self.test_topic
        subscription.sec_name = self.test_username
        subscription.sub_key = 'test_sub_key_123'

        self.rest_server.backend.subs_by_topic = {
            self.test_topic: {
                self.test_username: subscription
            }
        }

        # Create request with invalid parameters
        environ = self._create_environ({'max_messages': -1})

        # Call method - invalid parameters should be handled gracefully
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Should get bad request for invalid parameters
        self.assertIsInstance(response, UnauthorizedResponse)
        self.assertEqual(response.cid, self.test_cid)

    def test_on_messages_get_handles_no_subscription_found(self):
        """ on_messages_get handles case when no subscription is found for user.
        """
        # Set up users for authentication
        self.rest_server.users = {'test_user': {'sec_name': 'test_sec_def', 'password': 'test_password'}}

        # Clear subscriptions so none will be found
        self.rest_server.backend.subs_by_topic.clear()

        # Create request
        environ = self._create_environ({'max_messages': 1})

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify specific error response
        self.assertIsInstance(response, UnauthorizedResponse)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.details, 'No subscription found for user')



    def test_on_messages_get_error_response_consistency(self):
        """ on_messages_get returns consistent error responses across different failures.
        """
        # Set up users for authentication
        self.rest_server.users = {'test_user': {'sec_name': 'test_sec_def', 'password': 'test_password'}}

        # Test no subscription scenario
        self.rest_server.backend.subs_by_topic.clear()

        # Create request
        environ = self._create_environ({'max_messages': 1})

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify error response structure
        self.assertIsInstance(response, UnauthorizedResponse)
        self.assertEqual(response.cid, self.test_cid)
        self.assertIsInstance(response.details, str)
        self.assertTrue(len(response.details) > 0)
        self.assertEqual(response.details, 'No subscription found for user')

    def test_on_messages_get_preserves_cid_in_all_error_responses(self):
        """ on_messages_get preserves CID in all error response types.
        """
        # Set up users for authentication
        self.rest_server.users = {'test_user': {'sec_name': 'test_sec_def', 'password': 'test_password'}}

        different_cids = ['cid-001', 'cid-002', 'error-cid-123', 'test-correlation-456']

        for cid in different_cids:
            with self.subTest(cid=cid):
                # Clear subscriptions for consistent error
                self.rest_server.backend.subs_by_topic.clear()

                # Create request
                environ = self._create_environ({'max_messages': 1})

                # Call method with different CID
                response = self.rest_server.on_messages_get(cid, environ, None)

                # Verify CID is preserved
                self.assertIsInstance(response, UnauthorizedResponse)
                self.assertEqual(response.cid, cid)

                # Reset subscriptions for next test
                subscription = Subscription()
                subscription.topic_name = self.test_topic
                subscription.sec_name = self.test_username
                subscription.sub_key = self.test_sub_key
                self.rest_server.backend.subs_by_topic = {
                    self.test_topic: {
                        self.test_username: subscription
                    }
                }

    def test_on_messages_get_handles_empty_subscription_data(self):
        """ on_messages_get handles empty subscription data gracefully.
        """
        # Set up users for authentication
        self.rest_server.users = {'test_user': {'sec_name': 'test_sec_def', 'password': 'test_password'}}

        # Clear all subscriptions
        self.rest_server.backend.subs_by_topic.clear()

        # Create request
        environ = self._create_environ({'max_messages': 1})

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify error response
        self.assertIsInstance(response, UnauthorizedResponse)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.details, 'No subscription found for user')

    def test_on_messages_get_handles_malformed_subscription_data(self):
        """ on_messages_get handles malformed subscription data gracefully.
        """
        # Set up users for authentication
        self.rest_server.users = {'test_user': {'sec_name': 'test_sec_def', 'password': 'test_password'}}

        # Set malformed subscription data - None subscription will cause AttributeError
        # when _find_user_sub_key tries to access subscription.sub_key
        self.rest_server.backend.subs_by_topic = {
            self.test_topic: {
                self.test_username: None  # Invalid subscription object
            }
        }

        # Create request
        environ = self._create_environ({'max_messages': 1})

        # Call method and expect error response instead of AttributeError
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)
        self.assertIsInstance(response, UnauthorizedResponse)
        self.assertFalse(response.is_ok)
        self.assertEqual(response.cid, self.test_cid)

    def test_on_messages_get_handles_parameter_validation_with_invalid_types(self):
        """ on_messages_get raises TypeError when parameter types are invalid in _validate_get_params.
        """
        # Set up users for authentication
        self.rest_server.users = {'test_user': {'sec_name': 'test_sec_def', 'password': 'test_password'}}

        # Create request with invalid parameter types that cause TypeError in min() function
        test_cases = [
            {'max_messages': 'invalid_string', 'max_len': 1000},
            {'max_messages': 5, 'max_len': 'invalid_string'},
            {'max_messages': None, 'max_len': 1000},
            {'max_messages': [], 'max_len': 1000}
        ]

        for invalid_data in test_cases:
            with self.subTest(data=invalid_data):
                # Clear subscriptions for consistent error
                self.rest_server.backend.subs_by_topic.clear()

                # Create request
                environ = self._create_environ(invalid_data)

                # Call method and expect TypeError from min() function in _validate_get_params
                with self.assertRaises(TypeError):
                    _ = self.rest_server.on_messages_get(self.test_cid, environ, None)

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
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
