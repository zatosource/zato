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
from zato.common.test import rand_string

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

class RESTOnUnsubscribeIntegrationTestCase(TestCase):

    def setUp(self):

        # Suppress ResourceWarnings from gevent
        warnings.filterwarnings('ignore', category=ResourceWarning)

        # Create a test broker client that captures publish calls
        self.broker_client = BrokerClientHelper()
        self.rest_server = PubSubRESTServer('localhost', 8080, should_init_broker_client=False)
        self.rest_server.backend = RESTBackend(self.rest_server, self.broker_client) # type: ignore
        self.rest_server.users = {'test_user': 'test_password'}

        # Set up permissions for test_user
        self.rest_server.backend.pattern_matcher.add_client('test_user', [
            {'pattern': 'test.topic', 'access_type': 'subscriber'}
        ])

        # Test data constants
        self.test_cid = 'test-cid-123'
        self.test_username = 'test_user'
        self.test_topic = 'test.topic'

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

    def test_on_unsubscribe_returns_success_when_all_conditions_met(self):
        """ on_unsubscribe returns success response when all conditions are met.
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

    def test_on_unsubscribe_calls_backend_unregister_subscription(self):
        """ on_unsubscribe calls backend unregister_subscription with correct parameters.
        """
        # Track backend calls
        backend_calls = []

        def track_unregister_subscription(cid, topic_name, *, sec_name='', username=''):
            backend_calls.append((cid, topic_name, sec_name, username))

            response = StatusResponse()
            response.is_ok = True
            return response

        self.rest_server.backend.unregister_subscription = track_unregister_subscription

        # Create request
        environ = self._create_environ()

        # Call method
        _ = self.rest_server.on_unsubscribe(self.test_cid, environ, None, self.test_topic)

        # Verify backend was called with correct parameters
        self.assertEqual(len(backend_calls), 1)
        cid, topic_name, sec_name, username = backend_calls[0]
        self.assertEqual(cid, self.test_cid)
        self.assertEqual(topic_name, self.test_topic)
        self.assertEqual(sec_name, '')  # Default empty sec_name
        self.assertEqual(username, self.test_username)

# ################################################################################################################################

    def test_on_unsubscribe_propagates_backend_response(self):
        """ on_unsubscribe propagates backend response correctly.
        """
        # Mock backend to return specific response
        def mock_unregister_subscription(cid, topic_name, *, sec_name='', username=''):

            response = StatusResponse()
            response.is_ok = False  # Simulate failure
            return response

        self.rest_server.backend.unregister_subscription = mock_unregister_subscription

        # Create request
        environ = self._create_environ()

        # Call method
        response = self.rest_server.on_unsubscribe(self.test_cid, environ, None, self.test_topic)

        # Verify response propagation
        self.assertFalse(response.is_ok)
        self.assertEqual(response.cid, self.test_cid)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
