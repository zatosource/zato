# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock

# Zato
from zato.common.pubsub.disk_store import DiskMessageStore
from zato.common.pubsub.redis_backend import PublishResult, RedisPubSubBackend, ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

class TestRedisPubSubBackend(unittest.TestCase):

    def setUp(self) -> 'None':
        self.redis_mock = MagicMock()
        self.test_dir = tempfile.mkdtemp()
        self.disk_store = DiskMessageStore(self.test_dir)
        self.backend = RedisPubSubBackend(self.redis_mock, self.disk_store)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        shutil.rmtree(self.test_dir)

# ################################################################################################################################

    def test_publish_returns_publish_result(self) -> 'None':
        """ Test that publishing returns a PublishResult with msg_id.
        """
        topic_name = 'test.topic'
        data = 'test message'

        result = self.backend.publish(topic_name, data, publisher='testuser')

        self.assertIsInstance(result, PublishResult)
        self.assertIsNotNone(result.msg_id)

        msg_id_len = len(result.msg_id)
        self.assertTrue(msg_id_len > 0)

# ################################################################################################################################

    def test_publish_creates_stream_entry_with_data_ref(self) -> 'None':
        """ Test that publishing a message stores data_ref in the stream entry.
        """
        topic_name = 'test.topic'
        data = 'test message'

        result = self.backend.publish(topic_name, data, publisher='testuser')

        self.redis_mock.xadd.assert_called_once()

        call_args = self.redis_mock.xadd.call_args
        stream_key = call_args[0][0]
        message = call_args[0][1]

        self.assertEqual(stream_key, f'{ModuleCtx.Stream_Prefix}{topic_name}')
        self.assertIn('data_ref', message)
        self.assertIn('data_size', message)
        self.assertIn('data_preview', message)
        self.assertNotIn('data', message)
        self.assertEqual(message['topic_name'], topic_name)
        self.assertEqual(message['publisher'], 'testuser')
        self.assertEqual(message['msg_id'], result.msg_id)

        data_size = message['data_size']
        self.assertEqual(data_size, len(data))

# ################################################################################################################################

    def test_publish_writes_payload_to_disk(self) -> 'None':
        """ Test that publishing writes the payload to a disk file.
        """
        topic_name = 'test.topic'
        data = 'test message payload'

        result = self.backend.publish(topic_name, data, publisher='testuser')

        # .. get the data_ref from the xadd call ..
        call_args = self.redis_mock.xadd.call_args
        message = call_args[0][1]
        data_ref = message['data_ref']

        # .. verify we can load it back from disk ..
        load_result = self.disk_store.load(data_ref)
        self.assertEqual(load_result.data, data)

# ################################################################################################################################

    def test_publish_stores_data_preview(self) -> 'None':
        """ Test that the data preview is stored in Redis.
        """
        topic_name = 'test.topic'
        data = 'A' * 200

        _ = self.backend.publish(topic_name, data, publisher='testuser')

        call_args = self.redis_mock.xadd.call_args
        message = call_args[0][1]

        preview_len = len(message['data_preview'])
        self.assertEqual(preview_len, 100)

# ################################################################################################################################

    def test_subscribe_creates_consumer_group(self) -> 'None':
        """ Test that subscribing creates a consumer group.
        """
        sub_key = 'sub.test123'
        topic_name = 'test.topic'

        self.backend.subscribe(sub_key, topic_name)

        self.assertEqual(self.redis_mock.sadd.call_count, 2)

        self.redis_mock.xgroup_create.assert_called_once()

        call_args = self.redis_mock.xgroup_create.call_args
        stream_key = call_args[0][0]
        group_name = call_args[0][1]

        self.assertEqual(stream_key, f'{ModuleCtx.Stream_Prefix}{topic_name}')
        self.assertEqual(group_name, sub_key)

# ################################################################################################################################

    def test_unsubscribe_removes_from_sets(self) -> 'None':
        """ Test that unsubscribing removes entries from sets.
        """
        sub_key = 'sub.test123'
        topic_name = 'test.topic'

        self.redis_mock.scard.return_value = 1

        self.backend.unsubscribe(sub_key, topic_name)

        self.assertEqual(self.redis_mock.srem.call_count, 2)

        self.redis_mock.xgroup_destroy.assert_not_called()

# ################################################################################################################################

    def test_unsubscribe_last_topic_destroys_consumer_group(self) -> 'None':
        """ Test that unsubscribing from last topic destroys the consumer group.
        """
        sub_key = 'sub.test123'
        topic_name = 'test.topic'

        self.redis_mock.scard.return_value = 0

        self.backend.unsubscribe(sub_key, topic_name)

        self.redis_mock.xgroup_destroy.assert_called_once()

# ################################################################################################################################

    def test_fetch_returns_empty_when_no_subscriptions(self) -> 'None':
        """ Test that fetch returns empty list when user has no subscriptions.
        """
        sub_key = 'sub.test123'

        self.redis_mock.smembers.return_value = set()

        messages = self.backend.fetch_messages(sub_key)

        self.assertEqual(messages, [])
        self.redis_mock.xreadgroup.assert_not_called()

# ################################################################################################################################

    def test_delete_topic_removes_all_data(self) -> 'None':
        """ Test that deleting a topic removes stream and subscriber mappings.
        """
        topic_name = 'test.topic'

        self.redis_mock.smembers.return_value = [b'sub.user1', b'sub.user2']

        self.backend.delete_topic(topic_name)

        self.redis_mock.delete.assert_called()

        self.assertTrue(self.redis_mock.srem.call_count >= 2)

# ################################################################################################################################

    def test_get_subscribed_topics(self) -> 'None':
        """ Test getting list of subscribed topics for a user.
        """
        sub_key = 'sub.test123'

        self.redis_mock.smembers.return_value = ['topic1', 'topic2']

        topics = self.backend.get_subscribed_topics(sub_key)

        self.assertEqual(set(topics), {'topic1', 'topic2'})

# ################################################################################################################################

    def test_get_topic_subscribers(self) -> 'None':
        """ Test getting list of subscribers for a topic.
        """
        topic_name = 'test.topic'

        self.redis_mock.smembers.return_value = ['sub.user1', 'sub.user2']

        subs = self.backend.get_topic_subscribers(topic_name)

        self.assertEqual(set(subs), {'sub.user1', 'sub.user2'})

# ################################################################################################################################

    def test_rename_topic(self) -> 'None':
        """ Test renaming a topic.
        """
        old_name = 'old.topic'
        new_name = 'new.topic'

        self.redis_mock.smembers.return_value = [b'sub.user1']

        self.backend.rename_topic(old_name, new_name)

        self.redis_mock.rename.assert_called()

        self.redis_mock.srem.assert_called()
        self.redis_mock.sadd.assert_called()

# ################################################################################################################################

    def test_ack_message_deletes_disk_file(self) -> 'None':
        """ Test that acknowledging a message with data_ref deletes the disk file.
        """

        # .. first, store a payload on disk ..
        message_id = 'zpsm.20260517-113200-1234-abcdef1234567890'
        data_ref = self.disk_store.store(message_id, 'test.topic', 'test data', '')

        # .. ack with data_ref should delete the file ..
        self.backend.ack_message('stream:test', 'sub1', '1-0', data_ref)

        import os
        absolute_path = os.path.join(self.test_dir, data_ref)
        self.assertFalse(os.path.exists(absolute_path))

# ################################################################################################################################

    def test_ack_message_without_data_ref(self) -> 'None':
        """ Test that acknowledging without data_ref still works.
        """
        self.backend.ack_message('stream:test', 'sub1', '1-0')
        self.redis_mock.xack.assert_called_once()

# ################################################################################################################################

    def test_browse_messages_returns_metadata(self) -> 'None':
        """ Test that browse_messages returns metadata from the stream.
        """
        topic_name = 'test.topic'

        self.redis_mock.xrange.return_value = [
            ('1-0', {
                'msg_id': 'msg1',
                'data_ref': 'test.topic/ab/cd/msg1.msg',
                'data_size': '12',
                'data_preview': 'test payload',
                'topic_name': topic_name,
                'priority': '5',
                'expiration': '3600',
                'pub_time_iso': '2026-01-01T00:00:01',
                'recv_time_iso': '2026-01-01T00:00:01',
                'expiration_time_iso': '2027-01-01T00:00:01',
                'publisher': 'testuser',
            }),
        ]

        messages, next_cursor = self.backend.browse_messages(topic_name)

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['msg_id'], 'msg1')
        self.assertEqual(messages[0]['data_size'], 12)
        self.assertEqual(messages[0]['data_preview'], 'test payload')
        self.assertNotIn('data', messages[0])

        # .. single message returned, fewer than page_size, so no more pages ..
        self.assertEqual(next_cursor, '')

# ################################################################################################################################

    def test_browse_messages_pagination(self) -> 'None':
        """ Test that browse_messages provides a next_cursor for pagination.
        """
        topic_name = 'test.topic'

        # .. simulate a full page of 2 messages with page_size=2 ..
        self.redis_mock.xrange.return_value = [
            ('1000-0', {
                'msg_id': 'msg1', 'data_ref': 'ref1', 'data_size': '5',
                'data_preview': 'hello', 'topic_name': topic_name,
                'priority': '5', 'expiration': '3600',
                'pub_time_iso': '2026-01-01T00:00:01',
                'recv_time_iso': '2026-01-01T00:00:01',
                'expiration_time_iso': '2027-01-01T00:00:01',
            }),
            ('2000-3', {
                'msg_id': 'msg2', 'data_ref': 'ref2', 'data_size': '5',
                'data_preview': 'world', 'topic_name': topic_name,
                'priority': '5', 'expiration': '3600',
                'pub_time_iso': '2026-01-01T00:00:02',
                'recv_time_iso': '2026-01-01T00:00:02',
                'expiration_time_iso': '2027-01-01T00:00:02',
            }),
        ]

        messages, next_cursor = self.backend.browse_messages(topic_name, page_size=2)

        self.assertEqual(len(messages), 2)
        self.assertEqual(next_cursor, '2000-4')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()
