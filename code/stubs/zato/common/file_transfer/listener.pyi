from typing import Any

import argparse
import fnmatch
import glob
import logging
import os
import sys
import time
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver
from watchdog.observers.inotify import InotifyObserver
from zato.broker.client import BrokerClient
from zato.common.util.api import new_cid, publish_file, publish_enmasse, publish_user_conf
from watchdog.events import FileSystemEvent
from watchdog.observers.api import BaseObserver
from zato.common.typing_ import strlist, strlistnone

def find_base_directories(directory_path: str, pattern: str) -> strlist: ...

def find_matching_items(directory_path: str) -> strlist: ...

def find_deepest_common_directory(directories: list[str]) -> str: ...

class ZatoFileSystemEventHandler(FileSystemEventHandler):
    matching_dirs: Any
    event_types: Any
    file_patterns: Any
    file_sizes: Any
    file_checks: Any
    stability_threshold: Any
    modified_files: set
    broker_client: BrokerClient
    def __init__(self: Any, matching_dirs: strlist, event_types: strlistnone, file_patterns: strlistnone) -> None: ...
    def _is_event_relevant(self: Any, event_path: str, event_type: str) -> bool: ...
    def _check_file_stability(self: Any, event_path: str) -> None: ...
    def on_created(self: Any, event: FileSystemEvent) -> None: ...
    def on_modified(self: Any, event: FileSystemEvent) -> None: ...
    def publish_file_ready_event(self: Any, event_path: str) -> None: ...
    def on_closed(self: Any, event: FileSystemEvent) -> None: ...
    def on_closed_no_write(self: Any, event: FileSystemEvent) -> None: ...
    def on_deleted(self: Any, event: FileSystemEvent) -> None: ...

def watch_directory(directory_path: str, matching_items: strlist, event_types: strlistnone, file_patterns: strlistnone, observer_type: str = ...) -> BaseObserver: ...
