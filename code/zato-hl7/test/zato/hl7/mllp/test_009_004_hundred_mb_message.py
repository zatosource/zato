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
    frame,
    ini_path_from_test_file,
    parse_ack,
    start_server,
    tcp_session,
    unframe,
)

from test_009_001_large_message import _build_message_with_obx

# ################################################################################################################################
# ################################################################################################################################

class HundredMBMessageTestCase(TestCase):
    """ Test 9.4 - build a message with a 100 MB OBX field.
    Verify complete delivery and ACK. No artificial size limit in the server.
    """

    @classmethod
    def setUpClass(cls) -> 'None':
        cls.received_sizes = []

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> 'None':
            cls.received_sizes.append(len(data))
            return None

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)

    @classmethod
    def tearDownClass(cls) -> 'None':
        cls.server.stop()

    def test_100mb_message(self) -> 'None':

        hundred_mb = 100 * 1024 * 1024
        payload = _build_message_with_obx(b'100MB_001', hundred_mb)
        expected_size = len(payload)

        with tcp_session(self.host, self.port, timeout=120.0) as sock:
            sock.sendall(frame(payload))

            resp = b''
            while EB_CR not in resp:
                chunk = sock.recv(1048576)
                if not chunk:
                    break
                resp += chunk

        ack = parse_ack(unframe(resp))
        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], b'100MB_001')

        self.assertEqual(len(self.received_sizes), 1)
        self.assertEqual(self.received_sizes[0], expected_size)

# ################################################################################################################################
# ################################################################################################################################
