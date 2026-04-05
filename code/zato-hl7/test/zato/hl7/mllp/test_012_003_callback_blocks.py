# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from threading import Thread
from time import monotonic
from unittest import TestCase

# gevent
from gevent import sleep as gsleep

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

class CallbackBlocksTestCase(TestCase):
    """ Test 12.3 - callback sleeps 3 seconds on the first call.
    Send two messages on separate connections. The second connection's response
    must not be blocked by the first.
    """

    @classmethod
    def setUpClass(cls) -> 'None':
        cls.call_count = 0

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> 'None':
            cls.call_count += 1
            if cls.call_count == 1:
                gsleep(3.0)
            return None

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)

    @classmethod
    def tearDownClass(cls) -> 'None':
        cls.server.stop()

    def test_second_not_blocked(self) -> 'None':

        msg1 = build_adt_a01(control_id=b'BLOCK_001')
        msg2 = build_adt_a01(control_id=b'BLOCK_002')

        result1 = [None]
        result2 = [None]
        time2 = [None]

        def sender1() -> 'None':
            resp = tcp_send(self.host, self.port, frame(msg1), timeout=10.0)
            result1[0] = parse_ack(unframe(resp))

        def sender2() -> 'None':
            gsleep(0.3)
            t0 = monotonic()
            resp = tcp_send(self.host, self.port, frame(msg2), timeout=10.0)
            time2[0] = monotonic() - t0
            result2[0] = parse_ack(unframe(resp))

        t1 = Thread(target=sender1)
        t2 = Thread(target=sender2)
        t1.start()
        t2.start()
        t1.join(timeout=10.0)
        t2.join(timeout=10.0)

        self.assertIsNotNone(result1[0])
        self.assertEqual(result1[0]['ack_code'], b'AA')

        self.assertIsNotNone(result2[0])
        self.assertEqual(result2[0]['ack_code'], b'AA')
        self.assertEqual(result2[0]['control_id'], b'BLOCK_002')

        # The second client should get its response in under 2 seconds,
        # not blocked by the first client's 3-second callback ..
        self.assertLess(time2[0], 2.0)

# ################################################################################################################################
# ################################################################################################################################
