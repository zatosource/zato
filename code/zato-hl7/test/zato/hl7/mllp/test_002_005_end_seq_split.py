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
    SB,
    build_adt_a01,
    ini_path_from_test_file,
    parse_ack,
    start_server,
    tcp_session,
    unframe,
)

# ################################################################################################################################
# ################################################################################################################################

class EndSeqSplitTestCase(TestCase):
    """ Test 2.5 - send the framed message in two parts: everything up to and including
    the 0x1C byte in one send(), the trailing 0x0D in a second send().
    Server must still recognize the complete message and return an ACK.
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

    def test_end_seq_split_across_sends(self) -> 'None':

        payload = build_adt_a01(control_id=b'SPLIT001')

        # First part: SB + payload + 0x1C ..
        part1 = SB + payload + b'\x1c'

        # Second part: 0x0D ..
        part2 = b'\x0d'

        with tcp_session(self.host, self.port) as sock:
            sock.sendall(part1)
            sleep(0.05)
            sock.sendall(part2)

            response_raw = sock.recv(65536)

        ack = parse_ack(unframe(response_raw))
        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], b'SPLIT001')

# ################################################################################################################################
# ################################################################################################################################
