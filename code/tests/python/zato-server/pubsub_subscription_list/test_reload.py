# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato_common_core.zato_common_core import SubscriptionList

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def test_reload_rebuilds_subscription_list(in_process_server:'any_') -> 'None':
    """ A reload replaces the subscription list from config.db and leaves every pair confirmed.
    """
    server, _push_endpoint = in_process_server

    _ = server.server.config_manager.init_pubsub()

    subscription_list = server.server.pubsub_subscription_list

    assert subscription_list.is_loaded()
    assert not subscription_list.has_unconfirmed()

    for _sub_key, _topic, status in subscription_list.statuses():
        assert status == SubscriptionList.STATUS_CONFIRMED

# ################################################################################################################################
# ################################################################################################################################
