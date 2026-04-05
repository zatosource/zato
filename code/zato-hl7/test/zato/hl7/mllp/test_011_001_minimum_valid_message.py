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

class MinimumValidMessageTestCase(TestCase):
    """ Test 11.1 - a message with only MSH (shortest possible valid HL7 v2 message).
    Verify ACK is returned.
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

    def test_msh_only(self) -> 'None':

        sep = b'|'
        msh = sep.join([
            b'MSH', b'^~\\&',
            b'App', b'Fac',
            b'ZatoApp', b'ZatoFac',
            b'20240101120000', b'',
            b'ADT^A01', b'MIN_001',
            b'P', b'2.5',
        ])
        payload = msh + b'\x0d'

        response_raw = tcp_send(self.host, self.port, frame(payload))

        ack = parse_ack(unframe(response_raw))
        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], b'MIN_001')

        self.assertEqual(len(self.received_messages), 1)

# ################################################################################################################################
# ################################################################################################################################
