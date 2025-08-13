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
from base64 import b64encode
from json import dumps
from io import BytesIO

# Zato
from zato.common.pubsub.backend.rest_backend import RESTBackend
from zato.common.pubsub.server.rest import PubSubRESTServer
from zato.common.pubsub.models import APIResponse
from zato.broker.client import BrokerClient

# ################################################################################################################################
# ################################################################################################################################

class RESTOnPublishBasicTestCase(TestCase):

    def setUp(self):

        # Suppress ResourceWarnings from gevent
        warnings.filterwarnings('ignore', category=ResourceWarning)

        self.broker_client = BrokerClient()
        self.rest_server = PubSubRESTServer('localhost', 8080, should_init_broker_client=False)
        self.rest_server.backend = RESTBackend(self.rest_server, self.broker_client)

        # Test data constants
        self.test_cid = 'test-cid-123'
        self.test_username = 'test_user'
        self.test_password = 'secure_password_123'
        self.test_topic = 'test.topic'

        # Add test user to server
        self.rest_server.users[self.test_username] = {'sec_name': 'test_sec_def', 'password': self.test_password}

        # Add permissions for test user
        self.rest_server.backend.pattern_matcher.add_client(self.test_username, [
            {'pattern': 'test.*', 'access_type': 'publisher'}
        ])

# ################################################################################################################################

    def _create_basic_auth_header(self, username, password):
        credentials = f'{username}:{password}'
        encoded = b64encode(credentials.encode('utf-8')).decode('ascii')
        return f'Basic {encoded}'

    def _create_environ(self, auth_header, data=None):
        json_data = dumps(data) if data else '{}'
        environ = {
            'HTTP_AUTHORIZATION': auth_header,
            'wsgi.input': BytesIO(json_data.encode('utf-8')),
            'CONTENT_LENGTH': str(len(json_data)),
            'PATH_INFO': '/api/v1/pubsub/publish'
        }
        return environ

    def _create_start_response(self):
        def start_response(status, headers):
            pass
        return start_response

# ################################################################################################################################

    def test_on_publish_with_valid_data(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message data
        message_data = {
            'data': 'Hello, World!',
            'priority': 5,
            'expiration': 3600,
            'correl_id': 'test-correlation-123',
            'in_reply_to': 'test-reply-to'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert response is correct type and successful
        self.assertIsInstance(result, APIResponse)
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_minimal_data(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create minimal message data (only required 'data' field)
        message_data = {
            'data': 'Minimal message'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert response is correct type and successful
        self.assertIsInstance(result, APIResponse)
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_string_data(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message with string data
        message_data = {
            'data': 'Simple string message'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert response is correct type and successful
        self.assertIsInstance(result, APIResponse)
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_numeric_data(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message with numeric data
        message_data = {
            'data': 42
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert response is correct type and successful
        self.assertIsInstance(result, APIResponse)
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_boolean_data(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message with boolean data
        message_data = {
            'data': True
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Assert response is correct type and successful
        self.assertIsInstance(result, APIResponse)
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
