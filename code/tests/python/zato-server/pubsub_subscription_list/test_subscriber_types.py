# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager
from zato_common_core.zato_common_core import SubscriptionList

from .conftest import Topic_Pull, Topic_Second

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def test_publication_delivers_to_pending_pull_pair(in_process_server:'any_') -> 'None':
    """ A publication to a pending pull pair inserts its row in the same commit and is delivered.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server
    subscription_list = parallel.pubsub_subscription_list
    backend = parallel.pubsub_backend

    sub_key = None

    for candidate, topic, _status in subscription_list.statuses():
        if topic == Topic_Pull.lower():
            sub_key = candidate
            break

    assert sub_key is not None

    topics = subscription_list.topics_of(sub_key)
    topic_flags = {}

    for topic_name in topics:
        topic_flags[topic_name] = {
            'is_pub_enabled': True,
            'is_delivery_enabled': True,
        }

    topic_flags[Topic_Second.lower()] = {
        'is_pub_enabled': True,
        'is_delivery_enabled': True,
    }

    _ = subscription_list.set_topics(sub_key, True, topic_flags)

    pending, _removals = subscription_list.differences()
    assert pending

    data = 'message.' + CryptoManager.generate_hex_string(8)
    result = backend.publish(Topic_Second, data)

    assert result.msg_id

    for _sub_key, topic, status in subscription_list.statuses():
        if topic == Topic_Second.lower():
            if _sub_key == sub_key:
                assert status == SubscriptionList.STATUS_CONFIRMED
                break
    else:
        raise Exception('The pair was not confirmed after the publication')

# ################################################################################################################################
# ################################################################################################################################
