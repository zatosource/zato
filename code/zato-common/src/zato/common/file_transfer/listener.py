# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import glob
import os
import sys

# ################################################################################################################################
# ################################################################################################################################

pickup_order_patterns = [

    'common*/**',
    'util*/**',
    'model*/**',
    'core*/**',
    'channel*/**',
    'adapter*/**',
    'api*/**',
    'services*/**',
    '**/enmasse*.y*ml',
]

# ################################################################################################################################
# ################################################################################################################################

def find_matching_items(directory_path:'str') -> 'list[str]':
    """ Finds all files and directories matching pickup_order_patterns in the given directory,
    but only after locating a "src" directory inside it. Returns a list of matching paths sorted alphabetically.
    """
    # Make sure we have the absolute path
    directory_path = os.path.abspath(directory_path)

    # Check if the directory exists
    if not os.path.isdir(directory_path):
        raise ValueError(f'Directory does not exist: {directory_path}')

    # First, find the "src" directory (exact match) inside the provided directory
    src_pattern = os.path.join(directory_path, '**/src')
    src_directories = glob.glob(src_pattern, recursive=True)

    # Filter to ensure we only match exact 'src' directories, not something like 'mysrc'
    src_directories = [d for d in src_directories if os.path.basename(d) == 'src' and os.path.isdir(d)]

    # If no src directory found, return empty list
    if not src_directories:
        return []

    # Use the first found src directory as our base for pattern matching
    src_directory = src_directories[0]

    # Store all matching items
    out = []

    # Process each pattern within the src directory
    for pattern in pickup_order_patterns:
        # Get the full pattern path - prepend '**/' to ensure we catch items at any depth
        full_pattern = os.path.join(src_directory, '**/' + pattern)

        # Find matching items
        matches = glob.glob(full_pattern, recursive=True)

        # Add to result list
        out.extend(matches)

    # Remove duplicates and sort
    out = sorted(set(out))

    # Filter out __pycache__ directories and *.pyc files
    out = [item for item in out
        if not ('__pycache__' in item or item.endswith('.pyc'))]

    return out

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # Check if a directory path was provided
    if len(sys.argv) < 2:
        print(f'Usage: {os.path.basename(sys.argv[0])} <directory_path>')
        sys.exit(1)

    # Get the directory path from command line
    directory_path = sys.argv[1]

    try:
        # Find matching items
        matching_items = find_matching_items(directory_path)

        # Print results
        if not matching_items:
            print(f'No "src" directory found in {directory_path} or no matching items within src directory.')
        else:
            # Find the src directory that was used
            src_pattern = os.path.join(directory_path, '**/src')
            src_directories = glob.glob(src_pattern, recursive=True)
            src_directories = [d for d in src_directories if os.path.basename(d) == 'src' and os.path.isdir(d)]
            src_directory = src_directories[0] if src_directories else 'Unknown'

            print(f'Using src directory: {src_directory}')
            print(f'Found {len(matching_items)} matching items:')
            for item in matching_items:
                print(f'  {item}')

    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)
