# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Local
from _support import ModuleCtx, change_topics, create_client, create_pull_subscription_to, create_topics, is_queued, \
    new_marker, new_prefix, publish_accepted, queue_path, start_publication, subscription_item_id, \
    wait_for_publication, wait_for_queued, wait_for_statuses

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

    any_ = any_
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

def test_subscription_removal_pending(logged_in_page:'any_', zato_dashboard:'anydict', write_lock:'any_') -> 'None':
    """ A topic removed while the lock is held shows as pending removal, a message published to it does not appear
    in the queue of the subscriber, and the topic disappears after the release.
    """
    page = logged_in_page
    base_url = zato_dashboard['dashboard_url']
    prefix = new_prefix('removal')

    client = create_client(page, base_url, prefix, 'client')
    topics = create_topics(page, base_url, prefix, 2)

    removed = topics[0]
    kept = topics[1]
    removed_name = removed['name']
    kept_name = kept['name']

    create_pull_subscription_to(page, base_url, client['name'], [removed_name, kept_name])

    item_id = subscription_item_id(page, base_url, client['name'])
    confirmed = {removed_name: ModuleCtx.Status_Confirmed, kept_name: ModuleCtx.Status_Confirmed}
    wait_for_statuses(page, base_url, item_id, confirmed, 'The confirmation of both pairs')

    path = queue_path(page, base_url, item_id, ModuleCtx.Queue_State_All)

    # Remove the topic while no row of a pair can be deleted ..
    write_lock.acquire()
    _ = change_topics(page, base_url, item_id, [removed_name, kept_name], {removed_name: False})

    pending = {removed_name: ModuleCtx.Status_Pending_Removal, kept_name: ModuleCtx.Status_Confirmed}
    wait_for_statuses(page, base_url, item_id, pending, 'The pending removal of the pair')

    # .. publish to it behind the lock and let the publication through ..
    removed_marker = new_marker('removed')
    start_publication(page, base_url, removed, removed_marker)
    time.sleep(ModuleCtx.Publish_Hold_Seconds)

    write_lock.release()

    status = wait_for_publication(page)
    assert status.startswith(ModuleCtx.Publish_Accepted), status

    # .. a message to the kept topic, published after it, reaches the queue while the first one does not ..
    kept_marker = new_marker('kept')
    publish_accepted(page, base_url, kept, kept_marker)

    wait_for_queued(page, base_url, path, kept_marker)
    assert not is_queued(page, base_url, path, removed_marker)

    # .. and the removed topic disappears from the subscription.
    wait_for_statuses(page, base_url, item_id, {kept_name: ModuleCtx.Status_Confirmed}, 'The removal of the pair')

# ################################################################################################################################
# ################################################################################################################################
