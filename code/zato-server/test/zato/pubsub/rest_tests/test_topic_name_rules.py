# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
from base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

class TestTopicNameRules(BaseTestCase):

    def test_non_ascii_topic_name_rejected(self) -> 'None':
        """ Test that non-ASCII topic names are rejected.
        """
        client = self.get_client()
        topic = 'demo.тест'

        result = client.publish(topic, 'test message')
        self.assertFalse(result.get('is_ok'), 'Non-ASCII topic name should be rejected')

# ################################################################################################################################

    def test_case_insensitive_topic_names(self) -> 'None':
        """ Test that topic names are case-insensitive.
        """
        client = self.get_client()
        topic_lower = 'demo.1'
        topic_upper = 'DEMO.1'

        result = client.subscribe(topic_lower)
        self.assertTrue(result.get('is_ok'), 'Subscribe to lowercase topic should succeed')

        result = client.publish(topic_upper, 'test message')
        self.assertTrue(result.get('is_ok'), 'Publish to uppercase topic should succeed')

        result = client.get_messages()
        self.assertTrue(result.get('is_ok'), 'Get messages should succeed')

        messages = result.get('messages', [])
        self.assertGreaterEqual(len(messages), 1, 'Should receive message from case-insensitive topic')

        client.unsubscribe(topic_lower)

# ################################################################################################################################
# ################################################################################################################################
