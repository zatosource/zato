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
from zato.common.typing_ import any_, dict_, list_, optional
from zato.openapi.generator.ast_parser import find_services_and_models
from zato.openapi.generator.type_converter import convert_type_to_schema
from zato.openapi.generator.utils import extract_description_from_docstring, extract_path_from_service_name, determine_http_method_from_service
from zato.openapi.generator.utils import generate_operation_id, generate_service_summary, scan_directory_for_modules
from zato.server.service import Model, Service

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
        if isinstance(input_str, str):
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
                    schema_ref = {'$ref': f'#/components/schemas/{model_name}'}

                    # Add response schema
                    path_object[http_method]['responses']['200']['content'] = {
                        'application/json': {
                            'schema': schema_ref
                        }
                    }
        
        # Process model attribute (used by some adapter services)
        if 'model' in service_info['attrs']:
            model_name = service_info['attrs']['model']
            if isinstance(model_name, str):
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
        # Process all services
        for service_name, service_info in self.services.items():
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
