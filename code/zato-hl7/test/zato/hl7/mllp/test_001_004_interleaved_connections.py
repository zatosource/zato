# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

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

class InterleavedConnectionsTestCase(TestCase):
    """ Test 1.4 - open two TCP connections simultaneously.
    Send a message on each, verify both get correct independent ACKs.
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

    def test_two_simultaneous_connections(self) -> 'None':

        control_id_a = b'CONN_A_01'
        control_id_b = b'CONN_B_01'

        with tcp_session(self.host, self.port) as sock_a, \
             tcp_session(self.host, self.port) as sock_b:

            # .. send on connection A ..
            sock_a.sendall(frame(build_adt_a01(control_id=control_id_a)))

            # .. send on connection B ..
            sock_b.sendall(frame(build_adt_a01(control_id=control_id_b)))

            # .. read responses ..
            ack_a = parse_ack(unframe(sock_a.recv(65536)))
            ack_b = parse_ack(unframe(sock_b.recv(65536)))

        self.assertEqual(ack_a['ack_code'], b'AA')
        self.assertEqual(ack_a['control_id'], control_id_a)

        self.assertEqual(ack_b['ack_code'], b'AA')
        self.assertEqual(ack_b['control_id'], control_id_b)

# ################################################################################################################################
# ################################################################################################################################
