# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import unittest

# Zato
from zato.common.test.conftest_base_multi_cpu import ModuleCtx as MultiCPUCtx, MultiCPUTestConfig, WorkerControl

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intset

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_rest.worker_list')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The heartbeat age above which a ready worker is reported as stale, in milliseconds
    Max_Heartbeat_Age_Ms = 5000

    # How many requests are sent to find the worker of every slot
    Request_Count = 64

# ################################################################################################################################
# ################################################################################################################################

class TestWorkerList(unittest.TestCase):
    """ zato.server.worker.get-list reports every slot of the server, with values that agree with one another.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.control = WorkerControl(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)

# ################################################################################################################################

    def test_every_slot_is_reported_ready(self) -> 'None':
        """ Every slot appears once, its worker is ready, and its heartbeat is recent.
        """
        rows = self.control.wait_for_all_ready()

        slots:'intset' = set()
        pids:'intset' = set()

        for row in rows:
            logger.info('Slot row: %s', row)

            slots.add(row['slot'])
            pids.add(row['pid'])

            self.assertEqual(row['state'], MultiCPUCtx.State_Ready)
            self.assertGreater(row['generation'], 0)
            self.assertLess(row['heartbeat_age_ms'], ModuleCtx.Max_Heartbeat_Age_Ms)

        self.assertEqual(len(rows), MultiCPUTestConfig.worker_count)
        self.assertEqual(slots, set(range(MultiCPUTestConfig.worker_count)))
        self.assertEqual(len(pids), MultiCPUTestConfig.worker_count)

# ################################################################################################################################

    def test_every_reported_pid_serves_its_slot(self) -> 'None':
        """ The process that serves a request for a slot is the process the list reports for that slot.
        """
        rows = self.control.wait_for_all_ready()

        pid_by_slot:'dict[int, int]' = {}

        for row in rows:
            pid_by_slot[row['slot']] = row['pid']

        served:'intset' = set()

        for _ in range(ModuleCtx.Request_Count):
            response = self.control.client.invoke(MultiCPUCtx.Worker_Slot_Service)
            slot = response['slot']
            served.add(slot)

            self.assertEqual(response['pid'], pid_by_slot[slot], f'Slot {slot}')

        self.assertEqual(served, set(pid_by_slot))

# ################################################################################################################################

    def test_subscription_key_counts_are_not_negative(self) -> 'None':
        """ The subscription key count of every slot is a count, and the counts of all slots add up to the same total
        on every read.
        """
        first_total = 0
        second_total = 0

        for row in self.control.wait_for_all_ready():
            self.assertGreaterEqual(row['sub_key_count'], 0)
            first_total += row['sub_key_count']

        for row in self.control.wait_for_all_ready():
            second_total += row['sub_key_count']

        self.assertEqual(first_total, second_total)

# ################################################################################################################################
# ################################################################################################################################
