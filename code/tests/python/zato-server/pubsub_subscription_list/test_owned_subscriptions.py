# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.facade import PubSubFacade
from zato_common_core.zato_common_core import SubscriptionList

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pubsub_in_process import InProcessServer
    from zato.common.test.pubsub_in_process_support import RESTPushEndpoint
    from zato.common.typing_ import any_

    any_ = any_
    InProcessServer = InProcessServer
    RESTPushEndpoint = RESTPushEndpoint

# ################################################################################################################################
# ################################################################################################################################

def test_facade_refuses_governed_sub_key(in_process_server:'any_') -> 'None':
    """ An ad hoc subscription with a governed sub key is refused.
    """
    server, _push_endpoint = in_process_server
    facade = PubSubFacade(server.server, 'test.owned.subscriptions')

    sub_key = 'sk' + CryptoManager.generate_hex_string(32)
    assert SubscriptionList.is_governed(sub_key)

    raised = False

    try:
        facade.subscribe('zato.service.test.topic', sub_key)
    except Exception:
        raised = True

    assert raised

# ################################################################################################################################

def test_mechanism_owned_rows_untouched(in_process_server:'any_') -> 'None':
    """ Startup and reload leave the rows of mechanism-owned subscriptions in place.
    """
    server, _push_endpoint = in_process_server
    backend = server.server.pubsub_backend

    owned_sub_key = 'zato.service.' + CryptoManager.generate_hex_string(8)
    owned_topic = 'zato.service.' + CryptoManager.generate_hex_string(8)

    backend.subscribe(owned_sub_key, owned_topic)

    pairs_before = backend.get_governed_pairs()
    backend.get_topic_subscribers(owned_topic)

    _ = server.server.config_manager.init_pubsub()

    pairs_after = backend.get_governed_pairs()
    subscribers = backend.get_topic_subscribers(owned_topic)

    assert owned_sub_key in subscribers
    assert pairs_before == pairs_after

# ################################################################################################################################
# ################################################################################################################################
