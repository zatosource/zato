# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time

# PyYAML
import yaml

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import create_all_subscription_prerequisites, create_pull_subscription, \
    navigate_to_page

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_Subscription_Page = '/zato/pubsub/subscription/'

# ################################################################################################################################

def test_enmasse_pending(
    logged_in_page:'any_',
    zato_dashboard:'any_',
    sqlite_write_lock:'any_',
) -> 'None':
    """ An enmasse file with deletions placed into the pickup directory while the lock is held shows pending pairs.
    """
    page = logged_in_page
    base_url = zato_dashboard['dashboard_url']
    prefix = 'ui.enmasse.' + CryptoManager.generate_hex_string(8) + '.'

    prerequisites = create_all_subscription_prerequisites(page, base_url, prefix, '1')
    create_pull_subscription(page, base_url, prerequisites['sec_name'], prerequisites['topic_name'])

    pickup_dir = os.path.join(zato_dashboard['server_dir'], 'pickup', 'incoming', 'services')
    os.makedirs(pickup_dir, exist_ok=True)

    definition = {
        'pubsub_subscription': [{
            'security': prerequisites['sec_name'],
            'delivery_type': 'pull',
            'topic_list': [],
        }],
    }

    sqlite_write_lock.acquire()

    path = os.path.join(pickup_dir, f'enmasse-delete-{CryptoManager.generate_hex_string(4)}.yaml')
    with open(path, 'w') as enmasse_file:
        _ = enmasse_file.write(yaml.dump(definition))

    navigate_to_page(page, base_url, _Subscription_Page)
    page.wait_for_selector('.ps-pair-status-pending, .ps-pair-status-pending-removal, #data-table', timeout=30000)

    sqlite_write_lock.release()

    deadline = time.monotonic() + 60

    while time.monotonic() < deadline:
        navigate_to_page(page, base_url, _Subscription_Page)
        if page.locator('.ps-pair-status-pending, .ps-pair-status-pending-removal').count() == 0:
            break
        time.sleep(1)

# ################################################################################################################################
# ################################################################################################################################
