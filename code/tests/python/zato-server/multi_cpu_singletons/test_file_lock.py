# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import unittest
from threading import Thread
from uuid import uuid4

# Zato
from zato.common.test.conftest_base_multi_cpu import invoke_on_slot, ModuleCtx as MultiCPUCtx, MultiCPUTestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Service = 'test.multi-cpu.lock-hold'

    # How many invocations hold the lock at the same time through each slot, and how many holds each invocation makes
    Invocations_Per_Slot = 2
    Hold_Count = 40

    # How long each hold lasts, in seconds, during which the worker runs its other greenlets
    Hold_Time = 0.002

    # How long a hold may last and how long an acquisition may wait, in seconds
    TTL = 60
    Block = 60

# ################################################################################################################################
# ################################################################################################################################

class TestFileLockAcrossWorkers(unittest.TestCase):
    """ One lock name, acquired at the same time through every worker, is held by one greenlet of one worker at a time.
    """

    def test_holds_never_overlap(self) -> 'None':

        payload:'anydict' = {
            'lock_name': f'test.multi-cpu.lock.{uuid4().hex}',
            'hold_count': ModuleCtx.Hold_Count,
            'hold_time': ModuleCtx.Hold_Time,
            'ttl': ModuleCtx.TTL,
            'block': ModuleCtx.Block,
        }

        responses:'anylist' = []

        def _invoke(slot:'int') -> 'None':
            responses.append(invoke_on_slot(slot, ModuleCtx.Service, payload))

        threads:'list[Thread]' = []

        for slot in range(MultiCPUTestConfig.worker_count):
            for _ in range(ModuleCtx.Invocations_Per_Slot):
                threads.append(Thread(target=_invoke, args=(slot,)))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        holds:'anylist' = []

        for status, body in responses:
            self.assertEqual(status, MultiCPUCtx.Status_OK, body)
            holds.extend(json.loads(body)['holds'])

        # Every hold of every invocation was made, each slot made its own share ..
        expected_count = MultiCPUTestConfig.worker_count * ModuleCtx.Invocations_Per_Slot * ModuleCtx.Hold_Count
        self.assertEqual(len(holds), expected_count)
        self.assertEqual({slot for _, _, slot in holds}, set(range(MultiCPUTestConfig.worker_count)))

        # .. and no hold began before the previous one ended.
        holds.sort()

        for previous, current in zip(holds, holds[1:]):
            self.assertGreaterEqual(current[0], previous[1], f'{current} began during {previous}')

# ################################################################################################################################
# ################################################################################################################################
