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
from zato.openapi.generator import io_scanner

# Reference the imported function directly
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
    parser = argparse.ArgumentParser(description='Generate OpenAPI specification from Zato ODB')
    parser.add_argument('directories', nargs='*', help='(Ignored)')
    parser.add_argument('--output', '-o', default='/tmp/openapi.yaml', help='Output file path (default: /tmp/openapi.yaml)')
    return parser.parse_args()

# ################################################################################################################################

def main() -> 'None':
    """ Main entry point for the CLI.
    """
    args = parse_args()
    from zato.openapi.generator import db_openapi
    db_openapi.main(args.output)

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
