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

class RESTOnPublishPermissionsDeniedTestCase(TestCase):

    def setUp(self):

        # Suppress ResourceWarnings from gevent
        warnings.filterwarnings('ignore', category=ResourceWarning)

        # Create a test broker client that captures publish calls
        self.broker_client = TestBrokerClient()
        self.rest_server = PubSubRESTServerPublish('localhost', 8080, should_init_broker_client=False)
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

    def test_on_publish_with_no_matching_pattern(self):
        """ User with non-matching pattern cannot publish.
        """

        # Add permission for different topic
        permissions = [{'pattern': 'orders.*', 'access_type': 'publisher'}]
        self._add_user_permissions(self.test_username, permissions)

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message data
        message_data = {'data': 'Test inventory update'}
        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Should fail - no permission for inventory topics
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, 'inventory.updated')

        self.assertEqual(cm.exception.cid, self.test_cid)

        # Verify no messages were published due to authorization failure
        self.assertEqual(len(self.broker_client.published_messages), 0)
        self.assertEqual(len(self.broker_client.published_exchanges), 0)
        self.assertEqual(len(self.broker_client.published_routing_keys), 0)

# ################################################################################################################################

    def test_on_publish_with_subscribe_only_permission(self):
        """ User with subscribe-only permission cannot publish.
        """

        # Add subscribe-only permission
        permissions = [{'pattern': 'orders.*', 'access_type': 'subscriber'}]
        self._add_user_permissions(self.test_username, permissions)

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message data
        message_data = {'data': 'Test order created'}
        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Should fail - user has subscribe permission, not publish
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, 'orders.created')

        self.assertEqual(cm.exception.cid, self.test_cid)

        # Verify no messages were published due to authorization failure
        self.assertEqual(len(self.broker_client.published_messages), 0)
        self.assertEqual(len(self.broker_client.published_exchanges), 0)
        self.assertEqual(len(self.broker_client.published_routing_keys), 0)

# ################################################################################################################################

    def test_on_publish_with_no_permissions(self):
        """ User with no permissions cannot publish.
        """

        # Don't add any permissions for user

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message data
        message_data = {'data': 'Test message'}
        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Should fail - no permissions at all
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, 'any.topic')

        self.assertEqual(cm.exception.cid, self.test_cid)

        # Verify no messages were published due to authorization failure
        self.assertEqual(len(self.broker_client.published_messages), 0)
        self.assertEqual(len(self.broker_client.published_exchanges), 0)
        self.assertEqual(len(self.broker_client.published_routing_keys), 0)

# ################################################################################################################################

    def test_on_publish_with_wildcard_mismatch(self):
        """ User with wildcard pattern cannot publish to non-matching topic.
        """

        # Add wildcard permission for orders
        permissions = [{'pattern': 'orders.*', 'access_type': 'publisher'}]
        self._add_user_permissions(self.test_username, permissions)

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message data
        message_data = {'data': 'Test inventory update'}
        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Should fail - orders.* doesn't match inventory.updated
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, 'inventory.updated')

        self.assertEqual(cm.exception.cid, self.test_cid)

        # Verify no messages were published due to authorization failure
        self.assertEqual(len(self.broker_client.published_messages), 0)
        self.assertEqual(len(self.broker_client.published_exchanges), 0)
        self.assertEqual(len(self.broker_client.published_routing_keys), 0)

# ################################################################################################################################

    def test_on_publish_with_single_wildcard_depth_mismatch(self):
        """ User with single wildcard cannot publish to deeper nested topic.
        """

        # Add single wildcard permission
        permissions = [{'pattern': 'orders.*', 'access_type': 'publisher'}]
        self._add_user_permissions(self.test_username, permissions)

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message data
        message_data = {'data': 'Test deep order event'}
        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Should fail - orders.* doesn't match orders.region.us.created (single wildcard doesn't match multiple levels)
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, 'orders.region.us.created')

        self.assertEqual(cm.exception.cid, self.test_cid)

        # Verify no messages were published due to authorization failure
        self.assertEqual(len(self.broker_client.published_messages), 0)
        self.assertEqual(len(self.broker_client.published_exchanges), 0)
        self.assertEqual(len(self.broker_client.published_routing_keys), 0)

# ################################################################################################################################

    def test_on_publish_with_complex_pattern_mismatch(self):
        """ User with complex pattern cannot publish to non-matching topic.
        """

        # Add complex pattern permission
        permissions = [{'pattern': 'department.*.events.**', 'access_type': 'publisher'}]
        self._add_user_permissions(self.test_username, permissions)

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message data
        message_data = {'data': 'Test department alert'}
        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Should fail - department.*.events.** doesn't match department.sales.alerts.critical
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, 'department.sales.alerts.critical')

        self.assertEqual(cm.exception.cid, self.test_cid)

        # Verify no messages were published due to authorization failure
        self.assertEqual(len(self.broker_client.published_messages), 0)
        self.assertEqual(len(self.broker_client.published_exchanges), 0)
        self.assertEqual(len(self.broker_client.published_routing_keys), 0)

# ################################################################################################################################

    def test_on_publish_with_first_matching_pattern_wins(self):
        """ First matching pattern in list determines access.
        """

        # Add patterns where first match allows
        permissions = [
            {'pattern': 'orders.**', 'access_type': 'publisher'},  # Allow all orders (first)
            {'pattern': 'orders.sensitive', 'access_type': 'subscriber'}  # Would deny but comes second
        ]
        self._add_user_permissions(self.test_username, permissions)

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message data
        message_data = {'data': 'Sensitive order data'}
        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Should succeed - first pattern (orders.**) allows publishing
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, 'orders.sensitive')
        self.assertTrue(result.is_ok)

        # Verify topic creation and broker call
        self.assertIn('orders.sensitive', self.rest_server.backend.topics)
        self.assertEqual(len(self.broker_client.published_messages), 1)
        self.assertEqual(len(self.broker_client.published_exchanges), 1)
        self.assertEqual(len(self.broker_client.published_routing_keys), 1)
        self.assertEqual(self.broker_client.published_exchanges[0], 'pubsubapi')
        self.assertEqual(self.broker_client.published_routing_keys[0], 'orders.sensitive')

# ################################################################################################################################

    def test_on_publish_with_empty_permission_list(self):
        """ User with empty permission list cannot publish.
        """

        # Add empty permissions
        permissions = []
        self._add_user_permissions(self.test_username, permissions)

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message data
        message_data = {'data': 'Test message'}
        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Should fail - empty permissions
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, 'any.topic')

        self.assertEqual(cm.exception.cid, self.test_cid)

        # Verify no messages were published due to authorization failure
        self.assertEqual(len(self.broker_client.published_messages), 0)
        self.assertEqual(len(self.broker_client.published_exchanges), 0)
        self.assertEqual(len(self.broker_client.published_routing_keys), 0)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
