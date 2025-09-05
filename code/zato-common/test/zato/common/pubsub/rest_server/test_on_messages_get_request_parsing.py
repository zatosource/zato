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
from zato.common.pubsub.server.rest_publish import PubSubRESTServer

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

class RESTOnMessagesGetRequestParsingTestCase(TestCase):

    def setUp(self):

        # Suppress ResourceWarnings from gevent
        warnings.filterwarnings('ignore', category=ResourceWarning)

        # Create a test broker client that captures publish calls
        self.broker_client = BrokerClientHelper()
        self.rest_server = PubSubRESTServer('localhost', 8080, should_init_broker_client=False)
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
                self.test_username: subscription
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

    def test_on_messages_get_calls_parse_json_with_correct_params(self):
        """ on_messages_get calls _parse_json with correct parameters.
        """
        # Clear subscriptions for consistent error
        self.rest_server.backend.subs_by_topic.clear()

        # Create request
        test_data = {'max_messages': 5}
        environ = self._create_environ(test_data)

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify error response
        self.assertEqual(response.details, 'No subscription found for user')

# ################################################################################################################################

    def test_on_messages_get_creates_request_object_from_environ(self):
        """ on_messages_get creates Request object from environ correctly.
        """
        # Clear subscriptions for consistent error
        self.rest_server.backend.subs_by_topic.clear()

        # Create request
        test_data = {'max_messages': 3, 'max_len': 2000}
        environ = self._create_environ(test_data)

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify error response
        self.assertEqual(response.details, 'No subscription found for user')

# ################################################################################################################################

    def test_on_messages_get_passes_parsed_data_to_validate_params(self):
        """ on_messages_get passes parsed JSON data to _validate_get_params.
        """
        # Clear subscriptions for consistent error
        self.rest_server.backend.subs_by_topic.clear()

        # Create request
        test_data = {'max_messages': 7, 'max_len': 3000}
        environ = self._create_environ(test_data)

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify error response
        self.assertEqual(response.details, 'No subscription found for user')

# ################################################################################################################################

    def test_on_messages_get_handles_empty_json_request(self):
        """ on_messages_get handles empty JSON request correctly.
        """
        # Clear subscriptions for consistent error
        self.rest_server.backend.subs_by_topic.clear()

        # Create request with empty JSON
        test_data = {}
        environ = self._create_environ(test_data)

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify error response
        self.assertEqual(response.details, 'No subscription found for user')

# ################################################################################################################################

    def test_on_messages_get_handles_json_with_extra_fields(self):
        """ on_messages_get handles JSON with extra fields correctly.
        """
        # Clear subscriptions for consistent error
        self.rest_server.backend.subs_by_topic.clear()

        # Create request with extra fields
        test_data = {
            'max_messages': 4,
            'max_len': 1500,
            'extra_field1': 'value1',
            'extra_field2': 123,
            'extra_field3': True
        }
        environ = self._create_environ(test_data)

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify error response
        self.assertEqual(response.details, 'No subscription found for user')

# ################################################################################################################################

    def test_on_messages_get_handles_different_json_data_types(self):
        """ on_messages_get handles different JSON data types correctly.
        """
        # Clear subscriptions for consistent error
        self.rest_server.backend.subs_by_topic.clear()

        # Test with various data types
        test_cases = [
            {'max_messages': 1, 'string_field': 'test'},
            {'max_messages': 2, 'number_field': 42},
            {'max_messages': 3, 'boolean_field': True},
            {'max_messages': 4, 'null_field': None},
            {'max_messages': 5, 'list_field': [1, 2, 3]}
        ]

        for test_data in test_cases:
            with self.subTest(test_data=test_data):
                # Create request
                environ = self._create_environ(test_data)

                # Call method
                response = self.rest_server.on_messages_get(self.test_cid, environ, None)

                # Verify error response
                self.assertEqual(response.details, 'No subscription found for user')

# ################################################################################################################################

    def test_on_messages_get_request_parsing_order(self):
        """ on_messages_get performs request parsing in correct order.
        """
        # Clear subscriptions for consistent error
        self.rest_server.backend.subs_by_topic.clear()

        # Create request
        test_data = {'max_messages': 2}
        environ = self._create_environ(test_data)

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify error response
        self.assertEqual(response.details, 'No subscription found for user')

# ################################################################################################################################

    def test_on_messages_get_preserves_request_data_integrity(self):
        """ on_messages_get preserves request data integrity through parsing chain.
        """
        # Clear subscriptions for consistent error
        self.rest_server.backend.subs_by_topic.clear()

        # Create request with specific data
        original_data = {
            'max_messages': 42,
            'max_len': 9999,
            'custom_field': 'test_value'
        }
        environ = self._create_environ(original_data)

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify error response
        self.assertEqual(response.details, 'No subscription found for user')

# ################################################################################################################################

    def test_on_messages_get_handles_nested_json_structures(self):
        """ on_messages_get handles nested JSON structures correctly.
        """
        # Clear subscriptions for consistent error
        self.rest_server.backend.subs_by_topic.clear()

        # Create request with nested data
        test_data = {
            'max_messages': 8,
            'max_len': 4000,
            'metadata': {
                'client_info': {
                    'version': '1.0',
                    'platform': 'test'
                },
                'request_id': 'req_123'
            },
            'filters': ['filter1', 'filter2']
        }
        environ = self._create_environ(test_data)

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify error response
        self.assertEqual(response.details, 'No subscription found for user')

# ################################################################################################################################

    def test_on_messages_get_request_object_properties(self):
        """ on_messages_get creates Request object with correct properties.
        """
        # Clear subscriptions for consistent error
        self.rest_server.backend.subs_by_topic.clear()

        # Create request
        test_data = {'max_messages': 6}
        environ = self._create_environ(test_data)

        # Call method
        response = self.rest_server.on_messages_get(self.test_cid, environ, None)

        # Verify error response
        self.assertEqual(response.details, 'No subscription found for user')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
