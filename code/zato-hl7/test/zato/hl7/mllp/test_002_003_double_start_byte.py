# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Test helpers
from conftest import (
    SB,
    EB_CR,
    build_adt_a01,
    ini_path_from_test_file,
    start_server,
    tcp_session,
)

# ################################################################################################################################
# ################################################################################################################################

class DoubleStartByteTestCase(TestCase):
    """ Test 2.3 - send 0x0B 0x0B + payload + 0x1C 0x0D.
    The first 0x0B is consumed as the header, the second 0x0B becomes part of the payload.
    Server processes it as a normal message (the extra byte is just corrupted payload data).
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

    def test_double_start_byte_delivers_payload_with_extra_byte(self) -> 'None':

        payload = build_adt_a01(control_id=b'DBL_SB01')
        bad_frame = SB + SB + payload + EB_CR

        with tcp_session(self.host, self.port, timeout=3.0) as sock:
            sock.sendall(bad_frame)

            # Server processes it, the extra 0x0B is part of the delivered payload ..
            data = sock.recv(65536)
            self.assertTrue(len(data) > 0)

        # The callback received the payload with the extra 0x0B prepended ..
        self.assertEqual(len(self.received_messages), 1)
        self.assertTrue(self.received_messages[0].startswith(b'\x0b'))

# ################################################################################################################################
# ################################################################################################################################
