# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Local
from _support import ModuleCtx, create_client, create_pull_subscription_to, create_topics, is_queued, \
    kill_config_process, new_marker, new_prefix, open_subscription_edit, pair_statuses, publish_accepted, queue_path, \
    set_edit_topic, subscription_item_id, wait_for, wait_for_queued, wait_for_statuses

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

    any_ = any_
    anydict = anydict
    Page = Page

# ################################################################################################################################
# ################################################################################################################################

class TestCtx:

    # How long each sync of config.db waits during the save, in milliseconds, which outlasts the save
    Sync_Delay_Ms = 120_000

    # How long the save is given to reach the delayed sync, in seconds
    Save_Stall_Seconds = 3.0

    # How long one publication is given to reach the queue during the recovery, in seconds
    Delivery_Timeout = 10.0

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_delivery(page:'Page', base_url:'str', path:'str', topic:'anydict') -> 'None':
    """ Publishes to a topic until a message reaches the queue, which it does once the worker loaded the configuration
    that the new config process committed.
    """
    def _is_delivered() -> 'bool':
        marker = new_marker('recovered')
        publish_accepted(page, base_url, topic, marker)

        def _is_queued() -> 'bool':
            out = is_queued(page, base_url, path, marker)
            return out

        try:
            wait_for(_is_queued, f'The queueing of {marker}', TestCtx.Delivery_Timeout)
        except Exception:
            out = False
        else:
            out = True

        return out

    wait_for(_is_delivered, f'The delivery of a message of {topic["name"]}')

# ################################################################################################################################
# ################################################################################################################################

def test_config_process_kill(logged_in_page:'any_', zato_dashboard:'anydict', filesystem_fault:'any_') -> 'None':
    """ A save during which the config process is killed while the syncs of config.db are delayed shows an error,
    and after the reload of the worker the page shows each topic as confirmed and each topic it shows delivers.
    """
    page = logged_in_page
    base_url = zato_dashboard['dashboard_url']
    prefix = new_prefix('config.kill')

    client = create_client(page, base_url, prefix, 'client')
    topics = create_topics(page, base_url, prefix, 2)

    first = topics[0]
    added = topics[1]
    first_name = first['name']
    added_name = added['name']

    create_pull_subscription_to(page, base_url, client['name'], [first_name])

    item_id = subscription_item_id(page, base_url, client['name'])
    wait_for_statuses(page, base_url, item_id, {first_name: ModuleCtx.Status_Confirmed}, 'The confirmation of the pair')

    path = queue_path(page, base_url, item_id, ModuleCtx.Queue_State_All)

    # Add a topic and save it while each sync of config.db waits ..
    open_subscription_edit(page, base_url, item_id, [first_name])
    set_edit_topic(page, added_name, True)

    filesystem_fault.delay_syncs(TestCtx.Sync_Delay_Ms)
    page.click('#edit-div input[type="submit"]')

    # .. the save is still waiting for its sync when the config process is killed ..
    time.sleep(TestCtx.Save_Stall_Seconds)
    assert page.is_visible('#edit-div'), 'The save completed without a sync of config.db'

    kill_config_process(zato_dashboard['server_process'].pid)
    filesystem_fault.clear()

    # .. Dashboard shows an error ..
    _ = page.wait_for_selector(ModuleCtx.User_Message_Failure, state='visible', timeout=ModuleCtx.Publish_Timeout)

    # .. the page shows each topic of the subscription as confirmed, with or without the topic of the save ..
    def _is_settled() -> 'bool':
        statuses = pair_statuses(page, base_url, item_id)

        if statuses is None:
            raise Exception(f'The subscription {item_id} is no longer listed')

        out = first_name in statuses

        for status in statuses.values():
            if status != ModuleCtx.Status_Confirmed:
                out = False

        return out

    wait_for(_is_settled, 'The confirmation of each pair after the recovery')

    statuses = pair_statuses(page, base_url, item_id)
    if statuses is None:
        raise Exception(f'The subscription {item_id} is no longer listed')

    # .. each topic that the page shows delivers to the subscriber ..
    _wait_for_delivery(page, base_url, path, first)

    if added_name in statuses:
        _wait_for_delivery(page, base_url, path, added)

    # .. and the topic that the page does not show delivers nothing to it.
    else:
        added_marker = new_marker('absent')
        publish_accepted(page, base_url, added, added_marker)

        first_marker = new_marker('present')
        publish_accepted(page, base_url, first, first_marker)

        wait_for_queued(page, base_url, path, first_marker)
        assert not is_queued(page, base_url, path, added_marker)

# ################################################################################################################################
# ################################################################################################################################
