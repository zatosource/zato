# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.hl7.mllp.server import ServerQuirks

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

class ZatoCtxServerQuirksDefaultsTestCase(TestCase):
    """ Test 15.36 - Quirks exposed in zato_ctx: default quirks (no [quirks] in .ini).
    """

    @classmethod
    def setUpClass(cls) -> 'None':
        cls.received_contexts = []

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> 'None':
            cls.received_contexts.append(zato_ctx)
            return None

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)

    @classmethod
    def tearDownClass(cls) -> 'None':
        cls.server.stop()

    def test_zato_ctx_default_server_quirks(self) -> 'None':
        payload = build_adt_a01()
        tcp_send(self.host, self.port, frame(payload))

        self.assertEqual(len(self.received_contexts), 1)
        zato_ctx = self.received_contexts[0]
        server_quirks = zato_ctx['zato.channel_item']['server_quirks']
        self.assertIsInstance(server_quirks, ServerQuirks)
        self.assertTrue(server_quirks.normalize_lf_to_cr)
        self.assertFalse(server_quirks.prepend_msh_if_missing)
        self.assertEqual(server_quirks.max_ack_field_len, 200)


# ################################################################################################################################
# ################################################################################################################################
