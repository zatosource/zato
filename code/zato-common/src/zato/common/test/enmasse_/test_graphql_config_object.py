# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase, main

# Zato
from zato.common.model.graphql_ import GraphQLConfigObject

# ################################################################################################################################
# ################################################################################################################################

class TestGraphQLConfigObject(TestCase):
    """ Tests for GraphQLConfigObject dataclass fields and defaults.
    """

    def test_default_values(self):
        config = GraphQLConfigObject()

        self.assertEqual(config.id, 0)
        self.assertEqual(config.name, '')
        self.assertFalse(config.is_active)
        self.assertFalse(config.is_internal)
        self.assertEqual(config.address, '')
        self.assertIsNone(config.security_id)
        self.assertIsNone(config.security_name)
        self.assertIsNone(config.sec_type)
        self.assertIsNone(config.username)
        self.assertIsNone(config.password)
        self.assertIsNone(config.default_query_timeout)
        self.assertIsNone(config.extra)

# ################################################################################################################################

    def test_field_assignment(self):
        config = GraphQLConfigObject()
        config.id = 42
        config.name = 'ms365-graph'
        config.is_active = True
        config.address = 'https://graph.microsoft.com/v1.0'
        config.security_id = '7'
        config.security_name = 'ms365-oauth'
        config.sec_type = 'oauth'
        config.default_query_timeout = 30

        self.assertEqual(config.id, 42)
        self.assertEqual(config.name, 'ms365-graph')
        self.assertTrue(config.is_active)
        self.assertEqual(config.address, 'https://graph.microsoft.com/v1.0')
        self.assertEqual(config.security_id, '7')
        self.assertEqual(config.security_name, 'ms365-oauth')
        self.assertEqual(config.sec_type, 'oauth')
        self.assertEqual(config.default_query_timeout, 30)

# ################################################################################################################################

    def test_extra_field_json(self):
        config = GraphQLConfigObject()
        config.extra = '{"introspection": false, "custom_headers": {"X-Tenant": "abc"}}'

        self.assertEqual(config.extra, '{"introspection": false, "custom_headers": {"X-Tenant": "abc"}}')

# ################################################################################################################################

    def test_multiple_instances_independent(self):
        config1 = GraphQLConfigObject()
        config1.name = 'connection-1'
        config1.address = 'https://api1.example.com/graphql'

        config2 = GraphQLConfigObject()
        config2.name = 'connection-2'
        config2.address = 'https://api2.example.com/graphql'

        self.assertEqual(config1.name, 'connection-1')
        self.assertEqual(config2.name, 'connection-2')
        self.assertNotEqual(config1.address, config2.address)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
