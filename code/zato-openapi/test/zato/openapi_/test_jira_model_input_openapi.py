# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from unittest import TestCase, main

# Zato
from zato.openapi.generator.io_scanner import IOScanner

# ################################################################################################################################
# ################################################################################################################################

class TestJiraModelInputOpenAPI(TestCase):

    def test_jira_service_with_model_input(self):
        services_dir = os.path.join(os.path.dirname(__file__), 'services')
        sys.path.insert(0, services_dir)

        try:
            model_file = os.path.join(services_dir, 'test_jira_model.py')
            service_file = os.path.join(services_dir, 'test_jira_service.py')

            if not os.path.exists(model_file) or not os.path.exists(service_file):
                self.skipTest('Test files not found')

            scanner = IOScanner()
            model_result = scanner.scan_file(model_file)
            service_result = scanner.scan_file(service_file)

            self.assertEqual(len(model_result['models']), 1)
            self.assertIn('JiraAccessRequestInput', model_result['models'])

            self.assertEqual(len(service_result['services']), 1)
            service = service_result['services'][0]

            service_name = service['name']
            service_input = service['input']
            input_type = service_input['type']
            model_name = service_input['model_name']

            self.assertEqual(service_name, 'test.channel.jira.webhook')
            self.assertEqual(input_type, 'model')
            self.assertEqual(model_name, 'JiraAccessRequestInput')

        finally:
            sys.path.remove(services_dir)

# ################################################################################################################################

    def test_jira_openapi_generation_with_model(self):
        services_dir = os.path.join(os.path.dirname(__file__), 'services')
        sys.path.insert(0, services_dir)

        try:
            model_file = os.path.join(services_dir, 'test_jira_model.py')
            service_file = os.path.join(services_dir, 'test_jira_service.py')

            if not os.path.exists(model_file) or not os.path.exists(service_file):
                self.skipTest('Test files not found')

            scanner = IOScanner()
            service_result = scanner.scan_file(service_file)

            self.assertEqual(len(service_result['services']), 1)
            service = service_result['services'][0]

            service_input = service['input']
            input_type = service_input['type']
            model_name = service_input['model_name']

            self.assertEqual(input_type, 'model')
            self.assertEqual(model_name, 'JiraAccessRequestInput')

            self.assertIn('JiraAccessRequestInput', service_result['models'])

        finally:
            sys.path.remove(services_dir)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()
