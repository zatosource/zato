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

class PatternMatcherMiscTestCase(TestCase):

    def setUp(self):
        self.matcher = PatternMatcher()
        self.client_id = 'test-client-123'

# ################################################################################################################################

    def test_regex_dos_nested_wildcards(self):
        """Test potential regex DoS with nested wildcards"""
        permissions = [{'pattern': '**.**.**.**', 'access_type': PubSub.API_Client.Publisher}]
        self.matcher.add_client(self.client_id, permissions)

        # Should not hang or crash
        result = self.matcher.evaluate(self.client_id, 'a.b.c.d.e.f.g.h', 'publish')
        self.assertTrue(result.is_ok)

# ################################################################################################################################

    def test_case_sensitivity_bypass_reserved_names(self):
        """Test case variations of reserved names"""
        reserved_patterns = ['ZaTo.admin.**', 'zato.admin.**', 'ZPSK.secret.**', 'zpsk.secret.**']

        for pattern in reserved_patterns:
            permissions = [{'pattern': pattern, 'access_type': PubSub.API_Client.Publisher}]
            with self.assertRaises(ValueError, msg=f'Should reject reserved pattern: {pattern}'):
                self.matcher.add_client(self.client_id, permissions)

# ################################################################################################################################

    def test_unicode_homograph_attacks(self):
        """Test non-ASCII characters are rejected"""
        # Non-ASCII patterns that should be rejected
        non_ascii_patterns = [
            'ᴢᴀᴛᴏ.admin.**',  # Small caps
            'ᴢᴘsᴋ.secret.**',  # Small caps
            'zato​.admin.**',  # Zero-width space
            'tëst.admin.**'   # Accented character
        ]

        for pattern in non_ascii_patterns:
            permissions = [{'pattern': pattern, 'access_type': PubSub.API_Client.Publisher}]
            with self.assertRaises(ValueError, msg=f'Should reject non-ASCII pattern: {pattern}'):
                self.matcher.add_client(self.client_id, permissions)

# ################################################################################################################################

    def test_wildcard_boundary_exploitation(self):
        """Test wildcard boundary conditions"""
        permissions = [{'pattern': '**.admin.**', 'access_type': PubSub.API_Client.Publisher}]
        self.matcher.add_client(self.client_id, permissions)

        # Test various boundary cases
        boundary_topics = [
            '.admin.',
            'admin.',
            '.admin',
            '..admin..',
            'prefix.admin.suffix',
            'admin'
        ]

        for topic in boundary_topics:
            result = self.matcher.evaluate(self.client_id, topic, 'publish')
            self.assertTrue(isinstance(result.is_ok, bool), f"Boundary test failed for: {topic}") # type: ignore

# ################################################################################################################################

    def test_regex_special_chars_in_topics(self):
        """Test regex special characters in topic names"""
        permissions = [{'pattern': 'admin.*', 'access_type': PubSub.API_Client.Publisher}]
        self.matcher.add_client(self.client_id, permissions)

        # Topics with regex special chars - should be treated literally
        special_topics = [
            'admin.[test]',
            'admin.(test)',
            'admin.test+',
            'admin.test*',
            'admin.test?',
            'admin.test^',
            'admin.test$',
            'admin.test|'
        ]

        for topic in special_topics:
            result = self.matcher.evaluate(self.client_id, topic, 'publish')
            self.assertTrue(result.is_ok, f"Special char topic should match: {topic}")

# ################################################################################################################################

    def test_empty_segment_abuse(self):
        """Test empty segment manipulation"""
        permissions = [
            {'pattern': 'admin.*.secret', 'access_type': PubSub.API_Client.Publisher},
            {'pattern': 'admin..secret', 'access_type': PubSub.API_Client.Subscriber}
        ]
        self.matcher.add_client(self.client_id, permissions)

        # Empty segment should match wildcard
        result = self.matcher.evaluate(self.client_id, 'admin..secret', 'publish')
        self.assertTrue(result.is_ok)

        # Should also match exact empty pattern for subscribe
        result = self.matcher.evaluate(self.client_id, 'admin..secret', 'subscribe')
        self.assertTrue(result.is_ok)

# ################################################################################################################################

    def test_permission_escalation_overlapping(self):
        """Test permission escalation through overlapping patterns"""
        permissions = [
            {'pattern': 'admin.*', 'access_type': PubSub.API_Client.Subscriber},  # Less privilege
            {'pattern': 'admin.delete', 'access_type': PubSub.API_Client.Publisher}  # More privilege
        ]
        self.matcher.add_client(self.client_id, permissions)

        # Exact pattern should take precedence (publisher permission)
        result = self.matcher.evaluate(self.client_id, 'admin.delete', 'publish')
        self.assertTrue(result.is_ok)

        # Should have subscribe permission via wildcard pattern
        result = self.matcher.evaluate(self.client_id, 'admin.delete', 'subscribe')
        self.assertTrue(result.is_ok)

# ################################################################################################################################

    def test_long_topic_names(self):
        """Test very long topic names"""
        permissions = [{'pattern': 'test.**', 'access_type': PubSub.API_Client.Publisher}]
        self.matcher.add_client(self.client_id, permissions)

        # Very long topic name
        long_segment = 'a' * 1000
        long_topic = f'test.{long_segment}.end'

        result = self.matcher.evaluate(self.client_id, long_topic, 'publish')
        self.assertTrue(result.is_ok)

# ################################################################################################################################

    def test_publisher_subscriber(self):
        """Test Publisher_Subscriber permission abuse"""
        permissions = [
            {'pattern': 'restricted.admin.**', 'access_type': PubSub.API_Client.Publisher_Subscriber}
        ]
        self.matcher.add_client(self.client_id, permissions)

        # Should have both publish and subscribe permissions
        result = self.matcher.evaluate(self.client_id, 'restricted.admin.delete', 'publish')
        self.assertTrue(result.is_ok)

        result = self.matcher.evaluate(self.client_id, 'restricted.admin.delete', 'subscribe')
        self.assertTrue(result.is_ok)

# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
