# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# local
from base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

class TestMetaFields(BaseTestCase):

    def test_topic_name_in_meta(self) -> 'None':
        """ Test that topic_name is present in message metadata.
        """
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Subscribe should succeed')

        result = client.publish(topic, 'test message')
        self.assertTrue(result.get('is_ok'), 'Publish should succeed')

        result = client.get_messages()
        self.assertTrue(result.get('is_ok'), 'Get messages should succeed')

        messages = result.get('messages', [])
        self.assertGreaterEqual(len(messages), 1, 'Should have at least 1 message')

        meta = messages[0].get('meta', {})
        self.assertEqual(meta.get('topic_name'), topic)

        client.unsubscribe(topic)

# ################################################################################################################################

    def test_size_in_meta(self) -> 'None':
        """ Test that size is present in message metadata.
        """
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Subscribe should succeed')

        test_data = 'test message 12345'
        result = client.publish(topic, test_data)
        self.assertTrue(result.get('is_ok'), 'Publish should succeed')

        result = client.get_messages()
        self.assertTrue(result.get('is_ok'), 'Get messages should succeed')

        messages = result.get('messages', [])
        self.assertGreaterEqual(len(messages), 1, 'Should have at least 1 message')

        meta = messages[0].get('meta', {})
        self.assertEqual(meta.get('size'), len(test_data))

        client.unsubscribe(topic)

# ################################################################################################################################

    def test_msg_id_in_meta(self) -> 'None':
        """ Test that msg_id is present in message metadata.
        """
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Subscribe should succeed')

        result = client.publish(topic, 'test message')
        self.assertTrue(result.get('is_ok'), 'Publish should succeed')
        published_msg_id = result.get('msg_id')

        result = client.get_messages()
        self.assertTrue(result.get('is_ok'), 'Get messages should succeed')

        messages = result.get('messages', [])
        self.assertGreaterEqual(len(messages), 1, 'Should have at least 1 message')

        meta = messages[0].get('meta', {})
        self.assertIsNotNone(meta.get('msg_id'))
        self.assertEqual(meta.get('msg_id'), published_msg_id)

        client.unsubscribe(topic)

# ################################################################################################################################

    def test_expiration_in_meta(self) -> 'None':
        """ Test that expiration is present in message metadata.
        """
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Subscribe should succeed')

        expiration = 3600
        result = client.publish_with_expiration(topic, 'test message', expiration)
        self.assertTrue(result.get('is_ok'), 'Publish should succeed')

        result = client.get_messages()
        self.assertTrue(result.get('is_ok'), 'Get messages should succeed')

        messages = result.get('messages', [])
        self.assertGreaterEqual(len(messages), 1, 'Should have at least 1 message')

        meta = messages[0].get('meta', {})
        self.assertEqual(meta.get('expiration'), expiration)

        client.unsubscribe(topic)

# ################################################################################################################################

    def test_pub_time_iso_in_meta(self) -> 'None':
        """ Test that pub_time_iso is present in message metadata.
        """
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Subscribe should succeed')

        result = client.publish(topic, 'test message')
        self.assertTrue(result.get('is_ok'), 'Publish should succeed')

        result = client.get_messages()
        self.assertTrue(result.get('is_ok'), 'Get messages should succeed')

        messages = result.get('messages', [])
        self.assertGreaterEqual(len(messages), 1, 'Should have at least 1 message')

        meta = messages[0].get('meta', {})
        pub_time_iso = meta.get('pub_time_iso')
        self.assertIsNotNone(pub_time_iso)
        self.assertIn('T', pub_time_iso)

        client.unsubscribe(topic)

# ################################################################################################################################

    def test_recv_time_iso_in_meta(self) -> 'None':
        """ Test that recv_time_iso is present in message metadata.
        """
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Subscribe should succeed')

        result = client.publish(topic, 'test message')
        self.assertTrue(result.get('is_ok'), 'Publish should succeed')

        result = client.get_messages()
        self.assertTrue(result.get('is_ok'), 'Get messages should succeed')

        messages = result.get('messages', [])
        self.assertGreaterEqual(len(messages), 1, 'Should have at least 1 message')

        meta = messages[0].get('meta', {})
        recv_time_iso = meta.get('recv_time_iso')
        self.assertIsNotNone(recv_time_iso)
        self.assertIn('T', recv_time_iso)

        client.unsubscribe(topic)

# ################################################################################################################################

    def test_expiration_time_iso_in_meta(self) -> 'None':
        """ Test that expiration_time_iso is present in message metadata.
        """
        client = self.get_client()
        topic = self.config.topic_allowed

        result = client.subscribe(topic)
        self.assertTrue(result.get('is_ok'), 'Subscribe should succeed')

        result = client.publish(topic, 'test message')
        self.assertTrue(result.get('is_ok'), 'Publish should succeed')

        result = client.get_messages()
        self.assertTrue(result.get('is_ok'), 'Get messages should succeed')

        messages = result.get('messages', [])
        self.assertGreaterEqual(len(messages), 1, 'Should have at least 1 message')

        meta = messages[0].get('meta', {})
        expiration_time_iso = meta.get('expiration_time_iso')
        self.assertIsNotNone(expiration_time_iso)
        self.assertIn('T', expiration_time_iso)

        client.unsubscribe(topic)

# ################################################################################################################################
# ################################################################################################################################
