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
import warnings
from unittest import main, TestCase

# Zato
from zato.common.pubsub.backend.rest_backend import RESTBackend
from zato.common.pubsub.models import StatusResponse
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

class RESTOnUnsubscribeAuthenticationTestCase(TestCase):

    def setUp(self):

        # Suppress ResourceWarnings from gevent
        warnings.filterwarnings('ignore', category=ResourceWarning)

        # Create a test broker client that captures publish calls
        self.broker_client = BrokerClientHelper()
        self.rest_server = PubSubRESTServer('localhost', 8080, should_init_broker_client=False)
        self.rest_server.backend = RESTBackend(self.rest_server, self.broker_client) # type: ignore

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

# ################################################################################################################################

    def _create_environ(self, username='test_user', password='test_password'):
        """ Helper to create WSGI environ with HTTP Basic Auth.
        """
        # Create HTTP Basic Auth header
        credentials = f'{username}:{password}'
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('ascii')
        auth_header = f'Basic {encoded_credentials}'

        return {
            'REQUEST_METHOD': 'DELETE',
            'CONTENT_TYPE': 'application/json',
            'HTTP_AUTHORIZATION': auth_header,
            'PATH_INFO': f'/unsubscribe/{self.test_topic}',
        }

# ################################################################################################################################

    def test_on_unsubscribe_calls_authenticate_with_correct_params(self):
        """ on_unsubscribe calls authenticate method with correct parameters.
        """
        # Track authenticate calls
        authenticate_calls = []

        def track_authenticate(cid, environ):
            authenticate_calls.append((cid, environ))
            return self.test_username

        self.rest_server.authenticate = track_authenticate

        # Mock backend unregister_subscription to avoid broker call
        def mock_unregister_subscription(cid, topic_name, username=''):

            response = StatusResponse()
            response.is_ok = True
            return response

        self.rest_server.backend.unregister_subscription = mock_unregister_subscription

        # Create request
        environ = self._create_environ()

        # Call method
        response = self.rest_server.on_unsubscribe(self.test_cid, environ, None, self.test_topic)

        # Verify authenticate was called with correct parameters
        self.assertEqual(len(authenticate_calls), 1)
        cid, passed_environ = authenticate_calls[0]
        self.assertEqual(cid, self.test_cid)
        self.assertEqual(passed_environ, environ)

        # Verify successful response
        self.assertTrue(response.is_ok)
        self.assertEqual(response.cid, self.test_cid)

# ################################################################################################################################

    def test_on_unsubscribe_uses_authenticated_username(self):
        """ on_unsubscribe uses the username returned by authenticate.
        """
        expected_username = 'authenticated_user'

        # Add permissions for the authenticated user
        self.rest_server.backend.pattern_matcher.add_client(expected_username, [
            {'pattern': 'test.topic', 'access_type': 'subscriber'}
        ])

        # Track backend calls
        backend_calls = []

        def track_unregister_subscription(cid, topic_name, username=''):
            backend_calls.append((cid, topic_name, username))

            response = StatusResponse()
            response.is_ok = True
            return response

        self.rest_server.backend.unregister_subscription = track_unregister_subscription

        # Override authenticate to return specific username
        def mock_authenticate(cid, environ):
            return expected_username

        self.rest_server.authenticate = mock_authenticate

        # Create request
        environ = self._create_environ()

        # Call method
        _ = self.rest_server.on_unsubscribe(self.test_cid, environ, None, self.test_topic)

        # Verify backend was called with authenticated username
        self.assertEqual(len(backend_calls), 1)
        _, _, username = backend_calls[0]
        self.assertEqual(username, expected_username)

# ################################################################################################################################

    def test_on_unsubscribe_with_different_usernames(self):
        """ on_unsubscribe works correctly with different authenticated usernames.
        """
        test_usernames = ['user1', 'user2', 'admin_user']

        for username in test_usernames:
            with self.subTest(username=username):
                # Add permissions for the user
                self.rest_server.backend.pattern_matcher.add_client(username, [
                    {'pattern': 'test.topic', 'access_type': 'subscriber'}
                ])

                # Track backend calls
                backend_calls = []

                def track_unregister_subscription(cid, topic_name, username=''):
                    backend_calls.append((cid, topic_name, username))

                    response = StatusResponse()
                    response.is_ok = True
                    return response

                self.rest_server.backend.unregister_subscription = track_unregister_subscription

                # Override authenticate to return specific username
                def mock_authenticate(cid, environ):
                    return username

                self.rest_server.authenticate = mock_authenticate

                # Create request
                environ = self._create_environ()

                # Call method
                response = self.rest_server.on_unsubscribe(self.test_cid, environ, None, self.test_topic)

                # Verify success
                self.assertTrue(response.is_ok)
                self.assertEqual(response.cid, self.test_cid)

                # Verify backend was called with correct username
                self.assertEqual(len(backend_calls), 1)
                _, _, passed_username = backend_calls[0]
                self.assertEqual(passed_username, username)

# ################################################################################################################################

    def test_on_unsubscribe_handles_authentication_failure(self):
        """ on_unsubscribe handles authentication failure properly.
        """
        # Create request with invalid credentials
        environ = self._create_environ('invalid_user', 'invalid_password')

        # Call method and expect exception
        with self.assertRaises(UnauthorizedException) as context:
            _ = self.rest_server.on_unsubscribe(self.test_cid, environ, None, self.test_topic)

        # Verify exception details
        self.assertEqual(context.exception.cid, self.test_cid)

# ################################################################################################################################

    def test_on_unsubscribe_handles_missing_auth_header(self):
        """ on_unsubscribe handles missing authentication header properly.
        """
        # Create request without authentication header
        environ = {
            'REQUEST_METHOD': 'DELETE',
            'CONTENT_TYPE': 'application/json',
            'PATH_INFO': f'/unsubscribe/{self.test_topic}',
        }

        # Call method and expect exception
        with self.assertRaises(UnauthorizedException) as context:
            _ = self.rest_server.on_unsubscribe(self.test_cid, environ, None, self.test_topic)

        # Verify exception details
        self.assertEqual(context.exception.cid, self.test_cid)

# ################################################################################################################################

    def test_on_unsubscribe_authentication_happens_before_processing(self):
        """ on_unsubscribe performs authentication before any other processing.
        """
        # Track method calls
        method_calls = []

        # Override methods to track calls
        original_authenticate = self.rest_server.authenticate

        def track_authenticate(cid, environ):
            method_calls.append('authenticate')
            return original_authenticate(cid, environ)

        def track_unregister_subscription(cid, topic_name, *, sec_name='', username=''):
            method_calls.append('unregister_subscription')

            response = StatusResponse()
            response.is_ok = True
            return response

        self.rest_server.authenticate = track_authenticate
        self.rest_server.backend.unregister_subscription = track_unregister_subscription

        # Create request
        environ = self._create_environ()

        # Call method
        _ = self.rest_server.on_unsubscribe(self.test_cid, environ, None, self.test_topic)

        # Verify authenticate was called first
        self.assertTrue(len(method_calls) >= 2)
        self.assertEqual(method_calls[0], 'authenticate')
        self.assertIn('unregister_subscription', method_calls)

# ################################################################################################################################

    def test_on_unsubscribe_stops_processing_on_auth_failure(self):
        """ on_unsubscribe stops processing when authentication fails.
        """
        # Track method calls
        method_calls = []

        # Override method to track calls
        def track_unregister_subscription(cid, topic_name, *, sec_name='', username=''):
            method_calls.append('unregister_subscription')

            response = StatusResponse()
            response.is_ok = True
            return response

        self.rest_server.backend.unregister_subscription = track_unregister_subscription

        # Create request with invalid credentials
        environ = self._create_environ('invalid_user', 'invalid_password')

        # Call method and expect exception
        with self.assertRaises(UnauthorizedException):
            _ = self.rest_server.on_unsubscribe(self.test_cid, environ, None, self.test_topic)

        # Verify no further processing occurred
        self.assertEqual(len(method_calls), 0)

# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
