# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Local
from _support import ModuleCtx, Pickup, create_client, create_pull_subscription_to, create_topics, new_prefix, \
    subscription_item_id, wait_for_statuses, yaml_subscription

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

    any_ = any_
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

def test_enmasse_pending(logged_in_page:'any_', zato_dashboard:'anydict', write_lock:'any_') -> 'None':
    """ An enmasse file with deletions placed into the pickup directory while the lock is held shows the affected
    pairs as pending removal until the reconciliation.
    """
    page = logged_in_page
    base_url = zato_dashboard['dashboard_url']
    prefix = new_prefix('enmasse')

    client = create_client(page, base_url, prefix, 'client')
    topics = create_topics(page, base_url, prefix, 2)

    removed_name = topics[0]['name']
    kept_name = topics[1]['name']

    create_pull_subscription_to(page, base_url, client['name'], [removed_name, kept_name])

    item_id = subscription_item_id(page, base_url, client['name'])
    confirmed = {removed_name: ModuleCtx.Status_Confirmed, kept_name: ModuleCtx.Status_Confirmed}
    wait_for_statuses(page, base_url, item_id, confirmed, 'The confirmation of both pairs')

    # Import a file that leaves the subscriber on one topic while no row of a pair can be deleted ..
    write_lock.acquire()

    pickup = Pickup(zato_dashboard['server_dir'])
    definitions = yaml_subscription(client['name'], [kept_name])
    pickup.apply(f'{prefix}yaml', definitions)

    pending = {removed_name: ModuleCtx.Status_Pending_Removal, kept_name: ModuleCtx.Status_Confirmed}
    wait_for_statuses(page, base_url, item_id, pending, 'The pending removal of the pair')

    # .. and the reconciliation deletes its rows after the release.
    write_lock.release()
    wait_for_statuses(page, base_url, item_id, {kept_name: ModuleCtx.Status_Confirmed}, 'The removal of the pair')

# ################################################################################################################################
# ################################################################################################################################
