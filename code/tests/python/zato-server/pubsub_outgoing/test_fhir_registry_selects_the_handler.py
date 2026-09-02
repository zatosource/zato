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
from _helpers import get_client, publish, publish_fhir

# ################################################################################################################################
# ################################################################################################################################

# How long to keep watching after a document arrived, to see whether the other target hears of it too.
_quiet_period_seconds = 5

# ################################################################################################################################
# ################################################################################################################################

class FHIRRegistrySelectsTheHandlerTestCase(unittest.TestCase):
    """ A REST connection and a FHIR connection go by one and the same name, so what decides where
    a message goes is the type it was published to, which is the registry doing the choosing.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.client = get_client()

# ################################################################################################################################

    def test_a_rest_publication_reaches_only_the_rest_target(self) -> 'None':

        payload = {'order_id': 'order-shared-1', 'customer': 'Maria Johnson'}

        _ = publish(self.client, TestConfig.shared_connection, payload)

        rest_receiver = TestConfig.shared_rest_receiver
        requests = rest_receiver.wait_for_requests(1)

        self.assertEqual(len(requests), 1, requests)
        self.assertEqual(requests[0].path, '/api/shared')
        self.assertEqual(loads(requests[0].body), payload)

        # The FHIR connection of the same name hears nothing of it
        time.sleep(_quiet_period_seconds)

        fhir_receiver = TestConfig.shared_fhir_receiver
        self.assertEqual(fhir_receiver.requests, [], fhir_receiver.requests)

# ################################################################################################################################

    def test_a_fhir_publication_reaches_only_the_fhir_target(self) -> 'None':

        document = {
            'resourceType': 'Patient',
            'name': [{'family': 'Johnson', 'given': ['Maria']}],
        }

        _ = publish_fhir(self.client, TestConfig.shared_connection, document)

        fhir_receiver = TestConfig.shared_fhir_receiver
        requests = fhir_receiver.wait_for_requests(1)

        self.assertEqual(len(requests), 1, requests)

        expected_path = TestConfig.fhir_base_path + '/Patient'

        self.assertEqual(requests[0].path, expected_path)
        self.assertEqual(loads(requests[0].body), document)

        # The REST connection of the same name hears nothing of it
        time.sleep(_quiet_period_seconds)

        rest_receiver = TestConfig.shared_rest_receiver
        self.assertEqual(rest_receiver.requests, [], rest_receiver.requests)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
