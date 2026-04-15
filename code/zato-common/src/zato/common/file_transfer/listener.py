# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import fnmatch
import glob
import logging
import os
import threading

# Watchdog
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from watchdog.events import FileSystemEvent
    from watchdog.observers.api import BaseObserver
    from zato.common.typing_ import callable_, strlist, strlistnone

# ################################################################################################################################
# ################################################################################################################################

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

ignored_names = [
    '__pycache__',
    '.git',
]

ignored_suffixes = [
    '.pyc',
    '.pyo',
    '.so',
    '.pyd',
]

# ################################################################################################################################
# ################################################################################################################################

def find_base_directories(directory_path:'str', pattern:'str') -> 'strlist':
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
    """
    directory_path = os.path.abspath(directory_path)

    if not os.path.isdir(directory_path):
        raise ValueError(f'Directory does not exist: {directory_path}')

    base_dirs = []

    src_dirs = find_base_directories(directory_path, '**/src')
    base_dirs.extend(src_dirs)

    config_dirs = find_base_directories(directory_path, '**/config')
    base_dirs.extend(config_dirs)

    enmasse_matches = set()
    other_dir_matches = set()

    for pattern in pickup_order_patterns:
        if 'enmasse' in pattern:
            if pattern.startswith('**/'):
                full_pattern = os.path.join(directory_path, pattern)
            else:
                full_pattern = os.path.join(directory_path, '**/' + pattern)

            for match in glob.glob(full_pattern, recursive=True):
                if os.path.isfile(match):
                    enmasse_matches.add(match.rstrip(os.path.sep))

    for base_dir in base_dirs:
        for pattern in pickup_order_patterns:
            if 'enmasse' not in pattern:
                full_pattern = os.path.join(base_dir, '**/' + pattern)

                for match in glob.glob(full_pattern, recursive=True):
                    directory = os.path.dirname(match) if os.path.isfile(match) else match
                    other_dir_matches.add(directory.rstrip(os.path.sep))

    out = list(enmasse_matches.union(other_dir_matches))
    out = sorted(out)

    filtered_out = []
    for item in out:
        should_ignore = False

        for name in ignored_names:
            if name in item:
                should_ignore = True
                break

        if not should_ignore:
            for suffix in ignored_suffixes:
                if item.endswith(suffix):
                    should_ignore = True
                    break

        if not should_ignore:
            filtered_out.append(item)

    return filtered_out

# ################################################################################################################################
# ################################################################################################################################

def find_deepest_common_directory(directories:'list[str]') -> 'str':
    if not directories:
        return ''

    paths_components = []
    for path in directories:
        components = path.split(os.path.sep)
        paths_components.append(components)

    min_length = min(len(components) for components in paths_components)

    common_components = []
    for idx in range(min_length):
        component = paths_components[0][idx]
        if all(components[idx] == component for components in paths_components):
            common_components.append(component)
        else:
            break

    if common_components:
        out = os.path.sep.join(common_components)
        if directories[0].startswith(os.path.sep):
            out = os.path.sep + out.lstrip(os.path.sep)
        return out
    else:
        return ''

# ################################################################################################################################
# ################################################################################################################################

class ZatoFileSystemEventHandler(FileSystemEventHandler):
    """ Watches for file system events and calls a callback when a file is ready.
    """
    def __init__(
        self,
        matching_dirs:'strlist',
        on_file_ready:'callable_',
        event_types:'strlistnone'=None,
        file_patterns:'strlistnone'=None,
    ) -> 'None':
        self.matching_dirs = matching_dirs
        self.on_file_ready = on_file_ready

        self.event_types = event_types or ['created', 'deleted', 'modified', 'closed', 'closed_no_write']
        self.file_patterns = file_patterns or ['*.py', '*.yaml', '*.yml', '*.ini']

        self.file_sizes:'dict' = {}
        self.file_checks:'dict' = {}
        self.stability_threshold = 3
        self.modified_files:'set' = set()

        super().__init__()

# ################################################################################################################################

    def _is_event_relevant(self, event_path:'str', event_type:'str') -> 'bool':
        if event_type not in self.event_types:
            return False

        is_enmasse = 'enmasse' in event_path and ('.yml' in event_path or '.yaml' in event_path)

        if os.path.isdir(event_path) and not is_enmasse:
            return False

        if is_enmasse:
            return True

        matches_pattern = False
        for pattern in self.file_patterns:
            if fnmatch.fnmatch(os.path.basename(event_path), pattern):
                matches_pattern = True
                break

        if not matches_pattern:
            return False

        for dir_path in self.matching_dirs:
            if event_path.startswith(dir_path):
                return True

        return False

# ################################################################################################################################

    def _check_file_stability(self, event_path:'str') -> 'None':
        if not os.path.exists(event_path) or os.path.isdir(event_path):
            return

        current_size = os.path.getsize(event_path)

        if event_path in self.file_sizes:
            if current_size == self.file_sizes[event_path]:
                self.file_checks[event_path] += 1
                if self.file_checks[event_path] >= self.stability_threshold:
                    logger.debug('File ready (stable): %s', event_path)
                    self.on_file_ready(event_path)
                    del self.file_sizes[event_path]
                    del self.file_checks[event_path]
            else:
                self.file_sizes[event_path] = current_size
                self.file_checks[event_path] = 1
        else:
            self.file_sizes[event_path] = current_size
            self.file_checks[event_path] = 1

# ################################################################################################################################

    def on_created(self, event:'FileSystemEvent') -> 'None':
        event_path:'str' = event.src_path.rstrip(os.path.sep) # type: ignore

        if self._is_event_relevant(event_path, 'created'):
            self.modified_files.add(event_path)
            _ = self._check_file_stability(event_path)

# ################################################################################################################################

    def on_modified(self, event:'FileSystemEvent') -> 'None':
        event_path:'str' = event.src_path.rstrip(os.path.sep) # type: ignore

        if self._is_event_relevant(event_path, 'modified'):
            if not os.path.isdir(event_path):
                self.modified_files.add(event_path)
                _ = self._check_file_stability(event_path)

# ################################################################################################################################

    def on_closed(self, event:'FileSystemEvent') -> 'None':
        if self._is_event_relevant(event.src_path, 'closed'): # type: ignore
            event_path = event.src_path
            logger.debug('File closed: %s', event_path)

            if event_path in self.modified_files:
                logger.debug('File ready (closed): %s', event_path)
                self.on_file_ready(event_path) # type: ignore
                if event_path in self.file_sizes:
                    del self.file_sizes[event_path]
                    del self.file_checks[event_path]
                self.modified_files.remove(event_path)

# ################################################################################################################################

    def on_closed_no_write(self, event:'FileSystemEvent') -> 'None':
        event_path:'str' = event.src_path.rstrip(os.path.sep) # type: ignore

        is_in_matching_dir = False
        for dir_path in self.matching_dirs:
            if event_path.startswith(dir_path):
                is_in_matching_dir = True
                break

        is_enmasse = 'enmasse' in event_path and ('.yml' in event_path or '.yaml' in event_path)

        if is_in_matching_dir or is_enmasse:
            if event_path in self.modified_files:
                self.modified_files.remove(event_path)

# ################################################################################################################################

    def on_deleted(self, event:'FileSystemEvent') -> 'None':
        event_path:'str' = event.src_path.rstrip(os.path.sep) # type: ignore

        if self._is_event_relevant(event_path, 'deleted'):
            logger.info('File deleted: %s', event_path)
            if event_path in self.file_sizes:
                del self.file_sizes[event_path]
                del self.file_checks[event_path]

# ################################################################################################################################
# ################################################################################################################################

def watch_directory(
    matching_items:'strlist',
    on_file_ready:'callable_',
    event_types:'strlistnone'=None,
    file_patterns:'strlistnone'=None,
    observer_type:'str'='inotify',
) -> 'BaseObserver':
    """ Sets up a watchdog observer to monitor changes in the deepest common directory.
    """
    if observer_type == 'polling':
        observer = PollingObserver()
    elif observer_type == 'inotify':
        try:
            from watchdog.observers.inotify import InotifyObserver
            observer = InotifyObserver()
        except Exception as e:
            logger.warning('Could not create InotifyObserver, falling back to default: %s', e)
            observer = Observer()
    else:
        observer = Observer()

    watch_dir = find_deepest_common_directory(matching_items)

    event_handler = ZatoFileSystemEventHandler(matching_items, on_file_ready, event_types, file_patterns)

    _ = observer.schedule(event_handler, watch_dir, recursive=True)

    return observer

# ################################################################################################################################
# ################################################################################################################################

def start_file_listener_thread(
    server:'any_',
    watch_directories:'strlist',
    observer_type:'str'='inotify',
) -> 'threading.Thread | None':
    """ Start the file system listener as a real OS thread inside the server process.
    The listener watches the given directories and, when an enmasse file is ready,
    loads it directly into the server's ConfigStore and reloads the configuration.
    No broker is involved.
    """
    if 0:
        from zato.common.typing_ import any_

    if not watch_directories:
        logger.info('File listener: no directories to watch')
        return None

    # Build the matching items list from the provided directories
    matching_items = []
    for directory_path in watch_directories:
        directory_path = os.path.abspath(directory_path)
        if not os.path.isdir(directory_path):
            logger.info('File listener: directory does not exist, skipping: %s', directory_path)
            continue

        is_incoming_services = directory_path.rstrip(os.path.sep).endswith(os.path.join('incoming', 'services'))

        if is_incoming_services:
            matching_items.append(directory_path)
        else:
            items = find_matching_items(directory_path)
            matching_items.extend(items)

            # Always watch the directory itself for enmasse files,
            # even if find_matching_items found nothing at startup.
            if directory_path not in matching_items:
                matching_items.append(directory_path)

    if not matching_items:
        logger.info('File listener: no matching items found in watch directories')
        return None

    def _on_file_ready(file_path):
        """ Called by watchdog (from its thread) when a file is ready to be processed. """
        try:
            is_enmasse = 'enmasse' in file_path and ('.yml' in file_path or '.yaml' in file_path)
            is_static = file_path.endswith('.ini') or file_path.endswith('.zrules')
            is_python = file_path.endswith('.py')

            if is_enmasse:
                if file_path.endswith('env.ini'):
                    return
                logger.info('File listener: loading enmasse YAML from %s', file_path)
                server.config_store.load_yaml(file_path)
                try:
                    server.reload_config()
                except Exception:
                    from traceback import format_exc
                    logger.warning('File listener: enmasse loaded but reload_config failed: %s', format_exc())

            elif is_python:
                logger.debug('File listener: hot-deploying Python file %s', file_path)
                with open(file_path, 'r') as f:
                    payload = f.read()
                server.invoke('zato.hot-deploy.create', {
                    'payload': payload,
                    'payload_name': file_path,
                })

            elif is_static:
                logger.debug('File listener: processing static file %s', file_path)
                with open(file_path, 'r') as f:
                    data = f.read()
                server.invoke('zato.pickup.on-update-user-conf', {
                    'data': data,
                    'full_path': file_path,
                    'file_name': os.path.basename(file_path),
                    'relative_dir': '',
                })

            else:
                logger.debug('File listener: ignoring file %s', file_path)

        except Exception:
            from traceback import format_exc
            logger.warning('File listener: error processing %s: %s', file_path, format_exc())

    def _run():
        try:
            observer = watch_directory(
                matching_items,
                _on_file_ready,
                observer_type=observer_type,
            )
            observer.start()
            n = len(matching_items)
            logger.info('File listener started, watching %d %s (%s)', n, 'item' if n == 1 else 'items', observer_type)

            # Store observer on the server so it can be stopped later
            server._file_listener_observer = observer

            # Block this thread forever (watchdog's observer runs its own threads,
            # but we need this thread alive to keep the observer referenced).
            import time
            while not getattr(server, '_file_listener_stop', False):
                time.sleep(1)

            observer.stop()
            observer.join()
            logger.info('File listener stopped')

        except Exception:
            from traceback import format_exc
            logger.warning('File listener thread error: %s', format_exc())

    thread = threading.Thread(target=_run, name='zato-file-listener', daemon=True)
    thread.start()

    return thread

# ################################################################################################################################
# ################################################################################################################################
