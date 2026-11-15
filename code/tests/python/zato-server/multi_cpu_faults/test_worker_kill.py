# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import unittest
from threading import Thread
from time import sleep

# Zato
from zato.common.test.conftest_base_multi_cpu import get_json, MultiCPUTestConfig, new_connection, WorkerControl

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from http.client import HTTPConnection
    from zato.common.typing_ import anydict, anylist, intset

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_faults.worker_kill')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Slot_Path  = '/test/multi-cpu/worker-slot'
    Sleep_Path = '/test/multi-cpu/worker-sleep'

    # How many requests are sent while a slot has no worker
    Gap_Request_Count = 32

    # How many connections each slot receives on average in the test of requests in progress
    Connections_Per_Slot = 4

    # How long after the start of the slow requests the worker is killed, in seconds,
    # which is below the duration of test.multi-cpu.worker-sleep
    Kill_Delay = 1.0

# ################################################################################################################################
# ################################################################################################################################

class _SlowRequest:
    """ One connection whose slot is known, which sends one slow request from a thread of its own.
    """

    def __init__(self, connection:'HTTPConnection', slot:'int') -> 'None':
        self.connection = connection
        self.slot = slot
        self.response:'anydict | None' = None
        self.error:'Exception | None' = None
        self.thread = Thread(target=self.run, daemon=True)

    def run(self) -> 'None':
        try:
            self.response = get_json(self.connection, ModuleCtx.Sleep_Path)
        except Exception as e:
            self.error = e
        finally:
            self.connection.close()

# ################################################################################################################################
# ################################################################################################################################

class TestWorkerKill(unittest.TestCase):
    """ A worker terminated with SIGKILL is respawned, and the workers of the other slots keep serving.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.control = WorkerControl(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)

# ################################################################################################################################

    def test_kill_of_each_idle_slot(self) -> 'None':
        """ SIGKILL of each slot in turn results in a respawn with a new generation, and every request sent
        while the slot has no worker succeeds.
        """
        for slot in range(MultiCPUTestConfig.worker_count):

            _ = self.control.wait_for_all_ready()
            killed = self.control.kill(slot)
            logger.info('Killed slot %s -> %s', slot, killed)

            # .. every request in the gap reaches a worker that is alive ..
            for _ in range(ModuleCtx.Gap_Request_Count):
                connection = new_connection()
                response = get_json(connection, ModuleCtx.Slot_Path)
                connection.close()

                if response['pid'] == killed['pid']:
                    self.fail(f'Slot {slot} served a request after its worker was killed')

            # .. and the slot receives a new worker.
            respawned = self.control.wait_for_respawn(slot, killed['generation'])
            logger.info('Respawned slot %s -> %s', slot, respawned)

            self.assertNotEqual(respawned['pid'], killed['pid'])
            self.assertFalse(os.path.exists(f'/proc/{killed["pid"]}'))

# ################################################################################################################################

    def test_kill_during_requests(self) -> 'None':
        """ Requests in progress on the killed worker fail at the connection level, and requests in progress
        on every other worker complete.
        """
        rows = self.control.wait_for_all_ready()
        target_slot = MultiCPUTestConfig.worker_count - 1

        requests:'anylist' = []
        slots:'intset' = set()

        # .. open connections until every slot holds at least one, each pinned to the worker that accepted it ..
        connection_count = MultiCPUTestConfig.worker_count * ModuleCtx.Connections_Per_Slot

        while len(requests) < connection_count or slots != set(range(MultiCPUTestConfig.worker_count)):
            connection = new_connection()
            response = get_json(connection, ModuleCtx.Slot_Path)
            requests.append(_SlowRequest(connection, response['slot']))
            slots.add(response['slot'])

        # .. start the slow requests, kill the worker of the target slot while they are in progress ..
        for request in requests:
            request.thread.start()

        sleep(ModuleCtx.Kill_Delay)
        killed = self.control.kill(target_slot)

        for request in requests:
            request.thread.join()

        # .. each request on the killed worker failed, and every other request completed in its own worker ..
        for request in requests:
            if request.slot == target_slot:
                self.assertIsNone(request.response)
                self.assertIsNotNone(request.error)
            else:
                self.assertIsNone(request.error, f'Slot {request.slot}')

                if request.response is None:
                    self.fail(f'No response from slot {request.slot}')

                self.assertEqual(request.response['slot'], request.slot)

        # .. and the workers of the other slots are the ones that were there before the kill.
        respawned = self.control.wait_for_respawn(target_slot, killed['generation'])
        self.assertNotEqual(respawned['pid'], killed['pid'])

        for row in rows:
            if row['slot'] != target_slot:
                current = self.control.get_slot(row['slot'])
                self.assertEqual(current['pid'], row['pid'])

# ################################################################################################################################
# ################################################################################################################################
