# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager

from .conftest import Topic_Pull

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def test_inactive_topic_refuses_publication(in_process_server:'any_') -> 'None':
    """ A publication to an inactive topic of config.db is refused.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server

    parallel.pubsub_inactive_topics.add(Topic_Pull.lower())

    raised = False

    try:
        _ = parallel.pubsub_backend.publish(Topic_Pull, 'inactive.' + CryptoManager.generate_hex_string(8))
    except Exception:
        raised = True

    assert raised

    parallel.pubsub_inactive_topics.discard(Topic_Pull.lower())

# ################################################################################################################################
# ################################################################################################################################
