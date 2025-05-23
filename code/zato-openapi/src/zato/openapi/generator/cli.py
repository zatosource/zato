# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import argparse
import logging

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
    _ = parser.add_argument('directories', nargs='*')
    _ = parser.add_argument('--output', '-o', default='/tmp/openapi.yaml', help='Output file path (default: /tmp/openapi.yaml)')
    return parser.parse_args()

# ################################################################################################################################

def main() -> 'None':
    """ Main entry point for the CLI.
    """
    args = parse_args()
    from zato.openapi.generator import db_openapi
    db_openapi.main(args.output, args.directories)

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
