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

class TestTupleInputOpenAPI(TestCase):

    def test_tuple_input_with_optional_params(self):
        test_file = os.path.join(
            os.path.dirname(__file__),
            'services',
            'test_tuple_input_service.py'
        )

        if not os.path.exists(test_file):
            self.skipTest(f'Test file not found: {test_file}')

        scanner = IOScanner()
        result = scanner.scan_file(test_file)

        self.assertEqual(len(result['services']), 1)
        service = result['services'][0]

        service_name = service['name']
        service_input = service['input']
        input_type = service_input['type']
        elements = service_input['elements']

        self.assertEqual(service_name, 'test.channel.person.get')
        self.assertEqual(input_type, 'tuple')
        self.assertEqual(len(elements), 3)

        elem0 = elements[0]
        elem1 = elements[1]
        elem2 = elements[2]

        self.assertEqual(elem0['name'], 'phone_number')
        self.assertTrue(elem0['required'])

        self.assertEqual(elem1['name'], 'message_to_user')
        self.assertFalse(elem1['required'])

        self.assertEqual(elem2['name'], 'authentication_method')
        self.assertFalse(elem2['required'])

# ################################################################################################################################

    def test_tuple_input_openapi_generation(self):
        test_file = os.path.join(
            os.path.dirname(__file__),
            'services',
            'test_tuple_input_service.py'
        )

        if not os.path.exists(test_file):
            self.skipTest(f'Test file not found: {test_file}')

        scanner = IOScanner()
        result = scanner.scan_file(test_file)

        service = result['services'][0]
        service_input = service['input']
        input_type = service_input['type']
        elements = service_input['elements']

        self.assertEqual(input_type, 'tuple')
        self.assertEqual(len(elements), 3)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()
