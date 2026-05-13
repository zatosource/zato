# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
from base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

class TestMessageMetadata(BaseTestCase):

    def test_correl_id_preserved(self):
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Subscribe should succeed')

        correl_id = 'test-correlation-123'
        result = client.publish_with_metadata(topic, 'test message', correl_id=correl_id)
        self.assertTrue(result.get('is_ok'), 'Publish with correl_id should succeed')

        result = client.get_messages()
        self.assertTrue(result.get('is_ok'), 'Get messages should succeed')

        messages = result.get('messages', [])
        self.assertGreaterEqual(len(messages), 1, 'Should have at least 1 message')

        meta = messages[0].get('meta', {})
        self.assertEqual(meta.get('correl_id'), correl_id)

        client.unsubscribe(topic)

    def test_in_reply_to_preserved(self):
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Subscribe should succeed')

        in_reply_to = 'original-msg-456'
        result = client.publish_with_metadata(topic, 'reply message', in_reply_to=in_reply_to)
        self.assertTrue(result.get('is_ok'), 'Publish with in_reply_to should succeed')

        result = client.get_messages()
        self.assertTrue(result.get('is_ok'), 'Get messages should succeed')

        messages = result.get('messages', [])
        self.assertGreaterEqual(len(messages), 1, 'Should have at least 1 message')

        meta = messages[0].get('meta', {})
        self.assertEqual(meta.get('in_reply_to'), in_reply_to)

        client.unsubscribe(topic)

    def test_ext_client_id_preserved(self):
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Subscribe should succeed')

        ext_client_id = 'external-client-789'
        result = client.publish_with_metadata(topic, 'test message', ext_client_id=ext_client_id)
        self.assertTrue(result.get('is_ok'), 'Publish with ext_client_id should succeed')

        result = client.get_messages()
        self.assertTrue(result.get('is_ok'), 'Get messages should succeed')

        messages = result.get('messages', [])
        self.assertGreaterEqual(len(messages), 1, 'Should have at least 1 message')

        meta = messages[0].get('meta', {})
        self.assertEqual(meta.get('ext_client_id'), ext_client_id)

        client.unsubscribe(topic)

# ################################################################################################################################
# ################################################################################################################################
