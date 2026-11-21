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
    find_row_by_link_text, navigate_to_page, open_edit_dialog, submit_edit_form, unpick_subscription_topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_Subscription_Page = '/zato/pubsub/subscription/'

# ################################################################################################################################

def test_subscription_removal_pending(
    logged_in_page:'any_',
    zato_dashboard:'any_',
    sqlite_write_lock:'any_',
) -> 'None':
    """ A topic removed while the lock is held shows as pending removal until the lock is released.
    """
    page = logged_in_page
    base_url = zato_dashboard['dashboard_url']
    prefix = 'ui.removal.' + CryptoManager.generate_hex_string(8) + '.'

    prerequisites = create_all_subscription_prerequisites(page, base_url, prefix, '1')
    create_pull_subscription(page, base_url, prerequisites['sec_name'], prerequisites['topic_name'])

    sqlite_write_lock.release()
    time.sleep(1)
    sqlite_write_lock.acquire()

    navigate_to_page(page, base_url, _Subscription_Page)
    row = find_row_by_link_text(page, prerequisites['sec_name'])
    item_id = row.get_attribute('id').replace('tr_', '')

    open_edit_dialog(page, 'pubsub.subscription', item_id)
    unpick_subscription_topic(page, prerequisites['topic_name'])
    submit_edit_form(page)

    navigate_to_page(page, base_url, _Subscription_Page)
    page.wait_for_selector('.ps-pair-status-pending-removal, #data-table tbody tr', timeout=15000)

    sqlite_write_lock.release()

    deadline = time.monotonic() + 30

    while time.monotonic() < deadline:
        navigate_to_page(page, base_url, _Subscription_Page)
        if page.locator('.ps-pair-status-pending-removal').count() == 0:
            break
        time.sleep(1)

# ################################################################################################################################
# ################################################################################################################################
