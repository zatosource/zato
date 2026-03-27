# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from unittest.mock import MagicMock, patch

# Zato
from zato.common.pubsub.redis_backend import RedisPubSubBackend, ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

class TestRedisPubSubBackend(unittest.TestCase):

    def setUp(self) -> 'None':
        self.redis_mock = MagicMock()
        self.backend = RedisPubSubBackend(self.redis_mock)

# ################################################################################################################################

    def test_publish_creates_stream_entry(self) -> 'None':
        """ Test that publishing a message adds an entry to the stream.
        """
        topic_name = 'test.topic'
        data = 'test message'

        msg_id = self.backend.publish(topic_name, data, publisher='testuser')

        # Verify xadd was called
        self.redis_mock.xadd.assert_called_once()

        call_args = self.redis_mock.xadd.call_args
        stream_key = call_args[0][0]
        message = call_args[0][1]

        self.assertEqual(stream_key, f'{ModuleCtx.Stream_Prefix}{topic_name}')
        self.assertEqual(message['data'], data)
        self.assertEqual(message['topic_name'], topic_name)
        self.assertEqual(message['publisher'], 'testuser')
        self.assertIsNotNone(msg_id)

# ################################################################################################################################

    def test_subscribe_creates_consumer_group(self) -> 'None':
        """ Test that subscribing creates a consumer group.
        """
        sub_key = 'zpsk.test123'
        topic_name = 'test.topic'

        self.backend.subscribe(sub_key, topic_name)

        # Verify sadd was called for both sets
        self.assertEqual(self.redis_mock.sadd.call_count, 2)

        # Verify xgroup_create was called
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

        # Mock smembers to return subscribed topics
        self.redis_mock.smembers.return_value = [b'topic1']

        # Mock xreadgroup to return messages with different priorities
        self.redis_mock.xreadgroup.return_value = [
            (b'zato:pubsub:stream:topic1', [
                (b'1-0', {b'msg_id': b'msg1', b'data': b'low', b'priority': b'1', b'pub_time_iso': b'2025-01-01T00:00:01'}),
                (b'2-0', {b'msg_id': b'msg2', b'data': b'high', b'priority': b'9', b'pub_time_iso': b'2025-01-01T00:00:02'}),
                (b'3-0', {b'msg_id': b'msg3', b'data': b'medium', b'priority': b'5', b'pub_time_iso': b'2025-01-01T00:00:03'}),
            ])
        ]

        messages = self.backend.fetch_messages(sub_key)

        # Verify order: priority 9, then 5, then 1
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0]['data'], 'high')
        self.assertEqual(messages[0]['priority'], 9)
        self.assertEqual(messages[1]['data'], 'medium')
        self.assertEqual(messages[1]['priority'], 5)
        self.assertEqual(messages[2]['data'], 'low')
        self.assertEqual(messages[2]['priority'], 1)

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

        # Verify xack was called
        self.redis_mock.xack.assert_called_once()

# ################################################################################################################################

    def test_unsubscribe_removes_from_sets(self) -> 'None':
        """ Test that unsubscribing removes entries from sets.
        """
        sub_key = 'zpsk.test123'
        topic_name = 'test.topic'

        # Mock scard to return 1 (still has other subscriptions)
        self.redis_mock.scard.return_value = 1

        self.backend.unsubscribe(sub_key, topic_name)

        # Verify srem was called for both sets
        self.assertEqual(self.redis_mock.srem.call_count, 2)

        # Verify consumer group was NOT destroyed (still has subscriptions)
        self.redis_mock.xgroup_destroy.assert_not_called()

# ################################################################################################################################

    def test_unsubscribe_last_topic_destroys_consumer_group(self) -> 'None':
        """ Test that unsubscribing from last topic destroys the consumer group.
        """
        sub_key = 'zpsk.test123'
        topic_name = 'test.topic'

        # Mock scard to return 0 (no remaining subscriptions)
        self.redis_mock.scard.return_value = 0

        self.backend.unsubscribe(sub_key, topic_name)

        # Verify consumer group was destroyed
        self.redis_mock.xgroup_destroy.assert_called_once()

# ################################################################################################################################

    def test_fetch_returns_empty_when_no_subscriptions(self) -> 'None':
        """ Test that fetch returns empty list when user has no subscriptions.
        """
        sub_key = 'zpsk.test123'

        # Mock smembers to return empty set
        self.redis_mock.smembers.return_value = set()

        messages = self.backend.fetch_messages(sub_key)

        self.assertEqual(messages, [])
        self.redis_mock.xreadgroup.assert_not_called()

# ################################################################################################################################

    def test_delete_topic_removes_all_data(self) -> 'None':
        """ Test that deleting a topic removes stream and subscriber mappings.
        """
        topic_name = 'test.topic'

        # Mock smembers to return subscribers
        self.redis_mock.smembers.return_value = [b'zpsk.user1', b'zpsk.user2']

        self.backend.delete_topic(topic_name)

        # Verify stream was deleted
        self.redis_mock.delete.assert_called()

        # Verify srem was called for each subscriber
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

        # Verify rename was called for stream
        self.redis_mock.rename.assert_called()

        # Verify subscriber's topic set was updated
        self.redis_mock.srem.assert_called()
        self.redis_mock.sadd.assert_called()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()
