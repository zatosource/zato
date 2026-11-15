# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from math import ceil
from time import monotonic
from uuid import uuid4

# gevent
from gevent import sleep

# Zato
from zato.server.connection.cache import ModuleCtx as CacheModuleCtx
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

# Module-level coalescing counters
counters = CoalesceCounters()

# ################################################################################################################################

def _serve_coalesced(ctx:'ResponseCacheContext', value:'any_') -> 'any_':
    """ Serves the entry that another request stored while this one waited for it.
    """
    counters.coalesced_count += 1

    out = serve_hit(ctx, value, ModuleCtx.Outcome_Coalesced)
    return out

# ################################################################################################################################

def _invoke(invoke_func:'callable_', invoke_args:'anytuple') -> 'any_':
    """ Invokes the service on behalf of the current request.
    """
    counters.invoke_count += 1

    out = invoke_func(*invoke_args)
    return out

# ################################################################################################################################

def invoke_coalesced(ctx:'ResponseCacheContext', invoke_func:'callable_', invoke_args:'anytuple') -> 'any_':
    """ Invokes the service with one lock per key in Redis, shared by every process - on a miss of an admitted key,
    the request that stores the lock key computes the entry while the others poll for it, bounded by the coalesce timeout.
    Coalescing is an optimization that can only ever no-op, not fail.
    """
    coalesce_timeout = ctx.config.coalesce_timeout

    # First-ever requests have nothing to wait for and run in parallel ..
    if not ctx.is_admitted:
        out = _invoke(invoke_func, invoke_args)
        return out

    # .. and without a timeout no request waits for another one, while the lock key would have no expiry.
    if not coalesce_timeout:
        out = _invoke(invoke_func, invoke_args)
        return out

    # The lock key expires with the coalesce timeout, so a holder whose process terminated blocks no one beyond it
    lock_key = CacheModuleCtx.Response_Lock_Prefix + ctx.key
    lock_expiry = ceil(coalesce_timeout)
    token = uuid4().hex

    deadline = monotonic() + coalesce_timeout

    while True:

        # The request that stores the lock key becomes the holder ..
        if ctx.cache_api.set_if_absent(lock_key, token, lock_expiry):
            try:

                # .. the previous holder may have filled the cache since the last poll of this request ..
                value = ctx.cache_api.get(ctx.key)

                if isinstance(value, dict):
                    out = _serve_coalesced(ctx, value)
                    return out

                # .. it did not, so this request computes the entry itself -
                # the store happens inside invoke_func, before the lock is released below.
                out = _invoke(invoke_func, invoke_args)
                return out

            finally:
                # The lock is always released, even when the holder's service raised an exception,
                # unless it expired and another request holds it now
                _ = ctx.cache_api.delete_if_value(lock_key, token)

        # .. every other request polls for the entry, and takes the lock in turn once it is released without one ..
        value = ctx.cache_api.get(ctx.key)

        if isinstance(value, dict):
            out = _serve_coalesced(ctx, value)
            return out

        # .. and a request that waited for the whole timeout invokes the service itself - a slow service degrades
        # to uncoalesced behavior, never to queued callers.
        if monotonic() >= deadline:
            counters.coalesce_timeout_count += 1
            zato_rest_channel_cache_operations_total.labels(ctx.channel_name, ModuleCtx.Outcome_Coalesce_Timeout).inc()

            out = _invoke(invoke_func, invoke_args)
            return out

        sleep(ModuleCtx.Coalesce_Poll_Interval)

# ################################################################################################################################
# ################################################################################################################################
