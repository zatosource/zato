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

# Zato
from zato.common.test.conftest_base_multi_cpu import get_staging_path, invoke_on_slot, ModuleCtx as MultiCPUCtx, \
     MultiCPUTestConfig, wait_for_every_slot

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long every slot has to observe a change, in seconds
    Change_Deadline = 60.0

    # The slot through which each change is made
    Change_Slot = 0

    # The services that Dashboard invokes for each change
    Env_Variables_Save = 'zato.env-variables.save'
    SQL_Get            = 'zato.config-db.sql.get'
    SQL_Save           = 'zato.config-db.sql.save'
    Redis_Get          = 'zato.config-db.redis.get'
    Redis_Save         = 'zato.config-db.redis.save'
    Server_Invoker     = 'zato.server.invoker'
    IDE_Delete_File    = 'zato.service.ide.delete-file'

    # The services that read the state of the worker of a slot
    Env_Read   = 'test.multi-cpu.env-read'
    Log_Level  = 'test.multi-cpu.log-level'
    Redis_DB   = 'test.multi-cpu.redis-db'

    # The SQL database whose configuration is changed and the variable that holds its display name
    SQL_Database          = 'audit-log'
    SQL_Display_Name_Env  = 'Zato_Audit_Log_DB_Display_Name'

    # The number of databases that a Redis server provides by default
    Redis_DB_Count = 16

    Services_Dir = os.path.join('pickup', 'incoming', 'services')

    Service_Template = '''# -*- coding: utf-8 -*-

# Zato
from zato.server.service import Service

class Deployed(Service):
    name = {service_name!r}

    def handle(self) -> 'None':
        self.response.payload = {{'is_deployed': True}}
'''

# ################################################################################################################################
# ################################################################################################################################

def _invoke(slot:'int', service_name:'str', payload:'anydict') -> 'any_':
    """ Invokes a service through the worker of a slot and returns its response, which must be a success.
    """
    status, body = invoke_on_slot(slot, service_name, payload)

    if status != MultiCPUCtx.Status_OK:
        raise Exception(f'{service_name} returned {status} -> {body}')

    out = json.loads(body)
    return out

# ################################################################################################################################

def _wait_for_value(service_name:'str', payload:'anydict', key:'str', expected:'any_', description:'str') -> 'None':
    """ Waits until the service returns the expected value under the key through every slot.
    """
    def _has_value(slot:'int') -> 'bool':
        out = _invoke(slot, service_name, payload)[key] == expected
        return out

    wait_for_every_slot(_has_value, description, ModuleCtx.Change_Deadline)

# ################################################################################################################################

def _wait_for_status(service_name:'str', is_ok:'bool', description:'str') -> 'None':
    """ Waits until the service answers through every slot with a success if is_ok is True, or without one otherwise.
    """
    def _has_status(slot:'int') -> 'bool':
        status, _ = invoke_on_slot(slot, service_name, {})
        out = (status == MultiCPUCtx.Status_OK) == is_ok
        return out

    wait_for_every_slot(_has_status, description, ModuleCtx.Change_Deadline)

# ################################################################################################################################
# ################################################################################################################################

class TestDashboardChangesAcrossWorkers(unittest.TestCase):
    """ A change made through Dashboard, which one worker serves, is in effect in every worker.
    """

    def test_env_variables_save(self) -> 'None':
        """ An environment variable set through zato.env-variables.save.
        """
        name = f'Zato_Test_Multi_CPU_Dashboard_{uuid4().hex[:12]}'
        value = uuid4().hex

        _ = _invoke(ModuleCtx.Change_Slot, ModuleCtx.Env_Variables_Save, {'variables': f'{name}={value}'})
        _wait_for_value(ModuleCtx.Env_Read, {'name': name}, 'value', value, f'environment variable {name}')

# ################################################################################################################################

    def test_sql_save(self) -> 'None':
        """ A display name of the audit log database set and then removed through zato.config-db.sql.save.
        """
        values = _invoke(ModuleCtx.Change_Slot, ModuleCtx.SQL_Get, {'database': ModuleCtx.SQL_Database})['values']
        payload = {'name': ModuleCtx.SQL_Display_Name_Env}

        # The display name is set ..
        display_name = uuid4().hex
        values['display_name'] = display_name

        _ = _invoke(ModuleCtx.Change_Slot, ModuleCtx.SQL_Save, {'database': ModuleCtx.SQL_Database, 'values': values})
        _wait_for_value(ModuleCtx.Env_Read, payload, 'value', display_name, 'display name set')

        # .. and an empty one removes its variable.
        values['display_name'] = ''

        _ = _invoke(ModuleCtx.Change_Slot, ModuleCtx.SQL_Save, {'database': ModuleCtx.SQL_Database, 'values': values})
        _wait_for_value(ModuleCtx.Env_Read, payload, 'value', None, 'display name removed')

# ################################################################################################################################

    def test_redis_save(self) -> 'None':
        """ A database number of the Redis configuration changed through zato.config-db.redis.save.
        """
        values = _invoke(ModuleCtx.Change_Slot, ModuleCtx.Redis_Get, {})['values']
        original = dict(values)

        db = (values['db'] + 1) % ModuleCtx.Redis_DB_Count
        values['db'] = db

        try:
            _ = _invoke(ModuleCtx.Change_Slot, ModuleCtx.Redis_Save, {'values': values})
            _wait_for_value(ModuleCtx.Redis_DB, {}, 'db', db, f'Redis database {db}')

        finally:
            _ = _invoke(ModuleCtx.Change_Slot, ModuleCtx.Redis_Save, {'values': original})

# ################################################################################################################################

    def test_set_logging(self) -> 'None':
        """ A logger level set through set_logging of zato.server.invoker.
        """
        name = f'zato.test.multi-cpu.dashboard.{uuid4().hex[:12]}'

        _ = _invoke(ModuleCtx.Change_Slot, ModuleCtx.Server_Invoker, {'func_name': 'set_logging', 'text': f'{name}=DEBUG'})
        _wait_for_value(ModuleCtx.Log_Level, {'name': name}, 'level', 'DEBUG', f'level of {name}')

# ################################################################################################################################

    def test_ide_delete_file(self) -> 'None':
        """ A deployed service file deleted through zato.service.ide.delete-file.
        """
        suffix = uuid4().hex[:12]
        service_name = f'test.multi-cpu.dashboard.deployed.{suffix}'
        path = os.path.join(MultiCPUTestConfig.server_directory, ModuleCtx.Services_Dir, f'test_multi_cpu_dashboard_{suffix}.py')

        # The service is deployed through the pickup directory ..
        staging_path = get_staging_path(ModuleCtx.Services_Dir)

        with open(staging_path, 'w') as staging_file:
            _ = staging_file.write(ModuleCtx.Service_Template.format(service_name=service_name))

        os.replace(staging_path, path)

        _wait_for_status(service_name, True, f'{service_name} deployed')

        # .. and its file is deleted.
        _ = _invoke(ModuleCtx.Change_Slot, ModuleCtx.IDE_Delete_File, {'fs_location': path})
        _wait_for_status(service_name, False, f'{service_name} deleted')

# ################################################################################################################################
# ################################################################################################################################
