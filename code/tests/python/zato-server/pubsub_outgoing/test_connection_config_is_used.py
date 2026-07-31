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
from _helpers import get_client, publish

# ################################################################################################################################
# ################################################################################################################################

class ConnectionConfigIsUsedTestCase(unittest.TestCase):
    """ A publication carries the payload and nothing else - the method, the path, the query string,
    the headers and the credentials all come from the connection that is published to.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.client = get_client()

# ################################################################################################################################

    def setUp(self) -> 'None':

        self.payload = {'item_id': 'inventory-item-1', 'quantity': 12}

        _ = publish(self.client, TestConfig.inventory_connection, self.payload)

        receiver = TestConfig.inventory_receiver
        requests = receiver.wait_for_requests(1)

        self.assertEqual(len(requests), 1, requests)

        self.request = requests[0]

# ################################################################################################################################

    def test_the_method_comes_from_the_connection(self) -> 'None':
        self.assertEqual(self.request.method, 'PUT')

# ################################################################################################################################

    def test_the_path_comes_from_the_connection(self) -> 'None':
        self.assertEqual(self.request.path, '/api/inventory/items')

# ################################################################################################################################

    def test_the_query_string_comes_from_the_connection(self) -> 'None':
        self.assertEqual(self.request.query_string, 'status=active')

# ################################################################################################################################

    def test_the_headers_come_from_the_connection(self) -> 'None':
        self.assertEqual(self.request.headers['x-sync-source'], 'daily-sync')

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

    def test_the_body_is_what_was_published(self) -> 'None':
        self.assertEqual(loads(self.request.body), self.payload)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
