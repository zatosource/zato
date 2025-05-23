# -*- coding: utf-8 -*-
"""
CLI entry point for generating OpenAPI from ODB (channels, security, etc).
"""
import logging
import sys
from pathlib import Path
from zato.openapi.generator import db_scanner
from zato.openapi.generator.openapi_ import OpenAPIGenerator

logger = logging.getLogger(__name__)

class _DummyTypeMapper:
    def get_schema_components(self):
        return {}

def main(output_file='/tmp/openapi.yaml'):
    scan_results = db_scanner.build_scan_results()
    openapi_generator = OpenAPIGenerator(type_mapper=_DummyTypeMapper())
    openapi_generator.generate_openapi(scan_results, output_file)
    logger.info(f'OpenAPI specification saved to {output_file}')

if __name__ == '__main__':
    main()
