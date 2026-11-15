# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import unittest
from uuid import uuid4
from zipfile import ZipFile

# Zato
from zato.common.test.conftest_base_multi_cpu import invoke_on_slot, ModuleCtx as MultiCPUCtx, MultiCPUTestConfig, \
     wait_for_every_slot

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long every slot has to observe a deployed version, in seconds
    Deploy_Deadline = 60.0

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

    Rule_Name = 'Versioned'

    Rules_Reader_Template = '''# -*- coding: utf-8 -*-

# Zato
from zato.server.service import Service

class RulesReader(Service):
    name = {service_name!r}

    def handle(self) -> 'None':
        result = self.rules.match_first({{'kind': 'versioned'}}, {rule_full_name!r})
        self.response.payload = {{'version': result.then['version']}}
'''

    Rules_Template = '''rule
    {rule_name}
docs
    The version of the ruleset deployed through the pickup directory.
when
    kind is 'versioned'
then
    version = '{version}'
'''

# ################################################################################################################################
# ################################################################################################################################

def _publish(directory:'str', file_name:'str', staging_path:'str') -> 'None':
    """ Moves a complete file into the pickup directory, so the listener never reads a partially written one.
    """
    path = os.path.join(MultiCPUTestConfig.server_directory, directory, file_name)
    os.replace(staging_path, path)

# ################################################################################################################################

def _staging_path(file_name:'str') -> 'str':
    out = os.path.join(MultiCPUTestConfig.server_directory, f'staging-{file_name}')
    return out

# ################################################################################################################################

def _write(directory:'str', file_name:'str', content:'str') -> 'None':
    staging_path = _staging_path(file_name)

    with open(staging_path, 'w') as output_file:
        _ = output_file.write(content)

    _publish(directory, file_name, staging_path)

# ################################################################################################################################

def _write_archive(directory:'str', file_name:'str', member_name:'str', content:'str') -> 'None':
    staging_path = _staging_path(file_name)

    with ZipFile(staging_path, 'w') as archive:
        archive.writestr(member_name, content)

    _publish(directory, file_name, staging_path)

# ################################################################################################################################
# ################################################################################################################################

class TestFileKindsAcrossWorkers(unittest.TestCase):
    """ Each kind of file deployed through the pickup directory, and each change of it, is in effect in every worker.
    """

    def _wait_for_version(self, service_name:'str', version:'str') -> 'None':
        """ Waits until the service answers with the given version through every slot.
        """
        def _is_at_version(slot:'int') -> 'bool':
            status, body = invoke_on_slot(slot, service_name, {})

            if status != MultiCPUCtx.Status_OK:
                return False

            out = json.loads(body)['version'] == version
            return out

        wait_for_every_slot(_is_at_version, f'version {version} of {service_name}', ModuleCtx.Deploy_Deadline)

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

    def test_archive_change(self) -> 'None':
        """ An archive with a service module and its changed version.
        """
        suffix = uuid4().hex[:12]
        service_name = f'test.multi-cpu.archived.{suffix}'
        member_name = f'test_multi_cpu_archived_{suffix}.py'
        file_name = f'test_multi_cpu_archive_{suffix}.zip'

        for version in ('first', 'second'):
            source = ModuleCtx.Service_Template.format(service_name=service_name, version=version)
            _write_archive(ModuleCtx.Services_Dir, file_name, member_name, source)
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

    def test_rules_change(self) -> 'None':
        """ A .zrules file, evaluated by a service, and its changed version.
        """
        suffix = uuid4().hex[:12]
        ruleset_name = f'test_multi_cpu_rules_{suffix}'
        rule_full_name = f'{ruleset_name}_{ModuleCtx.Rule_Name}'
        service_name = f'test.multi-cpu.rules-reader.{suffix}'

        rules = ModuleCtx.Rules_Template.format(rule_name=ModuleCtx.Rule_Name, version='first')
        _write(ModuleCtx.User_Conf_Dir, f'{ruleset_name}.zrules', rules)

        reader = ModuleCtx.Rules_Reader_Template.format(service_name=service_name, rule_full_name=rule_full_name)
        _write(ModuleCtx.Services_Dir, f'test_multi_cpu_rules_reader_{suffix}.py', reader)

        self._wait_for_version(service_name, 'first')

        rules = ModuleCtx.Rules_Template.format(rule_name=ModuleCtx.Rule_Name, version='second')
        _write(ModuleCtx.User_Conf_Dir, f'{ruleset_name}.zrules', rules)

        self._wait_for_version(service_name, 'second')

# ################################################################################################################################
# ################################################################################################################################
