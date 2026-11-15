# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import unittest
from base64 import b64encode
from time import monotonic, sleep

# Zato
from zato.common.test.conftest_base_multi_cpu import connection_to_slot, ModuleCtx as MultiCPUCtx, MultiCPUTestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from http.client import HTTPResponse
    from zato.common.typing_ import anydict, intlist, strdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_mcp.sessions')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Path = '/mcp/multi-cpu'
    Username = 'test.multi-cpu.mcp'

    Session_Header = 'Mcp-Session-Id'
    Protocol_Version = '2025-06-18'

    # How long every slot has to refuse a terminated session, in seconds
    Termination_Deadline = 30.0
    Poll_Interval = 0.25

# ################################################################################################################################
# ################################################################################################################################

def _headers(session_id:'str') -> 'strdict':
    credentials = f'{ModuleCtx.Username}:{MultiCPUTestConfig.sec_password}'

    out = {
        'Authorization': 'Basic ' + b64encode(credentials.encode()).decode(),
        'Content-Type': 'application/json',
    }

    if session_id:
        out[ModuleCtx.Session_Header] = session_id

    return out

# ################################################################################################################################

def _send(slot:'int', method:'str', session_id:'str', params:'anydict') -> 'tuple[HTTPResponse, bytes]':
    """ Sends one JSON-RPC request to the worker of a slot and returns its response and body.
    """
    request:'anydict' = {
        'jsonrpc': '2.0',
        'id': 1,
        'method': method,
        'params': params,
    }

    connection = connection_to_slot(slot)
    connection.request('POST', ModuleCtx.Path, body=json.dumps(request), headers=_headers(session_id))

    response = connection.getresponse()
    body = response.read()
    connection.close()

    out = (response, body)
    return out

# ################################################################################################################################

def _delete(slot:'int', session_id:'str') -> 'int':
    connection = connection_to_slot(slot)
    connection.request('DELETE', ModuleCtx.Path, headers=_headers(session_id))

    response = connection.getresponse()
    _ = response.read()
    connection.close()

    out = response.status
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestMCPSessionsAcrossWorkers(unittest.TestCase):
    """ An MCP session opened through one worker continues through every other worker and ends on every worker.
    """

    def _initialize(self, slot:'int') -> 'str':
        params = {
            'protocolVersion': ModuleCtx.Protocol_Version,
            'capabilities': {},
            'clientInfo': {'name': 'zato-multi-cpu-test', 'version': '1.0'},
        }

        response, body = _send(slot, 'initialize', '', params)
        self.assertEqual(response.status, MultiCPUCtx.Status_OK, body)

        session_id = response.getheader(ModuleCtx.Session_Header)

        if session_id is None:
            self.fail(f'No session ID from slot {slot} -> {body!r}')

        out = session_id
        return out

# ################################################################################################################################

    def test_session_continues_through_every_worker(self) -> 'None':
        """ A session opened through the first slot serves tools/list through every slot.
        """
        session_id = self._initialize(0)

        for slot in range(MultiCPUTestConfig.worker_count):
            response, body = _send(slot, 'tools/list', session_id, {})
            logger.info('tools/list through slot %s -> %s', slot, response.status)

            self.assertEqual(response.status, MultiCPUCtx.Status_OK, f'Slot {slot} -> {body!r}')
            self.assertIn('result', json.loads(body), f'Slot {slot}')

# ################################################################################################################################

    def test_session_ends_on_every_worker(self) -> 'None':
        """ A session opened through the first slot and terminated through the last slot is refused by every slot.
        """
        last_slot = MultiCPUTestConfig.worker_count - 1
        session_id = self._initialize(0)

        status = _delete(last_slot, session_id)
        self.assertLess(status, 300)

        pending:'intlist' = list(range(MultiCPUTestConfig.worker_count))
        deadline = monotonic() + ModuleCtx.Termination_Deadline

        while pending:
            still_pending:'intlist' = []

            for slot in pending:
                response, _ = _send(slot, 'tools/list', session_id, {})
                if response.status == MultiCPUCtx.Status_OK:
                    still_pending.append(slot)

            pending = still_pending

            if pending:
                if monotonic() > deadline:
                    self.fail(f'Slots {pending} still serve the terminated session after {ModuleCtx.Termination_Deadline}s')
                sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################
# ################################################################################################################################
