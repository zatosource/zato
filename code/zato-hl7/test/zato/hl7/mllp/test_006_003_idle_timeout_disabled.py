# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# gevent
from gevent import sleep as gsleep

# Test helpers
from conftest import (
    build_adt_a01,
    frame,
    ini_path_from_test_file,
    parse_ack,
    start_server,
    tcp_session,
    unframe,
)

# ################################################################################################################################
# ################################################################################################################################

class IdleTimeoutDisabledTestCase(TestCase):
    """ Test 6.3 - configure idle_timeout = 0 (disabled).
    Connect, wait 5 seconds, send a message.
    Verify the message is still processed (connection not closed).
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

    def test_no_idle_timeout(self) -> 'None':

        msg = build_adt_a01(control_id=b'NOIDL_001')

        with tcp_session(self.host, self.port, timeout=10.0) as sock:

            # Wait well beyond any reasonable idle timeout ..
            gsleep(5.0)

            # Send a message - connection should still be alive ..
            sock.sendall(frame(msg))
            resp = b''
            while b'\x1c\x0d' not in resp:
                chunk = sock.recv(4096)
                if not chunk:
                    self.fail('Connection closed despite idle_timeout = 0')
                resp += chunk

            ack = parse_ack(unframe(resp))
            self.assertEqual(ack['ack_code'], b'AA')
            self.assertEqual(ack['control_id'], b'NOIDL_001')

# ################################################################################################################################
# ################################################################################################################################
