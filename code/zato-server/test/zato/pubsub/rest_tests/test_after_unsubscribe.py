# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
from base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

class TestAfterUnsubscribe(BaseTestCase):

    def test_get_messages_after_unsubscribe(self):
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Subscribe should succeed')
        sub_key = result.get('sub_key')

        result = client.publish(topic, 'test message')
        self.assertTrue(result.get('is_ok'), 'Publish should succeed')

        result = client.unsubscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Unsubscribe should succeed')

        result = client.get_messages(sub_key)
        messages = result.get('messages', [])
        message_count = result.get('message_count', 0)

        if isinstance(messages, str):
            messages = []
        self.assertTrue(message_count == 0 or len(messages) == 0,
            'Get messages after unsubscribe should return empty')

# ################################################################################################################################
# ################################################################################################################################
