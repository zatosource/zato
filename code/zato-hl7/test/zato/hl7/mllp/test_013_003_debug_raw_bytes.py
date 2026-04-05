# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
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

class _LogCapture(logging.Handler):
    """ Captures log records for later inspection.
    """
    def __init__(self) -> 'None':
        super().__init__()
        self.records = [] # type: list

    def emit(self, record:'logging.LogRecord') -> 'None':
        self.records.append(self.format(record))

# ################################################################################################################################
# ################################################################################################################################

class DebugRawBytesTestCase(TestCase):
    """ Test 13.3 - configure logging level to DEBUG.
    Send a message, verify the debug log contains the raw received bytes and their length.
    """

    @classmethod
    def setUpClass(cls) -> 'None':

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> 'None':
            return None

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)

        cls.log_capture = _LogCapture()
        cls.log_capture.setLevel(logging.DEBUG)
        logging.getLogger('zato_hl7').addHandler(cls.log_capture)

    @classmethod
    def tearDownClass(cls) -> 'None':
        logging.getLogger('zato_hl7').removeHandler(cls.log_capture)
        cls.server.stop()

    def test_debug_log_raw_bytes(self) -> 'None':

        payload = build_adt_a01(control_id=b'DBG_001')
        framed = frame(payload)
        _ = tcp_send(self.host, self.port, framed)

        all_logs = '\n'.join(self.log_capture.records)

        # Debug log should contain "HL7 MLLP data received" with the raw bytes ..
        self.assertIn('HL7 MLLP data received', all_logs)

        # Debug log should contain the byte length in parentheses ..
        expected_len = str(len(framed))
        self.assertIn(f'({expected_len})', all_logs)

# ################################################################################################################################
# ################################################################################################################################
