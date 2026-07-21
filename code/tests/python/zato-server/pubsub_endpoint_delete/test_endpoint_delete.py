# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import time

# Zato
from zato.common.test import pubsub_db

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_endpoint_delete')

_settle_time = 0.5

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
    cleans up all pub/sub state (GAP 28): subscription rows, pending delivery rows,
    in-memory config, and delivery greenlets.
    """

# ################################################################################################################################

    def test_01_subscription_state_cleaned(self, zato_server:'any_') -> 'None':
        """ After endpoint delete: the (sub_key, topic) subscription rows are gone
        from the pub/sub database in both directions.
        Proves GAP 28 fix: subscription state is removed when the REST endpoint is deleted.
        """
        admin = _get_admin()

        # .. find the pre-created push subscription ..
        sub_key = _get_sub_key_for_topics(admin, ['ed.topic.push'])

        # .. verify the subscription state exists before delete ..
        topic_name = 'ed.topic.push'

        assert topic_name in pubsub_db.get_subscribed_topics(sub_key), \
            'Expected the topic among the sub_key subscriptions before delete'
        assert sub_key in pubsub_db.get_topic_subscribers(topic_name), \
            'Expected sub_key among the topic subscribers before delete'

        # .. delete the outgoing REST endpoint ..
        endpoint_id = _get_outgoing_rest_id(admin, 'test.ed.out.webhook')
        _delete_outgoing_rest(admin, endpoint_id)
        time.sleep(_settle_time)

        # .. verify the subscription state is cleaned ..
        assert topic_name not in pubsub_db.get_subscribed_topics(sub_key), \
            'Expected the topic removed from the sub_key subscriptions after endpoint delete'
        assert sub_key not in pubsub_db.get_topic_subscribers(topic_name), \
            'Expected sub_key removed from the topic subscribers after endpoint delete'

        # .. verify the sub_key has no remaining subscriptions ..
        assert pubsub_db.get_subscribed_topics(sub_key) == [], \
            'Expected no subscriptions left after endpoint delete'

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
        no delivery rows remain for the sub_key.
        Proves GAP 28 fix: pending delivery rows are removed on endpoint delete.
        """
        from zato.common.test.config_pubsub_endpoint_delete import TestConfig
        from zato.common.test.conftest_base_pubsub import find_free_port

        admin = _get_admin()
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

        # .. verify there is pending state in the database ..
        pending_count = pubsub_db.count_pending(sub_key)

        assert pending_count > 0, \
            f'Expected pending messages before delete, got {pending_count}'

        # .. delete the outgoing REST endpoint ..
        _delete_outgoing_rest(admin, endpoint_id)
        time.sleep(_settle_time)

        # .. verify pending state is gone ..
        assert pubsub_db.count_pending(sub_key) == 0, \
            'Expected no delivery rows after endpoint delete'

# ################################################################################################################################

    def test_05_queue_state_removed(self, zato_server:'any_') -> 'None':
        """ Create a push subscription, delete the endpoint: the subscriber
        disappears from the topic and holds no delivery rows.
        Proves GAP 28 fix: the whole queue is removed when the endpoint is deleted.
        """
        from zato.common.test.config_pubsub_endpoint_delete import TestConfig

        admin = _get_admin()

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

        # .. verify the subscriber is registered with the topic ..
        assert sub_key in pubsub_db.get_topic_subscribers(topic_name), \
            f'Expected subscriber {sub_key} to exist before delete'

        # .. delete the outgoing REST endpoint ..
        _delete_outgoing_rest(admin, endpoint_id)
        time.sleep(_settle_time)

        # .. verify the whole queue is gone ..
        assert sub_key not in pubsub_db.get_topic_subscribers(topic_name), \
            f'Expected subscriber {sub_key} to be removed after endpoint delete'
        assert pubsub_db.count_pending(sub_key) == 0, \
            'Expected no delivery rows after endpoint delete'

# ################################################################################################################################
# ################################################################################################################################
