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
from zato.common.api import APIResponse
from zato.broker.client import BrokerClient

# ################################################################################################################################
# ################################################################################################################################

class RESTOnPublishTopicsTestCase(TestCase):

    def setUp(self):

        # Suppress ResourceWarnings from gevent
        warnings.filterwarnings('ignore', category=ResourceWarning)

        self.broker_client = BrokerClient()
        self.rest_server = PubSubRESTServer('localhost', 8080)
        self.rest_server.backend = RESTBackend(self.rest_server, self.broker_client)

        # Test data constants
        self.test_cid = 'test-cid-123'
        self.test_username = 'test_user'
        self.test_password = 'secure_password_123'

        # Add test user to server
        self.rest_server.users[self.test_username] = self.test_password

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
            'CONTENT_LENGTH': str(len(json_data))
        }
        return environ

    def _create_start_response(self):
        def start_response(status, headers):
            pass
        return start_response

# ################################################################################################################################

    def test_on_publish_creates_new_topic(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Use a new topic that doesn't exist
        new_topic = 'new.test.topic'

        # Create message
        message_data = {
            'data': 'Message for new topic'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, new_topic)

        # Assert response is correct type and successful
        self.assertIsInstance(result, APIResponse)
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_dotted_topic_name(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Use topic with multiple dots
        dotted_topic = 'system.events.user.login'

        # Create message
        message_data = {
            'data': 'Dotted topic message'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, dotted_topic)

        # Assert response is correct type and successful
        self.assertIsInstance(result, APIResponse)
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_underscored_topic_name(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Use topic with underscores
        underscored_topic = 'system_events_user_logout'

        # Create message
        message_data = {
            'data': 'Underscored topic message'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, underscored_topic)

        # Assert response is correct type and successful
        self.assertIsInstance(result, APIResponse)
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_hyphenated_topic_name(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Use topic with hyphens
        hyphenated_topic = 'system-events-user-action'

        # Create message
        message_data = {
            'data': 'Hyphenated topic message'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, hyphenated_topic)

        # Assert response is correct type and successful
        self.assertIsInstance(result, APIResponse)
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_numeric_topic_name(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Use topic with numbers
        numeric_topic = 'topic123.event456.data789'

        # Create message
        message_data = {
            'data': 'Numeric topic message'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, numeric_topic)

        # Assert response is correct type and successful
        self.assertIsInstance(result, APIResponse)
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_unicode_topic_name(self):

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Use topic with Unicode characters
        unicode_topic = 'συστημα.γεγονοτα.χρηστης'

        # Create message
        message_data = {
            'data': 'Unicode topic message'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Call the method under test
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, unicode_topic)

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
