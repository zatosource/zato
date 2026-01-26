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
from zato.openapi.generator.io_scanner import IOVisitor, IOScanner, TypeMapper
from zato.openapi.generator.openapi_ import OpenAPIGenerator

# ################################################################################################################################
# ################################################################################################################################

class TestIOVisitor(TestCase):

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
        visitor = IOVisitor()
        visitor.visit(tree)

        self.assertEqual(len(visitor.services), 1)
        service = visitor.services[0]
        service_name = service['name']
        service_input = service['input']
        service_output = service['output']

        self.assertEqual(service_name, 'test.wsx.service')
        self.assertIsNone(service_input)
        self.assertIsNone(service_output)

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
        visitor = IOVisitor()
        visitor.visit(tree)

        self.assertEqual(len(visitor.services), 1)
        service = visitor.services[0]
        service_name = service['name']
        service_input = service['input']
        input_type = service_input['type']
        elements = service_input['elements']

        self.assertEqual(service_name, 'test.tuple.service')
        self.assertEqual(input_type, 'tuple')
        self.assertEqual(len(elements), 3)

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
        visitor = IOVisitor()
        visitor.visit(tree)

        self.assertEqual(len(visitor.services), 1)
        service = visitor.services[0]
        service_input = service['input']
        service_output = service['output']

        self.assertEqual(service_input['type'], 'model')
        self.assertEqual(service_input['model_name'], 'InputModel')
        self.assertEqual(service_output['type'], 'model')
        self.assertEqual(service_output['model_name'], 'OutputModel')

        self.assertEqual(len(visitor.models), 2)
        self.assertIn('InputModel', visitor.models)
        self.assertIn('OutputModel', visitor.models)

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

        scanner = IOScanner()
        result = scanner.scan_file(test_file)

        self.assertEqual(len(result['services']), 1)
        service = result['services'][0]
        service_name = service['name']
        service_input = service['input']
        service_output = service['output']

        self.assertEqual(service_name, 'test.channel.wsx.measurement')
        self.assertIsNone(service_input)
        self.assertIsNone(service_output)

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
            scanner = IOScanner()
            result = scanner.scan_file(temp_input)
            self.assertEqual(len(result['services']), 1)

            type_mapper = TypeMapper()
            generator = OpenAPIGenerator(type_mapper)

            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                temp_output = f.name

            generator.generate_openapi({'services': result['services'], 'models': result['models']}, temp_output)

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
