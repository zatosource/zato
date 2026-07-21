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
    from zato.common.typing_ import any_, anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_sub_delete')

_settle_time = 0.5

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
    """ Verifies that subscription deletion cleans up all pub/sub database state (GAP 9):
    subscription rows both ways, pending delivery rows and retained payloads.
    """

# ################################################################################################################################

    def test_01_subscription_state_cleaned(self, zato_server:'any_') -> 'None':
        """ After subscribe + delete: the (sub_key, topic) subscription rows are gone
        from the pub/sub database in both directions.
        Proves GAP 9 fix: subscription state is removed on subscription delete.
        """
        admin = _get_admin()

        # .. find the pre-created single-topic subscription ..
        sub_key = _get_sub_key_for_topics(admin, ['sd.topic.single'])
        sub = _find_subscription_by_topics(admin, ['sd.topic.single'])

        # .. verify the subscription state exists before delete ..
        topic_name = 'sd.topic.single'

        assert topic_name in pubsub_db.get_subscribed_topics(sub_key), \
            'Expected the topic among the sub_key subscriptions before delete'
        assert sub_key in pubsub_db.get_topic_subscribers(topic_name), \
            'Expected sub_key among the topic subscribers before delete'

        # .. delete the subscription ..
        _delete_subscription(admin, sub['id'])
        time.sleep(_settle_time)

        # .. verify the subscription state is cleaned ..
        assert topic_name not in pubsub_db.get_subscribed_topics(sub_key), \
            'Expected the topic removed from the sub_key subscriptions after delete'
        assert sub_key not in pubsub_db.get_topic_subscribers(topic_name), \
            'Expected sub_key removed from the topic subscribers after delete'

        # .. verify the sub_key has no remaining subscriptions ..
        assert pubsub_db.get_subscribed_topics(sub_key) == [], \
            'Expected no subscriptions left after single-topic subscription delete'

# ################################################################################################################################

    def test_02_pending_messages_cleaned(self, zato_server:'any_') -> 'None':
        """ Publish messages, subscribe, delete sub: pending state is cleaned.
        Proves GAP 9 fix: pending delivery rows are removed on subscription delete.
        """
        admin = _get_admin()
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

        # .. verify there is pending state in the database ..
        pending_count = pubsub_db.count_pending(sub_key)

        assert pending_count > 0, \
            f'Expected pending messages before delete, got {pending_count}'

        # .. delete the subscription ..
        sub = _find_subscription_by_topics(admin, [topic_name])
        _delete_subscription(admin, sub['id'])
        time.sleep(_settle_time)

        # .. verify pending state is gone ..
        assert pubsub_db.count_pending(sub_key) == 0, \
            'Expected no delivery rows after subscription delete'

# ################################################################################################################################

    def test_03_payloads_dropped(self, zato_server:'any_') -> 'None':
        """ Publish messages, delete sub: the payloads of messages no subscriber
        needs anymore are dropped from the message rows.
        Proves GAP 9 fix: retained payloads are removed when no pending subscribers remain.
        """
        admin = _get_admin()
        publisher = _get_publisher()

        topic_name = 'sd.topic.payloads'

        # .. create a fresh topic ..
        _ = _create_topic(admin, topic_name)
        time.sleep(_settle_time)

        # .. create a subscription ..
        _ = _create_subscription(admin, [topic_name])
        time.sleep(_settle_time)

        # .. publish messages and remember their identifiers ..
        msg_ids:'strlist' = []

        for idx in range(3):
            result = publisher.publish(topic_name, f'retained-payload-{idx}-' + ('x' * 1024))
            msg_ids.append(result['msg_id'])

        time.sleep(_settle_time)

        # .. verify the payloads are retained while the messages are pending ..
        with_payload = pubsub_db.count_messages_with_payload(msg_ids)

        assert with_payload > 0, \
            'Expected retained payloads before subscription delete'

        # .. delete the subscription ..
        sub = _find_subscription_by_topics(admin, [topic_name])
        _delete_subscription(admin, sub['id'])
        time.sleep(_settle_time)

        # .. verify the payloads are dropped ..
        assert pubsub_db.count_messages_with_payload(msg_ids) == 0, \
            'Expected all payloads dropped after subscription delete'

# ################################################################################################################################

    def test_04_queue_state_removed(self, zato_server:'any_') -> 'None':
        """ After delete (with no remaining topics): neither subscription state
        nor delivery rows remain anywhere for the sub_key.
        Proves GAP 9 fix: the whole queue disappears when the subscriber has no subscriptions left.
        """
        admin = _get_admin()
        publisher = _get_publisher()

        topic_name = 'sd.topic.queue'

        # .. create a fresh topic ..
        _ = _create_topic(admin, topic_name)
        time.sleep(_settle_time)

        # .. create a subscription ..
        _ = _create_subscription(admin, [topic_name])
        time.sleep(_settle_time)

        # .. find the sub_key ..
        sub_key = _get_sub_key_for_topics(admin, [topic_name])

        # .. give the subscriber something pending ..
        _ = publisher.publish(topic_name, 'queue-state-payload')
        time.sleep(_settle_time)

        # .. verify the queue exists ..
        assert sub_key in pubsub_db.get_topic_subscribers(topic_name), \
            f'Expected subscriber {sub_key} to exist before delete'

        # .. delete the subscription ..
        sub = _find_subscription_by_topics(admin, [topic_name])
        _delete_subscription(admin, sub['id'])
        time.sleep(_settle_time)

        # .. verify the whole queue is gone ..
        assert sub_key not in pubsub_db.get_topic_subscribers(topic_name), \
            f'Expected subscriber {sub_key} to be removed after delete'
        assert pubsub_db.count_pending(sub_key) == 0, \
            'Expected no delivery rows after delete'

# ################################################################################################################################

    def test_05_multi_topic_partial(self, zato_server:'any_') -> 'None':
        """ Subscribe to 2 topics, delete sub: state cleaned for both topics.
        Proves GAP 9 fix: unsubscribe is called for every topic the sub_key belongs to.
        """
        admin = _get_admin()

        # .. find the pre-created multi-topic subscription (sd.topic.multi.first + sd.topic.multi.second) ..
        sub_key = _get_sub_key_for_topics(admin, ['sd.topic.multi.first', 'sd.topic.multi.second'])
        sub = _find_subscription_by_topics(admin, ['sd.topic.multi.first', 'sd.topic.multi.second'])

        # .. verify subscription state exists for both topics before delete ..
        assert sub_key in pubsub_db.get_topic_subscribers('sd.topic.multi.first'), \
            'Expected sub_key among subscribers of sd.topic.multi.first before delete'
        assert sub_key in pubsub_db.get_topic_subscribers('sd.topic.multi.second'), \
            'Expected sub_key among subscribers of sd.topic.multi.second before delete'

        subscribed_topics = pubsub_db.get_subscribed_topics(sub_key)
        subscribed_count = len(subscribed_topics)

        assert subscribed_count == 2, \
            f'Expected 2 subscribed topics before delete, got {subscribed_count}'

        # .. delete the subscription ..
        _delete_subscription(admin, sub['id'])
        time.sleep(_settle_time)

        # .. verify both topics are cleaned ..
        assert sub_key not in pubsub_db.get_topic_subscribers('sd.topic.multi.first'), \
            'Expected sub_key removed from subscribers of sd.topic.multi.first after delete'
        assert sub_key not in pubsub_db.get_topic_subscribers('sd.topic.multi.second'), \
            'Expected sub_key removed from subscribers of sd.topic.multi.second after delete'
        assert pubsub_db.get_subscribed_topics(sub_key) == [], \
            'Expected no subscriptions left after multi-topic subscription delete'

# ################################################################################################################################
# ################################################################################################################################
