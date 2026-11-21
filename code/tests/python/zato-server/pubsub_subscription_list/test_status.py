# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.json_internal import loads
from zato_common_core.zato_common_core import SubscriptionList

from .conftest import Topic_Pull
from .helpers import remove_topic_pending, status_of, sub_key_for_topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

    any_ = any_
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

def _get_subscriptions(parallel:'any_') -> 'anylist':
    """ Returns the subscriptions that get-list returns in-process, whose response is serialized to JSON.
    """
    response = parallel.invoke('zato.pubsub.subscription.get-list', {}, skip_response_elem=True)

    out = loads(response)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_statuses_after_startup(in_process_server:'any_') -> 'None':
    """ After startup every configured pair of the subscription list is confirmed.
    """
    server, _push_endpoint = in_process_server
    subscription_list = server.server.pubsub_subscription_list

    assert subscription_list.is_loaded()

    for _sub_key, _topic, status in subscription_list.statuses():
        assert status == SubscriptionList.STATUS_CONFIRMED

# ################################################################################################################################

def test_has_unconfirmed_false_when_synced(in_process_server:'any_') -> 'None':
    """ A synchronized subscription list reports no unconfirmed pairs.
    """
    server, _push_endpoint = in_process_server
    subscription_list = server.server.pubsub_subscription_list

    assert not subscription_list.has_unconfirmed()

# ################################################################################################################################

def test_get_list_returns_pending_status(in_process_server:'any_') -> 'None':
    """ get-list returns the pending status of a pair that has no row yet.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server
    subscription_list = parallel.pubsub_subscription_list

    sub_key = sub_key_for_topic(subscription_list, Topic_Pull)

    # get-list lists the pairs of config.db, so the pending pair is one of config.db whose row the list does not consider committed
    subscription_list.mark_committed([], [(sub_key, Topic_Pull.lower())])

    assert status_of(subscription_list, sub_key, Topic_Pull) == SubscriptionList.STATUS_PENDING

    subscriptions = _get_subscriptions(parallel)

    # get-list reports whether any pair is unconfirmed in the first subscription only
    assert subscriptions[0]['has_unconfirmed']

    found = False

    for item in subscriptions:
        if item['sub_key'] != sub_key:
            continue

        for topic in item['topic_name_list']:
            if topic['topic_name'] == Topic_Pull.lower():
                assert topic['status'] == SubscriptionList.STATUS_PENDING
                found = True
                break

    assert found

# ################################################################################################################################

def test_get_list_returns_pending_removal_and_depths_omit_it(in_process_server:'any_') -> 'None':
    """ get-list returns pending removal, and depths withhold that pair.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server
    subscription_list = parallel.pubsub_subscription_list
    backend = parallel.pubsub_backend

    sub_key = sub_key_for_topic(subscription_list, Topic_Pull)

    _ = backend.publish(Topic_Pull, 'before.removal')

    remove_topic_pending(subscription_list, sub_key, Topic_Pull)

    assert status_of(subscription_list, sub_key, Topic_Pull) == SubscriptionList.STATUS_PENDING_REMOVAL
    assert subscription_list.withholds_pair(sub_key, Topic_Pull.lower())

    subscriptions = _get_subscriptions(parallel)

    found = False

    for item in subscriptions:
        if item['sub_key'] != sub_key:
            continue

        for topic in item['topic_name_list']:
            if topic['topic_name'] == Topic_Pull.lower():
                assert topic['status'] == SubscriptionList.STATUS_PENDING_REMOVAL
                found = True
                break

        depths = backend.get_pending_depths([(sub_key, Topic_Pull.lower())])
        assert depths[sub_key] == 0

    assert found

# ################################################################################################################################
# ################################################################################################################################
