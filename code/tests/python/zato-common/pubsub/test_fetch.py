# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import shutil
import tempfile
import time
import unittest

# redis
from redis import Redis

# Zato
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
_test_redis_db   = 0

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class BaseFetchTestCase(unittest.TestCase):
    """ Shared setUp, tearDown, and helpers for all fetch/pull tests.
    """

    def setUp(self) -> 'None':

        # Set up a real Redis connection ..
        self.redis = Redis(host=_test_redis_host, port=_test_redis_port, db=_test_redis_db, decode_responses=True)

        # .. set up a temp directory for disk store ..
        self.test_dir = tempfile.mkdtemp()
        self.disk_store = DiskMessageStore(self.test_dir)

        # .. create the backend instance ..
        self.backend = RedisPubSubBackend(self.redis, self.disk_store)

        # .. use a unique topic name per test run to avoid collisions ..
        self._run_id = f'{int(time.time())}'
        self.topic_name = f'test.fetch.{self._run_id}'

        # .. track resources created during the test for cleanup.
        self.created_data_refs:'strlist' = []
        self.subscribed_keys:'strlist' = []

# ################################################################################################################################

    def tearDown(self) -> 'None':

        # Clean up all Redis keys created during the test ..
        for data_ref in self.created_data_refs:
            pending_key = f'{ModuleCtx.Pending_Prefix}{data_ref}'
            _ = self.redis.delete(pending_key)
            _ = self.redis.zrem(ModuleCtx.Pending_Expiry_Key, data_ref)

        # .. clean up subscriber, topic, and stream keys ..
        topic_subs_key = f'{ModuleCtx.Topic_Subs_Prefix}{self.topic_name}'
        stream_key = f'{ModuleCtx.Stream_Prefix}{self.topic_name}'
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

    def subscribe(self, sub_key:'str') -> 'None':
        """ Subscribe a sub_key to the test topic and track it for cleanup.
        """
        self.backend.subscribe(sub_key, self.topic_name)
        self.subscribed_keys.append(sub_key)

# ################################################################################################################################

    def get_data_ref_from_stream(self) -> 'str':
        """ Reads the last message from the stream and returns its data_ref.
        """
        stream_key = f'{ModuleCtx.Stream_Prefix}{self.topic_name}'
        messages:'anylist' = cast_('anylist', self.redis.xrevrange(stream_key, count=1))

        first_entry = messages[0]
        _, message_data = first_entry
        data_ref = message_data['data_ref']

        self.created_data_refs.append(data_ref)

        return data_ref

# ################################################################################################################################
# ################################################################################################################################

class TestMetadataEnvelope(BaseFetchTestCase):
    """ Full metadata envelope check - all expected fields present in fetched message.
    """

    def test_fetched_message_has_full_metadata(self) -> 'None':

        # Subscribe ..
        sub_key = f'sub.meta.{self._run_id}'
        self.subscribe(sub_key)

        # .. publish with all optional fields ..
        result = self.backend.publish(
            self.topic_name, 'envelope payload',
            priority=7,
            expiration=3600,
            correl_id='corr-123',
            in_reply_to='reply-456',
            ext_client_id='ext-789',
            pub_time='2026-05-18T10:00:00',
        )

        _ = self.get_data_ref_from_stream()

        # .. fetch ..
        messages = self.backend.fetch_messages(sub_key)
        logger.info('fetch_messages -> %s', messages)
        self.assertEqual(len(messages), 1)

        message = messages[0]

        # .. verify all metadata fields ..
        self.assertEqual(message['data'], 'envelope payload')
        self.assertEqual(message['topic_name'], self.topic_name)
        self.assertEqual(message['msg_id'], result.msg_id)
        self.assertEqual(message['correl_id'], 'corr-123')
        self.assertEqual(message['in_reply_to'], 'reply-456')
        self.assertEqual(message['ext_client_id'], 'ext-789')
        self.assertEqual(message['priority'], 7)
        self.assertEqual(message['expiration'], 3600)
        self.assertEqual(message['pub_time_iso'], '2026-05-18T10:00:00')
        self.assertIn('recv_time_iso', message)
        self.assertIn('expiration_time_iso', message)
        self.assertIn('data_size', message)

# ################################################################################################################################
# ################################################################################################################################

class TestExpiredMessageNotAvailable(BaseFetchTestCase):
    """ 1-second TTL expired message not available.
    """

    def test_expired_message_not_fetched(self) -> 'None':

        # Subscribe ..
        sub_key = f'sub.ttl.{self._run_id}'
        self.subscribe(sub_key)

        # .. publish with 1-second TTL ..
        _ = self.backend.publish(self.topic_name, 'short-lived', expiration=1)
        _ = self.get_data_ref_from_stream()

        # .. wait for expiry ..
        time.sleep(1.5)

        # .. fetch returns nothing because the message is expired.
        messages = self.backend.fetch_messages(sub_key)
        logger.info('fetch_messages (expired) -> %s', messages)
        self.assertEqual(len(messages), 0)

# ################################################################################################################################
# ################################################################################################################################

class TestPriorityRoundTrip(BaseFetchTestCase):
    """ Priority 9 round-trips correctly.
    """

    def test_priority_nine_round_trips(self) -> 'None':

        # Subscribe ..
        sub_key = f'sub.pri.{self._run_id}'
        self.subscribe(sub_key)

        # .. publish with priority 9 ..
        _ = self.backend.publish(self.topic_name, 'high priority', priority=9)
        _ = self.get_data_ref_from_stream()

        # .. fetch and verify priority.
        messages = self.backend.fetch_messages(sub_key)
        logger.info('fetch_messages -> %s', messages)
        self.assertEqual(len(messages), 1)

        message = messages[0]
        self.assertEqual(message['priority'], 9)

# ################################################################################################################################
# ################################################################################################################################

class TestPriorityOrdering(BaseFetchTestCase):
    """ Priority ordering (9, 5, 1) - highest priority delivered first.
    """

    def test_messages_ordered_by_priority_desc(self) -> 'None':

        # Subscribe ..
        sub_key = f'sub.priord.{self._run_id}'
        self.subscribe(sub_key)

        # .. publish 3 messages with different priorities (in ascending order) ..
        _ = self.backend.publish(self.topic_name, 'low', priority=1)
        _ = self.get_data_ref_from_stream()

        _ = self.backend.publish(self.topic_name, 'medium', priority=5)
        _ = self.get_data_ref_from_stream()

        _ = self.backend.publish(self.topic_name, 'high', priority=9)
        _ = self.get_data_ref_from_stream()

        # .. fetch all three ..
        messages = self.backend.fetch_messages(sub_key)
        logger.info('fetch_messages -> %s', messages)
        self.assertEqual(len(messages), 3)

        # .. they arrive ordered by priority descending.
        first_message = messages[0]
        self.assertEqual(first_message['data'], 'high')
        self.assertEqual(first_message['priority'], 9)

        second_message = messages[1]
        self.assertEqual(second_message['data'], 'medium')
        self.assertEqual(second_message['priority'], 5)

        third_message = messages[2]
        self.assertEqual(third_message['data'], 'low')
        self.assertEqual(third_message['priority'], 1)

# ################################################################################################################################
# ################################################################################################################################

class TestCorrelIdRoundTrip(BaseFetchTestCase):
    """ correl_id, in_reply_to, ext_client_id, pub_time round-trip.
    """

    def test_optional_fields_round_trip(self) -> 'None':

        # Subscribe ..
        sub_key = f'sub.corr.{self._run_id}'
        self.subscribe(sub_key)

        # .. publish with all optional fields ..
        _ = self.backend.publish(
            self.topic_name, 'correlated',
            correl_id='corr-abc',
            in_reply_to='reply-def',
            ext_client_id='ext-ghi',
            pub_time='2026-01-15T08:30:00',
        )

        _ = self.get_data_ref_from_stream()

        # .. fetch and verify all optional fields round-trip.
        messages = self.backend.fetch_messages(sub_key)
        logger.info('fetch_messages -> %s', messages)
        self.assertEqual(len(messages), 1)

        message = messages[0]
        self.assertEqual(message['correl_id'], 'corr-abc')
        self.assertEqual(message['in_reply_to'], 'reply-def')
        self.assertEqual(message['ext_client_id'], 'ext-ghi')
        self.assertEqual(message['pub_time_iso'], '2026-01-15T08:30:00')

# ################################################################################################################################
# ################################################################################################################################

class TestMaxMessagesLimit(BaseFetchTestCase):
    """ max_messages=2 returns exactly 2.
    """

    def test_max_messages_caps_result(self) -> 'None':

        # Subscribe ..
        sub_key = f'sub.maxmsg.{self._run_id}'
        self.subscribe(sub_key)

        # .. publish 5 messages ..
        for _ in range(5):
            _ = self.backend.publish(self.topic_name, 'payload')
            _ = self.get_data_ref_from_stream()

        # .. fetch with max_messages=2 returns exactly 2.
        messages = self.backend.fetch_messages(sub_key, max_messages=2)
        logger.info('fetch_messages (max=2) -> %s', messages)
        self.assertEqual(len(messages), 2)

# ################################################################################################################################
# ################################################################################################################################

class TestMaxLenReturnsZero(BaseFetchTestCase):
    """ Small max_len returns 0 messages when payload exceeds the limit.
    """

    def test_small_max_len_returns_zero(self) -> 'None':

        # Subscribe ..
        sub_key = f'sub.maxlen.{self._run_id}'
        self.subscribe(sub_key)

        # .. publish a message with a payload larger than max_len ..
        large_payload = 'x' * 1000
        _ = self.backend.publish(self.topic_name, large_payload)
        _ = self.get_data_ref_from_stream()

        # .. fetch with max_len=10 returns 0 because the payload is too large.
        messages = self.backend.fetch_messages(sub_key, max_len=10)
        logger.info('fetch_messages (max_len=10) -> %s', messages)
        self.assertEqual(len(messages), 0)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
