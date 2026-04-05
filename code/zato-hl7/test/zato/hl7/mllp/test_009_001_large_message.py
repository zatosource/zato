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

def _build_message_with_obx(control_id:'bytes', obx_size:'int') -> 'bytes':
    """ Builds an ORU^R01 message with an OBX segment carrying obx_size bytes of observation data.
    """
    cr = b'\x0d'
    sep = b'|'

    msh = sep.join([
        b'MSH', b'^~\\&',
        b'TestApp', b'TestFac',
        b'ZatoApp', b'ZatoFac',
        b'20240101120000', b'',
        b'ORU^R01', control_id,
        b'P', b'2.5',
    ])

    pid = sep.join([b'PID', b'', b'', b'12345^^^Hosp^PI', b'', b'DOE^JOHN', b'', b'19800101', b'M'])
    obr = sep.join([b'OBR', b'1', b'', b'', b'CBC^Complete Blood Count'])

    # OBX with a large TX (text) value - use 'A' repeated obx_size times ..
    obx_value = b'A' * obx_size
    obx = sep.join([b'OBX', b'1', b'TX', b'RESULT', b'', obx_value, b'', b'', b'', b'', b'', b'F'])

    return cr.join([msh, pid, obr, obx]) + cr

# ################################################################################################################################
# ################################################################################################################################

class LargeMessageTestCase(TestCase):
    """ Test 9.1 - build a message with an OBX value containing 10,000 bytes.
    Verify the complete message is delivered to the callback and ACK is returned.
    """

    @classmethod
    def setUpClass(cls) -> 'None':
        cls.received_messages = []

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> 'None':
            cls.received_messages.append(data)
            return None

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)

    @classmethod
    def tearDownClass(cls) -> 'None':
        cls.server.stop()

    def test_10k_obx_message(self) -> 'None':

        payload = _build_message_with_obx(b'LRG_001', 10_000)

        with tcp_session(self.host, self.port, timeout=10.0) as sock:
            sock.sendall(frame(payload))

            resp = b''
            while b'\x1c\x0d' not in resp:
                chunk = sock.recv(65536)
                if not chunk:
                    break
                resp += chunk

        ack = parse_ack(unframe(resp))
        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], b'LRG_001')

        self.assertEqual(len(self.received_messages), 1)
        self.assertEqual(self.received_messages[0], payload)

# ################################################################################################################################
# ################################################################################################################################
