# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.facade import PubSubFacade
from zato_common_core.zato_common_core import SubscriptionList

from .conftest import Topic_Pull, Topic_Second
from .helpers import add_topic_pending, remove_topic_pending, status_of, sub_key_for_topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def test_backend_publish_confirms_pending_pair(in_process_server:'any_') -> 'None':
    """ A backend publication against a pending pair inserts the row and confirms the pair.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server
    subscription_list = parallel.pubsub_subscription_list
    backend = parallel.pubsub_backend

    sub_key = sub_key_for_topic(subscription_list, Topic_Pull)
    add_topic_pending(subscription_list, sub_key, Topic_Second)

    data = 'backend.pending.' + CryptoManager.generate_hex_string(8)
    result = backend.publish(Topic_Second, data)

    assert result.msg_id
    assert status_of(subscription_list, sub_key, Topic_Second) == SubscriptionList.STATUS_CONFIRMED

    messages = backend.fetch_messages(sub_key, max_messages=10)

    found = False

    for message in messages:
        if message['data'] == data:
            found = True
            break

    assert found

# ################################################################################################################################

def test_backend_publish_skips_pending_removal(in_process_server:'any_') -> 'None':
    """ A backend publication against a pair pending removal skips that subscriber.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server
    subscription_list = parallel.pubsub_subscription_list
    backend = parallel.pubsub_backend

    sub_key = sub_key_for_topic(subscription_list, Topic_Pull)
    remove_topic_pending(subscription_list, sub_key, Topic_Pull)

    data = 'backend.removal.' + CryptoManager.generate_hex_string(8)
    result = backend.publish(Topic_Pull, data)

    assert result.msg_id

    messages = backend.fetch_messages(sub_key, max_messages=10)

    for message in messages:
        assert message['data'] != data

# ################################################################################################################################

def test_facade_publish_against_pending_pair(in_process_server:'any_') -> 'None':
    """ A service facade publication against a pending pair confirms the pair.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server
    subscription_list = parallel.pubsub_subscription_list

    sub_key = sub_key_for_topic(subscription_list, Topic_Pull)
    add_topic_pending(subscription_list, sub_key, Topic_Second)

    facade = PubSubFacade(parallel, 'test.publication.paths')
    data = 'facade.pending.' + CryptoManager.generate_hex_string(8)

    result = facade.publish(Topic_Second, data)

    assert result.msg_id
    assert status_of(subscription_list, sub_key, Topic_Second) == SubscriptionList.STATUS_CONFIRMED

# ################################################################################################################################

def test_pull_ack_path_fetches_pending_confirmed_pair(in_process_server:'any_') -> 'None':
    """ A fetch after a publication to a pending pair returns the message once the pair is confirmed.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server
    subscription_list = parallel.pubsub_subscription_list
    backend = parallel.pubsub_backend

    sub_key = sub_key_for_topic(subscription_list, Topic_Pull)
    add_topic_pending(subscription_list, sub_key, Topic_Second)

    data = 'ack.path.' + CryptoManager.generate_hex_string(8)
    _ = backend.publish(Topic_Second, data)

    messages = backend.fetch_messages(sub_key, max_messages=10)

    found = False

    for message in messages:
        if message['data'] == data:
            found = True
            break

    assert found

# ################################################################################################################################
# ################################################################################################################################
