# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
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

logger = logging.getLogger('zato.test.pubsub_endpoint_delete')

_settle_time = 0.5

_test_redis_host = 'localhost'
_test_redis_port = 6379
_test_redis_db   = PubSub.Test_Redis_DB

_Subs_Prefix        = 'zato:pubsub:subs:'
_Topic_Subs_Prefix  = 'zato:pubsub:topic_subs:'
_Stream_Prefix      = 'zato:pubsub:stream:'
_Sub_Pending_Prefix = 'zato:pubsub:sub_pending:'

# ################################################################################################################################
# ################################################################################################################################

def _get_admin() -> 'any_':
    from zato.common.test.client import AdminClient
    from zato.common.test.config_pubsub_endpoint_delete import TestConfig

    out = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
    return out

# ################################################################################################################################

def _get_publisher() -> 'any_':
    from zato.common.test.client import PublishClient
    from zato.common.test.config_pubsub_endpoint_delete import TestConfig

    out = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
    return out

# ################################################################################################################################

def _get_redis() -> 'Redis':

    out = Redis(host=_test_redis_host, port=_test_redis_port, db=_test_redis_db, decode_responses=True)
    return out

# ################################################################################################################################

def _get_subscriptions(admin:'any_') -> 'anylist':
    """ Returns all subscriptions for the test subscriber security definition.
    """
    sub_list = admin.invoke('zato.pubsub.subscription.get-list', {'cluster_id': 1})

    if isinstance(sub_list, list):
        items:'anylist' = sub_list
    else:
        items = sub_list['zato_pubsub_subscription_get_list_response']

    out:'anylist' = []

    for item in items:
        if item['sec_name'] == 'test.ed.subscriber':
            out.append(item)

    return out

# ################################################################################################################################

def _get_outgoing_rest_id(admin:'any_', connection_name:'str') -> 'int':
    """ Looks up an outgoing REST connection ID by name.
    """
    result = admin.invoke('zato.http-soap.get-list', {
        'cluster_id': 1,
        'connection': 'outgoing',
        'transport': 'plain_http',
    })

    if isinstance(result, list):
        items:'anylist' = result
    else:
        items = result['zato_http_soap_get_list_response']

    for item in items:
        if item['name'] == connection_name:

            out = item['id']
            return out

    raise Exception(f'Outgoing REST connection not found: {connection_name}')

# ################################################################################################################################

def _delete_outgoing_rest(admin:'any_', endpoint_id:'int') -> 'None':
    """ Deletes an outgoing REST connection by ID.
    """
    _ = admin.invoke('zato.http-soap.delete', {'id': endpoint_id})

# ################################################################################################################################

def _find_subscription_by_topics(admin:'any_', topic_names:'list[str]') -> 'anydict':
    """ Finds a subscription that covers exactly the given topic names.
    """
    subs = _get_subscriptions(admin)
    topic_set = set(topic_names)

    for sub in subs:
        sub_topics = sub['topic_name_list']

        sub_topic_set:'set[str]' = set()

        for entry in sub_topics:
            sub_topic_set.add(entry['topic_name'])

        if sub_topic_set == topic_set:

            out = sub
            return out

    raise Exception(f'No subscription found covering topics: {topic_names}')

# ################################################################################################################################

def _get_sub_key_for_topics(admin:'any_', topic_names:'list[str]') -> 'str':
    """ Returns the sub_key for a subscription covering the given topics.
    """
    sub = _find_subscription_by_topics(admin, topic_names)

    out = sub['sub_key']
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestEndpointDelete:
    """ Verifies that deleting an HTTPSOAP outgoing connection used as a push endpoint
    cleans up all pub/sub state (GAP 28): Redis sets, pending messages, consumer groups,
    in-memory config, and delivery greenlets.
    """

# ################################################################################################################################

    def test_01_redis_sets_cleaned(self, zato_server:'any_') -> 'None':
        """ After endpoint delete: SISMEMBER topic_subs:<topic> <sub_key> returns 0,
        SCARD subs:<sub_key> returns 0.
        Proves GAP 28 fix: Redis set memberships are removed when the REST endpoint is deleted.
        """
        admin = _get_admin()
        redis = _get_redis()

        # .. find the pre-created push subscription ..
        sub_key = _get_sub_key_for_topics(admin, ['ed.topic.push'])

        # .. verify Redis sets exist before delete ..
        topic_name = 'ed.topic.push'
        subs_key = f'{_Subs_Prefix}{sub_key}'
        topic_subs_key = f'{_Topic_Subs_Prefix}{topic_name}'

        assert redis.sismember(subs_key, topic_name) == 1, \
            'Expected sub_key to be member of subs set before delete'
        assert redis.sismember(topic_subs_key, sub_key) == 1, \
            'Expected sub_key to be member of topic_subs set before delete'

        # .. delete the outgoing REST endpoint ..
        endpoint_id = _get_outgoing_rest_id(admin, 'test.ed.out.webhook')
        _delete_outgoing_rest(admin, endpoint_id)
        time.sleep(_settle_time)

        # .. verify Redis sets are cleaned ..
        assert redis.sismember(subs_key, topic_name) == 0, \
            'Expected topic removed from subs set after endpoint delete'
        assert redis.sismember(topic_subs_key, sub_key) == 0, \
            'Expected sub_key removed from topic_subs set after endpoint delete'

        # .. verify the subs key has no remaining members ..
        assert redis.scard(subs_key) == 0, \
            'Expected subs set to be empty after endpoint delete'

# ################################################################################################################################

    def test_02_subscription_row_gone(self, zato_server:'any_') -> 'None':
        """ After endpoint delete: subscription get-list returns no matching subscription.
        Proves GAP 28 fix: ODB cascade removed the subscription row.
        """
        admin = _get_admin()

        # .. verify no subscriptions remain for the test subscriber ..
        subs = _get_subscriptions(admin)

        assert len(subs) == 0, \
            f'Expected zero subscriptions after endpoint delete, got {len(subs)}'

# ################################################################################################################################

    def test_03_in_memory_config_cleaned(self, zato_server:'any_') -> 'None':
        """ After endpoint delete: publishing a message does NOT trigger push delivery
        to the webhook receiver. Proves GAP 28 fix: in-memory config and delivery
        greenlet are stopped.
        """
        from zato.common.test.config_pubsub_endpoint_delete import TestConfig
        from zato.common.test.receiver import WebhookReceiver

        publisher = _get_publisher()

        # .. create a fresh receiver to track deliveries ..
        receiver = WebhookReceiver(TestConfig.webhook_port, TestConfig.webhook_output_directory)
        receiver.clear_output()

        # .. publish a message to the topic whose subscription was cascade-deleted ..
        _ = publisher.publish('ed.topic.push', 'should-not-be-delivered')
        time.sleep(_settle_time)

        # .. verify the webhook receiver got zero deliveries ..
        delivered_count = receiver.delivered_count()

        assert delivered_count == 0, \
            f'Expected zero push deliveries after endpoint delete, got {delivered_count}'

# ################################################################################################################################

    def test_04_pending_messages_cleaned(self, zato_server:'any_') -> 'None':
        """ Publish messages, create a new push subscription, delete the endpoint:
        sub_pending:<sub_key> key is gone from Redis.
        Proves GAP 28 fix: pending message references are removed on endpoint delete.
        """
        from zato.common.test.config_pubsub_endpoint_delete import TestConfig
        from zato.common.test.conftest_base_pubsub import find_free_port

        admin = _get_admin()
        redis = _get_redis()
        publisher = _get_publisher()

        topic_name = 'ed.topic.pending'

        # The endpoint must point at a port with no listener so push deliveries fail
        # and the published messages remain in the pending state for this test to verify.
        unreachable_port = find_free_port()

        # .. create a new outgoing REST connection for this test ..
        _ = admin.invoke('zato.http-soap.create', {
            'cluster_id': 1,
            'name': 'test.ed.out.pending',
            'connection': 'outgoing',
            'transport': 'plain_http',
            'is_active': True,
            'is_internal': False,
            'host': f'http://127.0.0.1:{unreachable_port}',
            'url_path': '/webhook',
            'data_format': 'json',
            'timeout': 30,
            'has_rbac': False,
            'sec_use_rbac': False,
            'merge_url_params_req': True,
            'url_params_pri': 'path-over-qs',
            'params_pri': 'channel-params-over-msg',
        })

        time.sleep(_settle_time)

        # .. look up the new endpoint ID ..
        endpoint_id = _get_outgoing_rest_id(admin, 'test.ed.out.pending')

        # .. create a push subscription pointing at this endpoint ..
        _ = admin.invoke('zato.pubsub.subscription.create', {
            'cluster_id': 1,
            'topic_name_list': [topic_name],
            'sec_base_id': TestConfig.subscriber_sec_base_id,
            'delivery_type': 'push',
            'push_type': 'rest',
            'rest_push_endpoint_id': endpoint_id,
            'is_pub_active': True,
            'is_delivery_active': True,
        })

        time.sleep(_settle_time)

        # .. find the sub_key ..
        sub_key = _get_sub_key_for_topics(admin, [topic_name])

        # .. publish messages so they end up pending for this subscriber ..
        for _ in range(5):
            _ = publisher.publish(topic_name, 'pending-test-payload')

        time.sleep(_settle_time)

        # .. verify there is pending state in Redis ..
        sub_pending_key = f'{_Sub_Pending_Prefix}{sub_key}'
        pending_count:'int' = redis.scard(sub_pending_key) # type: ignore[assignment]

        assert pending_count > 0, \
            f'Expected pending messages before delete, got {pending_count}'

        # .. delete the outgoing REST endpoint ..
        _delete_outgoing_rest(admin, endpoint_id)
        time.sleep(_settle_time)

        # .. verify pending state is gone ..
        assert redis.exists(sub_pending_key) == 0, \
            'Expected sub_pending key to be deleted after endpoint delete'

# ################################################################################################################################

    def test_05_consumer_group_destroyed(self, zato_server:'any_') -> 'None':
        """ Create a push subscription, delete the endpoint:
        XINFO GROUPS does not list the sub_key consumer group.
        Proves GAP 28 fix: consumer group is destroyed when the endpoint is deleted.
        """
        from zato.common.test.config_pubsub_endpoint_delete import TestConfig

        admin = _get_admin()
        redis = _get_redis()

        topic_name = 'ed.topic.push'

        # .. create a new outgoing REST connection for this test ..
        _ = admin.invoke('zato.http-soap.create', {
            'cluster_id': 1,
            'name': 'test.ed.out.cgroup',
            'connection': 'outgoing',
            'transport': 'plain_http',
            'is_active': True,
            'is_internal': False,
            'host': f'http://127.0.0.1:{TestConfig.webhook_port}',
            'url_path': '/webhook',
            'data_format': 'json',
            'timeout': 30,
            'has_rbac': False,
            'sec_use_rbac': False,
            'merge_url_params_req': True,
            'url_params_pri': 'path-over-qs',
            'params_pri': 'channel-params-over-msg',
        })

        time.sleep(_settle_time)

        # .. look up the new endpoint ID ..
        endpoint_id = _get_outgoing_rest_id(admin, 'test.ed.out.cgroup')

        # .. create a push subscription pointing at this endpoint ..
        _ = admin.invoke('zato.pubsub.subscription.create', {
            'cluster_id': 1,
            'topic_name_list': [topic_name],
            'sec_base_id': TestConfig.subscriber_sec_base_id,
            'delivery_type': 'push',
            'push_type': 'rest',
            'rest_push_endpoint_id': endpoint_id,
            'is_pub_active': True,
            'is_delivery_active': True,
        })

        time.sleep(_settle_time)

        # .. find the sub_key ..
        sub_key = _get_sub_key_for_topics(admin, [topic_name])

        # .. verify the consumer group exists ..
        stream_key = f'{_Stream_Prefix}{topic_name}'
        groups:'list' = redis.xinfo_groups(stream_key) # type: ignore[assignment]

        group_names:'list[str]' = []

        for group in groups:
            group_names.append(group['name'])

        assert sub_key in group_names, \
            f'Expected consumer group {sub_key} to exist before delete'

        # .. delete the outgoing REST endpoint ..
        _delete_outgoing_rest(admin, endpoint_id)
        time.sleep(_settle_time)

        # .. verify the consumer group is destroyed ..
        groups_after:'list' = redis.xinfo_groups(stream_key) # type: ignore[assignment]

        group_names_after:'list[str]' = []

        for group in groups_after:
            group_names_after.append(group['name'])

        assert sub_key not in group_names_after, \
            f'Expected consumer group {sub_key} to be destroyed after endpoint delete'

# ################################################################################################################################
# ################################################################################################################################
