# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile
from unittest import TestCase, main

# PyYAML
import yaml

# Zato
from zato.openapi.generator.io_scanner import IOScanner, TypeMapper
from zato.openapi.generator.openapi_ import OpenAPIGenerator

# ################################################################################################################################
# ################################################################################################################################

class TestTupleOutputOpenAPI(TestCase):

    def test_tuple_output_scanning(self):
        test_file = os.path.join(
            os.path.dirname(__file__),
            'services',
            'test_tuple_output_service.py'
        )

        if not os.path.exists(test_file):
            self.skipTest(f'Test file not found: {test_file}')

        scanner = IOScanner()
        result = scanner.scan_file(test_file)

        self.assertEqual(len(result['services']), 1)
        service = result['services'][0]

        service_name = service['name']
        service_output = service['output']
        output_type = service_output['type']
        elements = service_output['elements']

        self.assertEqual(service_name, 'test.channel.user.get-details')
        self.assertEqual(output_type, 'tuple')
        self.assertEqual(len(elements), 3)

        elem0 = elements[0]
        elem1 = elements[1]
        elem2 = elements[2]

        self.assertEqual(elem0['name'], 'user_type')
        self.assertTrue(elem0['required'])

        self.assertEqual(elem1['name'], 'account_no')
        self.assertTrue(elem1['required'])

        self.assertEqual(elem2['name'], 'account_balance')
        self.assertFalse(elem2['required'])

# ################################################################################################################################

    def test_tuple_output_openapi_generation(self):
        test_file = os.path.join(
            os.path.dirname(__file__),
            'services',
            'test_tuple_output_service.py'
        )

        if not os.path.exists(test_file):
            self.skipTest(f'Test file not found: {test_file}')

        scanner = IOScanner()
        result = scanner.scan_file(test_file)

        service = result['services'][0]
        service_output = service['output']

        type_mapper = TypeMapper()
        generator = OpenAPIGenerator(type_mapper)

        response_schema = generator._create_response_schema(service_output, result['models'])

        self.assertIsNotNone(response_schema)
        self.assertEqual(response_schema['type'], 'object')
        self.assertIn('properties', response_schema)

        properties = response_schema['properties']
        self.assertIn('user_type', properties)
        self.assertIn('account_no', properties)
        self.assertIn('account_balance', properties)

        self.assertEqual(properties['user_type']['type'], 'string')
        self.assertEqual(properties['account_no']['type'], 'string')
        self.assertEqual(properties['account_balance']['type'], 'string')

        required = response_schema.get('required', [])
        self.assertIn('user_type', required)
        self.assertIn('account_no', required)
        self.assertNotIn('account_balance', required)

# ################################################################################################################################

    def test_optional_string_input_scanning(self):
        test_file = os.path.join(
            os.path.dirname(__file__),
            'services',
            'test_tuple_output_service.py'
        )

        if not os.path.exists(test_file):
            self.skipTest(f'Test file not found: {test_file}')

        scanner = IOScanner()
        result = scanner.scan_file(test_file)

        service = result['services'][0]
        service_input = service['input']

        self.assertEqual(service_input['type'], 'string')
        self.assertEqual(service_input['name'], 'name')
        self.assertFalse(service_input['required'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()
