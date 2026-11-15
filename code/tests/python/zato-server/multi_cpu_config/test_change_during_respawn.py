# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import unittest
from uuid import uuid4

# Zato
from zato.common.test.conftest_base_multi_cpu import enmasse_import, ModuleCtx as MultiCPUCtx, MultiCPUTestConfig, \
     request_on_slot, wait_for_every_slot, WorkerControl

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_config.change_during_respawn')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long every slot has to serve the channel of the import, in seconds
    Change_Deadline = 90.0

    Path_Prefix = '/test/multi-cpu/config/respawn'

# ################################################################################################################################
# ################################################################################################################################

class TestChangeDuringRespawn(unittest.TestCase):
    """ A configuration change imported while the worker of a slot is replaced is in effect in the replacement.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.control = WorkerControl(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)

# ################################################################################################################################

    def test_change_reaches_the_replacement(self) -> 'None':

        for slot in range(MultiCPUTestConfig.worker_count):

            suffix = uuid4().hex[:12]
            path = f'{ModuleCtx.Path_Prefix}/{suffix}'

            _ = self.control.wait_for_all_ready()

            # The worker of the slot is killed, so the import below runs while the slot has no worker
            # or has one that is still starting ..
            killed = self.control.kill(slot)
            logger.info('Killed slot %s -> %s', slot, killed)

            enmasse_import({
                'channel_rest': [{
                    'name': f'test.multi-cpu.config.respawn.{suffix}',
                    'service': MultiCPUCtx.Worker_Slot_Service,
                    'url_path': path,
                    'data_format': 'json',
                }],
            })

            respawned = self.control.wait_for_respawn(slot, killed['generation'])
            logger.info('Respawned slot %s -> %s', slot, respawned)

            # .. and the replacement serves the channel, as does every other slot.
            def _is_served(serving_slot:'int') -> 'bool':
                status, _ = request_on_slot(serving_slot, 'GET', path, '', {})
                out = status == MultiCPUCtx.Status_OK
                return out

            wait_for_every_slot(_is_served, path, ModuleCtx.Change_Deadline)

# ################################################################################################################################
# ################################################################################################################################
