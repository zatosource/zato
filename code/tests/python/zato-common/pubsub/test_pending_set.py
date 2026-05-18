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

class BasePendingSetTestCase(unittest.TestCase):
    """ Shared setUp, tearDown, and helpers for all pending-set tests.
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
        self.topic_name = f'test.pending.{self._run_id}'

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

        # .. clean up subscriber and topic keys ..
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
        logger.info('subscribe -> sub_key:%s, topic_name:%s', sub_key, self.topic_name)

# ################################################################################################################################

    def publish(self, data:'str'='test payload') -> 'str':
        """ Publish a message to the test topic and track its data_ref for cleanup.
        """
        result = self.backend.publish(self.topic_name, data)
        msg_id = result.msg_id
        logger.info('publish -> msg_id:%s, topic_name:%s', msg_id, self.topic_name)

        return msg_id

# ################################################################################################################################

    def get_pending_count(self, data_ref:'str') -> 'int':
        """ Returns the number of subscribers still in the pending set.
        """
        pending_key = f'{ModuleCtx.Pending_Prefix}{data_ref}'

        out = self.redis.scard(pending_key)
        logger.info('get_pending_count -> data_ref:%s, count:%s', data_ref, out)

        return out # pyright: ignore[reportReturnType]

# ################################################################################################################################

    def has_pending_member(self, data_ref:'str', sub_key:'str') -> 'bool':
        """ Returns True if the sub_key is in the pending set for data_ref.
        """
        pending_key = f'{ModuleCtx.Pending_Prefix}{data_ref}'

        out = self.redis.sismember(pending_key, sub_key)
        logger.info('has_pending_member -> data_ref:%s, sub_key:%s, result:%s', data_ref, sub_key, out)

        return bool(out)

# ################################################################################################################################

    def has_expiry_entry(self, data_ref:'str') -> 'bool':
        """ Returns True if the data_ref is still in the expiry sorted set.
        """
        score = self.redis.zscore(ModuleCtx.Pending_Expiry_Key, data_ref)
        logger.info('has_expiry_entry -> data_ref:%s, score:%s', data_ref, score)

        out = score is not None
        return out

# ################################################################################################################################

    def file_exists(self, data_ref:'str') -> 'bool':
        """ Returns True if the disk file for the given data_ref exists.
        """
        absolute_path = os.path.join(self.test_dir, data_ref)

        out = os.path.exists(absolute_path)
        logger.info('file_exists -> data_ref:%s, path:%s, exists:%s', data_ref, absolute_path, out)

        return out

# ################################################################################################################################

    def get_data_ref_from_stream(self) -> 'str':
        """ Reads the last message from the stream and returns its data_ref.
        """
        stream_key = f'{ModuleCtx.Stream_Prefix}{self.topic_name}'
        messages:'anylist' = cast_('anylist', self.redis.xrevrange(stream_key, count=1))
        _, message_data = messages[0]
        data_ref = message_data['data_ref']

        self.created_data_refs.append(data_ref)
        logger.info('get_data_ref_from_stream -> data_ref:%s', data_ref)

        return data_ref

# ################################################################################################################################
# ################################################################################################################################

class TestAckFirstSubscriber(BasePendingSetTestCase):
    """ Ack from first subscriber - pending set still contains the second sub_key, file exists.
    """

    def test_ack_from_first_subscriber_leaves_file_and_pending(self) -> 'None':
        """ After one of two subscribers acks, the file and pending set should still exist
        with the remaining subscriber.
        """

        # Subscribe two consumers to the topic ..
        sub_key_a = f'sub.pending_a.{self._run_id}'
        sub_key_b = f'sub.pending_b.{self._run_id}'

        self.subscribe(sub_key_a)
        self.subscribe(sub_key_b)

        # .. publish a message ..
        _ = self.publish()
        data_ref = self.get_data_ref_from_stream()

        # .. verify the pending set contains both subscribers ..
        pending_count = self.get_pending_count(data_ref)
        self.assertEqual(pending_count, 2)

        # .. fetch messages for subscriber A so we can ack ..
        messages = self.backend.fetch_messages(sub_key_a)
        logger.info('fetch_messages(sub_key_a) -> %s', messages)

        self.assertEqual(len(messages), 1)

        msg = messages[0]
        stream_name = msg['_stream_name']
        redis_message_id = msg['_redis_message_id']
        msg_data_ref = msg['_data_ref']

        # .. ack from subscriber A ..
        self.backend.ack_message(stream_name, sub_key_a, redis_message_id, msg_data_ref)

        # .. verify the pending set now has only subscriber B ..
        pending_count = self.get_pending_count(data_ref)
        self.assertEqual(pending_count, 1)

        has_a = self.has_pending_member(data_ref, sub_key_a)
        self.assertFalse(has_a)

        has_b = self.has_pending_member(data_ref, sub_key_b)
        self.assertTrue(has_b)

        # .. verify the disk file still exists ..
        file_present = self.file_exists(data_ref)
        self.assertTrue(file_present)

        # .. and verify the expiry entry still exists.
        expiry_present = self.has_expiry_entry(data_ref)
        self.assertTrue(expiry_present)

# ################################################################################################################################
# ################################################################################################################################

class TestAckSecondSubscriber(BasePendingSetTestCase):
    """ Ack from second subscriber - pending set deleted, expiry entry deleted, file deleted.
    """

    def test_ack_from_both_subscribers_deletes_everything(self) -> 'None':
        """ After both subscribers ack, the pending set, expiry entry, and disk file should all be gone.
        """

        # Subscribe two consumers to the topic ..
        sub_key_a = f'sub.pending_a.{self._run_id}'
        sub_key_b = f'sub.pending_b.{self._run_id}'

        self.subscribe(sub_key_a)
        self.subscribe(sub_key_b)

        # .. publish a message ..
        _ = self.publish()
        data_ref = self.get_data_ref_from_stream()

        # .. fetch and ack from subscriber A ..
        messages_a = self.backend.fetch_messages(sub_key_a)
        logger.info('fetch_messages(sub_key_a) -> %s', messages_a)

        msg_a = messages_a[0]
        self.backend.ack_message(msg_a['_stream_name'], sub_key_a, msg_a['_redis_message_id'], msg_a['_data_ref'])

        # .. verify file still exists after first ack ..
        file_present = self.file_exists(data_ref)
        self.assertTrue(file_present)

        # .. fetch and ack from subscriber B ..
        messages_b = self.backend.fetch_messages(sub_key_b)
        logger.info('fetch_messages(sub_key_b) -> %s', messages_b)

        msg_b = messages_b[0]
        self.backend.ack_message(msg_b['_stream_name'], sub_key_b, msg_b['_redis_message_id'], msg_b['_data_ref'])

        # .. verify the pending set is gone ..
        pending_count = self.get_pending_count(data_ref)
        self.assertEqual(pending_count, 0)

        # .. verify the disk file is gone ..
        file_present = self.file_exists(data_ref)
        self.assertFalse(file_present)

        # .. and verify the expiry entry is gone.
        expiry_present = self.has_expiry_entry(data_ref)
        self.assertFalse(expiry_present)

# ################################################################################################################################
# ################################################################################################################################

class TestAckOnlySubscriber(BasePendingSetTestCase):
    """ Ack from only subscriber - file deleted immediately.
    """

    def test_ack_from_sole_subscriber_deletes_everything(self) -> 'None':
        """ With a single subscriber, ack should delete the file, pending set, and expiry entry immediately.
        """

        # Subscribe one consumer to the topic ..
        sub_key = f'sub.pending_sole.{self._run_id}'
        self.subscribe(sub_key)

        # .. publish a message ..
        _ = self.publish()
        data_ref = self.get_data_ref_from_stream()

        # .. verify the pending set contains the subscriber ..
        pending_count = self.get_pending_count(data_ref)
        self.assertEqual(pending_count, 1)

        # .. fetch and ack ..
        messages = self.backend.fetch_messages(sub_key)
        logger.info('fetch_messages(sub_key) -> %s', messages)

        self.assertEqual(len(messages), 1)

        msg = messages[0]
        self.backend.ack_message(msg['_stream_name'], sub_key, msg['_redis_message_id'], msg['_data_ref'])

        # .. verify the pending set is gone ..
        pending_count = self.get_pending_count(data_ref)
        self.assertEqual(pending_count, 0)

        # .. verify the disk file is gone ..
        file_present = self.file_exists(data_ref)
        self.assertFalse(file_present)

        # .. and verify the expiry entry is gone.
        expiry_present = self.has_expiry_entry(data_ref)
        self.assertFalse(expiry_present)

# ################################################################################################################################
# ################################################################################################################################

class TestAckAfterUnsubscribe(BasePendingSetTestCase):
    """ Unsubscribe one subscriber, then ack from the other - file deleted after ack.
    """

    def test_ack_after_unsubscribe_deletes_file(self) -> 'None':
        """ Scenario:
        1. Two subscribers (A, B) are subscribed to the topic.
        2. A message is published - pending set gets {A, B}, sub_pending sets populated.
        3. Subscriber B is unsubscribed - the Lua script eagerly removes B from pending:{data_ref},
           leaving only {A}. sub_pending:{B} is deleted. File stays because A still needs it.
        4. Subscriber A fetches and acks - pending set becomes empty, file deleted.
        """

        # Subscribe two consumers to the topic ..
        sub_key_a = f'sub.pending_a.{self._run_id}'
        sub_key_b = f'sub.pending_b.{self._run_id}'

        self.subscribe(sub_key_a)
        self.subscribe(sub_key_b)

        # .. publish a message - pending set is now {A, B} ..
        _ = self.publish()
        data_ref = self.get_data_ref_from_stream()

        # .. verify the pending set has both ..
        pending_count = self.get_pending_count(data_ref)
        self.assertEqual(pending_count, 2)

        # .. unsubscribe B - Lua script eagerly removes B from the pending set ..
        self.backend.unsubscribe(sub_key_b, self.topic_name)
        logger.info('unsubscribed sub_key_b:%s from topic:%s', sub_key_b, self.topic_name)

        # .. the pending set no longer contains B (eagerly cleaned) ..
        has_b = self.has_pending_member(data_ref, sub_key_b)
        self.assertFalse(has_b)

        # .. but A is still there ..
        has_a = self.has_pending_member(data_ref, sub_key_a)
        self.assertTrue(has_a)

        # .. and the file still exists because A needs it ..
        file_present = self.file_exists(data_ref)
        self.assertTrue(file_present)

        # .. subscriber A fetches and acks the message ..
        messages = self.backend.fetch_messages(sub_key_a)
        logger.info('fetch_messages(sub_key_a) -> %s', messages)

        self.assertEqual(len(messages), 1)

        msg = messages[0]
        self.backend.ack_message(msg['_stream_name'], sub_key_a, msg['_redis_message_id'], msg['_data_ref'])

        # .. after A's ack, pending set is empty, everything cleaned up ..
        pending_count = self.get_pending_count(data_ref)
        self.assertEqual(pending_count, 0)

        # .. the disk file is gone ..
        file_present = self.file_exists(data_ref)
        self.assertFalse(file_present)

        # .. and the expiry entry is gone.
        expiry_present = self.has_expiry_entry(data_ref)
        self.assertFalse(expiry_present)

# ################################################################################################################################
# ################################################################################################################################

class TestAckAfterMultipleUnsubscribes(BasePendingSetTestCase):
    """ Unsubscribe 3 of 5 subscribers, ack from remaining 2 - file deleted after both ack.
    """

    def test_ack_after_multiple_unsubscribes_deletes_file(self) -> 'None':
        """ Scenario:
        1. Five subscribers (A through E) are subscribed to the topic.
        2. A message is published - pending set gets {A, B, C, D, E}.
        3. Subscribers C, D, E are unsubscribed. The Lua script eagerly removes each
           from pending:{data_ref}, leaving {A, B}. sub_pending keys for C, D, E are deleted.
        4. Subscriber A fetches and acks - pending set becomes {B}, file stays.
        5. Subscriber B fetches and acks - pending set becomes empty, file deleted.
        """

        # Subscribe five consumers to the topic ..
        sub_keys = [f'sub.pending_{letter}.{self._run_id}' for letter in 'abcde']

        for sub_key in sub_keys:
            self.subscribe(sub_key)

        # .. publish a message - pending set is now {A, B, C, D, E} ..
        _ = self.publish()
        data_ref = self.get_data_ref_from_stream()

        # .. verify the pending set has all 5 ..
        pending_count = self.get_pending_count(data_ref)
        self.assertEqual(pending_count, 5)

        # .. unsubscribe C, D, E - Lua script eagerly removes each from the pending set ..
        for sub_key in sub_keys[2:]:
            self.backend.unsubscribe(sub_key, self.topic_name)
            logger.info('unsubscribed %s from topic:%s', sub_key, self.topic_name)

        # .. the pending set now has only {A, B} ..
        pending_count = self.get_pending_count(data_ref)
        self.assertEqual(pending_count, 2)

        has_a = self.has_pending_member(data_ref, sub_keys[0])
        self.assertTrue(has_a)

        has_b = self.has_pending_member(data_ref, sub_keys[1])
        self.assertTrue(has_b)

        # .. C, D, E are gone from the pending set ..
        for sub_key in sub_keys[2:]:
            has_sub = self.has_pending_member(data_ref, sub_key)
            self.assertFalse(has_sub)

        # .. file still exists because A and B need it ..
        file_present = self.file_exists(data_ref)
        self.assertTrue(file_present)

        # .. subscriber A fetches and acks ..
        messages_a = self.backend.fetch_messages(sub_keys[0])
        logger.info('fetch_messages(sub_key_a) -> %s', messages_a)

        msg_a = messages_a[0]
        self.backend.ack_message(msg_a['_stream_name'], sub_keys[0], msg_a['_redis_message_id'], msg_a['_data_ref'])

        # .. after A's ack, pending set is {B}, file stays ..
        pending_count = self.get_pending_count(data_ref)
        self.assertEqual(pending_count, 1)

        file_present = self.file_exists(data_ref)
        self.assertTrue(file_present)

        # .. subscriber B fetches and acks ..
        messages_b = self.backend.fetch_messages(sub_keys[1])
        logger.info('fetch_messages(sub_key_b) -> %s', messages_b)

        msg_b = messages_b[0]
        self.backend.ack_message(msg_b['_stream_name'], sub_keys[1], msg_b['_redis_message_id'], msg_b['_data_ref'])

        # .. after B's ack, pending set is empty, everything cleaned up ..
        pending_count = self.get_pending_count(data_ref)
        self.assertEqual(pending_count, 0)

        # .. the disk file is gone ..
        file_present = self.file_exists(data_ref)
        self.assertFalse(file_present)

        # .. and the expiry entry is gone.
        expiry_present = self.has_expiry_entry(data_ref)
        self.assertFalse(expiry_present)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
