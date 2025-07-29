# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase
from unittest.mock import Mock

# Zato
from zato.common.pubsub.backend.rest_backend import RESTBackend

# ################################################################################################################################
# ################################################################################################################################

class RESTBackendPermissionEditTestCase(TestCase):

    def setUp(self):
        self.rest_server = Mock()
        self.rest_server.users = {}
        self.broker_client = Mock()
        self.backend = RESTBackend(self.rest_server, self.broker_client)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_PERMISSION_EDIT_updates_permissions_for_existing_user(self):

        # Set up test data
        username = 'test_user'
        self.rest_server.users[username] = 'password123'

        # Add initial permissions
        initial_permissions = [{'pattern': 'old.*', 'access_type': 'publisher'}]
        self.backend.pattern_matcher.add_client(username, initial_permissions)

        # Create the broker message with new permissions
        msg = {
            'cid': 'test-cid-123',
            'pattern': 'orders.*\ninvoices.*',
            'access_type': 'publisher',
            'username': username
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_PERMISSION_EDIT(msg)

        # Assert new permissions were set (replacing old ones)
        result_orders = self.backend.pattern_matcher.evaluate(username, 'orders.new', 'publish')
        result_invoices = self.backend.pattern_matcher.evaluate(username, 'invoices.paid', 'publish')
        result_old = self.backend.pattern_matcher.evaluate(username, 'old.topic', 'publish')

        self.assertTrue(result_orders.is_ok)
        self.assertTrue(result_invoices.is_ok)
        self.assertFalse(result_old.is_ok)  # Old permission should be gone
        self.assertEqual(result_orders.matched_pattern, 'orders.*')
        self.assertEqual(result_invoices.matched_pattern, 'invoices.*')

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_PERMISSION_EDIT_handles_nonexistent_user(self):

        # Create the broker message for a user that doesn't exist
        msg = {
            'cid': 'test-cid-456',
            'pattern': 'test.*',
            'access_type': 'subscriber',
            'username': 'nonexistent_user'
        }

        # Call the method under test - should not raise an exception
        self.backend.on_broker_msg_PUBSUB_PERMISSION_EDIT(msg)

        # Assert no permissions were added (pattern matcher should be empty)
        client_count = self.backend.pattern_matcher.get_client_count()
        self.assertEqual(client_count, 0)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_PERMISSION_EDIT_subscriber_permissions(self):

        # Set up test data
        username = 'subscriber_user'
        self.rest_server.users[username] = 'sub_password'

        # Add initial publisher permissions
        initial_permissions = [{'pattern': 'old.*', 'access_type': 'publisher'}]
        self.backend.pattern_matcher.add_client(username, initial_permissions)

        # Create the broker message for subscriber permissions
        msg = {
            'cid': 'test-cid-789',
            'pattern': 'notifications.*\nalerts.critical',
            'access_type': 'subscriber',
            'username': username
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_PERMISSION_EDIT(msg)

        # Assert subscriber permissions were set (replacing publisher permissions)
        result_notifications = self.backend.pattern_matcher.evaluate(username, 'notifications.email', 'subscribe')
        result_alerts = self.backend.pattern_matcher.evaluate(username, 'alerts.critical', 'subscribe')
        result_old_pub = self.backend.pattern_matcher.evaluate(username, 'old.topic', 'publish')

        self.assertTrue(result_notifications.is_ok)
        self.assertTrue(result_alerts.is_ok)
        self.assertFalse(result_old_pub.is_ok)  # Old publisher permission should be gone
        self.assertEqual(result_notifications.matched_pattern, 'notifications.*')
        self.assertEqual(result_alerts.matched_pattern, 'alerts.critical')

        # Assert user cannot publish to these topics (wrong access type)
        result_pub_notifications = self.backend.pattern_matcher.evaluate(username, 'notifications.email', 'publish')
        result_pub_alerts = self.backend.pattern_matcher.evaluate(username, 'alerts.critical', 'publish')

        self.assertFalse(result_pub_notifications.is_ok)
        self.assertFalse(result_pub_alerts.is_ok)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_PERMISSION_EDIT_single_pattern(self):

        # Set up test data
        username = 'single_user'
        self.rest_server.users[username] = 'single_password'

        # Add initial permissions
        initial_permissions = [{'pattern': 'old.*', 'access_type': 'publisher'}]
        self.backend.pattern_matcher.add_client(username, initial_permissions)

        # Create the broker message with single pattern
        msg = {
            'cid': 'test-cid-single',
            'pattern': 'exact.topic.name',
            'access_type': 'publisher',
            'username': username
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_PERMISSION_EDIT(msg)

        # Assert permission was set for exact topic
        result_exact = self.backend.pattern_matcher.evaluate(username, 'exact.topic.name', 'publish')
        result_old = self.backend.pattern_matcher.evaluate(username, 'old.topic', 'publish')

        self.assertTrue(result_exact.is_ok)
        self.assertFalse(result_old.is_ok)  # Old permission should be gone
        self.assertEqual(result_exact.matched_pattern, 'exact.topic.name')

        # Assert no permission for different topic
        result_different = self.backend.pattern_matcher.evaluate(username, 'different.topic', 'publish')
        self.assertFalse(result_different.is_ok)

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_PERMISSION_EDIT_empty_patterns_filtered(self):

        # Set up test data
        username = 'filter_user'
        self.rest_server.users[username] = 'filter_password'

        # Add initial permissions
        initial_permissions = [{'pattern': 'old.*', 'access_type': 'publisher'}]
        self.backend.pattern_matcher.add_client(username, initial_permissions)

        # Create the broker message with empty lines that should be filtered
        msg = {
            'cid': 'test-cid-filter',
            'pattern': 'valid.pattern\n\n  \nother.pattern\n\t\n',
            'access_type': 'subscriber',
            'username': username
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_PERMISSION_EDIT(msg)

        # Assert only valid patterns were set
        result_valid = self.backend.pattern_matcher.evaluate(username, 'valid.pattern', 'subscribe')
        result_other = self.backend.pattern_matcher.evaluate(username, 'other.pattern', 'subscribe')
        result_old = self.backend.pattern_matcher.evaluate(username, 'old.topic', 'publish')

        self.assertTrue(result_valid.is_ok)
        self.assertTrue(result_other.is_ok)
        self.assertFalse(result_old.is_ok)  # Old permission should be gone

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_PERMISSION_EDIT_does_not_affect_other_users(self):

        # Set up multiple users
        user1 = 'user_one'
        user2 = 'user_two'
        self.rest_server.users[user1] = 'password1'
        self.rest_server.users[user2] = 'password2'

        # Give both users initial permissions
        initial_permissions_1 = [{'pattern': 'user1.*', 'access_type': 'publisher'}]
        initial_permissions_2 = [{'pattern': 'user2.*', 'access_type': 'subscriber'}]
        self.backend.pattern_matcher.add_client(user1, initial_permissions_1)
        self.backend.pattern_matcher.add_client(user2, initial_permissions_2)

        # Create the broker message to edit user2's permissions only
        msg = {
            'cid': 'test-cid-isolation',
            'pattern': 'new.pattern.*',
            'access_type': 'publisher',
            'username': user2
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_PERMISSION_EDIT(msg)

        # Assert user1's permissions are unchanged
        result_user1_original = self.backend.pattern_matcher.evaluate(user1, 'user1.topic', 'publish')
        result_user1_new = self.backend.pattern_matcher.evaluate(user1, 'new.pattern.topic', 'publish')

        self.assertTrue(result_user1_original.is_ok)   # Original permission still exists
        self.assertFalse(result_user1_new.is_ok)       # New permission not added to user1

        # Assert user2 got the new permissions (old ones replaced)
        result_user2_new = self.backend.pattern_matcher.evaluate(user2, 'new.pattern.topic', 'publish')
        result_user2_old = self.backend.pattern_matcher.evaluate(user2, 'user2.topic', 'subscribe')

        self.assertTrue(result_user2_new.is_ok)        # New permission added to user2
        self.assertFalse(result_user2_old.is_ok)       # Old permission replaced

# ################################################################################################################################

    def test_on_broker_msg_PUBSUB_PERMISSION_EDIT_replaces_all_permissions(self):

        # Set up test data
        username = 'replace_user'
        self.rest_server.users[username] = 'replace_password'

        # Add multiple initial permissions
        initial_permissions = [
            {'pattern': 'old1.*', 'access_type': 'publisher'},
            {'pattern': 'old2.*', 'access_type': 'publisher'},
            {'pattern': 'old3.*', 'access_type': 'subscriber'}
        ]
        self.backend.pattern_matcher.add_client(username, initial_permissions)

        # Verify initial permissions work
        result_old1 = self.backend.pattern_matcher.evaluate(username, 'old1.topic', 'publish')
        result_old2 = self.backend.pattern_matcher.evaluate(username, 'old2.topic', 'publish')
        result_old3 = self.backend.pattern_matcher.evaluate(username, 'old3.topic', 'subscribe')

        self.assertTrue(result_old1.is_ok)
        self.assertTrue(result_old2.is_ok)
        self.assertTrue(result_old3.is_ok)

        # Create the broker message with completely new permissions
        msg = {
            'cid': 'test-cid-replace',
            'pattern': 'new1.*\nnew2.*',
            'access_type': 'subscriber',
            'username': username
        }

        # Call the method under test
        self.backend.on_broker_msg_PUBSUB_PERMISSION_EDIT(msg)

        # Assert all old permissions are gone
        result_old1_after = self.backend.pattern_matcher.evaluate(username, 'old1.topic', 'publish')
        result_old2_after = self.backend.pattern_matcher.evaluate(username, 'old2.topic', 'publish')
        result_old3_after = self.backend.pattern_matcher.evaluate(username, 'old3.topic', 'subscribe')

        self.assertFalse(result_old1_after.is_ok)
        self.assertFalse(result_old2_after.is_ok)
        self.assertFalse(result_old3_after.is_ok)

        # Assert new permissions work
        result_new1 = self.backend.pattern_matcher.evaluate(username, 'new1.topic', 'subscribe')
        result_new2 = self.backend.pattern_matcher.evaluate(username, 'new2.topic', 'subscribe')

        self.assertTrue(result_new1.is_ok)
        self.assertTrue(result_new2.is_ok)
        self.assertEqual(result_new1.matched_pattern, 'new1.*')
        self.assertEqual(result_new2.matched_pattern, 'new2.*')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
