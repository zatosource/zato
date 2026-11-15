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

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_hot_deploy.file_kinds')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long every slot has to observe a deployed version, in seconds
    Deploy_Deadline = 60.0
    Poll_Interval = 0.5

    Services_Dir  = os.path.join('pickup', 'incoming', 'services')
    User_Conf_Dir = os.path.join('pickup', 'incoming', 'user-conf')

    Service_Template = '''# -*- coding: utf-8 -*-

# Zato
from zato.server.service import Service

class Versioned(Service):
    name = {service_name!r}

    def handle(self) -> 'None':
        self.response.payload = {{'version': {version!r}}}
'''

    Helper_Template = '''# -*- coding: utf-8 -*-

VERSION = {version!r}
'''

    Importer_Template = '''# -*- coding: utf-8 -*-

# Zato
from zato.server.service import Service

class Importer(Service):
    name = {service_name!r}

    def handle(self) -> 'None':

        # The helper is imported at each invocation, so the module that the worker holds at that moment answers
        from {helper_module} import VERSION

        self.response.payload = {{'version': VERSION}}
'''

    Config_Reader_Template = '''# -*- coding: utf-8 -*-

# Zato
from zato.server.service import Service

class ConfigReader(Service):
    name = {service_name!r}

    def handle(self) -> 'None':
        self.response.payload = {{'version': self.user_config[{config_name!r}]['main']['version']}}
'''

    Config_Template = '''[main]
version={version}
'''

# ################################################################################################################################
# ################################################################################################################################

def _write(directory:'str', file_name:'str', content:'str') -> 'None':
    path = os.path.join(MultiCPUTestConfig.server_directory, directory, file_name)

    with open(path, 'w') as output_file:
        _ = output_file.write(content)

# ################################################################################################################################
# ################################################################################################################################

class TestFileKindsAcrossWorkers(unittest.TestCase):
    """ Each kind of file deployed through the pickup directory, and each change of it, is in effect in every worker.
    """

    def _wait_for_version(self, service_name:'str', version:'str') -> 'None':
        """ Waits until the service answers with the given version through every slot.
        """
        pending:'intlist' = list(range(MultiCPUTestConfig.worker_count))
        deadline = monotonic() + ModuleCtx.Deploy_Deadline

        while pending:
            still_pending:'intlist' = []

            for slot in pending:
                status, body = invoke_on_slot(slot, service_name, {})

                if status != MultiCPUCtx.Status_OK:
                    still_pending.append(slot)
                    continue

                if json.loads(body)['version'] != version:
                    still_pending.append(slot)

            pending = still_pending

            if pending:
                if monotonic() > deadline:
                    self.fail(f'{service_name} not at version {version} in slots {pending} after {ModuleCtx.Deploy_Deadline}s')
                sleep(ModuleCtx.Poll_Interval)

        logger.info('%s at version %s in every slot', service_name, version)

# ################################################################################################################################

    def test_service_module_change(self) -> 'None':
        """ A service module and its changed version.
        """
        suffix = uuid4().hex[:12]
        service_name = f'test.multi-cpu.versioned.{suffix}'
        file_name = f'test_multi_cpu_versioned_{suffix}.py'

        for version in ('first', 'second'):
            _write(ModuleCtx.Services_Dir, file_name, ModuleCtx.Service_Template.format(service_name=service_name, version=version))
            self._wait_for_version(service_name, version)

# ################################################################################################################################

    def test_helper_module_change(self) -> 'None':
        """ A helper module, a service that imports it, and a changed version of the helper.
        """
        suffix = uuid4().hex[:12]
        helper_module = f'test_multi_cpu_helper_{suffix}'
        service_name = f'test.multi-cpu.importer.{suffix}'

        _write(ModuleCtx.Services_Dir, f'{helper_module}.py', ModuleCtx.Helper_Template.format(version='first'))

        importer = ModuleCtx.Importer_Template.format(service_name=service_name, helper_module=helper_module)
        _write(ModuleCtx.Services_Dir, f'test_multi_cpu_importer_{suffix}.py', importer)

        self._wait_for_version(service_name, 'first')

        _write(ModuleCtx.Services_Dir, f'{helper_module}.py', ModuleCtx.Helper_Template.format(version='second'))
        self._wait_for_version(service_name, 'second')

# ################################################################################################################################

    def test_user_config_change(self) -> 'None':
        """ A user configuration file, read by a service, and its changed version.
        """
        suffix = uuid4().hex[:12]
        config_name = f'test_multi_cpu_config_{suffix}'
        service_name = f'test.multi-cpu.config-reader.{suffix}'

        _write(ModuleCtx.User_Conf_Dir, f'{config_name}.ini', ModuleCtx.Config_Template.format(version='first'))

        reader = ModuleCtx.Config_Reader_Template.format(service_name=service_name, config_name=config_name)
        _write(ModuleCtx.Services_Dir, f'test_multi_cpu_config_reader_{suffix}.py', reader)

        self._wait_for_version(service_name, 'first')

        _write(ModuleCtx.User_Conf_Dir, f'{config_name}.ini', ModuleCtx.Config_Template.format(version='second'))
        self._wait_for_version(service_name, 'second')

# ################################################################################################################################
# ################################################################################################################################
