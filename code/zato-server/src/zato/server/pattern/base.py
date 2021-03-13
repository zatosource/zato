# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from logging import getLogger

# Zato
from zato.common import CHANNEL
from zato.common.util import spawn_greenlet
from zato.server.pattern.model import CacheEntry, ParallelCtx

# ################################################################################################################################

if 0:
    from gevent.lock import RLock
    from zato.server.service import Service

    Service = Service

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_channel_fanout = CHANNEL.FANOUT_CALL
_channel_parallel = CHANNEL.PARALLEL_EXEC_CALL

# ################################################################################################################################
# ################################################################################################################################

class ParallelBase:
    """ A base class for most parallel integration patterns. An instance of this class is created for each service instance.
    """
    def __init__(self, source, cache, lock):
        # type: (Service, dict, RLock) -> None
        self.source = source
        self.cache = cache
        self.lock = lock
        self.cid = source.cid

# ################################################################################################################################

    def _invoke(self, ctx):
        # type: (ParallelCtx)

        # Store metadata about our invocation ..
        with self.lock:

            # .. create a new entry ..
            entry = CacheEntry()
            entry.cid = ctx.cid
            entry.req_ts_utc = ctx.req_ts_utc
            entry.on_target_list = ctx.on_target_list
            entry.on_final_list = ctx.on_final_list

            # .. and add it to the cache.
            self.cache[ctx.cid] = entry

        print()

        for item in ctx.target_list:
            print(111, item)

        print(222, self.cache)

        print()

# ################################################################################################################################

    def invoke(self, targets, on_final, on_target=None, cid=None, _utcnow=datetime.utcnow):
        """ Invokes targets collecting their responses, can be both as a whole or individual ones,
        and executes callback(s).
        """
        # type: (list, list, list, str) -> None

        # Establish what our CID is ..
        cid = cid or self.cid

        # .. create an execution context ..
        ctx = ParallelCtx()
        ctx.cid = cid
        ctx.req_ts_utc = _utcnow()
        ctx.source_name = self.source.name
        ctx.target_list = targets
        ctx.on_final_list = [on_final] if isinstance(on_final, str) else on_final
        ctx.on_target_list = [on_target] if isinstance(on_target, str) else on_target

        # .. invoke our implementation in background ..
        spawn_greenlet(self._invoke, ctx)

        # .. and return the CID to the caller.
        return cid

# ################################################################################################################################
# ################################################################################################################################
