# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import create_all_subscription_prerequisites, create_pull_subscription, \
    find_row_by_link_text, get_item_id, navigate_to_page, open_edit_dialog, open_publish_overlay, \
    publish_via_overlay, submit_edit_form, unpick_subscription_topic

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

def test_publication_ordering(
    logged_in_page:'any_',
    zato_dashboard:'any_',
    sqlite_write_lock:'any_',
) -> 'None':
    """ A publication held behind the lock while the operator removes the topic shows in the queue only when it committed first.
    """
    page = logged_in_page
    base_url = zato_dashboard['dashboard_url']
    prefix = 'ui.order.' + CryptoManager.generate_hex_string(8) + '.'

    prerequisites = create_all_subscription_prerequisites(page, base_url, prefix, '1')
    create_pull_subscription(page, base_url, prerequisites['sec_name'], prerequisites['topic_name'])

    sqlite_write_lock.acquire()

    navigate_to_page(page, base_url, _Topic_Page)
    topic_id = get_item_id(page, prerequisites['topic_name'])
    open_publish_overlay(page, topic_id)
    publish_via_overlay(page, 'order.publish.first')

    navigate_to_page(page, base_url, _Subscription_Page)
    row = find_row_by_link_text(page, prerequisites['sec_name'])
    item_id = row.get_attribute('id').replace('tr_', '')
    open_edit_dialog(page, 'pubsub.subscription', item_id)
    unpick_subscription_topic(page, prerequisites['topic_name'])
    submit_edit_form(page)

    sqlite_write_lock.release()

    navigate_to_page(page, base_url, _Subscription_Page)
    page.wait_for_selector('#data-table', timeout=15000)

# ################################################################################################################################
# ################################################################################################################################
