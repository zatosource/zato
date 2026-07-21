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

logger = logging.getLogger('zato.test.pubsub_sub_delete_mismatch')

_settle_time = 0.5

_security_name = 'test.mismatch.security.subscriber'

# ################################################################################################################################
# ################################################################################################################################

def _get_admin() -> 'any_':
    from zato.common.test.client import AdminClient
    from zato.common.test.config_pubsub_sub_delete_mismatch import TestConfig
    admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
    return admin

# ################################################################################################################################

def _get_publisher() -> 'any_':
    from zato.common.test.client import PublishClient
    from zato.common.test.config_pubsub_sub_delete_mismatch import TestConfig
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
    subs = _get_subscriptions(admin, _security_name)
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
    from zato.common.test.config_pubsub_sub_delete_mismatch import TestConfig

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

class TestSubscriptionDeleteMismatch:
    """ Verifies that subscription deletion works correctly when the security
    definition's name and username are different values. Before the fix,
    the Delete handler swapped pubsub_msg.username and pubsub_msg.sec_name,
    causing remove_user to receive the security name instead of the credential username.
    """

# ################################################################################################################################

    def test_01_delete_cleans_subscription_state(self, zato_server:'any_') -> 'None':
        """ Delete a subscription whose security definition has name != username,
        verify that the pub/sub database state is cleaned up correctly.
        """
        admin = _get_admin()

        topic_name = 'mismatch.topic.delete'

        # .. find the pre-created subscription ..
        sub_key = _get_sub_key_for_topics(admin, [topic_name])
        sub = _find_subscription_by_topics(admin, [topic_name])

        # .. verify the subscription state exists before delete ..
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

        # .. verify the sub_key has no remaining subscriptions.
        assert pubsub_db.get_subscribed_topics(sub_key) == [], \
            'Expected no subscriptions left after subscription delete'

# ################################################################################################################################

    def test_02_resubscribe_gets_fresh_sub_key(self, zato_server:'any_') -> 'None':
        """ Delete a subscription and re-create it for the same user,
        verify a fresh sub_key is assigned. If remove_user received the
        wrong identifier, the stale _username_to_sub_key mapping would
        cause get_or_create_sub_key to return the old sub_key.
        """
        admin = _get_admin()

        topic_name = 'mismatch.topic.resub'

        # .. create a fresh topic ..
        _ = _create_topic(admin, topic_name)
        time.sleep(_settle_time)

        # .. create the first subscription ..
        _ = _create_subscription(admin, [topic_name])
        time.sleep(_settle_time)

        # .. record the first sub_key ..
        first_sub_key = _get_sub_key_for_topics(admin, [topic_name])
        first_sub = _find_subscription_by_topics(admin, [topic_name])

        # .. delete it ..
        _delete_subscription(admin, first_sub['id'])
        time.sleep(_settle_time)

        # .. create a second subscription for the same user and topic ..
        _ = _create_subscription(admin, [topic_name])
        time.sleep(_settle_time)

        # .. the new subscription must have a different sub_key.
        second_sub_key = _get_sub_key_for_topics(admin, [topic_name])

        assert second_sub_key != first_sub_key, \
            f'Expected fresh sub_key after delete, got same: {first_sub_key}'

# ################################################################################################################################

    def test_03_publish_after_resubscribe(self, zato_server:'any_') -> 'None':
        """ Full round-trip: subscribe, publish, delete, re-subscribe, publish again.
        Proves the create-delete-recreate cycle works when name != username.
        """
        admin = _get_admin()
        publisher = _get_publisher()

        topic_name = 'mismatch.topic.roundtrip'

        # .. create a fresh topic ..
        _ = _create_topic(admin, topic_name)
        time.sleep(_settle_time)

        # .. create the first subscription ..
        _ = _create_subscription(admin, [topic_name])
        time.sleep(_settle_time)

        # .. publish a message ..
        _ = publisher.publish(topic_name, 'first-message')
        time.sleep(_settle_time)

        # .. delete the subscription ..
        first_sub = _find_subscription_by_topics(admin, [topic_name])
        _delete_subscription(admin, first_sub['id'])
        time.sleep(_settle_time)

        # .. re-subscribe ..
        _ = _create_subscription(admin, [topic_name])
        time.sleep(_settle_time)

        # .. publish another message after re-subscribe ..
        _ = publisher.publish(topic_name, 'second-message')
        time.sleep(_settle_time)

        # .. verify the subscription exists and is active.
        second_sub = _find_subscription_by_topics(admin, [topic_name])

        assert second_sub['sub_key'], \
            'Expected re-created subscription to have a valid sub_key'

# ################################################################################################################################
# ################################################################################################################################
