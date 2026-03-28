# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
from base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

class TestBasicFlow(BaseTestCase):

    def run(self):
        client = self.get_client()
        topic = self.config.topic_allowed

        print('1. Publish message before subscribe')
        result = client.publish(topic, 'message before subscribe')
        self.assert_true(result.get('is_ok'), 'Publish before subscribe should succeed')
        self.assert_true(result.get('msg_id'), 'Publish should return msg_id')

        print('2. Subscribe to topic')
        result = client.subscribe(topic)
        self.assert_true(result.get('is_ok'), 'Subscribe should succeed')
        self.assert_true(result.get('sub_key'), 'Subscribe should return sub_key')

        print('3. Publish message after subscribe')
        result = client.publish(topic, 'message after subscribe')
        self.assert_true(result.get('is_ok'), 'Publish after subscribe should succeed')

        print('4. Get messages')
        result = client.get_messages()
        self.assert_true(result.get('is_ok'), 'Get messages should succeed')
        self.assert_true('message after subscribe' in str(result.get('messages', '')),
            'Should receive message published after subscribe')

        print('5. Unsubscribe')
        result = client.unsubscribe(topic)
        self.assert_true(result.get('is_ok'), 'Unsubscribe should succeed')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    import sys
    test = TestBasicFlow()
    success = test.execute()
    sys.exit(0 if success else 1)
