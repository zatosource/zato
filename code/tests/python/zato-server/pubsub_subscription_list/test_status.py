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

def test_statuses_after_startup(in_process_server:'any_') -> 'None':
    """ After startup every configured pair of the subscription list is confirmed.
    """
    server, _push_endpoint = in_process_server
    subscription_list = server.server.pubsub_subscription_list

    assert subscription_list.is_loaded()

    for _sub_key, _topic, status in subscription_list.statuses():
        assert status == SubscriptionList.STATUS_CONFIRMED

# ################################################################################################################################

def test_has_unconfirmed_false_when_synced(in_process_server:'any_') -> 'None':
    """ A synchronized subscription list reports no unconfirmed pairs.
    """
    server, _push_endpoint = in_process_server
    subscription_list = server.server.pubsub_subscription_list

    assert not subscription_list.has_unconfirmed()

# ################################################################################################################################
# ################################################################################################################################
