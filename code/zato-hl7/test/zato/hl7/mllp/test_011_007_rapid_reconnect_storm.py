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
    tcp_send,
    unframe,
)

# ################################################################################################################################
# ################################################################################################################################

class RapidReconnectStormTestCase(TestCase):
    """ Test 11.7 - open and close 100 connections in a tight loop, each sending one message.
    Verify all 100 ACKs are received and the server remains healthy.
    """

    @classmethod
    def setUpClass(cls) -> 'None':
        cls.received_count = 0

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> 'None':
            cls.received_count += 1
            return None

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)

    @classmethod
    def tearDownClass(cls) -> 'None':
        cls.server.stop()

    def test_100_rapid_connections(self) -> 'None':

        total = 100
        ack_codes = []

        for i in range(total):
            control_id = f'STORM_{i:03d}'.encode('ascii')
            msg = build_adt_a01(control_id=control_id)
            resp = tcp_send(self.host, self.port, frame(msg))
            ack = parse_ack(unframe(resp))
            ack_codes.append(ack['ack_code'])

        self.assertEqual(len(ack_codes), total)
        self.assertTrue(all(code == b'AA' for code in ack_codes))
        self.assertEqual(self.received_count, total)

# ################################################################################################################################
# ################################################################################################################################
