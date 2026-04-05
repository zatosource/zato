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

class MaxAckFieldLenDisabledZeroTestCase(TestCase):
    """ Test 15.30 - max_ack_field_len = 0 disables truncation in ACK.
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

    def test_ack_msh_sending_app_full_length(self) -> 'None':
        payload = build_adt_a01(sending_app=b'C' * 500, control_id=b'CTRL030')
        response_raw = tcp_send(self.host, self.port, frame(payload))
        ack = parse_ack(unframe(response_raw))
        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(len(ack['msh_fields'][4]), 500)


# ################################################################################################################################
# ################################################################################################################################
