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
    FileIOVisitor,
    FileOpenAPIGenerator,
    scan_file,
    scan_files,
)

# ################################################################################################################################
# ################################################################################################################################

class TestFileIOVisitor(TestCase):

    def test_extract_service_with_no_io(self):
        code = '''
from zato.server.service import WSXAdapter

class TestWSXService(WSXAdapter):
    name = 'test.wsx.service'

    def on_connected(self, ctx):
        pass

    def on_message_received(self, ctx):
        pass
'''
        import ast
        tree = ast.parse(code)
        visitor = FileIOVisitor()
        visitor.visit(tree)

        self.assertEqual(len(visitor.services), 1)
        self.assertEqual(visitor.services[0]['name'], 'test.wsx.service')
        self.assertIsNone(visitor.services[0]['input'])
        self.assertIsNone(visitor.services[0]['output'])

# ################################################################################################################################

    def test_extract_service_with_tuple_input(self):
        code = '''
from zato.server.service import Service

class TestService(Service):
    name = 'test.tuple.service'
    input = ('param1', 'param2', 'param3')

    def handle(self):
        pass
'''
        import ast
        tree = ast.parse(code)
        visitor = FileIOVisitor()
        visitor.visit(tree)

        self.assertEqual(len(visitor.services), 1)
        service = visitor.services[0]
        self.assertEqual(service['name'], 'test.tuple.service')
        self.assertEqual(service['input']['type'], 'tuple')
        self.assertEqual(len(service['input']['elements']), 3)

# ################################################################################################################################

    def test_extract_service_with_model_io(self):
        code = '''
from zato.server.service import Service, Model

class InputModel(Model):
    field1: str
    field2: int

class OutputModel(Model):
    result: str

class TestService(Service):
    name = 'test.model.service'
    input = InputModel
    output = OutputModel

    def handle(self):
        pass
'''
        import ast
        tree = ast.parse(code)
        visitor = FileIOVisitor()
        visitor.visit(tree)

        self.assertEqual(len(visitor.services), 1)
        service = visitor.services[0]
        self.assertEqual(service['input']['type'], 'model')
        self.assertEqual(service['input']['model_name'], 'InputModel')
        self.assertEqual(service['output']['type'], 'model')
        self.assertEqual(service['output']['model_name'], 'OutputModel')

        self.assertEqual(len(visitor.models), 2)
        self.assertIn('InputModel', visitor.models)
        self.assertIn('OutputModel', visitor.models)

# ################################################################################################################################
# ################################################################################################################################

class TestFileOpenAPIGenerator(TestCase):

    def test_generate_openapi_no_io(self):
        services = [
            {'name': 'test.no.io', 'class_name': 'TestNoIO', 'input': None, 'output': None}
        ]
        models = {}

        generator = FileOpenAPIGenerator()
        openapi = generator.generate(services, models, 'Test API')

        self.assertEqual(openapi['openapi'], '3.1.0')
        self.assertEqual(openapi['info']['title'], 'Test API')
        self.assertIn('/test/no/io', openapi['paths'])

        path_item = openapi['paths']['/test/no/io']['post']
        request_schema = path_item['requestBody']['content']['application/json']['schema']
        response_schema = path_item['responses']['200']['content']['application/json']['schema']

        self.assertEqual(request_schema['type'], 'object')
        self.assertTrue(request_schema.get('additionalProperties'))
        self.assertEqual(response_schema['type'], 'object')
        self.assertTrue(response_schema.get('additionalProperties'))

# ################################################################################################################################

    def test_generate_openapi_tuple_input(self):
        services = [
            {
                'name': 'test.tuple.input',
                'class_name': 'TestTupleInput',
                'input': {'type': 'tuple', 'elements': [
                    {'name': 'param1', 'required': True},
                    {'name': 'param2', 'required': True},
                ]},
                'output': None
            }
        ]
        models = {}

        generator = FileOpenAPIGenerator()
        openapi = generator.generate(services, models, 'Test API')

        path_item = openapi['paths']['/test/tuple/input']['post']
        request_schema = path_item['requestBody']['content']['application/json']['schema']

        self.assertEqual(request_schema['type'], 'object')
        self.assertIn('param1', request_schema['properties'])
        self.assertIn('param2', request_schema['properties'])
        self.assertIn('param1', request_schema['required'])
        self.assertIn('param2', request_schema['required'])

# ################################################################################################################################
# ################################################################################################################################

class TestScanFile(TestCase):

    def test_scan_wsx_service_file(self):
        test_file = os.path.join(
            os.path.dirname(__file__),
            'services',
            'test_wsx_measurement.py'
        )

        if not os.path.exists(test_file):
            self.skipTest(f'Test file not found: {test_file}')

        result = scan_file(test_file)

        self.assertEqual(len(result['services']), 1)
        service = result['services'][0]
        self.assertEqual(service['name'], 'test.channel.wsx.measurement')
        self.assertIsNone(service['input'])
        self.assertIsNone(service['output'])

# ################################################################################################################################

    def test_scan_files_missing_file(self):
        result = scan_files(['/nonexistent/path/file.py'])
        self.assertEqual(len(result['services']), 0)

# ################################################################################################################################
# ################################################################################################################################

class TestCLIIntegration(TestCase):

    def test_full_generation_flow(self):
        service_code = '''
from zato.server.service import Service

class TestIntegrationService(Service):
    name = 'test.integration.service'
    input = ('name', 'value')

    def handle(self):
        pass
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(service_code)
            temp_input = f.name

        try:
            result = scan_files([temp_input])
            self.assertEqual(len(result['services']), 1)

            generator = FileOpenAPIGenerator()
            openapi = generator.generate(result['services'], result['models'], 'Integration Test')

            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(openapi, f)
                temp_output = f.name

            try:
                with open(temp_output, 'r') as f:
                    loaded = yaml.safe_load(f)

                self.assertEqual(loaded['openapi'], '3.1.0')
                self.assertIn('/test/integration/service', loaded['paths'])
            finally:
                os.unlink(temp_output)
        finally:
            os.unlink(temp_input)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()
