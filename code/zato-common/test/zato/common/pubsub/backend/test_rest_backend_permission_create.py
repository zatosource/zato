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

class RESTBackendPermissionCreateTestCase(TestCase):

    def setUp(self):
        self.rest_server = Mock()
        self.rest_server.users = {}
        self.broker_client = Mock()
        self.backend = RESTBackend(self.rest_server, self.broker_client)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_PERMISSION_CREATE_adds_permissions_for_existing_user(self):

        # Set up test data
        username = 'test_user'
        self.rest_server.users[username] = {"sec_name": "test_sec_def", "password": 'password123'}

        # Create the broker message
        msg = {
            'cid': 'test-cid-123',
            'pattern': 'orders.*\ninvoices.*',
            'access_type': 'publisher',
            'username': username
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_PERMISSION_CREATE(msg)

        # Assert permissions were added for the specific user
        result_orders = self.backend.pattern_matcher.evaluate(username, 'orders.new', 'publish')
        result_invoices = self.backend.pattern_matcher.evaluate(username, 'invoices.paid', 'publish')

        self.assertTrue(result_orders.is_ok)
        self.assertTrue(result_invoices.is_ok)
        self.assertEqual(result_orders.matched_pattern, 'orders.*')
        self.assertEqual(result_invoices.matched_pattern, 'invoices.*')

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_PERMISSION_CREATE_handles_nonexistent_user(self):

        # Create the broker message for a user that doesn't exist
        msg = {
            'cid': 'test-cid-456',
            'pattern': 'test.*',
            'access_type': 'subscriber',
            'username': 'nonexistent_user'
        }

        # Call the method under test - should not raise an exception
        self.backend.on_broker_msg_PUBSUB_PERMISSION_CREATE(msg)

        # Assert no permissions were added (pattern matcher should be empty)
        client_count = self.backend.pattern_matcher.get_client_count()
        self.assertEqual(client_count, 0)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_PERMISSION_CREATE_subscriber_permissions(self):

        # Set up test data
        username = 'subscriber_user'
        self.rest_server.users[username] = {"sec_name": "test_sec_def", "password": 'sub_password'}

        # Create the broker message for subscriber permissions
        msg = {
            'cid': 'test-cid-789',
            'pattern': 'notifications.*\nalerts.critical',
            'access_type': 'subscriber',
            'username': username
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_PERMISSION_CREATE(msg)

        # Assert subscriber permissions were added
        result_notifications = self.backend.pattern_matcher.evaluate(username, 'notifications.email', 'subscribe')
        result_alerts = self.backend.pattern_matcher.evaluate(username, 'alerts.critical', 'subscribe')

        self.assertTrue(result_notifications.is_ok)
        self.assertTrue(result_alerts.is_ok)
        self.assertEqual(result_notifications.matched_pattern, 'notifications.*')
        self.assertEqual(result_alerts.matched_pattern, 'alerts.critical')

        # Assert user cannot publish to these topics (wrong access type)
        result_pub_notifications = self.backend.pattern_matcher.evaluate(username, 'notifications.email', 'publish')
        result_pub_alerts = self.backend.pattern_matcher.evaluate(username, 'alerts.critical', 'publish')

        self.assertFalse(result_pub_notifications.is_ok)
        self.assertFalse(result_pub_alerts.is_ok)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_PERMISSION_CREATE_single_pattern(self):

        # Set up test data
        username = 'single_pattern_user'
        self.rest_server.users[username] = {"sec_name": "test_sec_def", "password": 'single_password'}

        # Create the broker message with a single pattern
        msg = {
            'cid': 'test-cid-single',
            'pattern': 'exact.topic.name',
            'access_type': 'publisher',
            'username': username
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_PERMISSION_CREATE(msg)

        # Assert permission was added for exact topic
        result_exact = self.backend.pattern_matcher.evaluate(username, 'exact.topic.name', 'publish')
        self.assertTrue(result_exact.is_ok)
        self.assertEqual(result_exact.matched_pattern, 'exact.topic.name')

        # Assert no permission for different topic
        result_different = self.backend.pattern_matcher.evaluate(username, 'different.topic', 'publish')
        self.assertFalse(result_different.is_ok)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_PERMISSION_CREATE_empty_patterns_filtered(self):

        # Set up test data
        username = 'filter_user'
        self.rest_server.users[username] = {"sec_name": "test_sec_def", "password": 'filter_password'}

        # Create the broker message with empty lines that should be filtered
        msg = {
            'cid': 'test-cid-filter',
            'pattern': 'valid.pattern\n\n  \nother.pattern\n\t\n',
            'access_type': 'subscriber',
            'username': username
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_PERMISSION_CREATE(msg)

        # Assert only valid patterns were added
        result_valid = self.backend.pattern_matcher.evaluate(username, 'valid.pattern', 'subscribe')
        result_other = self.backend.pattern_matcher.evaluate(username, 'other.pattern', 'subscribe')

        self.assertTrue(result_valid.is_ok)
        self.assertTrue(result_other.is_ok)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_PERMISSION_CREATE_does_not_affect_other_users(self):

        # Set up multiple users
        user1 = 'user_one'
        user2 = 'user_two'
        self.rest_server.users[user1] = {"sec_name": "test_sec_def", "password": 'password1'}
        self.rest_server.users[user2] = {"sec_name": "test_sec_def", "password": 'password2'}

        # Give user1 some initial permissions
        initial_permissions = [{'pattern': 'initial.*', 'access_type': 'publisher'}]
        self.backend.pattern_matcher.add_client(user1, initial_permissions)

        # Create the broker message for user2 only
        msg = {
            'cid': 'test-cid-isolation',
            'pattern': 'user2.*',
            'access_type': 'subscriber',
            'username': user2
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_PERMISSION_CREATE(msg)

        # Assert user1's permissions are unchanged
        result_user1_initial = self.backend.pattern_matcher.evaluate(user1, 'initial.topic', 'publish')
        result_user1_new = self.backend.pattern_matcher.evaluate(user1, 'user2.topic', 'subscribe')

        self.assertTrue(result_user1_initial.is_ok)  # Original permission still exists
        self.assertFalse(result_user1_new.is_ok)     # New permission not added to user1

        # Assert user2 got the new permissions
        result_user2_new = self.backend.pattern_matcher.evaluate(user2, 'user2.topic', 'subscribe')
        result_user2_initial = self.backend.pattern_matcher.evaluate(user2, 'initial.topic', 'publish')

        self.assertTrue(result_user2_new.is_ok)      # New permission added to user2
        self.assertFalse(result_user2_initial.is_ok) # user1's permission not added to user2

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
