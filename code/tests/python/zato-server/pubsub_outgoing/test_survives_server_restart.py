# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from json import loads

# Zato
from zato.common.test.config_pubsub_outgoing import restart_server, TestConfig

# local
from _helpers import get_client, publish

# ################################################################################################################################
# ################################################################################################################################

class SurvivesServerRestartTestCase(unittest.TestCase):
    """ A message queued for a connection that could not be reached is delivered once the server
    is running again and the connection is back up.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.client = get_client()

# ################################################################################################################################

    def test_a_queued_message_outlives_a_restart(self) -> 'None':

        receiver = TestConfig.orders_receiver
        payload = {'order_id': 'order-6789', 'customer': 'Maria Kowalska'}

        # The target is down, so nothing can be delivered to it ..
        receiver.stop()

        try:
            _ = publish(self.client, TestConfig.orders_connection, payload)

            # .. the server stops with the message still queued, and comes back up ..
            restart_server()

        finally:

            # .. by which time the target is up again.
            receiver.start()

        requests = receiver.wait_for_requests(1)

        self.assertEqual(len(requests), 1, requests)

        request = requests[0]

        self.assertEqual(request.path, '/api/orders')
        self.assertEqual(loads(request.body), payload)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
