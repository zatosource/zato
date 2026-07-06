# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import threading
import time

# redis
from redis import Redis

# Zato
from zato.common.api import PubSub
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, strset

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_topic_delete_atomic')

_settle_time = 0.5

_topic_target = 'tda.topic.a'
_topic_survivor = 'tda.topic.b'

_test_redis_host = 'localhost'
_test_redis_port = 6379
_test_redis_db   = PubSub.Test_Redis_DB

_Stream_Prefix      = 'zato:pubsub:stream:'
_Topic_Subs_Prefix  = 'zato:pubsub:topic_subs:'
_Subs_Prefix        = 'zato:pubsub:subs:'
_Pending_Prefix     = 'zato:pubsub:pending:'
_Sub_Pending_Prefix = 'zato:pubsub:sub_pending:'
_Pending_Expiry_Key = 'zato:pubsub:pending_expiry'

# ################################################################################################################################
# ################################################################################################################################

def _get_admin() -> 'any_':
    from zato.common.test.client import AdminClient
    from zato.common.test.config_pubsub_topic_delete_atomic import TestConfig

    admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
    return admin

# ################################################################################################################################

def _get_publisher() -> 'any_':
    from zato.common.test.client import PublishClient
    from zato.common.test.config_pubsub_topic_delete_atomic import TestConfig

    publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
    return publisher

# ################################################################################################################################

def _get_redis() -> 'Redis':
    redis = Redis(host=_test_redis_host, port=_test_redis_port, db=_test_redis_db, decode_responses=True)
    return redis

# ################################################################################################################################

def _get_topic_id(admin:'any_', topic_name:'str') -> 'int':
    topic_list = admin.invoke('zato.pubsub.topic.get-list', {'cluster_id': 1})

    if isinstance(topic_list, list):
        items:'anylist' = topic_list
    else:
        items = topic_list['zato_pubsub_topic_get_list_response']

    for item in items:
        if item['name'] == topic_name:
            return item['id']

    raise RuntimeError(f'Topic not found: {topic_name}')

# ################################################################################################################################

def _get_sub_key(admin:'any_', topic_name:'str') -> 'str':
    from zato.common.test.config_pubsub_topic_delete_atomic import TestConfig

    sub_list = admin.invoke('zato.pubsub.subscription.get-list', {'cluster_id': 1})

    if isinstance(sub_list, list):
        items:'anylist' = sub_list
    else:
        items = sub_list['zato_pubsub_subscription_get_list_response']

    for item in items:
        if item['sec_name'] == TestConfig.subscriber_username:
            topic_name_list = item['topic_name_list']
            for topic_entry in topic_name_list:
                if topic_entry['topic_name'] == topic_name:
                    return item['sub_key']

    raise RuntimeError(f'No subscription found for topic: {topic_name}')

# ################################################################################################################################

def _get_data_refs_from_stream(redis:'Redis', topic_name:'str') -> 'anylist':
    stream_key = f'{_Stream_Prefix}{topic_name}'
    entries:'anylist' = cast_('anylist', redis.xrange(stream_key))

    data_refs:'anylist' = []

    for _, fields in entries:
        data_ref = fields['data_ref']
        data_refs.append(data_ref)

    return data_refs

# ################################################################################################################################

def _count_msg_files(directory:'str') -> 'int':
    count = 0

    if not os.path.isdir(directory):
        return 0

    for _, _dirs, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith('.msg'):
                count += 1

    return count

# ################################################################################################################################

def _recreate_topic_and_subscribe(admin:'any_', topic_name:'str') -> 'None':
    from zato.common.test.config_pubsub_topic_delete_atomic import TestConfig

    _ = admin.invoke('zato.pubsub.topic.create', {
        'name': topic_name,
        'is_active': True,
    })

    time.sleep(_settle_time)

    _ = admin.invoke('zato.pubsub.subscription.create', {
        'cluster_id': 1,
        'topic_name_list': [topic_name],
        'sec_base_id': TestConfig.subscriber_sec_base_id,
        'delivery_type': 'pull',
    })

    time.sleep(_settle_time)

# ################################################################################################################################
# ################################################################################################################################

class TestNoDiskFilesRemainAfterConcurrentPublishAndDelete:
    """ Gap A: concurrent publish during delete must not leave disk files
    with no stream entry pointing to them.
    """

    def test_01_no_disk_files_remain_after_concurrent_publish_and_delete(self, zato_server:'any_') -> 'None':

        from zato.common.test.config_pubsub_topic_delete_atomic import TestConfig

        admin = _get_admin()
        publisher = _get_publisher()
        redis = _get_redis()

        # .. publish 5 messages so there are disk files ..
        for _ in range(5):
            _ = publisher.publish(_topic_target, 'pre-delete-payload')

        time.sleep(_settle_time)

        topic_id = _get_topic_id(admin, _topic_target)

        # .. collect data_refs that are currently in the stream ..
        data_refs_before = _get_data_refs_from_stream(redis, _topic_target)

        # .. publish more from a background thread while deleting ..
        def _publish_loop() -> 'None':
            for _ in range(5):
                try:
                    _ = publisher.publish(_topic_target, 'concurrent-payload')
                except Exception:
                    pass

        publish_thread = threading.Thread(target=_publish_loop)
        publish_thread.start()

        # .. delete the topic concurrently ..
        _ = admin.invoke('zato.pubsub.topic.delete', {'id': topic_id})

        publish_thread.join()
        time.sleep(_settle_time)

        # .. verify: no stream key ..
        stream_key = f'{_Stream_Prefix}{_topic_target}'
        stream_exists = redis.exists(stream_key)
        assert stream_exists == 0, f'Stream key still exists: {stream_key}'

        # .. verify: no topic_subs key ..
        topic_subs_key = f'{_Topic_Subs_Prefix}{_topic_target}'
        topic_subs_exists = redis.exists(topic_subs_key)
        assert topic_subs_exists == 0, f'topic_subs key still exists: {topic_subs_key}'

        # .. verify: no disk files remain ..
        pubsub_messages_dir = os.path.join(TestConfig.server_directory, 'work', 'pubsub-messages')
        topic_dir = os.path.join(pubsub_messages_dir, _topic_target)
        file_count = _count_msg_files(topic_dir)
        assert file_count == 0, f'Expected 0 .msg files after delete, found {file_count}'

        # .. verify: no stale pending entries for data_refs that were in the stream ..
        for data_ref in data_refs_before:
            pending_key = f'{_Pending_Prefix}{data_ref}'
            exists = redis.exists(pending_key)
            assert exists == 0, f'Stale pending key: {pending_key}'

        # .. restore for subsequent tests.
        _recreate_topic_and_subscribe(admin, _topic_target)

# ################################################################################################################################
# ################################################################################################################################

class TestNoDanglingSubReferenceAfterConcurrentSubscribeAndDelete:
    """ Gap B: concurrent subscribe during delete must not leave dangling references
    where a subscriber's subs set still contains the deleted topic name.
    """

    def test_02_no_dangling_sub_reference_after_concurrent_subscribe_and_delete(self, zato_server:'any_') -> 'None':

        from zato.common.test.config_pubsub_topic_delete_atomic import TestConfig

        admin = _get_admin()
        redis = _get_redis()

        topic_id = _get_topic_id(admin, _topic_target)

        # .. attempt to subscribe from a background thread while deleting ..
        def _subscribe_loop() -> 'None':
            try:
                _ = admin.invoke('zato.pubsub.subscription.create', {
                    'cluster_id': 1,
                    'topic_name_list': [_topic_target],
                    'sec_base_id': TestConfig.subscriber_sec_base_id,
                    'delivery_type': 'pull',
                })
            except Exception:
                pass

        subscribe_thread = threading.Thread(target=_subscribe_loop)
        subscribe_thread.start()

        # .. delete the topic concurrently ..
        try:
            _ = admin.invoke('zato.pubsub.topic.delete', {'id': topic_id})
        except Exception as error:
            logger.warning('topic.delete raised during concurrent subscribe: %s', error)

        subscribe_thread.join()
        time.sleep(_settle_time)

        # .. verify: no topic_subs key ..
        topic_subs_key = f'{_Topic_Subs_Prefix}{_topic_target}'
        topic_subs_exists = redis.exists(topic_subs_key)
        assert topic_subs_exists == 0, f'topic_subs key still exists: {topic_subs_key}'

        # .. verify: no subs:<sub_key> set contains the deleted topic ..
        cursor = 0
        while True:
            scan_result = cast_('tuple', redis.scan(cursor, match=f'{_Subs_Prefix}*', count=100))
            cursor = scan_result[0]
            keys = scan_result[1]

            for key in keys:
                members:'strset' = cast_('strset', redis.smembers(key))
                assert _topic_target not in members, \
                    f'Dangling reference to {_topic_target} in {key}'

            if cursor == 0:
                break

        # .. restore for subsequent tests.
        _recreate_topic_and_subscribe(admin, _topic_target)

# ################################################################################################################################
# ################################################################################################################################

class TestNoPartialSubscriptionAfterConcurrentSubscribeAndDelete:
    """ Gap C: concurrent subscribe tries XGROUP_CREATE on deleted stream.
    Re-creating the topic and subscribing fresh must work without errors.
    """

    def test_03_no_partial_subscription_after_concurrent_subscribe_and_delete(self, zato_server:'any_') -> 'None':

        from zato.common.test.config_pubsub_topic_delete_atomic import TestConfig

        admin = _get_admin()
        publisher = _get_publisher()
        redis = _get_redis()

        topic_id = _get_topic_id(admin, _topic_target)

        # .. attempt subscribe from background thread while deleting ..
        def _subscribe_loop() -> 'None':
            try:
                _ = admin.invoke('zato.pubsub.subscription.create', {
                    'cluster_id': 1,
                    'topic_name_list': [_topic_target],
                    'sec_base_id': TestConfig.subscriber_sec_base_id,
                    'delivery_type': 'pull',
                })
            except Exception:
                pass

        subscribe_thread = threading.Thread(target=_subscribe_loop)
        subscribe_thread.start()

        try:
            _ = admin.invoke('zato.pubsub.topic.delete', {'id': topic_id})
        except Exception:
            pass

        subscribe_thread.join()
        time.sleep(_settle_time)

        # .. verify: no consumer groups on the (now-deleted) stream ..
        stream_key = f'{_Stream_Prefix}{_topic_target}'
        stream_exists = redis.exists(stream_key)
        assert stream_exists == 0, f'Stream still exists: {stream_key}'

        # .. re-create topic and subscribe fresh - must succeed without errors ..
        _recreate_topic_and_subscribe(admin, _topic_target)

        # .. publish and pull to prove the full round-trip works ..
        _ = publisher.publish(_topic_target, 'post-recreate-message')
        time.sleep(_settle_time)

        from zato.common.test.client import PullClient
        puller = PullClient(TestConfig.base_url, TestConfig.subscriber_username, TestConfig.subscriber_password)
        result = puller.pull(max_messages=10)
        message_count = result['message_count']

        assert message_count >= 1, f'Expected at least 1 message after re-subscribe, got {message_count}'

# ################################################################################################################################
# ################################################################################################################################

class TestBurstPublishDuringDeleteLeaveNoFiles:
    """ Gap A high-volume variant: 10 rapid publishes concurrent with delete
    must not leave disk files or stale pending entries.
    """

    def test_04_burst_publish_during_delete_leaves_no_files(self, zato_server:'any_') -> 'None':

        from zato.common.test.config_pubsub_topic_delete_atomic import TestConfig

        admin = _get_admin()
        publisher = _get_publisher()
        redis = _get_redis()

        topic_id = _get_topic_id(admin, _topic_target)

        # .. rapid publish from background thread ..
        def _publish_loop() -> 'None':
            for _ in range(10):
                try:
                    _ = publisher.publish(_topic_target, 'burst-payload')
                except Exception:
                    pass

        publish_thread = threading.Thread(target=_publish_loop)
        publish_thread.start()

        # .. delete concurrently ..
        _ = admin.invoke('zato.pubsub.topic.delete', {'id': topic_id})

        publish_thread.join()
        time.sleep(_settle_time)

        # .. verify: no stream, no topic_subs, no disk files ..
        stream_key = f'{_Stream_Prefix}{_topic_target}'
        assert redis.exists(stream_key) == 0

        topic_subs_key = f'{_Topic_Subs_Prefix}{_topic_target}'
        assert redis.exists(topic_subs_key) == 0

        pubsub_messages_dir = os.path.join(TestConfig.server_directory, 'work', 'pubsub-messages')
        topic_dir = os.path.join(pubsub_messages_dir, _topic_target)
        file_count = _count_msg_files(topic_dir)
        assert file_count == 0, f'Expected 0 .msg files after burst delete, found {file_count}'

        # .. verify: no stale pending entries referencing the deleted topic ..
        cursor = 0
        while True:
            scan_result = cast_('tuple', redis.scan(cursor, match=f'{_Pending_Prefix}*', count=100))
            cursor = scan_result[0]
            keys = scan_result[1]

            for key in keys:
                data_ref = key.replace(_Pending_Prefix, '')
                if f'{_topic_target}/' in data_ref:
                    assert False, f'Stale pending key for deleted topic: {key}'

            if cursor == 0:
                break

        # .. restore.
        _recreate_topic_and_subscribe(admin, _topic_target)

# ################################################################################################################################
# ################################################################################################################################

class TestNoStalePendingEntriesAfterDelete:
    """ Pending and expiry sets must be fully cleaned for the deleted topic's data_refs.
    """

    def test_05_no_stale_pending_entries_after_delete(self, zato_server:'any_') -> 'None':

        admin = _get_admin()
        publisher = _get_publisher()
        redis = _get_redis()

        # .. record stream length before publishing ..
        stream_key_before = f'{_Stream_Prefix}{_topic_target}'
        stream_len_before = cast_('int', redis.xlen(stream_key_before))

        # .. publish 5 messages (pending sets will be populated for the subscriber) ..
        for _ in range(5):
            _ = publisher.publish(_topic_target, 'pending-test-payload')

        time.sleep(_settle_time)

        # .. collect data_refs - only the ones we just published ..
        all_data_refs = _get_data_refs_from_stream(redis, _topic_target)
        data_refs = all_data_refs[stream_len_before:]
        assert len(data_refs) == 5

        sub_key = _get_sub_key(admin, _topic_target)
        sub_pending_key = f'{_Sub_Pending_Prefix}{sub_key}'

        # .. verify pending state exists before delete ..
        for data_ref in data_refs:
            pending_key = f'{_Pending_Prefix}{data_ref}'
            assert redis.exists(pending_key) == 1, f'Expected pending key to exist before delete: {pending_key}'

        # .. delete the topic ..
        topic_id = _get_topic_id(admin, _topic_target)
        _ = admin.invoke('zato.pubsub.topic.delete', {'id': topic_id})
        time.sleep(_settle_time)

        # .. verify: all pending:<data_ref> keys gone ..
        for data_ref in data_refs:
            pending_key = f'{_Pending_Prefix}{data_ref}'
            exists = redis.exists(pending_key)
            assert exists == 0, f'Stale pending key after delete: {pending_key}'

        # .. verify: data_refs removed from sub_pending ..
        sub_pending_members:'strset' = cast_('strset', redis.smembers(sub_pending_key))
        for data_ref in data_refs:
            assert data_ref not in sub_pending_members, \
                f'Stale data_ref in sub_pending after delete: {data_ref}'

        # .. verify: pending_expiry sorted set has no entries for these data_refs ..
        for data_ref in data_refs:
            score = redis.zscore(_Pending_Expiry_Key, data_ref)
            assert score is None, f'Stale expiry entry after delete: {data_ref}'

        # .. restore.
        _recreate_topic_and_subscribe(admin, _topic_target)

# ################################################################################################################################
# ################################################################################################################################

class TestMultiTopicSubscriberSurvivorTopicIntact:
    """ Subscriber on two topics (each with its own sub_key). Delete one topic.
    The other topic's sub_key, sub_pending, pending sets, and stream must remain intact.
    """

    def test_06_multi_topic_subscriber_survivor_topic_intact(self, zato_server:'any_') -> 'None':

        admin = _get_admin()
        publisher = _get_publisher()
        redis = _get_redis()

        # .. record stream lengths before publishing ..
        stream_len_target_before = cast_('int', redis.xlen(f'{_Stream_Prefix}{_topic_target}'))
        stream_len_survivor_before = cast_('int', redis.xlen(f'{_Stream_Prefix}{_topic_survivor}'))

        # .. publish 3 messages to each topic ..
        for _ in range(3):
            _ = publisher.publish(_topic_target, 'target-topic-payload')

        for _ in range(3):
            _ = publisher.publish(_topic_survivor, 'survivor-topic-payload')

        time.sleep(_settle_time)

        # .. collect only the data_refs we just published ..
        all_data_refs_target = _get_data_refs_from_stream(redis, _topic_target)
        all_data_refs_survivor = _get_data_refs_from_stream(redis, _topic_survivor)

        data_refs_target = all_data_refs_target[stream_len_target_before:]
        data_refs_survivor = all_data_refs_survivor[stream_len_survivor_before:]

        assert len(data_refs_target) == 3
        assert len(data_refs_survivor) == 3

        # .. get sub_key for the survivor topic ..
        sub_key_survivor = _get_sub_key(admin, _topic_survivor)
        sub_pending_key_survivor = f'{_Sub_Pending_Prefix}{sub_key_survivor}'

        # .. verify survivor sub_pending contains its data_refs before delete ..
        sub_pending_survivor_before:'strset' = cast_('strset', redis.smembers(sub_pending_key_survivor))

        for data_ref in data_refs_survivor:
            assert data_ref in sub_pending_survivor_before, \
                f'Expected {data_ref} in survivor sub_pending before delete'

        # .. delete the target topic ..
        topic_id = _get_topic_id(admin, _topic_target)
        _ = admin.invoke('zato.pubsub.topic.delete', {'id': topic_id})
        time.sleep(_settle_time)

        # .. verify: target topic's pending sets are gone ..
        for data_ref in data_refs_target:
            pending_key = f'{_Pending_Prefix}{data_ref}'
            exists = redis.exists(pending_key)
            assert exists == 0, f'Target pending key still exists: {pending_key}'

        # .. verify: target topic's stream is gone ..
        stream_key_target = f'{_Stream_Prefix}{_topic_target}'
        assert redis.exists(stream_key_target) == 0, 'Target stream still exists'

        # .. verify: survivor topic's sub_pending is intact ..
        sub_pending_survivor_after:'strset' = cast_('strset', redis.smembers(sub_pending_key_survivor))

        for data_ref in data_refs_survivor:
            assert data_ref in sub_pending_survivor_after, \
                f'Survivor data_ref lost from sub_pending after deleting target topic: {data_ref}'

        # .. verify: survivor topic's pending sets still contain the survivor sub_key ..
        for data_ref in data_refs_survivor:
            pending_key = f'{_Pending_Prefix}{data_ref}'
            members:'strset' = cast_('strset', redis.smembers(pending_key))
            assert sub_key_survivor in members, \
                f'Survivor sub_key lost from pending set: {pending_key}'

        # .. verify: survivor topic stream is intact ..
        stream_key_survivor = f'{_Stream_Prefix}{_topic_survivor}'
        stream_len = cast_('int', redis.xlen(stream_key_survivor))
        assert stream_len >= 3, f'Survivor topic stream should have at least 3 entries, got {stream_len}'

        # .. verify: survivor topic_subs key is intact ..
        topic_subs_key_survivor = f'{_Topic_Subs_Prefix}{_topic_survivor}'
        topic_subs_exists = redis.exists(topic_subs_key_survivor)
        assert topic_subs_exists == 1, f'Survivor topic_subs key is gone: {topic_subs_key_survivor}'

        # .. restore the target topic.
        _recreate_topic_and_subscribe(admin, _topic_target)

# ################################################################################################################################
# ################################################################################################################################

class TestDoubleDeleteIdempotent:
    """ Deleting the same topic twice must be a no-op the second time, no errors.
    """

    def test_07_double_delete_idempotent(self, zato_server:'any_') -> 'None':

        admin = _get_admin()
        publisher = _get_publisher()

        # .. publish some messages ..
        for _ in range(3):
            _ = publisher.publish(_topic_target, 'double-delete-payload')

        time.sleep(_settle_time)

        # .. first delete ..
        topic_id = _get_topic_id(admin, _topic_target)
        _ = admin.invoke('zato.pubsub.topic.delete', {'id': topic_id})
        time.sleep(_settle_time)

        # .. second delete - the topic no longer exists in ODB, so the API call
        # .. will raise because it cannot find the topic. That is expected.
        try:
            _ = admin.invoke('zato.pubsub.topic.delete', {'id': topic_id})
        except Exception:
            pass

        # .. the important thing: no crash, no stale state.
        # .. Restore for subsequent tests.
        _recreate_topic_and_subscribe(admin, _topic_target)

# ################################################################################################################################
# ################################################################################################################################

class TestDeleteTopicWithNoSubscribers:
    """ Empty topic_subs path: just stream and key cleanup, no pending work.
    """

    def test_08_delete_topic_with_no_subscribers(self, zato_server:'any_') -> 'None':

        admin = _get_admin()
        publisher = _get_publisher()
        redis = _get_redis()

        # .. create a fresh topic with no subscribers ..
        _ = admin.invoke('zato.pubsub.topic.create', {
            'name': 'tda.topic.nosub',
            'is_active': True,
        })

        time.sleep(_settle_time)

        # .. publish to it (publish Lua sees 0 subscribers, self-cleans disk files) ..
        _ = publisher.publish('tda.topic.nosub', 'no-subscriber-payload')
        time.sleep(_settle_time)

        # .. delete it ..
        topic_id = _get_topic_id(admin, 'tda.topic.nosub')
        _ = admin.invoke('zato.pubsub.topic.delete', {'id': topic_id})
        time.sleep(_settle_time)

        # .. verify: stream gone, topic_subs gone ..
        stream_key = f'{_Stream_Prefix}tda.topic.nosub'
        assert redis.exists(stream_key) == 0, f'Stream still exists: {stream_key}'

        topic_subs_key = f'{_Topic_Subs_Prefix}tda.topic.nosub'
        assert redis.exists(topic_subs_key) == 0, f'topic_subs still exists: {topic_subs_key}'

# ################################################################################################################################
# ################################################################################################################################
