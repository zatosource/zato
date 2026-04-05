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
    start_server,
    tcp_send,
)

# ################################################################################################################################
# ################################################################################################################################

class EmptyMSH18TestCase(TestCase):
    """ Test 3.3 - build a message with no MSH-18 field.
    Verify the server defaults to ISO-8859-1.
    """

    @classmethod
    def setUpClass(cls) -> 'None':
        cls.received_ctx = []

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> 'None':
            cls.received_ctx.append(zato_ctx)
            return None

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)

    @classmethod
    def tearDownClass(cls) -> 'None':
        cls.server.stop()

    def test_empty_msh18_defaults_to_iso8859(self) -> 'None':

        # build_adt_a01 with default charset=b'' leaves MSH-18 empty ..
        payload = build_adt_a01(control_id=b'DFLT_001')
        _ = tcp_send(self.host, self.port, frame(payload))

        self.assertEqual(len(self.received_ctx), 1)
        channel_item = self.received_ctx[0]['zato.channel_item']
        self.assertEqual(channel_item['data_encoding'], 'iso-8859-1')

# ################################################################################################################################
# ################################################################################################################################
