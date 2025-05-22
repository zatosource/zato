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

# Local imports
from . import service_scanner
from . import io_scanner

# Reference the imported functions directly
scan_services = service_scanner.scan_services
scan_io = io_scanner.scan_io

# ################################################################################################################################
# ################################################################################################################################

# Logger for this module
logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def parse_args() -> 'argparse.Namespace':
    """ Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='Scan Zato services and generate OpenAPI specification')
    parser.add_argument('directories', nargs='+', help='Directories to scan for services')
    parser.add_argument('--output', '-o', default='/tmp/openapi.yaml', help='Output file path (default: /tmp/openapi.yaml)')
    parser.add_argument('--scanner', '-s', choices=['service', 'io'], default='service', 
                      help='Scanner to use: "service" for basic service info or "io" for detailed I/O definitions (default: service)')
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

    # Select scanner based on command line option
    if args.scanner == 'service':
        # Use the basic service scanner
        scan_services(args.directories, args.output)
    else:
        # Use the I/O scanner for detailed service I/O definitions
        scan_io(args.directories, args.output)

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
