# -*- coding: utf-8 -*-

# stdlib
import logging

# Zato
from zato.openapi.generator import db_scanner, io_scanner
from zato.openapi.generator.openapi_ import OpenAPIGenerator

logger = logging.getLogger(__name__)

def main(output_file='/tmp/openapi.yaml', directories=None):

    # Get channels and security definitions from the database
    db_results = db_scanner.build_scan_results()

    # Create an IO scanner to extract schemas from code
    scanner = io_scanner.IOScanner()
    io_results = scanner.scan_directories(directories)

    # Map service names to their schema information
    schema_by_service = {}
    for service in io_results['services']:
        service_name = service.get('name')
        if service_name:
            schema_by_service[service_name] = {
                'input': service.get('input'),
                'output': service.get('output'),
                'class_name': service.get('class_name')
            }

    # Enhance DB results with schema info
    for service in db_results['services']:
        service_info = schema_by_service.get(service['name'])
        if service_info:
            service.update(service_info)

    # Preserve models for schema generation
    db_results['models'] = io_results['models']

    # Generate OpenAPI spec using the IO scanner's type mapper
    openapi_generator = OpenAPIGenerator(type_mapper=scanner.type_mapper)
    openapi_generator.generate_openapi(db_results, output_file)
    logger.info(f'OpenAPI specification saved to {output_file}')

if __name__ == '__main__':
    main()
