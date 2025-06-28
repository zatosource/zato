# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import fnmatch
import logging
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

# watchdog
from watchdog.events import DirCreatedEvent, DirModifiedEvent, FileCreatedEvent, FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

# typing
if 0:
    from typing import Dict, List, Set
    Dict = Dict
    List = List
    Set = Set

# ################################################################################################################################
# ################################################################################################################################

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('zato.file_transfer.listener')

# ################################################################################################################################
# ################################################################################################################################

# Patterns for file pickup, ordered by importance
pickup_order_patterns = [
    '  common*/**',
    '  util*/**',
    '  model*/**',
    '  core*/**',
    '  channel*/**',
    '  adapter*/**',
    '  api*/**',
    '  services*/**',
    '  **/enmasse*.y*ml',
]

# Clean up the patterns (remove leading/trailing whitespace)
pickup_order_patterns = [pattern.strip() for pattern in pickup_order_patterns]

# ################################################################################################################################
# ################################################################################################################################

class ZatoFileSystemEventHandler(FileSystemEventHandler):
    """ Custom file system event handler for Zato projects.
    """
    
    def __init__(self, root_dir:'str', patterns:'List[str]') -> 'None':
        super().__init__()
        self.root_dir = Path(root_dir)
        self.patterns = patterns
        
    def _is_path_matching_patterns(self, path:'Path') -> 'bool':
        """ Check if the path matches any of the defined patterns.
        """
        rel_path_str = str(path.relative_to(self.root_dir))
        for pattern in self.patterns:
            if fnmatch.fnmatch(rel_path_str, pattern):
                return True
        return False
    
    def on_created(self, event:'FileSystemEventHandler') -> 'None':
        path = Path(event.src_path)
        if self._is_path_matching_patterns(path):
            event_type = "directory" if isinstance(event, DirCreatedEvent) else "file"
            logger.info(f'Created {event_type}: {path}')
    
    def on_modified(self, event:'FileSystemEventHandler') -> 'None':
        path = Path(event.src_path)
        if self._is_path_matching_patterns(path):
            event_type = "directory" if isinstance(event, DirModifiedEvent) else "file"
            logger.info(f'Modified {event_type}: {path}')
            
    def on_deleted(self, event:'FileSystemEventHandler') -> 'None':
        path = Path(event.src_path)
        if self._is_path_matching_patterns(path):
            event_type = "directory" if hasattr(event, 'is_directory') and event.is_directory else "file"
            logger.info(f'Deleted {event_type}: {path}')

# ################################################################################################################################
# ################################################################################################################################

class ZatoDirectoryWatcher:
    """ Watches directories specified by Zato_Project_Root* environment variables.
    """
    
    def __init__(self, patterns:'List[str]'=None) -> 'None':
        self.patterns = patterns or pickup_order_patterns
        self.observers = {}
        self.watched_paths = defaultdict(set)
        
    def _get_project_root_dirs(self) -> 'dict':
        """ Get all environment variables starting with Zato_Project_Root.
        """
        project_roots = {}
        for key, value in os.environ.items():
            if key.startswith('Zato_Project_Root'):
                if os.path.exists(value) and os.path.isdir(value):
                    project_roots[key] = value
                else:
                    logger.warning(f'Directory specified by {key} doesn\'t exist: {value}')
        return project_roots
    
    def _find_matching_paths(self, root_dir:'str') -> 'list':
        """ Find all paths under root_dir that match any of the patterns.
        """
        matching_paths = []
        root_path = Path(root_dir)
        
        for pattern in self.patterns:
            # Use Path.glob() for recursive pattern matching
            if '**' in pattern:
                # Handle recursive patterns correctly
                matching_paths.extend([str(p) for p in root_path.glob(pattern)])
            else:
                # Handle non-recursive patterns
                matching_paths.extend([str(p) for p in root_path.glob(pattern)])
                
        return matching_paths
    
    def start_watching(self) -> 'list':
        """ Start watching all project root directories.
        """
        project_roots = self._get_project_root_dirs()
        
        if not project_roots:
            logger.warning("No Zato_Project_Root* environment variables found")
            return []
        
        initially_matched = []
        
        for env_var, root_dir in project_roots.items():
            logger.info(f'Setting up watcher for {env_var}: {root_dir}')
            matching_paths = self._find_matching_paths(root_dir)
            initially_matched.extend(matching_paths)
            
            # Set up the observer for this root directory
            observer = Observer()
            event_handler = ZatoFileSystemEventHandler(root_dir, self.patterns)
            observer.schedule(event_handler, root_dir, recursive=True)
            observer.start()
            
            self.observers[env_var] = observer
            self.watched_paths[env_var] = set(matching_paths)
            
            logger.info(f'Watching {len(matching_paths)} paths in {root_dir}')
        
        return initially_matched
    
    def stop_watching(self) -> 'None':
        """ Stop all file system observers.
        """
        for env_var, observer in self.observers.items():
            logger.info(f'Stopping observer for {env_var}')
            observer.stop()
            observer.join()
    
    def check_for_new_directories(self) -> 'None':
        """ Check if there are any new directories to watch.
        """
        current_roots = self._get_project_root_dirs()
        
        # Check for new roots
        for env_var, root_dir in current_roots.items():
            if env_var not in self.observers:
                logger.info(f'New project root detected: {env_var} -> {root_dir}')
                observer = Observer()
                event_handler = ZatoFileSystemEventHandler(root_dir, self.patterns)
                observer.schedule(event_handler, root_dir, recursive=True)
                observer.start()
                
                self.observers[env_var] = observer
                matching_paths = self._find_matching_paths(root_dir)
                self.watched_paths[env_var] = set(matching_paths)
                
                logger.info(f'Now watching {len(matching_paths)} paths in {root_dir}')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    try:
        logger.info("Starting Zato file system watcher")
        watcher = ZatoDirectoryWatcher()
        initially_matched = watcher.start_watching()
        
        # Print initially matched paths
        if initially_matched:
            logger.info(f'\nInitially matched {len(initially_matched)} paths:')
            for path in sorted(initially_matched):
                logger.info(f'  - {path}')
        else:
            logger.info("No paths initially matched the patterns")
        
        try:
            # Keep the main thread running to process file system events
            logger.info("\nWatcher is running. Press Ctrl+C to stop.")
            while True:
                # Check for new directories every minute
                watcher.check_for_new_directories()
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("\nStopping watcher due to keyboard interrupt")
            watcher.stop_watching()
            
    except Exception as e:
        logger.exception(f'Error in Zato file system watcher: {e}')
        sys.exit(1)
