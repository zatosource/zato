# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Local
from _support import ModuleCtx, create_client, create_pull_subscription_to, create_topics, is_queued, new_marker, \
    new_prefix, open_subscription_edit, publish_accepted, queue_path, save_edit, set_edit_topic, start_publication, \
    subscription_item_id, wait_for_not_queued, wait_for_publication, wait_for_queued, wait_for_statuses

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict, anylist

    any_ = any_
    anydict = anydict
    anylist = anylist
    Page = Page

# ################################################################################################################################
# ################################################################################################################################

class Setup:
    """ A pull subscriber to two topics, of which the first is removed during the test.
    """

    def __init__(self, page:'Page', base_url:'str', label:'str') -> 'None':
        prefix = new_prefix(label)

        client = create_client(page, base_url, prefix, 'client')
        topics:'anylist' = create_topics(page, base_url, prefix, 2)

        self.removed = topics[0]
        self.kept = topics[1]
        self.removed_name = self.removed['name']
        self.kept_name = self.kept['name']

        create_pull_subscription_to(page, base_url, client['name'], [self.removed_name, self.kept_name])

        self.item_id = subscription_item_id(page, base_url, client['name'])

        confirmed = {self.removed_name: ModuleCtx.Status_Confirmed, self.kept_name: ModuleCtx.Status_Confirmed}
        wait_for_statuses(page, base_url, self.item_id, confirmed, 'The confirmation of both pairs')

        self.path = queue_path(page, base_url, self.item_id, ModuleCtx.Queue_State_All)
        self.pending = {self.removed_name: ModuleCtx.Status_Pending_Removal, self.kept_name: ModuleCtx.Status_Confirmed}
        self.removed_only = {self.kept_name: ModuleCtx.Status_Confirmed}

    def open_removal(self, page:'Page', base_url:'str') -> 'None':
        """ Opens the edit form of the subscription with the first topic unsubscribed, ready to be saved.
        """
        open_subscription_edit(page, base_url, self.item_id, [self.removed_name, self.kept_name])
        set_edit_topic(page, self.removed_name, False)

# ################################################################################################################################
# ################################################################################################################################

def test_publication_committed_before_removal(logged_in_page:'any_', zato_dashboard:'anydict', write_lock:'any_') -> 'None':
    """ A publication held behind the lock that commits before the operator removes the topic in another page
    shows in the queue browser until the removal deletes it.
    """
    publisher_page = logged_in_page
    base_url = zato_dashboard['dashboard_url']
    setup = Setup(publisher_page, base_url, 'order.first')

    operator_page = publisher_page.context.new_page()

    try:
        setup.open_removal(operator_page, base_url)

        # The publication waits behind the lock and commits after the release ..
        write_lock.acquire()

        marker = new_marker('first')
        start_publication(publisher_page, base_url, setup.removed, marker)
        time.sleep(ModuleCtx.Publish_Hold_Seconds)

        write_lock.release()

        status = wait_for_publication(publisher_page)
        assert status.startswith(ModuleCtx.Publish_Accepted), status

        # .. so it reaches the queue of the subscriber ..
        wait_for_queued(publisher_page, base_url, setup.path, marker)

        # .. after which the removal in the other page deletes it together with the pair.
        _ = save_edit(operator_page)

        wait_for_statuses(publisher_page, base_url, setup.item_id, setup.removed_only, 'The removal of the pair')
        wait_for_not_queued(publisher_page, base_url, setup.path, marker)

    finally:
        operator_page.close()

# ################################################################################################################################

def test_publication_held_behind_removal(logged_in_page:'any_', zato_dashboard:'anydict', write_lock:'any_') -> 'None':
    """ A publication held behind the lock while the operator removes the topic in another page does not show
    in the queue browser, as it commits after the removal.
    """
    publisher_page = logged_in_page
    base_url = zato_dashboard['dashboard_url']
    setup = Setup(publisher_page, base_url, 'order.second')

    operator_page = publisher_page.context.new_page()

    try:
        setup.open_removal(operator_page, base_url)

        # The publication waits behind the lock while the removal is saved in the other page ..
        write_lock.acquire()

        marker = new_marker('second')
        start_publication(publisher_page, base_url, setup.removed, marker)

        _ = save_edit(operator_page)
        wait_for_statuses(operator_page, base_url, setup.item_id, setup.pending, 'The pending removal of the pair')

        write_lock.release()

        status = wait_for_publication(publisher_page)
        assert status.startswith(ModuleCtx.Publish_Accepted), status

        # .. so a message to the kept topic, published after it, reaches the queue while it does not.
        kept_marker = new_marker('kept')
        publish_accepted(publisher_page, base_url, setup.kept, kept_marker)

        wait_for_queued(publisher_page, base_url, setup.path, kept_marker)
        assert not is_queued(publisher_page, base_url, setup.path, marker)

        wait_for_statuses(publisher_page, base_url, setup.item_id, setup.removed_only, 'The removal of the pair')

    finally:
        operator_page.close()

# ################################################################################################################################
# ################################################################################################################################
