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

    def test_publish_subscribe_flow(self):
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.publish(topic, 'message before subscribe')
        self.assertTrue(result.get('is_ok'), 'Publish before subscribe should succeed')
        self.assertTrue(result.get('msg_id'), 'Publish should return msg_id')

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Subscribe should succeed')
        self.assertTrue(result.get('sub_key'), 'Subscribe should return sub_key')

        result = client.publish(topic, 'message after subscribe')
        self.assertTrue(result.get('is_ok'), 'Publish after subscribe should succeed')

        result = client.get_messages()
        self.assertTrue(result.get('is_ok'), 'Get messages should succeed')
        self.assertIn('message after subscribe', str(result.get('messages', '')))

        result = client.unsubscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Unsubscribe should succeed')

# ################################################################################################################################
# ################################################################################################################################
