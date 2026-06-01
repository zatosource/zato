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
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_unsub_atomic')

_settle_time = 0.5

_topic_concurrent = 'unsub.atomic.concurrent'
_topic_burst      = 'unsub.atomic.burst'

_test_redis_host = 'localhost'
_test_redis_port = 6379
_test_redis_db   = PubSub.Test_Redis_DB

_Pending_Prefix     = 'zato:pubsub:pending:'
_Sub_Pending_Prefix = 'zato:pubsub:sub_pending:'

# ################################################################################################################################
# ################################################################################################################################

def _get_admin() -> 'any_':
    from zato.common.test.client import AdminClient
    from zato.common.test.config_pubsub_unsub_atomic import TestConfig

    admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
    return admin

# ################################################################################################################################

def _get_publisher() -> 'any_':
    from zato.common.test.client import PublishClient
    from zato.common.test.config_pubsub_unsub_atomic import TestConfig

    publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
    return publisher

# ################################################################################################################################

def _get_redis() -> 'Redis':
    redis = Redis(host=_test_redis_host, port=_test_redis_port, db=_test_redis_db, decode_responses=True)
    return redis

# ################################################################################################################################

def _get_subscriptions(admin:'any_', sec_name:'str') -> 'anylist':
    """ Returns all subscriptions for a given security definition name.
    """
    sub_list = admin.invoke('zato.pubsub.subscription.get-list', {'cluster_id': 1})

    if isinstance(sub_list, list):
        items:'anylist' = sub_list
    else:
        items = sub_list['zato_pubsub_subscription_get_list_response']

    out:'anylist' = []

    for item in items:
        if item['sec_name'] == sec_name:
            out.append(item)

    return out

# ################################################################################################################################

def _get_sub_key(admin:'any_', topic_name:'str') -> 'str':
    """ Returns the sub_key for the test subscriber on the given topic.
    """
    from zato.common.test.config_pubsub_unsub_atomic import TestConfig

    subscriptions = _get_subscriptions(admin, TestConfig.subscriber_username)

    for subscription in subscriptions:
        topic_name_list = subscription['topic_name_list']

        for topic_entry in topic_name_list:
            if topic_entry['topic_name'] == topic_name:

                out = subscription['sub_key']
                return out

    raise RuntimeError(f'No subscription found for topic: {topic_name}')

# ################################################################################################################################

def _get_sub_id(admin:'any_', topic_name:'str') -> 'int':
    """ Returns the subscription ID for the test subscriber on the given topic.
    """
    from zato.common.test.config_pubsub_unsub_atomic import TestConfig

    subscriptions = _get_subscriptions(admin, TestConfig.subscriber_username)

    for subscription in subscriptions:
        topic_name_list = subscription['topic_name_list']

        for topic_entry in topic_name_list:
            if topic_entry['topic_name'] == topic_name:

                out = subscription['id']
                return out

    raise RuntimeError(f'No subscription found for topic: {topic_name}')

# ################################################################################################################################

def _recreate_subscription(admin:'any_', topic_name:'str') -> 'None':
    """ Re-creates the subscription for the test subscriber on the given topic.
    """
    from zato.common.test.config_pubsub_unsub_atomic import TestConfig

    _ = admin.invoke('zato.pubsub.subscription.create', {
        'cluster_id': 1,
        'topic_name_list': [topic_name],
        'sec_base_id': TestConfig.subscriber_sec_base_id,
        'delivery_type': 'pull',
    })

# ################################################################################################################################

def _scan_pending_keys_for_sub(redis:'Redis', sub_key:'str') -> 'anylist':
    """ Scans all pending:<data_ref> keys and returns those that still contain sub_key.
    """
    out:'anylist' = []
    cursor = 0

    while True:
        scan_result = cast_('tuple', redis.scan(cursor, match=f'{_Pending_Prefix}*', count=100))
        cursor = scan_result[0]
        keys = scan_result[1]

        for key in keys:
            if redis.sismember(key, sub_key):
                out.append(key)

        if cursor == 0:
            break

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestNoStalePendingAfterConcurrentPublishAndUnsub:
    """ Proves the primary race is closed: concurrent publish + unsubscribe
    cannot leave stale entries in pending sets.

    Gap: between SREM topic_subs and Lua pending cleanup, a publish Lua could
    read SMEMBERS before the SREM and add the sub_key to a pending set that
    the cleanup Lua then misses. After fix, both operations are atomic.
    """

    def test_01_no_stale_pending_after_concurrent_publish_and_unsub(self, zato_server:'any_') -> 'None':

        admin = _get_admin()
        publisher = _get_publisher()
        redis = _get_redis()

        sub_key = _get_sub_key(admin, _topic_concurrent)
        sub_id = _get_sub_id(admin, _topic_concurrent)

        # .. publish messages from a background thread while the main thread unsubscribes ..
        publish_count = 5

        def _publish_loop() -> 'None':
            for _ in range(publish_count):
                try:
                    _ = publisher.publish(_topic_concurrent, 'race-test-payload')
                except Exception:
                    pass

        publish_thread = threading.Thread(target=_publish_loop)
        publish_thread.start()

        # .. delete the subscription (triggers unsubscribe internally) ..
        try:
            _ = admin.invoke('zato.pubsub.subscription.delete', {'id': sub_id})
        except Exception as error:
            logger.warning('subscription.delete raised: %s', error)

        publish_thread.join()
        time.sleep(_settle_time)

        # .. after unsubscribe, no pending:<data_ref> set should contain sub_key ..
        stale_keys = _scan_pending_keys_for_sub(redis, sub_key)

        assert stale_keys == [], \
            f'Stale pending entries found containing sub_key after unsub: {stale_keys}'

        # .. sub_pending:<sub_key> must not exist ..
        sub_pending_key = f'{_Sub_Pending_Prefix}{sub_key}'
        sub_pending_exists = redis.exists(sub_pending_key)

        assert sub_pending_exists == 0, \
            f'sub_pending key still exists after unsub: {sub_pending_key}'

        # .. re-create the subscription for test isolation.
        _recreate_subscription(admin, _topic_concurrent)
        time.sleep(_settle_time)

# ################################################################################################################################
# ################################################################################################################################

class TestUnsubDuringBurstPublish:
    """ Burst variant: 10 rapid publishes concurrent with unsub.
    After unsub completes, no pending set contains the sub_key.

    Gap: same as test_01 but with higher message volume to increase
    the probability of interleaving under the old non-atomic code.
    """

    def test_02_unsub_during_burst_publish(self, zato_server:'any_') -> 'None':

        admin = _get_admin()
        publisher = _get_publisher()
        redis = _get_redis()

        sub_key = _get_sub_key(admin, _topic_burst)
        sub_id = _get_sub_id(admin, _topic_burst)

        # .. publish 10 messages in rapid succession from a background thread ..
        publish_count = 10

        def _publish_loop() -> 'None':
            for _ in range(publish_count):
                try:
                    _ = publisher.publish(_topic_burst, 'burst-race-payload')
                except Exception:
                    pass

        publish_thread = threading.Thread(target=_publish_loop)
        publish_thread.start()

        # .. delete the subscription mid-burst ..
        try:
            _ = admin.invoke('zato.pubsub.subscription.delete', {'id': sub_id})
        except Exception as error:
            logger.warning('subscription.delete raised: %s', error)

        publish_thread.join()
        time.sleep(_settle_time)

        # .. no pending set should contain sub_key ..
        stale_keys = _scan_pending_keys_for_sub(redis, sub_key)

        assert stale_keys == [], \
            f'Stale pending entries found after burst unsub: {stale_keys}'

        # .. sub_pending:<sub_key> must not exist ..
        sub_pending_key = f'{_Sub_Pending_Prefix}{sub_key}'
        sub_pending_exists = redis.exists(sub_pending_key)

        assert sub_pending_exists == 0, \
            f'sub_pending key still exists after burst unsub: {sub_pending_key}'

        # .. re-create the subscription for test isolation.
        _recreate_subscription(admin, _topic_burst)
        time.sleep(_settle_time)

# ################################################################################################################################
# ################################################################################################################################

class TestDiskFilesCleanedAfterUnsub:
    """ Functional consequence: publish a message to a 1-subscriber topic,
    unsubscribe immediately, verify disk file is deleted.

    Gap: if a stale pending entry were left behind, the disk file would never
    be cleaned because the pending count would never reach zero. This test
    proves that after the atomic fix, disk cleanup proceeds correctly.
    """

    def test_03_disk_files_cleaned_after_unsub(self, zato_server:'any_') -> 'None':

        from zato.common.test.config_pubsub_unsub_atomic import TestConfig

        admin = _get_admin()
        publisher = _get_publisher()

        sub_id = _get_sub_id(admin, _topic_concurrent)

        # .. publish 1 message so it ends up on disk ..
        _ = publisher.publish(_topic_concurrent, 'disk-cleanup-race-payload')
        time.sleep(_settle_time)

        # .. delete the subscription (triggers unsubscribe + disk cleanup) ..
        _ = admin.invoke('zato.pubsub.subscription.delete', {'id': sub_id})
        time.sleep(_settle_time)

        # .. verify no .msg files remain for this topic ..
        pubsub_messages_dir = os.path.join(TestConfig.server_directory, 'work', 'pubsub-messages')
        topic_dir = os.path.join(pubsub_messages_dir, _topic_concurrent)

        file_count = 0

        if os.path.isdir(topic_dir):
            for _, _dirs, files in os.walk(topic_dir):
                for file_name in files:
                    if file_name.endswith('.msg'):
                        file_count += 1

        assert file_count == 0, \
            f'Expected 0 .msg files after unsub, found {file_count} in {topic_dir}'

        # .. re-create the subscription for test isolation.
        _recreate_subscription(admin, _topic_concurrent)
        time.sleep(_settle_time)

# ################################################################################################################################
# ################################################################################################################################
