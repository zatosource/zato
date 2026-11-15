# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import unittest
from tempfile import mkdtemp
from time import monotonic, sleep

# Zato
from zato.common.test.conftest_base_multi_cpu import get_json, get_parent_pid, MultiCPUTestConfig, new_connection, \
     WorkerControl

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import list_
    floatlist = list_[float]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_faults.crash_loop')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Slot_Path = '/test/multi-cpu/worker-slot'

    # How many consecutive respawns of the slot the test observes
    Respawn_Count = 4

    # How long the test waits for those respawns, in seconds
    Loop_Deadline = 180.0

    Poll_Interval = 0.25

    Module_Name = 'test_multi_cpu_crash_loop.py'

    # The module that terminates the worker of one slot while the marker file exists, each time the worker imports it
    Module_Template = '''# -*- coding: utf-8 -*-

# stdlib
import os

# Zato
from zato.common.worker_slot import get_worker_slot
from zato.server.service import Service

if get_worker_slot() == {slot} and os.path.exists({marker_path!r}):
    os._exit(1)

class CrashLoop(Service):
    name = 'test.multi-cpu.crash-loop'

    def handle(self) -> 'None':
        self.response.payload = {{'slot': get_worker_slot()}}
'''

# ################################################################################################################################
# ################################################################################################################################

class TestCrashLoop(unittest.TestCase):
    """ A slot whose worker terminates on each start is respawned with a growing delay, while the other slots
    keep serving and the arbiter stays alive.
    """

    def test_crash_loop(self) -> 'None':

        control = WorkerControl(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)
        rows = control.wait_for_all_ready()

        target_slot = MultiCPUTestConfig.worker_count - 1
        arbiter_pid = get_parent_pid(rows[0]['pid'])

        target = control.get_slot(target_slot)
        generation = target['generation']

        # .. the marker file keeps the loop going for as long as it exists ..
        marker_path = os.path.join(mkdtemp(prefix='zato-multi-cpu-crash-loop-'), 'marker')

        with open(marker_path, 'w') as marker_file:
            _ = marker_file.write('')

        source = ModuleCtx.Module_Template.format(slot=target_slot, marker_path=marker_path)
        pickup_path = os.path.join(MultiCPUTestConfig.server_directory, 'pickup', 'incoming', 'services', ModuleCtx.Module_Name)

        with open(pickup_path, 'w') as module_file:
            _ = module_file.write(source)

        # .. observe the respawns of the slot, sending requests to the other slots in between ..
        respawn_times:'floatlist' = []
        deadline = monotonic() + ModuleCtx.Loop_Deadline

        while len(respawn_times) < ModuleCtx.Respawn_Count and monotonic() < deadline:

            row = control.get_slot(target_slot)

            if row['generation'] > generation:
                generation = row['generation']
                respawn_times.append(monotonic())
                logger.info('Slot %s respawned -> generation %s', target_slot, generation)

            connection = new_connection()
            _ = get_json(connection, ModuleCtx.Slot_Path)
            connection.close()

            sleep(ModuleCtx.Poll_Interval)

        self.assertEqual(len(respawn_times), ModuleCtx.Respawn_Count)

        # .. the delay between respawns grows ..
        first_interval = respawn_times[1] - respawn_times[0]
        last_interval = respawn_times[-1] - respawn_times[-2]

        logger.info('Respawn intervals: first %.2fs, last %.2fs', first_interval, last_interval)
        self.assertGreater(last_interval, first_interval)

        # .. the arbiter stays alive ..
        self.assertTrue(os.path.exists(f'/proc/{arbiter_pid}'))

        # .. and without the marker the slot starts again.
        os.remove(marker_path)

        restored = control.wait_for_respawn(target_slot, generation)
        self.assertEqual(get_parent_pid(restored['pid']), arbiter_pid)

# ################################################################################################################################
# ################################################################################################################################
