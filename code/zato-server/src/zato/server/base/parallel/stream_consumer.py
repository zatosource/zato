# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The consumer side of the Redis streams that the scheduler and the queue bridge send to the server. Every worker
# of a server reads the streams of a consumer group under a consumer name of its slot, so the group distributes
# the entries among the workers, and the replacement of a terminated worker takes over the entries that the group
# delivered to its slot and that were never acknowledged.

# gevent
from gevent import sleep, spawn

# redis
from redis.exceptions import ConnectionError as RedisConnectionError, TimeoutError as RedisTimeoutError

# Zato
from zato.common.worker_slot import get_slot_or_single

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from gevent import Greenlet
    from redis import Redis
    from zato.common.typing_ import any_, anydict, anylist, callable_

    any_ = any_
    anydict = anydict
    callable_ = callable_
    Greenlet = Greenlet
    Redis = Redis

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How many pending entries one XPENDING call returns at most
    Pending_Batch_Size = 100

    # The prefix of an exclusive start of an XPENDING range
    Exclusive_Prefix = '('

    # How long an acknowledgement waits before it is sent again to a Redis that could not be reached, in seconds
    Unreachable_Retry_Interval = 1.0

# ################################################################################################################################
# ################################################################################################################################

def get_consumer_name(group_name:'str') -> 'str':
    """ Returns the consumer name under which the worker of this process reads the streams of a consumer group.
    """
    slot = get_slot_or_single()

    out = f'{group_name}-{slot}'
    return out

# ################################################################################################################################

def claim_own_pending(redis_conn:'Redis', stream:'str', group_name:'str', consumer_name:'str') -> 'anylist':
    """ Claims again for a consumer name the entries of a stream that the group delivered to it and that were never
    acknowledged, which a worker of the same slot left when it terminated, and returns them as pairs of an ID and fields.
    The entries pending for the other consumer names, those of the live workers, remain theirs.
    """
    out:'anylist' = []
    start = '-'

    while True:

        # The entries pending for this consumer name come in batches, each one after the last entry of the previous one ..
        pending = redis_conn.xpending_range(
            stream,
            group_name,
            min=start,
            max='+',
            count=ModuleCtx.Pending_Batch_Size,
            consumername=consumer_name,
        )

        if not pending:
            break

        # .. each batch is claimed with no minimum idle time, which returns the fields of its entries ..
        msg_ids = [item['message_id'] for item in pending]
        claimed = redis_conn.xclaim(stream, group_name, consumer_name, min_idle_time=0, message_ids=msg_ids)
        out.extend(claimed)

        # .. until a batch shorter than the limit was the last one.
        if len(pending) < ModuleCtx.Pending_Batch_Size:
            break

        last_msg_id = msg_ids[-1]
        start = f'{ModuleCtx.Exclusive_Prefix}{last_msg_id}'

    return out

# ################################################################################################################################

def _run_then_ack(
    redis_conn:'Redis',
    stream:'str',
    group_name:'str',
    msg_id:'str',
    handler:'callable_',
    fields:'anydict',
    ) -> 'None':

    # The entry is acknowledged after its handler, also one that raised, which would otherwise run again
    # with each replacement of the worker.
    try:
        handler(fields)
    finally:
        _ack_until_reachable(redis_conn, stream, group_name, msg_id)

# ################################################################################################################################

def _ack_until_reachable(redis_conn:'Redis', stream:'str', group_name:'str', msg_id:'str') -> 'None':
    """ Acknowledges an entry, again until Redis accepts it, because an entry that a live worker did not acknowledge
    remains pending until the worker of its slot is replaced.
    """
    while True:
        try:
            _ = redis_conn.xack(stream, group_name, msg_id)
        except (RedisConnectionError, RedisTimeoutError):
            sleep(ModuleCtx.Unreachable_Retry_Interval)
        else:
            return

# ################################################################################################################################

def spawn_then_ack(
    redis_conn:'Redis',
    stream:'str',
    group_name:'str',
    msg_id:'str',
    handler:'callable_',
    fields:'anydict',
    ) -> 'Greenlet':
    """ Runs the handler of one entry in a greenlet of its own and acknowledges the entry when the handler returns,
    so that the entry of a worker that terminates during the handler remains pending for the replacement of the worker.
    """
    out = spawn(_run_then_ack, redis_conn, stream, group_name, msg_id, handler, fields)
    return out

# ################################################################################################################################
# ################################################################################################################################
