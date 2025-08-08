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
from zato.common.pubsub.models import BadRequestResponse, Subscription
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

class RESTOnMessagesGetErrorHandlingTestCase(TestCase):

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

        self.rest_server.backend.subs_by_topic = {
            self.test_topic: {
                self.test_username: subscription
            }
        }

    def _create_environ(self, json_data):
        """ Helper to create WSGI environ with JSON data.
        """
        import json
        json_str = json.dumps(json_data)
        return {
            'REQUEST_METHOD': 'GET',
            'CONTENT_TYPE': 'application/json',
            'CONTENT_LENGTH': str(len(json_str)),
            'wsgi.input': type('MockInput', (), {'read': lambda self, size=-1: json_str.encode('utf-8')})()
        }

# ################################################################################################################################

    def test_on_messages_get_handles_json_parsing_error(self):
        """ on_messages_get handles JSON parsing errors gracefully.
        """
        # Create request with invalid JSON
        environ = {
            'REQUEST_METHOD': 'GET',
            'CONTENT_TYPE': 'application/json',
            'CONTENT_LENGTH': '10',
            'wsgi.input': type('MockInput', (), {'read': lambda self, size=-1: b'invalid json'})(),
            'HTTP_AUTHORIZATION': 'Basic dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ='
        }

        # Set up users for authentication
        self.rest_server.users = {'test_user': 'test_password'}

        # Call method and expect exception to be handled
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify error response
        self.assertIsInstance(response, BadRequestResponse)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.details, 'Internal error retrieving messages')

# ################################################################################################################################

    def test_on_messages_get_handles_parameter_validation_error(self):
        """ on_messages_get handles parameter validation errors gracefully.
        """
        # Set up users for authentication
        self.rest_server.users = {'test_user': 'test_password'}

        # Create request with invalid parameters
        environ = self._create_environ({'max_messages': -1})
        environ['HTTP_AUTHORIZATION'] = 'Basic dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ='

        # Call method and expect exception to be handled
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify error response
        self.assertIsInstance(response, BadRequestResponse)
        self.assertEqual(response.cid, self.test_cid)

# ################################################################################################################################

    def test_on_messages_get_handles_no_subscription_found(self):
        """ on_messages_get handles case when no subscription is found for user.
        """
        # Set up users for authentication
        self.rest_server.users = {'test_user': 'test_password'}

        # Clear subscriptions so none will be found
        self.rest_server.backend.subs_by_topic.clear()

        # Create request
        environ = self._create_environ({'max_messages': 1})
        environ['HTTP_AUTHORIZATION'] = 'Basic dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ='

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify specific error response
        self.assertIsInstance(response, BadRequestResponse)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.details, 'No subscription found for user')

# ################################################################################################################################

    def test_on_messages_get_handles_rabbitmq_failure(self):
        """ on_messages_get handles RabbitMQ request failures gracefully.
        """
        # Set up users for authentication
        self.rest_server.users = {'test_user': 'test_password'}

        # Mock _fetch_from_rabbitmq to return None (failure)
        original_fetch = self.rest_server._fetch_from_rabbitmq
        self.rest_server._fetch_from_rabbitmq = lambda cid, api_url, payload: None

        # Create request
        environ = self._create_environ({'max_messages': 1})
        environ['HTTP_AUTHORIZATION'] = 'Basic dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ='

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Restore original method
        self.rest_server._fetch_from_rabbitmq = original_fetch

        # Verify specific error response
        self.assertIsInstance(response, BadRequestResponse)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.details, 'Failed to retrieve messages from queue')

# ################################################################################################################################

    def test_on_messages_get_handles_message_transformation_error(self):
        """ on_messages_get handles message transformation errors gracefully.
        """
        # Set up users for authentication
        self.rest_server.users = {'test_user': 'test_password'}

        # Mock _transform_messages to raise exception
        original_transform = self.rest_server._transform_messages
        self.rest_server._transform_messages = lambda messages_data: exec('raise RuntimeError("Test error")')

        # Mock _fetch_from_rabbitmq to return test data
        self.rest_server._fetch_from_rabbitmq = lambda cid, api_url, payload: [{'payload': 'test'}]

        # Create request
        environ = self._create_environ({'max_messages': 1})
        environ['HTTP_AUTHORIZATION'] = 'Basic dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ='

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Restore original method
        self.rest_server._transform_messages = original_transform

        # Verify error response
        self.assertIsInstance(response, BadRequestResponse)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.details, 'Internal error retrieving messages')

# ################################################################################################################################

    def test_on_messages_get_handles_specific_exceptions(self):
        """ on_messages_get handles specific exception types correctly.
        """
        # Set up users for authentication
        self.rest_server.users = {'test_user': 'test_password'}

        test_exceptions = [
            ValueError('Test ValueError'),
            RuntimeError('Test RuntimeError'),
            KeyError('Test KeyError'),
            TypeError('Test TypeError'),
        ]

        for exception in test_exceptions:
            with self.subTest(exception=type(exception).__name__):
                # Mock _transform_messages to raise specific exception
                original_transform = self.rest_server._transform_messages
                self.rest_server._transform_messages = lambda messages_data: exec(f'raise {type(exception).__name__}("{exception}")')

                # Mock _fetch_from_rabbitmq to return test data
                self.rest_server._fetch_from_rabbitmq = lambda cid, api_url, payload: [{'payload': 'test'}]

                # Create request
                environ = self._create_environ({'max_messages': 1})
                environ['HTTP_AUTHORIZATION'] = 'Basic dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ='

                # Call method
                response = self.rest_server.on_messages_get(self.test_cid, environ, None)

                # Restore original method
                self.rest_server._transform_messages = original_transform

                # Verify error response
                self.assertIsInstance(response, BadRequestResponse)
                self.assertEqual(response.cid, self.test_cid)
                self.assertEqual(response.details, 'Internal error retrieving messages')

# ################################################################################################################################

    def test_on_messages_get_error_response_consistency(self):
        """ on_messages_get returns consistent error responses across different failures.
        """
        # Set up users for authentication
        self.rest_server.users = {'test_user': 'test_password'}

        # Test different failure scenarios
        scenarios = [
            ('json_parse_fail', lambda: {
                'REQUEST_METHOD': 'GET',
                'CONTENT_TYPE': 'application/json',
                'CONTENT_LENGTH': '10',
                'wsgi.input': type('MockInput', (), {'read': lambda self, size=-1: b'invalid json'})(),
                'HTTP_AUTHORIZATION': 'Basic dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ='
            }),
            ('no_subscription', lambda: {
                **self._create_environ({'max_messages': 1}),
                'HTTP_AUTHORIZATION': 'Basic dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ='
            })
        ]

        for scenario_name, environ_func in scenarios:
            with self.subTest(scenario=scenario_name):
                if scenario_name == 'no_subscription':
                    self.rest_server.backend.subs_by_topic.clear()

                # Create request
                environ = environ_func()

                # Call method
                response = self.rest_server.on_messages_get(self.test_cid, environ, None)

                # Verify consistent error response structure
                self.assertIsInstance(response, BadRequestResponse)
                self.assertEqual(response.cid, self.test_cid)
                self.assertIsInstance(response.details, str)
                self.assertTrue(len(response.details) > 0)

                # Reset subscriptions
                if scenario_name == 'no_subscription':
                    subscription = Subscription()
                    subscription.topic_name = self.test_topic
                    subscription.sec_name = self.test_username
                    subscription.sub_key = self.test_sub_key
                    self.rest_server.backend.subs_by_topic = {
                        self.test_topic: {
                            self.test_username: subscription
                        }
                    }

# ################################################################################################################################

    def test_on_messages_get_preserves_cid_in_all_error_responses(self):
        """ on_messages_get preserves CID in all error response types.
        """
        # Set up users for authentication
        self.rest_server.users = {'test_user': 'test_password'}

        different_cids = ['cid-001', 'cid-002', 'error-cid-123', 'test-correlation-456']

        for cid in different_cids:
            with self.subTest(cid=cid):
                # Clear subscriptions for consistent error
                self.rest_server.backend.subs_by_topic.clear()

                # Create request
                environ = self._create_environ({'max_messages': 1})
                environ['HTTP_AUTHORIZATION'] = 'Basic dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ='

                # Call method with different CID
                response = self.rest_server.on_messages_get(cid, environ, None)

                # Verify CID is preserved
                self.assertIsInstance(response, BadRequestResponse)
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

# ################################################################################################################################

    def test_on_messages_get_handles_empty_subscription_data(self):
        """ on_messages_get handles empty subscription data gracefully.
        """
        # Set up users for authentication
        self.rest_server.users = {'test_user': 'test_password'}

        # Clear all subscriptions
        self.rest_server.backend.subs_by_topic.clear()

        # Create request
        environ = self._create_environ({'max_messages': 1})
        environ['HTTP_AUTHORIZATION'] = 'Basic dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ='

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify error response
        self.assertIsInstance(response, BadRequestResponse)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.details, 'No subscription found for user')

# ################################################################################################################################

    def test_on_messages_get_handles_malformed_subscription_data(self):
        """ on_messages_get handles malformed subscription data gracefully.
        """
        # Set up users for authentication
        self.rest_server.users = {'test_user': 'test_password'}

        # Set malformed subscription data
        self.rest_server.backend.subs_by_topic = {
            self.test_topic: {
                self.test_username: None  # Invalid subscription object
            }
        }

        # Create request
        environ = self._create_environ({'max_messages': 1})
        environ['HTTP_AUTHORIZATION'] = 'Basic dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ='

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify error response (should handle gracefully)
        self.assertIsInstance(response, BadRequestResponse)
        self.assertEqual(response.cid, self.test_cid)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
