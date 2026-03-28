# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
from base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

class TestPubTime(BaseTestCase):

    def test_custom_pub_time_preserved(self) -> 'None':
        """ Test that custom pub_time is preserved in message metadata.
        """
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Subscribe should succeed')

        custom_pub_time = '2025-01-01T12:00:00+00:00'
        result = client.publish_with_pub_time(topic, 'test message', custom_pub_time)
        self.assertTrue(result.get('is_ok'), 'Publish with pub_time should succeed')

        result = client.get_messages()
        self.assertTrue(result.get('is_ok'), 'Get messages should succeed')

        messages = result.get('messages', [])
        self.assertGreaterEqual(len(messages), 1, 'Should have at least 1 message')

        meta = messages[0].get('meta', {})
        self.assertEqual(meta.get('pub_time_iso'), custom_pub_time)

        client.unsubscribe(topic)

# ################################################################################################################################
# ################################################################################################################################
