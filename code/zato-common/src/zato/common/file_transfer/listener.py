# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import argparse
import fnmatch
import glob
import logging
import os
import sys
import time

# Watchdog
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver
from watchdog.observers.inotify import InotifyObserver

# Zato
from zato.broker.client import BrokerClient
from zato.common.util.api import new_cid, publish_file, publish_enmasse, publish_static

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from watchdog.events import FileSystemEvent
    from watchdog.observers.api import BaseObserver
    from zato.common.typing_ import strlist, strlistnone

# ################################################################################################################################
# ################################################################################################################################

# Logger for this module
logger = logging.getLogger(__name__)

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
    'user-conf/**',
    '**/config.yaml',
    '**/enmasse.yaml',
    '**/config*.y*ml',
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

def find_base_directories(directory_path:'str', pattern:'str') -> 'strlist':
    """ Finds all directories matching the given pattern under directory_path.
    """
    out = []
    full_pattern = os.path.join(directory_path, pattern)
    directories = glob.glob(full_pattern, recursive=True)
    for d in directories:
        if os.path.isdir(d):
            out.append(d)
    return out

# ################################################################################################################################
# ################################################################################################################################

def find_matching_items(directory_path:'str') -> 'strlist':
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

    # Determine the base directories for searching by looking for 'src' and 'config'
    base_dirs = []

    src_dirs = find_base_directories(directory_path, '**/src')
    base_dirs.extend(src_dirs)

    config_dirs = find_base_directories(directory_path, '**/config')
    base_dirs.extend(config_dirs)

    # Store enmasse matches (full paths) and non-enmasse matches (will be directories)
    enmasse_matches = set()
    other_dir_matches = set()

    # Process any patterns containing "enmasse" - these can be anywhere in the input directory
    for pattern in pickup_order_patterns:
        if 'enmasse' in pattern:
            # Get the full pattern path
            if pattern.startswith('**/'):
                full_pattern = os.path.join(directory_path, pattern)
            else:
                full_pattern = os.path.join(directory_path, '**/' + pattern)

            # Find matching items
            for match in glob.glob(full_pattern, recursive=True):
                if os.path.isfile(match):
                    enmasse_matches.add(match.rstrip(os.path.sep))

    # Process non-enmasse patterns within each base directory
    for base_dir in base_dirs:
        for pattern in pickup_order_patterns:
            if 'enmasse' not in pattern:
                # Get the full pattern path
                full_pattern = os.path.join(base_dir, '**/' + pattern)

                # Find matching items
                for match in glob.glob(full_pattern, recursive=True):
                    directory = os.path.dirname(match) if os.path.isfile(match) else match
                    other_dir_matches.add(directory.rstrip(os.path.sep))

    # Combine enmasse full paths with unique directories from other matches
    out = list(enmasse_matches.union(other_dir_matches))

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
    """ Custom event handler that processes file system events.
    """
    def __init__(
        self,
        matching_dirs:'strlist',
        event_types:'strlistnone',
        file_patterns:'strlistnone',
    ) -> 'None':
        """ Initialize with matching directories and event types to track.
        """
        self.matching_dirs = matching_dirs

        # Include default events if none provided
        self.event_types = event_types or ['created', 'deleted', 'modified', 'closed', 'closed_no_write']

        # File patterns to match (e.g. ['*.py', '*.txt'])
        self.file_patterns = file_patterns or ['*.py', '*.yaml', '*.yml',  '*.ini']

        # For tracking file size stability
        self.file_sizes = {}
        self.file_checks = {}

        # Number of checks with stable size required to consider a file complete
        self.stability_threshold = 3

        # Track files that have been modified or created - these are candidates for 'file ready'
        # when a subsequent 'closed' event is received
        self.modified_files = set()

        # Initialize broker client for publishing events
        self.broker_client = BrokerClient()
        self.broker_client.ping_connection()
        super().__init__()

# ################################################################################################################################

    def _is_event_relevant(self, event_path:'str', event_type:'str') -> 'bool':
        """ Check if event should be processed based on path and type.
        """
        # Skip if event type is not in our list of tracked events
        if event_type not in self.event_types:
            return False

        # Ignore all directory events (not just modified ones)
        # But make an exception for enmasse files which we always want to process
        is_enmasse = 'enmasse' in event_path and ('.yml' in event_path or '.yaml' in event_path)

        # Skip all directory events (unless it's enmasse-related)
        if os.path.isdir(event_path) and not is_enmasse:
            return False

        # Always process enmasse events
        if is_enmasse:
            return True

        # Check if the file matches any of our file patterns
        matches_pattern = False
        for pattern in self.file_patterns:
            if fnmatch.fnmatch(os.path.basename(event_path), pattern):
                matches_pattern = True
                break

        # If file doesn't match any patterns, skip it
        if not matches_pattern:
            return False

        # For file events, check if the path is in one of our matching directories
        for dir_path in self.matching_dirs:
            if event_path.startswith(dir_path):
                return True

        # Event is not in any of the matching directories
        return False

# ################################################################################################################################

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

                # If file size has been stable for several checks, consider it complete
                if self.file_checks[event_path] >= self.stability_threshold:
                    logger.info('File ready: %s', event_path)
                    # Publish the file-ready event
                    self.publish_file_ready_event(event_path)
                    del self.file_sizes[event_path]
                    del self.file_checks[event_path]
            else:
                # Size changed, update and reset counter
                self.file_sizes[event_path] = current_size
                self.file_checks[event_path] = 1
        else:
            # Start tracking this file
            self.file_sizes[event_path] = current_size
            self.file_checks[event_path] = 1

# ################################################################################################################################

    def on_created(self, event:'FileSystemEvent') -> 'None':
        """ Handle created events and start stability checking.
        """
        # Get normalized path
        event_path:'str' = event.src_path.rstrip(os.path.sep) # type: ignore

        if self._is_event_relevant(event_path, 'created'):
            # Mark this file as modified/created for later reference
            self.modified_files.add(event_path)
            # Silent - start stability checking for this file
            _ = self._check_file_stability(event_path)

# ################################################################################################################################

    def on_modified(self, event:'FileSystemEvent') -> 'None':
        """ Handle modified events and update stability checking.
        """
        # Get normalized path
        event_path:'str' = event.src_path.rstrip(os.path.sep) # type: ignore

        if self._is_event_relevant(event_path, 'modified'):
            # Silent - continue stability checking if it's a file
            if not os.path.isdir(event_path):
                # Mark this file as modified for later reference
                self.modified_files.add(event_path)
                _ = self._check_file_stability(event_path)

# ################################################################################################################################

    def publish_file_ready_event(self, event_path:'str') -> 'None':
        """ Publish file-ready event to the broker.
        """
        try:
            cid = new_cid()
            is_enmasse = 'enmasse' in event_path and ('.yml' in event_path or '.yaml' in event_path)
            is_static = event_path.endswith('.ini') or event_path.endswith('.zrules')
            
            if is_enmasse:
                msg = publish_enmasse(self.broker_client, cid, event_path)
            elif is_static:
                msg = publish_static(self.broker_client, cid, event_path)
            else:
                msg = publish_file(self.broker_client, cid, event_path)
            logger.info('Sent msg -> %s', msg)
        except Exception as e:
            logger.warning('Could not publish event to broker: %s -> %s', e, event_path)

# ################################################################################################################################

    def on_closed(self, event:'FileSystemEvent') -> 'None':
        """ Handle closed events (file was written to and closed).
        """
        if self._is_event_relevant(event.src_path, 'closed'): # type: ignore
            event_path = event.src_path
            logger.info('File closed: %s', event_path)

            # Check if this file was previously modified or created
            if event_path in self.modified_files:
                logger.info('File ready: %s', event_path)

                # Publish the file-ready event
                self.publish_file_ready_event(event_path) # type: ignore

                # Clean up any stability checks for this file
                if event_path in self.file_sizes:
                    del self.file_sizes[event_path]
                    del self.file_checks[event_path]

                # Remove from modified files
                self.modified_files.remove(event_path)

# ################################################################################################################################

    def on_closed_no_write(self, event:'FileSystemEvent') -> 'None':
        """ Handle closed_no_write events (file was opened but not modified).
        """
        # Get normalized path
        event_path:'str' = event.src_path.rstrip(os.path.sep) # type: ignore

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
            logger.debug('File closed without writing: %s', event_path)

            # If it's in the modified set, it was a false positive, remove it
            if event_path in self.modified_files:
                self.modified_files.remove(event_path)

# ################################################################################################################################

    def on_deleted(self, event:'FileSystemEvent') -> 'None':
        """ Handle deleted events and clean up tracking.
        """
        # Get normalized path
        event_path:'str' = event.src_path.rstrip(os.path.sep) # type: ignore

        if self._is_event_relevant(event_path, 'deleted'):
            logger.info('File deleted: %s', event_path)

            # Clean up any tracking for this file
            if event_path in self.file_sizes:
                del self.file_sizes[event_path]
                del self.file_checks[event_path]

# ################################################################################################################################
# ################################################################################################################################

def watch_directory(
    directory_path:'str',
    matching_items:'strlist',
    event_types:'strlistnone',
    file_patterns:'strlistnone',
    observer_type:'str'='inotify',
) -> 'BaseObserver':
    """ Sets up a watchdog observer to monitor changes in the deepest common directory.
    """
    # Create the appropriate watchdog observer based on type
    if observer_type == 'polling':
        observer = PollingObserver()
    elif observer_type == 'inotify':
        try:
            observer = InotifyObserver()
        except Exception as e:
            logger.warning('Could not create InotifyObserver, falling back to default: %s', e)
            observer = Observer()
    else: # 'auto' or any other value defaults to the system-specific observer
        observer = Observer()

    # Find the deepest common directory to watch
    # This optimizes the observer to watch from the appropriate level
    watch_directory = find_deepest_common_directory(matching_items)

    # Create event handler
    event_handler = ZatoFileSystemEventHandler(matching_items, event_types, file_patterns)

    # Schedule the observer
    _ = observer.schedule(event_handler, watch_directory, recursive=True)

    return observer

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format)

    # Configure argument parser
    parser = argparse.ArgumentParser(description='Zato file event monitoring system')

    _ = parser.add_argument('directory', nargs='?', default=os.getcwd(), help='Directory to monitor (default: current working directory)')

    _ = parser.add_argument(
        '--observer',
        dest='observer_type',
        default='inotify',
        choices=['inotify', 'polling', 'auto'],
        help='Observer type to use for file monitoring (default: inotify)'
    )

    default_patterns = ['*.py', '*.yaml', '*.yml', '*.ini', '*.zrules']

    _ = parser.add_argument(
        '--patterns',
        nargs='*',
        default=default_patterns,
        help=f'File patterns to monitor (default: {default_patterns})'
    )

    # Parse arguments
    args = parser.parse_args()

    # Get absolute path for the directory
    base_dir = os.path.abspath(args.directory)

    logger.info('Using current directory: %s', base_dir)

    try:
        matching_items = []
        is_incoming_services = base_dir.rstrip(os.path.sep).endswith(os.path.join('incoming', 'services'))

        if is_incoming_services:
            matching_items = [base_dir]
            logger.info('Watching for changes in %s', base_dir)
        else:
            matching_items = find_matching_items(base_dir)
            if not matching_items:
                logger.info('No "src" directory found in %s, or no matching items within it. Nothing to watch.', base_dir)
            else:
                common_dir = find_deepest_common_directory(matching_items)
                logger.info('Watching for changes in %s and subdirectories.', common_dir)
                logger.info('Found %s matching items to process:', len(matching_items))
                for item in matching_items:
                    logger.info('  %s', item)

        # Start the watcher if we have something to watch
        if matching_items:

            # Use the parsed arguments
            file_patterns = args.patterns
            observer_type = args.observer_type

            logger.info('Using file patterns: %s', file_patterns)
            logger.info('Using observer type: %s', observer_type)

            # Automatically watch for changes
            try:
                observer = watch_directory(
                    base_dir,
                    matching_items,
                    event_types=None,
                    file_patterns=file_patterns,
                    observer_type=observer_type
                )
                observer.start()
                logger.info('Watching for changes, press Ctrl+C to stop...')

                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    observer.stop()

                observer.join()
                logger.info('\nWatching stopped.')
            except Exception as e:
                logger.info(f'\nError setting up file watching: {e}')

    except Exception as e:
        logger.info(f'Error: {e}')
        sys.exit(1)

# ################################################################################################################################
# ################################################################################################################################
