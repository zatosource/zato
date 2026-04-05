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

class NormalizeConcatenatedAckControlIdsTestCase(TestCase):
    """ Test 15.25 - normalize_concatenated_messages: ACK control ids match each message.
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

    def test_acks_reference_distinct_control_ids(self) -> 'None':
        msg1 = (
            b'MSH|^~\\&|App1|Fac1|RecvApp|RecvFac|20240101120000||ADT^A01|CAT_201|P|2.5\x0d'
            b'PID|||111^^^Hospital^PI||DOE^JOHN||19800101|M\x0d'
        )
        msg2 = (
            b'MSH|^~\\&|App2|Fac2|RecvApp|RecvFac|20240101120000||ADT^A01|CAT_202|P|2.5\x0d'
            b'PID|||222^^^Hospital^PI||SMITH^JANE||19900202|F\x0d'
        )
        combined = msg1 + msg2

        with tcp_session(self.host, self.port) as sock:
            sock.sendall(frame(combined))
            buf = b''
            while buf.count(b'\x1c\x0d') < 2:
                chunk = sock.recv(65536)
                if not chunk:
                    break
                buf += chunk

        responses = [resp for resp in buf.split(b'\x1c\x0d') if resp]
        self.assertEqual(len(responses), 2)

        ack1 = parse_ack(unframe(responses[0] + b'\x1c\x0d'))
        ack2 = parse_ack(unframe(responses[1] + b'\x1c\x0d'))
        self.assertEqual(ack1['control_id'], b'CAT_201')
        self.assertEqual(ack2['control_id'], b'CAT_202')

        self.assertEqual(len(self.received_payloads), 2)


# ################################################################################################################################
# ################################################################################################################################
