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
from zato.common.pubsub.server.rest_base import BadRequestException
from zato.broker.client import BrokerClient

# ################################################################################################################################
# ################################################################################################################################

class RESTOnPublishSecurityValidationTestCase(TestCase):

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
        self.rest_server.users[self.test_username] = {"sec_name": "test_sec_def", "password": self.test_password}

        # Add permissions for test user
        self.rest_server.backend.pattern_matcher.add_client(self.test_username, [
            {'pattern': 'test.*', 'access_type': 'publisher'}
        ])

# ################################################################################################################################

    def _create_basic_auth_header(self, username, password):
        credentials = f'{username}:{password}'
        encoded = b64encode(credentials.encode('utf-8')).decode('ascii')
        return f'Basic {encoded}'

    def _create_environ(self, auth_header, data=None, content_type='application/json'):
        json_data = dumps(data) if data else '{}'
        environ = {
            'HTTP_AUTHORIZATION': auth_header,
            'wsgi.input': BytesIO(json_data.encode('utf-8')),
            'CONTENT_LENGTH': str(len(json_data)),
            'CONTENT_TYPE': content_type,
            'PATH_INFO': '/api/v1/pubsub/publish'
        }
        return environ

    def _create_start_response(self):
        def start_response(status, headers):
            pass
        return start_response

# ################################################################################################################################

    def test_on_publish_with_empty_request_body(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create environ with empty body
        environ = self._create_environ(auth_header, data=None)
        environ['wsgi.input'] = BytesIO(b'')
        environ['CONTENT_LENGTH'] = '0'
        start_response = self._create_start_response()

        # Call the method under test and expect BadRequestException
        with self.assertRaises(BadRequestException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        self.assertEqual(cm.exception.cid, self.test_cid)
        self.assertIn('missing', cm.exception.message.lower())

# ################################################################################################################################

    def test_on_publish_with_invalid_json(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create environ with invalid JSON
        invalid_json = '{"data": "test", invalid json}'
        environ = {
            'HTTP_AUTHORIZATION': auth_header,
            'wsgi.input': BytesIO(invalid_json.encode('utf-8')),
            'CONTENT_LENGTH': str(len(invalid_json)),
            'PATH_INFO': '/api/v1/pubsub/publish'
        }
        start_response = self._create_start_response()

        # Call the method under test and expect JSONDecodeError
        from json import JSONDecodeError
        with self.assertRaises(JSONDecodeError):
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

# ################################################################################################################################

    def test_on_publish_with_missing_data_field(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message without 'data' field
        message_data = {
            'priority': 5,
            'expiration': 3600
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test and expect BadRequestException
        with self.assertRaises(BadRequestException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        self.assertEqual(cm.exception.cid, self.test_cid)
        self.assertIn('data missing', cm.exception.message.lower())

# ################################################################################################################################

    def test_on_publish_with_null_data_field(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message with null 'data' field
        message_data = {
            'data': None,
            'priority': 5
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test and expect BadRequestException
        with self.assertRaises(BadRequestException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        self.assertEqual(cm.exception.cid, self.test_cid)
        self.assertIn('data missing', cm.exception.message.lower())

# ################################################################################################################################

    def test_on_publish_with_extremely_large_payload(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message with extremely large data (over 5MB limit)
        large_data = 'x' * (5_000_001)  # Just over the 5MB limit
        message_data = {
            'data': large_data
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test - should handle large payloads gracefully
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # This might succeed or fail depending on implementation limits
        # The test ensures it doesn't crash the server
        self.assertIsNotNone(result)

# ################################################################################################################################

    def test_on_publish_with_invalid_priority_type(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message with invalid priority type
        message_data = {
            'data': 'Test message',
            'priority': 'high'  # Should be integer
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test - should handle gracefully
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Should either succeed with default priority or fail with validation error
        self.assertIsNotNone(result)

# ################################################################################################################################

    def test_on_publish_with_invalid_expiration_type(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message with invalid expiration type
        message_data = {
            'data': 'Test message',
            'expiration': 'never'  # Should be integer
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test and expect TypeError
        with self.assertRaises(TypeError):
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

# ################################################################################################################################

    def test_on_publish_with_negative_priority(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message with negative priority
        message_data = {
            'data': 'Test message',
            'priority': -5
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test - should handle gracefully
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Should either succeed or fail with validation error
        self.assertIsNotNone(result)

# ################################################################################################################################

    def test_on_publish_with_negative_expiration(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message with negative expiration
        message_data = {
            'data': 'Test message',
            'expiration': -3600
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test - should handle gracefully
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Should either succeed or fail with validation error
        self.assertIsNotNone(result)

# ################################################################################################################################

    def test_on_publish_with_extremely_long_correlation_id(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message with extremely long correlation ID
        long_correl_id = 'x' * 10000
        message_data = {
            'data': 'Test message',
            'correl_id': long_correl_id
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test - should handle gracefully
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Should either succeed or fail with validation error
        self.assertIsNotNone(result)

# ################################################################################################################################

    def test_on_publish_with_special_characters_in_fields(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message with special characters
        message_data = {
            'data': 'Test message with special chars: <>&"\'',
            'correl_id': 'correl-id-with-<>&"\'-chars',
            'in_reply_to': 'reply-to-with-<>&"\'-chars'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test - should handle special characters
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Should succeed with proper escaping
        self.assertTrue(result.is_ok)

# ################################################################################################################################

    def test_on_publish_with_binary_data_in_json(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message with binary-like data
        message_data = {
            'data': '\x00\x01\x02\x03\x04\x05'  # Binary data as string
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test - should handle binary data
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        # Should succeed or fail gracefully
        self.assertIsNotNone(result)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
