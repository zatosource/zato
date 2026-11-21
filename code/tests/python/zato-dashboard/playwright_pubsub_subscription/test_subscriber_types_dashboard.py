# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import create_all_subscription_prerequisites, create_outgoing_rest, \
    create_pull_subscription, create_push_rest_subscription, navigate_to_page

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_Subscription_Page = '/zato/pubsub/subscription/'

# ################################################################################################################################

def test_subscriber_types_dashboard(
    logged_in_page:'any_',
    zato_dashboard:'any_',
    sqlite_write_lock:'any_',
) -> 'None':
    """ Pull and push REST subscribers created in Dashboard while the lock is held.
    """
    page = logged_in_page
    base_url = zato_dashboard['dashboard_url']
    prefix = 'ui.types.' + CryptoManager.generate_hex_string(8) + '.'

    prerequisites = create_all_subscription_prerequisites(page, base_url, prefix, '1')
    rest_name = create_outgoing_rest(page, base_url, prefix, 'rest')

    sqlite_write_lock.acquire()

    create_pull_subscription(page, base_url, prerequisites['sec_name'], prerequisites['topic_name'])
    create_push_rest_subscription(
        page, base_url, prerequisites['sec_name'], prerequisites['topic_name'], rest_name)

    navigate_to_page(page, base_url, _Subscription_Page)
    page.wait_for_selector('#data-table tbody tr', timeout=15000)

    sqlite_write_lock.release()

    navigate_to_page(page, base_url, _Subscription_Page)
    assert page.locator('#data-table tbody tr').count() >= 1

# ################################################################################################################################
# ################################################################################################################################
