# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
import unittest
from json import loads

# Zato
from zato.common.test.config_pubsub_outgoing import TestConfig

# local
from _helpers import get_client, publish

# ################################################################################################################################
# ################################################################################################################################

# How many times the target refuses the message before it accepts it.
_refusal_count = 2

# How long to keep watching after the message arrived, to see whether it arrives again.
_quiet_period_seconds = 15

# ################################################################################################################################
# ################################################################################################################################

class RetryUntilAcceptedTestCase(unittest.TestCase):
    """ A message the target refuses is offered again until it is accepted, and only once after that.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.client = get_client()

# ################################################################################################################################

    def test_a_refused_message_is_delivered_in_the_end(self) -> 'None':

        receiver = TestConfig.orders_receiver
        receiver.refuse_next(_refusal_count)

        payload = {'order_id': 'order-5678', 'customer': 'Maria Kowalska'}

        _ = publish(self.client, TestConfig.orders_connection, payload)

        requests = receiver.wait_for_requests(1)

        # The message arrived after the target stopped refusing it ..
        self.assertEqual(len(requests), 1, requests)

        request = requests[0]
        self.assertEqual(loads(request.body), payload)

        # .. it was refused as many times as the target was told to refuse it ..
        self.assertEqual(receiver.rejection_count, _refusal_count, receiver.rejection_count)

        # .. and having been accepted, it is not offered again.
        time.sleep(_quiet_period_seconds)

        self.assertEqual(len(receiver.requests), 1, receiver.requests)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
