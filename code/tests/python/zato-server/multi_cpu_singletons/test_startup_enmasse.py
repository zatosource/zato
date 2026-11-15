# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import unittest
from time import sleep

# Zato
from zato.common.test.conftest_base_multi_cpu import count_enmasse_imports, ModuleCtx as MultiCPUCtx, MultiCPUTestConfig, \
     request_on_slot, wait_for_every_slot, WorkerControl
from zato.common.test.config_multi_cpu_singletons import SingletonsConfig

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_singletons.startup_enmasse')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long every slot has to serve the channel of the startup file, in seconds
    Import_Deadline = 90.0

    # How long the log is observed after the import and after the respawn, so that an import repeated
    # by another worker or by the replacement worker is counted as well
    Settle_Period = 10.0

    # The slot whose first worker runs the duties that a server runs once after it starts
    Singleton_Slot = 0

# ################################################################################################################################
# ################################################################################################################################

class TestStartupEnmasse(unittest.TestCase):
    """ The enmasse file of the startup deployment is imported once per server start, whatever the worker count,
    and a respawned worker imports nothing.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.control = WorkerControl(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)

# ################################################################################################################################

    def test_imported_once_and_not_by_a_respawned_worker(self) -> 'None':

        file_name = SingletonsConfig.Startup_File_Name

        # The channel of the startup file is served by every slot ..
        def _is_served(slot:'int') -> 'bool':
            status, _ = request_on_slot(slot, 'GET', SingletonsConfig.Startup_Channel_Path, '', {})
            out = status == MultiCPUCtx.Status_OK
            return out

        wait_for_every_slot(_is_served, SingletonsConfig.Startup_Channel_Path, ModuleCtx.Import_Deadline)

        # .. the file was imported exactly once ..
        sleep(ModuleCtx.Settle_Period)
        self.assertEqual(count_enmasse_imports(file_name), 1)

        # .. the worker that imported it is killed and replaced ..
        _ = self.control.wait_for_all_ready()
        killed = self.control.kill(ModuleCtx.Singleton_Slot)
        logger.info('Killed slot %s -> %s', ModuleCtx.Singleton_Slot, killed)

        respawned = self.control.wait_for_respawn(ModuleCtx.Singleton_Slot, killed['generation'])
        logger.info('Respawned slot %s -> %s', ModuleCtx.Singleton_Slot, respawned)

        # .. and the replacement imports nothing, while the channel is still served by every slot.
        sleep(ModuleCtx.Settle_Period)
        self.assertEqual(count_enmasse_imports(file_name), 1)

        wait_for_every_slot(_is_served, SingletonsConfig.Startup_Channel_Path, ModuleCtx.Import_Deadline)

# ################################################################################################################################
# ################################################################################################################################
