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

class RESTBackendSecurityBasicAuthCreateTestCase(TestCase):

    def setUp(self):

        # Suppress ResourceWarnings from gevent
        warnings.filterwarnings('ignore', category=ResourceWarning)

        self.broker_client = BrokerClient()
        self.rest_server = PubSubRESTServer('localhost', 8080)
        self.backend = RESTBackend(self.rest_server, self.broker_client)

        # Test data constants
        self.test_cid = 'test-cid-123'
        self.test_username = 'test_user'
        self.test_password = 'secure_password_123'

        self.empty_password_cid = 'test-cid-empty'
        self.empty_password_username = 'empty_password_user'
        self.empty_password = ''

        self.special_chars_cid = 'test-cid-special'
        self.special_chars_username = 'user@domain.com'
        self.special_chars_password = 'password123'

        self.unicode_cid = 'test-cid-unicode'
        self.unicode_username = 'unicode_user_ñ'
        self.unicode_password = 'password_ü123'

        self.long_values_cid = 'test-cid-long'
        self.long_username = 'a' * 100
        self.long_password = 'b' * 200

        self.numeric_cid = 12345
        self.numeric_cid_username = 'numeric_cid_user'
        self.numeric_cid_password = 'numeric_password'

        self.preserve_cid = 'test-cid-preserve'
        self.preserve_username = 'preserve_user'
        self.preserve_password = 'preserve_password'

        self.duplicate_cid_1 = 'test-cid-duplicate'
        self.duplicate_cid_2 = 'test-cid-duplicate-2'
        self.duplicate_username = 'duplicate_user'
        self.duplicate_password_1 = 'first_password'
        self.duplicate_password_2 = 'second_password'

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CREATE_creates_new_user(self):

        # Create the broker message
        msg = {
            'cid': self.test_cid,
            'sec_name': self.test_username,
            'password': self.test_password
        }

        # Verify user doesn't exist initially
        self.assertNotIn(self.test_username, self.rest_server.users)

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CREATE(msg)

        # Assert user was added to users dict
        self.assertIn(self.test_username, self.rest_server.users)
        self.assertEqual(self.rest_server.users[self.test_username], self.test_password)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CREATE_with_empty_password(self):

        # Create the broker message with empty password
        msg = {
            'cid': self.empty_password_cid,
            'sec_name': self.empty_password_username,
            'password': self.empty_password
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CREATE(msg)

        # Assert user was added with empty password
        self.assertIn(self.empty_password_username, self.rest_server.users)
        self.assertEqual(self.rest_server.users[self.empty_password_username], self.empty_password)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CREATE_with_special_characters_in_username(self):

        # Create the broker message with special characters in username
        msg = {
            'cid': self.special_chars_cid,
            'sec_name': self.special_chars_username,
            'password': self.special_chars_password
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CREATE(msg)

        # Assert user was added with special character username
        self.assertIn(self.special_chars_username, self.rest_server.users)
        self.assertEqual(self.rest_server.users[self.special_chars_username], self.special_chars_password)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CREATE_with_unicode_characters(self):

        # Create the broker message with unicode characters
        msg = {
            'cid': self.unicode_cid,
            'sec_name': self.unicode_username,
            'password': self.unicode_password
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CREATE(msg)

        # Assert user was added with unicode characters
        self.assertIn(self.unicode_username, self.rest_server.users)
        self.assertEqual(self.rest_server.users[self.unicode_username], self.unicode_password)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CREATE_with_long_values(self):

        # Create the broker message with long values
        msg = {
            'cid': self.long_values_cid,
            'sec_name': self.long_username,
            'password': self.long_password
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CREATE(msg)

        # Assert user was added with long values
        self.assertIn(self.long_username, self.rest_server.users)
        self.assertEqual(self.rest_server.users[self.long_username], self.long_password)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CREATE_multiple_calls(self):

        # Test data for multiple users
        multi_cid_1 = 'test-cid-1'
        multi_cid_2 = 'test-cid-2'
        multi_cid_3 = 'test-cid-3'
        multi_username_1 = 'user1'
        multi_username_2 = 'user2'
        multi_username_3 = 'user3'
        multi_password_1 = 'password1'
        multi_password_2 = 'password2'
        multi_password_3 = 'password3'

        # Create multiple broker messages
        messages = [
            {
                'cid': multi_cid_1,
                'sec_name': multi_username_1,
                'password': multi_password_1
            },
            {
                'cid': multi_cid_2,
                'sec_name': multi_username_2,
                'password': multi_password_2
            },
            {
                'cid': multi_cid_3,
                'sec_name': multi_username_3,
                'password': multi_password_3
            }
        ]

        # Call the method under test multiple times
        for msg in messages:
            self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CREATE(msg)

        # Assert all users were added
        self.assertEqual(len(self.rest_server.users), 3)
        self.assertIn(multi_username_1, self.rest_server.users)
        self.assertIn(multi_username_2, self.rest_server.users)
        self.assertIn(multi_username_3, self.rest_server.users)
        self.assertEqual(self.rest_server.users[multi_username_1], multi_password_1)
        self.assertEqual(self.rest_server.users[multi_username_2], multi_password_2)
        self.assertEqual(self.rest_server.users[multi_username_3], multi_password_3)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CREATE_preserves_message_data(self):

        # Create the broker message with additional fields
        extra_field_value = 'should_be_ignored'
        another_field_value = 123

        msg = {
            'cid': self.preserve_cid,
            'sec_name': self.preserve_username,
            'password': self.preserve_password,
            'extra_field': extra_field_value,
            'another_field': another_field_value
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CREATE(msg)

        # Assert only the required fields were used and user was created
        self.assertIn(self.preserve_username, self.rest_server.users)
        self.assertEqual(self.rest_server.users[self.preserve_username], self.preserve_password)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CREATE_with_numeric_cid(self):

        # Create the broker message with numeric CID
        msg = {
            'cid': self.numeric_cid,
            'sec_name': self.numeric_cid_username,
            'password': self.numeric_cid_password
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CREATE(msg)

        # Assert user was created regardless of CID type
        self.assertIn(self.numeric_cid_username, self.rest_server.users)
        self.assertEqual(self.rest_server.users[self.numeric_cid_username], self.numeric_cid_password)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CREATE_does_not_modify_backend_state(self):

        # Store initial state
        initial_topics = dict(self.backend.topics)
        initial_subs = dict(self.backend.subs_by_topic)

        # Create the broker message
        msg = {
            'cid': 'test-cid-state',
            'sec_name': 'state_user',
            'password': 'state_password'
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CREATE(msg)

        # Assert backend state was not modified
        self.assertEqual(self.backend.topics, initial_topics)
        self.assertEqual(self.backend.subs_by_topic, initial_subs)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CREATE_duplicate_user_handling(self):

        # Create the broker message
        msg = {
            'cid': self.duplicate_cid_1,
            'sec_name': self.duplicate_username,
            'password': self.duplicate_password_1
        }

        # Call the method under test first time
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CREATE(msg)

        # Assert user was created
        self.assertIn(self.duplicate_username, self.rest_server.users)
        self.assertEqual(self.rest_server.users[self.duplicate_username], self.duplicate_password_1)

        # Create second message with same user but different password
        msg2 = {
            'cid': self.duplicate_cid_2,
            'sec_name': self.duplicate_username,
            'password': self.duplicate_password_2
        }

        # Call the method under test second time
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CREATE(msg2)

        # Assert user still exists with original password (no overwrite)
        self.assertIn(self.duplicate_username, self.rest_server.users)
        self.assertEqual(self.rest_server.users[self.duplicate_username], self.duplicate_password_1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
