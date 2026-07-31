# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.pubsub.outgoing import get_outgoing_sub_key
from zato.common.test.config_pubsub_outgoing import TestConfig
from zato.server.connection.outgoing_delivery import OutgoingType

# local
from _helpers import delete_connection, get_queue, get_client, publish

# ################################################################################################################################
# ################################################################################################################################

# How long to keep watching for a delivery that should never happen, in seconds.
_quiet_period_seconds = 10

# ################################################################################################################################
# ################################################################################################################################

class DeleteDropsTheQueueTestCase(unittest.TestCase):
    """ A deleted connection takes its queue with it, and what that queue still held is dropped
    rather than being delivered to something that is no longer there.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.client = get_client()

# ################################################################################################################################

    def test_a_deleted_connection_takes_its_queue_with_it(self) -> 'None':

        receiver = TestConfig.delete_receiver
        payload = {'order_id': 'order-9876', 'customer': 'Maria Kowalska'}

        conn_name = TestConfig.delete_connection

        # The target is down, so the message stays queued ..
        receiver.stop()

        try:
            _ = publish(self.client, conn_name, payload)

            # .. and the connection is deleted while it is still in there ..
            conn_id = delete_connection(self.client, conn_name)

        finally:

            # .. after which the target is up again, and would receive anything still queued.
            receiver.start()

        # Nothing is left of the queue ..
        sub_key = get_outgoing_sub_key(OutgoingType.REST, conn_id)
        queue = get_queue(self.client, sub_key)

        self.assertFalse(queue, queue)

        # .. and nothing ever reaches the target, because what was queued was dropped with the queue.
        requests = receiver.wait_for_requests(1, timeout=_quiet_period_seconds)
        self.assertEqual(requests, [], requests)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
