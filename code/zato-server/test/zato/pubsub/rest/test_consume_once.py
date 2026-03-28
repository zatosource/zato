# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
from .base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

class TestConsumeOnce(BaseTestCase):

    def run(self):
        client = self.get_client()
        topic = self.config.topic_allowed

        print('1. Subscribe to topic')
        result = client.subscribe(topic)
        self.assert_true(result.get('is_ok'), 'Subscribe should succeed')

        print('2. Publish multiple messages')
        for i in range(3):
            result = client.publish(topic, f'message {i}')
            self.assert_true(result.get('is_ok'), f'Publish message {i} should succeed')

        print('3. Get messages (first call)')
        result = client.get_messages()
        self.assert_true(result.get('is_ok'), 'First get messages should succeed')
        first_count = result.get('message_count', 0)
        self.assert_true(first_count >= 3, f'Should have at least 3 messages, got {first_count}')

        print('4. Get messages again (second call - should be empty)')
        result = client.get_messages()
        self.assert_true(result.get('is_ok'), 'Second get messages should succeed')
        second_count = result.get('message_count', 0)
        self.assert_equal(second_count, 0, 'Second get should return 0 messages (already consumed)')

        print('5. Cleanup - unsubscribe')
        client.unsubscribe(topic)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    import sys
    test = TestConsumeOnce()
    success = test.execute()
    sys.exit(0 if success else 1)
