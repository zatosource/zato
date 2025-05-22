# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import logging
from pathlib import Path

# PyYAML
import yaml

# Zato
from zato.common.typing_ import optional
from zato.openapi.generator.ast_parser import find_services_and_models
from zato.openapi.generator.type_converter import convert_type_to_schema
from zato.openapi.generator.utils import extract_path_from_service_name, determine_http_method_from_service
from zato.openapi.generator.utils import generate_operation_id, generate_service_summary, scan_directory_for_modules

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Scanner:
    """ Scans a directory for Zato service classes and model definitions to generate OpenAPI specifications.
    """
    def __init__(self, root_path:'str'):
        """ Initialize the scanner with a root directory path.
        """
        self.root_path = Path(root_path)
        self.services = {}
        self.models = {}
        self.paths = {}
        self.components = {'schemas': {}}
        self.spec = {}

        # Scan the directory
        self.scan_directory()

# ################################################################################################################################

    def add_directory(self, directory_path:'str') -> 'None':
        """ Adds an additional directory to scan for services and models.
        """
        # Store the current root path
        original_path = self.root_path

        # Set the new path temporarily
        self.root_path = Path(directory_path)

        # Scan the directory
        self.scan_directory()

        # Restore the original path
        self.root_path = original_path

    def scan_directory(self):
        """ Scans the root directory for Python files containing service and model definitions.
        """
        # Find all Python files
        py_files = scan_directory_for_modules(self.root_path)

        # Process each file using AST parsing
        for file_path in py_files:
            # Extract services and models using AST
            services, models = find_services_and_models(
                file_path,
                ['Service'],  # Base service class names to look for
                ['Model']    # Base model class names to look for
            )

            # Add to our collections
            for service_info in services:
                service_name = service_info['name']
                self.services[service_name] = service_info

            for model_info in models:
                model_name = model_info['name']
                self.models[model_name] = model_info

# ################################################################################################################################

    def parse_inline_input(self, input_str:'str') -> 'list[dict]':
        """ Parses an inline input string into parameters.
        """
        parameters = []

        # Simple parsing for string-based parameters
        parts = input_str.split(',')
        for part in parts:
            part = part.strip()
            if part:
                param = {
                    'name': part,
                    'in': 'query',
                    'schema': {
                        'type': 'string'
                    }
                }
                parameters.append(param)

        return parameters

# ################################################################################################################################

    def generate_path_from_service(self, service_info:'dict') -> 'optional[tuple[str, dict]]':
        """ Generates an OpenAPI path object from a service info dict (parsed by AST).
        """
        service_name = service_info['attrs'].get('name')
        if not service_name:
            return None

        path = extract_path_from_service_name(service_name)

        if not path:
            # Skip services without a proper path
            return None

        http_method = determine_http_method_from_service(service_name)
        operation_id = generate_operation_id(service_name)
        summary = generate_service_summary(service_name)

        # Use class name as fallback description if no docstring
        description = service_info.get('name', 'Service')

        # Initialize the path object
        path_object = {
            http_method: {
                'operationId': operation_id,
                'summary': summary,
                'description': description,
                'responses': {
                    '200': {
                        'description': 'Successful response',
                    }
                }
            }
        }

        # Add request body or parameters
        self._add_request_to_path(path_object, http_method, service_info)

        # Add response schema
        self._add_response_to_path(path_object, http_method, service_info)

        return path, path_object

# ################################################################################################################################

    def _add_request_to_path(self, path_object:'dict', http_method:'str', service_info:'dict') -> 'None':
        """ Adds request body or parameters to a path object based on service input definition.
        """
        # Add request body or parameters based on input definition
        if 'input' in service_info['attrs']:
            input_def = service_info['attrs']['input']

            if isinstance(input_def, str):
                # Inline input definition (parameter string)
                path_object[http_method]['parameters'] = self.parse_inline_input(input_def)

            elif isinstance(input_def, dict):
                # Dictionary model reference
                model_name = input_def.get('model')
                if model_name and isinstance(model_name, str):
                    # Ensure the model exists in our schemas
                    if model_name not in self.components['schemas']:
                        # If model was referenced but not found, create a placeholder schema
                        self.components['schemas'][model_name] = {
                            'type': 'object',
                            'description': f'Schema for {model_name} (auto-generated)',
                            'properties': {}
                        }

                    schema_ref = {'$ref': f'#/components/schemas/{model_name}'}

                    # Add request body
                    path_object[http_method]['requestBody'] = {
                        'required': True,
                        'content': {
                            'application/json': {
                                'schema': schema_ref
                            }
                        }
                    }

            # Handle when input is a direct reference to a model class
            elif isinstance(input_def, str) and input_def in self.models:
                model_name = input_def
                schema_ref = {'$ref': f'#/components/schemas/{model_name}'}

                # Add request body
                path_object[http_method]['requestBody'] = {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': schema_ref
                        }
                    }
                }

        # Handle SimpleIO-style input definitions
        elif 'input_required' in service_info or 'input_optional' in service_info:
            # Create a schema for the input
            schema = {
                'type': 'object',
                'properties': {},
                'required': []
            }

            # Process required input parameters
            if 'input_required' in service_info and service_info['input_required']:
                for param in service_info['input_required']:
                    if isinstance(param, str):
                        schema['properties'][param] = {'type': 'string'}
                        schema['required'].append(param)
                    elif isinstance(param, dict) and 'type' in param:  # Function call like Integer('port')
                        param_name = param['args'][0] if param['args'] else 'unknown'
                        param_type = param['type'].lower()

                        # Map Zato types to OpenAPI types
                        if param_type in ('integer', 'int', 'intsio'):
                            schema['properties'][param_name] = {'type': 'integer'}
                        elif param_type in ('boolean', 'bool', 'boolsio'):
                            schema['properties'][param_name] = {'type': 'boolean'}
                        elif param_type == 'float':
                            schema['properties'][param_name] = {'type': 'number', 'format': 'float'}
                        elif param_type == 'asis':
                            # Handle AsIs parameters
                            schema['properties'][param_name] = {'type': 'string'}
                        else:
                            schema['properties'][param_name] = {'type': 'string'}

                        schema['required'].append(param_name)

            # Process optional input parameters
            if 'input_optional' in service_info and service_info['input_optional']:
                for param in service_info['input_optional']:
                    if isinstance(param, str):
                        schema['properties'][param] = {'type': 'string'}
                    elif isinstance(param, dict) and 'type' in param:  # Function call like Integer('port')
                        param_name = param['args'][0] if param['args'] else 'unknown'
                        param_type = param['type'].lower()

                        # Map Zato types to OpenAPI types
                        if param_type in ('integer', 'int', 'intsio'):
                            schema['properties'][param_name] = {'type': 'integer'}
                        elif param_type in ('boolean', 'bool', 'boolsio'):
                            schema['properties'][param_name] = {'type': 'boolean'}
                        elif param_type == 'float':
                            schema['properties'][param_name] = {'type': 'number', 'format': 'float'}
                        elif param_type == 'asis':
                            # Handle AsIs parameters
                            schema['properties'][param_name] = {'type': 'string'}
                        else:
                            schema['properties'][param_name] = {'type': 'string'}

            # If we have any properties, add the request body
            if schema['properties']:
                # Generate a unique name for this schema
                service_name = service_info['name'] if 'name' in service_info else 'UnknownService'
                schema_name = f'{service_name}Input'

                # Add the schema to components
                self.components['schemas'][schema_name] = schema

                # Add request body
                path_object[http_method]['requestBody'] = {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {'$ref': f'#/components/schemas/{schema_name}'}
                        }
                    }
                }

# ################################################################################################################################

    def _add_response_to_path(self, path_object:'dict', http_method:'str', service_info:'dict') -> 'None':
        """ Adds response schema to a path object based on service output definition.
        """
        # Process output definition
        if 'output' in service_info['attrs']:
            output_def = service_info['attrs']['output']

            if isinstance(output_def, dict):
                # Dictionary model reference
                model_name = output_def.get('model')
                if model_name and isinstance(model_name, str):
                    # Ensure the model exists in our schemas
                    if model_name not in self.components['schemas']:
                        # If model was referenced but not found, create a placeholder schema
                        self.components['schemas'][model_name] = {
                            'type': 'object',
                            'description': f'Schema for {model_name} (auto-generated)',
                            'properties': {}
                        }

                    schema_ref = {'$ref': f'#/components/schemas/{model_name}'}

                    # Add response schema
                    path_object[http_method]['responses']['200']['content'] = {
                        'application/json': {
                            'schema': schema_ref
                        }
                    }

            # Handle when output is a direct reference to a model class
            elif isinstance(output_def, str) and output_def in self.models:
                model_name = output_def
                schema_ref = {'$ref': f'#/components/schemas/{model_name}'}

                # Add response schema
                path_object[http_method]['responses']['200']['content'] = {
                    'application/json': {
                        'schema': schema_ref
                    }
                }

        # Handle SimpleIO-style output definitions
        elif 'output_required' in service_info or 'output_optional' in service_info:
            # Create a schema for the output
            schema = {
                'type': 'object',
                'properties': {},
                'required': []
            }

            # Process required output parameters
            if 'output_required' in service_info and service_info['output_required']:
                for param in service_info['output_required']:
                    if isinstance(param, str):
                        schema['properties'][param] = {'type': 'string'}
                        schema['required'].append(param)
                    elif isinstance(param, dict) and 'type' in param:  # Function call like Integer('port')
                        param_name = param['args'][0] if param['args'] else 'unknown'
                        param_type = param['type'].lower()

                        # Map Zato types to OpenAPI types
                        if param_type in ('integer', 'int', 'intsio'):
                            schema['properties'][param_name] = {'type': 'integer'}
                        elif param_type in ('boolean', 'bool', 'boolsio'):
                            schema['properties'][param_name] = {'type': 'boolean'}
                        elif param_type == 'float':
                            schema['properties'][param_name] = {'type': 'number', 'format': 'float'}
                        elif param_type == 'asis':
                            # Handle AsIs parameters
                            schema['properties'][param_name] = {'type': 'string'}
                        else:
                            schema['properties'][param_name] = {'type': 'string'}

                        schema['required'].append(param_name)

            # Process optional output parameters
            if 'output_optional' in service_info and service_info['output_optional']:
                for param in service_info['output_optional']:
                    if isinstance(param, str):
                        schema['properties'][param] = {'type': 'string'}
                    elif isinstance(param, dict) and 'type' in param:  # Function call like Integer('port')
                        param_name = param['args'][0] if param['args'] else 'unknown'
                        param_type = param['type'].lower()

                        # Map Zato types to OpenAPI types
                        if param_type in ('integer', 'int', 'intsio'):
                            schema['properties'][param_name] = {'type': 'integer'}
                        elif param_type in ('boolean', 'bool', 'boolsio'):
                            schema['properties'][param_name] = {'type': 'boolean'}
                        elif param_type == 'float':
                            schema['properties'][param_name] = {'type': 'number', 'format': 'float'}
                        elif param_type == 'asis':
                            # Handle AsIs parameters
                            schema['properties'][param_name] = {'type': 'string'}
                        else:
                            schema['properties'][param_name] = {'type': 'string'}

            # If we have any properties, add the response schema
            if schema['properties']:
                # Generate a unique name for this schema
                service_name = service_info['name'] if 'name' in service_info else 'UnknownService'
                schema_name = f'{service_name}Output'

                # Add the schema to components
                self.components['schemas'][schema_name] = schema

                # Add response schema
                path_object[http_method]['responses']['200']['content'] = {
                    'application/json': {
                        'schema': {'$ref': f'#/components/schemas/{schema_name}'}
                    }
                }

        # Process model attribute (used by some adapter services)
        if 'model' in service_info['attrs']:
            model_name = service_info['attrs']['model']
            if isinstance(model_name, str):
                # Ensure the model exists in our schemas
                if model_name not in self.components['schemas']:
                    # If model was referenced but not found, create a placeholder schema
                    self.components['schemas'][model_name] = {
                        'type': 'object',
                        'description': f'Schema for {model_name} (auto-generated)',
                        'properties': {}
                    }

                schema_ref = {'$ref': f'#/components/schemas/{model_name}'}

                # Add response schema if not already added
                if 'content' not in path_object[http_method]['responses']['200']:
                    path_object[http_method]['responses']['200']['content'] = {
                        'application/json': {
                            'schema': schema_ref
                        }
                    }

# ################################################################################################################################

    def generate_spec(self, title:'str'='API Spec', version:'str'='1.0.0') -> 'dict':
        """ Generates an OpenAPI specification from scanned services and models.
        """
        # Process all models first to ensure they're available for services
        for model_name, model_info in self.models.items():
            schema = self.extract_model_schema(model_info)
            if schema:
                self.components['schemas'][model_name] = schema

        # Process all services
        for service_info in self.services.values():
            path_info = self.generate_path_from_service(service_info)
            if path_info:
                path, path_object = path_info
                self.paths[path] = path_object

        # Build the final spec
        self.spec = {
            'openapi': '3.0.0',
            'info': {
                'title': title,
                'version': version
            },
            'paths': self.paths
        }

        # Add components if we have any
        if self.components['schemas']:
            self.spec['components'] = self.components

        return self.spec

# ################################################################################################################################

    def extract_model_schema(self, model_info:'dict') -> 'optional[dict]':
        """ Extract OpenAPI schema from a model class information.
        """
        # If there are no annotations, we can't extract a schema
        if not model_info['annotations']:
            return None

        properties = {}
        required = []

        # Process each annotation as a property
        for field_name, field_type in model_info['annotations'].items():
            # Convert Python type to OpenAPI schema
            prop_schema = convert_type_to_schema(field_type)

            if prop_schema:
                properties[field_name] = prop_schema

                # Assume all fields are required unless they have a default value
                if field_name not in model_info.get('attrs', {}):
                    required.append(field_name)

        if not properties:
            return None

        # Create the schema
        schema = {
            'type': 'object',
            'properties': properties
        }

        # Add required fields if any
        if required:
            schema['required'] = required

        return schema

# ################################################################################################################################

    def to_yaml(self) -> 'str':
        """ Converts the OpenAPI specification to YAML format.
        """
        return yaml.dump(self.spec, default_flow_style=False, sort_keys=False)

# ################################################################################################################################

    def save_to_file(self, file_path:'str') -> 'None':
        """ Saves the OpenAPI specification to a file.
        """
        with open(file_path, 'w') as f:
            yaml.dump(self.spec, f, default_flow_style=False, sort_keys=False)

# ################################################################################################################################
# ################################################################################################################################
