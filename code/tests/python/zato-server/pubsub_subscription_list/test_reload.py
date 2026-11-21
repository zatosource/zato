# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager
from zato.server.base.config_manager.pubsub_subscription_sync import reconcile_once
from zato_common_core.zato_common_core import SubscriptionList

from .conftest import Topic_Pull, Topic_Push_Rest, Topic_Push_Service, Topic_Second
from .helpers import add_topic_pending, pair_in_rows, remove_topic_pending, status_of, sub_key_for_topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def test_reload_rebuilds_subscription_list(in_process_server:'any_') -> 'None':
    """ A reload replaces the subscription list from config.db and leaves every pair confirmed.
    """
    server, _push_endpoint = in_process_server

    _ = server.server.config_manager.init_pubsub()

    subscription_list = server.server.pubsub_subscription_list

    assert subscription_list.is_loaded()
    assert not subscription_list.has_unconfirmed()

    for _sub_key, _topic, status in subscription_list.statuses():
        assert status == SubscriptionList.STATUS_CONFIRMED

# ################################################################################################################################

def test_pending_pairs_after_failed_bulk_then_reconcile(in_process_server:'any_') -> 'None':
    """ Pending pairs left after a failed bulk write are committed by the reconciler.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server
    subscription_list = parallel.pubsub_subscription_list

    for topic_name in (Topic_Pull, Topic_Push_Rest, Topic_Push_Service):
        sub_key = sub_key_for_topic(subscription_list, topic_name)
        add_topic_pending(subscription_list, sub_key, Topic_Second)

    assert subscription_list.has_unconfirmed()

    reconcile_once(parallel.config_manager, full=False)

    assert not subscription_list.has_unconfirmed()

    pairs = parallel.pubsub_backend.get_governed_pairs()

    for topic_name in (Topic_Pull, Topic_Push_Rest, Topic_Push_Service):
        sub_key = sub_key_for_topic(subscription_list, topic_name)
        assert pair_in_rows(pairs, sub_key, Topic_Second)

# ################################################################################################################################

def test_publication_between_config_read_and_list_replace(in_process_server:'any_') -> 'None':
    """ A publication that commits while a reload rebuilds the list still delivers.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server
    backend = parallel.pubsub_backend

    data = 'during.reload.' + CryptoManager.generate_hex_string(8)
    result = backend.publish(Topic_Pull, data)

    assert result.msg_id

    _ = parallel.config_manager.init_pubsub()

    subscription_list = parallel.pubsub_subscription_list
    sub_key = sub_key_for_topic(subscription_list, Topic_Pull)
    messages = backend.fetch_messages(sub_key, max_messages=10)

    found = False

    for message in messages:
        if message['data'] == data:
            found = True
            break

    assert found

# ################################################################################################################################

def test_startup_removes_rows_of_deleted_subscriptions(in_process_server:'any_') -> 'None':
    """ A reload that drops a topic from config.db removes its subscription row through reconciliation.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server
    subscription_list = parallel.pubsub_subscription_list

    sub_key = sub_key_for_topic(subscription_list, Topic_Pull)
    remove_topic_pending(subscription_list, sub_key, Topic_Pull)

    assert status_of(subscription_list, sub_key, Topic_Pull) == SubscriptionList.STATUS_PENDING_REMOVAL

    reconcile_once(parallel.config_manager, full=False)

    pairs = parallel.pubsub_backend.get_governed_pairs()
    assert not pair_in_rows(pairs, sub_key, Topic_Pull)

# ################################################################################################################################
# ################################################################################################################################
