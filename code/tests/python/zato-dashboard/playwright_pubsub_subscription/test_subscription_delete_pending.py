# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Local
from _support import ModuleCtx, create_client, create_pull_subscription_to, create_topics, is_queued, new_marker, \
    new_prefix, publish_accepted, queue_path, start_publication, subscription_item_id, wait_for_publication, \
    wait_for_queued, wait_for_statuses

# Zato
from zato.common.test.playwright_pubsub import confirm_delete, navigate_to_page, trigger_delete

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

    any_ = any_
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

def test_subscription_delete_pending(logged_in_page:'any_', zato_dashboard:'anydict', write_lock:'any_') -> 'None':
    """ A subscription deleted while the lock is held has its pairs pending removal, whose messages the queue browser
    withholds while their rows remain, until the rows are deleted after the release.
    """
    page = logged_in_page
    base_url = zato_dashboard['dashboard_url']
    prefix = new_prefix('delete')

    client = create_client(page, base_url, prefix, 'client')
    topics = create_topics(page, base_url, prefix, 1)

    topic = topics[0]
    topic_name = topic['name']

    create_pull_subscription_to(page, base_url, client['name'], [topic_name])

    item_id = subscription_item_id(page, base_url, client['name'])
    wait_for_statuses(page, base_url, item_id, {topic_name: ModuleCtx.Status_Confirmed}, 'The confirmation of the pair')

    # A message queued before the deletion shows in the queue browser ..
    path = queue_path(page, base_url, item_id, ModuleCtx.Queue_State_All)
    queued_marker = new_marker('queued')

    publish_accepted(page, base_url, topic, queued_marker)
    wait_for_queued(page, base_url, path, queued_marker)

    # .. delete the subscription while no row of a pair can be deleted ..
    write_lock.acquire()

    navigate_to_page(page, base_url, ModuleCtx.Subscription_Page)
    trigger_delete(page, 'subscription', item_id)
    confirm_delete(page)

    wait_for_statuses(page, base_url, item_id, None, 'The deletion of the subscription')

    # .. its rows remain, and the queue browser withholds their message as the pairs are pending removal ..
    assert not is_queued(page, base_url, path, queued_marker)

    # .. a publication held behind the lock reaches no queue of the pairs after the release ..
    held_marker = new_marker('held')
    start_publication(page, base_url, topic, held_marker)
    time.sleep(ModuleCtx.Publish_Hold_Seconds)

    write_lock.release()

    status = wait_for_publication(page)
    assert status.startswith(ModuleCtx.Publish_Accepted), status

    # .. and once the rows are deleted, no message of the pairs remains.
    assert not is_queued(page, base_url, path, queued_marker)
    assert not is_queued(page, base_url, path, held_marker)

# ################################################################################################################################
# ################################################################################################################################
