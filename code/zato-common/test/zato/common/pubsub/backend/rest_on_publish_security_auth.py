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
from zato.common.pubsub.server.rest_publish import PubSubRESTServerPublish
from zato.common.pubsub.server.rest_base import UnauthorizedException
from zato.broker.client import BrokerClient

# ################################################################################################################################
# ################################################################################################################################

class RESTOnPublishSecurityAuthTestCase(TestCase):

    def setUp(self):

        # Suppress ResourceWarnings from gevent
        warnings.filterwarnings('ignore', category=ResourceWarning)

        self.broker_client = BrokerClient()
        self.rest_server = PubSubRESTServerPublish('localhost', 8080, should_init_broker_client=False)
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

    def _create_environ(self, auth_header=None, data=None):
        json_data = dumps(data) if data else '{}'
        environ = {
            'wsgi.input': BytesIO(json_data.encode('utf-8')),
            'CONTENT_LENGTH': str(len(json_data)),
            'PATH_INFO': '/api/v1/pubsub/publish'
        }
        if auth_header:
            environ['HTTP_AUTHORIZATION'] = auth_header
        return environ

    def _create_start_response(self):
        def start_response(status, headers):
            pass
        return start_response

# ################################################################################################################################

    def test_on_publish_with_missing_authorization_header(self):

        # Create message data
        message_data = {
            'data': 'Test message'
        }

        # Create environ without authorization header
        environ = self._create_environ(data=message_data)
        start_response = self._create_start_response()

        # Call the method under test and expect UnauthorizedException
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        self.assertEqual(cm.exception.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_invalid_username(self):

        # Create auth header with invalid username
        auth_header = self._create_basic_auth_header('invalid_user', self.test_password)

        # Create message data
        message_data = {
            'data': 'Test message'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test and expect UnauthorizedException
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        self.assertEqual(cm.exception.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_invalid_password(self):

        # Create auth header with invalid password
        auth_header = self._create_basic_auth_header(self.test_username, 'wrong_password')

        # Create message data
        message_data = {
            'data': 'Test message'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test and expect UnauthorizedException
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        self.assertEqual(cm.exception.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_empty_username(self):

        # Create auth header with empty username
        auth_header = self._create_basic_auth_header('', self.test_password)

        # Create message data
        message_data = {
            'data': 'Test message'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test and expect UnauthorizedException
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        self.assertEqual(cm.exception.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_empty_password(self):

        # Create auth header with empty password
        auth_header = self._create_basic_auth_header(self.test_username, '')

        # Create message data
        message_data = {
            'data': 'Test message'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test and expect UnauthorizedException
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        self.assertEqual(cm.exception.cid, self.test_cid)

# ################################################################################################################################



    def test_on_publish_with_case_sensitive_username(self):

        # Create auth header with different case username
        auth_header = self._create_basic_auth_header(self.test_username.upper(), self.test_password)

        # Create message data
        message_data = {
            'data': 'Test message'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test and expect UnauthorizedException
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)

        self.assertEqual(cm.exception.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_unicode_credentials(self):

        # Add Greek Unicode user to server
        unicode_username = 'χρήστης_δοκιμής'
        unicode_password = 'κωδικός_123'
        self.rest_server.users[unicode_username] = {"sec_name": "test_sec_def", "password": unicode_password}

        # Add permissions for test user and unicode user
        self.rest_server.backend.pattern_matcher.add_client(self.test_username, [
            {'pattern': 'test.*', 'access_type': 'publisher'}
        ])
        self.rest_server.backend.pattern_matcher.add_client(unicode_username, [
            {'pattern': 'test.*', 'access_type': 'publisher'}
        ])

        # Create auth header with Unicode credentials
        auth_header = self._create_basic_auth_header(unicode_username, unicode_password)

        # Create message data
        message_data = {
            'data': 'Test message with Unicode auth'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # This should work with valid Unicode credentials
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, self.test_topic)
        self.assertTrue(result.is_ok)

        # Now test with wrong Unicode password
        wrong_auth_header = self._create_basic_auth_header(unicode_username, 'λάθος_κωδικός')
        environ_wrong = self._create_environ(wrong_auth_header, data=message_data)

        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ_wrong, start_response, self.test_topic)

        self.assertEqual(cm.exception.cid, self.test_cid)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
