# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import inspect
import logging
from pathlib import Path
from typing import get_type_hints as typing_get_type_hints

# PyYAML
import yaml

# Zato
from zato.common.typing_ import any_, optional
from zato.openapi.type_converter import convert_type_to_schema, extract_model_fields
from zato.openapi.utils import extract_description_from_docstring, extract_path_from_service_name, determine_http_method_from_service
from zato.openapi.utils import find_services_and_models, generate_operation_id, generate_service_summary, import_module_from_path
from zato.openapi.utils import scan_directory_for_modules
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Scanner:
    """ Scans a directory for Zato service classes and model definitions to generate OpenAPI specifications.
    """
    def __init__(self, root_path:'str', base_service_class:'type'=Service, base_model_class:'type'=Model):
        self.root_path = Path(root_path)
        self.base_service_class = base_service_class
        self.base_model_class = base_model_class
        self.services = {}
        self.models = {}
        self.paths = {}
        self.components = {
            'schemas': {}
        }
        self.spec = {}

# ################################################################################################################################

    def scan_directory(self):
        """ Scans the root directory for Python files containing service and model definitions.
        """
        # Find all Python files
        py_files = scan_directory_for_modules(self.root_path)

        # Process each file
        for file_path in py_files:
            # Load the module
            module = import_module_from_path(file_path)
            if not module:
                logger.warning(f'Could not load module from {file_path}')
                continue

            # Extract services and models
            services, models = find_services_and_models(
                module,
                self.base_service_class,
                self.base_model_class
            )

            # Add to our collections
            self.services.update(services)
            self.models.update(models)

# ################################################################################################################################

    def parse_inline_input(self, input_def:'any_') -> 'list[dict]':
        """ Parses inline input definition (string or tuple of strings). """
        parameters = []

        if isinstance(input_def, str):
            # Single parameter
            input_params = [input_def]
        elif isinstance(input_def, tuple) and all(isinstance(item, str) for item in input_def):
            # Tuple of parameters
            input_params = input_def
        else:
            return parameters

        for param in input_params:
            required = True
            param_name = param

            # Check for optional parameter indicated by minus sign
            if param.startswith('-'):
                required = False
                param_name = param[1:]

            parameters.append({
                'name': param_name,
                'in': 'query',  # Default to query, can be overridden later
                'required': required,
                'schema': {
                    'type': 'string'  # Default type
                }
            })

        return parameters

# ################################################################################################################################

    def extract_model_schema(self, model_class):
        """ Extracts OpenAPI schema from a model class. """
        schema = {
            'type': 'object',
            'properties': {},
            'required': []
        }

        # Get type hints for the model
        type_hints = get_type_hints(model_class)

        # Use the helper to extract fields
        properties, required = extract_model_fields(model_class, type_hints)
        schema['properties'] = properties
        schema['required'] = required

        # If no required fields, remove the empty array
        if not schema['required']:
            del schema['required']

        return schema

# ################################################################################################################################

    def type_to_schema(self, field_type):
        """ Converts Python type to OpenAPI schema. """
        # Use the type converter helper function
        schema = convert_type_to_schema(field_type, self.is_model_class)

        # Register any referenced models
        if '$ref' in schema and schema['$ref'].startswith('#/components/schemas/'):
            model_name = schema['$ref'].split('/')[-1]
            if inspect.isclass(field_type) and model_name == field_type.__name__:
                self.models[model_name] = field_type

        return schema

# ################################################################################################################################

    def generate_path_from_service(self, service_class:'any_') -> 'optional[tuple[str, dict]]':
        """ Generates an OpenAPI path object from a service class. """
        if not hasattr(service_class, 'name'):
            return None

        service_name = service_class.name
        path = extract_path_from_service_name(service_name)
        http_method = determine_http_method_from_service(service_class)

        operation = {
            'operationId': generate_operation_id(service_name, http_method),
            'summary': generate_service_summary(service_class),
            'description': extract_description_from_docstring(service_class),
            'parameters': [],
            'responses': {
                '200': {
                    'description': 'Successful response'
                },
                '400': {
                    'description': 'Bad request'
                },
                '500': {
                    'description': 'Internal server error'
                }
            }
        }

        # Remove None values
        if not operation['description']:
            del operation['description']

        # Process input definition
        if hasattr(service_class, 'input'):
            input_def = service_class.input

            if isinstance(input_def, (str, tuple)):
                # Inline input definition
                operation['parameters'] = self.parse_inline_input(input_def)
            elif inspect.isclass(input_def) and self.is_model_class(input_def):
                # Model class input
                model_name = input_def.__name__
                self.models[model_name] = input_def

                operation['requestBody'] = {
                    'content': {
                        'application/yaml': {
                            'schema': {
                                '$ref': f'#/components/schemas/{model_name}'
                            }
                        }
                    },
                    'required': True
                }

        # Process output definition
        if hasattr(service_class, 'output'):
            output_def = service_class.output

            if inspect.isclass(output_def) and self.is_model_class(output_def):
                model_name = output_def.__name__
                self.models[model_name] = output_def

                operation['responses']['200']['content'] = {
                    'application/yaml': {
                        'schema': {
                            '$ref': f'#/components/schemas/{model_name}'
                        }
                    }
                }

        # Process model attribute (used by some adapter services)
        if hasattr(service_class, 'model'):
            model_def = service_class.model

            # Handle list of models
            if hasattr(model_def, '__origin__') and model_def.__origin__ is list and len(model_def.__args__) > 0:
                item_model = model_def.__args__[0]
                if inspect.isclass(item_model) and self.is_model_class(item_model):
                    model_name = item_model.__name__
                    self.models[model_name] = item_model

                    operation['responses']['200']['content'] = {
                        'application/yaml': {
                            'schema': {
                                'type': 'array',
                                'items': {
                                    '$ref': f'#/components/schemas/{model_name}'
                                }
                            }
                        }
                    }
            elif inspect.isclass(model_def) and self.is_model_class(model_def):
                model_name = model_def.__name__
                self.models[model_name] = model_def

                operation['responses']['200']['content'] = {
                    'application/yaml': {
                        'schema': {
                            '$ref': f'#/components/schemas/{model_name}'
                        }
                    }
                }

        return path, operation

# ################################################################################################################################

    def generate_spec(self, title:'str'='Zato API', version:'str'='1.0.0') -> 'dict':
        """ Generates the full OpenAPI specification. """
        # Scan for services and models
        self.scan_directory()

        # Generate paths
        for service_name, service_class in self.services.items():
            path_info = self.generate_path_from_service(service_class)
            if not path_info:
                continue

            path, operation = path_info
            http_method = determine_http_method_from_service(service_class).lower()

            # Initialize path dictionary if needed
            if path not in self.paths:
                self.paths[path] = {}

            # Add the operation under the appropriate HTTP method
            self.paths[path][http_method] = operation

        # Generate schemas from models
        for model_name, model_class in self.models.items():
            schema = self.extract_model_schema(model_class)
            if schema:
                self.components['schemas'][model_name] = schema

        # Construct the full specification
        self.spec = {
            'openapi': '3.0.0',
            'info': {
                'title': title,
                'version': version,
                'description': f'API specification for Zato services'
            },
            'paths': self.paths,
            'components': self.components
        }

        return self.spec

# ################################################################################################################################

    def to_yaml(self):
        """ Converts the OpenAPI specification to YAML format. """
        if not self.spec:
            self.generate_spec()

        return yaml.dump(self.spec, sort_keys=False)

# ################################################################################################################################

    def save_spec(self, output_path:'str', format_:'str'='yaml') -> 'None':
        """ Saves the OpenAPI specification to a YAML file. """
        if not self.spec:
            self.generate_spec()

        with open(output_path, 'w') as f:
            f.write(self.to_yaml())

# ################################################################################################################################
# ################################################################################################################################

def get_type_hints(cls):
    """ Gets type hints for a class, handling potential exceptions. """
    try:
        return typing_get_type_hints(cls)
    except (TypeError, NameError):
        # Fall back to __annotations__ if get_type_hints fails
        return getattr(cls, '__annotations__', {})

# ################################################################################################################################
# ################################################################################################################################

def scan_directory(directory_path, title='Zato API', version='1.0.0', output_path=None, format_='yaml'):
    """ Convenience function to scan a directory and generate an OpenAPI spec. """
    scanner = Scanner(directory_path)
    spec = scanner.generate_spec(title, version)

    if output_path:
        scanner.save_spec(output_path, format_)

    return spec

# ################################################################################################################################
# ################################################################################################################################
