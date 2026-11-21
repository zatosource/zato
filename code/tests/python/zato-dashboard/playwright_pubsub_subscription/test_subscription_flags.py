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

def test_subscription_flags(logged_in_page:'any_', zato_dashboard:'any_') -> 'None':
    """ Publishing and delivery flags changed in Dashboard are sent with the subscription form.
    """
    page = logged_in_page
    base_url = zato_dashboard['dashboard_url']
    prefix = 'ui.flags.' + CryptoManager.generate_hex_string(8) + '.'

    prerequisites = create_all_subscription_prerequisites(page, base_url, prefix, '1')
    create_pull_subscription(page, base_url, prerequisites['sec_name'], prerequisites['topic_name'])

    navigate_to_page(page, base_url, _Subscription_Page)
    row = find_row_by_link_text(page, prerequisites['sec_name'])
    item_id = row.get_attribute('id').replace('tr_', '')

    open_edit_dialog(page, 'pubsub.subscription', item_id)

    pub_checkbox = page.locator(f'input.topic-pub-enabled[data-topic="{prerequisites["topic_name"]}"]')
    delivery_checkbox = page.locator(
        f'input.topic-delivery-enabled[data-topic="{prerequisites["topic_name"]}"]')

    assert pub_checkbox.count() >= 1
    assert delivery_checkbox.count() >= 1

    pub_checkbox.uncheck()
    delivery_checkbox.uncheck()
    submit_edit_form(page)

    navigate_to_page(page, base_url, _Subscription_Page)
    open_edit_dialog(page, 'pubsub.subscription', item_id)

    assert not pub_checkbox.is_checked()
    assert not delivery_checkbox.is_checked()

# ################################################################################################################################
# ################################################################################################################################
