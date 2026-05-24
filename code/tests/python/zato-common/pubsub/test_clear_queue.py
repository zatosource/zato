# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import shutil
import tempfile
import time
import unittest

# redis
from redis import Redis

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.redis_backend import ModuleCtx, RedisPubSubBackend
from zato.common.pubsub.disk_store import DiskMessageStore
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

_test_redis_host = 'localhost'
_test_redis_port = 6379

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class BaseClearQueueTestCase(unittest.TestCase):
    """ Shared setUp, tearDown, and helpers for all clear_queue tests.
    """

    def setUp(self) -> 'None':

        # Set up a real Redis connection ..
        self.redis = Redis(host=_test_redis_host, port=_test_redis_port, db=PubSub.Test_Redis_DB, decode_responses=True)

        # .. set up a temp directory for disk store ..
        self.test_dir = tempfile.mkdtemp()
        self.disk_store = DiskMessageStore(self.test_dir)

        # .. create the backend instance ..
        self.backend = RedisPubSubBackend(self.redis, self.disk_store)

        # .. use a unique run ID per test to avoid collisions ..
        self._run_id = f'{int(time.time())}'
        self.topic_name = f'test.clear.{self._run_id}'

        # .. track resources for cleanup.
        self.created_data_refs:'strlist' = []
        self.subscribed_keys:'strlist' = []
        self.extra_topic_names:'strlist' = []

# ################################################################################################################################

    def tearDown(self) -> 'None':

        # Clean up all Redis keys created during the test ..
        for data_ref in self.created_data_refs:
            pending_key = f'{ModuleCtx.Pending_Prefix}{data_ref}'
            _ = self.redis.delete(pending_key)
            _ = self.redis.zrem(ModuleCtx.Pending_Expiry_Key, data_ref)

        # .. clean up subscriber, topic, and stream keys ..
        all_topics = [self.topic_name] + self.extra_topic_names

        for topic in all_topics:
            topic_subs_key = f'{ModuleCtx.Topic_Subs_Prefix}{topic}'
            stream_key = f'{ModuleCtx.Stream_Prefix}{topic}'
            _ = self.redis.delete(topic_subs_key)
            _ = self.redis.delete(stream_key)

        for sub_key in self.subscribed_keys:
            subs_key = f'{ModuleCtx.Subs_Prefix}{sub_key}'
            _ = self.redis.delete(subs_key)
            sub_pending_key = f'{ModuleCtx.Sub_Pending_Prefix}{sub_key}'
            _ = self.redis.delete(sub_pending_key)

        # .. and the temp directory.
        shutil.rmtree(self.test_dir)

# ################################################################################################################################

    def subscribe(self, sub_key:'str', topic_name:'str'='') -> 'None':
        """ Subscribe a sub_key to a topic and track it for cleanup.
        """
        if not topic_name:
            topic_name = self.topic_name

        self.backend.subscribe(sub_key, topic_name)

        if sub_key not in self.subscribed_keys:
            self.subscribed_keys.append(sub_key)

# ################################################################################################################################

    def publish_to(self, topic_name:'str', data:'str'='test payload') -> 'str':
        """ Publish a message to a specific topic.
        """
        result = self.backend.publish(topic_name, data)
        return result.msg_id

# ################################################################################################################################

    def publish(self, data:'str'='test payload') -> 'str':
        """ Publish a message to the default test topic.
        """
        return self.publish_to(self.topic_name, data)

# ################################################################################################################################

    def get_data_refs_from_stream(self, topic_name:'str', count:'int') -> 'strlist':
        """ Reads the last N data_refs from the stream for a topic.
        """
        stream_key = f'{ModuleCtx.Stream_Prefix}{topic_name}'
        messages:'anylist' = cast_('anylist', self.redis.xrevrange(stream_key, count=count))

        data_refs:'strlist' = []

        for _, message_data in messages:
            data_ref = message_data['data_ref']
            data_refs.append(data_ref)
            self.created_data_refs.append(data_ref)

        return data_refs

# ################################################################################################################################

    def get_data_ref_from_stream(self) -> 'str':
        """ Reads the last message from the default topic stream.
        """
        refs = self.get_data_refs_from_stream(self.topic_name, 1)
        return refs[0]

# ################################################################################################################################

    def has_pending_member(self, data_ref:'str', sub_key:'str') -> 'bool':
        """ Returns True if the sub_key is in the pending set for data_ref.
        """
        pending_key = f'{ModuleCtx.Pending_Prefix}{data_ref}'
        out = self.redis.sismember(pending_key, sub_key)
        return bool(out)

# ################################################################################################################################

    def has_sub_pending_member(self, sub_key:'str', data_ref:'str') -> 'bool':
        """ Returns True if the data_ref is in the sub_pending set for sub_key.
        """
        sub_pending_key = f'{ModuleCtx.Sub_Pending_Prefix}{sub_key}'
        out = self.redis.sismember(sub_pending_key, data_ref)
        return bool(out)

# ################################################################################################################################

    def has_expiry_entry(self, data_ref:'str') -> 'bool':
        """ Returns True if the data_ref is still in the expiry sorted set.
        """
        score = self.redis.zscore(ModuleCtx.Pending_Expiry_Key, data_ref)
        return score is not None

# ################################################################################################################################

    def get_pending_count(self, data_ref:'str') -> 'int':
        """ Returns the number of subscribers still in the pending set.
        """
        pending_key = f'{ModuleCtx.Pending_Prefix}{data_ref}'
        out = cast_('int', self.redis.scard(pending_key))
        return out

# ################################################################################################################################

    def file_exists(self, data_ref:'str') -> 'bool':
        """ Returns True if the disk file for the given data_ref exists.
        """
        absolute_path = os.path.join(self.test_dir, data_ref)
        return os.path.exists(absolute_path)

# ################################################################################################################################
# ################################################################################################################################

class TestClearEmptyQueue(BaseClearQueueTestCase):
    """ Clear an empty queue returns cleared_count: 0, no crash.
    """

    def test_clear_empty_queue(self) -> 'None':

        sub_key = f'sk_clear_empty_{self._run_id}'
        self.subscribe(sub_key)

        result = self.backend.clear_queue(sub_key)

        self.assertEqual(result['cleared_count'], 0)

# ################################################################################################################################
# ################################################################################################################################

class TestClearSingleMessage(BaseClearQueueTestCase):
    """ Clear a single message from a sole subscriber.
    """

    def test_clear_single_message_sole_subscriber(self) -> 'None':

        sub_key = f'sk_clear_single_{self._run_id}'
        self.subscribe(sub_key)

        # .. publish one message ..
        _ = self.publish()
        data_ref = self.get_data_ref_from_stream()

        # .. verify it exists ..
        self.assertTrue(self.file_exists(data_ref))
        self.assertTrue(self.has_pending_member(data_ref, sub_key))
        self.assertTrue(self.has_sub_pending_member(sub_key, data_ref))
        self.assertTrue(self.has_expiry_entry(data_ref))

        # .. clear the queue ..
        result = self.backend.clear_queue(sub_key)

        # .. verify cleared_count ..
        self.assertEqual(result['cleared_count'], 1)

        # .. verify everything is gone.
        self.assertFalse(self.file_exists(data_ref))
        self.assertFalse(self.has_pending_member(data_ref, sub_key))
        self.assertFalse(self.has_sub_pending_member(sub_key, data_ref))
        self.assertFalse(self.has_expiry_entry(data_ref))

# ################################################################################################################################
# ################################################################################################################################

class TestClearBulkMessages(BaseClearQueueTestCase):
    """ Clear 50 messages from a sole subscriber.
    """

    def test_clear_fifty_messages(self) -> 'None':

        sub_key = f'sk_clear_bulk_{self._run_id}'
        self.subscribe(sub_key)

        # .. publish 50 messages ..
        for idx in range(50):
            _ = self.publish(f'bulk payload {idx}')

        data_refs = self.get_data_refs_from_stream(self.topic_name, 50)
        self.assertEqual(len(data_refs), 50)

        # .. verify files exist ..
        for data_ref in data_refs:
            self.assertTrue(self.file_exists(data_ref))

        # .. clear the queue ..
        result = self.backend.clear_queue(sub_key)

        # .. verify count ..
        self.assertEqual(result['cleared_count'], 50)

        # .. verify everything is gone.
        for data_ref in data_refs:
            self.assertFalse(self.file_exists(data_ref))
            self.assertEqual(self.get_pending_count(data_ref), 0)
            self.assertFalse(self.has_expiry_entry(data_ref))

# ################################################################################################################################
# ################################################################################################################################

class TestClearOneOfTwoSubscribers(BaseClearQueueTestCase):
    """ Clear one subscriber's queue, verify the other subscriber still has the message.
    """

    def test_clear_one_subscriber_leaves_other(self) -> 'None':

        sub_key_a = f'sk_clear_a_{self._run_id}'
        sub_key_b = f'sk_clear_b_{self._run_id}'

        self.subscribe(sub_key_a)
        self.subscribe(sub_key_b)

        # .. publish one message ..
        _ = self.publish()
        data_ref = self.get_data_ref_from_stream()

        # .. both subscribers should be pending ..
        self.assertEqual(self.get_pending_count(data_ref), 2)

        # .. clear subscriber A's queue ..
        result = self.backend.clear_queue(sub_key_a)
        self.assertEqual(result['cleared_count'], 1)

        # .. A is gone from pending, B remains ..
        self.assertFalse(self.has_pending_member(data_ref, sub_key_a))
        self.assertTrue(self.has_pending_member(data_ref, sub_key_b))

        # .. disk file still exists because B needs it ..
        self.assertTrue(self.file_exists(data_ref))

        # .. expiry entry still exists ..
        self.assertTrue(self.has_expiry_entry(data_ref))

        # .. B can still fetch the message.
        messages = self.backend.fetch_messages(sub_key_b)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['_data_ref'], data_ref)

# ################################################################################################################################
# ################################################################################################################################

class TestClearWithPartiallyAckedMessages(BaseClearQueueTestCase):
    """ Subscriber fetches 3 of 5 messages (entering PEL), then clears. All 5 should be cleared.
    """

    def test_clear_with_pel_and_lag(self) -> 'None':

        sub_key = f'sk_clear_partial_{self._run_id}'
        self.subscribe(sub_key)

        # .. publish 5 messages ..
        for idx in range(5):
            _ = self.publish(f'partial payload {idx}')

        data_refs = self.get_data_refs_from_stream(self.topic_name, 5)
        self.assertEqual(len(data_refs), 5)

        # .. fetch 3 messages (they enter the PEL but remain unacked) ..
        messages = self.backend.fetch_messages(sub_key, max_messages=3)
        self.assertEqual(len(messages), 3)

        # .. clear the queue - should handle both PEL entries and unread lag ..
        result = self.backend.clear_queue(sub_key)

        self.assertEqual(result['cleared_count'], 5)

        # .. verify everything is gone.
        for data_ref in data_refs:
            self.assertFalse(self.file_exists(data_ref))
            self.assertEqual(self.get_pending_count(data_ref), 0)
            self.assertFalse(self.has_expiry_entry(data_ref))

# ################################################################################################################################
# ################################################################################################################################

class TestClearMultiTopicSubscriber(BaseClearQueueTestCase):
    """ Subscriber is subscribed to 3 topics, publish to each, clear, verify all cleared.
    """

    def test_clear_across_multiple_topics(self) -> 'None':

        sub_key = f'sk_clear_multi_{self._run_id}'

        # .. create 3 topics ..
        topic_a = f'test.clear.a.{self._run_id}'
        topic_b = f'test.clear.b.{self._run_id}'
        topic_c = f'test.clear.c.{self._run_id}'

        self.extra_topic_names.extend([topic_a, topic_b, topic_c])

        # .. subscribe to all 3 ..
        self.subscribe(sub_key, topic_a)
        self.subscribe(sub_key, topic_b)
        self.subscribe(sub_key, topic_c)

        # .. publish 2 messages to each topic ..
        for _ in range(2):
            _ = self.publish_to(topic_a, 'topic a payload')
            _ = self.publish_to(topic_b, 'topic b payload')
            _ = self.publish_to(topic_c, 'topic c payload')

        refs_a = self.get_data_refs_from_stream(topic_a, 2)
        refs_b = self.get_data_refs_from_stream(topic_b, 2)
        refs_c = self.get_data_refs_from_stream(topic_c, 2)

        all_refs = refs_a + refs_b + refs_c
        self.assertEqual(len(all_refs), 6)

        # .. clear the queue ..
        result = self.backend.clear_queue(sub_key)

        self.assertEqual(result['cleared_count'], 6)

        # .. verify all files are gone.
        for data_ref in all_refs:
            self.assertFalse(self.file_exists(data_ref))
            self.assertEqual(self.get_pending_count(data_ref), 0)

# ################################################################################################################################
# ################################################################################################################################

class TestQueueFunctionalAfterClear(BaseClearQueueTestCase):
    """ After clearing, new messages should be fetchable.
    """

    def test_publish_after_clear_is_fetchable(self) -> 'None':

        sub_key = f'sk_clear_reuse_{self._run_id}'
        self.subscribe(sub_key)

        # .. publish and clear ..
        _ = self.publish('old message')
        _ = self.get_data_ref_from_stream()

        result = self.backend.clear_queue(sub_key)
        self.assertEqual(result['cleared_count'], 1)

        # .. publish a new message ..
        _ = self.publish('new message')
        new_data_ref = self.get_data_ref_from_stream()

        # .. the new message should be fetchable ..
        messages = self.backend.fetch_messages(sub_key)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['data'], 'new message')
        self.assertEqual(messages[0]['_data_ref'], new_data_ref)

# ################################################################################################################################
# ################################################################################################################################

class TestClearIdempotent(BaseClearQueueTestCase):
    """ Clearing twice returns cleared_count: 0 on the second call.
    """

    def test_clear_twice_is_idempotent(self) -> 'None':

        sub_key = f'sk_clear_idem_{self._run_id}'
        self.subscribe(sub_key)

        # .. publish 5 messages ..
        for idx in range(5):
            _ = self.publish(f'idem payload {idx}')

        _ = self.get_data_refs_from_stream(self.topic_name, 5)

        # .. first clear ..
        result_first = self.backend.clear_queue(sub_key)
        self.assertEqual(result_first['cleared_count'], 5)

        # .. second clear ..
        result_second = self.backend.clear_queue(sub_key)
        self.assertEqual(result_second['cleared_count'], 0)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
