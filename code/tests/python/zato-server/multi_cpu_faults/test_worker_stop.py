# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import unittest
from time import monotonic, sleep

# Zato
from zato.common.test.conftest_base_multi_cpu import get_json, ModuleCtx as MultiCPUCtx, MultiCPUTestConfig, \
     new_connection, WorkerControl
from zato.server.arbiter_config import ModuleCtx as ArbiterCtx
from zato.server.control.hub import EntryStatus, ModuleCtx as HubCtx

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_faults.worker_stop')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Slot_Path = '/test/multi-cpu/worker-slot'

    # How long a worker stays stopped in the test below the heartbeat threshold, in seconds
    Short_Stop = 5.0

    # How long the test waits for a resumed worker to serve a request, in seconds
    Serve_Deadline = 30.0

    # How much longer than the timeout of a fan-out query its answer may take, in seconds
    Answer_Margin = 2.0

# ################################################################################################################################
# ################################################################################################################################

class TestWorkerStop(unittest.TestCase):
    """ A worker stopped with SIGSTOP beyond the heartbeat threshold is replaced, and one stopped below it continues.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.control = WorkerControl(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)

# ################################################################################################################################

    def test_stop_beyond_heartbeat_threshold(self) -> 'None':
        """ The arbiter terminates a worker whose heartbeat stopped and respawns its slot.
        """
        slot = 0

        _ = self.control.wait_for_all_ready()
        stopped = self.control.stop(slot)
        started_at = monotonic()

        respawned = self.control.wait_for_respawn(slot, stopped['generation'])
        elapsed = monotonic() - started_at

        logger.info('Slot %s respawned after %.1fs -> %s', slot, elapsed, respawned)

        self.assertGreaterEqual(elapsed, ArbiterCtx.Heartbeat_Threshold - ArbiterCtx.Heartbeat_Interval)
        self.assertNotEqual(respawned['pid'], stopped['pid'])
        self.assertFalse(os.path.exists(f'/proc/{stopped["pid"]}'))

# ################################################################################################################################

    def test_stop_below_heartbeat_threshold(self) -> 'None':
        """ A worker resumed before the threshold keeps its generation and serves requests again.
        """
        slot = MultiCPUTestConfig.worker_count - 1

        _ = self.control.wait_for_all_ready()
        stopped = self.control.stop(slot)

        sleep(ModuleCtx.Short_Stop)
        _ = self.control.resume(slot)

        # .. the slot keeps its worker ..
        current = self.control.get_slot(slot)

        self.assertEqual(current['pid'], stopped['pid'])
        self.assertEqual(current['generation'], stopped['generation'])

        # .. and that worker serves requests again.
        deadline = monotonic() + ModuleCtx.Serve_Deadline

        while monotonic() < deadline:
            connection = new_connection()
            response = get_json(connection, ModuleCtx.Slot_Path)
            connection.close()

            if response['slot'] == slot:
                self.assertEqual(response['pid'], stopped['pid'])
                return

        self.fail(f'Slot {slot} served no request within {ModuleCtx.Serve_Deadline}s after it was resumed')

# ################################################################################################################################

    def test_fan_out_with_a_stopped_worker(self) -> 'None':
        """ The worker list read while one worker is stopped reports a timeout for that slot and answers within
        the deadline of the query.
        """
        slot = MultiCPUTestConfig.worker_count - 1

        _ = self.control.wait_for_all_ready()
        stopped = self.control.stop(slot)

        try:
            deadline = monotonic() + ModuleCtx.Serve_Deadline

            while monotonic() < deadline:

                # .. a request that the kernel assigned to the stopped worker is not answered, the next one is sent ..
                started_at = monotonic()

                try:
                    rows = self.control.get_slots()
                except OSError as e:
                    logger.info('Request reached the stopped worker -> %s', e)
                    continue

                elapsed = monotonic() - started_at

                for row in rows:
                    if row['slot'] == slot:
                        self.assertEqual(row['response'], EntryStatus.Timeout)
                        self.assertEqual(row['pid'], stopped['pid'])
                    else:
                        self.assertEqual(row['response'], EntryStatus.OK)

                self.assertLess(elapsed, HubCtx.Query_Timeout + ModuleCtx.Answer_Margin)
                return

            self.fail(f'No worker list read within {ModuleCtx.Serve_Deadline}s')

        finally:
            _ = self.control.resume(slot)

# ################################################################################################################################

    def test_state_after_resume(self) -> 'None':
        """ A resumed worker is reported ready, with a heartbeat younger than the threshold.
        """
        rows = self.control.wait_for_all_ready()

        for row in rows:
            self.assertEqual(row['state'], MultiCPUCtx.State_Ready)
            self.assertLess(row['heartbeat_age_ms'], ArbiterCtx.Heartbeat_Threshold * ArbiterCtx.Milliseconds_Per_Second)

# ################################################################################################################################
# ################################################################################################################################
