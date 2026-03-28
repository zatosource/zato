# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
from .base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

class TestAfterUnsubscribe(BaseTestCase):

    def run(self):
        client = self.get_client()
        topic = self.config.topic_allowed

        print('1. Subscribe to topic')
        result = client.subscribe(topic)
        self.assert_true(result.get('is_ok'), 'Subscribe should succeed')
        sub_key = result.get('sub_key')

        print('2. Publish message')
        result = client.publish(topic, 'test message')
        self.assert_true(result.get('is_ok'), 'Publish should succeed')

        print('3. Unsubscribe')
        result = client.unsubscribe(topic)
        self.assert_true(result.get('is_ok'), 'Unsubscribe should succeed')

        print('4. Get messages after unsubscribe (should return empty or no sub_key)')
        result = client.get_messages(sub_key)
        messages = result.get('messages', [])
        message_count = result.get('message_count', 0)

        if isinstance(messages, str):
            messages = []
        self.assert_true(message_count == 0 or len(messages) == 0,
            'Get messages after unsubscribe should return empty')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    import sys
    test = TestAfterUnsubscribe()
    success = test.execute()
    sys.exit(0 if success else 1)
