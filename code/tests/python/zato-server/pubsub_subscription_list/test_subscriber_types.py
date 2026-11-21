# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager
from zato_common_core.zato_common_core import SubscriptionList

from .conftest import Topic_Pull, Topic_Push_Rest, Topic_Push_Service, Topic_Second
from .helpers import add_topic_pending, remove_topic_pending, set_delivery_enabled, status_of, sub_key_for_topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def _publish_confirms_pending(parallel:'any_', topic_name:'str') -> 'None':
    """ A pending addition of Topic_Second for the subscriber of topic_name is confirmed by a publication.
    """
    subscription_list = parallel.pubsub_subscription_list
    backend = parallel.pubsub_backend

    sub_key = sub_key_for_topic(subscription_list, topic_name)
    add_topic_pending(subscription_list, sub_key, Topic_Second)

    assert status_of(subscription_list, sub_key, Topic_Second) == SubscriptionList.STATUS_PENDING

    data = 'pending.add.' + CryptoManager.generate_hex_string(8)
    result = backend.publish(Topic_Second, data)

    assert result.msg_id
    assert status_of(subscription_list, sub_key, Topic_Second) == SubscriptionList.STATUS_CONFIRMED

# ################################################################################################################################

def _removal_skips_publication_and_withholds_fetch(parallel:'any_', topic_name:'str') -> 'None':
    """ A pending removal skips the subscriber on a publication and withholds its queued messages from a fetch.
    """
    subscription_list = parallel.pubsub_subscription_list
    backend = parallel.pubsub_backend

    sub_key = sub_key_for_topic(subscription_list, topic_name)
    data = 'before.removal.' + CryptoManager.generate_hex_string(8)

    _ = backend.publish(topic_name, data)

    remove_topic_pending(subscription_list, sub_key, topic_name)

    assert status_of(subscription_list, sub_key, topic_name) == SubscriptionList.STATUS_PENDING_REMOVAL
    assert subscription_list.withholds_pair(sub_key, topic_name.lower())

    after = 'after.removal.' + CryptoManager.generate_hex_string(8)
    result = backend.publish(topic_name, after)

    assert result.msg_id

    messages = backend.fetch_messages(sub_key, max_messages=20)

    for message in messages:
        assert message['topic_name'] != topic_name.lower()

# ################################################################################################################################

def _delivery_toggle_while_pending(parallel:'any_', topic_name:'str') -> 'None':
    """ Delivery switched off while a pair is pending withholds that topic, and switching it on restores delivery.
    """
    subscription_list = parallel.pubsub_subscription_list
    backend = parallel.pubsub_backend

    sub_key = sub_key_for_topic(subscription_list, topic_name)
    add_topic_pending(subscription_list, sub_key, Topic_Second)

    _ = backend.sync_subscription_pairs([(sub_key, Topic_Second.lower())], [])
    subscription_list.mark_committed([(sub_key, Topic_Second.lower())], [])

    data = 'delivery.toggle.' + CryptoManager.generate_hex_string(8)
    _ = backend.publish(Topic_Second, data)

    set_delivery_enabled(subscription_list, sub_key, Topic_Second, False)

    delivered = subscription_list.delivered_topics(sub_key)
    assert Topic_Second.lower() not in delivered

    set_delivery_enabled(subscription_list, sub_key, Topic_Second, True)

    delivered = subscription_list.delivered_topics(sub_key)
    assert Topic_Second.lower() in delivered

# ################################################################################################################################

def test_pull_pending_addition_publication_and_removal(in_process_server:'any_') -> 'None':
    """ A pull subscriber follows pending addition, removal and delivery toggles.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server

    _publish_confirms_pending(parallel, Topic_Pull)
    _removal_skips_publication_and_withholds_fetch(parallel, Topic_Pull)

# ################################################################################################################################

def test_push_rest_pending_addition_and_delivery_toggle(in_process_server:'any_') -> 'None':
    """ A push REST subscriber follows pending addition and delivery toggles.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server

    _publish_confirms_pending(parallel, Topic_Push_Rest)
    _delivery_toggle_while_pending(parallel, Topic_Push_Rest)

# ################################################################################################################################

def test_push_service_pending_addition_and_removal(in_process_server:'any_') -> 'None':
    """ A push service subscriber follows pending addition and removal.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server

    _publish_confirms_pending(parallel, Topic_Push_Service)
    _removal_skips_publication_and_withholds_fetch(parallel, Topic_Push_Service)

# ################################################################################################################################
# ################################################################################################################################
