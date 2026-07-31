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
from _helpers import get_client, publish_fhir

# ################################################################################################################################
# ################################################################################################################################

# How long to keep watching after the expected documents arrived, to see whether any more of them do.
_quiet_period_seconds = 5

# The path a Patient is created under, which is the base path of the connection plus the type's own name
_patient_path = TestConfig.fhir_base_path + '/Patient'

# ################################################################################################################################
# ################################################################################################################################

def _new_patient(family_name:'str') -> 'dict':
    out = {
        'resourceType': 'Patient',
        'name': [{'family': family_name, 'given': ['Maria']}],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class FHIRPublishDeliversTestCase(unittest.TestCase):
    """ What a service publishes to an outgoing FHIR connection reaches that connection's server.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.client = get_client()

# ################################################################################################################################

    def test_the_document_is_created_under_the_path_its_type_names(self) -> 'None':

        document = _new_patient('Kowalska')

        _ = publish_fhir(self.client, TestConfig.fhir_connection, document)

        receiver = TestConfig.fhir_receiver
        requests = receiver.wait_for_requests(1)

        self.assertEqual(len(requests), 1, requests)

        request = requests[0]

        # A resource is created by posting it to the path its own type names, under the base
        # path the connection is addressed with
        self.assertEqual(request.method, 'POST')
        self.assertEqual(request.path, _patient_path)

# ################################################################################################################################

    def test_the_body_is_the_document_that_was_published(self) -> 'None':

        document = _new_patient('Nowak')

        _ = publish_fhir(self.client, TestConfig.fhir_connection, document)

        receiver = TestConfig.fhir_receiver
        requests = receiver.wait_for_requests(1)

        self.assertEqual(len(requests), 1, requests)

        self.assertEqual(loads(requests[0].body), document)

# ################################################################################################################################

    def test_publish_returns_the_id_of_the_queued_document(self) -> 'None':

        document = _new_patient('Lewandowska')

        msg_id = publish_fhir(self.client, TestConfig.fhir_connection, document)

        self.assertTrue(msg_id, msg_id)

        receiver = TestConfig.fhir_receiver
        requests = receiver.wait_for_requests(1)

        self.assertEqual(len(requests), 1, requests)

# ################################################################################################################################

    def test_every_document_arrives_once(self) -> 'None':

        expected = []

        for index in range(3):
            document = _new_patient(f'Family-{index}')
            expected.append(document)
            _ = publish_fhir(self.client, TestConfig.fhir_connection, document)

        receiver = TestConfig.fhir_receiver
        requests = receiver.wait_for_requests(3)

        self.assertEqual(len(requests), 3, requests)

        received = []

        for request in requests:
            received.append(loads(request.body))

        self.assertEqual(received, expected)

        # .. nothing arrives twice, so the count stands after everything has had time to be repeated.
        time.sleep(_quiet_period_seconds)

        self.assertEqual(len(receiver.requests), 3, receiver.requests)

# ################################################################################################################################

    def test_a_document_with_no_resource_type_is_refused(self) -> 'None':
        """ Such a document has no path to be created under, so it is refused when it is published
        rather than left retrying in a queue forever.
        """
        document = {'name': [{'family': 'Kowalska'}]}

        with self.assertRaises(Exception):
            _ = publish_fhir(self.client, TestConfig.fhir_connection, document)

        receiver = TestConfig.fhir_receiver

        time.sleep(_quiet_period_seconds)

        self.assertEqual(receiver.requests, [], receiver.requests)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
