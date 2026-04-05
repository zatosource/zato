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

class StripWhitespaceSendingAppTestCase(TestCase):
    """ Test 15.17 - strip leading whitespace from MSH-3; ACK MSH reflects swapped sender.
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

    def test_ack_msh_field5_is_stripped_sending_app(self) -> 'None':
        payload = build_adt_a01(sending_app=b'  MyApp', control_id=b'CTRL017')
        response_raw = tcp_send(self.host, self.port, frame(payload))

        ack = parse_ack(unframe(response_raw))
        msh_fields = ack['msh_fields']
        self.assertEqual(msh_fields[4], b'MyApp')


# ################################################################################################################################
# ################################################################################################################################
