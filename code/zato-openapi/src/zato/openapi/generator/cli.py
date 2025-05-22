# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import argparse

# Zato
from zato.openapi.generator.scanner import Scanner

# ################################################################################################################################
# ################################################################################################################################

def main():
    """ Main entry point for the OpenAPI scanner CLI.
    """
    parser = argparse.ArgumentParser(description='Generate OpenAPI specification from Zato services')
    _ = parser.add_argument('paths', nargs='+', help='Directory paths containing Zato services')
    _ = parser.add_argument('-o', '--output', help='Output file path (YAML format)', default='/tmp/openapi.yaml')
    _ = parser.add_argument('-t', '--title', help='API title', default='API Spec')
    _ = parser.add_argument('-v', '--version', help='API version', default='1.0.0')
    args = parser.parse_args()

    # Use the first path to initialize the scanner
    scanner = Scanner(args.paths[0])

    # Add additional paths if provided
    for path in args.paths[1:]:
        scanner.add_directory(path)

    # Generate spec
    _ = scanner.generate_spec(title=args.title, version=args.version)

    # Save to file as YAML only
    scanner.save_to_file(args.output)

    print(f'OpenAPI specification saved to {args.output}')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
