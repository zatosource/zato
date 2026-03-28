# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# local
from base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

class TestMessageExpiration(BaseTestCase):

    def test_expired_message_not_delivered(self):
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Subscribe should succeed')

        result = client.publish_with_expiration(topic, 'expiring message', expiration=1)
        self.assertTrue(result.get('is_ok'), 'Publish with expiration should succeed')

        time.sleep(2)

        result = client.get_messages()
        self.assertTrue(result.get('is_ok'), 'Get messages should succeed')

        message_count = result.get('message_count', 0)
        self.assertEqual(message_count, 0, 'Expired message should not be delivered')

        client.unsubscribe(topic)

    def test_non_expired_message_delivered(self):
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Subscribe should succeed')

        result = client.publish_with_expiration(topic, 'long lived message', expiration=3600)
        self.assertTrue(result.get('is_ok'), 'Publish with expiration should succeed')

        result = client.get_messages()
        self.assertTrue(result.get('is_ok'), 'Get messages should succeed')

        message_count = result.get('message_count', 0)
        self.assertGreaterEqual(message_count, 1, 'Non-expired message should be delivered')

        client.unsubscribe(topic)

# ################################################################################################################################
# ################################################################################################################################
