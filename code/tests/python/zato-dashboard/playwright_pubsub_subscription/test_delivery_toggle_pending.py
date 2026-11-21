# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Local
from _support import ModuleCtx, change_topics, create_client, create_pull_subscription_to, create_topics, new_marker, \
    new_prefix, open_subscription_edit, publish_accepted, queue_path, save_edit, subscription_item_id, \
    wait_for_queued, wait_for_statuses

# Zato
from zato.common.test.playwright_pubsub import navigate_to_page

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict, strlist

    any_ = any_
    anydict = anydict
    Page = Page
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class TestCtx:
    Delivery_Checkbox = '#id_edit-is_delivery_active'
    Delivery_On_Badge = '.ps-badge-deliv-enabled'

# ################################################################################################################################
# ################################################################################################################################

def _set_delivery(page:'Page', base_url:'str', item_id:'str', current_topics:'strlist', is_active:'bool') -> 'None':
    open_subscription_edit(page, base_url, item_id, current_topics)
    page.set_checked(TestCtx.Delivery_Checkbox, is_active)
    _ = save_edit(page)

# ################################################################################################################################

def _has_delivery_on(page:'Page', base_url:'str', item_id:'str') -> 'bool':
    navigate_to_page(page, base_url, ModuleCtx.Subscription_Page)
    badge_count = page.locator(f'#tr_{item_id} {TestCtx.Delivery_On_Badge}').count()

    out = badge_count == 1
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_delivery_toggle_pending(logged_in_page:'any_', zato_dashboard:'anydict', write_lock:'any_') -> 'None':
    """ Delivery switched on while a pair is pending shows the active flag and the pending status together.
    """
    page = logged_in_page
    base_url = zato_dashboard['dashboard_url']
    prefix = new_prefix('delivery')

    client = create_client(page, base_url, prefix, 'client')
    topics = create_topics(page, base_url, prefix, 2)

    first_name = topics[0]['name']
    added = topics[1]
    added_name = added['name']

    create_pull_subscription_to(page, base_url, client['name'], [first_name])
    item_id = subscription_item_id(page, base_url, client['name'])

    # Switch delivery off while every pair is confirmed ..
    _set_delivery(page, base_url, item_id, [first_name], False)
    assert not _has_delivery_on(page, base_url, item_id)

    # .. add a topic while no row of a pair can be written ..
    write_lock.acquire()
    _ = change_topics(page, base_url, item_id, [first_name], {added_name: True})

    pending = {first_name: ModuleCtx.Status_Confirmed, added_name: ModuleCtx.Status_Pending}
    wait_for_statuses(page, base_url, item_id, pending, 'The pending status of the added pair')

    # .. switch delivery on while the pair is pending, after which the page shows both ..
    _set_delivery(page, base_url, item_id, [first_name, added_name], True)

    assert _has_delivery_on(page, base_url, item_id)
    wait_for_statuses(page, base_url, item_id, pending, 'The pending status next to the active flag')

    # .. the status clears after the release and the flag stays on ..
    write_lock.release()

    confirmed = {first_name: ModuleCtx.Status_Confirmed, added_name: ModuleCtx.Status_Confirmed}
    wait_for_statuses(page, base_url, item_id, confirmed, 'The confirmation of the added pair')
    assert _has_delivery_on(page, base_url, item_id)

    # .. and a message published to the added topic reaches the queue of the subscriber.
    marker = new_marker('delivery')
    publish_accepted(page, base_url, added['item_id'], marker)

    path = queue_path(page, base_url, item_id, ModuleCtx.Queue_State_All)
    wait_for_queued(page, base_url, path, marker)

# ################################################################################################################################
# ################################################################################################################################
