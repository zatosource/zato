# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager
from zato.server.base.config_manager.pubsub_subscription_sync import reconcile_once
from zato_common_core.zato_common_core import SubscriptionList

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def test_reconciler_commits_pending_addition(in_process_server:'any_') -> 'None':
    """ The reconciler inserts the row of a pending pair without a publication.
    """
    from .conftest import Topic_Second

    server, _push_endpoint = in_process_server
    parallel = server.server
    subscription_list = parallel.pubsub_subscription_list

    sub_key = None

    for candidate, topic, _status in subscription_list.statuses():
        if topic != Topic_Second.lower():
            if SubscriptionList.is_governed(candidate):
                sub_key = candidate
                break

    assert sub_key is not None

    topics = {
        Topic_Second.lower(): {
            'is_pub_enabled': True,
            'is_delivery_enabled': True,
        }
    }

    previous = subscription_list.topics_of(sub_key)

    for topic_name in previous:
        topics[topic_name] = {
            'is_pub_enabled': True,
            'is_delivery_enabled': True,
        }

    _ = subscription_list.set_topics(sub_key, True, topics)

    assert subscription_list.has_unconfirmed()

    reconcile_once(parallel.config_manager, full=False)

    assert not subscription_list.has_unconfirmed()

    pairs = parallel.pubsub_backend.get_governed_pairs()
    found = False

    for pair_sub_key, pair_topic in pairs:
        if pair_sub_key == sub_key:
            if pair_topic == Topic_Second.lower():
                found = True
                break

    assert found

# ################################################################################################################################
# ################################################################################################################################
