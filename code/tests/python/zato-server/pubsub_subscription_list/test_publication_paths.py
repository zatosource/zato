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

def test_backend_publish_to_configured_topic(in_process_server:'any_') -> 'None':
    """ A publication through the backend reaches the pull subscriber of a configured topic.
    """
    server, _push_endpoint = in_process_server
    backend = server.server.pubsub_backend

    data = 'publication.' + CryptoManager.generate_hex_string(8)
    result = backend.publish(Topic_Pull, data)

    assert result.msg_id

    sub_key = None
    subscription_list = server.server.pubsub_subscription_list

    for candidate, topic, _status in subscription_list.statuses():
        if topic == Topic_Pull.lower():
            sub_key = candidate
            break

    assert sub_key is not None

    messages = backend.fetch_messages(sub_key, max_messages=10)
    assert messages

# ################################################################################################################################
# ################################################################################################################################
