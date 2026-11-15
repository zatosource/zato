# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import subprocess
import unittest
from time import sleep
from uuid import uuid4

# PyYAML
import yaml

# Zato
from zato.common.test.conftest_base_multi_cpu import count_enmasse_imports, get_staging_path, ModuleCtx as MultiCPUCtx, MultiCPUTestConfig, request_on_slot, \
     wait_for_every_slot

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_hot_deploy.enmasse')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long every slot has to serve an imported channel, in seconds
    Import_Deadline = 90.0

    # How long the log is observed after an import, so that an import repeated by another worker is counted as well
    Settle_Period = 10.0

    Services_Dir = os.path.join('pickup', 'incoming', 'services')

    Path_Prefix = '/test/multi-cpu/enmasse'

# ################################################################################################################################
# ################################################################################################################################

def _build_config(suffix:'str', path_count:'int') -> 'anydict':
    """ An enmasse configuration with as many channels of test.multi-cpu.worker-slot as requested.
    """
    channels = []

    for index in range(path_count):
        channels.append({
            'name': f'test.multi-cpu.enmasse.{suffix}.{index}',
            'service': MultiCPUCtx.Worker_Slot_Service,
            'url_path': f'{ModuleCtx.Path_Prefix}/{suffix}/{index}',
            'data_format': 'json',
        })

    out = {'channel_rest': channels}
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseAcrossWorkers(unittest.TestCase):
    """ An enmasse configuration is imported once per change, and the change is in effect in every worker.
    """

    def _wait_for_path(self, path:'str') -> 'None':
        """ Waits until the channel of the path serves requests through every slot.
        """
        def _is_served(slot:'int') -> 'bool':
            status, _ = request_on_slot(slot, 'GET', path, '', {})
            out = status == MultiCPUCtx.Status_OK
            return out

        wait_for_every_slot(_is_served, path, ModuleCtx.Import_Deadline)

# ################################################################################################################################

    def test_pickup_import_once_per_change(self) -> 'None':
        """ An enmasse file in the pickup directory and its changed version, each imported exactly once.
        """
        suffix = uuid4().hex[:12]
        file_name = f'enmasse-multi-cpu-{suffix}.yaml'
        path = os.path.join(MultiCPUTestConfig.server_directory, ModuleCtx.Services_Dir, file_name)
        staging_path = get_staging_path(ModuleCtx.Services_Dir)

        for path_count in (1, 2):

            with open(staging_path, 'w') as staging_file:
                _ = staging_file.write(yaml.safe_dump(_build_config(suffix, path_count), sort_keys=False))

            os.replace(staging_path, path)

            self._wait_for_path(f'{ModuleCtx.Path_Prefix}/{suffix}/{path_count - 1}')
            sleep(ModuleCtx.Settle_Period)

            self.assertEqual(count_enmasse_imports(file_name), path_count)

# ################################################################################################################################

    def test_command_line_import(self) -> 'None':
        """ A configuration imported through zato enmasse --import is in effect in every worker.
        """
        suffix = uuid4().hex[:12]
        input_path = os.path.join(MultiCPUTestConfig.server_directory, f'multi-cpu-command-line-{suffix}.yaml')

        with open(input_path, 'w') as input_file:
            _ = input_file.write(yaml.safe_dump(_build_config(suffix, 1), sort_keys=False))

        command = [MultiCPUTestConfig.zato_bin, 'enmasse', MultiCPUTestConfig.server_directory, '--import', '--input', input_path]
        result = subprocess.run(command, capture_output=True, text=True, check=False)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self._wait_for_path(f'{ModuleCtx.Path_Prefix}/{suffix}/0')

# ################################################################################################################################
# ################################################################################################################################
