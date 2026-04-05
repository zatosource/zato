# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import sleep
from unittest import TestCase

# Test helpers
from conftest import (
    EB_CR,
    build_adt_a01,
    ini_path_from_test_file,
    parse_ack,
    start_server,
    tcp_session,
    unframe,
)

# ################################################################################################################################
# ################################################################################################################################

class StartSeqSplitTestCase(TestCase):
    """ Test 2.6 - configure the server with a two-byte start_seq (0x0B 0x0B).
    Send the first byte in one send(), the second byte plus the rest of the message in the next.
    Server must still accept the message.
    """

    @classmethod
    def setUpClass(cls) -> 'None':

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> 'None':
            return None

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)

    @classmethod
    def tearDownClass(cls) -> 'None':
        cls.server.stop()

    def test_two_byte_start_seq_split(self) -> 'None':

        payload = build_adt_a01(control_id=b'SBSPL001')

        # Server expects two-byte start_seq 0x0B 0x0B ..
        part1 = b'\x0b'
        part2 = b'\x0b' + payload + EB_CR

        with tcp_session(self.host, self.port) as sock:
            sock.sendall(part1)
            sleep(0.05)
            sock.sendall(part2)

            response_raw = sock.recv(65536)

        ack = parse_ack(unframe(response_raw))
        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], b'SBSPL001')

# ################################################################################################################################
# ################################################################################################################################
