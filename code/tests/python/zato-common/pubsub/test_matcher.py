# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.matcher import PatternMatcher

# ################################################################################################################################
# ################################################################################################################################

class PatternMatcherTestCase(TestCase):

    def setUp(self):
        self.matcher = PatternMatcher()
        self.client_id = 'test_client'

# ################################################################################################################################

    def test_exact_match_patterns(self):
        permissions = [{'pattern': 'orders.processed', 'access_type': PubSub.API_Client.Publisher}]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'orders.processed', 'publish')
        self.assertTrue(result.is_ok)
        self.assertEqual(result.matched_pattern, 'orders.processed')

        result = self.matcher.evaluate(self.client_id, 'orders.processed.daily', 'publish')
        self.assertFalse(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'orders.pending', 'publish')
        self.assertFalse(result.is_ok)

# ################################################################################################################################

    def test_single_wildcard_patterns(self):
        permissions = [{'pattern': 'orders.*', 'access_type': PubSub.API_Client.Publisher}]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'orders.processed', 'publish')
        self.assertTrue(result.is_ok)
        self.assertEqual(result.matched_pattern, 'orders.*')

        result = self.matcher.evaluate(self.client_id, 'orders.pending', 'publish')
        self.assertTrue(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'orders.cancelled', 'publish')
        self.assertTrue(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'orders.processed.daily', 'publish')
        self.assertFalse(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'orders.pending.urgent', 'publish')
        self.assertFalse(result.is_ok)

# ################################################################################################################################

    def test_multi_level_wildcard_patterns(self):
        permissions = [{'pattern': 'orders.**', 'access_type': PubSub.API_Client.Publisher}]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'orders.processed', 'publish')
        self.assertTrue(result.is_ok)
        self.assertEqual(result.matched_pattern, 'orders.**')

        result = self.matcher.evaluate(self.client_id, 'orders.processed.daily', 'publish')
        self.assertTrue(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'orders.pending.urgent.high', 'publish')
        self.assertTrue(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'inventory.low', 'publish')
        self.assertFalse(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'users.created', 'publish')
        self.assertFalse(result.is_ok)

# ################################################################################################################################

    def test_wildcards_at_beginning(self):
        permissions = [{'pattern': '*.orders', 'access_type': PubSub.API_Client.Publisher}]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'urgent.orders', 'publish')
        self.assertTrue(result.is_ok)
        self.assertEqual(result.matched_pattern, '*.orders')

        result = self.matcher.evaluate(self.client_id, 'daily.orders', 'publish')
        self.assertTrue(result.is_ok)

# ################################################################################################################################

    def test_mixed_wildcards_in_pattern(self):
        permissions = [{'pattern': 'orders.*.processed.**', 'access_type': PubSub.API_Client.Publisher}]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'orders.urgent.processed.daily', 'publish')
        self.assertTrue(result.is_ok)
        self.assertEqual(result.matched_pattern, 'orders.*.processed.**')

        result = self.matcher.evaluate(self.client_id, 'orders.bulk.processed.summary.final', 'publish')
        self.assertTrue(result.is_ok)

# ################################################################################################################################

    def test_empty_segments_allowed(self):
        permissions = [{'pattern': 'orders..123', 'access_type': PubSub.API_Client.Publisher}]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'orders..123', 'publish')
        self.assertTrue(result.is_ok)
        self.assertEqual(result.matched_pattern, 'orders..123')

# ################################################################################################################################

    def test_wildcard_matches_empty_segments(self):
        permissions = [{'pattern': 'orders.*.123', 'access_type': PubSub.API_Client.Publisher}]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'orders..123', 'publish')
        self.assertTrue(result.is_ok)
        self.assertEqual(result.matched_pattern, 'orders.*.123')

# ################################################################################################################################

    def test_multi_wildcard_matches_empty_segments(self):
        permissions = [{'pattern': 'orders.**', 'access_type': PubSub.API_Client.Publisher}]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'orders..123', 'publish')
        self.assertTrue(result.is_ok)
        self.assertEqual(result.matched_pattern, 'orders.**')

# ################################################################################################################################

    def test_special_characters_treated_literally(self):
        permissions = [{'pattern': 'orders-2024', 'access_type': PubSub.API_Client.Publisher}]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'orders-2024', 'publish')
        self.assertTrue(result.is_ok)
        self.assertEqual(result.matched_pattern, 'orders-2024')

# ################################################################################################################################

    def test_double_wildcard_at_end_matches_multiple_segments(self):
        permissions = [{'pattern': 'orders.**', 'access_type': PubSub.API_Client.Publisher}]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'orders.urgent', 'publish')
        self.assertTrue(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'orders.urgent.high', 'publish')
        self.assertTrue(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'orders.urgent.high.priority', 'publish')
        self.assertTrue(result.is_ok)

# ################################################################################################################################

    def test_double_wildcard_in_middle_of_pattern(self):
        permissions = [{'pattern': 'orders.**.new', 'access_type': PubSub.API_Client.Publisher}]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'orders.new', 'publish')
        self.assertTrue(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'orders.urgent.new', 'publish')
        self.assertTrue(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'orders.urgent.high.new', 'publish')
        self.assertTrue(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'orders.a.b.c.d.new', 'publish')
        self.assertTrue(result.is_ok)

# ################################################################################################################################

    def test_overlapping_patterns_exact_before_wildcards(self):
        permissions = [
            {'pattern': 'orders.*', 'access_type': PubSub.API_Client.Publisher},
            {'pattern': 'orders.urgent', 'access_type': PubSub.API_Client.Publisher}
        ]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'orders.urgent', 'publish')
        self.assertTrue(result.is_ok)
        self.assertEqual(result.matched_pattern, 'orders.urgent')

# ################################################################################################################################

    def test_case_insensitive_matching(self):
        permissions = [{'pattern': 'Orders.Processed', 'access_type': PubSub.API_Client.Publisher}]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'orders.processed', 'publish')
        self.assertTrue(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'ORDERS.PROCESSED', 'publish')
        self.assertTrue(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'Orders.Processed', 'publish')
        self.assertTrue(result.is_ok)

# ################################################################################################################################

    def test_alphabetical_evaluation_order(self):
        permissions = [
            {'pattern': 'transaction.priority', 'access_type': PubSub.API_Client.Publisher},
            {'pattern': 'transaction.*', 'access_type': PubSub.API_Client.Publisher},
            {'pattern': 'transaction.**.processed', 'access_type': PubSub.API_Client.Publisher},
            {'pattern': 'transaction.international', 'access_type': PubSub.API_Client.Publisher}
        ]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'transaction.international', 'publish')
        self.assertTrue(result.is_ok)
        self.assertEqual(result.matched_pattern, 'transaction.international')

        result = self.matcher.evaluate(self.client_id, 'transaction.domestic', 'publish')
        self.assertTrue(result.is_ok)
        self.assertEqual(result.matched_pattern, 'transaction.*')

        result = self.matcher.evaluate(self.client_id, 'transaction.wire.processed', 'publish')
        self.assertTrue(result.is_ok)
        self.assertEqual(result.matched_pattern, 'transaction.**.processed')

# ################################################################################################################################

    def test_publish_vs_subscribe_permissions(self):
        permissions = [
            {'pattern': 'commands.user.**', 'access_type': PubSub.API_Client.Publisher},
            {'pattern': 'events.user.*', 'access_type': PubSub.API_Client.Subscriber},
            {'pattern': 'notifications.user.email', 'access_type': PubSub.API_Client.Subscriber}
        ]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'commands.user.create', 'publish')
        self.assertTrue(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'commands.user.create', 'subscribe')
        self.assertFalse(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'events.user.created', 'subscribe')
        self.assertTrue(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'events.user.created', 'publish')
        self.assertFalse(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'commands.user.create', 'subscribe')
        self.assertFalse(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'events.user.login', 'subscribe')
        self.assertTrue(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'events.user.login', 'publish')
        self.assertFalse(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'notifications.user.email', 'subscribe')
        self.assertTrue(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'notifications.user.email', 'publish')
        self.assertFalse(result.is_ok)

# ################################################################################################################################

    def test_publisher_subscriber_permissions(self):
        permissions = [
            {'pattern': 'bidirectional.**', 'access_type': PubSub.API_Client.Publisher_Subscriber}
        ]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'bidirectional.messages', 'publish')
        self.assertTrue(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'bidirectional.messages', 'subscribe')
        self.assertTrue(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'bidirectional.events.user', 'publish')
        self.assertTrue(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'bidirectional.events.user', 'subscribe')
        self.assertTrue(result.is_ok)

# ################################################################################################################################

    def test_client_not_found(self):
        result = self.matcher.evaluate('nonexistent_client', 'orders.processed', 'publish')
        self.assertFalse(result.is_ok)
        self.assertEqual(result.reason, 'Client not found')

# ################################################################################################################################

    def test_invalid_operation(self):
        permissions = [{'pattern': 'orders.*', 'access_type': PubSub.API_Client.Publisher}]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'orders.processed', 'invalid_op')
        self.assertFalse(result.is_ok)
        self.assertEqual(result.reason, 'Invalid operation: invalid_op')

# ################################################################################################################################

    def test_no_matching_pattern(self):
        permissions = [{'pattern': 'orders.*', 'access_type': PubSub.API_Client.Publisher}]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'inventory.low', 'publish')
        self.assertFalse(result.is_ok)
        self.assertEqual(result.reason, 'No matching pattern found')

# ################################################################################################################################

    def test_rename_topic(self):
        permissions = [{'pattern': 'old.topic.name', 'access_type': PubSub.API_Client.Publisher}]
        self.matcher.add_client(self.client_id, permissions)

        # Verify original pattern works
        result = self.matcher.evaluate(self.client_id, 'old.topic.name', 'publish')
        self.assertTrue(result.is_ok)

        # Update pattern
        self.matcher.rename_topic(self.client_id, 'old.topic.name', 'new.topic.name')

        # Verify old pattern no longer works
        result = self.matcher.evaluate(self.client_id, 'old.topic.name', 'publish')
        self.assertFalse(result.is_ok)

        # Verify new pattern works
        result = self.matcher.evaluate(self.client_id, 'new.topic.name', 'publish')
        self.assertTrue(result.is_ok)

# ################################################################################################################################

    def test_rename_topic_wildcard_patterns_unchanged(self):
        permissions = [
            {'pattern': 'exact.topic', 'access_type': PubSub.API_Client.Publisher},
            {'pattern': 'wildcard.*', 'access_type': PubSub.API_Client.Publisher}
        ]
        self.matcher.add_client(self.client_id, permissions)

        # Update only affects exact patterns
        self.matcher.rename_topic(self.client_id, 'exact.topic', 'renamed.topic')

        # Wildcard pattern should still work
        result = self.matcher.evaluate(self.client_id, 'wildcard.test', 'publish')
        self.assertTrue(result.is_ok)

        # Old exact pattern should not work
        result = self.matcher.evaluate(self.client_id, 'exact.topic', 'publish')
        self.assertFalse(result.is_ok)

        # New exact pattern should work
        result = self.matcher.evaluate(self.client_id, 'renamed.topic', 'publish')
        self.assertTrue(result.is_ok)

# ################################################################################################################################

    def test_delete_topic(self):
        permissions = [{'pattern': 'topic.to.remove', 'access_type': PubSub.API_Client.Publisher}]
        self.matcher.add_client(self.client_id, permissions)

        # Verify pattern works initially
        result = self.matcher.evaluate(self.client_id, 'topic.to.remove', 'publish')
        self.assertTrue(result.is_ok)

        # Remove pattern
        self.matcher.delete_topic(self.client_id, 'topic.to.remove')

        # Verify pattern no longer works
        result = self.matcher.evaluate(self.client_id, 'topic.to.remove', 'publish')
        self.assertFalse(result.is_ok)
        self.assertEqual(result.reason, 'No matching pattern found')

# ################################################################################################################################

    def test_delete_topic_wildcard_patterns_unchanged(self):
        permissions = [
            {'pattern': 'exact.topic', 'access_type': PubSub.API_Client.Publisher},
            {'pattern': 'wildcard.*', 'access_type': PubSub.API_Client.Publisher}
        ]
        self.matcher.add_client(self.client_id, permissions)

        # Remove only affects exact patterns
        self.matcher.delete_topic(self.client_id, 'exact.topic')

        # Wildcard pattern should still work
        result = self.matcher.evaluate(self.client_id, 'wildcard.test', 'publish')
        self.assertTrue(result.is_ok)

        # Exact pattern should not work
        result = self.matcher.evaluate(self.client_id, 'exact.topic', 'publish')
        self.assertFalse(result.is_ok)

# ################################################################################################################################

    def test_pattern_evaluation_order_exact_before_wildcards(self):
        permissions = [
            {'pattern': 'alerts.**', 'access_type': PubSub.API_Client.Publisher},
            {'pattern': 'alerts.critical', 'access_type': PubSub.API_Client.Publisher},
            {'pattern': 'orders.*', 'access_type': PubSub.API_Client.Publisher},
            {'pattern': 'orders.urgent', 'access_type': PubSub.API_Client.Publisher}
        ]
        self.matcher.add_client(self.client_id, permissions)

        # Test that exact patterns are matched before wildcard patterns
        result = self.matcher.evaluate(self.client_id, 'alerts.critical', 'publish')
        self.assertTrue(result.is_ok)
        self.assertEqual(result.matched_pattern, 'alerts.critical')

        result = self.matcher.evaluate(self.client_id, 'orders.urgent', 'publish')
        self.assertTrue(result.is_ok)
        self.assertEqual(result.matched_pattern, 'orders.urgent')

        # Test that wildcard patterns still work for non-exact matches
        result = self.matcher.evaluate(self.client_id, 'alerts.warning', 'publish')
        self.assertTrue(result.is_ok)
        self.assertEqual(result.matched_pattern, 'alerts.**')

        result = self.matcher.evaluate(self.client_id, 'orders.processed', 'publish')
        self.assertTrue(result.is_ok)
        self.assertEqual(result.matched_pattern, 'orders.*')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
