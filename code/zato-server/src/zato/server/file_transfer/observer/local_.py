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
from datetime import datetime
from logging import getLogger

# gevent
from gevent import sleep

# inotify_simple
from inotify_simple import flags as inotify_flags, INotify

# Watchdog
from watchdog.events import FileCreatedEvent, FileModifiedEvent
from watchdog.utils.dirsnapshot import DirectorySnapshot, DirectorySnapshotDiff

# Zato
from zato.common.util.api import spawn_greenlet
from zato.common.util.platform_ import is_linux
from .base import BaseObserver

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from inotify_simple import Event as InotifyEvent

    InotifyEvent = InotifyEvent

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class _InotifyEvent:
    __slots__ = 'src_path'

    def __init__(self, src_path):
        self.src_path = src_path

# ################################################################################################################################

def _observe_path_linux(self, path):
    """ Local observer's main loop for Linux, uses inotify.
    """
    # type: (LocalObserver, str) -> None

    # The local directory may not exist yet at the time when we are starting
    # and we possibly need to wait until it does.
    self.ensure_path_exists(path)

    timeout = self.default_timeout
    handler_func = self.event_handler.on_created

    inotify = INotify()
    inotify.add_watch(path, inotify_flags.CLOSE_WRITE)

    try:
        while self.keep_running:

            try:
                for event in inotify.read(0):
                    try:
                        src_path = os.path.normpath(os.path.join(path, event.name))
                        handler_func(_InotifyEvent(src_path))
                    except Exception:
                        logger.warn('Exception in inotify handler `%s`', format_exc())
            except Exception:
                logger.warn('Exception in inotify.read() `%s`', format_exc())
            finally:
                sleep(timeout)

        # We get here only when self.keep_running is False = we are to stop
        logger.info('Stopped local file transfer observer `%s` for `%s` (inotify)', self.name, path)

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

    def ensure_path_exists(self, path):
        # type: (str) -> None

        # Local aliases
        utcnow = datetime.utcnow

        # How many times we have tried to find the correct path and since when
        idx = 0
        start = utcnow()
        log_every = 10

        # A flag indicating if path currently exists
        is_ok = False

        # This becomes True only if we learn that there is something wrong with path
        error_found = False

        # Wait until the directory exists (possibly it does already but we do not know it yet)
        while not is_ok:

            idx += 1

            # Honour the main loop's status
            if not self.keep_running:
                logger.info('Stopped `%s` path lookup function for local file transfer observer `%s` (not found)',
                    path, self.name)
                return

            if os.path.exists(path):

                if os.path.isdir(path):
                    is_ok = True
                else:
                    # Indicate that there was an erorr with path
                    error_found = True

                    if idx == 1 or (idx % log_every == 0):
                        logger.info('Local file transfer path `%s` is not a directory (%s) (c:% d:%s)',
                            path, self.name, idx, utcnow() - start)
            else:
                # Indicate that there was an erorr with path
                error_found = True

                if idx == 1 or (idx % log_every == 0):
                    #logger.info('Local file transfer path `%r` does not exist (%s) (c:%s d:%s)',
                    #    path, self.name, idx, utcnow() - start)
                    pass

            if is_ok:

                # Log only if had an error previously, otherwise it would emit too much to logs
                if error_found:
                    logger.info('Local file transfer path `%s` found successfully (%s) (c:% d:%s)',
                        path, self.name, idx, utcnow() - start)
            else:
                sleep(0.15)

# ################################################################################################################################

    def stop(self):
        logger.info('Stopping local file transfer observer `%s`', self.name)
        self.keep_running = False

# ################################################################################################################################

    def _start(self):
        for path in self.path_list: # type: str
            spawn_greenlet(self._observe_func, path)

# ################################################################################################################################
# ################################################################################################################################
