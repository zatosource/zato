# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.sql.fast_path import State_Delivered

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from gevent.lock import BoundedSemaphore
    from zato.common.pubsub.sql.backend import SQLPubSubBackend
    from zato.common.typing_ import anylist, strset
    from zato.server.base.config_manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

# How many messages one batch of a delivery greenlet holds at most
Delivery_Batch_Size = 50

# The most bytes of message data in one batch that a publication hands over to an idle delivery greenlet,
# the same as in one batch that the greenlet reads itself.
_delivery_batch_max_len = PubSub.Message.Default_Max_Len

# How long a delivery greenlet waits for a publication when its queue is empty, in seconds.
_delivery_wait_seconds = 5.0

# The prefix of the sub keys of the queues of outgoing connections
_outgoing_sub_key_prefix = PubSub.Outgoing.Sub_Key_Prefix

# ################################################################################################################################
# ################################################################################################################################

def _read(backend:'SQLPubSubBackend', database_slots:'BoundedSemaphore', sub_key:'str') -> 'tuple[anylist, int]':
    """ Reads the deliverable messages of a subscriber, holding a database slot during the read, and returns them
    with the payload epoch from before the read.
    """
    read_epoch = backend.payload_cache.get_epoch()

    with database_slots:
        messages = backend.fetch_messages(sub_key, max_messages=Delivery_Batch_Size)

    out = (messages, read_epoch)
    return out

# ################################################################################################################################

def fetch_new(
    backend:'SQLPubSubBackend',
    database_slots:'BoundedSemaphore',
    config_manager:'ConfigManager',
    paused:'strset',
    sub_key:'str',
) -> 'tuple[anylist, int]':
    """ Reads the deliverable messages of a subscriber and, if there are none, waits for a publication
    and reads them again, holding a database slot during each read and never during the wait. Returns the messages
    and the payload epoch from before the read that returned them. A publication that commits during the wait
    may hand its messages over directly, with their first attempts recorded, and these are returned without a read.
    """
    # Each read clears the wake-up event of the subscriber before its query ..
    out = _read(backend, database_slots, sub_key)

    messages, _ = out

    if messages:
        return out

    # .. so a publication committed after the query leaves the event set and the wait returns at once,
    # .. whereas a wait that ends without a publication means there is nothing new to read ..
    event = backend.get_sub_event(sub_key)

    # .. an outgoing connection's queue acknowledges each message on its own, so it reads its messages itself ..
    if sub_key.startswith(_outgoing_sub_key_prefix):
        if event.wait(_delivery_wait_seconds):
            out = _read(backend, database_slots, sub_key)

        return out

    # .. while any other subscriber waits as a target that a publication may hand its batch over to,
    # .. waiting for the outcome of the commit of a publication that claimed it, whenever the wait ends.
    fast_path = backend.fast_path
    target = fast_path.add_push_target(sub_key, Delivery_Batch_Size, _delivery_batch_max_len)

    try:
        is_woken = event.wait(_delivery_wait_seconds)
        fast_path.wait_push_outcome(target)
    finally:
        fast_path.remove_push_target(target)

    # A batch handed over is delivered, unless the subscriber was paused or removed in the meantime,
    # in which case its rows, with their first attempts recorded, go out with the next read of the queue ..
    if target.state == State_Delivered:
        if sub_key in paused:
            return out

        if sub_key not in config_manager._push_subs:
            return out

        out = (target.messages, target.read_epoch)

    # .. and a publication that only woke the subscriber up is read from the queue.
    elif is_woken:
        out = _read(backend, database_slots, sub_key)

    return out

# ################################################################################################################################
# ################################################################################################################################
