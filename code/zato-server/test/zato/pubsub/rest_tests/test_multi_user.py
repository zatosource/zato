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

    def test_multi_user_message_isolation(self):
        client1 = self.get_client(self.config.user1_username, self.config.user1_password)
        client2 = self.get_client(self.config.user2_username, self.config.user2_password)
        topic = self.config.topic_allowed

        result = client1.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'User1 subscribe should succeed')

        result = client1.publish(topic, 'message A from user1')
        self.assertTrue(result.get('is_ok'), 'User1 publish should succeed')

        result = client2.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'User2 subscribe should succeed')

        result = client1.publish(topic, 'message B from user1')
        self.assertTrue(result.get('is_ok'), 'User1 publish B should succeed')

        result = client1.get_messages()
        messages_str = str(result.get('messages', ''))
        self.assertIn('message A from user1', messages_str)
        self.assertIn('message B from user1', messages_str)

        result = client2.get_messages()
        messages_str = str(result.get('messages', ''))
        self.assertNotIn('message A from user1', messages_str)
        self.assertIn('message B from user1', messages_str)

        client1.unsubscribe(topic)
        client2.unsubscribe(topic)

# ################################################################################################################################
# ################################################################################################################################
