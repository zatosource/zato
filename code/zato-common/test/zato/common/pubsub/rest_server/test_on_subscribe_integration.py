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
from zato.common.pubsub.server.rest_publish import PubSubRESTServerPublish

# ################################################################################################################################
# ################################################################################################################################

class BrokerClientHelper:
    """ Test broker client that captures publish calls without mocking.
    """

    def __init__(self):
        self.published_messages = []
        self.published_exchanges = []
        self.published_routing_keys = []
        self.cluster_id = 'test-cluster'

    def publish(self, message, exchange, routing_key):
        """ Capture publish parameters for verification.
        """
        self.published_messages.append(message)
        self.published_exchanges.append(exchange)
        self.published_routing_keys.append(routing_key)

    def invoke_sync(self, service, request, timeout=20, needs_root_elem=False):
        """ Mock service invocation for security definitions.
        """
        return [
            {'username': 'allowed_user', 'name': 'allowed_user_sec'},
            {'username': 'denied_user', 'name': 'denied_user_sec'},
            {'username': 'admin_user', 'name': 'admin_user_sec'},
            {'username': 'test_user', 'name': 'test_user_sec'}
        ]

    def create_bindings(self, cid, sub_key, exchange_name, queue_name, topic_name):
        """ Mock AMQP binding creation.
        """
        pass

# ################################################################################################################################
# ################################################################################################################################

class RESTOnSubscribeIntegrationTestCase(TestCase):

    def setUp(self):

        # Suppress ResourceWarnings from gevent
        warnings.filterwarnings('ignore', category=ResourceWarning)

        # Create a test broker client that captures publish calls
        self.broker_client = BrokerClientHelper()
        self.rest_server = PubSubRESTServerPublish('localhost', 8080, should_init_broker_client=False)
        self.rest_server.backend = RESTBackend(self.rest_server, self.broker_client) # type: ignore
        self.rest_server.users = {'test_user': {'sec_name': 'test_sec_def', 'password': 'test_password'}}

        # Mock broker client invoke_sync to return dict with error key
        def mock_invoke_sync(service, request, timeout=None, needs_root_elem=False):
            if needs_root_elem:
                return {'error': None}
            return []

        self.broker_client.invoke_sync = mock_invoke_sync

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
            'REQUEST_METHOD': 'POST',
            'CONTENT_TYPE': 'application/json',
            'HTTP_AUTHORIZATION': auth_header,
            'PATH_INFO': f'/subscribe/{self.test_topic}',
        }

# ################################################################################################################################

    def test_on_subscribe_returns_success_when_all_conditions_met(self):
        """ on_subscribe returns success response when all conditions are met.
        """
        # Create request
        environ = self._create_environ()

        # Call method
        response = self.rest_server.on_subscribe(self.test_cid, environ, None, self.test_topic)

        # Verify success response
        self.assertTrue(response.is_ok)
        self.assertEqual(response.cid, self.test_cid)

# ################################################################################################################################

    def test_on_subscribe_calls_backend_register_subscription(self):
        """ on_subscribe calls backend register_subscription with correct parameters.
        """
        # Track backend calls
        backend_calls = []

        def track_register_subscription(cid, topic_name, username=None, username_to_sec_name=None, sub_key='', should_create_bindings=True, should_invoke_server=False):
            backend_calls.append((cid, topic_name, username, username_to_sec_name, sub_key, should_create_bindings))

            response = StatusResponse()
            response.is_ok = True
            return response

        self.rest_server.backend.register_subscription = track_register_subscription

        # Create request
        environ = self._create_environ()

        # Call method
        _ = self.rest_server.on_subscribe(self.test_cid, environ, None, self.test_topic)

        # Verify backend was called with correct parameters
        self.assertEqual(len(backend_calls), 1)
        cid, topic_name, username, username_to_sec_name, sub_key, should_create_bindings = backend_calls[0]
        self.assertEqual(cid, self.test_cid)
        self.assertEqual(topic_name, self.test_topic)
        self.assertEqual(username, self.test_username)
        self.assertIsNone(username_to_sec_name)
        self.assertEqual(sub_key, '')  # Default empty sub_key
        self.assertTrue(should_create_bindings)  # Default True

# ################################################################################################################################

    def test_on_subscribe_propagates_backend_response(self):
        """ on_subscribe propagates backend response correctly.
        """
        # Mock backend to return specific response
        def mock_register_subscription(cid, topic_name, username=None, username_to_sec_name=None, sub_key='', should_create_bindings=True, should_invoke_server=False):

            response = StatusResponse()
            response.is_ok = False  # Simulate failure
            return response

        self.rest_server.backend.register_subscription = mock_register_subscription

        # Create request
        environ = self._create_environ()

        # Call method
        response = self.rest_server.on_subscribe(self.test_cid, environ, None, self.test_topic)

        # Verify response propagation
        self.assertFalse(response.is_ok)
        self.assertEqual(response.cid, self.test_cid)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
