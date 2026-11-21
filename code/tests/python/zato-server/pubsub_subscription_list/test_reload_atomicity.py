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
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def test_reload_replaces_list_without_greenlet_switch(in_process_server:'any_') -> 'None':
    """ No greenlet switch occurs between the first and the last memory change of a reload of the subscription list.
    """
    server, _push_endpoint = in_process_server

    with SwitchObserver() as observer:
        _ = server.server.config_manager.init_pubsub()

    assert observer.switches == []

# ################################################################################################################################
# ################################################################################################################################
