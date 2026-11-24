# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager

from .conftest import Topic_Pull, Topic_Second
from .helpers import add_topic_pending, remove_topic_pending, sub_key_for_topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def test_addition_then_removal_before_publication(in_process_server:'any_') -> 'None':
    """ An addition and a removal whose row writes both fail leave the list governing the publication.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server
    subscription_list = parallel.pubsub_subscription_list
    backend = parallel.pubsub_backend

    sub_key = sub_key_for_topic(subscription_list, Topic_Pull)

    add_topic_pending(subscription_list, sub_key, Topic_Second)
    remove_topic_pending(subscription_list, sub_key, Topic_Second)

    data = 'lock.order.' + CryptoManager.generate_hex_string(8)
    result = backend.publish(Topic_Second, data)

    assert result.msg_id

    messages = backend.fetch_messages(sub_key, max_messages=20)

    for message in messages:
        assert message['data'] != data

# ################################################################################################################################
# ################################################################################################################################
