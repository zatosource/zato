#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Runner script for the I/O scanner
"""

# stdlib
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the scanner
from zato.openapi.generator.io_scanner import scan_io

def main():
    if len(sys.argv) < 2:
        print('Usage: python run_io_scanner.py DIRECTORY1 [DIRECTORY2...] [--output OUTPUT_FILE]')
        sys.exit(1)
    
    # Parse command line arguments
    directories = []
    output_file = '/tmp/openapi.yaml'
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--output' or sys.argv[i] == '-o':
            if i + 1 < len(sys.argv):
                output_file = sys.argv[i + 1]
                i += 2
            else:
                print('Error: --output requires a file path')
                sys.exit(1)
        else:
            directories.append(sys.argv[i])
            i += 1
    
    if not directories:
        print('Error: At least one directory must be specified')
        sys.exit(1)
    
    # Run the scanner
    try:
        print(f'Scanning directories: {directories}')
        print(f'Output file: {output_file}')
        scan_io(directories, output_file)
        print(f'OpenAPI specification saved to {output_file}')
        print('To validate the output, run: swagger-cli validate ' + output_file)
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
