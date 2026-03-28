# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
from base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

class TestMaxMessages(BaseTestCase):

    def test_max_messages_limit(self):
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Subscribe should succeed')

        for i in range(10):
            result = client.publish(topic, f'message {i}')
            self.assertTrue(result.get('is_ok'), f'Publish message {i} should succeed')

        result = client.get_messages_with_limit(max_messages=3)
        self.assertTrue(result.get('is_ok'), 'Get messages should succeed')

        message_count = result.get('message_count', 0)
        self.assertEqual(message_count, 3, 'Should return exactly 3 messages')

        result = client.get_messages()
        remaining_count = result.get('message_count', 0)
        self.assertEqual(remaining_count, 7, 'Should have 7 remaining messages')

        client.unsubscribe(topic)

    def test_max_messages_more_than_available(self):
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Subscribe should succeed')

        for i in range(3):
            result = client.publish(topic, f'message {i}')
            self.assertTrue(result.get('is_ok'), f'Publish message {i} should succeed')

        result = client.get_messages_with_limit(max_messages=100)
        self.assertTrue(result.get('is_ok'), 'Get messages should succeed')

        message_count = result.get('message_count', 0)
        self.assertEqual(message_count, 3, 'Should return all 3 available messages')

        client.unsubscribe(topic)

# ################################################################################################################################
# ################################################################################################################################
