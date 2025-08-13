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

class RESTOnUnsubscribePermissionCheckingTestCase(TestCase):

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
        self.test_cid = 'test-cid-123'
        self.test_topic = 'test.topic'
        self.restricted_topic = 'restricted.topic'

        # Clear pattern matcher and set up permissions
        self.rest_server.backend.pattern_matcher._clients = {}
        self.rest_server.backend.pattern_matcher._pattern_cache = {}

        # Add permissions for users
        self.rest_server.backend.pattern_matcher.add_client('test_user', [
            {'pattern': 'test.*', 'access_type': 'subscriber'}
        ])
        self.rest_server.backend.pattern_matcher.add_client('allowed_user', [
            {'pattern': 'test.*', 'access_type': 'subscriber'}
        ])
        self.rest_server.backend.pattern_matcher.add_client('admin_user', [
            {'pattern': 'restricted.*', 'access_type': 'subscriber'}
        ])
        # denied_user gets no permissions

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

    def test_on_unsubscribe_allows_user_with_subscribe_permission(self):
        """ on_unsubscribe allows user with subscribe permission to unsubscribe.
        """
        # Mock backend unregister_subscription
        def mock_unregister_subscription(cid, topic_name, username=''):

            response = StatusResponse()
            response.is_ok = True
            return response

        self.rest_server.backend.unregister_subscription = mock_unregister_subscription

        # Create request
        environ = self._create_environ()

        # Call method
        response = self.rest_server.on_unsubscribe(self.test_cid, environ, None, self.test_topic)

        # Verify success
        self.assertTrue(response.is_ok)
        self.assertEqual(response.cid, self.test_cid)

# ################################################################################################################################

    def test_on_unsubscribe_denies_user_without_subscribe_permission(self):
        """ on_unsubscribe denies user without subscribe permission.
        """
        # Create request for user without permission
        environ = self._create_environ('denied_user', 'denied_password')

        # Call method and expect exception
        with self.assertRaises(UnauthorizedException) as context:
            _ = self.rest_server.on_unsubscribe(self.test_cid, environ, None, self.test_topic)

        # Verify exception details
        self.assertEqual(context.exception.cid, self.test_cid)

# ################################################################################################################################

    def test_on_unsubscribe_allows_wildcard_permissions(self):
        """ on_unsubscribe allows users with wildcard permissions.
        """
        # Mock backend unregister_subscription
        def mock_unregister_subscription(cid, topic_name, username=''):

            response = StatusResponse()
            response.is_ok = True
            return response

        self.rest_server.backend.unregister_subscription = mock_unregister_subscription

        # Create request
        environ = self._create_environ('allowed_user', 'allowed_password')

        # Call method
        response = self.rest_server.on_unsubscribe(self.test_cid, environ, None, self.test_topic)

        # Verify success
        self.assertTrue(response.is_ok)
        self.assertEqual(response.cid, self.test_cid)

# ################################################################################################################################

    def test_on_unsubscribe_allows_double_wildcard_permissions(self):
        """ on_unsubscribe allows users with double wildcard permissions.
        """
        # Mock backend unregister_subscription
        def mock_unregister_subscription(cid, topic_name, username=''):

            response = StatusResponse()
            response.is_ok = True
            return response

        self.rest_server.backend.unregister_subscription = mock_unregister_subscription

        # Create request
        environ = self._create_environ('admin_user', 'admin_password')

        # Call method
        response = self.rest_server.on_unsubscribe(self.test_cid, environ, None, self.restricted_topic)

        # Verify success
        self.assertTrue(response.is_ok)
        self.assertEqual(response.cid, self.test_cid)

# ################################################################################################################################

    def test_on_unsubscribe_permission_check_happens_after_authentication(self):
        """ on_unsubscribe performs permission check after authentication.
        """
        # Track method calls
        method_calls = []

        def track_authenticate(cid, environ):
            method_calls.append('authenticate')
            return 'test_user'

        def track_evaluate(username, topic_name, operation):
            method_calls.append('evaluate')

            response = StatusResponse()
            response.is_ok = True
            return response

        def mock_unregister_subscription(cid, topic_name, username=''):

            response = StatusResponse()
            response.is_ok = True
            return response

        self.rest_server.authenticate = track_authenticate
        self.rest_server.backend.pattern_matcher.evaluate = track_evaluate
        self.rest_server.backend.unregister_subscription = mock_unregister_subscription

        # Create request
        environ = self._create_environ()

        # Call method
        _ = self.rest_server.on_unsubscribe(self.test_cid, environ, None, self.test_topic)

        # Verify order: authenticate should be called before evaluate
        self.assertEqual(method_calls, ['authenticate', 'evaluate'])
        self.assertIn('evaluate', method_calls)
        auth_index = method_calls.index('authenticate')
        eval_index = method_calls.index('evaluate')
        self.assertLess(auth_index, eval_index)

# ################################################################################################################################

    def test_on_unsubscribe_uses_correct_topic_name_for_permission_check(self):
        """ on_unsubscribe uses correct topic name for permission check.
        """
        # Track evaluate calls
        evaluate_calls = []

        def track_evaluate(username, topic_name, operation):
            evaluate_calls.append((username, topic_name, operation))

            response = StatusResponse()
            response.is_ok = True
            return response

        def mock_unregister_subscription(cid, topic_name, username=''):

            response = StatusResponse()
            response.is_ok = True
            return response

        self.rest_server.backend.pattern_matcher.evaluate = track_evaluate
        self.rest_server.backend.unregister_subscription = mock_unregister_subscription

        # Create request
        environ = self._create_environ('test_user', 'test_password')

        # Call method
        _ = self.rest_server.on_unsubscribe(self.test_cid, environ, None, self.test_topic)

        # Verify evaluate was called with correct parameters
        self.assertEqual(len(evaluate_calls), 1)
        username, topic_name, operation = evaluate_calls[0]
        self.assertEqual(username, 'test_user')
        self.assertEqual(topic_name, self.test_topic)
        self.assertEqual(operation, 'subscribe')

# ################################################################################################################################

    def test_on_unsubscribe_stops_processing_on_permission_failure(self):
        """ on_unsubscribe stops processing when permission check fails.
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

        # Create request for user without permission
        environ = self._create_environ('denied_user', 'denied_password')

        # Call method and expect exception
        with self.assertRaises(UnauthorizedException):
            _ = self.rest_server.on_unsubscribe(self.test_cid, environ, None, self.test_topic)

        # Verify no further processing occurred
        self.assertEqual(len(method_calls), 0)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
