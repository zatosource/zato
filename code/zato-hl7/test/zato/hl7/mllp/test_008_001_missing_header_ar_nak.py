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
    frame,
    ini_path_from_test_file,
    parse_ack,
    start_server,
    tcp_send,
    tcp_session,
    unframe,
)

# ################################################################################################################################
# ################################################################################################################################

class MissingHeaderARNakTestCase(TestCase):
    """ Test 8.1 - send data without the 0x0B prefix.
    Server sends a best-effort AR NAK (the data may not be parseable as HL7)
    and closes the connection. A subsequent connection must still work.
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

    def test_ar_nak_on_missing_header(self) -> 'None':

        payload = build_adt_a01(control_id=b'NOHEAD_001')
        bad_frame = payload + EB_CR

        with tcp_session(self.host, self.port, timeout=3.0) as sock:
            sock.sendall(bad_frame)

            # Server sends AR NAK before closing ..
            data = sock.recv(65536)
            nak = parse_ack(unframe(data))
            self.assertEqual(nak['ack_code'], b'AR')

            # Connection is closed after the NAK ..
            trailing = sock.recv(65536)
            self.assertEqual(trailing, b'')

        # Server still accepts new connections ..
        msg = build_adt_a01(control_id=b'NOHEAD_002')
        response_raw = tcp_send(self.host, self.port, frame(msg))
        ack = parse_ack(unframe(response_raw))
        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], b'NOHEAD_002')

# ################################################################################################################################
# ################################################################################################################################
