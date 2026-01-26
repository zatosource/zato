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
from zato.openapi.generator.file_generator import (
    FileOpenAPIGenerator,
    scan_file,
)

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

            model_result = scan_file(model_file)
            service_result = scan_file(service_file)

            self.assertEqual(len(model_result['models']), 1)
            self.assertIn('JiraAccessRequestInput', model_result['models'])

            self.assertEqual(len(service_result['services']), 1)
            service = service_result['services'][0]

            self.assertEqual(service['name'], 'test.channel.jira.webhook')
            self.assertEqual(service['input']['type'], 'model')
            self.assertEqual(service['input']['model_name'], 'JiraAccessRequestInput')

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

            model_result = scan_file(model_file)
            service_result = scan_file(service_file)

            all_services = service_result['services']
            all_models = {**model_result['models'], **service_result['models']}

            generator = FileOpenAPIGenerator()
            openapi = generator.generate(all_services, all_models, 'Jira API')

            self.assertEqual(openapi['openapi'], '3.1.0')
            self.assertIn('/test/channel/jira/webhook', openapi['paths'])

            path_item = openapi['paths']['/test/channel/jira/webhook']['post']
            request_schema = path_item['requestBody']['content']['application/json']['schema']

            self.assertIn('$ref', request_schema)
            self.assertEqual(request_schema['$ref'], '#/components/schemas/JiraAccessRequestInput')

            self.assertIn('JiraAccessRequestInput', openapi['components']['schemas'])

            model_schema = openapi['components']['schemas']['JiraAccessRequestInput']
            self.assertEqual(model_schema['type'], 'object')
            self.assertIn('issue_key', model_schema['properties'])
            self.assertIn('email', model_schema['properties'])

        finally:
            sys.path.remove(services_dir)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()
