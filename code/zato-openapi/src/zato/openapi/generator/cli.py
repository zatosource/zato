# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import argparse
import logging
import sys
from pathlib import Path

# Zato
from zato.openapi.generator.service_scanner import scan_services

# ################################################################################################################################
# ################################################################################################################################

# Logger for this module
logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def parse_args() -> 'argparse.Namespace':
    """ Parse command line arguments.
    """
    _ = parser = argparse.ArgumentParser(description='Scan Zato services and generate OpenAPI specification')
    _ = parser.add_argument('directories', nargs='+', help='Directories to scan for services')
    _ = parser.add_argument('--output', '-o', default='openapi.yaml', help='Output file path (default: openapi.yaml)')
    return parser.parse_args()

# ################################################################################################################################

def main() -> 'None':
    """ Main entry point for the CLI.
    """
    args = parse_args()

    # Validate directories
    for directory in args.directories:
        if not Path(directory).is_dir():
            logger.error(f'Error: {directory} is not a valid directory')
            sys.exit(1)

    # Scan services and generate OpenAPI spec
    scan_services(args.directories, args.output)

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
