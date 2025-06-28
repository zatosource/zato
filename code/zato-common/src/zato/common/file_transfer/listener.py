# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import fnmatch
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Callable, Dict, Any

# watchdog
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent
from watchdog.observers import Observer

# Zato
from zato.common.hot_deploy_ import pickup_order_patterns

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import TypeAlias, Set
    from watchdog.observers.api import ObservedWatch

    # Define type aliases
    path_: TypeAlias = 'str'
    pathlist: TypeAlias = 'List[str]'
    callback_: TypeAlias = 'Callable[[str, Dict[str, Any]], None]'
    watches_: TypeAlias = 'Set[ObservedWatch]'

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class FileEventHandler(FileSystemEventHandler):
    callback: 'callback_' = None
    patterns: 'pathlist' = field(default_factory=list)

    def __init__(self, callback:'callback_', patterns:'pathlist') -> 'None':
        self.callback = callback
        self.patterns = patterns

    def on_created(self, event:'FileCreatedEvent') -> 'None':
        """ Handles file creation events that match our patterns.
        """
        self._process_event(event)

    def on_modified(self, event:'FileModifiedEvent') -> 'None':
        """ Handles file modification events that match our patterns.
        """
        self._process_event(event)

    def _process_event(self, event) -> 'None':
        """ Common handler for both created and modified events.
        """
        # Skip if it's a directory or not relevant to our patterns
        if event.is_directory:
            return

        src_path = event.src_path

        # Check if the file matches any of our patterns
        if self._matches_any_pattern(src_path):
            # Call the callback function with file information
            self._handle_file_event(src_path)

    def _matches_any_pattern(self, file_path:'str') -> 'bool':
        """ Checks if a file path matches any of our monitoring patterns.
        """
        file_name = os.path.basename(file_path)
        dir_path = os.path.dirname(file_path)

        for pattern in self.patterns:
            # Remove leading spaces from pattern (as they appear in pickup_order_patterns)
            pattern = pattern.strip()

            # Check for match using fnmatch
            if fnmatch.fnmatch(file_path, pattern) or \
               fnmatch.fnmatch(file_name, pattern) or \
               fnmatch.fnmatch(dir_path, pattern):
                return True

        return False

    def _handle_file_event(self, file_path:'str') -> 'None':
        """ Handle a matched file event by gathering metadata and calling the callback.
        """
        try:
            # Collect file metadata
            stat_info = os.stat(file_path)
            file_size = stat_info.st_size
            mod_time = datetime.fromtimestamp(stat_info.st_mtime)

            # Read first 100 bytes of the file
            file_data = ''
            try:
                with open(file_path, 'rb') as f:
                    file_data = f.read(100)
            except Exception as e:
                logger.warning(f'Error reading file data from `{file_path}`, e:`{e}`')

            # Prepare metadata dict
            metadata = {
                'path': file_path,
                'size_bytes': file_size,
                'modified_time': mod_time,
                'first_100_bytes': file_data,
            }

            # Call the callback with the file path and metadata
            if self.callback:
                self.callback(file_path, metadata)

        except Exception as e:
            logger.error(f'Error processing file event for `{file_path}`, e:`{e}`')

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class FileListener:
    """ A file listener that monitors directories for file changes based on patterns.
    Uses the watchdog library to detect file creation and modification events.
    """
    patterns: 'pathlist' = field(default_factory=list)
    callback: 'callback_' = None
    directories: 'pathlist' = field(default_factory=list)
    observer: 'Observer' = field(default=None)
    watches: 'watches_' = field(default_factory=set)

    def __init__(self, callback:'callback_', patterns:'pathlist'=None) -> 'None':
        """ Initialize a file listener with callback and patterns.
        If no patterns are provided, it will use the default patterns from hot_deploy_.
        """
        self.callback = callback
        self.patterns = patterns or pickup_order_patterns
        self.directories = []
        self.observer = None
        self.watches = set()

        # Find all top-level directories from env variables
        self._find_top_level_directories()

    def _find_top_level_directories(self) -> 'None':
        """ Find all top-level directories from environment variables
        that start with 'Zato_Project_Root'.
        """
        for env_name, env_value in os.environ.items():
            if env_name.startswith('Zato_Project_Root'):
                if os.path.isdir(env_value):
                    self.directories.append(env_value)
                    logger.info(f'Added directory from env var `{env_name}`: `{env_value}`')
                else:
                    logger.warning(f'Environment variable `{env_name}` points to non-existent directory: `{env_value}`')

        # Log the result
        if self.directories:
            logger.info(f'Found {len(self.directories)} top-level directories to monitor')
        else:
            logger.warning('No top-level directories found from environment variables')

    def start(self) -> 'None':
        """ Start monitoring the directories for file changes.
        """
        if not self.directories:
            logger.warning('No directories to monitor, cannot start file listener')
            return

        # Create an observer
        self.observer = Observer()

        # Create an event handler for our callback and patterns
        event_handler = FileEventHandler(self.callback, self.patterns)

        # Set up watchers for each directory
        for directory in self.directories:
            logger.info(f'Setting up watcher for directory: `{directory}`')
            watch = self.observer.schedule(event_handler, directory, recursive=True)
            self.watches.add(watch)

        # Start the observer
        self.observer.start()
        logger.info('File listener started successfully')

    def stop(self) -> 'None':
        """ Stop monitoring for file changes.
        """
        if self.observer:
            # Unschedule all watches
            for watch in self.watches:
                self.observer.unschedule(watch)

            # Stop the observer
            self.observer.stop()
            self.observer.join()
            logger.info('File listener stopped')

            # Clear the watches and observer
            self.watches.clear()
            self.observer = None

# ################################################################################################################################
# ################################################################################################################################

def example_callback(file_path:'str', metadata:'Dict[str, Any]') -> 'None':
    """ Example callback function that logs file metadata and first 100 bytes.
    """
    logger.info(f'File event detected: {file_path}')
    logger.info(f'File size: {metadata["size_bytes"]} bytes')
    logger.info(f'Modified time: {metadata["modified_time"]}')
    logger.info(f'First 100 bytes: {metadata["first_100_bytes"]}')

# ################################################################################################################################
# ################################################################################################################################

# Main section for direct execution
if __name__ == '__main__':
    import sys
    import time

    # Configure basic logging to console
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    try:
        listener = FileListener(example_callback)

        if not listener.directories:
            logger.error('No directories found to monitor. Exiting.')
            sys.exit(1)

        listener.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info('Keyboard interrupt received. Stopping listener.')
    except Exception as e:
        logger.error(f'Error in main: {e}')

# ################################################################################################################################
# ################################################################################################################################
