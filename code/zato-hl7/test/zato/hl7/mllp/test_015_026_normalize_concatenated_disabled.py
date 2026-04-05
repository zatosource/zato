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

class NormalizeConcatenatedDisabledTestCase(TestCase):
    """ Test 15.26 - normalize_concatenated_messages disabled: one callback with full blob.
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

    def test_single_delivery_of_concatenated_blob(self) -> 'None':
        msg1 = (
            b'MSH|^~\\&|App1|Fac1|RecvApp|RecvFac|20240101120000||ADT^A01|CAT_301|P|2.5\x0d'
            b'PID|||111^^^Hospital^PI||DOE^JOHN||19800101|M\x0d'
        )
        msg2 = (
            b'MSH|^~\\&|App2|Fac2|RecvApp|RecvFac|20240101120000||ADT^A01|CAT_302|P|2.5\x0d'
            b'PID|||222^^^Hospital^PI||SMITH^JANE||19900202|F\x0d'
        )
        combined = msg1 + msg2
        tcp_send(self.host, self.port, frame(combined))

        self.assertEqual(len(self.received_payloads), 1)
        self.assertEqual(self.received_payloads[0], combined)


# ################################################################################################################################
# ################################################################################################################################
