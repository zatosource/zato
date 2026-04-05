# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Test helpers
from conftest import (
    frame,
    ini_path_from_test_file,
    parse_ack,
    start_server,
    tcp_send,
    unframe,
)

# ################################################################################################################################
# ################################################################################################################################

class CombinedAllQuirksDisabledTestCase(TestCase):
    """ Test 15.34 - Combined: all quirks disabled; raw bytes unchanged.
    """

    @classmethod
    def setUpClass(cls) -> 'None':
        cls.received_payloads = []

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> 'None':
            cls.received_payloads.append(data)
            return None

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)

    @classmethod
    def tearDownClass(cls) -> 'None':
        cls.server.stop()

    def test_callback_sees_raw_bytes_unchanged(self) -> 'None':
        raw = (
            b'MSH|^| Lab|Fac1|RecvApp|RecvFac\x0a'
            b'PID|||12345^^^Hospital^PI||DOE^JOHN||19800101|M\x0a'
        )

        response_raw = tcp_send(self.host, self.port, frame(raw))

        self.assertEqual(len(self.received_payloads), 1)
        self.assertEqual(self.received_payloads[0], raw)

        ack = parse_ack(unframe(response_raw))
        self.assertIn(ack['ack_code'], (b'AA', b'AE', b'AR'))


# ################################################################################################################################
# ################################################################################################################################
