# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from threading import Thread
from unittest import TestCase

# Test helpers
from conftest import (
    build_adt_a01,
    frame,
    ini_path_from_test_file,
    parse_ack,
    start_server,
    tcp_send,
    unframe,
)

# ################################################################################################################################
# ################################################################################################################################

class SimultaneousClientsTestCase(TestCase):
    """ Test 12.1 - open 10 TCP connections, each sending a different message concurrently.
    Verify all 10 receive correct ACKs with the right control ids.
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

    def test_10_simultaneous(self) -> 'None':

        total = 10
        results = [None] * total

        def send_one(idx:'int') -> 'None':
            control_id = f'SIM_{idx:03d}'.encode('ascii')
            msg = build_adt_a01(control_id=control_id)
            resp = tcp_send(self.host, self.port, frame(msg))
            ack = parse_ack(unframe(resp))
            results[idx] = (ack['ack_code'], ack['control_id'])

        threads = [Thread(target=send_one, args=(i,)) for i in range(total)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10.0)

        for i in range(total):
            expected_id = f'SIM_{i:03d}'.encode('ascii')
            self.assertIsNotNone(results[i], f'No result for client {i}')
            self.assertEqual(results[i][0], b'AA', f'Wrong ack code for client {i}')
            self.assertEqual(results[i][1], expected_id, f'Wrong control id for client {i}')

# ################################################################################################################################
# ################################################################################################################################
