# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import signal
import unittest
from threading import Thread
from time import monotonic, sleep
from uuid import uuid4

# Zato
from zato.common.test.conftest_base_multi_cpu import enmasse_import, invoke_on_slot, ModuleCtx as MultiCPUCtx, \
     MultiCPUTestConfig, request_on_slot, wait_for_every_slot, WorkerControl

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_config.config_process')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long every slot has to apply a change, in seconds
    Change_Deadline = 90.0

    # How long an import is retried while the config process is respawned, and how long it waits between attempts, in seconds
    Import_Deadline = 90.0
    Import_Retry_Interval = 0.5

    # How many imports change one channel at the same time, for each worker
    Imports_Per_Worker = 2

    Status_Not_Found = 404

    Contended_Name = 'test.multi-cpu.config.contended'
    Contended_Path_Prefix = '/test/multi-cpu/config/contended'

    Respawn_Path_Prefix = '/test/multi-cpu/config/config-respawn'

    Env_Change_Service = 'test.multi-cpu.env-change'
    Env_Read_Service = 'test.multi-cpu.env-read'
    Env_Name_Prefix = 'Zato_Test_Multi_CPU_Config_'

    Http_Soap_Get_Service = 'zato.http-soap.get'

# ################################################################################################################################
# ################################################################################################################################

def _invoke_json(slot:'int', service_name:'str', payload:'anydict') -> 'anydict':
    """ Invokes a service in the worker of a slot and returns its JSON response.
    """
    status, body = invoke_on_slot(slot, service_name, payload)

    if status != MultiCPUCtx.Status_OK:
        raise Exception(f'Status {status} from {service_name} in slot {slot} -> {body!r}')

    out = json.loads(body)
    return out

# ################################################################################################################################

def _is_served(slot:'int', path:'str') -> 'bool':
    status, _ = request_on_slot(slot, 'GET', path, '', {})
    out = status == MultiCPUCtx.Status_OK
    return out

# ################################################################################################################################

def _is_not_found(slot:'int', path:'str') -> 'bool':
    status, _ = request_on_slot(slot, 'GET', path, '', {})
    out = status == ModuleCtx.Status_Not_Found
    return out

# ################################################################################################################################

def _channel_config(name:'str', path:'str') -> 'anydict':
    out = {
        'channel_rest': [{
            'name': name,
            'service': MultiCPUCtx.Worker_Slot_Service,
            'url_path': path,
            'data_format': 'json',
        }],
    }
    return out

# ################################################################################################################################

def _import_until_accepted(config:'anydict') -> 'None':
    """ Imports the configuration, again after each failure, because an invocation forwarded to a config process
    that terminated fails to its caller until the replacement serves it.
    """
    deadline = monotonic() + ModuleCtx.Import_Deadline

    while True:
        try:
            enmasse_import(config)
        except Exception as e:
            if monotonic() > deadline:
                raise
            logger.info('Import not accepted while the config process is respawned -> %s', e)
            sleep(ModuleCtx.Import_Retry_Interval)
        else:
            return

# ################################################################################################################################
# ################################################################################################################################

class TestConfigProcess(unittest.TestCase):
    """ The changes of configuration that the config process commits are in effect in every worker.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.control = WorkerControl(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)

# ################################################################################################################################

    def test_concurrent_changes_leave_the_last_committed_one(self) -> 'None':

        import_count = MultiCPUTestConfig.worker_count * ModuleCtx.Imports_Per_Worker
        paths:'strlist' = [f'{ModuleCtx.Contended_Path_Prefix}/{uuid4().hex[:12]}' for _ in range(import_count)]
        errors:'anylist' = []

        def _import(path:'str') -> 'None':
            try:
                enmasse_import(_channel_config(ModuleCtx.Contended_Name, path))
            except Exception as e:
                errors.append(e)

        # Every import changes the path of one channel at the same time, through whichever worker receives it ..
        threads = [Thread(target=_import, args=(path,)) for path in paths]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        self.assertEqual(errors, [])

        # .. the path that the ODB holds is the one committed last ..
        channel = self.control.client.invoke(ModuleCtx.Http_Soap_Get_Service, {'name': ModuleCtx.Contended_Name})
        committed_path = channel['url_path']
        self.assertIn(committed_path, paths)

        # .. and every worker serves that path and none of the others.
        other_paths = [path for path in paths if path != committed_path]

        def _has_committed_path(slot:'int') -> 'bool':
            if not _is_served(slot, committed_path):
                return False

            for path in other_paths:
                if not _is_not_found(slot, path):
                    return False

            return True

        wait_for_every_slot(_has_committed_path, 'the path committed last', ModuleCtx.Change_Deadline)

# ################################################################################################################################

    def test_change_through_invoke_is_in_effect_when_it_returns(self) -> 'None':

        for slot in range(MultiCPUTestConfig.worker_count):

            variable = ModuleCtx.Env_Name_Prefix + uuid4().hex[:12]
            value = uuid4().hex

            # The worker that invoked the change reads it as soon as the invocation returns ..
            response = _invoke_json(slot, ModuleCtx.Env_Change_Service, {'name': variable, 'value': value})

            self.assertEqual(response['slot'], slot)
            self.assertEqual(response['value'], value)

            # .. and every other worker reads it too.
            def _has_value(serving_slot:'int', variable:'str'=variable, value:'str'=value) -> 'bool':
                read = _invoke_json(serving_slot, ModuleCtx.Env_Read_Service, {'name': variable})
                out = read['value'] == value
                return out

            wait_for_every_slot(_has_value, variable, ModuleCtx.Change_Deadline)

# ################################################################################################################################

    def test_change_during_config_process_respawn(self) -> 'None':

        _ = self.control.wait_for_all_ready()

        path = f'{ModuleCtx.Respawn_Path_Prefix}/{uuid4().hex[:12]}'
        name = f'test.multi-cpu.config.config-respawn.{uuid4().hex[:12]}'

        # The config process is killed, so the import below starts while the server has no config process
        # or has one that is still starting ..
        previous_pid = self.control.get_config_process_pid()
        os.kill(previous_pid, signal.SIGKILL)
        logger.info('Killed the config process %s', previous_pid)

        _import_until_accepted(_channel_config(name, path))

        respawned_pid = self.control.wait_for_config_process(previous_pid)
        logger.info('Config process respawned -> %s', respawned_pid)

        # .. and every worker serves the channel of the import.
        def _serves_path(slot:'int', path:'str'=path) -> 'bool':
            out = _is_served(slot, path)
            return out

        wait_for_every_slot(_serves_path, path, ModuleCtx.Change_Deadline)

        _ = self.control.wait_for_all_ready()

# ################################################################################################################################
# ################################################################################################################################
