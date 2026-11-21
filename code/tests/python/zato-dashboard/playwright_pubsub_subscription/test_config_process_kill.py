# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import signal
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

def test_config_process_kill(
    logged_in_page:'any_',
    zato_dashboard:'any_',
    filesystem_fault:'any_',
) -> 'None':
    """ A save during which the config process is killed shows an error and recovers after the reload.
    """
    page = logged_in_page
    base_url = zato_dashboard['dashboard_url']
    prefix = 'ui.cfgkill.' + CryptoManager.generate_hex_string(8) + '.'

    prerequisites = create_all_subscription_prerequisites(page, base_url, prefix, '1')
    create_pull_subscription(page, base_url, prerequisites['sec_name'], prerequisites['topic_name'])

    filesystem_fault.delay_syncs(8000)

    navigate_to_page(page, base_url, _Subscription_Page)
    row = find_row_by_link_text(page, prerequisites['sec_name'])
    item_id = row.get_attribute('id').replace('tr_', '')

    open_edit_dialog(page, 'pubsub.subscription', item_id)
    unpick_subscription_topic(page, prerequisites['topic_name'])

    server_process = zato_dashboard['server_process']
    if server_process:
        try:
            os.kill(server_process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass

    try:
        submit_edit_form(page)
    except Exception:
        pass

    filesystem_fault.clear()
    time.sleep(2)

    navigate_to_page(page, base_url, _Subscription_Page)
    page.wait_for_selector('#data-table', timeout=30000)

# ################################################################################################################################
# ################################################################################################################################
