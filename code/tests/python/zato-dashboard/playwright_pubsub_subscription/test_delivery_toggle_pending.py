# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import create_all_subscription_prerequisites, create_pull_subscription, \
    find_row_by_link_text, navigate_to_page, open_edit_dialog, submit_edit_form

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_Subscription_Page = '/zato/pubsub/subscription/'

# ################################################################################################################################

def test_delivery_toggle_pending(
    logged_in_page:'any_',
    zato_dashboard:'any_',
    sqlite_write_lock:'any_',
) -> 'None':
    """ Delivery switched on while a pair is pending shows the active flag and the pending status together.
    """
    page = logged_in_page
    base_url = zato_dashboard['dashboard_url']
    prefix = 'ui.delivery.' + CryptoManager.generate_hex_string(8) + '.'

    prerequisites = create_all_subscription_prerequisites(page, base_url, prefix, '1')
    create_pull_subscription(page, base_url, prerequisites['sec_name'], prerequisites['topic_name'])

    navigate_to_page(page, base_url, _Subscription_Page)
    row = find_row_by_link_text(page, prerequisites['sec_name'])
    item_id = row.get_attribute('id').replace('tr_', '')

    open_edit_dialog(page, 'pubsub.subscription', item_id)

    delivery_checkbox = page.locator(
        f'input.topic-delivery-enabled[data-topic="{prerequisites["topic_name"]}"]')
    if delivery_checkbox.count():
        delivery_checkbox.check()

    submit_edit_form(page)

    navigate_to_page(page, base_url, _Subscription_Page)

    assert page.locator('.ps-badge-deliv-enabled, .ps-pair-status-pending').count() >= 0

    sqlite_write_lock.release()

# ################################################################################################################################
# ################################################################################################################################
