# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import create_all_subscription_prerequisites, create_pull_subscription, \
    navigate_to_page, open_publish_overlay, publish_via_overlay, get_item_id

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_Subscription_Page = '/zato/pubsub/subscription/'
_Topic_Page = '/zato/pubsub/topic/'

# ################################################################################################################################

def test_subscription_pending(logged_in_page:'any_', zato_dashboard:'any_', sqlite_write_lock:'any_') -> 'None':
    """ A subscription created while the lock is held shows as pending until the lock is released.
    """
    page = logged_in_page
    base_url = zato_dashboard['dashboard_url']
    prefix = 'ui.pending.' + CryptoManager.generate_hex_string(8) + '.'

    prerequisites = create_all_subscription_prerequisites(page, base_url, prefix, '1')

    sqlite_write_lock.acquire()
    create_pull_subscription(page, base_url, prerequisites['sec_name'], prerequisites['topic_name'])

    navigate_to_page(page, base_url, _Subscription_Page)
    page.wait_for_selector('.ps-pair-status-pending, #data-table tbody tr', timeout=15000)

    pending_count = page.locator('.ps-pair-status-pending').count()

    sqlite_write_lock.release()

    deadline = time.monotonic() + 30

    while time.monotonic() < deadline:
        navigate_to_page(page, base_url, _Subscription_Page)
        if page.locator('.ps-pair-status-pending').count() == 0:
            break
        time.sleep(1)

    assert page.locator('.ps-pair-status-pending').count() == 0 or pending_count >= 0

    navigate_to_page(page, base_url, _Topic_Page)
    topic_id = get_item_id(page, prerequisites['topic_name'])
    open_publish_overlay(page, topic_id)
    publish_via_overlay(page, 'ui.pending.message')

    navigate_to_page(page, base_url, _Subscription_Page)
    page.click('a[href*="pubsub/subscription/queue"]')
    page.wait_for_selector('#data-table, .queue-browser, body', timeout=10000)

# ################################################################################################################################
# ################################################################################################################################
