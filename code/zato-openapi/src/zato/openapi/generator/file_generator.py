# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import argparse
import ast
import logging
import os
import sys

# PyYAML
import yaml

# ################################################################################################################################
# ################################################################################################################################

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class FileIOVisitor(ast.NodeVisitor):
    """ AST visitor that extracts service definitions from Python files.
    """
    def __init__(self):
        self.services = []
        self.models = {}
        self.current_class = None
        self.is_service = False
        self.is_model = False
        self.service_name = None
        self.service_input = None
        self.service_output = None
        self.model_fields = {}

    def visit_ClassDef(self, node):
        prev_class = self.current_class
        prev_is_service = self.is_service
        prev_is_model = self.is_model
        prev_model_fields = self.model_fields

        self.current_class = node.name
        self.is_service = False
        self.is_model = False
        self.service_name = None
        self.service_input = None
        self.service_output = None
        self.model_fields = {}

        # Check base classes for Service, RESTAdapter, WSXAdapter, etc.
        for base in node.bases:
            base_name = None
            if isinstance(base, ast.Name):
                base_name = base.id
            elif isinstance(base, ast.Attribute):
                base_name = base.attr

            if base_name in ('Service', 'RESTAdapter', 'WSXAdapter'):
                self.is_service = True
                break
            elif base_name == 'Model':
                self.is_model = True
                break

        for item in node.body:
            self.visit(item)

        if self.is_service and self.service_name:
            service_info = {
                'name': self.service_name,
                'class_name': self.current_class,
                'input': self.service_input,
                'output': self.service_output,
            }
            self.services.append(service_info)

        if self.is_model and self.model_fields:
            self.models[self.current_class] = self.model_fields

        self.current_class = prev_class
        self.is_service = prev_is_service
        self.is_model = prev_is_model
        self.model_fields = prev_model_fields

    def visit_Assign(self, node):
        if not self.current_class:
            return

        if self.is_service:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if target.id == 'name' and isinstance(node.value, ast.Constant):
                        self.service_name = node.value.value

                    elif target.id == 'input':
                        self.service_input = self._parse_io_value(node.value)

                    elif target.id == 'output':
                        self.service_output = self._parse_io_value(node.value)

    def visit_AnnAssign(self, node):
        if not self.current_class or not self.is_model:
            return

        if isinstance(node.target, ast.Name):
            field_name = node.target.id
            field_type = self._parse_annotation(node.annotation)
            field_default = None

            if node.value:
                if isinstance(node.value, ast.Constant):
                    field_default = node.value.value

            self.model_fields[field_name] = {
                'type': field_type,
                'default': field_default,
                'required': field_default is None
            }

    def _parse_io_value(self, node):
        if isinstance(node, ast.Name):
            return {'type': 'model', 'model_name': node.id}
        elif isinstance(node, ast.Constant):
            return {'type': 'string', 'name': node.value}
        elif isinstance(node, ast.Tuple):
            elements = []
            for elt in node.elts:
                if isinstance(elt, ast.Constant):
                    param_value = elt.value
                    if param_value.startswith('-'):
                        elements.append({'name': param_value[1:], 'required': False})
                    else:
                        elements.append({'name': param_value, 'required': True})
            return {'type': 'tuple', 'elements': elements}
        elif isinstance(node, ast.Subscript):
            container = self._get_name(node.value)
            element = self._get_name(node.slice)
            return {'type': 'container', 'container_type': container, 'element_type': element}
        return None

    def _parse_annotation(self, annotation):
        if isinstance(annotation, ast.Name):
            return annotation.id
        if isinstance(annotation, ast.Subscript):
            container = self._get_name(annotation.value)
            element = self._get_name(annotation.slice)
            if container in ('list_', 'List'):
                return {'container': 'list', 'element_type': element}
            if container in ('optional', 'Optional'):
                return {'type': element, 'optional': True}
        return 'object'

    def _get_name(self, node):
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Constant):
            return node.value
        return 'object'

# ################################################################################################################################
# ################################################################################################################################

class FileOpenAPIGenerator:
    """ Generates OpenAPI from scanned file results.
    """

    BASIC_TYPES = {
        'str': {'type': 'string'},
        'str_': {'type': 'string'},
        'int': {'type': 'integer'},
        'float': {'type': 'number'},
        'bool': {'type': 'boolean'},
        'bytes': {'type': 'string', 'format': 'binary'},
        'dict_': {'type': 'object'},
        'object': {'type': 'object'},
    }

    def __init__(self):
        self.schema_components = {}

    def map_type(self, type_info, models):
        if isinstance(type_info, str):
            if type_info in self.BASIC_TYPES:
                return self.BASIC_TYPES[type_info]
            if type_info in models:
                self._register_model(type_info, models)
                return {'$ref': f'#/components/schemas/{type_info}'}
            return {'type': 'object'}

        if isinstance(type_info, dict):
            if type_info.get('container') == 'list':
                return {
                    'type': 'array',
                    'items': self.map_type(type_info.get('element_type', 'object'), models)
                }
            if type_info.get('optional'):
                mapped = self.map_type(type_info.get('type', 'object'), models)
                mapped['nullable'] = True
                return mapped

        return {'type': 'object'}

    def _register_model(self, model_name, models):
        if model_name in self.schema_components:
            return

        model_def = models.get(model_name, {})
        properties = {}
        required = []

        for field_name, field_info in model_def.items():
            field_type = field_info.get('type', 'object')
            properties[field_name] = self.map_type(field_type, models)
            if field_info.get('required', True):
                required.append(field_name)

        schema = {'type': 'object', 'properties': properties}
        if required:
            schema['required'] = required

        self.schema_components[model_name] = schema

    def create_request_schema(self, service_input, models):
        if not service_input:
            return {'type': 'object', 'additionalProperties': True}

        input_type = service_input.get('type')

        if input_type == 'model':
            return self.map_type(service_input['model_name'], models)

        if input_type == 'string':
            return {
                'type': 'object',
                'properties': {service_input['name']: {'type': 'string'}},
                'required': [service_input['name']]
            }

        if input_type == 'tuple':
            properties = {}
            required = []
            for elem in service_input.get('elements', []):
                properties[elem['name']] = {'type': 'string'}
                if elem.get('required', True):
                    required.append(elem['name'])
            schema = {'type': 'object', 'properties': properties}
            if required:
                schema['required'] = required
            return schema

        if input_type == 'container':
            return {
                'type': 'array',
                'items': self.map_type(service_input.get('element_type', 'object'), models)
            }

        return {'type': 'object', 'additionalProperties': True}

    def create_response_schema(self, service_output, models):
        if not service_output:
            return {'type': 'object', 'additionalProperties': True}

        output_type = service_output.get('type')

        if output_type == 'model':
            return self.map_type(service_output['model_name'], models)

        if output_type == 'container':
            return {
                'type': 'array',
                'items': self.map_type(service_output.get('element_type', 'object'), models)
            }

        return {'type': 'object', 'additionalProperties': True}

    def generate(self, services, models, title='API'):
        openapi = {
            'openapi': '3.1.0',
            'info': {
                'title': title,
                'version': '1.0.0'
            },
            'paths': {},
            'components': {'schemas': {}}
        }

        for service in services:
            service_name = service.get('name')
            if not service_name:
                continue

            path = '/' + service_name.replace('.', '/')
            operation_id = service_name.replace('.', '_').replace('-', '_')

            request_schema = self.create_request_schema(service.get('input'), models)
            response_schema = self.create_response_schema(service.get('output'), models)

            operation = {
                'summary': f'{service.get("class_name", service_name)}',
                'operationId': operation_id,
                'requestBody': {
                    'required': True,
                    'content': {
                        'application/json': {'schema': request_schema}
                    }
                },
                'responses': {
                    '200': {
                        'description': 'OK',
                        'content': {
                            'application/json': {'schema': response_schema}
                        }
                    }
                }
            }

            openapi['paths'][path] = {'post': operation}

        if self.schema_components:
            openapi['components']['schemas'] = self.schema_components

        return openapi

# ################################################################################################################################
# ################################################################################################################################

def scan_file(file_path):
    """ Scan a Python file for services and models.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read(), filename=file_path)

    visitor = FileIOVisitor()
    visitor.visit(tree)

    return {
        'services': visitor.services,
        'models': visitor.models
    }

# ################################################################################################################################
# ################################################################################################################################

def scan_files(file_paths):
    """ Scan multiple files.
    """
    all_services = []
    all_models = {}

    for file_path in file_paths:
        if not os.path.isfile(file_path):
            logger.warning(f'File not found: {file_path}')
            continue

        result = scan_file(file_path)
        all_services.extend(result['services'])
        all_models.update(result['models'])

    return {'services': all_services, 'models': all_models}

# ################################################################################################################################
# ################################################################################################################################

def main():
    parser = argparse.ArgumentParser(description='Generate OpenAPI from Zato service files')
    parser.add_argument('files', nargs='+', help='Python files to scan')
    parser.add_argument('-o', '--output', default='openapi.yaml', help='Output file (default: openapi.yaml)')
    parser.add_argument('-t', '--title', default='API', help='API title')

    args = parser.parse_args()

    scan_result = scan_files(args.files)

    if not scan_result['services']:
        logger.error('No services found in the provided files')
        sys.exit(1)

    generator = FileOpenAPIGenerator()
    openapi = generator.generate(scan_result['services'], scan_result['models'], args.title)

    with open(args.output, 'w') as f:
        yaml.dump(openapi, f, sort_keys=False, allow_unicode=True)

    logger.info(f'Generated {args.output} with {len(scan_result["services"])} service(s)')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()
