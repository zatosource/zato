# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Must come first
from gevent import monkey;
_ = monkey.patch_all()

# stdlib
from unittest import main, TestCase
from unittest.mock import Mock

# Zato
from zato.common.pubsub.backend.rest_backend import RESTBackend

# ################################################################################################################################
# ################################################################################################################################

class RESTBackendPermissionDeleteTestCase(TestCase):

    def setUp(self):
        self.rest_server = Mock()
        self.rest_server.users = {}
        self.broker_client = Mock()
        self.backend = RESTBackend(self.rest_server, self.broker_client)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_PERMISSION_DELETE_removes_permissions_for_existing_user(self):

        # Set up test data
        username = 'test_user'
        self.rest_server.users[username] = 'password123'

        # Add initial permissions
        initial_permissions = [
            {'pattern': 'orders.*', 'access_type': 'publisher'},
            {'pattern': 'invoices.*', 'access_type': 'subscriber'}
        ]
        self.backend.pattern_matcher.add_client(username, initial_permissions)

        # Verify permissions exist
        result_orders = self.backend.pattern_matcher.evaluate(username, 'orders.new', 'publish')
        result_invoices = self.backend.pattern_matcher.evaluate(username, 'invoices.paid', 'subscribe')
        self.assertTrue(result_orders.is_ok)
        self.assertTrue(result_invoices.is_ok)

        # Create the broker message
        msg = {
            'cid': 'test-cid-123',
            'username': username
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_PERMISSION_DELETE(msg)

        # Assert all permissions were removed for the user
        result_orders_after = self.backend.pattern_matcher.evaluate(username, 'orders.new', 'publish')
        result_invoices_after = self.backend.pattern_matcher.evaluate(username, 'invoices.paid', 'subscribe')
        self.assertFalse(result_orders_after.is_ok)
        self.assertFalse(result_invoices_after.is_ok)

        # Assert user was removed from pattern matcher
        client_count = self.backend.pattern_matcher.get_client_count()
        self.assertEqual(client_count, 0)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_PERMISSION_DELETE_handles_nonexistent_user(self):

        # Add a different user to ensure we don't affect existing users
        other_username = 'other_user'
        self.rest_server.users[other_username] = 'other_password'
        other_permissions = [{'pattern': 'other.*', 'access_type': 'publisher'}]
        self.backend.pattern_matcher.add_client(other_username, other_permissions)

        # Create the broker message for a user that doesn't exist
        msg = {
            'cid': 'test-cid-456',
            'username': 'nonexistent_user'
        }

        # Call the method under test - should not raise an exception
        self.backend.on_broker_msg_PUBSUB_PERMISSION_DELETE(msg)

        # Assert other user's permissions are unchanged
        result_other = self.backend.pattern_matcher.evaluate(other_username, 'other.topic', 'publish')
        self.assertTrue(result_other.is_ok)

        # Assert pattern matcher still has the other user
        client_count = self.backend.pattern_matcher.get_client_count()
        self.assertEqual(client_count, 1)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_PERMISSION_DELETE_does_not_affect_other_users(self):

        # Set up multiple users
        user1 = 'user_one'
        user2 = 'user_two'
        user3 = 'user_three'
        self.rest_server.users[user1] = 'password1'
        self.rest_server.users[user2] = 'password2'
        self.rest_server.users[user3] = 'password3'

        # Give each user different permissions
        user1_permissions = [{'pattern': 'user1.*', 'access_type': 'publisher'}]
        user2_permissions = [{'pattern': 'user2.*', 'access_type': 'subscriber'}]
        user3_permissions = [{'pattern': 'user3.*', 'access_type': 'publisher'}]

        self.backend.pattern_matcher.add_client(user1, user1_permissions)
        self.backend.pattern_matcher.add_client(user2, user2_permissions)
        self.backend.pattern_matcher.add_client(user3, user3_permissions)

        # Verify all users have permissions
        result_user1 = self.backend.pattern_matcher.evaluate(user1, 'user1.topic', 'publish')
        result_user2 = self.backend.pattern_matcher.evaluate(user2, 'user2.topic', 'subscribe')
        result_user3 = self.backend.pattern_matcher.evaluate(user3, 'user3.topic', 'publish')

        self.assertTrue(result_user1.is_ok)
        self.assertTrue(result_user2.is_ok)
        self.assertTrue(result_user3.is_ok)

        # Create the broker message to delete permissions for user2 only
        msg = {
            'cid': 'test-cid-isolation',
            'username': user2
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_PERMISSION_DELETE(msg)

        # Assert user1 and user3 permissions are unchanged
        result_user1_after = self.backend.pattern_matcher.evaluate(user1, 'user1.topic', 'publish')
        result_user3_after = self.backend.pattern_matcher.evaluate(user3, 'user3.topic', 'publish')

        self.assertTrue(result_user1_after.is_ok)
        self.assertTrue(result_user3_after.is_ok)

        # Assert user2 permissions are gone
        result_user2_after = self.backend.pattern_matcher.evaluate(user2, 'user2.topic', 'subscribe')
        self.assertFalse(result_user2_after.is_ok)

        # Assert pattern matcher has 2 clients remaining
        client_count = self.backend.pattern_matcher.get_client_count()
        self.assertEqual(client_count, 2)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_PERMISSION_DELETE_removes_all_permission_types(self):

        # Set up test data
        username = 'multi_permission_user'
        self.rest_server.users[username] = 'multi_password'

        # Add permissions for both publisher and subscriber
        mixed_permissions = [
            {'pattern': 'publish.*', 'access_type': 'publisher'},
            {'pattern': 'subscribe.*', 'access_type': 'subscriber'},
            {'pattern': 'both.*', 'access_type': 'publisher'},
            {'pattern': 'both.*', 'access_type': 'subscriber'}
        ]
        self.backend.pattern_matcher.add_client(username, mixed_permissions)

        # Verify all permissions work
        result_publish = self.backend.pattern_matcher.evaluate(username, 'publish.topic', 'publish')
        result_subscribe = self.backend.pattern_matcher.evaluate(username, 'subscribe.topic', 'subscribe')
        result_both_pub = self.backend.pattern_matcher.evaluate(username, 'both.topic', 'publish')
        result_both_sub = self.backend.pattern_matcher.evaluate(username, 'both.topic', 'subscribe')

        self.assertTrue(result_publish.is_ok)
        self.assertTrue(result_subscribe.is_ok)
        self.assertTrue(result_both_pub.is_ok)
        self.assertTrue(result_both_sub.is_ok)

        # Create the broker message
        msg = {
            'cid': 'test-cid-multi',
            'username': username
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_PERMISSION_DELETE(msg)

        # Assert all permissions are gone
        result_publish_after = self.backend.pattern_matcher.evaluate(username, 'publish.topic', 'publish')
        result_subscribe_after = self.backend.pattern_matcher.evaluate(username, 'subscribe.topic', 'subscribe')
        result_both_pub_after = self.backend.pattern_matcher.evaluate(username, 'both.topic', 'publish')
        result_both_sub_after = self.backend.pattern_matcher.evaluate(username, 'both.topic', 'subscribe')

        self.assertFalse(result_publish_after.is_ok)
        self.assertFalse(result_subscribe_after.is_ok)
        self.assertFalse(result_both_pub_after.is_ok)
        self.assertFalse(result_both_sub_after.is_ok)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_PERMISSION_DELETE_with_empty_pattern_matcher(self):

        # Set up user but no permissions
        username = 'empty_user'
        self.rest_server.users[username] = 'empty_password'

        # Verify pattern matcher is empty
        client_count_before = self.backend.pattern_matcher.get_client_count()
        self.assertEqual(client_count_before, 0)

        # Create the broker message
        msg = {
            'cid': 'test-cid-empty',
            'username': username
        }

        # Call the method under test - should not raise an exception
        self.backend.on_broker_msg_PUBSUB_PERMISSION_DELETE(msg)

        # Assert pattern matcher is still empty
        client_count_after = self.backend.pattern_matcher.get_client_count()
        self.assertEqual(client_count_after, 0)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_PERMISSION_DELETE_preserves_cache_and_state(self):

        # Set up multiple users
        user1 = 'cache_user1'
        user2 = 'cache_user2'
        self.rest_server.users[user1] = 'cache_password1'
        self.rest_server.users[user2] = 'cache_password2'

        # Add permissions
        user1_permissions = [{'pattern': 'cache1.*', 'access_type': 'publisher'}]
        user2_permissions = [{'pattern': 'cache2.*', 'access_type': 'subscriber'}]

        self.backend.pattern_matcher.add_client(user1, user1_permissions)
        self.backend.pattern_matcher.add_client(user2, user2_permissions)

        # Trigger some evaluations to populate cache
        _ = self.backend.pattern_matcher.evaluate(user1, 'cache1.topic', 'publish')
        _ = self.backend.pattern_matcher.evaluate(user2, 'cache2.topic', 'subscribe')

        # Get initial cache size
        cache_size_before = self.backend.pattern_matcher.get_cache_size()
        self.assertGreater(cache_size_before, 0)

        # Create the broker message to delete user1
        msg = {
            'cid': 'test-cid-cache',
            'username': user1
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_PERMISSION_DELETE(msg)

        # Assert user1 is gone but user2 remains
        result_user1_after = self.backend.pattern_matcher.evaluate(user1, 'cache1.topic', 'publish')
        result_user2_after = self.backend.pattern_matcher.evaluate(user2, 'cache2.topic', 'subscribe')

        self.assertFalse(result_user1_after.is_ok)
        self.assertTrue(result_user2_after.is_ok)

        # Assert pattern matcher state is consistent
        client_count = self.backend.pattern_matcher.get_client_count()
        self.assertEqual(client_count, 1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
