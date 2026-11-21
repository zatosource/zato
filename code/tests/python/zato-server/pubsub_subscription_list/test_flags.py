# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager

from .conftest import Topic_Pull, Topic_Second
from .helpers import add_topic_pending, set_delivery_enabled, set_pub_enabled, sub_key_for_topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def test_inactive_topic_refuses_publication(in_process_server:'any_') -> 'None':
    """ A publication to an inactive topic of config.db is refused.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server

    parallel.pubsub_inactive_topics.add(Topic_Pull.lower())

    raised = False

    try:
        _ = parallel.pubsub_backend.publish(Topic_Pull, 'inactive.' + CryptoManager.generate_hex_string(8))
    except Exception:
        raised = True

    assert raised

    parallel.pubsub_inactive_topics.discard(Topic_Pull.lower())

# ################################################################################################################################

def test_inactive_topic_keeps_queued_messages(in_process_server:'any_') -> 'None':
    """ Messages already queued for a topic that is later deactivated remain fetchable.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server
    backend = parallel.pubsub_backend
    subscription_list = parallel.pubsub_subscription_list

    sub_key = sub_key_for_topic(subscription_list, Topic_Pull)
    data = 'queued.before.' + CryptoManager.generate_hex_string(8)

    result = backend.publish(Topic_Pull, data)
    assert result.msg_id

    parallel.pubsub_inactive_topics.add(Topic_Pull.lower())

    messages = backend.fetch_messages(sub_key, max_messages=10)

    found = False

    for message in messages:
        if message['data'] == data:
            found = True
            break

    assert found

    parallel.pubsub_inactive_topics.discard(Topic_Pull.lower())

# ################################################################################################################################

def test_is_pub_active_off_refuses_every_topic(in_process_server:'any_') -> 'None':
    """ A subscriber with is_pub_active off is refused on every topic.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server
    subscription_list = parallel.pubsub_subscription_list

    sub_key = sub_key_for_topic(subscription_list, Topic_Pull)
    add_topic_pending(subscription_list, sub_key, Topic_Second)

    topics = {}
    for topic_name in subscription_list.topics_of(sub_key):
        topics[topic_name] = {
            'is_pub_enabled': True,
            'is_delivery_enabled': True,
        }

    _ = subscription_list.set_topics(sub_key, False, topics)

    assert not subscription_list.is_publish_allowed(sub_key, Topic_Pull.lower())
    assert not subscription_list.is_publish_allowed(sub_key, Topic_Second.lower())

# ################################################################################################################################

def test_is_pub_enabled_off_refuses_that_topic_only(in_process_server:'any_') -> 'None':
    """ is_pub_enabled off refuses the client on that topic only.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server
    subscription_list = parallel.pubsub_subscription_list

    sub_key = sub_key_for_topic(subscription_list, Topic_Pull)
    add_topic_pending(subscription_list, sub_key, Topic_Second)
    set_pub_enabled(subscription_list, sub_key, Topic_Second, False)

    assert subscription_list.is_publish_allowed(sub_key, Topic_Pull.lower())
    assert not subscription_list.is_publish_allowed(sub_key, Topic_Second.lower())

# ################################################################################################################################

def test_is_delivery_enabled_off_withholds_messages(in_process_server:'any_') -> 'None':
    """ is_delivery_enabled off withholds that topic's messages from a fetch while the depth still counts them.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server
    backend = parallel.pubsub_backend
    subscription_list = parallel.pubsub_subscription_list

    sub_key = sub_key_for_topic(subscription_list, Topic_Pull)
    add_topic_pending(subscription_list, sub_key, Topic_Second)

    _ = backend.sync_subscription_pairs([(sub_key, Topic_Second.lower())], [])
    subscription_list.mark_committed([(sub_key, Topic_Second.lower())], [])

    data_pull = 'delivery.off.pull.' + CryptoManager.generate_hex_string(8)
    data_second = 'delivery.off.second.' + CryptoManager.generate_hex_string(8)

    _ = backend.publish(Topic_Pull, data_pull)
    _ = backend.publish(Topic_Second, data_second)

    set_delivery_enabled(subscription_list, sub_key, Topic_Second, False)

    delivered = subscription_list.delivered_topics(sub_key)
    assert Topic_Pull.lower() in delivered
    assert Topic_Second.lower() not in delivered

    messages = backend.fetch_messages(sub_key, max_messages=20)

    for message in messages:
        assert message['topic_name'] != Topic_Second.lower()

    assert not subscription_list.withholds_pair(sub_key, Topic_Second.lower())

    depths = backend.get_pending_depths([(sub_key, Topic_Second.lower())])
    assert depths[sub_key] > 0

# ################################################################################################################################
# ################################################################################################################################
