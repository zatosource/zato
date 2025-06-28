# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import glob
import os
import sys
import time

# watchdog
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

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

def find_deepest_common_directory(directories:'list[str]') -> 'str':
    """ Returns the deepest directory that is common to all input directories.

    For instance, given directories:
    /home/user/projects/app/src/module1
    /home/user/projects/app/src/module2
    /home/user/projects/app/src/lib/common

    This will return '/home/user/projects/app/src'

    If no common directory is found, returns an empty string.
    """
    if not directories:
        return ''

    # Split each path into components
    paths_components = []
    for path in directories:
        components = path.split(os.path.sep)
        paths_components.append(components)

    # Find the minimum length to avoid index errors
    min_length = min(len(components) for components in paths_components)

    # Find the common prefix
    common_components = []
    for idx in range(min_length):
        component = paths_components[0][idx]
        if all(components[idx] == component for components in paths_components):
            common_components.append(component)
        else:
            break

    # Convert back to path
    if common_components:
        out = os.path.sep.join(common_components)
        # Add leading path separator if it was there originally, but ensure only one
        if directories[0].startswith(os.path.sep):
            out = os.path.sep + out.lstrip(os.path.sep)
        return out
    else:
        return ''

# ################################################################################################################################
# ################################################################################################################################

class ZatoFileSystemEventHandler(FileSystemEventHandler):
    """ Custom event handler that filters events based on matching directories.
    Only processes events that occur within directories returned by find_matching_items,
    with special exception for enmasse files which are never ignored.
    """
    def __init__(self, matching_dirs:'list[str]', event_types:list=None):
        self.matching_dirs = matching_dirs
        # Include closed and closed_no_write events to detect fully written files
        self.event_types = event_types or ['created', 'deleted', 'modified', 'closed', 'closed_no_write']
        self.file_sizes = {}  # Track file sizes for stability checking
        self.file_checks = {}  # Track how many times we've checked file size
        super().__init__()

    def _is_event_relevant(self, event_path:'str', event_type:'str') -> 'bool':
        """ Returns True if the event is relevant based on the path and event type.
        Events are considered relevant if:
        - Event type is in the allowed types list
        - They occur within a directory returned by find_matching_items
        - They relate to enmasse files (which are never ignored)
        """
        # Check if this is a type of event we care about
        if event_type not in self.event_types:
            return False

        # Skip directory modification events (too noisy)
        if event_type == 'modified' and os.path.isdir(event_path):
            return False

        # Always process enmasse events
        if 'enmasse' in event_path and ('.yml' in event_path or '.yaml' in event_path):
            return True

        # Check if event path is within any of the matching directories
        for dir_path in self.matching_dirs:
            if event_path.startswith(dir_path):
                return True

        # Event is not in any of the matching directories
        return False

    def _check_file_stability(self, event_path:'str') -> 'None':
        """ Check if a file size has stabilized to determine if writing is complete.
        For files that are created by copying rather than direct writing.
        """
        # Ensure the file exists
        if not os.path.exists(event_path) or os.path.isdir(event_path):
            return

        current_size = os.path.getsize(event_path)

        if event_path in self.file_sizes:
            # If size hasn't changed, increment check counter
            if current_size == self.file_sizes[event_path]:
                self.file_checks[event_path] += 1
                # After 3 checks of stable size, consider file complete
                if self.file_checks[event_path] >= 3:
                    print(f'File fully written (size stable): {event_path}')
                    # Clean up tracking
                    del self.file_sizes[event_path]
                    del self.file_checks[event_path]
            else:
                # Size changed, update and reset counter
                self.file_sizes[event_path] = current_size
                self.file_checks[event_path] = 1
        else:
            # First time seeing this file, initialize tracking
            self.file_sizes[event_path] = current_size
            self.file_checks[event_path] = 1

    def on_created(self, event:'FileSystemEvent') -> 'None':
        """ Handle created events and start stability checking.
        """
        # Get normalized path
        event_path = event.src_path.rstrip(os.path.sep)

        if self._is_event_relevant(event_path, 'created'):
            print(f'Event detected: created - {event_path}')

            # Start stability checking for this file
            _ = self._check_file_stability(event_path)

    def on_modified(self, event:'FileSystemEvent') -> 'None':
        """ Handle modified events and update stability checking.
        """
        # Get normalized path
        event_path = event.src_path.rstrip(os.path.sep)

        if self._is_event_relevant(event_path, 'modified'):
            print(f'Event detected: modified - {event_path}')

            # Continue stability checking if it's a file
            if not os.path.isdir(event_path):
                _ = self._check_file_stability(event_path)

    def on_closed(self, event:'FileSystemEvent') -> 'None':
        """ Handle closed events (file was written to and closed).
        """
        # Get normalized path
        event_path = event.src_path.rstrip(os.path.sep)

        if self._is_event_relevant(event_path, 'closed'):
            print(f'File fully written (closed): {event_path}')

            # Clean up any stability checks for this file
            if event_path in self.file_sizes:
                del self.file_sizes[event_path]
                del self.file_checks[event_path]

    def on_closed_no_write(self, event:'FileSystemEvent') -> 'None':
        """ Handle closed_no_write events (file was opened but not modified).
        """
        # Get normalized path
        event_path = event.src_path.rstrip(os.path.sep)

        # Filter more strictly for closed_no_write events
        # First check if it's within our directory structure
        is_in_matching_dir = False
        for dir_path in self.matching_dirs:
            if event_path.startswith(dir_path):
                is_in_matching_dir = True
                break

        # Only process if it's in our directories or is an enmasse file
        is_enmasse = 'enmasse' in event_path and ('.yml' in event_path or '.yaml' in event_path)

        if is_in_matching_dir or is_enmasse:
            print(f'File closed (no write): {event_path}')

    def on_deleted(self, event:'FileSystemEvent') -> 'None':
        """ Handle deleted events and clean up tracking.
        """
        # Get normalized path
        event_path = event.src_path.rstrip(os.path.sep)

        if self._is_event_relevant(event_path, 'deleted'):
            print(f'Event detected: deleted - {event_path}')

            # Clean up any tracking for this file
            if event_path in self.file_sizes:
                del self.file_sizes[event_path]
                del self.file_checks[event_path]

def watch_directory(directory_path:'str', matching_items:'list[str]', event_types:list=None) -> 'Observer':
    """ Sets up a watchdog observer to monitor changes in the deepest common directory.
    Only processes events that occur within directories returned by find_matching_items,
    with special exception for enmasse files which are never ignored.

    Args:
        directory_path: Base directory path to search in
        matching_items: List of directories/files to watch for changes
        event_types: Types of events to monitor (default: created, deleted, modified)

    Returns the observer instance, which must be started by the caller.
    """
    # Find the deepest common directory to watch
    watch_directory = find_deepest_common_directory(matching_items)

    if not watch_directory:
        raise ValueError('No common directory to watch could be determined')

    # Create observer and event handler
    observer = Observer()
    event_handler = ZatoFileSystemEventHandler(matching_items, event_types)

    # Schedule the observer
    observer.schedule(event_handler, watch_directory, recursive=True)

    return observer

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

            # Find and display the deepest common directory
            common_dir = find_deepest_common_directory(matching_items)
            if common_dir:
                print(f'\nDeepest common directory: {common_dir}')

                # Automatically watch for changes
                try:
                    observer = watch_directory(directory_path, matching_items)
                    observer.start()
                    print(f'\nWatching for changes, press Ctrl+C to stop...')

                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        observer.stop()

                    observer.join()
                    print('\nWatching stopped.')
                except Exception as e:
                    print(f'\nError setting up file watching: {e}')

    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)
