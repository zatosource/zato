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
from zato.common.pubsub.models import BadRequestResponse, Subscription, UnauthorizedResponse
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

    def publish(self, message, exchange, routing_key):
        """ Capture publish parameters for verification.
        """
        self.published_messages.append(message)
        self.published_exchanges.append(exchange)
        self.published_routing_keys.append(routing_key)

# ################################################################################################################################
# ################################################################################################################################

class RESTOnMessagesGetIntegrationTestCase(TestCase):

    def setUp(self):

        # Suppress ResourceWarnings from gevent
        warnings.filterwarnings('ignore', category=ResourceWarning)

        # Create a test broker client that captures publish calls
        self.broker_client = BrokerClientHelper()
        self.rest_server = PubSubRESTServerPublish('localhost', 8080, should_init_broker_client=False)
        self.rest_server.backend = RESTBackend(self.rest_server, self.broker_client) # type: ignore
        self.rest_server.users = {'test_user': {'sec_name': 'test_sec_def', 'password': 'test_password'}}

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
                'test_sec_def': subscription
            }
        }

    def _create_environ(self, json_data, username='test_user', password='test_password'):
        """ Helper to create WSGI environ with JSON data and HTTP Basic Auth.
        """
        import json
        import base64
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

    def test_on_messages_get_returns_success_with_messages(self):
        """ on_messages_get returns success response with transformed messages when all conditions are met.
        """
        # Set up permissions for test_user
        self.rest_server.backend.pattern_matcher.add_client('test_user', [
            {'pattern': self.test_topic, 'access_type': 'subscriber'}
        ])

        # Mock _fetch_from_rabbitmq to return test messages
        def mock_fetch_from_rabbitmq(cid, api_url, payload):
            return [
                {
                    'payload': {
                        'data': 'test message 1',
                        'msg_id': 'msg_1',
                        'correl_id': 'corr_1',
                        'priority': 5,
                        'pub_time_iso': '2025-01-01T12:00:00+00:00',
                        'recv_time_iso': '2025-01-01T12:00:00+00:00',
                        'expiration': '0',
                        'topic_name': '',
                        'ext_client_id': '',
                        'expiration_time_iso': '',
                        'in_reply_to': '',
                        'size': 14
                    },
                    'properties': {
                        'message_id': 'msg_1',
                        'correlation_id': 'corr_1'
                    }
                }
            ]

        self.rest_server._fetch_from_rabbitmq = mock_fetch_from_rabbitmq

        # Create request
        environ = self._create_environ({'max_messages': 1})

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify success response
        self.assertTrue(response.is_ok)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.message_count, 1)
        self.assertEqual(response.data, 'test message 1')
        self.assertEqual(response.meta['msg_id'], 'msg_1')

# ################################################################################################################################

    def test_on_messages_get_returns_error_when_no_subscription(self):
        """ on_messages_get returns error when user has no subscription.
        """
        # Clear subscriptions for consistent error
        self.rest_server.backend.subs_by_topic.clear()

        # Create request
        environ = self._create_environ({'max_messages': 1})

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify error response
        self.assertIsInstance(response, UnauthorizedResponse)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.details, 'No subscription found for user')

# ################################################################################################################################

    def test_on_messages_get_returns_error_when_rabbitmq_fails(self):
        """ on_messages_get returns error when RabbitMQ request fails.
        """
        # Set up permissions for test_user
        self.rest_server.backend.pattern_matcher.add_client('test_user', [
            {'pattern': self.test_topic, 'access_type': 'subscriber'}
        ])

        # Mock _fetch_from_rabbitmq to return None (simulating RabbitMQ failure)
        def mock_fetch_from_rabbitmq(cid, api_url, payload):
            return None

        self.rest_server._fetch_from_rabbitmq = mock_fetch_from_rabbitmq

        # Create request
        environ = self._create_environ({'max_messages': 1})

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify error response (line 25 in on_messages_get)
        self.assertIsInstance(response, BadRequestResponse)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.details, 'Subscription not found')

# ################################################################################################################################

    def test_on_messages_get_handles_empty_message_list(self):
        """ on_messages_get handles empty message list from RabbitMQ.
        """
        # Set up permissions for test_user
        self.rest_server.backend.pattern_matcher.add_client('test_user', [
            {'pattern': self.test_topic, 'access_type': 'subscriber'}
        ])

        # Mock _fetch_from_rabbitmq to return empty list
        def mock_fetch_from_rabbitmq(cid, api_url, payload):
            return []

        self.rest_server._fetch_from_rabbitmq = mock_fetch_from_rabbitmq

        # Create request
        environ = self._create_environ({'max_messages': 1})

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify success response with empty message list
        self.assertTrue(response.is_ok)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.messages, [])
        self.assertEqual(response.message_count, 0)

# ################################################################################################################################

    def test_on_messages_get_uses_default_params_when_not_provided(self):
        """ on_messages_get uses default parameters when not provided in request.
        """
        # Clear subscriptions for consistent error
        self.rest_server.backend.subs_by_topic.clear()

        # Create request without max_messages or max_len
        environ = self._create_environ({})

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify error response
        self.assertIsInstance(response, UnauthorizedResponse)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.details, 'No subscription found for user')

# ################################################################################################################################

    def test_on_messages_get_passes_custom_params_to_rabbitmq(self):
        """ on_messages_get passes custom parameters to RabbitMQ request.
        """
        # Clear subscriptions for consistent error
        self.rest_server.backend.subs_by_topic.clear()

        # Create request with custom parameters
        custom_max_messages = 10
        custom_max_len = 2000
        environ = self._create_environ({
            'max_messages': custom_max_messages,
            'max_len': custom_max_len
        })

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify error response
        self.assertIsInstance(response, UnauthorizedResponse)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.details, 'No subscription found for user')

# ################################################################################################################################

    def test_on_messages_get_builds_correct_rabbitmq_url(self):
        """ on_messages_get builds correct RabbitMQ API URL with subscription key.
        """
        # Clear subscriptions for consistent error
        self.rest_server.backend.subs_by_topic.clear()

        # Create request
        environ = self._create_environ({'max_messages': 1})

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify error response
        self.assertIsInstance(response, UnauthorizedResponse)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.details, 'No subscription found for user')

# ################################################################################################################################

    def test_on_messages_get_handles_exception_during_processing(self):
        """ on_messages_get handles exceptions during message processing.
        """
        # Set up permissions for test_user
        self.rest_server.backend.pattern_matcher.add_client('test_user', [
            {'pattern': self.test_topic, 'access_type': 'subscriber'}
        ])

        # Mock _fetch_from_rabbitmq to raise an exception
        def mock_fetch_from_rabbitmq(cid, api_url, payload):
            raise Exception('Simulated RabbitMQ connection error')

        self.rest_server._fetch_from_rabbitmq = mock_fetch_from_rabbitmq

        # Create request
        environ = self._create_environ({'max_messages': 1})

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify error response (line 34-35 in on_messages_get)
        self.assertIsInstance(response, BadRequestResponse)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.details, 'Internal error retrieving messages')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
