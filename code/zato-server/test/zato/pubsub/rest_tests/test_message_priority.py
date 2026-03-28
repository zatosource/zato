# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
from base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

class TestMessagePriority(BaseTestCase):

    def test_higher_priority_delivered_first(self):
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Subscribe should succeed')

        result = client.publish_with_priority(topic, 'low priority message', priority=1)
        self.assertTrue(result.get('is_ok'), 'Publish low priority should succeed')

        result = client.publish_with_priority(topic, 'high priority message', priority=9)
        self.assertTrue(result.get('is_ok'), 'Publish high priority should succeed')

        result = client.publish_with_priority(topic, 'medium priority message', priority=5)
        self.assertTrue(result.get('is_ok'), 'Publish medium priority should succeed')

        result = client.get_messages()
        self.assertTrue(result.get('is_ok'), 'Get messages should succeed')

        messages = result.get('messages', [])
        self.assertGreaterEqual(len(messages), 3, 'Should have at least 3 messages')

        first_data = messages[0].get('data', '')
        self.assertIn('high priority', first_data)

        client.unsubscribe(topic)

# ################################################################################################################################
# ################################################################################################################################
