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

class PrependMSHNoMSHAnywhereTestCase(TestCase):
    """ Test 15.21 - prepend_msh_if_missing: no MSH anywhere; payload delivered as-is.
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

    def test_payload_unchanged_without_msh(self) -> 'None':
        raw = b'PID|1||MRN123||DOE^JOHN\x0d'
        tcp_send(self.host, self.port, frame(raw))

        self.assertEqual(len(self.received_payloads), 1)
        self.assertEqual(self.received_payloads[0], raw)


# ################################################################################################################################
# ################################################################################################################################
