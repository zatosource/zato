# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import unittest
from time import monotonic, sleep
from uuid import uuid4

# Zato
from zato.common.test.conftest_base_multi_cpu import invoke_on_slot, ModuleCtx as MultiCPUCtx, MultiCPUTestConfig
from zato.server.control.envelope import ModuleCtx as EnvelopeCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_hot_deploy.service_deploy')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long every slot has to serve a deployed service, in seconds
    Deploy_Deadline = 60.0
    Poll_Interval = 0.5

    # The module of the deployed service, whose padding makes its source as large as a test requires
    Module_Template = '''# -*- coding: utf-8 -*-

# Zato
from zato.common.worker_slot import get_slot_or_single
from zato.server.service import Service

PADDING = {padding!r}

class Deployed(Service):
    name = {service_name!r}

    def handle(self) -> 'None':
        self.response.payload = {{'slot': get_slot_or_single(), 'marker': {marker!r}}}
'''

# ################################################################################################################################
# ################################################################################################################################

class TestServiceDeployAcrossWorkers(unittest.TestCase):
    """ A service deployed through the pickup directory is invocable through every worker.
    """

    def _deploy_and_wait(self, padding_size:'int') -> 'None':

        suffix = uuid4().hex[:12]
        service_name = f'test.multi-cpu.deployed.{suffix}'
        marker = uuid4().hex

        source = ModuleCtx.Module_Template.format(padding='x' * padding_size, service_name=service_name, marker=marker)
        logger.info('Deploying %s, %s bytes', service_name, len(source))

        file_name = f'test_multi_cpu_deployed_{suffix}.py'
        pickup_path = os.path.join(MultiCPUTestConfig.server_directory, 'pickup', 'incoming', 'services', file_name)

        with open(pickup_path, 'w') as module_file:
            _ = module_file.write(source)

        # .. every slot serves the service with the response of this source ..
        pending:'intlist' = list(range(MultiCPUTestConfig.worker_count))
        deadline = monotonic() + ModuleCtx.Deploy_Deadline

        while pending:
            still_pending:'intlist' = []

            for slot in pending:
                status, body = invoke_on_slot(slot, service_name, {})

                if status != MultiCPUCtx.Status_OK:
                    still_pending.append(slot)
                    continue

                response = json.loads(body)
                self.assertEqual(response['slot'], slot)
                self.assertEqual(response['marker'], marker)

            pending = still_pending

            if pending:
                if monotonic() > deadline:
                    self.fail(f'{service_name} not served by slots {pending} after {ModuleCtx.Deploy_Deadline}s')
                sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

    def test_small_service(self) -> 'None':
        """ A service whose source is sent inline in the control message.
        """
        self._deploy_and_wait(0)

# ################################################################################################################################

    def test_service_above_the_inline_size(self) -> 'None':
        """ A service whose source exceeds the inline size of a control message, which is sent through a file.
        """
        self._deploy_and_wait(EnvelopeCtx.Max_Inline_Body * 2)

# ################################################################################################################################
# ################################################################################################################################
