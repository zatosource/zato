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
from zato.common.pubsub.server.rest_base import UnauthorizedException, BadRequestException

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

class RESTOnPublishPermissionsIntegrationTestCase(TestCase):

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

    def test_valid_auth_and_valid_permissions_succeeds(self):
        """ Valid authentication + valid permissions = successful publish.
        """

        # Add valid permissions
        permissions = [{'pattern': 'orders.*', 'access_type': 'publisher'}]
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
        self.assertEqual(result.cid, self.test_cid)

        # Verify topic creation and broker call
        self.assertIn('orders.created', self.rest_server.backend.topics)
        self.assertEqual(len(self.broker_client.published_messages), 1)
        self.assertEqual(len(self.broker_client.published_exchanges), 1)
        self.assertEqual(len(self.broker_client.published_routing_keys), 1)

        published_exchange = self.broker_client.published_exchanges[0] if self.broker_client.published_exchanges else None
        published_routing_key = self.broker_client.published_routing_keys[0] if self.broker_client.published_routing_keys else None

        exchange_msg = f'Expected exchange pubsubapi, got {published_exchange}. All: {self.broker_client.published_exchanges}'
        routing_key_msg = f'Expected routing key orders.created, got {published_routing_key}. All: {self.broker_client.published_routing_keys}'

        self.assertEqual(published_exchange, 'pubsubapi', exchange_msg)
        self.assertEqual(published_routing_key, 'orders.created', routing_key_msg)

# ################################################################################################################################

    def test_valid_auth_and_invalid_permissions_fails_with_permission_error(self):
        """ Valid authentication + invalid permissions = permission denied.
        """

        # Add permissions for different topic
        permissions = [{'pattern': 'inventory.*', 'access_type': 'publisher'}]
        self._add_user_permissions(self.test_username, permissions)

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message data
        message_data = {'data': 'Test order created'}
        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Should fail with permission error (not auth error)
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, 'orders.created')

        self.assertEqual(cm.exception.cid, self.test_cid)

        # Verify no messages were published due to authorization failure
        self.assertEqual(len(self.broker_client.published_messages), 0)
        self.assertEqual(len(self.broker_client.published_exchanges), 0)
        self.assertEqual(len(self.broker_client.published_routing_keys), 0)

# ################################################################################################################################

    def test_invalid_auth_fails_with_authentication_error(self):
        """ Invalid authentication = authentication error (not permission error).
        """

        # Add valid permissions for user
        permissions = [{'pattern': 'orders.*', 'access_type': 'publisher'}]
        self._add_user_permissions(self.test_username, permissions)

        # Create invalid auth header (wrong password)
        auth_header = self._create_basic_auth_header(self.test_username, 'wrong_password')

        # Create message data
        message_data = {'data': 'Test order created'}
        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Should fail with auth error before checking permissions
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, 'orders.created')

        self.assertEqual(cm.exception.cid, self.test_cid)

        # Verify no messages were published due to authentication failure
        self.assertEqual(len(self.broker_client.published_messages), 0)
        self.assertEqual(len(self.broker_client.published_exchanges), 0)
        self.assertEqual(len(self.broker_client.published_routing_keys), 0)

# ################################################################################################################################

    def test_invalid_auth_and_invalid_permissions_fails_with_authentication_error(self):
        """ Invalid auth + invalid permissions = authentication error (auth checked first).
        """

        # Add permissions for different topic
        permissions = [{'pattern': 'inventory.*', 'access_type': 'publisher'}]
        self._add_user_permissions(self.test_username, permissions)

        # Create invalid auth header
        auth_header = self._create_basic_auth_header('wrong_user', 'wrong_password')

        # Create message data
        message_data = {'data': 'Test order created'}
        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Should fail with auth error (auth is checked before permissions)
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, 'orders.created')

        self.assertEqual(cm.exception.cid, self.test_cid)

        # Verify no messages were published due to authentication failure
        self.assertEqual(len(self.broker_client.published_messages), 0)
        self.assertEqual(len(self.broker_client.published_exchanges), 0)
        self.assertEqual(len(self.broker_client.published_routing_keys), 0)

# ################################################################################################################################

    def test_valid_auth_valid_permissions_invalid_data_fails_with_validation_error(self):
        """ Valid auth + valid permissions + invalid data = validation error.
        """

        # Add valid permissions
        permissions = [{'pattern': 'orders.*', 'access_type': 'publisher'}]
        self._add_user_permissions(self.test_username, permissions)

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create invalid message data (missing 'data' field)
        message_data = {'priority': 5}  # No 'data' field
        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Should fail with validation error (not auth or permission error)
        with self.assertRaises(BadRequestException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, 'orders.created')

        self.assertEqual(cm.exception.cid, self.test_cid)
        self.assertIn('missing', cm.exception.message.lower())

        # Verify no messages were published due to validation failure
        self.assertEqual(len(self.broker_client.published_messages), 0)
        self.assertEqual(len(self.broker_client.published_exchanges), 0)
        self.assertEqual(len(self.broker_client.published_routing_keys), 0)

# ################################################################################################################################

    def test_no_auth_header_fails_immediately(self):
        """ Missing auth header fails before permission check.
        """

        # Add valid permissions
        permissions = [{'pattern': 'orders.*', 'access_type': 'publisher'}]
        self._add_user_permissions(self.test_username, permissions)

        # Create message data
        message_data = {'data': 'Test order created'}
        environ = self._create_environ(None, data=message_data)  # No auth header
        start_response = self._create_start_response()

        # Should fail with auth error
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, 'orders.created')

        self.assertEqual(cm.exception.cid, self.test_cid)

        # Verify no messages were published due to authentication failure
        self.assertEqual(len(self.broker_client.published_messages), 0)
        self.assertEqual(len(self.broker_client.published_exchanges), 0)
        self.assertEqual(len(self.broker_client.published_routing_keys), 0)

# ################################################################################################################################

    def test_multiple_users_with_different_permissions(self):
        """ Multiple users with different permissions work independently.
        """

        # Set up second user
        second_username = 'second_user'
        second_password = 'second_password'
        self.rest_server.users[second_username] = {"sec_name": "test_sec_def", "password": second_password}

        # Give first user orders permissions
        permissions1 = [{'pattern': 'orders.*', 'access_type': 'publisher'}]
        self._add_user_permissions(self.test_username, permissions1)

        # Give second user inventory permissions
        permissions2 = [{'pattern': 'inventory.*', 'access_type': 'publisher'}]
        self._add_user_permissions(second_username, permissions2)

        # Create message data
        message_data = {'data': 'Test message'}

        # First user can publish to orders
        auth_header1 = self._create_basic_auth_header(self.test_username, self.test_password)
        environ1 = self._create_environ(auth_header1, data=message_data)
        start_response = self._create_start_response()

        result1 = self.rest_server.on_publish(self.test_cid, environ1, start_response, 'orders.created')
        self.assertTrue(result1.is_ok)

        # Second user can publish to inventory
        auth_header2 = self._create_basic_auth_header(second_username, second_password)
        environ2 = self._create_environ(auth_header2, data=message_data)

        result2 = self.rest_server.on_publish(self.test_cid, environ2, start_response, 'inventory.updated')
        self.assertTrue(result2.is_ok)

        # Verify both successful publishes were recorded
        self.assertEqual(len(self.broker_client.published_messages), 2)
        self.assertEqual(len(self.broker_client.published_exchanges), 2)
        self.assertEqual(len(self.broker_client.published_routing_keys), 2)

        first_exchange = self.broker_client.published_exchanges[0] if len(self.broker_client.published_exchanges) > 0 else None
        second_exchange = self.broker_client.published_exchanges[1] if len(self.broker_client.published_exchanges) > 1 else None
        first_routing_key = self.broker_client.published_routing_keys[0] if len(self.broker_client.published_routing_keys) > 0 else None
        second_routing_key = self.broker_client.published_routing_keys[1] if len(self.broker_client.published_routing_keys) > 1 else None

        first_exchange_msg = f'Expected first exchange pubsubapi, got {first_exchange}. All: {self.broker_client.published_exchanges}'
        second_exchange_msg = f'Expected second exchange pubsubapi, got {second_exchange}. All: {self.broker_client.published_exchanges}'
        first_routing_msg = f'Expected first routing key orders.created, got {first_routing_key}. All: {self.broker_client.published_routing_keys}'
        second_routing_msg = f'Expected second routing key inventory.updated, got {second_routing_key}. All: {self.broker_client.published_routing_keys}'

        self.assertEqual(first_exchange, 'pubsubapi', first_exchange_msg)
        self.assertEqual(second_exchange, 'pubsubapi', second_exchange_msg)
        self.assertEqual(first_routing_key, 'orders.created', first_routing_msg)
        self.assertEqual(second_routing_key, 'inventory.updated', second_routing_msg)

        # First user cannot publish to inventory
        with self.assertRaises(UnauthorizedException):
            _ = self.rest_server.on_publish(self.test_cid, environ1, start_response, 'inventory.updated')

        # Second user cannot publish to orders
        with self.assertRaises(UnauthorizedException):
            _ = self.rest_server.on_publish(self.test_cid, environ2, start_response, 'orders.created')

        # Verify no additional messages were published due to authorization failures
        self.assertEqual(len(self.broker_client.published_messages), 2)
        self.assertEqual(len(self.broker_client.published_exchanges), 2)
        self.assertEqual(len(self.broker_client.published_routing_keys), 2)

# ################################################################################################################################

    def test_permission_check_happens_after_successful_authentication(self):
        """ Permissions are only checked after successful authentication.
        """

        # Don't add any permissions for user

        # Create valid auth header
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message data
        message_data = {'data': 'Test message'}
        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Should fail with permission error (proving auth succeeded first)
        with self.assertRaises(UnauthorizedException) as cm:
            _ = self.rest_server.on_publish(self.test_cid, environ, start_response, 'any.topic')

        self.assertEqual(cm.exception.cid, self.test_cid)

        # Verify no messages were published due to permission failure
        self.assertEqual(len(self.broker_client.published_messages), 0)
        self.assertEqual(len(self.broker_client.published_exchanges), 0)
        self.assertEqual(len(self.broker_client.published_routing_keys), 0)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
