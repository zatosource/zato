# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from logging import getLogger

# Zato
from zato.common import CHANNEL
from zato.common.util import spawn_greenlet
from zato.server.pattern.model import CacheEntry, InvocationResponse, ParallelCtx, Target

# ################################################################################################################################

if 0:
    from gevent.lock import RLock
    from zato.server.service import Service

    Service = Service

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ParallelBase:
    """ A base class for most parallel integration patterns. An instance of this class is created for each service instance.
    """
    call_channel = '<parallel-base-call-channel-not-set>'
    on_target_channel = '<parallel-base-target-channel-not-set>'
    on_final_channel = '<parallel-base-final-channel-not-set>'
    needs_on_final = False

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
            entry.len_targets = len(ctx.target_list)
            entry.remaining_targets = entry.len_targets
            entry.target_responses = []
            entry.final_responses = {}
            entry.on_target_list = ctx.on_target_list
            entry.on_final_list = ctx.on_final_list

            # .. and add it to the cache.
            self.cache[ctx.cid] = entry

        # Now that metadata is stored, we can actually invoke each of the serviced from our list of targets.

        for item in ctx.target_list: # type: Target
            self.source.invoke_async(item.name, item.payload, channel=self.call_channel, cid=ctx.cid)

# ################################################################################################################################

    def invoke(self, targets, on_final, on_target=None, cid=None, _utcnow=datetime.utcnow):
        """ Invokes targets collecting their responses, can be both as a whole or individual ones,
        and executes callback(s).
        """
        # type: (dict, list, list, str, object) -> None

        # Establish what our CID is ..
        cid = cid or self.cid

        # .. set up targets to invoke ..
        target_list = []
        for target_name, payload in targets.items():
            target = Target()
            target.name = target_name
            target.payload = payload
            target_list.append(target)

        # .. create an execution context ..
        ctx = ParallelCtx()
        ctx.cid = cid
        ctx.req_ts_utc = _utcnow()
        ctx.source_name = self.source.name
        ctx.target_list = target_list

        # .. on-final is always available ..
        ctx.on_final_list = [on_final] if isinstance(on_final, str) else on_final

        # .. but on-target may be None ..
        if on_target:
            ctx.on_target_list = [on_target] if isinstance(on_target, str) else on_target

        # .. invoke our implementation in background ..
        try:
            spawn_greenlet(self._invoke, ctx)
        except Exception:
            # Explicitly ignore any exception caught - this is because we are catching
            # deeper in the call stack to provide it to callback services so we do not want
            # to raise it here too.
            pass

        # .. and return the CID to the caller.
        return cid

# ################################################################################################################################

    def on_call_finished(self, invoked_service, response, exception, _utcnow=datetime.utcnow):
        # type: (Service, object, Exception, object)

        # Update metadata about the current parallel execution under a server-wide lock ..
        with self.lock:

            # .. find our cache entry ..
            entry = self.cache.get(invoked_service.cid) # type: CacheEntry

            # .. exit early if we cannot find the entry for any reason ..
            if not entry:
                logger.warning('No such parallel cache key `%s`', invoked_service.cid)
                return

            # .. alright, we can proceed ..
            else:

                # .. update the number of targets already invoked ..
                entry.remaining_targets -= 1

                # .. build information about the response that we have ..
                invocation_response = InvocationResponse()
                invocation_response.cid = invoked_service.cid
                invocation_response.req_ts_utc = entry.req_ts_utc
                invocation_response.resp_ts_utc = _utcnow()
                invocation_response.response = response
                invocation_response.exception = exception
                invocation_response.ok = False if exception else True
                invocation_response.source = self.source.name
                invocation_response.target = invoked_service.name

                # For pre-Zato 3.2 compatibility, callbacks expect dicts on input.
                dict_payload = {
                    'source': invocation_response.source,
                    'target': invocation_response.target,
                    'response': invocation_response.response,
                    'req_ts_utc': invocation_response.req_ts_utc.isoformat(),
                    'resp_ts_utc': invocation_response.resp_ts_utc.isoformat(),
                    'ok': invocation_response.ok,
                    'exception': invocation_response.exception,
                    'cid': invocation_response.cid,
                }

                # .. add the received response to the list of what we have so far ..
                entry.target_responses.append(dict_payload)

                # .. invoke any potential on-target callbacks ..
                if entry.on_target_list:

                    # Updates the dictionary in-place
                    dict_payload['phase'] = 'on-target'

                    for on_target_item in entry.on_target_list: # type: str
                        invoked_service.invoke_async(
                            on_target_item, dict_payload, channel=self.on_target_channel, cid=invoked_service.cid)

                # .. check if this was the last service that we were waiting for ..
                if entry.remaining_targets == 0:

                    # .. if so, run the final callback services if it is required in our case ..
                    if self.needs_on_final:
                        if entry.on_final_list:

                            # This message is what all the on-final callbacks
                            # receive in their self.request.payload attribute.
                            on_final_message = {
                                'phase': 'on-final',
                                'source': invocation_response.source,
                                'req_ts_utc': entry.req_ts_utc,
                                'on_target': entry.on_target_list,
                                'on_final': entry.on_final_list,
                                'data': entry.target_responses,
                            }

                            for on_final_item in entry.on_final_list: # type: str
                                invoked_service.invoke_async(
                                    on_final_item, on_final_message,
                                    channel=self.on_final_channel, cid=invoked_service.cid)

                    # .. now, clean up by deleting the current entry from cache.
                    # Note that we ise None in an unlikely it is already deleted,
                    # although this should not happen because we are the only piece of code holding this lock.
                    self.cache.pop(invoked_service.cid, None)

# ################################################################################################################################
# ################################################################################################################################

class ParallelExec(ParallelBase):
    call_channel = CHANNEL.PARALLEL_EXEC_CALL
    on_target_channel = CHANNEL.PARALLEL_EXEC_ON_TARGET

    def invoke(self, targets, on_target, cid=None):
        return super().invoke(targets, None, on_target, cid)

# ################################################################################################################################
# ################################################################################################################################

class FanOut(ParallelBase):
    call_channel = CHANNEL.FANOUT_CALL
    on_target_channel = CHANNEL.FANOUT_ON_TARGET
    on_final_channel = CHANNEL.FANOUT_ON_FINAL
    needs_on_final = True

# ################################################################################################################################
# ################################################################################################################################
