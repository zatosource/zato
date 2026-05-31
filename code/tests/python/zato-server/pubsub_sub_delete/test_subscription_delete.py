# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import time

# redis
from redis import Redis

# Zato
from zato.common.api import PubSub

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_sub_delete')

_settle_time = 0.5

_test_redis_host = 'localhost'
_test_redis_port = 6379
_test_redis_db   = PubSub.Test_Redis_DB

_Subs_Prefix        = 'zato:pubsub:subs:'
_Topic_Subs_Prefix  = 'zato:pubsub:topic_subs:'
_Stream_Prefix      = 'zato:pubsub:stream:'
_Sub_Pending_Prefix = 'zato:pubsub:sub_pending:'
_Pending_Prefix     = 'zato:pubsub:pending:'
_Pending_Expiry_Key = 'zato:pubsub:pending_expiry'

# ################################################################################################################################
# ################################################################################################################################

def _get_admin() -> 'any_':
    from zato.common.test.client import AdminClient
    from zato.common.test.config_pubsub_sub_delete import TestConfig
    admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
    return admin

# ################################################################################################################################

def _get_publisher() -> 'any_':
    from zato.common.test.client import PublishClient
    from zato.common.test.config_pubsub_sub_delete import TestConfig
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

def _find_subscription_by_topics(admin:'any_', topic_names:'list[str]') -> 'anydict':
    """ Finds a subscription that covers exactly the given topic names.
    """
    subs = _get_subscriptions(admin, 'test.sd.subscriber')
    topic_set = set(topic_names)

    for sub in subs:
        sub_topics = sub['topic_name_list']
        sub_topic_set = {item['topic_name'] for item in sub_topics}

        if sub_topic_set == topic_set:
            return sub

    raise Exception(f'No subscription found covering topics: {topic_names}')

# ################################################################################################################################

def _get_sub_key_for_topics(admin:'any_', topic_names:'list[str]') -> 'str':
    """ Returns the sub_key for a subscription covering the given topics.
    """
    sub = _find_subscription_by_topics(admin, topic_names)
    out = sub['sub_key']
    return out

# ################################################################################################################################

def _create_topic(admin:'any_', topic_name:'str') -> 'int':
    """ Creates a topic and returns its ID.
    """
    response = admin.invoke('zato.pubsub.topic.create', {
        'name': topic_name,
        'is_active': True,
    })
    out = response['id']
    return out

# ################################################################################################################################

def _create_subscription(admin:'any_', topic_names:'list[str]') -> 'anydict':
    """ Creates a pull subscription for the given topics.
    """
    from zato.common.test.config_pubsub_sub_delete import TestConfig

    response = admin.invoke('zato.pubsub.subscription.create', {
        'cluster_id': 1,
        'topic_name_list': topic_names,
        'sec_base_id': TestConfig.subscriber_sec_base_id,
        'delivery_type': 'pull',
    })

    return response

# ################################################################################################################################

def _delete_subscription(admin:'any_', sub_id:'int') -> 'None':
    """ Deletes a subscription by ID.
    """
    _ = admin.invoke('zato.pubsub.subscription.delete', {'id': sub_id})

# ################################################################################################################################
# ################################################################################################################################

class TestSubscriptionDelete:
    """ Verifies that subscription deletion cleans up all Redis state (GAP 9):
    subscriber set membership, topic subscriber sets, pending messages,
    disk payload files, and consumer groups.
    """

# ################################################################################################################################

    def test_01_redis_sets_cleaned(self, zato_server:'any_') -> 'None':
        """ After subscribe + delete: SISMEMBER zato:pubsub:topic_subs:<topic> <sub_key>
        returns 0, SCARD zato:pubsub:subs:<sub_key> returns 0.
        Proves GAP 9 fix: Redis set memberships are removed on subscription delete.
        """
        admin = _get_admin()
        redis = _get_redis()

        # .. find the pre-created single-topic subscription ..
        sub_key = _get_sub_key_for_topics(admin, ['sd.topic.alpha'])
        sub = _find_subscription_by_topics(admin, ['sd.topic.alpha'])

        # .. verify Redis sets exist before delete ..
        topic_name_lower = 'sd.topic.alpha'
        subs_key = f'{_Subs_Prefix}{sub_key}'
        topic_subs_key = f'{_Topic_Subs_Prefix}{topic_name_lower}'

        assert redis.sismember(subs_key, topic_name_lower) == 1, \
            'Expected sub_key to be member of subs set before delete'
        assert redis.sismember(topic_subs_key, sub_key) == 1, \
            'Expected sub_key to be member of topic_subs set before delete'

        # .. delete the subscription ..
        _delete_subscription(admin, sub['id'])
        time.sleep(_settle_time)

        # .. verify Redis sets are cleaned ..
        assert redis.sismember(subs_key, topic_name_lower) == 0, \
            'Expected topic removed from subs set after delete'
        assert redis.sismember(topic_subs_key, sub_key) == 0, \
            'Expected sub_key removed from topic_subs set after delete'

        # .. verify the subs key has no remaining members ..
        assert redis.scard(subs_key) == 0, \
            'Expected subs set to be empty after single-topic subscription delete'

# ################################################################################################################################

    def test_02_pending_messages_cleaned(self, zato_server:'any_') -> 'None':
        """ Publish messages, subscribe, delete sub: pending state is cleaned.
        Proves GAP 9 fix: pending message references are removed on subscription delete.
        """
        admin = _get_admin()
        redis = _get_redis()
        publisher = _get_publisher()

        topic_name = 'sd.topic.pending'

        # .. create a fresh topic ..
        _ = _create_topic(admin, topic_name)
        time.sleep(_settle_time)

        # .. create a subscription ..
        _ = _create_subscription(admin, [topic_name])
        time.sleep(_settle_time)

        # .. find the sub_key ..
        sub_key = _get_sub_key_for_topics(admin, [topic_name])

        # .. publish messages so they end up pending for this subscriber ..
        for idx in range(5):
            _ = publisher.publish(topic_name, f'pending-test-payload-{idx}')

        time.sleep(_settle_time)

        # .. verify there is pending state in Redis ..
        sub_pending_key = f'{_Sub_Pending_Prefix}{sub_key}'
        pending_count:'int' = redis.scard(sub_pending_key) # type: ignore[assignment]

        # .. the messages should be in the sub's pending set ..
        assert pending_count > 0, \
            f'Expected pending messages before delete, got {pending_count}'

        # .. delete the subscription ..
        sub = _find_subscription_by_topics(admin, [topic_name])
        _delete_subscription(admin, sub['id'])
        time.sleep(_settle_time)

        # .. verify pending state is gone ..
        assert redis.exists(sub_pending_key) == 0, \
            'Expected sub_pending key to be deleted after subscription delete'

# ################################################################################################################################

    def test_03_disk_payloads_cleaned(self, zato_server:'any_') -> 'None':
        """ Publish messages (trigger disk spill), delete sub: payload files are gone.
        Proves GAP 9 fix: disk payload files are removed when no pending subscribers remain.
        """
        admin = _get_admin()
        redis = _get_redis()
        publisher = _get_publisher()

        from zato.common.test.config_pubsub_sub_delete import TestConfig

        topic_name = 'sd.topic.disk'

        # .. create a fresh topic ..
        _ = _create_topic(admin, topic_name)
        time.sleep(_settle_time)

        # .. create a subscription ..
        _ = _create_subscription(admin, [topic_name])
        time.sleep(_settle_time)

        # .. find the sub_key ..
        sub_key = _get_sub_key_for_topics(admin, [topic_name])

        # .. publish messages (they will be stored on disk) ..
        for idx in range(3):
            _ = publisher.publish(topic_name, f'disk-payload-{idx}-' + ('x' * 1024))

        time.sleep(_settle_time)

        # .. collect data_refs from the sub_pending set ..
        sub_pending_key = f'{_Sub_Pending_Prefix}{sub_key}'
        data_refs:'set' = redis.smembers(sub_pending_key) # type: ignore[assignment]

        assert len(data_refs) > 0, \
            'Expected data_refs in sub_pending before delete'

        # .. verify disk files exist ..
        pubsub_messages_dir = os.path.join(TestConfig.server_directory, 'work', 'pubsub-messages')
        existing_files = []

        for data_ref in data_refs:
            file_path = os.path.join(pubsub_messages_dir, data_ref)
            if os.path.exists(file_path):
                existing_files.append(file_path)

        assert len(existing_files) > 0, \
            'Expected disk files to exist before subscription delete'

        # .. delete the subscription ..
        sub = _find_subscription_by_topics(admin, [topic_name])
        _delete_subscription(admin, sub['id'])
        time.sleep(_settle_time)

        # .. verify disk files are gone ..
        for file_path in existing_files:
            assert not os.path.exists(file_path), \
                f'Expected disk file to be deleted: {file_path}'

# ################################################################################################################################

    def test_04_consumer_group_destroyed(self, zato_server:'any_') -> 'None':
        """ After delete (with no remaining topics): XINFO GROUPS does not list the sub_key consumer group.
        Proves GAP 9 fix: consumer group is destroyed when subscriber has no remaining subscriptions.
        """
        admin = _get_admin()
        redis = _get_redis()

        topic_name = 'sd.topic.cgroup'

        # .. create a fresh topic ..
        _ = _create_topic(admin, topic_name)
        time.sleep(_settle_time)

        # .. create a subscription ..
        _ = _create_subscription(admin, [topic_name])
        time.sleep(_settle_time)

        # .. find the sub_key ..
        sub_key = _get_sub_key_for_topics(admin, [topic_name])

        # .. verify the consumer group exists ..
        stream_key = f'{_Stream_Prefix}{topic_name}'
        groups:'list' = redis.xinfo_groups(stream_key) # type: ignore[assignment]
        group_names = [group['name'] for group in groups]

        assert sub_key in group_names, \
            f'Expected consumer group {sub_key} to exist before delete'

        # .. delete the subscription ..
        sub = _find_subscription_by_topics(admin, [topic_name])
        _delete_subscription(admin, sub['id'])
        time.sleep(_settle_time)

        # .. verify the consumer group is destroyed ..
        groups_after:'list' = redis.xinfo_groups(stream_key) # type: ignore[assignment]
        group_names_after = [group['name'] for group in groups_after]

        assert sub_key not in group_names_after, \
            f'Expected consumer group {sub_key} to be destroyed after delete'

# ################################################################################################################################

    def test_05_multi_topic_partial(self, zato_server:'any_') -> 'None':
        """ Subscribe to 2 topics, delete sub: Redis cleaned for both topics.
        Proves GAP 9 fix: unsubscribe is called for every topic the sub_key belongs to.
        """
        admin = _get_admin()
        redis = _get_redis()

        # .. find the pre-created multi-topic subscription (sd.topic.beta + sd.topic.gamma) ..
        sub_key = _get_sub_key_for_topics(admin, ['sd.topic.beta', 'sd.topic.gamma'])
        sub = _find_subscription_by_topics(admin, ['sd.topic.beta', 'sd.topic.gamma'])

        # .. verify Redis sets exist for both topics before delete ..
        topic_beta_subs_key = f'{_Topic_Subs_Prefix}sd.topic.beta'
        topic_gamma_subs_key = f'{_Topic_Subs_Prefix}sd.topic.gamma'
        subs_key = f'{_Subs_Prefix}{sub_key}'

        assert redis.sismember(topic_beta_subs_key, sub_key) == 1, \
            'Expected sub_key in topic_subs for sd.topic.beta before delete'
        assert redis.sismember(topic_gamma_subs_key, sub_key) == 1, \
            'Expected sub_key in topic_subs for sd.topic.gamma before delete'
        assert redis.scard(subs_key) == 2, \
            'Expected 2 topics in subs set before delete'

        # .. delete the subscription ..
        _delete_subscription(admin, sub['id'])
        time.sleep(_settle_time)

        # .. verify both topics are cleaned from Redis ..
        assert redis.sismember(topic_beta_subs_key, sub_key) == 0, \
            'Expected sub_key removed from topic_subs for sd.topic.beta after delete'
        assert redis.sismember(topic_gamma_subs_key, sub_key) == 0, \
            'Expected sub_key removed from topic_subs for sd.topic.gamma after delete'
        assert redis.scard(subs_key) == 0, \
            'Expected subs set to be empty after multi-topic subscription delete'

# ################################################################################################################################
# ################################################################################################################################
