# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.facade import PubSubFacade
from zato.server.base.config_manager.pubsub_subscription_sync import reconcile_once
from zato_common_core.zato_common_core import SubscriptionList

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_Owned_Prefixes = (
    'zato.service.',
    'zato.out.',
    'zato.out.dlq.',
    'zato.in.dlq.',
)

# ################################################################################################################################

def test_facade_refuses_governed_sub_key(in_process_server:'any_') -> 'None':
    """ An ad hoc subscription with a governed sub key is refused.
    """
    server, _push_endpoint = in_process_server
    facade = PubSubFacade(server.server, 'test.owned.subscriptions')

    sub_key = 'sk' + CryptoManager.generate_hex_string(128)
    assert SubscriptionList.is_governed(sub_key)

    raised = False

    try:
        facade.subscribe('zato.service.test.topic', sub_key)
    except Exception:
        raised = True

    assert raised

# ################################################################################################################################

def test_mechanism_owned_rows_untouched_on_reload(in_process_server:'any_') -> 'None':
    """ Startup, reload and reconciliation leave the rows of mechanism-owned subscriptions in place.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server
    backend = parallel.pubsub_backend

    owned:'list' = []

    for prefix in _Owned_Prefixes:
        sub_key = prefix + CryptoManager.generate_hex_string(8)
        topic = prefix + 'topic.' + CryptoManager.generate_hex_string(8)
        backend.subscribe(sub_key, topic)
        owned.append((sub_key, topic))

    _ = parallel.config_manager.init_pubsub()
    reconcile_once(parallel.config_manager, full=True)

    for sub_key, topic in owned:
        subscribers = backend.get_topic_subscribers(topic)
        assert sub_key in subscribers

    governed = backend.get_governed_pairs()

    for sub_key, topic in owned:
        for pair_sub_key, _ in governed:
            assert pair_sub_key != sub_key

# ################################################################################################################################
# ################################################################################################################################
