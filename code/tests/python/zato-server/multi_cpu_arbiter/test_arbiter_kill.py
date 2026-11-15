# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import signal
import socket
import unittest
from time import monotonic, sleep

# Zato
from zato.common.test.conftest_base_multi_cpu import get_child_pids, get_parent_pid, MultiCPUTestConfig, WorkerControl

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_arbiter.arbiter_kill')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long every child of a killed arbiter has to terminate, in seconds
    Exit_Deadline = 10.0

    Poll_Interval = 0.1

# ################################################################################################################################
# ################################################################################################################################

class TestArbiterKill(unittest.TestCase):
    """ SIGKILL of the arbiter terminates every process it forked, and the listening port is free afterwards.
    This suite has a server of its own, because the test terminates it.
    """

    def test_arbiter_kill(self) -> 'None':

        control = WorkerControl(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)
        rows = control.wait_for_all_ready()

        # .. the arbiter is the parent of every worker ..
        arbiter_pid = get_parent_pid(rows[0]['pid'])

        for row in rows:
            self.assertEqual(get_parent_pid(row['pid']), arbiter_pid)

        # .. its children include the workers and the processes that are not workers ..
        child_pids = get_child_pids(arbiter_pid)
        logger.info('Arbiter %s, children %s', arbiter_pid, child_pids)

        for row in rows:
            self.assertIn(row['pid'], child_pids)

        os.kill(arbiter_pid, signal.SIGKILL)
        started_at = monotonic()

        # .. every child terminates within the deadline ..
        remaining:'intlist' = list(child_pids)

        while remaining and monotonic() - started_at < ModuleCtx.Exit_Deadline:
            still_running:'intlist' = []

            for pid in remaining:
                if os.path.exists(f'/proc/{pid}'):
                    still_running.append(pid)

            remaining = still_running
            sleep(ModuleCtx.Poll_Interval)

        logger.info('Children terminated after %.2fs, remaining %s', monotonic() - started_at, remaining)
        self.assertEqual(remaining, [])

        # .. and the port can be bound again.
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            listener.bind((MultiCPUTestConfig.host, MultiCPUTestConfig.port))
        finally:
            listener.close()

# ################################################################################################################################
# ################################################################################################################################
