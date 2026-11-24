# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager

# Fault tools
from container import Container
from faults import Packet_Loss, PacketFault

# Local
from _support import assert_rows_equal_list, get_msg_ids, publish_accepted, publish_client, pull_all, pull_client, wait_for, \
    wait_for_no_unconfirmed, yaml_subscription

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist

    any_ = any_
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The share of the packets of the container of PostgreSQL that the partial loss drops, in percent
    Partial_Loss = 20

    # How many messages are published to each topic during the partial loss
    Publication_Count = 10

# ################################################################################################################################
# ################################################################################################################################

def _publish_many(publisher:'any_', topic_name:'str') -> 'strlist':
    """ Publishes messages to a topic, each again until it is accepted, and returns their IDs.
    """
    out:'strlist' = []

    for _ in range(ModuleCtx.Publication_Count):
        msg_id = publish_accepted(publisher, topic_name, 'network.' + CryptoManager.generate_hex_string(32))
        out.append(msg_id)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_network_faults(
    environment:'any_',
    pickup:'any_',
    runtime:'any_',
    names:'any_',
    database_proxy:'any_',
    ) -> 'None':
    """ Partial packet loss during enmasse files and publications ends with rows equal to the subscription list,
    every message delivered to its subscribers and none to a removed pair.
    """
    sub_key = runtime.sub_key(names.security_pull)
    added_pair = (sub_key, names.topic_second.lower())
    removed_pair = (sub_key, names.topic_pull.lower())

    fault = PacketFault(Container(database_proxy.database.container_name), Packet_Loss)

    # The subscriber is subscribed to both topics ..
    pickup.apply('add-second', yaml_subscription(names.security_pull, [names.topic_pull, names.topic_second]))
    wait_for_no_unconfirmed(runtime)

    assert added_pair in runtime.governed_pairs()
    assert_rows_equal_list(runtime)

    # .. and a part of the packets to PostgreSQL is lost while the server applies the removal
    # and messages are published to both topics.
    publisher = publish_client(environment, names)
    fault.apply(ModuleCtx.Partial_Loss)

    try:
        pickup.apply('remove-pull-during-partial-loss', yaml_subscription(names.security_pull, [names.topic_second]))
        removed_topic_msg_ids = _publish_many(publisher, names.topic_pull)
        kept_topic_msg_ids = _publish_many(publisher, names.topic_second)
    finally:
        fault.remove()

    wait_for_no_unconfirmed(runtime)

    assert removed_pair not in runtime.governed_pairs()
    assert_rows_equal_list(runtime)

    # No subscriber is left on the topic removed, so its deliveries go with the rows of the pair
    def _is_emptied() -> 'bool':
        out = runtime.topic_deliveries(names.topic_pull) == 0
        return out

    wait_for(_is_emptied, 'The removal of the deliveries of the topic removed')

    pull_msg_ids = get_msg_ids(pull_all(pull_client(environment, names, names.security_pull)))
    second_msg_ids = get_msg_ids(pull_all(pull_client(environment, names, names.security_second)))

    for msg_id in kept_topic_msg_ids:
        assert msg_id in pull_msg_ids
        assert msg_id in second_msg_ids

    for msg_id in removed_topic_msg_ids:
        assert msg_id not in pull_msg_ids

# ################################################################################################################################
# ################################################################################################################################
