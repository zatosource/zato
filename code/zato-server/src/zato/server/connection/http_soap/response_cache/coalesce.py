# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import threading
from dataclasses import dataclass

# Zato
from zato.server.connection.http_soap.response_cache.common import ModuleCtx
from zato.server.connection.http_soap.response_cache.store import serve_hit
from zato.server.metrics import zato_rest_channel_cache_operations_total

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anytuple, callable_
    from zato.server.connection.http_soap.response_cache.common import ResponseCacheContext
    ResponseCacheContext = ResponseCacheContext

# ################################################################################################################################
# ################################################################################################################################

# The per-key lock dict of the coalescing code - the class itself is defined below
keylockdict = dict[str, '_KeyLockEntry']

# ################################################################################################################################
# ################################################################################################################################

class CoalesceCounters:
    """ First-class counts of what the coalescing code did - metrics and tests read them directly,
    they are never inferred from timing.
    """
    def __init__(self) -> 'None':
        self.invoke_count = 0
        self.coalesced_count = 0
        self.coalesce_timeout_count = 0

# ################################################################################################################################

    def reset(self) -> 'None':
        self.invoke_count = 0
        self.coalesced_count = 0
        self.coalesce_timeout_count = 0

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class _KeyLockEntry:
    """ One per-key lock along with the count of requests currently interested in it.
    """
    lock: 'any_'
    refcount: 'int'

# ################################################################################################################################
# ################################################################################################################################

# Module-level coalescing state - the counters, the per-key lock dict and the one lock guarding the dict
counters = CoalesceCounters()

_key_locks:'keylockdict' = {}
_key_locks_lock = threading.RLock()

# ################################################################################################################################

def _checkout_key_lock(key:'str') -> '_KeyLockEntry':
    """ Returns the lock entry of a key, creating it if needed, and registers the caller's interest in it.
    """
    with _key_locks_lock:

        # The entry is created on the key's first checkout and reused until the last checkin removes it
        if not (out := _key_locks.get(key)):
            out = _KeyLockEntry()
            out.lock = threading.RLock()
            out.refcount = 0
            _key_locks[key] = out

        out.refcount += 1

        return out

# ################################################################################################################################

def _checkin_key_lock(key:'str') -> 'None':
    """ Withdraws the caller's interest in a key's lock, removing the entry once it is uncontended,
    so the dict does not grow with key cardinality.
    """
    with _key_locks_lock:
        entry = _key_locks[key]
        entry.refcount -= 1

        if entry.refcount == 0:
            del _key_locks[key]

# ################################################################################################################################

def invoke_coalesced(ctx:'ResponseCacheContext', invoke_func:'callable_', invoke_args:'anytuple') -> 'any_':
    """ Invokes the service with double-checked locking per key - on a miss of an admitted key,
    one request computes the entry while the others wait for it, bounded by the coalesce timeout.
    Coalescing is an optimization that can only ever no-op, not fail.
    """

    # First-ever requests have nothing to wait for and run in parallel
    if not ctx.is_admitted:
        counters.invoke_count += 1
        out = invoke_func(*invoke_args)
        return out

    entry = _checkout_key_lock(ctx.key)
    is_acquired = entry.lock.acquire(timeout=ctx.config.coalesce_timeout)

    # A waiter whose acquire timed out invokes the service itself - a slow service degrades
    # to uncoalesced behavior, never to queued callers.
    if not is_acquired:
        _checkin_key_lock(ctx.key)
        counters.coalesce_timeout_count += 1
        zato_rest_channel_cache_operations_total.labels(ctx.channel_name, ModuleCtx.Outcome_Coalesce_Timeout).inc()

        counters.invoke_count += 1
        out = invoke_func(*invoke_args)
        return out

    try:
        # The previous holder may have filled the cache while this request waited ..
        value = ctx.cache_api.get(ctx.key)

        if isinstance(value, dict):
            counters.coalesced_count += 1

            out = serve_hit(ctx, value, ModuleCtx.Outcome_Coalesced)
            return out

        # .. it did not, so this request becomes the holder and computes the entry itself -
        # the store happens inside invoke_func, before the lock is released below.
        counters.invoke_count += 1

        out = invoke_func(*invoke_args)
        return out

    finally:
        # The lock is always released, even when the holder's service raised an exception
        entry.lock.release()
        _checkin_key_lock(ctx.key)

# ################################################################################################################################
# ################################################################################################################################
