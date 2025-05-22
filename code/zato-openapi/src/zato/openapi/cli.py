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
from zato.openapi.scanner import scan_directories

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Zato OpenAPI Type Scanner')
    parser.add_argument(
        'directories',
        nargs='+',
        help='Directories to scan for Zato services'
    )
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output YAML file for OpenAPI type mappings'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    return parser.parse_args()

# ################################################################################################################################
# ################################################################################################################################

def setup_logging(verbose=False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# ################################################################################################################################
# ################################################################################################################################

def main():
    """Main entry point for the CLI."""
    args = parse_args()
    setup_logging(args.verbose)

    try:
        # Validate directories
        for directory in args.directories:
            if not Path(directory).exists():
                logger.error(f"Directory does not exist: {directory}")
                return 1

        # Run the scanner
        scan_directories(args.directories, args.output)
        return 0
    except Exception as e:
        logger.exception(f"Error scanning directories: {e}")
        return 1

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    sys.exit(main())

# ################################################################################################################################
# ################################################################################################################################
