# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from traceback import format_exc

# gevent
from gevent.monkey import patch_all
patch_all()

# stdlib
import os
from logging import getLogger

# gevent
from gevent import sleep

# Watchdog
from watchdog.events import FileCreatedEvent, FileModifiedEvent
from watchdog.utils.dirsnapshot import DirectorySnapshot, DirectorySnapshotDiff

# Zato
from zato.common.util.api import spawn_greenlet
from zato.common.util.platform_ import is_linux
from .base import BaseObserver

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class PathCreatedEvent:
    __slots__ = 'src_path'

    def __init__(self, src_path):
        self.src_path = src_path

# ################################################################################################################################

def _observe_path_linux(self, path, inotify, inotify_flags, lock_func, wd_to_path_map):
    """ Local observer's main loop for Linux, uses inotify.
    """
    # type: (LocalObserver, str) -> None
    try:

        # The local directory may not exist yet at the time when we are starting
        # and we possibly need to wait until it does.
        #self.ensure_path_exists(path)

        # Create a new watch descriptor
        wd = inotify.add_watch(path, inotify_flags)

        # .. and map the input path to wd for use in higher-level layers.
        with lock_func:
            wd_to_path_map[wd] = path

    except Exception:
        logger.warn("Exception in inotify observer's main loop `%s`", format_exc())

# ################################################################################################################################

def _observe_path_non_linux(self, path):
    """ Local observer's main loop for systems other than Linux, uses snapshots.
    """
    # type: (LocalObserver, str) -> None

    # The local directory may not exist yet at the time when we are starting
    # and we possibly need to wait until it does.
    self.ensure_path_exists(path)

    # Local aliases to avoid namespace lookups in self
    timeout = self.default_timeout
    handler_func = self.event_handler.on_created
    is_recursive = self.is_recursive

    # Take an initial snapshot
    snapshot = DirectorySnapshot(path, recursive=is_recursive)

    while self.keep_running:

        # The latest snapshot ..
        new_snapshot = DirectorySnapshot(path, recursive=is_recursive)

        # .. difference between the old and new will return, in particular, new or modified files ..
        diff = DirectorySnapshotDiff(snapshot, new_snapshot)

        for path_created in diff.files_created:
            handler_func(FileCreatedEvent(path_created))

        for path_modified in diff.files_modified:
            handler_func(FileModifiedEvent(path_modified))

        # .. a new snapshot which will be treated as the old one in the next iteration ..
        snapshot = DirectorySnapshot(path, recursive=is_recursive)

        sleep(timeout)

    # We get here only when self.keep_running is False = we are to stop
    logger.info('Stopped local file transfer observer `%s` for `%s` (snapshot)', self.name, self.path)

# ################################################################################################################################
# ################################################################################################################################

class LocalObserver(BaseObserver):
    """ A local file-system observer.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    if is_linux:
        _observe_func = _observe_path_linux
    else:
        _observe_func = _observe_path_non_linux

    def schedule(self, event_handler, path_list, recursive):
        # type: (object, list, bool) -> None
        self.event_handler = event_handler
        self.path_list = path_list
        self.is_recursive = recursive

# ################################################################################################################################

    def stop(self):
        logger.info('Stopping local file transfer observer `%s`', self.name)
        self.keep_running = False

# ################################################################################################################################

    def _start(self, *args, **kwargs):
        for path in self.path_list: # type: str

            # Start only for paths that are valid - all invalid ones
            # are handled by a background path inspector.
            if self.is_path_valid(path):
                logger.info('Starting local file observer `%s` for `%s` (inotify)', path, self.name)
                spawn_greenlet(self._observe_func, path, *args, **kwargs)
            else:
                logger.info('Skipping invalid path `%s` for `%s` (inotify)', path, self.name)

# ################################################################################################################################

    def is_path_valid(self, path):
        # type: (str) -> bool
        return os.path.exists(path) and os.path.isdir(path)

# ################################################################################################################################
# ################################################################################################################################
