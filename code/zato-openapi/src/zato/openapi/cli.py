# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import argparse

# Zato
from zato.openapi.scanner import Scanner

# ################################################################################################################################
# ################################################################################################################################

def main():
    parser = argparse.ArgumentParser(description='Generate OpenAPI specification from Zato services')
    _ = parser.add_argument('path', help='Directory path containing Zato services')
    _ = parser.add_argument('-o', '--output', help='Output file path (YAML format)', default='/tmp/openapi.yaml')
    _ = parser.add_argument('-t', '--title', help='API title', default='API Spec')
    _ = parser.add_argument('-v', '--version', help='API version', default='1.0.0')
    args = parser.parse_args()

    # Create scanner
    scanner = Scanner(args.path)

    # Generate spec
    _ = scanner.generate_spec(title=args.title, version=args.version)

    # Save to file as YAML only
    scanner.save_spec(args.output, format_='yaml')

    print(f'OpenAPI specification saved to {args.output}')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
