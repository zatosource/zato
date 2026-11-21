# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from time import monotonic

# gevent
from gevent import sleep, spawn

# Zato
from zato.common.pubsub.subscription_list import Reconcile_Full_Interval, Reconcile_Pending_Interval
from zato.common.worker_slot import is_config_process
from zato.server.base.config_manager.pubsub_subscription_sync import reconcile_once

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.server.base.config_manager import ConfigManager

    ConfigManager = ConfigManager

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def start_subscription_reconciler(config_manager:'ConfigManager') -> 'None':
    """ Starts the greenlet that commits the difference between the subscription list and the rows.
    """
    if is_config_process():
        return

    _ = spawn(_reconcile_loop, config_manager)

# ################################################################################################################################

def _reconcile_loop(config_manager:'ConfigManager') -> 'None':
    """ Commits unconfirmed pairs on the pending interval and compares the list with all governed rows on the full one.
    """
    last_full = monotonic()

    while True:

        sleep(Reconcile_Pending_Interval)

        subscription_list = config_manager.server.pubsub_subscription_list

        if not subscription_list.is_loaded():
            continue

        now = monotonic()
        needs_full = (now - last_full) >= Reconcile_Full_Interval

        if needs_full:
            reconcile_once(config_manager, full=True)
            last_full = now

        elif subscription_list.has_unconfirmed():
            reconcile_once(config_manager, full=False)

# ################################################################################################################################
# ################################################################################################################################
