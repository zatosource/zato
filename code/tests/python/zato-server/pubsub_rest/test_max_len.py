# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
from base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

class TestMaxLen(BaseTestCase):

    def test_max_len_limit(self):
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Subscribe should succeed')

        large_message = 'x' * 1000
        for i in range(5):
            result = client.publish(topic, large_message)
            self.assertTrue(result.get('is_ok'), f'Publish message {i} should succeed')

        result = client.get_messages_with_limit(max_len=2500)
        self.assertTrue(result.get('is_ok'), 'Get messages should succeed')

        message_count = result.get('message_count', 0)
        self.assertLessEqual(message_count, 3, 'Should return at most 2-3 messages due to size limit')

        client.get_messages()
        client.unsubscribe(topic)

# ################################################################################################################################
# ################################################################################################################################
