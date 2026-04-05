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

class FixTruncatedMSHMinimalMSHTestCase(TestCase):
    """ Test 15.14 - fix_truncated_msh: inbound MSH contains only MSH|^~\\& before CR.
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

    def test_server_returns_ack_without_crash(self) -> 'None':
        raw = (
            b'MSH|^~\\&\x0d'
            b'PID|||12345^^^Hospital^PI||DOE^JOHN||19800101|M\x0d'
        )

        response_raw = tcp_send(self.host, self.port, frame(raw))

        self.assertEqual(len(self.received_payloads), 1)

        ack = parse_ack(unframe(response_raw))
        self.assertEqual(ack['ack_code'], b'AA')


# ################################################################################################################################
# ################################################################################################################################
