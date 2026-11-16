# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import unittest
from threading import Thread
from time import monotonic, sleep
from uuid import uuid4

# Zato
from zato.common.test.conftest_base_multi_cpu import get_parent_pid, invoke_on_slot, ModuleCtx as MultiCPUCtx, \
     MultiCPUTestConfig, WorkerControl

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_config.event_flood')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Flood_Service = 'test.multi-cpu.event-flood'
    Watch_Service = 'test.multi-cpu.event-watch'

    Env_Name_Prefix = 'Zato_Test_Multi_CPU_Flood_'

    # How many configuration events the flood consists of
    Event_Count = 10_000

    # How long each worker has to apply every event, which is below the request timeout of the tests, in seconds
    Watch_Timeout = 25.0

    # How long the watch of each worker runs before the flood starts, in seconds
    Watch_Start_Time = 1.0

    # How much the resident memory of the arbiter may exceed its baseline once the flood was applied, in kilobytes,
    # and how long it has to return within that bound, in seconds
    Memory_Tolerance_KB = 8 * 1024
    Memory_Deadline = 30.0

    Status_Field = 'VmRSS:'

# ################################################################################################################################
# ################################################################################################################################

def _get_rss_kb(pid:'int') -> 'int':
    """ Returns the resident memory of a process, in kilobytes.
    """
    with open(f'/proc/{pid}/status') as status_file:
        for line in status_file:
            if line.startswith(ModuleCtx.Status_Field):
                out = int(line.split()[1])
                return out

    raise Exception(f'No {ModuleCtx.Status_Field} in the status of {pid}')

# ################################################################################################################################
# ################################################################################################################################

class TestEventFlood(unittest.TestCase):
    """ A flood of configuration events is applied in order by every worker, and the memory of the arbiter
    returns to its baseline afterwards.
    """

    def test_flood_applied_in_order(self) -> 'None':

        control = WorkerControl(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)
        rows = control.wait_for_all_ready()

        arbiter_pid = get_parent_pid(rows[0]['pid'])
        baseline_kb = _get_rss_kb(arbiter_pid)

        variable = ModuleCtx.Env_Name_Prefix + uuid4().hex[:12]
        last_seq = ModuleCtx.Event_Count - 1

        watch_request = {
            'name': variable,
            'expected': last_seq,
            'timeout': ModuleCtx.Watch_Timeout,
        }

        results:'anylist' = []

        # Each worker watches the variable of the flood ..
        def _watch(slot:'int') -> 'None':
            status, body = invoke_on_slot(slot, ModuleCtx.Watch_Service, watch_request)
            self.assertEqual(status, MultiCPUCtx.Status_OK, body)
            results.append(json.loads(body))

        threads:'anylist' = []

        for slot in range(MultiCPUTestConfig.worker_count):
            threads.append(Thread(target=_watch, args=(slot,)))

        for thread in threads:
            thread.start()

        sleep(ModuleCtx.Watch_Start_Time)

        # .. while the config process relays every event of the flood ..
        flood_started = monotonic()
        response = control.client.invoke(ModuleCtx.Flood_Service, {'name': variable, 'count': ModuleCtx.Event_Count})
        self.assertEqual(response['count'], ModuleCtx.Event_Count)

        for thread in threads:
            thread.join()

        peak_kb = _get_rss_kb(arbiter_pid)
        logger.info('Flood applied in %.2fs, arbiter RSS %s kB before, %s kB after -> %s', monotonic() - flood_started,
            baseline_kb, peak_kb, results)

        # .. and every worker reached the last event without having applied any event before an earlier one.
        self.assertEqual(len(results), MultiCPUTestConfig.worker_count)

        for result in results:
            slot = result['slot']
            self.assertTrue(result['is_in_order'], f'Slot {slot}')
            self.assertEqual(result['last_value'], last_seq, f'Slot {slot}')

        # The memory of the arbiter returns to its baseline.
        deadline = monotonic() + ModuleCtx.Memory_Deadline
        current_kb = _get_rss_kb(arbiter_pid)

        while current_kb > baseline_kb + ModuleCtx.Memory_Tolerance_KB:
            if monotonic() > deadline:
                break

            sleep(MultiCPUCtx.Poll_Interval)
            current_kb = _get_rss_kb(arbiter_pid)

        logger.info('Arbiter RSS %s kB, baseline %s kB', current_kb, baseline_kb)
        self.assertLessEqual(current_kb, baseline_kb + ModuleCtx.Memory_Tolerance_KB)

        _ = control.wait_for_all_ready()

# ################################################################################################################################
# ################################################################################################################################
