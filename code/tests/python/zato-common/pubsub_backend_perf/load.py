# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
from gevent import sleep

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.sql.backend import SQLPubSubBackend
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

def consume_until_done(backend:'SQLPubSubBackend', sub_key:'str', counters:'anydict', block_ms:'int') -> 'None':
    """ What one consumer greenlet runs - the same loop push delivery uses later:
    blocking fetch, then one batched acknowledgement per fetched batch,
    until the whole population has delivered everything the run expects.
    """
    while counters['delivered'] < counters['expected']:

        messages = backend.fetch_messages(sub_key, block_ms=block_ms)

        if not messages:
            continue

        msg_ids:'strlist' = []

        for message in messages:
            msg_ids.append(message['msg_id'])

        _ = backend.ack_messages(sub_key, msg_ids)

        counters['delivered'] += len(messages)

        # Yield after each batch the way the real delivery loop yields on the network
        # I/O of invoking its target - fetch and ack are synchronous C calls that never
        # switch greenlets on their own, and without this a deep drain would starve
        # every publisher on the shared loop, which the real pattern does not do.
        sleep(0)

# ################################################################################################################################

def consume_until_stopped(
    backend:'SQLPubSubBackend',
    sub_key:'str',
    per_sub_delivered:'anydict',
    stop:'anydict',
    block_ms:'int',
    ) -> 'None':
    """ Like consume_until_done, for runs where how much each queue will deliver
    cannot be known upfront - e.g. because operators clear queues mid-run. Counts
    deliveries per subscriber and runs until told to stop.
    """
    while not stop['is_set']:

        messages = backend.fetch_messages(sub_key, block_ms=block_ms)

        if not messages:
            continue

        msg_ids:'strlist' = []

        for message in messages:
            msg_ids.append(message['msg_id'])

        _ = backend.ack_messages(sub_key, msg_ids)

        per_sub_delivered[sub_key] += len(messages)

        # The same yield as in consume_until_done, for the same reason.
        sleep(0)

# ################################################################################################################################
# ################################################################################################################################
