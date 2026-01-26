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
from zato.openapi.generator.file_generator import (
    FileOpenAPIGenerator,
    scan_file,
)

# ################################################################################################################################
# ################################################################################################################################

class TestTupleInputOpenAPI(TestCase):

    def test_tuple_input_with_optional_params(self):
        test_file = os.path.join(
            os.path.dirname(__file__),
            'services',
            'test_tuple_input_service.py'
        )

        if not os.path.exists(test_file):
            self.skipTest(f'Test file not found: {test_file}')

        result = scan_file(test_file)

        self.assertEqual(len(result['services']), 1)
        service = result['services'][0]

        self.assertEqual(service['name'], 'test.channel.person.get')
        self.assertEqual(service['input']['type'], 'tuple')

        elements = service['input']['elements']
        self.assertEqual(len(elements), 3)

        self.assertEqual(elements[0]['name'], 'phone_number')
        self.assertTrue(elements[0]['required'])

        self.assertEqual(elements[1]['name'], 'message_to_user')
        self.assertFalse(elements[1]['required'])

        self.assertEqual(elements[2]['name'], 'authentication_method')
        self.assertFalse(elements[2]['required'])

# ################################################################################################################################

    def test_tuple_input_openapi_generation(self):
        test_file = os.path.join(
            os.path.dirname(__file__),
            'services',
            'test_tuple_input_service.py'
        )

        if not os.path.exists(test_file):
            self.skipTest(f'Test file not found: {test_file}')

        result = scan_file(test_file)
        generator = FileOpenAPIGenerator()
        openapi = generator.generate(result['services'], result['models'], 'Test API')

        self.assertEqual(openapi['openapi'], '3.1.0')
        self.assertIn('/test/channel/person/get', openapi['paths'])

        path_item = openapi['paths']['/test/channel/person/get']['post']
        request_schema = path_item['requestBody']['content']['application/json']['schema']

        self.assertEqual(request_schema['type'], 'object')
        self.assertIn('phone_number', request_schema['properties'])
        self.assertIn('message_to_user', request_schema['properties'])
        self.assertIn('authentication_method', request_schema['properties'])

        self.assertIn('phone_number', request_schema['required'])
        self.assertNotIn('message_to_user', request_schema['required'])
        self.assertNotIn('authentication_method', request_schema['required'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()
