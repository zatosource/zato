# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import unittest
from random import choice
from threading import Lock, Thread
from time import monotonic, sleep, time
from uuid import uuid4

# Zato
from zato.common.test.conftest_base_multi_cpu import invoke_on_slot, ModuleCtx as MultiCPUCtx, MultiCPUTestConfig, \
     request_on_slot
from zato.common.test.config_multi_cpu_cache import CacheConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_cache.response_cache_load')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How many keys the clients request, how many clients run at once and for how long, in seconds
    Key_Count = 8
    Client_Count = 32
    Run_Duration = 40.0

    # How often the channel is invalidated during the run, in seconds
    Invalidation_Interval = 10.0

# ################################################################################################################################
# ################################################################################################################################

class Response:
    """ One response that a client received, with the time its request was sent.
    """
    key: 'str'
    invocation_id: 'str'
    sent_at: 'float'

# ################################################################################################################################
# ################################################################################################################################

def _read_invocations() -> 'anydict':
    """ The key and the start time of every invocation of the cached service, by the ID of the invocation.
    """
    out:'anydict' = {}

    with open(os.environ[CacheConfig.Invocation_Log_Env]) as invocation_log:
        for line in invocation_log.read().splitlines():
            key, invocation_id, started_at = line.split()
            out[invocation_id] = (key, float(started_at))

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestResponseCacheUnderLoad(unittest.TestCase):
    """ Concurrent clients spread over every worker, with invalidations during the run, invoke the service of each key
    a bounded number of times and never receive a response from before an invalidation.
    """

    def test_load_with_invalidations(self) -> 'None':

        run_id = uuid4().hex[:8]
        keys:'strlist' = []

        for index in range(ModuleCtx.Key_Count):
            keys.append(f'{run_id}-{index}')

        responses:'anylist' = []
        errors:'anylist' = []
        lock = Lock()
        run_end = monotonic() + ModuleCtx.Run_Duration

        def _client(client_index:'int') -> 'None':
            slot = client_index % MultiCPUTestConfig.worker_count

            while monotonic() < run_end:
                key = choice(keys)
                sent_at = time()
                status, body = request_on_slot(slot, 'GET', f'{CacheConfig.First_Channel_Path}?key={key}', '', {})

                with lock:
                    if status != MultiCPUCtx.Status_OK:
                        errors.append((status, body))
                        continue

                    response = Response()
                    response.key = key
                    response.invocation_id = json.loads(body)['invocation_id']
                    response.sent_at = sent_at
                    responses.append(response)

        threads:'anylist' = []

        for client_index in range(ModuleCtx.Client_Count):
            thread = Thread(target=_client, args=(client_index,), daemon=True)
            threads.append(thread)
            thread.start()

        # The channel is invalidated periodically through each slot in turn while the clients run ..
        invalidations:'anylist' = []
        invalidation_slot = 0

        while monotonic() + ModuleCtx.Invalidation_Interval < run_end:
            sleep(ModuleCtx.Invalidation_Interval)

            started_at = time()
            status, body = invoke_on_slot(invalidation_slot, CacheConfig.Invalidate_Service,
                {'channel_name': CacheConfig.First_Channel_Name})
            self.assertEqual(status, MultiCPUCtx.Status_OK, body)

            invalidations.append((started_at, time()))
            invalidation_slot = (invalidation_slot + 1) % MultiCPUTestConfig.worker_count

        for thread in threads:
            thread.join()

        self.assertEqual(errors, [])

        invocations = _read_invocations()
        logger.info('Responses %s, invocations %s, invalidations %s', len(responses), len(invocations), len(invalidations))

        # .. no request sent after an invalidation completed receives the response of an invocation
        # that started before the invalidation did ..
        for response in responses:
            _, invocation_started_at = invocations[response.invocation_id]

            for invalidation_start, invalidation_end in invalidations:
                is_stale = invocation_started_at < invalidation_start and response.sent_at > invalidation_end
                self.assertFalse(is_stale, f'Key {response.key} served invocation {response.invocation_id} after an invalidation')

        # .. and each key is invoked at least once and at most twice for each invalidation besides its first invocation,
        # which allows for an invocation in progress during an invalidation whose response is discarded.
        upper_bound = 1 + 2 * len(invalidations)

        for key in keys:
            count = 0

            for invocation_key, _ in invocations.values():
                if invocation_key == key:
                    count += 1

            self.assertGreaterEqual(count, 1, f'Key {key} never invoked')
            self.assertLessEqual(count, upper_bound, f'Key {key} invoked {count} times')

# ################################################################################################################################
# ################################################################################################################################
