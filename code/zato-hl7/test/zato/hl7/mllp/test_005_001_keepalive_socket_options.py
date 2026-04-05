# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket as socket_mod
from unittest import TestCase

# Test helpers
from conftest import (
    build_adt_a01,
    frame,
    ini_path_from_test_file,
    start_server,
    tcp_session,
    unframe,
)

# ################################################################################################################################
# ################################################################################################################################

class KeepaliveSocketOptionsTestCase(TestCase):
    """ Test 5.1 - after a connection is established, verify that SO_KEEPALIVE,
    TCP_KEEPIDLE, TCP_KEEPINTVL, and TCP_KEEPCNT match the configured values.
    The callback captures conn_ctx.socket for inspection.
    """

    @classmethod
    def setUpClass(cls) -> 'None':
        cls.captured_sockets = []

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> 'None':
            conn_ctx = zato_ctx['zato.channel_item']['hl7_mllp_conn_ctx']
            cls.captured_sockets.append(conn_ctx.socket)
            return None

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)

    @classmethod
    def tearDownClass(cls) -> 'None':
        cls.server.stop()

    def test_keepalive_options(self) -> 'None':

        payload = build_adt_a01(control_id=b'KA_001')

        with tcp_session(self.host, self.port) as sock:
            sock.sendall(frame(payload))
            resp = b''
            while b'\x1c\x0d' not in resp:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                resp += chunk

        self.assertEqual(len(self.captured_sockets), 1)
        server_sock = self.captured_sockets[0]

        keepalive = server_sock.getsockopt(socket_mod.SOL_SOCKET, socket_mod.SO_KEEPALIVE)
        self.assertEqual(keepalive, 1)

        if hasattr(socket_mod, 'TCP_KEEPIDLE'):
            idle = server_sock.getsockopt(socket_mod.IPPROTO_TCP, socket_mod.TCP_KEEPIDLE)
            self.assertEqual(idle, 77)

        if hasattr(socket_mod, 'TCP_KEEPINTVL'):
            interval = server_sock.getsockopt(socket_mod.IPPROTO_TCP, socket_mod.TCP_KEEPINTVL)
            self.assertEqual(interval, 13)

        if hasattr(socket_mod, 'TCP_KEEPCNT'):
            count = server_sock.getsockopt(socket_mod.IPPROTO_TCP, socket_mod.TCP_KEEPCNT)
            self.assertEqual(count, 9)

# ################################################################################################################################
# ################################################################################################################################
