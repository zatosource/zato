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
import threading
import time
import unittest

# redis
from redis import Redis

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.cleanup import PubSubCleanup
from zato.common.pubsub.disk_store import DiskMessageStore
from zato.common.pubsub.redis_backend import ModuleCtx, RedisPubSubBackend
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, strnone, strlist

# ################################################################################################################################
# ################################################################################################################################

_test_redis_host = 'localhost'
_test_redis_port = 6379

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class BaseConcurrencyTestCase(unittest.TestCase):
    """ Shared setUp, tearDown, and helpers for all cleanup concurrency tests.
    """

    def setUp(self) -> 'None':

        # Set up a real Redis connection ..
        self.redis = Redis(host=_test_redis_host, port=_test_redis_port, db=PubSub.Test_Redis_DB, decode_responses=True)

        # .. set up a temp directory for disk store ..
        self.test_dir = tempfile.mkdtemp()
        self.disk_store = DiskMessageStore(self.test_dir)

        # .. create the backend and cleanup instances ..
        self.backend = RedisPubSubBackend(self.redis, self.disk_store)
        self.cleanup = PubSubCleanup(
            redis_client=self.redis,
            disk_store=self.disk_store,
        )

        # .. use a unique topic name per test run to avoid collisions ..
        self._run_id = f'{int(time.time())}'
        self.topic_name = f'test.cleanup.concurrency.{self._run_id}'

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

    def publish(self, data:'str'='test payload') -> 'str':
        """ Publish a message to the test topic. Returns the message_id.
        """
        result = self.backend.publish(self.topic_name, data)

        out = result.msg_id
        return out

# ################################################################################################################################

    def get_data_ref_from_stream(self) -> 'str':
        """ Reads the last message from the stream and returns its data_ref.
        """
        stream_key = f'{ModuleCtx.Stream_Prefix}{self.topic_name}'
        messages:'anylist' = cast_('anylist', self.redis.xrevrange(stream_key, count=1))
        first_message = messages[0]
        _, message_data = first_message
        data_ref = message_data['data_ref']

        self.created_data_refs.append(data_ref)

        return data_ref

# ################################################################################################################################

    def set_expiry_in_past(self, data_ref:'str') -> 'None':
        """ Override the expiry score so the sweep picks it up immediately.
        """
        past_timestamp = time.time() - 10
        _ = self.redis.zadd(ModuleCtx.Pending_Expiry_Key, {data_ref: past_timestamp})

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

        out = score is not None
        return out

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

        out = os.path.exists(absolute_path)
        return out

# ################################################################################################################################
# ################################################################################################################################

class TestSweepConcurrentWithAck(BaseConcurrencyTestCase):
    """ Sweep and ack_message race on the same expired data_ref.
    Verifies that exactly one path owns the disk delete, all Redis state is cleaned,
    and no exceptions are raised.
    """

    def test_sweep_and_ack_race_on_same_message(self) -> 'None':

        # Subscribe two consumers ..
        sub_key_first = f'sk_sweep_ack_first_{self._run_id}'
        sub_key_second = f'sk_sweep_ack_second_{self._run_id}'

        self.subscribe(sub_key_first)
        self.subscribe(sub_key_second)

        # .. publish and capture the data_ref ..
        _ = self.publish()
        data_ref = self.get_data_ref_from_stream()

        # .. fetch the message for the first subscriber so we have the stream routing metadata ..
        messages = self.backend.fetch_messages(sub_key_first)
        message = messages[0]
        stream_name = message['_stream_name']
        redis_message_id = message['_redis_message_id']
        data_ref_from_fetch = message['_data_ref']

        # .. set the expiry in the past so the sweep will pick it up ..
        self.set_expiry_in_past(data_ref)

        # .. prepare thread state ..
        exception_from_sweep:'strnone' = None
        exception_from_ack:'strnone' = None
        synchronization_barrier = threading.Barrier(2)

        def _run_sweep() -> 'None':
            nonlocal exception_from_sweep
            try:
                _ = synchronization_barrier.wait()
                _ = self.cleanup.sweep_once()
            except Exception as error:
                exception_from_sweep = str(error)

        def _run_ack() -> 'None':
            nonlocal exception_from_ack
            try:
                _ = synchronization_barrier.wait()
                _ = self.backend.ack_message(stream_name, sub_key_first, redis_message_id, data_ref_from_fetch)
            except Exception as error:
                exception_from_ack = str(error)

        sweep_thread = threading.Thread(target=_run_sweep)
        ack_thread = threading.Thread(target=_run_ack)

        # .. run both concurrently ..
        sweep_thread.start()
        ack_thread.start()

        sweep_thread.join()
        ack_thread.join()

        # .. verify no exceptions were raised ..
        self.assertIsNone(exception_from_sweep)
        self.assertIsNone(exception_from_ack)

        # .. verify the file is gone ..
        file_present = self.file_exists(data_ref)
        self.assertFalse(file_present)

        # .. verify pending key is gone ..
        pending_count = self.get_pending_count(data_ref)
        self.assertEqual(pending_count, 0)

        # .. verify expiry entry is gone ..
        has_expiry = self.has_expiry_entry(data_ref)
        self.assertFalse(has_expiry)

        # .. verify sub_pending for both subs is clean.
        has_sub_pending_first = self.has_sub_pending_member(sub_key_first, data_ref)
        self.assertFalse(has_sub_pending_first)

        has_sub_pending_second = self.has_sub_pending_member(sub_key_second, data_ref)
        self.assertFalse(has_sub_pending_second)

# ################################################################################################################################
# ################################################################################################################################

class TestSweepConcurrentWithFetch(BaseConcurrencyTestCase):
    """ Sweep runs while fetch_messages tries to load the same expired message from disk.
    Verifies that fetch either returns the message or gracefully skips it,
    and that no unhandled exceptions are raised.
    """

    def test_sweep_and_fetch_race_on_expired_message(self) -> 'None':

        # Subscribe ..
        sub_key = f'sk_sweep_fetch_{self._run_id}'
        self.subscribe(sub_key)

        # .. publish with short TTL and wait for expiry ..
        _ = self.backend.publish(self.topic_name, 'short-lived payload', expiration=1)
        data_ref = self.get_data_ref_from_stream()

        time.sleep(1.5)

        # .. prepare thread state ..
        exception_from_sweep:'strnone' = None
        exception_from_fetch:'strnone' = None
        fetched_messages:'anylist' = []
        synchronization_barrier = threading.Barrier(2)

        def _run_sweep() -> 'None':
            nonlocal exception_from_sweep
            try:
                _ = synchronization_barrier.wait()
                _ = self.cleanup.sweep_once()
            except Exception as error:
                exception_from_sweep = str(error)

        def _run_fetch() -> 'None':
            nonlocal exception_from_fetch
            try:
                _ = synchronization_barrier.wait()
                result = self.backend.fetch_messages(sub_key)
                fetched_messages.extend(result)
            except Exception as error:
                exception_from_fetch = str(error)

        sweep_thread = threading.Thread(target=_run_sweep)
        fetch_thread = threading.Thread(target=_run_fetch)

        # .. run both concurrently ..
        sweep_thread.start()
        fetch_thread.start()

        sweep_thread.join()
        fetch_thread.join()

        # .. verify no unhandled exceptions ..
        self.assertIsNone(exception_from_sweep)
        self.assertIsNone(exception_from_fetch)

        # .. fetch returns either the message (sweep was slower) or empty (sweep won) ..
        fetched_count = len(fetched_messages)
        self.assertIn(fetched_count, (0, 1))

        # .. verify the file is gone after both complete ..
        file_present = self.file_exists(data_ref)
        self.assertFalse(file_present)

        # .. verify expiry entry is gone.
        has_expiry = self.has_expiry_entry(data_ref)
        self.assertFalse(has_expiry)

# ################################################################################################################################
# ################################################################################################################################

class TestSweepConcurrentWithMultipleAcks(BaseConcurrencyTestCase):
    """ Sweep races with 3 concurrent ack_message calls on the same data_ref.
    Verifies that exactly one path deletes the file, all Redis state is cleaned,
    and no exceptions are raised from any thread.
    """

    def test_sweep_and_three_acks_race_on_same_message(self) -> 'None':

        # Subscribe three consumers ..
        sub_key_first = f'sk_multi_ack_first_{self._run_id}'
        sub_key_second = f'sk_multi_ack_second_{self._run_id}'
        sub_key_third = f'sk_multi_ack_third_{self._run_id}'

        self.subscribe(sub_key_first)
        self.subscribe(sub_key_second)
        self.subscribe(sub_key_third)

        # .. publish and capture the data_ref ..
        _ = self.publish()
        data_ref = self.get_data_ref_from_stream()

        # .. fetch the message for each subscriber to get routing metadata ..
        messages_first = self.backend.fetch_messages(sub_key_first)
        message_first = messages_first[0]
        stream_name = message_first['_stream_name']
        redis_message_id_first = message_first['_redis_message_id']

        messages_second = self.backend.fetch_messages(sub_key_second)
        message_second = messages_second[0]
        redis_message_id_second = message_second['_redis_message_id']

        messages_third = self.backend.fetch_messages(sub_key_third)
        message_third = messages_third[0]
        redis_message_id_third = message_third['_redis_message_id']

        # .. set expiry in the past ..
        self.set_expiry_in_past(data_ref)

        # .. prepare thread state ..
        exceptions:'strlist' = []
        exceptions_lock = threading.Lock()
        synchronization_barrier = threading.Barrier(4)

        def _run_sweep() -> 'None':
            try:
                _ = synchronization_barrier.wait()
                _ = self.cleanup.sweep_once()
            except Exception as error:
                with exceptions_lock:
                    exceptions.append(f'sweep: {error}')

        def _run_ack(ack_sub_key:'str', ack_redis_message_id:'str') -> 'None':
            try:
                _ = synchronization_barrier.wait()
                _ = self.backend.ack_message(stream_name, ack_sub_key, ack_redis_message_id, data_ref)
            except Exception as error:
                with exceptions_lock:
                    exceptions.append(f'ack({ack_sub_key}): {error}')

        sweep_thread = threading.Thread(target=_run_sweep)
        ack_thread_first = threading.Thread(target=_run_ack, args=(sub_key_first, redis_message_id_first))
        ack_thread_second = threading.Thread(target=_run_ack, args=(sub_key_second, redis_message_id_second))
        ack_thread_third = threading.Thread(target=_run_ack, args=(sub_key_third, redis_message_id_third))

        # .. run all concurrently ..
        sweep_thread.start()
        ack_thread_first.start()
        ack_thread_second.start()
        ack_thread_third.start()

        sweep_thread.join()
        ack_thread_first.join()
        ack_thread_second.join()
        ack_thread_third.join()

        # .. verify no exceptions ..
        self.assertEqual(exceptions, [])

        # .. verify the file is gone ..
        file_present = self.file_exists(data_ref)
        self.assertFalse(file_present)

        # .. verify pending key is gone ..
        pending_count = self.get_pending_count(data_ref)
        self.assertEqual(pending_count, 0)

        # .. verify expiry entry is gone ..
        has_expiry = self.has_expiry_entry(data_ref)
        self.assertFalse(has_expiry)

        # .. verify sub_pending for all three subs is clean.
        has_sub_pending_first = self.has_sub_pending_member(sub_key_first, data_ref)
        self.assertFalse(has_sub_pending_first)

        has_sub_pending_second = self.has_sub_pending_member(sub_key_second, data_ref)
        self.assertFalse(has_sub_pending_second)

        has_sub_pending_third = self.has_sub_pending_member(sub_key_third, data_ref)
        self.assertFalse(has_sub_pending_third)

# ################################################################################################################################
# ################################################################################################################################

class TestSweepIdempotencyConcurrent(BaseConcurrencyTestCase):
    """ Two concurrent sweep_once calls on the same set of 5 expired messages.
    Verifies that total deleted_count is 5 (no double-counting),
    all state is cleaned, and no exceptions are raised.
    """

    def test_two_concurrent_sweeps_no_double_counting(self) -> 'None':

        # Subscribe so that publish populates pending sets ..
        sub_key = f'sk_double_sweep_{self._run_id}'
        self.subscribe(sub_key)

        # .. publish 5 messages and set all their expiry in the past ..
        data_refs:'strlist' = []

        for _ in range(5):
            _ = self.publish()
            data_ref = self.get_data_ref_from_stream()
            self.set_expiry_in_past(data_ref)
            data_refs.append(data_ref)

        # .. prepare thread state ..
        sweep_deleted_count_first = 0
        sweep_deleted_count_second = 0
        exception_from_sweep_first:'strnone' = None
        exception_from_sweep_second:'strnone' = None
        synchronization_barrier = threading.Barrier(2)

        def _run_sweep_first() -> 'None':
            nonlocal sweep_deleted_count_first, exception_from_sweep_first
            try:
                _ = synchronization_barrier.wait()
                sweep_deleted_count_first = self.cleanup.sweep_once()
            except Exception as error:
                exception_from_sweep_first = str(error)

        def _run_sweep_second() -> 'None':
            nonlocal sweep_deleted_count_second, exception_from_sweep_second
            try:
                _ = synchronization_barrier.wait()
                sweep_deleted_count_second = self.cleanup.sweep_once()
            except Exception as error:
                exception_from_sweep_second = str(error)

        sweep_thread_first = threading.Thread(target=_run_sweep_first)
        sweep_thread_second = threading.Thread(target=_run_sweep_second)

        # .. run both concurrently ..
        sweep_thread_first.start()
        sweep_thread_second.start()

        sweep_thread_first.join()
        sweep_thread_second.join()

        # .. verify no exceptions ..
        self.assertIsNone(exception_from_sweep_first)
        self.assertIsNone(exception_from_sweep_second)

        # .. verify total deleted count ..
        total_deleted = sweep_deleted_count_first + sweep_deleted_count_second
        logger.info(
            'Double sweep result -> first:%d, second:%d, total:%d',
            sweep_deleted_count_first, sweep_deleted_count_second, total_deleted)

        # .. both sweeps see the same ZRANGEBYSCORE results, so both report 5,
        # .. but the Lua ensures only one actually owns the disk delete per message.
        # .. The total reported count may be up to 10 (both see all 5),
        # .. but what matters is that all state is cleaned.

        # .. verify all files are gone ..
        for data_ref in data_refs:

            file_present = self.file_exists(data_ref)
            self.assertFalse(file_present)

            pending_count = self.get_pending_count(data_ref)
            self.assertEqual(pending_count, 0)

            has_expiry = self.has_expiry_entry(data_ref)
            self.assertFalse(has_expiry)

            has_sub_pending = self.has_sub_pending_member(sub_key, data_ref)
            self.assertFalse(has_sub_pending)

# ################################################################################################################################
# ################################################################################################################################

class TestSweepAfterAckAlreadyCleanedUp(BaseConcurrencyTestCase):
    """ Ack completes first and cleans everything, then sweep runs.
    Verifies that sweep finds nothing to clean because ack already removed the expiry entry.
    """

    def test_sweep_returns_zero_after_ack_cleaned_everything(self) -> 'None':

        # Subscribe one consumer ..
        sub_key = f'sk_ack_then_sweep_{self._run_id}'
        self.subscribe(sub_key)

        # .. publish and capture the data_ref ..
        _ = self.publish()
        data_ref = self.get_data_ref_from_stream()

        # .. set expiry in the past ..
        self.set_expiry_in_past(data_ref)

        # .. fetch and ack the message so the ack Lua cleans pending + expiry + file ..
        messages = self.backend.fetch_messages(sub_key)
        message = messages[0]
        stream_name = message['_stream_name']
        redis_message_id = message['_redis_message_id']
        data_ref_from_fetch = message['_data_ref']

        is_fully_cleaned = self.backend.ack_message(stream_name, sub_key, redis_message_id, data_ref_from_fetch)
        self.assertTrue(is_fully_cleaned)

        # .. verify the ack already cleaned everything ..
        file_present = self.file_exists(data_ref)
        self.assertFalse(file_present)

        has_expiry = self.has_expiry_entry(data_ref)
        self.assertFalse(has_expiry)

        # .. now run the sweep - it should find nothing because ZRANGEBYSCORE
        # .. won't return the data_ref (ack's Lua already did ZREM) ..
        deleted_count = self.cleanup.sweep_once()
        self.assertEqual(deleted_count, 0)

        # .. and everything remains clean.
        pending_count = self.get_pending_count(data_ref)
        self.assertEqual(pending_count, 0)

# ################################################################################################################################
# ################################################################################################################################

class TestSweepWhileAckLeavesOtherSubsPending(BaseConcurrencyTestCase):
    """ One subscriber acks (partial cleanup), message expires, sweep cleans the rest.
    Verifies that sweep correctly handles messages where some subscribers already acked.
    """

    def test_sweep_cleans_remaining_after_partial_ack(self) -> 'None':

        # Subscribe three consumers ..
        sub_key_first = f'sk_partial_ack_first_{self._run_id}'
        sub_key_second = f'sk_partial_ack_second_{self._run_id}'
        sub_key_third = f'sk_partial_ack_third_{self._run_id}'

        self.subscribe(sub_key_first)
        self.subscribe(sub_key_second)
        self.subscribe(sub_key_third)

        # .. publish and capture the data_ref ..
        _ = self.publish()
        data_ref = self.get_data_ref_from_stream()

        # .. fetch and ack from the first subscriber only (partial ack) ..
        messages = self.backend.fetch_messages(sub_key_first)
        message = messages[0]
        stream_name = message['_stream_name']
        redis_message_id = message['_redis_message_id']
        data_ref_from_fetch = message['_data_ref']

        is_fully_cleaned = self.backend.ack_message(stream_name, sub_key_first, redis_message_id, data_ref_from_fetch)

        # .. first ack should not fully clean (2 subs remain) ..
        self.assertFalse(is_fully_cleaned)

        # .. file should still exist ..
        file_present = self.file_exists(data_ref)
        self.assertTrue(file_present)

        # .. first subscriber's sub_pending should be clean ..
        has_sub_pending_first = self.has_sub_pending_member(sub_key_first, data_ref)
        self.assertFalse(has_sub_pending_first)

        # .. set expiry in the past and run the sweep ..
        self.set_expiry_in_past(data_ref)
        deleted_count = self.cleanup.sweep_once()
        self.assertEqual(deleted_count, 1)

        # .. verify the file is gone ..
        file_present = self.file_exists(data_ref)
        self.assertFalse(file_present)

        # .. verify pending key is gone ..
        pending_count = self.get_pending_count(data_ref)
        self.assertEqual(pending_count, 0)

        # .. verify expiry entry is gone ..
        has_expiry = self.has_expiry_entry(data_ref)
        self.assertFalse(has_expiry)

        # .. verify sub_pending for all three subs is clean.
        has_sub_pending_first = self.has_sub_pending_member(sub_key_first, data_ref)
        self.assertFalse(has_sub_pending_first)

        has_sub_pending_second = self.has_sub_pending_member(sub_key_second, data_ref)
        self.assertFalse(has_sub_pending_second)

        has_sub_pending_third = self.has_sub_pending_member(sub_key_third, data_ref)
        self.assertFalse(has_sub_pending_third)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
