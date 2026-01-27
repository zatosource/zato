# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from traceback import format_exc

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def build_openapi_spec(
    channel_name,
    services_info,
    file_paths,
):
    """ Builds OpenAPI specification from services info and scanned file paths.
    This is the core OpenAPI generation logic used by both web-admin and the server-side service.
    """
    from zato.openapi.generator.io_scanner import IOScanner
    from zato.openapi.generator.openapi_ import OpenAPIGenerator
    import yaml

    # Scan source files for input/output definitions
    scanner = IOScanner()
    scan_results = scanner.scan_files(file_paths) if file_paths else {'services': [], 'models': {}}

    # Build lookup dict from scan results
    schema_by_service = {}
    for service in scan_results['services']:
        service_name = service.get('name')
        if service_name:
            schema_by_service[service_name] = {
                'input': service.get('input'),
                'output': service.get('output'),
                'class_name': service.get('class_name')
            }

    # Merge schema info into services_info
    for service in services_info:
        schema = schema_by_service.get(service['name'])
        if schema:
            service.update(schema)

    # Collect security schemes from services
    security_schemes = {}
    for service in services_info:
        security_name = service.get('security_name')
        if security_name and security_name not in security_schemes:
            security_schemes[security_name] = {
                'type': 'http',
                'scheme': 'basic'
            }

    # Initialize OpenAPI spec structure
    openapi_spec = {
        'openapi': '3.1.0',
        'info': {
            'title': channel_name,
            'version': '1.0.0'
        },
        'paths': {},
        'components': {
            'schemas': {},
            'securitySchemes': security_schemes
        }
    }

    openapi_generator = OpenAPIGenerator(type_mapper=scanner.type_mapper)

    # Build path operations for each service
    for service in services_info:
        path = service.get('url_path', f'/{service["name"].replace(".", "/")}')
        method = service.get('http_method', 'post').lower()

        # Base operation structure
        operation = {
            'summary': f'Invoke {service["name"]}',
            'operationId': service['name'].replace('.', '_').replace('-', '_'),
            'responses': {
                '200': {'description': 'Successful response'},
                '400': {'description': 'Bad Request'},
                '500': {'description': 'Internal Server Error'}
            }
        }

        # Add security requirement if service has security
        security_name = service.get('security_name')
        if security_name:
            operation['security'] = [{security_name: []}]

        # Add request body schema if service has input definition
        if service.get('input'):
            try:
                request_schema = openapi_generator._create_request_schema(service['input'], scan_results['models'])
                if request_schema:
                    input_def = service['input']
                    is_required = True
                    if input_def.get('type') == 'string':
                        is_required = input_def.get('required', True)
                    elif input_def.get('type') == 'tuple':
                        is_required = any(el.get('required', True) for el in input_def.get('elements', []))
                    operation['requestBody'] = {
                        'required': is_required,
                        'content': {'application/json': {'schema': request_schema}}
                    }
            except Exception:
                logger.warning('Could not create request schema for %s: %s', service['name'], format_exc())

        # Add response schema if service has output definition
        if service.get('output'):
            try:
                response_schema = openapi_generator._create_response_schema(service['output'], scan_results['models'])
                if response_schema:
                    operation['responses']['200']['content'] = {
                        'application/json': {'schema': response_schema}
                    }
            except Exception:
                logger.warning('Could not create response schema for %s: %s', service['name'], format_exc())

        # Add operation to the spec
        if path not in openapi_spec['paths']:
            openapi_spec['paths'][path] = {}
        openapi_spec['paths'][path][method] = operation

    # Add schema components from type mapper
    schema_components = openapi_generator.type_mapper.get_schema_components()
    if schema_components:
        openapi_spec['components']['schemas'].update(schema_components)

    # Serialize to YAML
    yaml_output = yaml.dump(openapi_spec, sort_keys=False, allow_unicode=True)

    return yaml_output

# ################################################################################################################################
# ################################################################################################################################
