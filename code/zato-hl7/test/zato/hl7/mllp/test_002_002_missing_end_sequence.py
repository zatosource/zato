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
    build_adt_a01,
    ini_path_from_test_file,
    start_server,
    tcp_session,
)

# ################################################################################################################################
# ################################################################################################################################

class MissingEndSequenceTestCase(TestCase):
    """ Test 2.2 - send 0x0B + payload but never send 0x1C 0x0D.
    After idle_timeout, server closes the connection.
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

    def test_no_end_sequence_triggers_idle_timeout(self) -> 'None':

        # Send start byte + payload but no end sequence ..
        payload = build_adt_a01(control_id=b'NOEND001')
        incomplete = SB + payload

        with tcp_session(self.host, self.port, timeout=10.0) as sock:
            sock.sendall(incomplete)

            # Server idle_timeout is 3s, recv_timeout is 1s,
            # so the connection should be closed within ~4s ..
            data = sock.recv(65536)
            self.assertEqual(data, b'')

# ################################################################################################################################
# ################################################################################################################################
