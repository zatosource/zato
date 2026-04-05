# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Test helpers
from conftest import (
    frame,
    ini_path_from_test_file,
    parse_ack,
    start_server,
    tcp_send,
    unframe,
)

# ################################################################################################################################
# ################################################################################################################################

class Bare0x1CInPayloadTestCase(TestCase):
    """ Test 2.4 - build a message where an OBX observation value contains a literal 0x1C byte
    (not followed by 0x0D). Server must deliver the complete message to the callback without truncation.
    """

    @classmethod
    def setUpClass(cls) -> 'None':
        cls.received_messages = []

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> 'None':
            cls.received_messages.append(data)
            return None

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)

    @classmethod
    def tearDownClass(cls) -> 'None':
        cls.server.stop()

    def test_bare_0x1c_not_treated_as_end(self) -> 'None':

        cr = b'\x0d'
        sep = b'|'

        # Build a message with 0x1C embedded in an OBX value (not followed by 0x0D) ..
        msh = sep.join([
            b'MSH', b'^~\\&',
            b'TestApp', b'TestFac',
            b'ZatoApp', b'ZatoFac',
            b'20240101120000', b'',
            b'ORU^R01', b'BARE1C01',
            b'P', b'2.5',
        ])

        obx_value = b'ABC\x1cDEF'
        obx = sep.join([b'OBX', b'1', b'ST', b'12345', b'', obx_value])

        payload = cr.join([msh, obx]) + cr
        framed = frame(payload)

        response_raw = tcp_send(self.host, self.port, framed)
        ack = parse_ack(unframe(response_raw))

        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], b'BARE1C01')

        # The callback must have received the full payload including the 0x1C byte ..
        self.assertEqual(len(self.received_messages), 1)
        self.assertIn(b'\x1c', self.received_messages[0])
        self.assertIn(b'ABC\x1cDEF', self.received_messages[0])

# ################################################################################################################################
# ################################################################################################################################
