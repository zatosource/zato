# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase
import warnings

# Zato
from zato.common.pubsub.backend.rest_backend import RESTBackend
from zato.common.pubsub.server.rest import PubSubRESTServer
from zato.broker.client import BrokerClient

# ################################################################################################################################
# ################################################################################################################################

class RESTBackendSecurityBasicAuthChangePasswordTestCase(TestCase):

    def setUp(self):

        # Suppress ResourceWarnings from gevent
        warnings.filterwarnings('ignore', category=ResourceWarning)

        self.broker_client = BrokerClient()
        self.rest_server = PubSubRESTServer('localhost', 8080)
        self.backend = RESTBackend(self.rest_server, self.broker_client)

        # Test data constants
        self.test_cid = 'test-cid-123'
        self.test_username = 'test_user'
        self.test_old_password = 'old_password_123'
        self.test_new_password = 'new_password_456'

        self.empty_password_cid = 'test-cid-empty'
        self.empty_password_username = 'empty_password_user'
        self.empty_old_password = 'old_password'
        self.empty_new_password = ''

        self.special_chars_cid = 'test-cid-special'
        self.special_chars_username = 'user@domain.com'
        self.special_chars_old_password = 'old_password123'
        self.special_chars_new_password = 'new_password!@#$%'

        self.unicode_cid = 'test-cid-unicode'
        self.unicode_username = 'unicode_user_ñ'
        self.unicode_old_password = 'old_password_ü123'
        self.unicode_new_password = 'new_password_ñ456'

        self.long_values_cid = 'test-cid-long'
        self.long_username = 'a' * 100
        self.long_old_password = 'b' * 200
        self.long_new_password = 'c' * 300

        self.numeric_cid = 12345
        self.numeric_cid_username = 'numeric_cid_user'
        self.numeric_old_password = 'old_numeric_password'
        self.numeric_new_password = 'new_numeric_password'

        self.preserve_cid = 'test-cid-preserve'
        self.preserve_username = 'preserve_user'
        self.preserve_old_password = 'old_preserve_password'
        self.preserve_new_password = 'new_preserve_password'

        self.nonexistent_cid = 'test-cid-nonexistent'
        self.nonexistent_username = 'nonexistent_user'
        self.nonexistent_old_password = 'old_password'
        self.nonexistent_new_password = 'new_password'

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD_updates_existing_user(self):

        # First create a user
        self.rest_server.users[self.test_username] = self.test_old_password

        # Create the broker message
        msg = {
            'cid': self.test_cid,
            'username': self.test_username,
            'password': self.test_new_password
        }

        # Verify user has old password initially
        self.assertEqual(self.rest_server.users[self.test_username], self.test_old_password)

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(msg)

        # Assert password was updated
        self.assertEqual(self.rest_server.users[self.test_username], self.test_new_password)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD_with_empty_password(self):

        # First create a user
        self.rest_server.users[self.empty_password_username] = self.empty_old_password

        # Create the broker message with empty new password
        msg = {
            'cid': self.empty_password_cid,
            'username': self.empty_password_username,
            'password': self.empty_new_password
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(msg)

        # Assert password was updated to empty string
        self.assertEqual(self.rest_server.users[self.empty_password_username], self.empty_new_password)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD_with_special_characters(self):

        # First create a user
        self.rest_server.users[self.special_chars_username] = self.special_chars_old_password

        # Create the broker message with special characters
        msg = {
            'cid': self.special_chars_cid,
            'username': self.special_chars_username,
            'password': self.special_chars_new_password
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(msg)

        # Assert password was updated
        self.assertEqual(self.rest_server.users[self.special_chars_username], self.special_chars_new_password)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD_with_unicode_characters(self):

        # First create a user
        self.rest_server.users[self.unicode_username] = self.unicode_old_password

        # Create the broker message with unicode characters
        msg = {
            'cid': self.unicode_cid,
            'username': self.unicode_username,
            'password': self.unicode_new_password
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(msg)

        # Assert password was updated
        self.assertEqual(self.rest_server.users[self.unicode_username], self.unicode_new_password)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD_with_long_values(self):

        # First create a user
        self.rest_server.users[self.long_username] = self.long_old_password

        # Create the broker message with long values
        msg = {
            'cid': self.long_values_cid,
            'username': self.long_username,
            'password': self.long_new_password
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(msg)

        # Assert password was updated
        self.assertEqual(self.rest_server.users[self.long_username], self.long_new_password)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD_multiple_calls(self):

        # Test data for multiple password changes
        multi_cid_1 = 'test-cid-multi-1'
        multi_username = 'multi_user'
        multi_password_1 = 'password_1'
        multi_password_2 = 'password_2'
        multi_password_3 = 'password_3'

        # First create a user
        self.rest_server.users[multi_username] = multi_password_1

        # First password change
        msg1 = {
            'cid': multi_cid_1,
            'username': multi_username,
            'password': multi_password_2
        }

        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(msg1)
        self.assertEqual(self.rest_server.users[multi_username], multi_password_2)

        # Second password change
        msg2 = {
            'cid': 'test-cid-multi-2',
            'username': multi_username,
            'password': multi_password_3
        }

        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(msg2)
        self.assertEqual(self.rest_server.users[multi_username], multi_password_3)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD_preserves_message_data(self):

        # First create a user
        self.rest_server.users[self.preserve_username] = self.preserve_old_password

        # Extra fields that should be ignored
        extra_field_value = 'extra_value'
        another_field_value = 42

        msg = {
            'cid': self.preserve_cid,
            'username': self.preserve_username,
            'password': self.preserve_new_password,
            'extra_field': extra_field_value,
            'another_field': another_field_value
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(msg)

        # Assert password was updated and user exists
        self.assertEqual(self.rest_server.users[self.preserve_username], self.preserve_new_password)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD_with_numeric_cid(self):

        # First create a user
        self.rest_server.users[self.numeric_cid_username] = self.numeric_old_password

        # Create the broker message with numeric CID
        msg = {
            'cid': self.numeric_cid,
            'username': self.numeric_cid_username,
            'password': self.numeric_new_password
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(msg)

        # Assert password was updated regardless of CID type
        self.assertEqual(self.rest_server.users[self.numeric_cid_username], self.numeric_new_password)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD_does_not_modify_backend_state(self):

        # First create a user
        self.rest_server.users['state_user'] = 'old_state_password'

        # Store initial state
        initial_topics = dict(self.backend.topics)
        initial_subs = dict(self.backend.subs_by_topic)

        # Create the broker message
        msg = {
            'cid': 'test-cid-state',
            'username': 'state_user',
            'password': 'new_state_password'
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(msg)

        # Assert backend state was not modified
        self.assertEqual(self.backend.topics, initial_topics)
        self.assertEqual(self.backend.subs_by_topic, initial_subs)

        # But password should be updated
        self.assertEqual(self.rest_server.users['state_user'], 'new_state_password')

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD_nonexistent_user_handling(self):

        # Verify user doesn't exist initially
        self.assertNotIn(self.nonexistent_username, self.rest_server.users)

        # Create the broker message for nonexistent user
        msg = {
            'cid': self.nonexistent_cid,
            'username': self.nonexistent_username,
            'password': self.nonexistent_new_password
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(msg)

        # Assert user still doesn't exist (no creation occurred)
        self.assertNotIn(self.nonexistent_username, self.rest_server.users)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
