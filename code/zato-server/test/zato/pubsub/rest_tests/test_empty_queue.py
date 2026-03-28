# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
from base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

class TestEmptyQueue(BaseTestCase):

    def test_get_messages_empty_queue(self):
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Subscribe should succeed')

        result = client.get_messages()

        result = client.get_messages()

        self.assertTrue(result.get('is_ok'), 'Get messages should succeed')
        self.assertEqual(result.get('message_count', -1), 0, 'Message count should be 0')

        messages = result.get('messages', None)
        self.assertIsNotNone(messages, 'Messages field should exist')
        self.assertEqual(len(messages), 0, 'Messages array should be empty')

        client.unsubscribe(topic)

# ################################################################################################################################
# ################################################################################################################################
