# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import unittest
from uuid import uuid4

# Zato
from zato.common.test.conftest_base_multi_cpu import basic_auth_header, enmasse_import, invoke_on_slot, ModuleCtx as MultiCPUCtx, \
     MultiCPUTestConfig, request_on_slot, wait_for_every_slot

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long every slot has to apply an imported change, in seconds
    Change_Deadline = 90.0

    Status_Unauthorized = 401
    Status_Not_Found = 404

    Sec_Name = 'test.multi-cpu.config.sec'

    Moved_Name = 'test.multi-cpu.config.moved'
    Moved_Path_Before = '/test/multi-cpu/config/before'
    Moved_Path_After = '/test/multi-cpu/config/after'

    Secured_Path = '/test/multi-cpu/config/secured'

    Outconn_Name = 'test.multi-cpu.config.out'
    Outgoing_Invoke_Service = 'test.multi-cpu.outgoing-invoke'
    Target_First = 'test.multi-cpu.config.target-first'
    Target_Second = 'test.multi-cpu.config.target-second'
    Target_Second_Path = '/test/multi-cpu/config/target-second'

# ################################################################################################################################
# ################################################################################################################################

def _status_of(slot:'int', path:'str', password:'str'='') -> 'int':
    """ The status of a GET request to the path through the worker of a slot, with the credentials of the changed
    security definition when a password is given.
    """
    headers:'anydict' = {}

    if password:
        headers['Authorization'] = basic_auth_header(ModuleCtx.Sec_Name, password)

    status, _ = request_on_slot(slot, 'GET', path, '', headers)
    return status

# ################################################################################################################################

def _outgoing_target(slot:'int') -> 'str':
    """ The name of the channel that the outgoing connection reaches when the worker of a slot invokes it.
    """
    status, body = invoke_on_slot(slot, ModuleCtx.Outgoing_Invoke_Service, {'outconn_name': ModuleCtx.Outconn_Name})

    if status != MultiCPUCtx.Status_OK:
        raise Exception(f'Status {status} from {ModuleCtx.Outgoing_Invoke_Service} in slot {slot} -> {body!r}')

    out = json.loads(body)['response']['channel']
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestConfigPropagation(unittest.TestCase):
    """ A channel, a security definition and an outgoing connection changed through one enmasse import
    are in effect in every worker.
    """

    def test_import_changes_every_worker(self) -> 'None':

        old_password = MultiCPUTestConfig.sec_password
        new_password = uuid4().hex

        # Every slot serves the configuration of the template before the import ..
        for slot in range(MultiCPUTestConfig.worker_count):
            self.assertEqual(_status_of(slot, ModuleCtx.Moved_Path_Before), MultiCPUCtx.Status_OK)
            self.assertEqual(_status_of(slot, ModuleCtx.Secured_Path, old_password), MultiCPUCtx.Status_OK)
            self.assertEqual(_outgoing_target(slot), ModuleCtx.Target_First)

        # .. one import changes all three objects ..
        enmasse_import({
            'security': [{
                'name': ModuleCtx.Sec_Name,
                'type': 'basic_auth',
                'username': ModuleCtx.Sec_Name,
                'password': new_password,
            }],
            'channel_rest': [{
                'name': ModuleCtx.Moved_Name,
                'service': MultiCPUCtx.Worker_Slot_Service,
                'url_path': ModuleCtx.Moved_Path_After,
                'data_format': 'json',
            }],
            'outgoing_rest': [{
                'name': ModuleCtx.Outconn_Name,
                'host': MultiCPUTestConfig.base_url,
                'url_path': ModuleCtx.Target_Second_Path,
                'data_format': 'json',
                'timeout': 30,
            }],
        })

        # .. the channel answers under its new path only ..
        def _is_moved(slot:'int') -> 'bool':
            is_after = _status_of(slot, ModuleCtx.Moved_Path_After) == MultiCPUCtx.Status_OK
            is_before_gone = _status_of(slot, ModuleCtx.Moved_Path_Before) == ModuleCtx.Status_Not_Found
            out = is_after and is_before_gone
            return out

        wait_for_every_slot(_is_moved, 'the new path of the channel', ModuleCtx.Change_Deadline)

        # .. the definition accepts the new password only ..
        def _is_secured(slot:'int') -> 'bool':
            is_new_accepted = _status_of(slot, ModuleCtx.Secured_Path, new_password) == MultiCPUCtx.Status_OK
            is_old_rejected = _status_of(slot, ModuleCtx.Secured_Path, old_password) == ModuleCtx.Status_Unauthorized
            out = is_new_accepted and is_old_rejected
            return out

        wait_for_every_slot(_is_secured, 'the new password of the definition', ModuleCtx.Change_Deadline)

        # .. and the outgoing connection reaches its new target.
        def _is_retargeted(slot:'int') -> 'bool':
            out = _outgoing_target(slot) == ModuleCtx.Target_Second
            return out

        wait_for_every_slot(_is_retargeted, 'the new path of the outgoing connection', ModuleCtx.Change_Deadline)

# ################################################################################################################################
# ################################################################################################################################
