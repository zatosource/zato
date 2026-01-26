# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import logging

# PyYAML
import yaml

# ################################################################################################################################
# ################################################################################################################################

# Logger for this module
logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class TypeConversionError(Exception):
    """ Raised when a type cannot be converted to an OpenAPI type.
    """
    pass

# ################################################################################################################################
# ################################################################################################################################

class OpenAPIGenerator:
    """ Generates OpenAPI specifications from scan results.
    """
    def __init__(self, type_mapper):
        self.type_mapper = type_mapper

    def _create_request_schema(self, service_input, models):
        """ Create a schema for the request body.
        """
        if not service_input:
            return None

        # Handle model-based input
        if service_input['type'] == 'model':
            model_name = service_input['model_name']
            try:
                return self.type_mapper.map_type(model_name, models)
            except TypeConversionError as e:
                error_msg = f'Could not map input model: {e}'
                logger.error(error_msg)
                raise TypeConversionError(error_msg)

        # Handle string input
        elif service_input['type'] == 'string':
            properties = {}
            required = []

            properties[service_input['name']] = {'type': 'string'}
            if service_input.get('required', True):
                required.append(service_input['name'])

            schema = {
                'type': 'object',
                'properties': properties
            }
            if required:
                schema['required'] = required

            return schema

        # Handle tuple input
        elif service_input['type'] == 'tuple':
            properties = {}
            required = []

            for element in service_input['elements']:
                properties[element['name']] = {'type': 'string'}
                if element.get('required', True):
                    required.append(element['name'])

            schema = {
                'type': 'object',
                'properties': properties
            }
            if required:
                schema['required'] = required

            return schema

        # Handle container input like list_[Model]
        elif service_input['type'] == 'container':
            container_type = service_input['container_type']
            element_type = service_input['element_type']

            if container_type in ('list_', 'List'):
                try:
                    items_schema = self.type_mapper.map_type(element_type, models)
                    return {
                        'type': 'array',
                        'items': items_schema
                    }
                except TypeConversionError as e:
                    logger.warning(f'Could not map container type: {e}')
                    raise

        # If we can't map the input, raise an exception
        raise TypeConversionError(f'Cannot map service input {service_input["type"]} to OpenAPI schema. Add handling for this input type in _create_request_schema method')

    def _create_response_schema(self, service_output, models):
        """ Create a schema for the response body.
        """
        if not service_output:
            return None

        # Handle model-based output
        if service_output['type'] == 'model':
            model_name = service_output['model_name']
            try:
                return self.type_mapper.map_type(model_name, models)
            except TypeConversionError as e:
                logger.warning(f'Could not map output model: {e}')
                raise

        # Handle tuple output
        elif service_output['type'] == 'tuple':
            properties = {}
            required = []

            for element in service_output['elements']:
                properties[element['name']] = {'type': 'string'}
                if element.get('required', True):
                    required.append(element['name'])

            schema = {
                'type': 'object',
                'properties': properties
            }
            if required:
                schema['required'] = required

            return schema

        # Handle container output like list_[Model]
        elif service_output['type'] == 'container':
            container_type = service_output['container_type']
            element_type = service_output['element_type']

            if container_type in ('list_', 'List'):
                try:
                    items_schema = self.type_mapper.map_type(element_type, models)
                    return {
                        'type': 'array',
                        'items': items_schema
                    }
                except TypeConversionError as e:
                    logger.warning(f'Could not map container type: {e}')
                    raise

        # If we can't map the output, raise an exception
        raise TypeConversionError(f'Cannot map service output {service_output["type"]} to OpenAPI schema. Add handling for this output type in _create_response_schema method')

    def generate_openapi(self, scan_results, output_file):
        """ Generate an OpenAPI specification from the scanned services and models.
        """
        services = scan_results['services']
        models = scan_results['models']

        openapi = {
            'openapi': '3.1.0',
            'info': {
                'title': 'API Specification',
                'description': '',
                'version': '1.0.0'
            },
            'paths': {},
            'components': {
                'schemas': {}
            }
        }

        # Create paths for each service
        for service in services:
            service_name = service.get('name')
            if not service_name:
                continue

            # Use url_path and http_method from DB-driven scan if present
            path = service.get('url_path') or f'/{service_name.replace(".", "/")}'
            http_method = service.get('http_method', 'post').lower()
            operation = {
                'summary': f'Invoke {service_name}',
                'description': f'Invoke the {service.get('class_name', '')} service',
                'operationId': service_name.replace('.', '_').replace('-', '_'),
                'tags': ['API Endpoints'],
                'responses': {
                    '200': {
                        'description': 'Successful response'
                    },
                    '400': {
                        'description': 'Bad Request'
                    },
                    '500': {
                        'description': 'Internal Server Error'
                    }
                }
            }

            # Add request body if input is defined
            if service.get('input'):
                try:
                    request_schema = self._create_request_schema(service['input'], models)
                    if request_schema:
                        operation['requestBody'] = {
                            'description': 'Input parameters',
                            'required': True,
                            'content': {
                                'application/json': {
                                    'schema': request_schema
                                }
                            }
                        }
                except TypeConversionError as e:
                    file_path = service.get('file_path', 'unknown_file')
                    logger.error(f'Skipping request body for service "{service_name}" in file {file_path}: {e}')
                    logger.error(f'Service details: {service}')

            # Add response schema if output is defined
            if service.get('output'):
                try:
                    response_schema = self._create_response_schema(service['output'], models)
                    if response_schema:
                        operation['responses']['200']['content'] = {
                            'application/json': {
                                'schema': response_schema
                            }
                        }
                except TypeConversionError as e:
                    file_path = service.get('file_path', 'unknown_file')
                    logger.error(f'Skipping response schema for service "{service_name}" in file {file_path}: {e}')

            # Add the operation to the path
            if path not in openapi['paths']:
                openapi['paths'][path] = {}

            openapi['paths'][path][http_method] = operation

        # Add schema components
        schema_components = self.type_mapper.get_schema_components()
        if schema_components:
            openapi['components']['schemas'].update(schema_components)

        # Write the OpenAPI specification to a file
        with open(output_file, 'w') as f:
            yaml.dump(openapi, f, sort_keys=False)

# ################################################################################################################################
# ################################################################################################################################
