# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager

from .conftest import Topic_Pull
from .helpers import sub_key_for_topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def test_publication_after_lock_contention(in_process_server:'any_') -> 'None':
    """ A publication after a contended write still delivers and stores its payload.
    """
    server, _push_endpoint = in_process_server
    backend = server.server.pubsub_backend

    data = 'after.lock.' + CryptoManager.generate_hex_string(8)
    result = backend.publish(Topic_Pull, data)

    assert result.msg_id

    subscription_list = server.server.pubsub_subscription_list
    sub_key = sub_key_for_topic(subscription_list, Topic_Pull)
    messages = backend.fetch_messages(sub_key, max_messages=10)

    found = False

    for message in messages:
        if message['data'] == data:
            found = True
            break

    assert found

# ################################################################################################################################
# ################################################################################################################################
