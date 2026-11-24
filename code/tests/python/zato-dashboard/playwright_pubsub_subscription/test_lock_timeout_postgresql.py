# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Local
from _support import ModuleCtx, RowLock, change_topics, create_client, create_pull_subscription_to, create_topics, \
    new_prefix, sub_key_of, subscription_item_id, wait_for_statuses

# Zato
from zato.common.pubsub.subscription_list import Lock_Timeout_Ms

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_, anydict, anylist

    any_ = any_
    anydict = anydict
    anylist = anylist
    Page = Page
    PubSubDatabase = PubSubDatabase

# ################################################################################################################################
# ################################################################################################################################

class TestCtx:

    # A save that completes at once takes less than this share of the lock timeout
    Free_Share = 0.5

    # The lock on the row of one pair
    Topic_Sub_Lock = 'select sub_key from pubsub_topic_sub where sub_key = %s and topic_name = %s for update'

# ################################################################################################################################
# ################################################################################################################################

def _create_subscriber(page:'Page', base_url:'str', prefix:'str', suffix:'str', topic_names:'anylist') -> 'str':
    client = create_client(page, base_url, prefix, suffix)
    create_pull_subscription_to(page, base_url, client['name'], topic_names)

    out = subscription_item_id(page, base_url, client['name'])
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_lock_timeout_postgresql(
    logged_in_page:'any_',
    zato_dashboard:'anydict',
    pubsub_database:'PubSubDatabase',
    ) -> 'None':
    """ With the row of a pair locked, a topic removed from a subscription in Dashboard is saved at once and shows
    as pending removal, a save of another subscription completes while the first row write waits, and both statuses
    clear after the lock is released.
    """
    page = logged_in_page
    base_url = zato_dashboard['dashboard_url']
    prefix = new_prefix('lock.timeout')

    topics = create_topics(page, base_url, prefix, 2)

    removed_name = topics[0]['name']
    kept_name = topics[1]['name']
    topic_names = [removed_name, kept_name]

    first_id = _create_subscriber(page, base_url, prefix, 'first', topic_names)
    second_id = _create_subscriber(page, base_url, prefix, 'second', topic_names)

    confirmed = {removed_name: ModuleCtx.Status_Confirmed, kept_name: ModuleCtx.Status_Confirmed}
    wait_for_statuses(page, base_url, first_id, confirmed, 'The confirmation of the pairs of the first subscription')
    wait_for_statuses(page, base_url, second_id, confirmed, 'The confirmation of the pairs of the second subscription')

    removed_only = {kept_name: ModuleCtx.Status_Confirmed}
    pending = {removed_name: ModuleCtx.Status_Pending_Removal, kept_name: ModuleCtx.Status_Confirmed}

    free_limit = Lock_Timeout_Ms * TestCtx.Free_Share / 1000.0
    first_sub_key = sub_key_of(page, base_url, first_id)

    row_lock = RowLock(pubsub_database, TestCtx.Topic_Sub_Lock, [first_sub_key, removed_name])
    row_lock.acquire()

    try:

        # The removal from the first subscription is saved at once and its pair waits for the locked row ..
        elapsed = change_topics(page, base_url, first_id, topic_names, {removed_name: False})
        assert elapsed < free_limit, elapsed

        wait_for_statuses(page, base_url, first_id, pending, 'The pending removal of the locked pair')

        # .. the removal from the second subscription is saved at once and completes while the first one waits ..
        elapsed = change_topics(page, base_url, second_id, topic_names, {removed_name: False})
        assert elapsed < free_limit, elapsed

        wait_for_statuses(page, base_url, second_id, removed_only, 'The removal of the pair of the second subscription')
        wait_for_statuses(page, base_url, first_id, pending, 'The pending removal of the locked pair')

    finally:
        row_lock.release()

    # .. and the first one completes after the release.
    wait_for_statuses(page, base_url, first_id, removed_only, 'The removal of the pair of the first subscription')
    wait_for_statuses(page, base_url, second_id, removed_only, 'The removal of the pair of the second subscription')

# ################################################################################################################################
# ################################################################################################################################
