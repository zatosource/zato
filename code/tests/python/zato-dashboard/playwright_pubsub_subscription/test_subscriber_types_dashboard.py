# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Local
from _support import ModuleCtx, change_topics, create_client, create_pull_subscription_to, create_topics, is_queued, \
    new_marker, new_prefix, publish_accepted, queue_path, subscription_item_id, wait_for_queued, wait_for_statuses

# Zato
from zato.common.test.playwright_pubsub import create_outgoing_rest, create_push_rest_subscription, \
    create_service_subscription

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict, anylist, callable_

    any_ = any_
    anydict = anydict
    anylist = anylist
    callable_ = callable_
    Page = Page

# ################################################################################################################################
# ################################################################################################################################

class TestCtx:

    # The service that the push subscriber to a service is, deployed by playwright_/conftest.py
    Push_Service = 'test.pubsub.dashboard-service-subscriber.edit'

# ################################################################################################################################
# ################################################################################################################################

def _check_subscriber(
    page:'Page',
    base_url:'str',
    write_lock:'any_',
    topics:'anylist',
    subscriber_name:'str',
    create:'callable_',
    ) -> 'None':
    """ Creates a subscriber in Dashboard while the lock is held, adds a topic to it and removes one from it, each while
    the lock is held, and checks after each release which messages reach its queue.
    """
    first = topics[0]
    added = topics[1]
    first_name = first['name']
    added_name = added['name']

    # Create the subscriber while no row of a pair can be written ..
    write_lock.acquire()
    create(first_name)

    item_id = subscription_item_id(page, base_url, subscriber_name)
    wait_for_statuses(page, base_url, item_id, {first_name: ModuleCtx.Status_Pending}, 'The pending status of the pair')

    write_lock.release()
    wait_for_statuses(page, base_url, item_id, {first_name: ModuleCtx.Status_Confirmed}, 'The confirmation of the pair')

    path = queue_path(page, base_url, item_id, ModuleCtx.Queue_State_All)

    # .. add a topic while the lock is held, after which a message published to it reaches the queue ..
    write_lock.acquire()
    _ = change_topics(page, base_url, item_id, [first_name], {added_name: True})

    pending = {first_name: ModuleCtx.Status_Confirmed, added_name: ModuleCtx.Status_Pending}
    wait_for_statuses(page, base_url, item_id, pending, 'The pending status of the added pair')

    write_lock.release()

    confirmed = {first_name: ModuleCtx.Status_Confirmed, added_name: ModuleCtx.Status_Confirmed}
    wait_for_statuses(page, base_url, item_id, confirmed, 'The confirmation of the added pair')

    added_marker = new_marker('added')
    publish_accepted(page, base_url, added, added_marker)
    wait_for_queued(page, base_url, path, added_marker)

    # .. and remove a topic while the lock is held, after which a message published to it does not.
    write_lock.acquire()
    _ = change_topics(page, base_url, item_id, [first_name, added_name], {first_name: False})

    pending = {first_name: ModuleCtx.Status_Pending_Removal, added_name: ModuleCtx.Status_Confirmed}
    wait_for_statuses(page, base_url, item_id, pending, 'The pending removal of the pair')

    write_lock.release()
    wait_for_statuses(page, base_url, item_id, {added_name: ModuleCtx.Status_Confirmed}, 'The removal of the pair')

    removed_marker = new_marker('removed')
    publish_accepted(page, base_url, first, removed_marker)

    kept_marker = new_marker('kept')
    publish_accepted(page, base_url, added, kept_marker)

    wait_for_queued(page, base_url, path, kept_marker)
    assert not is_queued(page, base_url, path, removed_marker)

# ################################################################################################################################
# ################################################################################################################################

def test_pull_subscriber(logged_in_page:'any_', zato_dashboard:'anydict', write_lock:'any_') -> 'None':
    """ A pull subscriber created and edited in Dashboard while the lock is held.
    """
    page = logged_in_page
    base_url = zato_dashboard['dashboard_url']
    prefix = new_prefix('types.pull')

    client = create_client(page, base_url, prefix, 'client')
    topics = create_topics(page, base_url, prefix, 2)

    def _create(topic_name:'str') -> 'None':
        create_pull_subscription_to(page, base_url, client['name'], [topic_name])

    _check_subscriber(page, base_url, write_lock, topics, client['name'], _create)

# ################################################################################################################################

def test_push_rest_subscriber(logged_in_page:'any_', zato_dashboard:'anydict', write_lock:'any_') -> 'None':
    """ A push subscriber to a REST endpoint created and edited in Dashboard while the lock is held.
    """
    page = logged_in_page
    base_url = zato_dashboard['dashboard_url']
    prefix = new_prefix('types.rest')

    client = create_client(page, base_url, prefix, 'client')
    topics = create_topics(page, base_url, prefix, 2)
    rest_name = create_outgoing_rest(page, base_url, prefix, 'push')

    def _create(topic_name:'str') -> 'None':
        create_push_rest_subscription(page, base_url, client['name'], topic_name, rest_name)

    _check_subscriber(page, base_url, write_lock, topics, client['name'], _create)

# ################################################################################################################################

def test_push_service_subscriber(logged_in_page:'any_', zato_dashboard:'anydict', write_lock:'any_') -> 'None':
    """ A push subscriber to a service created and edited in Dashboard while the lock is held.
    """
    page = logged_in_page
    base_url = zato_dashboard['dashboard_url']
    prefix = new_prefix('types.service')

    topics = create_topics(page, base_url, prefix, 2)

    def _create(topic_name:'str') -> 'None':
        create_service_subscription(page, base_url, [TestCtx.Push_Service], topic_name)

    _check_subscriber(page, base_url, write_lock, topics, TestCtx.Push_Service, _create)

# ################################################################################################################################
# ################################################################################################################################
