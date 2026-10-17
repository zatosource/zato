# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import logging
import re

# PyYAML
import yaml

# Zato
from zato.openapi.generator.examples import get_integer_example, get_string_example
from zato.openapi.generator.naming import get_operation_ids, get_summary, get_tags

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, dictlist, strlist, strset
    from zato.openapi.generator.io_scanner import TypeMapper
    TypeMapper = TypeMapper
    any_ = any_
    anydict = anydict
    anylist = anylist
    dictlist = dictlist
    strlist = strlist
    strset = strset

# ################################################################################################################################
# ################################################################################################################################

# Logger for this module
logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Services without typed input or output are documented with this schema - any JSON object is accepted or returned.
_any_object_schema = {'type': 'object', 'additionalProperties': True}

# Placeholders in channel URL paths, e.g. /patients/{patient_id}
_path_placeholder_pattern = re.compile(r'\{([^}]+)\}')

# Methods whose input is documented as query string parameters rather than as a request body
_query_string_methods = ('get', 'head', 'delete')

# Path and query string values always reach services as strings
_parameter_schema = {'type': 'string'}

# Example values by schema format - formats take precedence over types
_example_by_format = {
    'date-time': '2026-01-01T12:00:00+00:00',
    'date': '2026-01-01',
    'binary': 'ZGF0YQ==',
}

# The extension keys under which deprecated operations have their sunset date and their successor path
_sunset_key = 'x-sunset'
_successor_key = 'x-successor'

# The extension key under which request bodies and query string parameters have an example with every optional property,
# next to the standard example, which has only the properties a request needs
_complete_example_key = 'x-complete-example'

# The example of a string whose name says nothing about its values
_default_string_example = 'string'

# The media type of responses from endpoints that do not require one of their own
_default_media_type = 'application/json'

# Example values by schema type
_example_by_type = {
    'string': _default_string_example,
    'integer': 1,
    'number': 1.0,
    'boolean': True,
}

# ################################################################################################################################
# ################################################################################################################################

def _get_service_path(service_name:'str', service:'anydict') -> 'str':
    """ Returns the URL path of a service's channel, or a path derived from the service name if it has no channel.
    """
    out = service.get('url_path') or f'/{service_name.replace(".", "/")}'
    return out

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
    def __init__(self, type_mapper:'TypeMapper') -> 'None':
        self.type_mapper = type_mapper

    def _create_request_schema(self, service_input:'anydict', models:'anydict') -> 'anydict':
        """ Create a schema for the request body.
        """
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

            properties[service_input['name']] = {'type': service_input['schema_type']}
            if service_input.get('required', True):
                required.append(service_input['name'])

            schema:'anydict' = {
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
                properties[element['name']] = {'type': element['schema_type']}
                if element.get('required', True):
                    required.append(element['name'])

            schema:'anydict' = {
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
            f'Cannot map service input {service_input["type"]} to OpenAPI schema. ' +
            'Add handling for this input type in _create_request_schema method')

    def _create_response_schema(self, service_output:'anydict', models:'anydict') -> 'anydict':
        """ Create a schema for the response body.
        """
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

            properties[service_output['name']] = {'type': service_output['schema_type']}
            if service_output.get('required', True):
                required.append(service_output['name'])

            schema:'anydict' = {
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
                properties[element['name']] = {'type': element['schema_type']}
                if element.get('required', True):
                    required.append(element['name'])

            schema:'anydict' = {
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
            f'Cannot map service output {service_output["type"]} to OpenAPI schema. ' +
            'Add handling for this output type in _create_response_schema method')

    def _build_example(
        self,
        schema:'anydict',
        visited:'strset',
        should_skip_optional:'bool',
        property_name:'str',
        ) -> 'any_':
        """ Builds an example value for a schema, resolving references into registered components.
        Self-referential models stop the recursion with an empty object. Request examples skip
        optional properties without a default because a sample value would replace the default the service applies.
        Scalar values are chosen by the name of the property they belong to, if the name is known.
        """
        # References are resolved into the component schema they point to ..
        if '$ref' in schema:
            ref_name = schema['$ref'].rsplit('/', 1)[-1]

            if ref_name in visited:
                return {}

            components = self.type_mapper.get_schema_components()
            if ref_name not in components:
                return {}

            component = components[ref_name]
            branch_visited = visited | {ref_name}

            out = self._build_example(component, branch_visited, should_skip_optional, property_name)
            return out

        # .. composed schemas take their example from the first alternative ..
        for composed_key in ('anyOf', 'oneOf'):
            if composed_key in schema:
                alternative = schema[composed_key][0]
                out = self._build_example(alternative, visited, should_skip_optional, property_name)
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

            required = schema.get('required', [])

            out = {}
            for name, property_schema in properties.items():
                if should_skip_optional:
                    if not self._is_example_property(name, property_schema, required):
                        continue
                out[name] = self._build_example(property_schema, visited, should_skip_optional, name)

            return out

        # .. arrays wrap one example element ..
        if schema_type == 'array':
            items = schema.get('items')
            if not items:
                return []

            element = self._build_example(items, visited, should_skip_optional, property_name)

            out = [element]
            return out

        # .. a scalar default from the model definition wins over generic values ..
        if 'default' in schema:
            out = schema['default']
            return out

        # .. then the format, which is exact ..
        schema_format = schema.get('format')
        if schema_format in _example_by_format:
            out = _example_by_format[schema_format]
            return out

        # .. then the property name, which says what kind of value is expected ..
        if schema_type == 'string':
            if out := get_string_example(property_name):
                return out

        if schema_type == 'integer':
            out = get_integer_example(property_name)
            return out

        # .. and the type is all that is left.
        if schema_type in _example_by_type:
            out = _example_by_type[schema_type]
            return out

        return {}

    def _is_example_property(self, name:'str', property_schema:'anydict', required:'strlist') -> 'bool':
        """ Returns True if a property belongs in a request example - it is required or it has a default of its own.
        """
        if name in required:
            return True

        out = property_schema.get('default') is not None
        return out

    def _get_parameter_example(self, parameter_name:'str') -> 'str':
        """ Returns a sample value for a path or query string parameter, which is always a string.
        """
        if not (out := get_string_example(parameter_name)):
            out = _default_string_example

        return out

    def _resolve_schema(self, schema:'anydict') -> 'anydict':
        """ Returns the component schema a reference points to, or the schema itself if it is not a reference.
        """
        if '$ref' in schema:
            ref_name = schema['$ref'].rsplit('/', 1)[-1]
            components = self.type_mapper.get_schema_components()
            out = components[ref_name]
        else:
            out = schema

        return out

    def _build_path_parameters(self, path_parameter_names:'strlist') -> 'dictlist':
        """ Builds one required path parameter per placeholder in a channel's URL path.
        """
        out:'dictlist' = []

        for parameter_name in path_parameter_names:
            parameter = {
                'name': parameter_name,
                'in': 'path',
                'required': True,
                'schema': _parameter_schema,
                'example': self._get_parameter_example(parameter_name),
            }
            out.append(parameter)

        return out

    def _apply_path_parameter_defaults(self, parameters:'dictlist', request_schema:'anydict') -> 'None':
        """ Gives each path parameter whose input property has a default of its own that default as its sample value.
        """
        # Untyped and list-based input has no properties to take defaults from ..
        resolved = self._resolve_schema(request_schema)
        if not (properties := resolved.get('properties')):
            return

        # .. and a parameter with no property of the same name keeps the sample value its name gave it.
        for parameter in parameters:
            if property_schema := properties.get(parameter['name']):
                if 'default' in property_schema:
                    parameter['example'] = property_schema['default']

    def _build_query_parameters(self, request_schema:'anydict', path_parameter_names:'strlist') -> 'dictlist':
        """ Builds query string parameters out of the properties of an input schema,
        leaving out the properties that are already path parameters.
        """
        out:'dictlist' = []

        # Untyped and list-based input has no properties to turn into parameters ..
        resolved = self._resolve_schema(request_schema)
        if not (properties := resolved.get('properties')):
            return out

        # .. the required list is present only if at least one property is required ..
        if not (required := resolved.get('required')):
            required = []

        # .. and each property that is not in the path becomes one parameter.
        for property_name, property_schema in properties.items():

            if property_name in path_parameter_names:
                continue

            parameter = {
                'name': property_name,
                'in': 'query',
                'required': property_name in required,
                'schema': property_schema,
            }

            # Only the parameters a request example would have get a sample value ..
            if self._is_example_property(property_name, property_schema, required):
                parameter['example'] = self._build_example(property_schema, set(), True, property_name)

            # .. while the complete example has one for each of them.
            parameter[_complete_example_key] = self._build_example(property_schema, set(), False, property_name)

            out.append(parameter)

        return out

    def _has_body_properties(self, request_schema:'anydict', path_parameter_names:'strlist') -> 'bool':
        """ Returns True if an input schema has anything left for a request body once path parameters are excluded.
        """
        resolved = self._resolve_schema(request_schema)

        # Untyped and list-based input is always documented as a body ..
        if not (properties := resolved.get('properties')):
            return True

        # .. and objects need at least one property that is not in the path.
        for property_name in properties:
            if property_name not in path_parameter_names:
                out = True
                break
        else:
            out = False

        return out

    def build_spec(self, scan_results:'anydict') -> 'anydict':
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

        # Endpoints are grouped by their URL paths, by section and, in large sections, by the resource
        # that follows the section, so the document never reveals which services are behind them.
        service_paths:'strlist' = []
        service_operations:'anylist' = []

        for service in services:
            if service_name := service.get('name'):
                service_path = _get_service_path(service_name, service)
                service_paths.append(service_path)
                service_operations.append((service.get('http_method', 'post').lower(), service_path))

        tags = get_tags(service_paths)
        operation_ids = get_operation_ids(service_operations)

        # Create paths for each service
        for service in services:
            service_name = service.get('name')
            if not service_name:
                continue

            path = _get_service_path(service_name, service)
            http_method = service.get('http_method', 'post').lower()

            tag = tags[path]

            # The description is the service's docstring and, for deprecated endpoints, it points
            # to the sunset date and the successor path when they are known.
            description_parts:'strlist' = []
            summary = ''

            if docstring := service.get('docstring'):
                description_parts.append(docstring)
                summary = get_summary(docstring)

            is_deprecated = service.get('is_deprecated')
            deprecation_sunset = service.get('deprecation_sunset')
            deprecation_successor = service.get('deprecation_successor')

            if is_deprecated:
                description_parts.append('This endpoint is deprecated.')

                if deprecation_sunset:
                    description_parts.append(f'It will be retired on {deprecation_sunset}.')

                if deprecation_successor:
                    description_parts.append(f'Use `{deprecation_successor}` instead.')

            operation:'anydict' = {
                'operationId': operation_ids[http_method, path],
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

            if summary:
                operation['summary'] = summary

            if description_parts:
                operation['description'] = ' '.join(description_parts)

            # Deprecated endpoints have the flag in the document itself, next to the sunset date and the successor
            if is_deprecated:
                operation['deprecated'] = True

                if deprecation_sunset:
                    operation[_sunset_key] = deprecation_sunset

                if deprecation_successor:
                    operation[_successor_key] = deprecation_successor

            # Placeholders in the URL path are always parameters, whatever the method ..
            path_parameter_names = _path_placeholder_pattern.findall(path)
            parameters = self._build_path_parameters(path_parameter_names)

            # .. the remaining input is a query string for methods without a body and a request body otherwise.
            if service.get('input'):
                try:
                    request_schema = self._create_request_schema(service['input'], models)
                    self._apply_path_parameter_defaults(parameters, request_schema)

                    if http_method in _query_string_methods:
                        query_parameters = self._build_query_parameters(request_schema, path_parameter_names)
                        parameters.extend(query_parameters)

                    elif self._has_body_properties(request_schema, path_parameter_names):
                        request_content = {'schema': request_schema}

                        # An example derived from the schema, kept even when empty, because without one
                        # the console fills in a placeholder for every optional property.
                        request_content['example'] = self._build_example(request_schema, set(), True, '')
                        request_content[_complete_example_key] = self._build_example(request_schema, set(), False, '')

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

            if parameters:
                operation['parameters'] = parameters

            # Responses are JSON unless the endpoint is reached only by requests that accept a media type of its own ..
            if response_media_type := service.get('response_media_type'):
                operation['responses']['200']['content'] = {response_media_type: {}}
            else:
                response_media_type = _default_media_type

            # .. and the response schema is added if output is defined.
            if service.get('output'):
                try:
                    response_schema = self._create_response_schema(service['output'], models)
                    response_content = {'schema': response_schema}

                    # An example derived from the schema, same as for the request body
                    response_example = self._build_example(response_schema, set(), False, '')
                    if response_example:
                        response_content['example'] = response_example

                    operation['responses']['200']['content'] = {
                        response_media_type: response_content
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

    def generate_openapi(self, scan_results:'anydict', output_file:'str') -> 'None':
        """ Generate an OpenAPI specification from the scanned services and models and write it out as YAML.
        """
        openapi = self.build_spec(scan_results)

        # Write the OpenAPI specification to a file
        with open(output_file, 'w') as f:
            yaml.dump(openapi, f, sort_keys=False)

# ################################################################################################################################
# ################################################################################################################################
