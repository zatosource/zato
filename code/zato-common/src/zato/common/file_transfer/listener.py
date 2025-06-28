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

# Names to ignore in paths
ignored_names = [
    '__pycache__',
    '.git',
]

# File suffixes to ignore
ignored_suffixes = [
    '.pyc',
    '.pyo',
    '.so',
    '.pyd',
]

# ################################################################################################################################
# ################################################################################################################################

def find_matching_items(directory_path:'str') -> 'list[str]':
    """ Finds all files and directories matching pickup_order_patterns in the given directory.
    For non-enmasse patterns, returns only the directories containing matches (under "src").
    For enmasse patterns, returns the full paths to matching files (anywhere in the directory).
    Returns a list of unique paths sorted alphabetically.
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
    filtered_src_directories = []
    for d in src_directories:
        if os.path.basename(d) == 'src' and os.path.isdir(d):
            filtered_src_directories.append(d)
    src_directories = filtered_src_directories

    # Store enmasse matches (full paths) and non-enmasse matches (will be directories)
    # Use sets to ensure uniqueness
    enmasse_matches = set()
    other_dir_matches = set()

    # Process any patterns containing "enmasse" - these can be anywhere in the input directory
    for pattern in pickup_order_patterns:
        if 'enmasse' in pattern:
            # Get the full pattern path - avoid double-prepending **/ to patterns
            if pattern.startswith('**/'):
                full_pattern = os.path.join(directory_path, pattern)
            else:
                full_pattern = os.path.join(directory_path, '**/' + pattern)

            # Find matching items
            matches = glob.glob(full_pattern, recursive=True)

            # Add normalized full paths to enmasse matches
            for match in matches:
                # Normalize the path by removing trailing slashes
                normalized_match = match.rstrip(os.path.sep)
                enmasse_matches.add(normalized_match)

    # Continue only if src directory was found for the other patterns
    if src_directories:
        # Use the first found src directory as our base for pattern matching
        src_directory = src_directories[0]

        # Process each non-enmasse pattern within the src directory
        for pattern in pickup_order_patterns:
            if 'enmasse' not in pattern:
                # Get the full pattern path - prepend '**/' to ensure we catch items at any depth
                full_pattern = os.path.join(src_directory, '**/' + pattern)

                # Find matching items
                matches = glob.glob(full_pattern, recursive=True)

                # Extract only the directories for non-enmasse matches
                for match in matches:
                    if os.path.isfile(match):
                        # For files, get the parent directory
                        directory = os.path.dirname(match)
                    else:
                        # For directories, use as is
                        directory = match

                    # Normalize the path by removing trailing slashes
                    directory = directory.rstrip(os.path.sep)

                    other_dir_matches.add(directory)

    # Combine enmasse full paths with unique directories from other matches
    out = list(enmasse_matches) + list(other_dir_matches)

    # Sort the combined results
    out = sorted(out)

    # Filter out items based on ignored_names and ignored_suffixes
    filtered_out = []
    for item in out:
        should_ignore = False

        # Check if any ignored name is in the path
        for name in ignored_names:
            if name in item:
                should_ignore = True
                break

        # If not already ignored, check for ignored suffixes
        if not should_ignore:
            for suffix in ignored_suffixes:
                if item.endswith(suffix):
                    should_ignore = True
                    break

        # Add to filtered list if not ignored
        if not should_ignore:
            filtered_out.append(item)

    out = filtered_out

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
            filtered_src_directories = []
            for d in src_directories:
                if os.path.basename(d) == 'src' and os.path.isdir(d):
                    filtered_src_directories.append(d)
            src_directories = filtered_src_directories
            src_directory = src_directories[0] if src_directories else 'Unknown'

            print(f'Using src directory: {src_directory}')
            print(f'Found {len(matching_items)} matching items:')
            for item in matching_items:
                print(f'  {item}')

    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)
