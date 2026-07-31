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
from _helpers import get_client, publish, publish_fhir

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
        """ One restart is paid for once, so both a REST connection and a FHIR one are put through it.
        """

        rest_receiver = TestConfig.orders_receiver
        fhir_receiver = TestConfig.fhir_receiver

        payload = {'order_id': 'order-6789', 'customer': 'Maria Kowalska'}

        document = {
            'resourceType': 'Patient',
            'name': [{'family': 'Kowalska', 'given': ['Maria']}],
        }

        # Both targets are down, so nothing can be delivered to either of them ..
        rest_receiver.stop()
        fhir_receiver.stop()

        try:
            _ = publish(self.client, TestConfig.orders_connection, payload)
            _ = publish_fhir(self.client, TestConfig.fhir_connection, document)

            # .. the server stops with both messages still queued, and comes back up ..
            restart_server()

        finally:

            # .. by which time both targets are up again.
            rest_receiver.start()
            fhir_receiver.start()

        # The REST message queued before the restart is delivered after it ..
        requests = rest_receiver.wait_for_requests(1)

        self.assertEqual(len(requests), 1, requests)

        request = requests[0]

        self.assertEqual(request.path, '/api/orders')
        self.assertEqual(loads(request.body), payload)

        # .. and so is the FHIR one, through a queue of its own.
        requests = fhir_receiver.wait_for_requests(1)

        self.assertEqual(len(requests), 1, requests)

        request = requests[0]

        expected_path = TestConfig.fhir_base_path + '/Patient'

        self.assertEqual(request.path, expected_path)
        self.assertEqual(loads(request.body), document)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
