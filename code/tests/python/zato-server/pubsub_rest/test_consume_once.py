# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
from base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

class TestConsumeOnce(BaseTestCase):

    def test_messages_consumed_only_once(self):
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Subscribe should succeed')

        for i in range(3):
            result = client.publish(topic, f'message {i}')
            self.assertTrue(result.get('is_ok'), f'Publish message {i} should succeed')

        result = client.get_messages()
        self.assertTrue(result.get('is_ok'), 'First get messages should succeed')
        first_count = result.get('message_count', 0)
        self.assertGreaterEqual(first_count, 3, f'Should have at least 3 messages, got {first_count}')

        result = client.get_messages()
        self.assertTrue(result.get('is_ok'), 'Second get messages should succeed')
        second_count = result.get('message_count', 0)
        self.assertEqual(second_count, 0, 'Second get should return 0 messages (already consumed)')

        client.unsubscribe(topic)

# ################################################################################################################################
# ################################################################################################################################
