# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
from base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

class TestMultiUser(BaseTestCase):

    def run(self):
        client1 = self.get_client(self.config.user1_username, self.config.user1_password)
        client2 = self.get_client(self.config.user2_username, self.config.user2_password)
        topic = self.config.topic_allowed

        print('1. User1 subscribes')
        result = client1.subscribe(topic)
        self.assert_true(result.get('is_ok'), 'User1 subscribe should succeed')

        print('2. User1 publishes message A')
        result = client1.publish(topic, 'message A from user1')
        self.assert_true(result.get('is_ok'), 'User1 publish should succeed')

        print('3. User2 subscribes')
        result = client2.subscribe(topic)
        self.assert_true(result.get('is_ok'), 'User2 subscribe should succeed')

        print('4. User1 publishes message B')
        result = client1.publish(topic, 'message B from user1')
        self.assert_true(result.get('is_ok'), 'User1 publish B should succeed')

        print('5. User1 gets messages (should have A and B)')
        result = client1.get_messages()
        messages_str = str(result.get('messages', ''))
        self.assert_true('message A from user1' in messages_str, 'User1 should have message A')
        self.assert_true('message B from user1' in messages_str, 'User1 should have message B')

        print('6. User2 gets messages (should only have B)')
        result = client2.get_messages()
        messages_str = str(result.get('messages', ''))
        self.assert_false('message A from user1' in messages_str, 'User2 should NOT have message A')
        self.assert_true('message B from user1' in messages_str, 'User2 should have message B')

        print('7. Cleanup - unsubscribe both users')
        client1.unsubscribe(topic)
        client2.unsubscribe(topic)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    import sys
    test = TestMultiUser()
    success = test.execute()
    sys.exit(0 if success else 1)
