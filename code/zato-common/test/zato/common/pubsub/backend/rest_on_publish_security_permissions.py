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
from zato.common.pubsub.models import BadRequestResponse
from zato.common.pubsub.matcher import PatternMatcher
from zato.broker.client import BrokerClient

# ################################################################################################################################
# ################################################################################################################################

class RESTOnPublishSecurityPermissionsTestCase(TestCase):

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
        self.restricted_username = 'restricted_user'
        self.restricted_password = 'restricted_pass_456'

        # Add test users to server
        self.rest_server.users[self.test_username] = self.test_password
        self.rest_server.users[self.restricted_username] = self.restricted_password

        # Set up pattern matcher with permissions
        self.pattern_matcher = PatternMatcher()
        
        # Give full permissions to test_user
        full_permissions = [
            {'pattern': '*', 'access_type': 'pub'},
            {'pattern': '*', 'access_type': 'sub'}
        ]
        self.pattern_matcher.add_client(self.test_username, full_permissions)
        
        # Give restricted permissions to restricted_user (only specific topics)
        restricted_permissions = [
            {'pattern': 'allowed.topic.*', 'access_type': 'pub'},
            {'pattern': 'public.*', 'access_type': 'pub'}
        ]
        self.pattern_matcher.add_client(self.restricted_username, restricted_permissions)
        
        # Replace the backend's pattern matcher
        self.rest_server.backend.pattern_matcher = self.pattern_matcher

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

    def test_on_publish_with_full_permissions_succeeds(self):

        # Create auth header for user with full permissions
        auth_header = self._create_basic_auth_header(self.test_username, self.test_password)

        # Create message data
        message_data = {
            'data': 'Test message for any topic'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Test publishing to any topic should work
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, 'any.topic.name')
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_restricted_permissions_allowed_topic(self):

        # Create auth header for restricted user
        auth_header = self._create_basic_auth_header(self.restricted_username, self.restricted_password)

        # Create message data
        message_data = {
            'data': 'Test message for allowed topic'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Test publishing to allowed topic should work
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, 'allowed.topic.test')
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_restricted_permissions_public_topic(self):

        # Create auth header for restricted user
        auth_header = self._create_basic_auth_header(self.restricted_username, self.restricted_password)

        # Create message data
        message_data = {
            'data': 'Test message for public topic'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Test publishing to public topic should work
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, 'public.announcements')
        self.assertTrue(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)

# ################################################################################################################################

    def test_on_publish_with_restricted_permissions_forbidden_topic(self):

        # Create auth header for restricted user
        auth_header = self._create_basic_auth_header(self.restricted_username, self.restricted_password)

        # Create message data
        message_data = {
            'data': 'Test message for forbidden topic'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Test publishing to forbidden topic should fail
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, 'forbidden.topic')
        self.assertIsInstance(result, BadRequestResponse)
        self.assertFalse(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)
        self.assertIn('permission', result.details.lower())

# ################################################################################################################################

    def test_on_publish_with_no_permissions_configured(self):

        # Add user without any permissions
        no_perms_username = 'no_perms_user'
        no_perms_password = 'no_perms_pass'
        self.rest_server.users[no_perms_username] = no_perms_password

        # Create auth header for user without permissions
        auth_header = self._create_basic_auth_header(no_perms_username, no_perms_password)

        # Create message data
        message_data = {
            'data': 'Test message from user with no permissions'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Test publishing should fail
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, 'any.topic')
        self.assertIsInstance(result, BadRequestResponse)
        self.assertFalse(result.is_ok)
        self.assertEqual(result.cid, self.test_cid)
        self.assertIn('permission', result.details.lower())

# ################################################################################################################################

    def test_on_publish_with_wildcard_pattern_matching(self):

        # Add user with specific wildcard permissions
        wildcard_username = 'wildcard_user'
        wildcard_password = 'wildcard_pass'
        self.rest_server.users[wildcard_username] = wildcard_password

        # Give permissions for system.* topics only
        wildcard_permissions = [
            {'pattern': 'system.*', 'access_type': 'pub'}
        ]
        self.pattern_matcher.add_client(wildcard_username, wildcard_permissions)

        # Create auth header
        auth_header = self._create_basic_auth_header(wildcard_username, wildcard_password)

        # Create message data
        message_data = {
            'data': 'Test message for wildcard matching'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Test publishing to matching wildcard topic should work
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, 'system.events')
        self.assertTrue(result.is_ok)

        # Test publishing to non-matching topic should fail
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, 'user.events')
        self.assertIsInstance(result, BadRequestResponse)
        self.assertFalse(result.is_ok)

# ################################################################################################################################

    def test_on_publish_with_exact_topic_pattern(self):

        # Add user with exact topic permissions
        exact_username = 'exact_user'
        exact_password = 'exact_pass'
        self.rest_server.users[exact_username] = exact_password

        # Give permissions for exact topic only
        exact_permissions = [
            {'pattern': 'exact.topic.name', 'access_type': 'pub'}
        ]
        self.pattern_matcher.add_client(exact_username, exact_permissions)

        # Create auth header
        auth_header = self._create_basic_auth_header(exact_username, exact_password)

        # Create message data
        message_data = {
            'data': 'Test message for exact topic'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Test publishing to exact topic should work
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, 'exact.topic.name')
        self.assertTrue(result.is_ok)

        # Test publishing to similar but different topic should fail
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, 'exact.topic.other')
        self.assertIsInstance(result, BadRequestResponse)
        self.assertFalse(result.is_ok)

# ################################################################################################################################

    def test_on_publish_with_multiple_pattern_permissions(self):

        # Add user with multiple pattern permissions
        multi_username = 'multi_user'
        multi_password = 'multi_pass'
        self.rest_server.users[multi_username] = multi_password

        # Give multiple permissions
        multi_permissions = [
            {'pattern': 'logs.*', 'access_type': 'pub'},
            {'pattern': 'metrics.cpu.*', 'access_type': 'pub'},
            {'pattern': 'alerts.critical', 'access_type': 'pub'}
        ]
        self.pattern_matcher.add_client(multi_username, multi_permissions)

        # Create auth header
        auth_header = self._create_basic_auth_header(multi_username, multi_password)

        # Create message data
        message_data = {
            'data': 'Test message for multiple patterns'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Test all allowed patterns
        allowed_topics = ['logs.application', 'logs.system', 'metrics.cpu.usage', 'alerts.critical']
        for topic in allowed_topics:
            result = self.rest_server.on_publish(self.test_cid, environ, start_response, topic)
            self.assertTrue(result.is_ok, f'Failed for allowed topic: {topic}')

        # Test forbidden patterns
        forbidden_topics = ['metrics.memory.usage', 'alerts.warning', 'debug.info']
        for topic in forbidden_topics:
            result = self.rest_server.on_publish(self.test_cid, environ, start_response, topic)
            self.assertIsInstance(result, BadRequestResponse, f'Should have failed for forbidden topic: {topic}')
            self.assertFalse(result.is_ok)

# ################################################################################################################################

    def test_on_publish_with_subscription_only_permissions(self):

        # Add user with subscription-only permissions
        sub_only_username = 'sub_only_user'
        sub_only_password = 'sub_only_pass'
        self.rest_server.users[sub_only_username] = sub_only_password

        # Give subscription permissions only (no publish permissions)
        sub_only_permissions = [
            {'pattern': '*', 'access_type': 'sub'}
        ]
        self.pattern_matcher.add_client(sub_only_username, sub_only_permissions)

        # Create auth header
        auth_header = self._create_basic_auth_header(sub_only_username, sub_only_password)

        # Create message data
        message_data = {
            'data': 'Test message from subscription-only user'
        }

        environ = self._create_environ(auth_header, data=message_data)
        start_response = self._create_start_response()

        # Test publishing should fail (no publish permissions)
        result = self.rest_server.on_publish(self.test_cid, environ, start_response, 'any.topic')
        self.assertIsInstance(result, BadRequestResponse)
        self.assertFalse(result.is_ok)
        self.assertIn('permission', result.details.lower())

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
