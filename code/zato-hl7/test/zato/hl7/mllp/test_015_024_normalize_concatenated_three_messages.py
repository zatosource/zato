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
    tcp_session,
    unframe,
)

# ################################################################################################################################
# ################################################################################################################################

class NormalizeConcatenatedThreeMessagesTestCase(TestCase):
    """ Test 15.24 - normalize_concatenated_messages: three HL7 messages in one MLLP frame.
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

    def test_three_callbacks_and_three_acks(self) -> 'None':
        msg1 = (
            b'MSH|^~\\&|App1|Fac1|RecvApp|RecvFac|20240101120000||ADT^A01|CAT_101|P|2.5\x0d'
            b'PID|||111^^^Hospital^PI||DOE^JOHN||19800101|M\x0d'
        )
        msg2 = (
            b'MSH|^~\\&|App2|Fac2|RecvApp|RecvFac|20240101120000||ADT^A01|CAT_102|P|2.5\x0d'
            b'PID|||222^^^Hospital^PI||SMITH^JANE||19900202|F\x0d'
        )
        msg3 = (
            b'MSH|^~\\&|App3|Fac3|RecvApp|RecvFac|20240101120000||ADT^A01|CAT_103|P|2.5\x0d'
            b'PID|||333^^^Hospital^PI||BROWN^ALICE||20000303|F\x0d'
        )
        combined = msg1 + msg2 + msg3

        with tcp_session(self.host, self.port) as sock:
            sock.sendall(frame(combined))
            buf = b''
            while buf.count(b'\x1c\x0d') < 3:
                chunk = sock.recv(65536)
                if not chunk:
                    break
                buf += chunk

        responses = [resp for resp in buf.split(b'\x1c\x0d') if resp]
        self.assertEqual(len(responses), 3)
        for resp in responses:
            ack = parse_ack(unframe(resp + b'\x1c\x0d'))
            self.assertEqual(ack['ack_code'], b'AA')

        self.assertEqual(len(self.received_payloads), 3)
        self.assertIn(b'CAT_101', self.received_payloads[0])
        self.assertIn(b'CAT_102', self.received_payloads[1])
        self.assertIn(b'CAT_103', self.received_payloads[2])


# ################################################################################################################################
# ################################################################################################################################
