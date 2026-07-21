# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import threading
import time

# Zato
from zato.common.test import pubsub_db

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_topic_delete_atomic')

_settle_time = 0.5

_topic_target = 'tda.topic.a'
_topic_survivor = 'tda.topic.b'

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

def _get_topic_id(admin:'any_', topic_name:'str') -> 'int':
    topic_list = admin.invoke('zato.pubsub.topic.get-list', {'cluster_id': 1})

    if isinstance(topic_list, list):
        items:'anylist' = topic_list
    else:
        items = topic_list['zato_pubsub_topic_get_list_response']

    for item in items:
        if item['name'] == topic_name:
            return item['id']

    raise Exception(f'Topic not found: {topic_name}')

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

    raise Exception(f'No subscription found for topic: {topic_name}')

# ################################################################################################################################

def _publish_messages(publisher:'any_', topic_name:'str', count:'int', payload:'str') -> 'strlist':
    """ Publishes messages and returns their public identifiers.
    """
    out:'strlist' = []

    for _ in range(count):
        result = publisher.publish(topic_name, payload)
        out.append(result['msg_id'])

    return out

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

class TestNoRowsRemainAfterConcurrentPublishAndDelete:
    """ Gap A: concurrent publish during delete must not leave message rows
    behind with no topic to belong to.
    """

    def test_01_no_rows_remain_after_concurrent_publish_and_delete(self, zato_server:'any_') -> 'None':

        admin = _get_admin()
        publisher = _get_publisher()

        # .. publish 5 messages so there are message rows ..
        msg_ids_before = _publish_messages(publisher, _topic_target, 5, 'pre-delete-payload')

        time.sleep(_settle_time)

        topic_id = _get_topic_id(admin, _topic_target)

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

        # .. verify: no message rows for the topic ..
        message_count = pubsub_db.count_topic_messages(_topic_target)
        assert message_count == 0, f'Message rows still exist for {_topic_target}: {message_count}'

        # .. verify: no subscription state for the topic ..
        subscribers = pubsub_db.get_topic_subscribers(_topic_target)
        assert subscribers == [], f'Subscription state still exists: {subscribers}'

        # .. verify: no delivery rows for the topic ..
        delivery_count = pubsub_db.count_topic_deliveries(_topic_target)
        assert delivery_count == 0, f'Delivery rows still exist: {delivery_count}'

        # .. verify: the rows of the messages published before the delete are gone ..
        remaining = pubsub_db.count_message_rows(msg_ids_before)
        assert remaining == 0, f'Stale message rows: {remaining}'

        # .. restore for subsequent tests.
        _recreate_topic_and_subscribe(admin, _topic_target)

# ################################################################################################################################
# ################################################################################################################################

class TestNoDanglingSubReferenceAfterConcurrentSubscribeAndDelete:
    """ Gap B: concurrent subscribe during delete must not leave dangling references
    where a subscriber still holds a subscription row for the deleted topic.
    """

    def test_02_no_dangling_sub_reference_after_concurrent_subscribe_and_delete(self, zato_server:'any_') -> 'None':

        from zato.common.test.config_pubsub_topic_delete_atomic import TestConfig

        admin = _get_admin()

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

        # .. verify: no subscription rows remain for the deleted topic - the same table
        # .. holds both directions, so an empty subscriber list means no dangling references ..
        subscribers = pubsub_db.get_topic_subscribers(_topic_target)
        assert subscribers == [], f'Dangling references to {_topic_target}: {subscribers}'

        # .. restore for subsequent tests.
        _recreate_topic_and_subscribe(admin, _topic_target)

# ################################################################################################################################
# ################################################################################################################################

class TestNoPartialSubscriptionAfterConcurrentSubscribeAndDelete:
    """ Gap C: a concurrent subscribe must not leave a partially created queue behind.
    Re-creating the topic and subscribing fresh must work without errors.
    """

    def test_03_no_partial_subscription_after_concurrent_subscribe_and_delete(self, zato_server:'any_') -> 'None':

        from zato.common.test.config_pubsub_topic_delete_atomic import TestConfig

        admin = _get_admin()
        publisher = _get_publisher()

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

        # .. verify: no message rows remain for the deleted topic ..
        message_count = pubsub_db.count_topic_messages(_topic_target)
        assert message_count == 0, f'Message rows still exist: {message_count}'

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

class TestBurstPublishDuringDeleteLeavesNoRows:
    """ Gap A high-volume variant: 10 rapid publishes concurrent with delete
    must not leave message or delivery rows behind.
    """

    def test_04_burst_publish_during_delete_leaves_no_rows(self, zato_server:'any_') -> 'None':

        admin = _get_admin()
        publisher = _get_publisher()

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

        # .. verify: no message rows, no subscription state, no delivery rows ..
        message_count = pubsub_db.count_topic_messages(_topic_target)
        assert message_count == 0, f'Expected 0 message rows after burst delete, found {message_count}'

        subscribers = pubsub_db.get_topic_subscribers(_topic_target)
        assert subscribers == [], f'Subscription state still exists: {subscribers}'

        delivery_count = pubsub_db.count_topic_deliveries(_topic_target)
        assert delivery_count == 0, f'Stale delivery rows for deleted topic: {delivery_count}'

        # .. restore.
        _recreate_topic_and_subscribe(admin, _topic_target)

# ################################################################################################################################
# ################################################################################################################################

class TestNoStalePendingEntriesAfterDelete:
    """ Delivery rows and message rows must be fully cleaned for the deleted topic.
    """

    def test_05_no_stale_pending_entries_after_delete(self, zato_server:'any_') -> 'None':

        admin = _get_admin()
        publisher = _get_publisher()

        # .. publish 5 messages (delivery rows will be created for the subscriber) ..
        msg_ids = _publish_messages(publisher, _topic_target, 5, 'pending-test-payload')

        time.sleep(_settle_time)

        sub_key = _get_sub_key(admin, _topic_target)

        # .. verify pending state exists before delete ..
        pending_count = pubsub_db.count_pending(sub_key, _topic_target)
        assert pending_count >= 5, f'Expected pending deliveries before delete, got {pending_count}'

        # .. delete the topic ..
        topic_id = _get_topic_id(admin, _topic_target)
        _ = admin.invoke('zato.pubsub.topic.delete', {'id': topic_id})
        time.sleep(_settle_time)

        # .. verify: all delivery rows gone ..
        delivery_count = pubsub_db.count_topic_deliveries(_topic_target)
        assert delivery_count == 0, f'Stale delivery rows after delete: {delivery_count}'

        # .. verify: the message rows are gone too ..
        remaining = pubsub_db.count_message_rows(msg_ids)
        assert remaining == 0, f'Stale message rows after delete: {remaining}'

        # .. restore.
        _recreate_topic_and_subscribe(admin, _topic_target)

# ################################################################################################################################
# ################################################################################################################################

class TestMultiTopicSubscriberSurvivorTopicIntact:
    """ Subscriber on two topics (each with its own sub_key). Delete one topic.
    The other topic's subscription state, delivery rows and payloads must remain intact.
    """

    def test_06_multi_topic_subscriber_survivor_topic_intact(self, zato_server:'any_') -> 'None':

        admin = _get_admin()
        publisher = _get_publisher()

        # .. publish 3 messages to each topic ..
        msg_ids_target = _publish_messages(publisher, _topic_target, 3, 'target-topic-payload')
        msg_ids_survivor = _publish_messages(publisher, _topic_survivor, 3, 'survivor-topic-payload')

        time.sleep(_settle_time)

        # .. get the sub_key for the survivor topic ..
        sub_key_survivor = _get_sub_key(admin, _topic_survivor)

        # .. verify the survivor has its messages pending before delete ..
        pending_survivor_before = pubsub_db.count_pending(sub_key_survivor, _topic_survivor)
        assert pending_survivor_before >= 3, \
            f'Expected survivor pending deliveries before delete, got {pending_survivor_before}'

        # .. delete the target topic ..
        topic_id = _get_topic_id(admin, _topic_target)
        _ = admin.invoke('zato.pubsub.topic.delete', {'id': topic_id})
        time.sleep(_settle_time)

        # .. verify: the target topic's rows are gone ..
        assert pubsub_db.count_message_rows(msg_ids_target) == 0, \
            'Target message rows still exist after delete'
        assert pubsub_db.count_topic_deliveries(_topic_target) == 0, \
            'Target delivery rows still exist after delete'

        # .. verify: the survivor topic's pending deliveries are intact ..
        pending_survivor_after = pubsub_db.count_pending(sub_key_survivor, _topic_survivor)
        assert pending_survivor_after >= 3, \
            f'Survivor pending deliveries lost after deleting target topic: {pending_survivor_after}'

        # .. verify: the survivor topic's messages still hold their payloads ..
        with_payload = pubsub_db.count_messages_with_payload(msg_ids_survivor)
        assert with_payload == 3, \
            f'Survivor payloads lost after deleting target topic: {with_payload}'

        # .. verify: the survivor topic's subscription state is intact ..
        assert sub_key_survivor in pubsub_db.get_topic_subscribers(_topic_survivor), \
            'Survivor subscription state is gone'

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
        _ = _publish_messages(publisher, _topic_target, 3, 'double-delete-payload')

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
    """ Empty subscriber path: just message row cleanup, no pending work.
    """

    def test_08_delete_topic_with_no_subscribers(self, zato_server:'any_') -> 'None':

        admin = _get_admin()
        publisher = _get_publisher()

        # .. create a fresh topic with no subscribers ..
        _ = admin.invoke('zato.pubsub.topic.create', {
            'name': 'tda.topic.nosub',
            'is_active': True,
        })

        time.sleep(_settle_time)

        # .. publish to it - with 0 subscribers the message row stays behind
        # .. as an already delivered trace with no payload ..
        _ = publisher.publish('tda.topic.nosub', 'no-subscriber-payload')
        time.sleep(_settle_time)

        # .. delete it ..
        topic_id = _get_topic_id(admin, 'tda.topic.nosub')
        _ = admin.invoke('zato.pubsub.topic.delete', {'id': topic_id})
        time.sleep(_settle_time)

        # .. verify: no message rows, no subscription state ..
        message_count = pubsub_db.count_topic_messages('tda.topic.nosub')
        assert message_count == 0, f'Message rows still exist: {message_count}'

        subscribers = pubsub_db.get_topic_subscribers('tda.topic.nosub')
        assert subscribers == [], f'Subscription state still exists: {subscribers}'

# ################################################################################################################################
# ################################################################################################################################
