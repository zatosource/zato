# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Local
from _support import ModuleCtx, create_client, create_pull_subscription_to, create_topics, new_marker, new_prefix, \
    publish_accepted, queue_path, subscription_item_id, wait_for_queued, wait_for_statuses

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

    any_ = any_
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

def test_subscription_pending(logged_in_page:'any_', zato_dashboard:'anydict', write_lock:'any_') -> 'None':
    """ A subscription created while the lock is held shows as pending, the status clears after the release,
    and a message published from the topic page appears in the queue of the subscriber.
    """
    page = logged_in_page
    base_url = zato_dashboard['dashboard_url']
    prefix = new_prefix('pending')

    client = create_client(page, base_url, prefix, 'client')
    topics = create_topics(page, base_url, prefix, 1)

    topic = topics[0]
    topic_name = topic['name']

    # Create the subscription while no row of a pair can be written ..
    write_lock.acquire()
    create_pull_subscription_to(page, base_url, client['name'], [topic_name])

    item_id = subscription_item_id(page, base_url, client['name'])
    wait_for_statuses(page, base_url, item_id, {topic_name: ModuleCtx.Status_Pending}, 'The pending status of the pair')

    # .. the status clears once the row can be written ..
    write_lock.release()
    wait_for_statuses(page, base_url, item_id, {topic_name: ModuleCtx.Status_Confirmed}, 'The confirmation of the pair')

    # .. and a message published from the topic page reaches the queue of the subscriber.
    marker = new_marker('pending')
    publish_accepted(page, base_url, topic, marker)

    path = queue_path(page, base_url, item_id, ModuleCtx.Queue_State_All)
    wait_for_queued(page, base_url, path, marker)

# ################################################################################################################################
# ################################################################################################################################
