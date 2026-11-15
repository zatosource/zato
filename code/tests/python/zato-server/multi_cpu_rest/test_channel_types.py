# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import unittest

# Zato
from zato.common.soap.common import Content_Type, SOAP_Action_Header, SOAPVersion
from zato.common.soap.envelope import attach_body, build_envelope, to_bytes
from zato.common.soap.message import SOAPMessage
from zato.common.test.conftest_base_multi_cpu import basic_auth_header, ModuleCtx as MultiCPUCtx, MultiCPUTestConfig, \
     request_on_slot

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Service_Name = 'test.multi-cpu.constant'

    REST_Path = '/test/multi-cpu/constant'

    SOAP_Path      = '/test/multi-cpu/soap/constant'
    SOAP_Action    = 'urn:test:multi-cpu:constant'
    SOAP_Operation = 'GetConstant'
    SOAP_Version   = SOAPVersion.V11

# ################################################################################################################################
# ################################################################################################################################

class TestChannelTypesAcrossWorkers(unittest.TestCase):
    """ Every channel type answers a request for the same service with the same response from every worker.
    """

    def _assert_identical(self, method:'str', path:'str', body:'str', headers:'anydict') -> 'None':
        """ Sends the request through the worker of each slot and checks that every worker answers it in the same way.
        """
        responses:'dict[int, tuple[int, bytes]]' = {}

        for slot in range(MultiCPUTestConfig.worker_count):
            responses[slot] = request_on_slot(slot, method, path, body, headers)

        expected_status, expected_body = responses[0]
        self.assertEqual(expected_status, MultiCPUCtx.Status_OK, expected_body)

        for slot, response in responses.items():
            self.assertEqual(response, (expected_status, expected_body), f'Slot {slot}')

# ################################################################################################################################

    def test_rest_channel(self) -> 'None':
        self._assert_identical('GET', ModuleCtx.REST_Path, '', {})

# ################################################################################################################################

    def test_soap_channel(self) -> 'None':

        envelope = build_envelope(ModuleCtx.SOAP_Version)
        _ = attach_body(envelope, SOAPMessage(), ModuleCtx.SOAP_Operation)
        body = to_bytes(envelope).decode('utf8')

        headers = {
            'Content-Type': Content_Type[ModuleCtx.SOAP_Version],
            SOAP_Action_Header: ModuleCtx.SOAP_Action,
        }

        self._assert_identical('POST', ModuleCtx.SOAP_Path, body, headers)

# ################################################################################################################################

    def test_admin_invoke_channel(self) -> 'None':

        headers = {
            'Authorization': basic_auth_header(MultiCPUCtx.Admin_Username, MultiCPUTestConfig.invoke_password),
            'Content-Type': 'application/json',
        }

        path = MultiCPUCtx.Admin_Invoke_Path.format(ModuleCtx.Service_Name)
        self._assert_identical('POST', path, json.dumps({}), headers)

# ################################################################################################################################
# ################################################################################################################################
