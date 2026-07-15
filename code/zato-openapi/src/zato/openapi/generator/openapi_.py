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

if 0:
    from zato.common.typing_ import any_, anydict, dictlist
    any_ = any_
    anydict = anydict
    dictlist = dictlist

# ################################################################################################################################
# ################################################################################################################################

# Logger for this module
logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Services without typed input or output are documented with this schema - any JSON object is accepted or returned.
_any_object_schema = {'type': 'object', 'additionalProperties': True}

# The tag for services whose names have no dotted prefix to derive a group from
_default_tag = 'General'

# Example values by schema format - formats take precedence over types
_example_by_format = {
    'date-time': '2026-01-01T12:00:00+00:00',
    'date': '2026-01-01',
    'binary': 'ZGF0YQ==',
}

# Example values by schema type
_example_by_type = {
    'string': 'string',
    'integer': 1,
    'number': 1.0,
    'boolean': True,
}

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

        # Handle untyped input - any JSON object is accepted
        if service_input['type'] == 'any':
            return _any_object_schema

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
        raise TypeConversionError(
            f'Cannot map service input {service_input["type"]} to OpenAPI schema. '
            'Add handling for this input type in _create_request_schema method')

    def _create_response_schema(self, service_output, models):
        """ Create a schema for the response body.
        """
        if not service_output:
            return None

        # Handle untyped output - any JSON object may be returned
        if service_output['type'] == 'any':
            return _any_object_schema

        # Handle model-based output
        if service_output['type'] == 'model':
            model_name = service_output['model_name']
            try:
                return self.type_mapper.map_type(model_name, models)
            except TypeConversionError as e:
                logger.warning(f'Could not map output model: {e}')
                raise

        # Handle string output
        elif service_output['type'] == 'string':
            properties = {}
            required = []

            properties[service_output['name']] = {'type': 'string'}
            if service_output.get('required', True):
                required.append(service_output['name'])

            schema = {
                'type': 'object',
                'properties': properties
            }
            if required:
                schema['required'] = required

            return schema

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
        raise TypeConversionError(
            f'Cannot map service output {service_output["type"]} to OpenAPI schema. '
            'Add handling for this output type in _create_response_schema method')

    def _build_example(self, schema:'anydict', visited:'any_'=None) -> 'any_':
        """ Builds an example value for a schema, resolving references into registered components.
        Self-referential models stop the recursion with an empty object.
        """
        if visited is None:
            visited = set()

        # References are resolved into the component schema they point to ..
        if '$ref' in schema:
            ref_name = schema['$ref'].rsplit('/', 1)[-1]

            if ref_name in visited:
                return {}
            visited.add(ref_name)

            components = self.type_mapper.get_schema_components()
            if ref_name not in components:
                return {}

            out = self._build_example(components[ref_name], visited)
            return out

        # .. composed schemas take their example from the first alternative ..
        for composed_key in ('anyOf', 'oneOf'):
            if composed_key in schema:
                out = self._build_example(schema[composed_key][0], visited)
                return out

        # .. type lists come from nullable fields, whose first entry is the actual type ..
        schema_type = schema.get('type')
        if isinstance(schema_type, list):
            schema_type = schema_type[0]

        # .. objects build one example value per property ..
        if schema_type == 'object':
            properties = schema.get('properties')
            if not properties:
                return {}

            out = {}
            for property_name, property_schema in properties.items():
                out[property_name] = self._build_example(property_schema, visited)

            return out

        # .. arrays wrap one example element ..
        if schema_type == 'array':
            items = schema.get('items')
            if not items:
                return []

            element = self._build_example(items, visited)

            out = [element]
            return out

        # .. a scalar default from the model definition wins over generic values ..
        if 'default' in schema:
            out = schema['default']
            return out

        # .. otherwise the example comes from the format or the type.
        schema_format = schema.get('format')
        if schema_format in _example_by_format:
            out = _example_by_format[schema_format]
            return out

        if schema_type in _example_by_type:
            out = _example_by_type[schema_type]
            return out

        return {}

    def build_spec(self, scan_results):
        """ Build an OpenAPI specification document from the scanned services and models and return it as a dict.
        """
        services = scan_results['services']
        models = scan_results['models']

        openapi:'anydict' = {
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

            # Endpoints are grouped by the dotted prefix of the service name,
            # so package and module structure becomes the tag structure.
            if '.' in service_name:
                tag = service_name.rsplit('.', 1)[0]
            else:
                tag = _default_tag

            operation = {
                'summary': f'Invoke {service_name}',
                'description': f'Invoke the {service.get('class_name', '')} service',
                'operationId': service_name.replace('.', '_').replace('-', '_'),
                'tags': [tag],
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
                        request_content = {'schema': request_schema}

                        # An example derived from the schema, so the docs are never bare schemas
                        request_example = self._build_example(request_schema)
                        if request_example:
                            request_content['example'] = request_example

                        operation['requestBody'] = {
                            'description': 'Input parameters',
                            'required': True,
                            'content': {
                                'application/json': request_content
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
                        response_content = {'schema': response_schema}

                        # An example derived from the schema, same as for the request body
                        response_example = self._build_example(response_schema)
                        if response_example:
                            response_content['example'] = response_example

                        operation['responses']['200']['content'] = {
                            'application/json': response_content
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

        # Collect all the tags used by operations into the document-level list, sorted by name
        tag_names:'any_' = set()
        paths:'anydict' = openapi['paths']

        for path_item in paths.values():
            for operation in path_item.values():
                tag_names.update(operation['tags'])

        document_tags:'dictlist' = []
        for tag_name in sorted(tag_names):
            document_tags.append({'name': tag_name})

        if document_tags:
            openapi['tags'] = document_tags

        return openapi

    def generate_openapi(self, scan_results, output_file):
        """ Generate an OpenAPI specification from the scanned services and models and write it out as YAML.
        """
        openapi = self.build_spec(scan_results)

        # Write the OpenAPI specification to a file
        with open(output_file, 'w') as f:
            yaml.dump(openapi, f, sort_keys=False)

# ################################################################################################################################
# ################################################################################################################################
