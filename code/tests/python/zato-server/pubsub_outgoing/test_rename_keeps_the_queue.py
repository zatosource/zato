# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from json import loads

# Zato
from zato.common.pubsub.outgoing import get_outgoing_sub_key, get_outgoing_topic_name, OutgoingType
from zato.common.test.config_pubsub_outgoing import TestConfig

# local
from _helpers import get_queue, get_client, publish, rename_connection

# ################################################################################################################################
# ################################################################################################################################

# How long to keep watching for a second delivery of the same message, in seconds.
_quiet_period_seconds = 5

# ################################################################################################################################
# ################################################################################################################################

class RenameKeepsTheQueueTestCase(unittest.TestCase):
    """ A message queued for a connection that is then renamed is delivered to that connection
    under its new name, out of the one queue it was in all along.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.client = get_client()

# ################################################################################################################################

    def test_a_queued_message_outlives_a_rename(self) -> 'None':

        receiver = TestConfig.rename_receiver
        payload = {'order_id': 'order-4321', 'customer': 'Maria Kowalska'}

        conn_name = TestConfig.rename_connection
        new_name = TestConfig.rename_connection_new_name

        # The target is down, so the message stays queued ..
        receiver.stop()

        try:
            _ = publish(self.client, conn_name, payload)

            # .. and the connection is renamed while it is still in there ..
            conn_id = rename_connection(self.client, conn_name, new_name)

        finally:

            # .. by which time the target is up again.
            receiver.start()

        requests = receiver.wait_for_requests(1)

        self.assertEqual(len(requests), 1, requests)

        request = requests[0]

        # What was published before the rename reached the connection after it ..
        self.assertEqual(request.path, '/api/rename')
        self.assertEqual(loads(request.body), payload)

        # .. exactly once ..
        requests = receiver.wait_for_requests(2, timeout=_quiet_period_seconds)
        self.assertEqual(len(requests), 1, requests)

        # .. out of the queue it was always in, of which there is one and not two ..
        sub_key = get_outgoing_sub_key(OutgoingType.REST, conn_id)
        queue = get_queue(self.client, sub_key)

        self.assertTrue(queue, sub_key)

        # .. and that queue is under the topic of the new name only ..
        new_topic = get_outgoing_topic_name(OutgoingType.REST, new_name)
        self.assertEqual(queue['topic_name_list'], [new_topic])

        # .. which is also the queue that what is published from now on goes through.
        second_payload = {'order_id': 'order-5432', 'customer': 'Anna Nowak'}
        _ = publish(self.client, new_name, second_payload)

        requests = receiver.wait_for_requests(2)

        self.assertEqual(len(requests), 2, requests)
        self.assertEqual(loads(requests[1].body), second_payload)

        queue = get_queue(self.client, sub_key)
        self.assertEqual(queue['topic_name_list'], [new_topic])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
