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
    unframe,
)

# ################################################################################################################################
# ################################################################################################################################

class _FakeHL7Message:
    """ Minimal object with a serialize() method, mimicking zato_hl7v2.base.HL7Message.
    """
    def __init__(self, raw:'bytes') -> 'None':
        self.raw = raw

    def serialize(self) -> 'bytes':
        return self.raw

# ################################################################################################################################
# ################################################################################################################################

class CallbackReturnsSerializableTestCase(TestCase):
    """ Test 4.4 - callback returns an object with a serialize() method.
    The server must call serialize() and forward the result as the response.
    """

    serialized = b'MSH|^~\\&|ZatoApp|ZatoFac|TestApp|TestFac|20240101120000||ACK|SER_ACK|P|2.5\x0dMSA|AA|SER_001\x0d'

    @classmethod
    def setUpClass(cls) -> 'None':

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> '_FakeHL7Message':
            return _FakeHL7Message(cls.serialized)

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)

    @classmethod
    def tearDownClass(cls) -> 'None':
        cls.server.stop()

    def test_serializable_response(self) -> 'None':

        payload = build_adt_a01(control_id=b'SER_001')
        response_raw = tcp_send(self.host, self.port, frame(payload))

        response_payload = unframe(response_raw)
        self.assertEqual(response_payload, self.serialized)

# ################################################################################################################################
# ################################################################################################################################
