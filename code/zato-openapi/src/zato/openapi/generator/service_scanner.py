# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import ast
import os

# Zato
from zato.common.typing_ import dictlist, list_

# diskcache
from diskcache import Cache

# PyYAML
import yaml

# tqdm
from tqdm import tqdm

# ################################################################################################################################
# ################################################################################################################################

class ServiceVisitor(ast.NodeVisitor):
    """ AST visitor that finds services in Python files.
    """
    def __init__(self) -> 'None':
        self.services = []
        self.current_class = None
        self.is_service = False
        self.name = None
        self.input = None
        self.output = None
        self.handle_method_exists = False

    def visit_ClassDef(self, node) -> 'None':
        """ Visit class definitions to identify services.
        """
        prev_class = self.current_class
        self.current_class = node.name
        self.is_service = False
        self.name = None
        self.input = None
        self.output = None
        self.handle_method_exists = False

        # Check if the class inherits from Service or RESTAdapter
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id in ('Service', 'RESTAdapter'):
                self.is_service = True
                break

        # Visit all class contents
        for item in node.body:
            self.visit(item)

        # If this is a service, collect its information
        if self.is_service and self.name:
            service_info = {
                'name': self.name,
                'class_name': self.current_class,
                'input': self.input,
                'output': self.output,
                'has_handle_method': self.handle_method_exists
            }
            self.services.append(service_info)

        self.current_class = prev_class

    def visit_Assign(self, node) -> 'None':
        """ Visit assignments to find service attributes like name, input, output.
        """
        if not self.current_class or not self.is_service:
            return

        # Check for name, input, and output assignments
        for target in node.targets:
            if isinstance(target, ast.Name):
                # Check for name attribute
                if target.id == 'name' and isinstance(node.value, ast.Constant):
                    self.name = node.value.value

                # Check for input attribute
                elif target.id == 'input':
                    if isinstance(node.value, ast.Name):
                        # Input as a model class
                        self.input = node.value.id
                    elif isinstance(node.value, ast.Constant):
                        # Input as a string
                        self.input = node.value.value
                    elif isinstance(node.value, ast.Tuple):
                        # Input as a tuple of strings
                        elts = []
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant):
                                elts.append(elt.value)
                        if elts:
                            self.input = tuple(elts)

                # Check for output attribute
                elif target.id == 'output' and isinstance(node.value, ast.Name):
                    self.output = node.value.id

    def visit_FunctionDef(self, node) -> 'None':
        """ Visit function definitions to find handle() method.
        """
        if self.current_class and self.is_service and node.name == 'handle':
            self.handle_method_exists = True

# ################################################################################################################################
# ################################################################################################################################

class ServiceScanner:
    """ Scans directories for Zato services and extracts their information.
    """
    def __init__(self, cache_dir:'str'='/tmp/zato_service_scanner_cache'):
        self.cache = Cache(cache_dir)

    def is_python_file(self, file_path:'str') -> 'bool':
        """ Check if a file is a Python file.
        """
        return file_path.endswith('.py')

    def get_file_mtime(self, file_path:'str') -> 'float':
        """ Get the modification time of a file.
        """
        return os.path.getmtime(file_path)

    def scan_file(self, file_path:'str') -> 'dictlist':
        """ Scan a single Python file for services.
        """
        # Check cache first
        mtime = self.get_file_mtime(file_path)
        cache_key = f"{file_path}:{mtime}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        services = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=file_path)
                visitor = ServiceVisitor()
                visitor.visit(tree)
                services = visitor.services

            # Store in cache
            self.cache[cache_key] = services
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

        return services

    def scan_directory(self, directory:'str') -> 'dictlist':
        """ Recursively scan a directory for services.
        """
        all_services = []
        py_files = []

        # Find all Python files in the directory
        for root, _, files in os.walk(directory):
            for file in files:
                if self.is_python_file(file):
                    py_files.append(os.path.join(root, file))

        # Scan each Python file with progress bar
        for file_path in tqdm(py_files, desc=f"Scanning {directory}"):
            file_services = self.scan_file(file_path)
            all_services.extend(file_services)

        return all_services

    def scan_directories(self, directories:'list_[str]') -> 'dictlist':
        """ Scan multiple directories for services.
        """
        all_services = []
        for directory in directories:
            services = self.scan_directory(directory)
            all_services.extend(services)
        return all_services

    def generate_openapi(self, services:'dictlist', output_file:'str') -> 'None':
        """ Generate an OpenAPI specification from the scanned services.
        """
        openapi = {
            'openapi': '3.0.0',
            'info': {
                'title': 'Zato API',
                'description': 'API generated from Zato services',
                'version': '1.0.0'
            },
            'paths': {}
        }

        # Create paths for each service
        for service in services:
            service_name = service['name']
            if not service_name:
                continue

            # Create path from service name
            path = f"/{service_name.replace('.', '/')}"
            openapi['paths'][path] = {
                'post': {
                    'summary': f"Invoke {service_name}",
                    'description': f"Invoke the {service['class_name']} service",
                    'operationId': service_name.replace('.', '_'),
                    'responses': {
                        '200': {
                            'description': 'Successful response',
                        }
                    }
                }
            }

            # Add request body if input is defined
            if service['input']:
                openapi['paths'][path]['post']['requestBody'] = {
                    'description': 'Input parameters',
                    'required': True,
                    'content': {
                        'application/json': {}
                    }
                }

                # Handle different input types
                if isinstance(service['input'], str):
                    # Single string input
                    openapi['paths'][path]['post']['requestBody']['content']['application/json']['schema'] = {
                        'type': 'object',
                        'properties': {
                            service['input']: {
                                'type': 'string'
                            }
                        }
                    }
                elif isinstance(service['input'], tuple):
                    # Tuple of string inputs
                    properties = {}
                    for input_param in service['input']:
                        properties[input_param] = {
                            'type': 'string'
                        }
                    openapi['paths'][path]['post']['requestBody']['content']['application/json']['schema'] = {
                        'type': 'object',
                        'properties': properties
                    }
                else:
                    # Reference to a model class
                    # We just note it's a model reference since we don't have the model definition here
                    openapi['paths'][path]['post']['requestBody']['content']['application/json']['schema'] = {
                        'type': 'object',
                        'description': f"Model: {service['input']}"
                    }

            # Add response schema if output is defined
            if service['output']:
                openapi['paths'][path]['post']['responses']['200']['content'] = {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'description': f"Model: {service['output']}"
                        }
                    }
                }

        # Write the OpenAPI specification to a file
        with open(output_file, 'w') as f:
            yaml.dump(openapi, f, sort_keys=False)

# ################################################################################################################################
# ################################################################################################################################

def scan_services(directories:'list_[str]', output_file:'str') -> 'None':
    """ Scan directories for services and generate an OpenAPI specification.
    """
    scanner = ServiceScanner()
    services = scanner.scan_directories(directories)
    scanner.generate_openapi(services, output_file)
    print(f"Found {len(services)} services. OpenAPI specification saved to {output_file}")

# ################################################################################################################################
# ################################################################################################################################
