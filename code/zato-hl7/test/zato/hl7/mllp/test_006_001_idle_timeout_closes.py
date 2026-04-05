# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
from time import monotonic
from unittest import TestCase

# Test helpers
from conftest import (
    ini_path_from_test_file,
    start_server,
)

# ################################################################################################################################
# ################################################################################################################################

class IdleTimeoutClosesTestCase(TestCase):
    """ Test 6.1 - configure idle_timeout = 2, recv_timeout = 1.
    Connect, send nothing. Verify the server closes the connection within 3 seconds.
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

    def test_idle_timeout_closes_connection(self) -> 'None':

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect((self.host, self.port))

        t0 = monotonic()

        # Wait for the server to close the connection ..
        try:
            while True:
                data = sock.recv(4096)
                if not data:
                    break
        except (ConnectionError, socket.timeout, OSError):
            pass
        finally:
            sock.close()

        elapsed = monotonic() - t0

        # The server should have closed within ~2-3 seconds (idle_timeout=2, recv_timeout=1) ..
        self.assertLess(elapsed, 5.0)
        self.assertGreaterEqual(elapsed, 1.5)

# ################################################################################################################################
# ################################################################################################################################
