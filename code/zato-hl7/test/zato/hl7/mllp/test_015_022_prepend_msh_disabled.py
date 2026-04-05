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
    start_server,
    tcp_send,
)

# ################################################################################################################################
# ################################################################################################################################

class PrependMSHDisabledTestCase(TestCase):
    """ Test 15.22 - prepend_msh_if_missing disabled; SH-prefixed message unchanged.
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

    def test_raw_starts_with_sh(self) -> 'None':
        raw = (
            b'SH|^~\\&|SendApp|SendFac|RecvApp|RecvFac|20240101120000||ADT^A01|CTRL022|P|2.5\x0d'
            b'PID|||12345^^^Hospital^PI||DOE^JOHN||19800101|M\x0d'
        )
        tcp_send(self.host, self.port, frame(raw))

        self.assertEqual(len(self.received_payloads), 1)
        self.assertEqual(self.received_payloads[0], raw)
        self.assertTrue(self.received_payloads[0].startswith(b'SH|'))


# ################################################################################################################################
# ################################################################################################################################
