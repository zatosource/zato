# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.pubsub.matcher import PatternMatcher

# ################################################################################################################################
# ################################################################################################################################

class PatternMatcherTestCase(TestCase):

    def setUp(self):
        self.matcher = PatternMatcher()
        self.client_id = 'test_client'

# ################################################################################################################################

    def test_exact_match_patterns(self):
        permissions = [{'pattern': 'orders.processed', 'is_pub': True, 'is_sub': False}]
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
        permissions = [{'pattern': 'orders.*', 'is_pub': True, 'is_sub': False}]
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
        permissions = [{'pattern': 'orders.**', 'is_pub': True, 'is_sub': False}]
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
        permissions = [{'pattern': '*.orders', 'is_pub': True, 'is_sub': False}]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'urgent.orders', 'publish')
        self.assertTrue(result.is_ok)
        self.assertEqual(result.matched_pattern, '*.orders')

        result = self.matcher.evaluate(self.client_id, 'daily.orders', 'publish')
        self.assertTrue(result.is_ok)

# ################################################################################################################################

    def test_mixed_wildcards_in_pattern(self):
        permissions = [{'pattern': 'orders.*.processed.**', 'is_pub': True, 'is_sub': False}]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'orders.urgent.processed.daily', 'publish')
        self.assertTrue(result.is_ok)
        self.assertEqual(result.matched_pattern, 'orders.*.processed.**')

        result = self.matcher.evaluate(self.client_id, 'orders.bulk.processed.summary.final', 'publish')
        self.assertTrue(result.is_ok)

# ################################################################################################################################

    def test_empty_segments_allowed(self):
        permissions = [{'pattern': 'orders..123', 'is_pub': True, 'is_sub': False}]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'orders..123', 'publish')
        self.assertTrue(result.is_ok)
        self.assertEqual(result.matched_pattern, 'orders..123')

# ################################################################################################################################

    def test_wildcard_matches_empty_segments(self):
        permissions = [{'pattern': 'orders.*.123', 'is_pub': True, 'is_sub': False}]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'orders..123', 'publish')
        self.assertTrue(result.is_ok)
        self.assertEqual(result.matched_pattern, 'orders.*.123')

# ################################################################################################################################

    def test_multi_wildcard_matches_empty_segments(self):
        permissions = [{'pattern': 'orders.**', 'is_pub': True, 'is_sub': False}]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'orders..123', 'publish')
        self.assertTrue(result.is_ok)
        self.assertEqual(result.matched_pattern, 'orders.**')

# ################################################################################################################################

    def test_special_characters_treated_literally(self):
        permissions = [{'pattern': 'orders-2024', 'is_pub': True, 'is_sub': False}]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'orders-2024', 'publish')
        self.assertTrue(result.is_ok)
        self.assertEqual(result.matched_pattern, 'orders-2024')

# ################################################################################################################################

    def test_double_wildcard_at_end_matches_multiple_segments(self):
        permissions = [{'pattern': 'orders.**', 'is_pub': True, 'is_sub': False}]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'orders.urgent', 'publish')
        self.assertTrue(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'orders.urgent.high', 'publish')
        self.assertTrue(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'orders.urgent.high.priority', 'publish')
        self.assertTrue(result.is_ok)

# ################################################################################################################################

    def test_double_wildcard_in_middle_of_pattern(self):
        permissions = [{'pattern': 'orders.**.new', 'is_pub': True, 'is_sub': False}]
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
            {'pattern': 'orders.*', 'is_pub': True, 'is_sub': False},
            {'pattern': 'orders.urgent', 'is_pub': True, 'is_sub': False}
        ]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'orders.urgent', 'publish')
        self.assertTrue(result.is_ok)
        self.assertEqual(result.matched_pattern, 'orders.urgent')

# ################################################################################################################################

    def test_case_insensitive_matching(self):
        permissions = [{'pattern': 'Orders.Processed', 'is_pub': True, 'is_sub': False}]
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
            {'pattern': 'transaction.priority', 'is_pub': True, 'is_sub': False},
            {'pattern': 'transaction.*', 'is_pub': True, 'is_sub': False},
            {'pattern': 'transaction.**.processed', 'is_pub': True, 'is_sub': False},
            {'pattern': 'transaction.international', 'is_pub': True, 'is_sub': False}
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
            {'pattern': 'commands.user.**', 'is_pub': True, 'is_sub': False},
            {'pattern': 'events.user.*', 'is_pub': False, 'is_sub': True},
            {'pattern': 'notifications.user.email', 'is_pub': False, 'is_sub': True}
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

# ################################################################################################################################

    def test_client_not_found(self):
        result = self.matcher.evaluate('nonexistent_client', 'orders.processed', 'publish')
        self.assertFalse(result.is_ok)
        self.assertEqual(result.reason, 'Client not found')

# ################################################################################################################################

    def test_invalid_operation(self):
        permissions = [{'pattern': 'orders.*', 'is_pub': True, 'is_sub': False}]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'orders.processed', 'invalid_op')
        self.assertFalse(result.is_ok)
        self.assertEqual(result.reason, 'Invalid operation: invalid_op')

# ################################################################################################################################

    def test_no_matching_pattern(self):
        permissions = [{'pattern': 'orders.*', 'is_pub': True, 'is_sub': False}]
        self.matcher.add_client(self.client_id, permissions)

        result = self.matcher.evaluate(self.client_id, 'inventory.low', 'publish')
        self.assertFalse(result.is_ok)
        self.assertEqual(result.reason, 'No matching pattern found')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
