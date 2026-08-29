# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from base64 import b64decode
from json import loads

# Zato
from zato.common.test.config_pubsub_outgoing import TestConfig

# local
from _helpers import get_client, publish_fhir

# ################################################################################################################################
# ################################################################################################################################

class FHIRConnectionConfigIsUsedTestCase(unittest.TestCase):
    """ A publication carries the document and nothing else - the address the request goes to and
    the credentials it goes out with both come from the connection that is published to.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.client = get_client()

# ################################################################################################################################

    def setUp(self) -> 'None':

        self.document = {
            'resourceType': 'Patient',
            'name': [{'family': 'Johnson', 'given': ['Maria']}],
        }

        _ = publish_fhir(self.client, TestConfig.fhir_secured_connection, self.document)

        receiver = TestConfig.fhir_secured_receiver
        requests = receiver.wait_for_requests(1)

        self.assertEqual(len(requests), 1, requests)

        self.request = requests[0]

# ################################################################################################################################

    def test_the_base_path_comes_from_the_connection(self) -> 'None':
        """ The connection is addressed with a base path, so the path a request lands on says
        both where it came from and what it is creating.
        """
        expected = TestConfig.fhir_base_path + '/Patient'
        self.assertEqual(self.request.path, expected)

# ################################################################################################################################

    def test_the_credentials_come_from_the_connection(self) -> 'None':

        header = self.request.headers['authorization']

        self.assertTrue(header.startswith('Basic '), header)

        encoded = header.split(' ', 1)[1]
        decoded = b64decode(encoded).decode('utf-8')

        username, password = decoded.split(':', 1)

        self.assertEqual(username, TestConfig.connection_username)
        self.assertEqual(password, TestConfig.connection_password)

# ################################################################################################################################

    def test_the_body_is_the_document_and_nothing_else(self) -> 'None':
        """ Nothing of the envelope that carried the document through the queue reaches the server.
        """
        body = loads(self.request.body)

        self.assertEqual(body, self.document)

# ################################################################################################################################

    def test_the_connection_that_was_not_published_to_is_left_alone(self) -> 'None':

        receiver = TestConfig.fhir_receiver
        self.assertEqual(receiver.requests, [], receiver.requests)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
