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

class FileEventHandler(FileSystemEventHandler):
    """ Handles file system events and filters them based on patterns.
    """
    
    def __init__(self, callback:'callback_', patterns:'pathlist', monitor_dirs:bool=True) -> 'None':
        """ Initialize the event handler with a callback and patterns.
        
        Args:
            callback: Function to call when a matched file is created/modified
            patterns: List of glob patterns to match files against
            monitor_dirs: Whether to monitor and log directory events (creation/deletion)
        """
        super().__init__()
        self.callback = callback
        self.monitor_dirs = monitor_dirs
        # Store patterns as a tuple if they're not None, since tuples are hashable
        self.patterns = tuple(p.strip() for p in patterns) if patterns else ()

    def on_created(self, event:'FileCreatedEvent') -> 'None':
        """ Handles file creation events that match our patterns.
        """
        self._process_event(event)

    def on_modified(self, event:'FileModifiedEvent') -> 'None':
        """ Handles file modification events that match our patterns.
        """
        self._process_event(event)
        
    def on_created(self, event) -> 'None':
        """ Handles file or directory creation events.
        """
        # Log directory creation events if monitoring is enabled
        if event.is_directory and self.monitor_dirs:
            logger.info(f'Directory created: `{event.src_path}`')
        else:
            self._process_event(event)
            
    def on_deleted(self, event) -> 'None':
        """ Handles file or directory deletion events.
        """
        # Log directory deletion events if monitoring is enabled
        if event.is_directory and self.monitor_dirs:
            logger.info(f'Directory deleted: `{event.src_path}`')

    def _process_event(self, event) -> 'None':
        """ Common handler for file events that need pattern matching.
        """
        # Skip if it's a directory - directory events are handled separately
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
    watches: 'Dict[str, any]' = field(default_factory=dict)
    is_running: bool = field(default=False)
    handler: 'FileEventHandler' = field(default=None)

    def __init__(self, callback:'callback_', patterns:'pathlist'=None, use_env_vars:bool=True) -> 'None':
        """ Initialize a file listener with callback and patterns.
        If no patterns are provided, it will use the default patterns from hot_deploy_.
        
        Args:
            callback: The callback function to invoke when files matching patterns are created/modified
            patterns: List of patterns to match files against (default: patterns from hot_deploy_)
            use_env_vars: Whether to load initial directories from env vars (default: True)
        """
        self.callback = callback
        # Convert patterns to tuple for hashability
        self.patterns = tuple(patterns) if patterns else tuple(pickup_order_patterns) 
        self.directories = []
        self.observer = None
        self.watches = {}
        self.is_running = False
        self.handler = None  # Will create handler when needed
        
        # Load directories from environment variables if requested
        if use_env_vars:
            self.load_directories_from_env()

    def load_directories_from_env(self) -> 'List[str]':
        """ Find all top-level directories from environment variables
        that start with 'Zato_Project_Root' and add them to the monitored directories.
        
        Returns:
            List of directories that were added
        """
        added_dirs = []
        
        for env_name, env_value in os.environ.items():
            if env_name.startswith('Zato_Project_Root'):
                if os.path.isdir(env_value) and env_value not in self.directories:
                    self.add_directory(env_value)
                    added_dirs.append(env_value)
                    logger.info(f'Added directory from env var `{env_name}`: `{env_value}`')
                elif not os.path.isdir(env_value):
                    logger.warning(f'Environment variable `{env_name}` points to non-existent directory: `{env_value}`')
        
        return added_dirs
        
    def add_directory(self, directory:'str') -> 'bool':
        """ Add a new directory to monitor.
        If the listener is already running, the directory will be added to the observer immediately.
        
        Args:
            directory: The path to the directory to monitor
            
        Returns:
            bool: True if the directory was added, False otherwise
        """
        # Normalize the path
        directory = str(Path(directory).absolute())
        
        # Check if directory exists
        if not os.path.isdir(directory):
            logger.warning(f'Cannot add non-existent directory: `{directory}`')
            return False
            
        # Check if directory is already being monitored
        if directory in self.directories:
            logger.debug(f'Directory already being monitored: `{directory}`')
            return False
            
        # Add to our list of directories
        self.directories.append(directory)
        logger.info(f'Directory added to monitoring list: `{directory}`')
        
        # If the observer is running, schedule it immediately
        if self.is_running and self.observer:
            # Create a new handler for this directory to avoid hashability issues
            handler = FileEventHandler(self.callback, self.patterns)
            watch = self.observer.schedule(handler, directory, recursive=True)
            self.watches[directory] = watch
            logger.info(f'Started monitoring directory: `{directory}`')
            
            # Log all subdirectories of the newly added directory
            try:
                for root, dirs, _ in os.walk(directory):
                    for dir_name in dirs:
                        subdir_path = os.path.join(root, dir_name)
                        logger.info(f'  Monitoring subdirectory: `{subdir_path}`')
            except Exception as e:
                logger.error(f'Error scanning subdirectories of `{directory}`, e:`{e}`')
            
        return True
        
    def remove_directory(self, directory:'str') -> 'bool':
        """ Remove a directory from monitoring.
        If the listener is running, the directory will be unscheduled from the observer immediately.
        
        Args:
            directory: The path to the directory to remove
            
        Returns:
            bool: True if the directory was removed, False otherwise
        """
        # Normalize the path
        directory = str(Path(directory).absolute())
        
        # Check if directory is being monitored
        if directory not in self.directories:
            logger.debug(f'Directory not being monitored: `{directory}`')
            return False
            
        # If the observer is running, unschedule it
        if self.is_running and self.observer and directory in self.watches:
            # Log which subdirectories will no longer be monitored
            try:
                logger.info(f'Unmonitoring directory with all subdirectories: `{directory}`')
                for root, dirs, _ in os.walk(directory):
                    for dir_name in dirs:
                        subdir_path = os.path.join(root, dir_name)
                        logger.info(f'  Stopping monitoring of subdirectory: `{subdir_path}`')
            except Exception as e:
                logger.error(f'Error listing subdirectories for `{directory}`, e:`{e}`')
                
            # Unschedule the directory
            self.observer.unschedule(self.watches[directory])
            del self.watches[directory]
            logger.info(f'Stopped monitoring directory: `{directory}`')
            
        # Remove from our list of directories
        self.directories.remove(directory)
        logger.info(f'Directory removed from monitoring list: `{directory}`')
        
        return True
        
    def get_monitored_directories(self) -> 'List[str]':
        """ Get a list of all currently monitored directories.
        
        Returns:
            List of directory paths being monitored
        """
        return list(self.directories)

    def start(self) -> 'bool':
        """ Start monitoring the directories for file changes.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        if self.is_running:
            logger.warning('File listener is already running')
            return False
            
        if not self.directories:
            logger.warning('No directories to monitor, cannot start file listener')
            return False

        # Create an observer
        self.observer = Observer()
        
        # Set up watchers for each directory
        for directory in self.directories:
            try:
                logger.info(f'Setting up watcher for directory: `{directory}`')
                # Create a new handler for each directory to avoid hashability issues
                handler = FileEventHandler(self.callback, self.patterns, monitor_dirs=True)
                watch = self.observer.schedule(handler, directory, recursive=True)
                self.watches[directory] = watch
            except Exception as e:
                logger.error(f'Error setting up watcher for `{directory}`, e:`{e}`')

        # Start the observer
        self.observer.start()
        self.is_running = True
        logger.info('File listener started successfully')
        
        # Log all currently monitored directories, including subdirectories
        self._log_all_monitored_directories()
        
        return True
        
    def _log_all_monitored_directories(self) -> 'None':
        """ Log all directories under monitoring, including subdirectories.
        """
        logger.info('=== Monitored Directories ===')
        for top_dir in self.directories:
            logger.info(f'Top-level directory: `{top_dir}`')
            # Find and log all subdirectories
            try:
                for root, dirs, _ in os.walk(top_dir):
                    for dir_name in dirs:
                        subdir_path = os.path.join(root, dir_name)
                        logger.info(f'  Subdirectory: `{subdir_path}`')
            except Exception as e:
                logger.error(f'Error scanning subdirectories of `{top_dir}`, e:`{e}`')
        logger.info('=== End of Monitored Directories ===')


    def stop(self) -> 'bool':
        """ Stop monitoring for file changes.
        
        Returns:
            bool: True if stopped successfully, False if it wasn't running
        """
        if not self.is_running or not self.observer:
            logger.warning('File listener is not running')
            return False
            
        try:
            # Stop the observer
            self.observer.stop()
            self.observer.join()
            
            # Clear the watches and observer
            self.watches.clear()
            self.observer = None
            self.is_running = False
            
            logger.info('File listener stopped successfully')
            return True
        except Exception as e:
            logger.error(f'Error stopping file listener: `{e}`')
            return False
            
    def is_directory_monitored(self, directory:'str') -> 'bool':
        """ Check if a directory is currently being monitored.
        
        Args:
            directory: The directory path to check
            
        Returns:
            bool: True if the directory is being monitored, False otherwise
        """
        # Normalize the path
        directory = str(Path(directory).absolute())
        return directory in self.directories

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
