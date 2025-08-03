# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.pubsub.backend.rest_backend import RESTBackend
from zato.common.pubsub.server.rest import PubSubRESTServer
from zato.broker.client import BrokerClient

# ################################################################################################################################
# ################################################################################################################################

class RESTBackendSecurityBasicAuthCreateTestCase(TestCase):

    def setUp(self):
        self.broker_client = BrokerClient()
        self.rest_server = PubSubRESTServer('localhost', 8080)
        self.backend = RESTBackend(self.rest_server, self.broker_client)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CREATE_creates_new_user(self):

        # Create the broker message
        msg = {
            'cid': 'test-cid-123',
            'sec_name': 'test_user',
            'password': 'secure_password_123'
        }

        # Verify user doesn't exist initially
        self.assertNotIn('test_user', self.rest_server.users)

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CREATE(msg)

        # Assert user was added to users dict
        self.assertIn('test_user', self.rest_server.users)
        self.assertEqual(self.rest_server.users['test_user'], 'secure_password_123')

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CREATE_with_empty_password(self):

        # Create the broker message with empty password
        msg = {
            'cid': 'test-cid-empty',
            'sec_name': 'empty_password_user',
            'password': ''
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CREATE(msg)

        # Assert user was added with empty password
        self.assertIn('empty_password_user', self.rest_server.users)
        self.assertEqual(self.rest_server.users['empty_password_user'], '')

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CREATE_with_special_characters_in_username(self):

        # Create the broker message with special characters in username
        msg = {
            'cid': 'test-cid-special',
            'sec_name': 'user@domain.com',
            'password': 'password123'
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CREATE(msg)

        # Assert user was added with special character username
        self.assertIn('user@domain.com', self.rest_server.users)
        self.assertEqual(self.rest_server.users['user@domain.com'], 'password123')

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CREATE_with_unicode_characters(self):

        # Create the broker message with unicode characters
        msg = {
            'cid': 'test-cid-unicode',
            'sec_name': 'unicode_user_ñ',
            'password': 'password_ü123'
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CREATE(msg)

        # Assert user was added with unicode characters
        self.assertIn('unicode_user_ñ', self.rest_server.users)
        self.assertEqual(self.rest_server.users['unicode_user_ñ'], 'password_ü123')

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CREATE_with_long_values(self):

        # Create the broker message with long values
        long_username = 'a' * 100
        long_password = 'b' * 200
        msg = {
            'cid': 'test-cid-long',
            'sec_name': long_username,
            'password': long_password
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CREATE(msg)

        # Assert user was added with long values
        self.assertIn(long_username, self.rest_server.users)
        self.assertEqual(self.rest_server.users[long_username], long_password)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CREATE_multiple_calls(self):

        # Create multiple broker messages
        messages = [
            {
                'cid': 'test-cid-1',
                'sec_name': 'user1',
                'password': 'password1'
            },
            {
                'cid': 'test-cid-2',
                'sec_name': 'user2',
                'password': 'password2'
            },
            {
                'cid': 'test-cid-3',
                'sec_name': 'user3',
                'password': 'password3'
            }
        ]

        # Call the method under test multiple times
        for msg in messages:
            self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CREATE(msg)

        # Assert all users were added
        self.assertEqual(len(self.rest_server.users), 3)
        self.assertIn('user1', self.rest_server.users)
        self.assertIn('user2', self.rest_server.users)
        self.assertIn('user3', self.rest_server.users)
        self.assertEqual(self.rest_server.users['user1'], 'password1')
        self.assertEqual(self.rest_server.users['user2'], 'password2')
        self.assertEqual(self.rest_server.users['user3'], 'password3')

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CREATE_preserves_message_data(self):

        # Create the broker message with additional fields
        msg = {
            'cid': 'test-cid-preserve',
            'sec_name': 'preserve_user',
            'password': 'preserve_password',
            'extra_field': 'should_be_ignored',
            'another_field': 123
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CREATE(msg)

        # Assert only the required fields were used and user was created
        self.assertIn('preserve_user', self.rest_server.users)
        self.assertEqual(self.rest_server.users['preserve_user'], 'preserve_password')

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_CREATE_with_numeric_cid(self):

        # Create the broker message with numeric CID
        msg = {
            'cid': 12345,
            'sec_name': 'numeric_cid_user',
            'password': 'numeric_password'
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CREATE(msg)

        # Assert user was created regardless of CID type
        self.assertIn('numeric_cid_user', self.rest_server.users)
        self.assertEqual(self.rest_server.users['numeric_cid_user'], 'numeric_password')

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
            'cid': 'test-cid-duplicate',
            'sec_name': 'duplicate_user',
            'password': 'first_password'
        }

        # Call the method under test first time
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CREATE(msg)

        # Assert user was created
        self.assertIn('duplicate_user', self.rest_server.users)
        self.assertEqual(self.rest_server.users['duplicate_user'], 'first_password')

        # Create second message with same user but different password
        msg2 = {
            'cid': 'test-cid-duplicate-2',
            'sec_name': 'duplicate_user',
            'password': 'second_password'
        }

        # Call the method under test second time
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_CREATE(msg2)

        # Assert user still exists with original password (no overwrite)
        self.assertIn('duplicate_user', self.rest_server.users)
        self.assertEqual(self.rest_server.users['duplicate_user'], 'first_password')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
