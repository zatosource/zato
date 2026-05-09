# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from unittest.mock import MagicMock

# Zato
from zato.common.pubsub.redis_backend import PublishResult, RedisPubSubBackend, ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

class TestRedisPubSubBackend(unittest.TestCase):

    def setUp(self) -> 'None':
        self.redis_mock = MagicMock()
        self.backend = RedisPubSubBackend(self.redis_mock)

# ################################################################################################################################

    def test_publish_returns_publish_result(self) -> 'None':
        """ Test that publishing returns a PublishResult with msg_id.
        """
        topic_name = 'test.topic'
        data = 'test message'

        result = self.backend.publish(topic_name, data, publisher='testuser')

        self.assertIsInstance(result, PublishResult)
        self.assertIsNotNone(result.msg_id)
        self.assertTrue(len(result.msg_id) > 0)

# ################################################################################################################################

    def test_publish_creates_stream_entry(self) -> 'None':
        """ Test that publishing a message adds an entry to the stream.
        """
        topic_name = 'test.topic'
        data = 'test message'

        result = self.backend.publish(topic_name, data, publisher='testuser')

        self.redis_mock.xadd.assert_called_once()

        call_args = self.redis_mock.xadd.call_args
        stream_key = call_args[0][0]
        message = call_args[0][1]

        self.assertEqual(stream_key, f'{ModuleCtx.Stream_Prefix}{topic_name}')
        self.assertEqual(message['data'], data)
        self.assertEqual(message['topic_name'], topic_name)
        self.assertEqual(message['publisher'], 'testuser')
        self.assertEqual(message['msg_id'], result.msg_id)

# ################################################################################################################################

    def test_subscribe_creates_consumer_group(self) -> 'None':
        """ Test that subscribing creates a consumer group.
        """
        sub_key = 'zpsk.test123'
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

    def test_fetch_returns_messages_in_priority_order(self) -> 'None':
        """ Test that messages are returned sorted by priority (desc) then timestamp (asc).
        """
        sub_key = 'zpsk.test123'

        self.redis_mock.smembers.return_value = [b'topic1']

        self.redis_mock.xreadgroup.return_value = [
            (b'zato:pubsub:stream:topic1', [
                (b'1-0', {
                    b'msg_id': b'msg1', b'data': b'low', b'priority': b'1',
                    b'pub_time_iso': b'2025-01-01T00:00:01', b'recv_time_iso': b'2025-01-01T00:00:01',
                    b'topic_name': b'topic1', b'expiration': b'3600',
                }),
                (b'2-0', {
                    b'msg_id': b'msg2', b'data': b'high', b'priority': b'9',
                    b'pub_time_iso': b'2025-01-01T00:00:02', b'recv_time_iso': b'2025-01-01T00:00:02',
                    b'topic_name': b'topic1', b'expiration': b'3600',
                }),
                (b'3-0', {
                    b'msg_id': b'msg3', b'data': b'medium', b'priority': b'5',
                    b'pub_time_iso': b'2025-01-01T00:00:03', b'recv_time_iso': b'2025-01-01T00:00:03',
                    b'topic_name': b'topic1', b'expiration': b'3600',
                }),
            ])
        ]

        messages = self.backend.fetch_messages(sub_key)

        self.assertEqual(len(messages), 3)

        # Verify {data, meta} format
        self.assertIn('data', messages[0])
        self.assertIn('meta', messages[0])

        # Verify order: priority 9, then 5, then 1
        self.assertEqual(messages[0]['data'], 'high')
        self.assertEqual(messages[0]['meta']['priority'], 9)
        self.assertEqual(messages[1]['data'], 'medium')
        self.assertEqual(messages[1]['meta']['priority'], 5)
        self.assertEqual(messages[2]['data'], 'low')
        self.assertEqual(messages[2]['meta']['priority'], 1)

# ################################################################################################################################

    def test_fetch_includes_time_since_fields(self) -> 'None':
        """ Test that fetched messages include time_since_pub and time_since_recv.
        """
        sub_key = 'zpsk.test123'

        self.redis_mock.smembers.return_value = [b'topic1']
        self.redis_mock.xreadgroup.return_value = [
            (b'zato:pubsub:stream:topic1', [
                (b'1-0', {
                    b'msg_id': b'msg1', b'data': b'test', b'priority': b'5',
                    b'pub_time_iso': b'2025-01-01T00:00:01', b'recv_time_iso': b'2025-01-01T00:00:01',
                    b'topic_name': b'topic1', b'expiration': b'3600',
                }),
            ])
        ]

        messages = self.backend.fetch_messages(sub_key)

        self.assertEqual(len(messages), 1)
        meta = messages[0]['meta']
        self.assertIn('time_since_pub', meta)
        self.assertIn('time_since_recv', meta)
        self.assertTrue(len(meta['time_since_pub']) > 0)
        self.assertTrue(len(meta['time_since_recv']) > 0)

# ################################################################################################################################

    def test_fetch_deserializes_json_data(self) -> 'None':
        """ Test that JSON-encoded data is deserialized back to a dict.
        """
        sub_key = 'zpsk.test123'

        self.redis_mock.smembers.return_value = [b'topic1']
        self.redis_mock.xreadgroup.return_value = [
            (b'zato:pubsub:stream:topic1', [
                (b'1-0', {
                    b'msg_id': b'msg1', b'data': b'{"order_id": 123}', b'priority': b'5',
                    b'pub_time_iso': b'2025-01-01T00:00:01', b'recv_time_iso': b'2025-01-01T00:00:01',
                    b'topic_name': b'topic1', b'expiration': b'3600',
                }),
            ])
        ]

        messages = self.backend.fetch_messages(sub_key)

        self.assertEqual(len(messages), 1)
        self.assertIsInstance(messages[0]['data'], dict)
        self.assertEqual(messages[0]['data']['order_id'], 123)

# ################################################################################################################################

    def test_fetch_keeps_plain_string_data(self) -> 'None':
        """ Test that plain string data stays as a string.
        """
        sub_key = 'zpsk.test123'

        self.redis_mock.smembers.return_value = [b'topic1']
        self.redis_mock.xreadgroup.return_value = [
            (b'zato:pubsub:stream:topic1', [
                (b'1-0', {
                    b'msg_id': b'msg1', b'data': b'hello world', b'priority': b'5',
                    b'pub_time_iso': b'2025-01-01T00:00:01', b'recv_time_iso': b'2025-01-01T00:00:01',
                    b'topic_name': b'topic1', b'expiration': b'3600',
                }),
            ])
        ]

        messages = self.backend.fetch_messages(sub_key)

        self.assertEqual(len(messages), 1)
        self.assertIsInstance(messages[0]['data'], str)
        self.assertEqual(messages[0]['data'], 'hello world')

# ################################################################################################################################

    def test_fetch_acknowledges_messages(self) -> 'None':
        """ Test that fetched messages are acknowledged.
        """
        sub_key = 'zpsk.test123'

        self.redis_mock.smembers.return_value = [b'topic1']
        self.redis_mock.xreadgroup.return_value = [
            (b'zato:pubsub:stream:topic1', [
                (b'1-0', {b'msg_id': b'msg1', b'data': b'test', b'priority': b'5'}),
            ])
        ]

        _ = self.backend.fetch_messages(sub_key)

        self.redis_mock.xack.assert_called_once()

# ################################################################################################################################

    def test_unsubscribe_removes_from_sets(self) -> 'None':
        """ Test that unsubscribing removes entries from sets.
        """
        sub_key = 'zpsk.test123'
        topic_name = 'test.topic'

        self.redis_mock.scard.return_value = 1

        self.backend.unsubscribe(sub_key, topic_name)

        self.assertEqual(self.redis_mock.srem.call_count, 2)

        self.redis_mock.xgroup_destroy.assert_not_called()

# ################################################################################################################################

    def test_unsubscribe_last_topic_destroys_consumer_group(self) -> 'None':
        """ Test that unsubscribing from last topic destroys the consumer group.
        """
        sub_key = 'zpsk.test123'
        topic_name = 'test.topic'

        self.redis_mock.scard.return_value = 0

        self.backend.unsubscribe(sub_key, topic_name)

        self.redis_mock.xgroup_destroy.assert_called_once()

# ################################################################################################################################

    def test_fetch_returns_empty_when_no_subscriptions(self) -> 'None':
        """ Test that fetch returns empty list when user has no subscriptions.
        """
        sub_key = 'zpsk.test123'

        self.redis_mock.smembers.return_value = set()

        messages = self.backend.fetch_messages(sub_key)

        self.assertEqual(messages, [])
        self.redis_mock.xreadgroup.assert_not_called()

# ################################################################################################################################

    def test_delete_topic_removes_all_data(self) -> 'None':
        """ Test that deleting a topic removes stream and subscriber mappings.
        """
        topic_name = 'test.topic'

        self.redis_mock.smembers.return_value = [b'zpsk.user1', b'zpsk.user2']

        self.backend.delete_topic(topic_name)

        self.redis_mock.delete.assert_called()

        self.assertTrue(self.redis_mock.srem.call_count >= 2)

# ################################################################################################################################

    def test_get_subscribed_topics(self) -> 'None':
        """ Test getting list of subscribed topics for a user.
        """
        sub_key = 'zpsk.test123'

        self.redis_mock.smembers.return_value = [b'topic1', b'topic2']

        topics = self.backend.get_subscribed_topics(sub_key)

        self.assertEqual(set(topics), {'topic1', 'topic2'})

# ################################################################################################################################

    def test_get_topic_subscribers(self) -> 'None':
        """ Test getting list of subscribers for a topic.
        """
        topic_name = 'test.topic'

        self.redis_mock.smembers.return_value = [b'zpsk.user1', b'zpsk.user2']

        subs = self.backend.get_topic_subscribers(topic_name)

        self.assertEqual(set(subs), {'zpsk.user1', 'zpsk.user2'})

# ################################################################################################################################

    def test_rename_topic(self) -> 'None':
        """ Test renaming a topic.
        """
        old_name = 'old.topic'
        new_name = 'new.topic'

        self.redis_mock.smembers.return_value = [b'zpsk.user1']

        self.backend.rename_topic(old_name, new_name)

        self.redis_mock.rename.assert_called()

        self.redis_mock.srem.assert_called()
        self.redis_mock.sadd.assert_called()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()
