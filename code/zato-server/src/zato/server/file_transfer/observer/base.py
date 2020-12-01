# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from logging import getLogger
from traceback import format_exc

# gevent
from gevent import sleep

# Watchdog
from watchdog.events import FileCreatedEvent, FileModifiedEvent
from watchdog.utils.dirsnapshot import DirectorySnapshot, DirectorySnapshotDiff

# Zato
from zato.common.api import FILE_TRANSFER
from zato.common.util.api import spawn_greenlet

# ################################################################################################################################

if 0:
    from zato.server.file_transfer.api import FileTransferAPI

    FileTransferAPI = FileTransferAPI

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class BaseObserver:
    observer_impl_type = '<observer-type-not-set>'

    def __init__(self, manager, channel_id, source_type, name, is_active, default_timeout):
        # type: (FileTransferAPI, int, str, str, bool, float) -> None
        self.manager = manager
        self.channel_id = channel_id
        self.source_type = source_type
        self.is_local = self.source_type == FILE_TRANSFER.SOURCE_TYPE.LOCAL.id
        self.name = name
        self.is_active = is_active
        self.default_timeout = default_timeout
        self.event_handler = None
        self.path_list = ['<initial-observer>']
        self.is_recursive = False
        self.keep_running = True

# ################################################################################################################################

    def start(self, observer_start_args):
        if self.is_active:
            spawn_greenlet(self._start, observer_start_args)
        else:
            logger.info('Skipping an inactive file transfer channel `%s` (%s)', self.name, self.path_list)

# ################################################################################################################################

    def _start(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################

    def is_path_valid(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################

    def path_exists(self, path):
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################

    def path_is_directory(self, path):
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################

    def wait_for_path(self, path, observer_start_args):
        # type: (str, BaseObserver, object, tuple) -> None

        # Local aliases
        utcnow = datetime.utcnow

        # How many times we have tried to find the correct path and since when
        idx = 0
        start = utcnow()
        log_every = 2

        # A flag indicating if path currently exists
        is_ok = False

        # This becomes True only if we learn that there is something wrong with path
        error_found = False

        # Wait until the directory exists (possibly it does already but we do not know it yet)
        while not is_ok:

            idx += 1

            # Honour the main loop's status
            if not self.keep_running:
                logger.info('Stopped `%s` path lookup function for local file transfer observer `%s` (not found) (%s)',
                    path, self.name, self.observer_impl_type)
                return

            if self.path_exists(path):

                if self.path_is_directory(path):
                    is_ok = True
                else:
                    # Indicate that there was an erorr with path
                    error_found = True

                    if idx == 1 or (idx % log_every == 0):
                        logger.warn('Local file transfer path `%s` is not a directory (%s) (c:%s d:%s t:%s)',
                            path, self.name, idx, utcnow() - start, self.observer_impl_type)
            else:
                # Indicate that there was an erorr with path
                error_found = True

                if idx == 1 or (idx % log_every == 0):
                    logger.warn('Local file transfer path `%r` does not exist (%s) (c:%s d:%s t:%s)',
                        path, self.name, idx, utcnow() - start, self.observer_impl_type)

            if is_ok:

                # Log only if had an error previously, otherwise it would emit too much to logs ..
                if error_found:
                    logger.info('Local file transfer path `%s` found successfully (%s) (c:%s d:%s t:%s)',
                        path, self.name, idx, utcnow() - start, self.observer_impl_type)

                # .. and start the observer now.
                self.start(observer_start_args)

            else:
                sleep(5)

# ################################################################################################################################

    def observe_with_snapshots(self, path, *args, **kwargs):
        """ An observer's main loop that uses snapshots.
        """
        # type: (str) -> None

        try:

            # Local aliases to avoid namespace lookups in self
            timeout = self.default_timeout
            handler_func = self.event_handler.on_created
            is_recursive = self.is_recursive

            # Take an initial snapshot
            snapshot = DirectorySnapshot(path, recursive=is_recursive)

            while self.keep_running:

                try:

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

                except FileNotFoundError:

                    # Log the error ..
                    logger.warn('File not found caught in file observer main loop `%s` (%s t:%s) e:`%s',
                        path, format_exc(), self.name, self.observer_impl_type)

                    # .. start a background inspector which will wait for the path to become available ..
                    self.manager.wait_for_deleted_path(path)

                    # .. and end the main loop.
                    return

                except Exception:
                    logger.warn('Exception in file observer main loop `%s` e:`%s (%s t:%s)',
                        path, format_exc(), self.name, self.observer_impl_type)
                finally:
                    sleep(timeout)

        except Exception:
            logger.warn('Exception in file observer `%s` e:`%s (%s t:%s)',
                path, format_exc(), self.name, self.observer_impl_type)

        # We get here only when self.keep_running is False = we are to stop
        logger.info('Stopped file transfer observer `%s` for `%s` (snapshot)', self.name, self.path)

# ################################################################################################################################
# ################################################################################################################################

class BackgroundPathInspector:
    def __init__(self, path, observer, observer_start_args=None):
        # type: (str, BaseObserver, tuple) -> None
        self.path = path
        self.observer = observer
        self.observer_start_args = observer_start_args

    def start(self):
        if self.observer.is_active:
            spawn_greenlet(self.observer.wait_for_path, self.path, self.observer_start_args)

# ################################################################################################################################
# ################################################################################################################################
