# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
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

class MissingStartByteTestCase(TestCase):
    """ Test 2.1 - send payload bytes without the leading 0x0B.
    Server must close the connection.
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

    def test_no_start_byte(self) -> 'None':

        # Send payload without 0x0B, just raw data + end sequence ..
        payload = build_adt_a01(control_id=b'NOSB_001')
        bad_frame = payload + EB_CR

        with tcp_session(self.host, self.port, timeout=3.0) as sock:
            sock.sendall(bad_frame)

            # Server detects header mismatch, sends a best-effort AR NAK, then closes ..
            data = sock.recv(65536)
            nak_payload = unframe(data)
            ack = parse_ack(nak_payload)
            self.assertEqual(ack['ack_code'], b'AR')

            # After the NAK, the connection is closed ..
            trailing = sock.recv(65536)
            self.assertEqual(trailing, b'')

# ################################################################################################################################
# ################################################################################################################################
