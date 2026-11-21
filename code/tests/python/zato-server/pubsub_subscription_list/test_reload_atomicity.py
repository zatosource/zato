# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.test.pubsub_in_process_support import SwitchObserver

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

    any_ = any_
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

class _ObservedSubscriptionList:
    """ Delegates to the subscription list of the server and records the greenlet switches during each replacement.
    """

    def __init__(self, subscription_list:'any_') -> 'None':
        self._subscription_list = subscription_list
        self.replacements:'anylist' = []

    def replace(self, subscribers:'any_', committed:'any_') -> 'any_':
        with SwitchObserver() as observer:
            out = self._subscription_list.replace(subscribers, committed)

        self.replacements.append(observer.switches)
        return out

    def __getattr__(self, name:'str') -> 'any_':
        out = getattr(self._subscription_list, name)
        return out

# ################################################################################################################################
# ################################################################################################################################

def test_reload_replaces_list_without_greenlet_switch(in_process_server:'any_') -> 'None':
    """ No greenlet switch occurs between the first and the last memory change of a reload of the subscription list.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server

    subscription_list = parallel.pubsub_subscription_list
    observed = _ObservedSubscriptionList(subscription_list)

    parallel.pubsub_subscription_list = observed

    try:
        _ = parallel.config_manager.init_pubsub()
    finally:
        parallel.pubsub_subscription_list = subscription_list

    assert len(observed.replacements) == 1
    assert observed.replacements[0] == []

# ################################################################################################################################
# ################################################################################################################################
