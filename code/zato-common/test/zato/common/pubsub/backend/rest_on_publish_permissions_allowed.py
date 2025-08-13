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

# ################################################################################################################################
# ################################################################################################################################

class TestBrokerClient:
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

class RESTOnPublishPermissionsAllowedTestCase(TestCase):

    def setUp(self):

        # Suppress ResourceWarnings from gevent
        warnings.filterwarnings('ignore', category=ResourceWarning)

        # Create a test broker client that captures publish calls
        self.broker_client = TestBrokerClient()
        self.rest_server = PubSubRESTServer('localhost', 8080, should_init_broker_client=False)
        self.rest_server.backend = RESTBackend(self.rest_server, self.broker_client) # type: ignore

        # Test data constants
        self.test_cid = 'test-cid-123'
        self.test_username = 'test_user'
        self.test_password = 'secure_password_123'

        # Add test user to server
        self.rest_server.users[self.test_username] = {"sec_name": "test_sec_def", "password": self.test_password}

# ################################################################################################################################

    def _create_basic_auth_header(self, username, password):
        credentials = f'{username}:{password}'
        encoded = b64encode(credentials.encode('utf-8')).decode('ascii')
        return f'Basic {encoded}'

    def _create_environ(self, auth_header, data=None, content_type='application/json'):
        json_data = dumps(data) if data else '{}'
        json_bytes = json_data.encode('utf-8')
        environ = {
            'HTTP_AUTHORIZATION': auth_header,
            'wsgi.input': BytesIO(json_bytes),
            'CONTENT_LENGTH': str(len(json_bytes)),
            'CONTENT_TYPE': content_type,
            'PATH_INFO': '/api/v1/pubsub/publish',
            'REQUEST_METHOD': 'POST'
        }
        return environ

    def _create_start_response(self):
        def start_response(status, headers):
            pass
        return start_response

    def _add_user_permissions(self, username, permissions):
        """ Add permissions for a user to the pattern matcher.
        """
        self.rest_server.backend.pattern_matcher.add_client(username, permissions)

# ################################################################################################################################

    def test_on_publish_with_exact_topic_match_permission(self):
        """ User with exact topic permission can publish to that topic.
        """

        # Add exact topic permission
        permissions = [{'pattern': 'orders.created', 'access_type': 'publisher'}]
        self._add_user_permissions(self.test_username, permissions)

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message data
        message_data = {'data': 'Test order created'}
        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Should succeed
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, 'orders.created')
        self.assertTrue(result.is_ok)

        # Verify topic was created in backend
        self.assertIn('orders.created', self.rest_server.backend.topics)

        # Verify broker client was called
        self.assertEqual(len(self.broker_client.published_messages), 1)
        self.assertEqual(self.broker_client.published_routing_keys[0], 'orders.created')

        # Verify message content
        published_msg = self.broker_client.published_messages[0]
        self.assertEqual(published_msg['data'], 'Test order created')
        self.assertEqual(published_msg['topic_name'], 'orders.created')
        self.assertEqual(published_msg['publisher'], self.test_username)

# ################################################################################################################################

    def test_on_publish_with_single_wildcard_permission(self):
        """ User with single wildcard permission can publish to matching topics.
        """

        # Add single wildcard permission
        permissions = [{'pattern': 'orders.*', 'access_type': 'publisher'}]
        self._add_user_permissions(self.test_username, permissions)

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message data
        message_data = {'data': 'Test order updated'}
        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Should succeed for orders.updated
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, 'orders.updated')
        self.assertTrue(result.is_ok)

        # Verify first topic was created
        self.assertIn('orders.updated', self.rest_server.backend.topics)

        # Create fresh environ for second call
        environ2 = self._create_environ(auth_header, data=message_data)

        # Should succeed for orders.deleted
        result = self.rest_server.on_publish(self.test_cid, environ2, start_response, 'orders.deleted')
        self.assertTrue(result.is_ok)

        # Verify second topic was created
        self.assertIn('orders.deleted', self.rest_server.backend.topics)

        # Verify both broker calls were made
        self.assertEqual(len(self.broker_client.published_messages), 2)
        self.assertEqual(self.broker_client.published_routing_keys[0], 'orders.updated')
        self.assertEqual(self.broker_client.published_routing_keys[1], 'orders.deleted')

# ################################################################################################################################

    def test_on_publish_with_multi_level_wildcard_permission(self):
        """ User with multi-level wildcard permission can publish to deeply nested topics.
        """

        # Add multi-level wildcard permission
        permissions = [{'pattern': 'orders.**', 'access_type': 'publisher'}]
        self._add_user_permissions(self.test_username, permissions)

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message data
        message_data = {'data': 'Test deep order event'}
        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Should succeed for deeply nested topic
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, 'orders.region.us.created')
        self.assertTrue(result.is_ok)

        # Verify first topic was created
        self.assertIn('orders.region.us.created', self.rest_server.backend.topics)

        # Create fresh environ for second call
        environ2 = self._create_environ(auth_header, data=message_data)

        # Should succeed for another deep topic
        result = self.rest_server.on_publish(self.test_cid, environ2, start_response, 'orders.department.sales.updated')
        self.assertTrue(result.is_ok)

        # Verify second topic was created
        self.assertIn('orders.department.sales.updated', self.rest_server.backend.topics)

        # Verify both broker calls were made
        self.assertEqual(len(self.broker_client.published_messages), 2)

# ################################################################################################################################

    def test_on_publish_with_complex_wildcard_pattern(self):
        """ User with complex wildcard pattern can publish to matching topics.
        """

        # Add complex wildcard permission
        permissions = [{'pattern': 'department.*.events.**', 'access_type': 'publisher'}]
        self._add_user_permissions(self.test_username, permissions)

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message data
        message_data = {'data': 'Test department event'}
        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Should succeed for matching pattern
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, 'department.sales.events.created')
        self.assertTrue(result.is_ok)

        # Verify first topic was created
        self.assertIn('department.sales.events.created', self.rest_server.backend.topics)

        # Create fresh environ for second call
        environ2 = self._create_environ(auth_header, data=message_data)

        # Should succeed for another matching pattern
        result = self.rest_server.on_publish(self.test_cid, environ2, start_response, 'department.hr.events.user.updated')
        self.assertTrue(result.is_ok)

        # Verify second topic was created
        self.assertIn('department.hr.events.user.updated', self.rest_server.backend.topics)

        # Verify both broker calls were made
        self.assertEqual(len(self.broker_client.published_messages), 2)

# ################################################################################################################################

    def test_on_publish_with_both_pub_sub_permissions(self):
        """ User with both pub and sub permissions can publish.
        """

        # Add both pub and sub permissions
        permissions = [{'pattern': 'notifications.*', 'access_type': 'publisher-subscriber'}]
        self._add_user_permissions(self.test_username, permissions)

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message data
        message_data = {'data': 'Test notification'}
        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Should succeed
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, 'notifications.email')
        self.assertTrue(result.is_ok)

        # Verify topic creation and broker call
        self.assertIn('notifications.email', self.rest_server.backend.topics)
        self.assertEqual(len(self.broker_client.published_messages), 1)

# ################################################################################################################################

    def test_on_publish_with_exact_pattern_overrides_wildcard(self):
        """ Exact pattern permission overrides wildcard when both exist.
        """

        # Add both wildcard (deny) and exact (allow) permissions
        permissions = [
            {'pattern': 'orders.*', 'access_type': 'subscriber'},  # Only subscribe
            {'pattern': 'orders.created', 'access_type': 'publisher'}  # Can publish to this exact topic
        ]
        self._add_user_permissions(self.test_username, permissions)

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message data
        message_data = {'data': 'Test order created'}
        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Should succeed for exact match despite wildcard being sub-only
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, 'orders.created')
        self.assertTrue(result.is_ok)

        # Verify topic creation and broker call
        self.assertIn('orders.created', self.rest_server.backend.topics)
        self.assertEqual(len(self.broker_client.published_messages), 1)

# ################################################################################################################################

    def test_on_publish_with_multiple_overlapping_patterns(self):
        """ User with multiple overlapping patterns can publish when any allows.
        """

        # Add multiple overlapping permissions
        permissions = [
            {'pattern': 'events.*', 'access_type': 'publisher'},
            {'pattern': 'events.user.**', 'access_type': 'publisher'},
            {'pattern': 'events.user.created', 'access_type': 'publisher'}
        ]
        self._add_user_permissions(self.test_username, permissions)

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message data
        message_data = {'data': 'Test user event'}
        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Should succeed - multiple patterns allow this
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, 'events.user.created')
        self.assertTrue(result.is_ok)

        # Verify topic creation and broker call
        self.assertIn('events.user.created', self.rest_server.backend.topics)
        self.assertEqual(len(self.broker_client.published_messages), 1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
