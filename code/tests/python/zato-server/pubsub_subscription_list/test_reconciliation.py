# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.test.direct_sql.fault import remove_topic_subscriptions
from zato.server.base.config_manager.pubsub_subscription_sync import reconcile_once
from zato_common_core.zato_common_core import SubscriptionList

from .conftest import Topic_Pull, Topic_Second
from .helpers import add_topic_pending, pair_in_rows, remove_topic_pending, status_of, sub_key_for_topic

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
    server, _push_endpoint = in_process_server
    parallel = server.server
    subscription_list = parallel.pubsub_subscription_list

    sub_key = sub_key_for_topic(subscription_list, Topic_Pull)
    add_topic_pending(subscription_list, sub_key, Topic_Second)

    assert subscription_list.has_unconfirmed()

    reconcile_once(parallel.config_manager, full=False)

    assert not subscription_list.has_unconfirmed()
    assert status_of(subscription_list, sub_key, Topic_Second) == SubscriptionList.STATUS_CONFIRMED

    pairs = parallel.pubsub_backend.get_governed_pairs()
    assert pair_in_rows(pairs, sub_key, Topic_Second)

# ################################################################################################################################

def test_reconciler_commits_pending_removal(in_process_server:'any_') -> 'None':
    """ The reconciler deletes the row of a pair pending removal without a publication.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server
    subscription_list = parallel.pubsub_subscription_list

    sub_key = sub_key_for_topic(subscription_list, Topic_Pull)
    remove_topic_pending(subscription_list, sub_key, Topic_Pull)

    assert status_of(subscription_list, sub_key, Topic_Pull) == SubscriptionList.STATUS_PENDING_REMOVAL

    reconcile_once(parallel.config_manager, full=False)

    assert not subscription_list.has_unconfirmed()

    pairs = parallel.pubsub_backend.get_governed_pairs()
    assert not pair_in_rows(pairs, sub_key, Topic_Pull)

# ################################################################################################################################

def test_reconciler_restores_row_removed_outside_server(in_process_server:'any_') -> 'None':
    """ A full reconciliation restores a row that was removed outside the server.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server
    subscription_list = parallel.pubsub_subscription_list
    backend = parallel.pubsub_backend

    sub_key = sub_key_for_topic(subscription_list, Topic_Pull)

    remove_topic_subscriptions(backend.engine, Topic_Pull.lower())

    pairs = backend.get_governed_pairs()
    assert not pair_in_rows(pairs, sub_key, Topic_Pull)

    reconcile_once(parallel.config_manager, full=True)

    pairs = backend.get_governed_pairs()
    assert pair_in_rows(pairs, sub_key, Topic_Pull)
    assert status_of(subscription_list, sub_key, Topic_Pull) == SubscriptionList.STATUS_CONFIRMED

# ################################################################################################################################

def test_status_kept_through_failed_sync(in_process_server:'any_') -> 'None':
    """ A failed row write leaves the pair pending until a later reconciliation commits it.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server
    subscription_list = parallel.pubsub_subscription_list

    sub_key = sub_key_for_topic(subscription_list, Topic_Pull)
    add_topic_pending(subscription_list, sub_key, Topic_Second)

    assert status_of(subscription_list, sub_key, Topic_Second) == SubscriptionList.STATUS_PENDING
    assert subscription_list.has_unconfirmed()

    reconcile_once(parallel.config_manager, full=False)

    assert status_of(subscription_list, sub_key, Topic_Second) == SubscriptionList.STATUS_CONFIRMED

# ################################################################################################################################
# ################################################################################################################################
