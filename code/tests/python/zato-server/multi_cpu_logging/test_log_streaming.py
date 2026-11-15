# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import unittest

# Zato
from zato.common.test.conftest_base_multi_cpu import invoke_on_slot, ModuleCtx as MultiCPUCtx, wait_for_every_slot

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Toggle_Service = 'zato.log.streaming.toggle'
    Status_Service = 'zato.log.streaming.status'
    Handler_Service = 'test.multi-cpu.log-streaming-handler'

    # How long every worker has to apply a toggle made through another worker, in seconds
    Deadline = 30.0

# ################################################################################################################################
# ################################################################################################################################

def _invoke(slot:'int', service_name:'str') -> 'anydict':
    payload:'anydict' = {}
    status, body = invoke_on_slot(slot, service_name, payload)

    if status != MultiCPUCtx.Status_OK:
        raise Exception(f'{service_name} returned {status} through slot {slot} -> {body}')

    out = json.loads(body)
    return out

# ################################################################################################################################

def _toggle() -> 'bool':
    out = _invoke(0, ModuleCtx.Toggle_Service)['streaming_enabled']
    return out

# ################################################################################################################################

def _wait_for_streaming(is_enabled:'bool') -> 'None':
    """ Waits until every worker reports the expected state of log streaming and has the streaming handler
    added to its loggers or removed from them accordingly.
    """
    def _is_applied(slot:'int') -> 'bool':
        status = _invoke(slot, ModuleCtx.Status_Service)['streaming_enabled']
        is_handler_added = _invoke(slot, ModuleCtx.Handler_Service)['is_handler_added']

        out = status == is_enabled and is_handler_added == is_enabled
        return out

    wait_for_every_slot(_is_applied, f'log streaming {is_enabled}', ModuleCtx.Deadline)

# ################################################################################################################################
# ################################################################################################################################

class TestLogStreamingAcrossWorkers(unittest.TestCase):
    """ A toggle of log streaming through one worker is the state of every worker, in what each reports
    and in the handlers through which each streams its records.
    """

    def test_toggle_reaches_every_worker(self) -> 'None':

        is_enabled = _toggle()

        try:
            _wait_for_streaming(is_enabled)

        finally:
            is_restored = _toggle()
            _wait_for_streaming(is_restored)

        self.assertNotEqual(is_enabled, is_restored)

# ################################################################################################################################
# ################################################################################################################################
