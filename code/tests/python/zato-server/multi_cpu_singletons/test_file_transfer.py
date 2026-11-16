# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import sqlite3
import unittest
from time import monotonic, sleep
from uuid import uuid4

# Zato
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.audit_log.file_transfer_run import Run_Status_Interrupted
from zato.common.test.conftest_base_multi_cpu import invoke_on_slot, ModuleCtx as MultiCPUCtx, MultiCPUTestConfig, \
     WorkerControl
from zato.common.test.config_multi_cpu_singletons import SingletonsConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, intlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_singletons.file_transfer')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Schedule_Name = 'test.multi-cpu.singletons'
    Directory = '/test/multi-cpu/singletons'
    Job_ID = 1

    # The slot whose worker is killed in the middle of its run
    Killed_Slot = 1

    # How long the runs of every worker have to be written, in seconds
    Deadline = 60.0

    Interrupted_Query = 'select count(*) from event where object_name = ? and status = ?'

# ################################################################################################################################
# ################################################################################################################################

def _count_interrupted(conn_name:'str') -> 'int':
    """ Returns how many runs of the connection the audit database records as interrupted,
    which the test reads without becoming a writer of the database.
    """
    path = os.environ[AuditLogCtx.Env_Name]

    with sqlite3.connect(f'file:{path}?mode=ro', uri=True) as connection:
        out = connection.execute(ModuleCtx.Interrupted_Query, (conn_name, Run_Status_Interrupted)).fetchone()[0]

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestFileTransferRunsAcrossWorkers(unittest.TestCase):
    """ A new run through any worker concludes as interrupted the run of a worker that was killed, once,
    and leaves running the runs of the workers that are live.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.control = WorkerControl(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)

# ################################################################################################################################

    def _close_through(self, slot:'int', payload:'anydict') -> 'intlist':
        status, body = invoke_on_slot(slot, SingletonsConfig.Transfer_Close_Service, payload)
        self.assertEqual(status, MultiCPUCtx.Status_OK, body)

        response = json.loads(body)
        self.assertEqual(response['slot'], slot)

        out = response['running_slots']
        return out

# ################################################################################################################################

    def test_interrupted_run_of_a_killed_worker(self) -> 'None':

        all_slots = list(range(MultiCPUTestConfig.worker_count))

        payload:'anydict' = {
            'conn_name': f'test.multi-cpu.singletons.transfer.{uuid4().hex}',
            'schedule_name': ModuleCtx.Schedule_Name,
            'directory': ModuleCtx.Directory,
            'job_id': ModuleCtx.Job_ID,
        }

        # Each worker opens a run and leaves it running ..
        for slot in all_slots:
            status, body = invoke_on_slot(slot, SingletonsConfig.Transfer_Open_Service, payload)
            self.assertEqual(status, MultiCPUCtx.Status_OK, body)

        # .. the runs of the live workers are left running by a new run through any of them ..
        deadline = monotonic() + ModuleCtx.Deadline

        while (running_slots := self._close_through(0, payload)) != all_slots:

            if monotonic() > deadline:
                raise Exception(f'Runs of slots {running_slots} of {all_slots} found running')

            sleep(MultiCPUCtx.Poll_Interval)

        # .. the worker of one slot is killed in the middle of its run and replaced ..
        _ = self.control.wait_for_all_ready()
        killed = self.control.kill(ModuleCtx.Killed_Slot)
        logger.info('Killed slot %s -> %s', ModuleCtx.Killed_Slot, killed)

        respawned = self.control.wait_for_respawn(ModuleCtx.Killed_Slot, killed['generation'])
        logger.info('Respawned slot %s -> %s', ModuleCtx.Killed_Slot, respawned)

        # .. and a new run through each worker, its replacement included, leaves running the runs of the others only ..
        expected_slots:'intlist' = []

        for slot in all_slots:
            if slot != ModuleCtx.Killed_Slot:
                expected_slots.append(slot)

        for slot in all_slots:
            self.assertEqual(self._close_through(slot, payload), expected_slots)

        # .. having concluded the run of the killed worker once.
        self.assertEqual(_count_interrupted(payload['conn_name']), 1)

# ################################################################################################################################
# ################################################################################################################################
