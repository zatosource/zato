# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from logging import getLogger
from traceback import format_exc
from sys import maxsize

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
    from bunch import Bunch
    from zato.server.file_transfer.api import FileTransferAPI

    Bunch = Bunch
    FileTransferAPI = FileTransferAPI

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class BaseObserver:
    observer_type_impl = '<observer-type-impl-not-set>'
    observer_type_name = '<observer-type-name-not-set>'
    observer_type_name_title = observer_type_name.upper()

    def __init__(self, manager, channel_config, default_timeout):
        # type: (FileTransferAPI, Bunch, float) -> None
        self.manager = manager
        self.channel_config = channel_config
        self.channel_id = channel_config.id
        self.source_type = channel_config.source_type
        self.is_local = self.source_type == FILE_TRANSFER.SOURCE_TYPE.LOCAL.id
        self.name = channel_config.name
        self.is_active = channel_config.is_active
        self.default_timeout = default_timeout
        self.event_handler = None
        self.path_list = ['<initial-observer>']
        self.is_recursive = False
        self.keep_running = True

# ################################################################################################################################

    def set_up(self, event_handler, path_list, recursive):
        # type: (object, list, bool) -> None
        self.event_handler = event_handler
        self.path_list = path_list
        self.is_recursive = recursive

# ################################################################################################################################

    def start(self, observer_start_args):
        if self.is_active:
            spawn_greenlet(self._start, observer_start_args)
        else:
            logger.info('Skipping an inactive file transfer channel `%s` (%s)', self.name, self.path_list)

# ################################################################################################################################

    def stop(self):
        logger.info('Stopping %s transfer observer `%s`', self.observer_type_name, self.name)
        self.keep_running = False

# ################################################################################################################################

    def _start(self, observer_start_args):
        for path in self.path_list: # type: str

            # Start only for paths that are valid - all invalid ones
            # are handled by a background path inspector.
            if self.is_path_valid(path):
                logger.info('Starting %s observer `%s` for `%s` (%s)',
                    self.observer_type_name, path, self.name, self.observer_type_impl)
                spawn_greenlet(self._observe_func, path, observer_start_args)
            else:
                logger.info('Skipping invalid path `%s` for `%s` (%s)', path, self.name, self.observer_type_impl)

# ################################################################################################################################

    def is_path_valid(self, *args, **kwargs):
        """ Returns True if path can be used as a source for file transfer (e.g. it exists and it is a directory).
        """
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################

    def path_exists(self, path):
        """ Returns True if path exists, False otherwise.
        """
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################

    def path_is_directory(self, path):
        """ Returns True if path is a directory, False otherwise.
        """
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################

    def get_dir_snapshot(path, is_recursive):
        """ Returns an implementation-specific snapshot of a directory.
        """
        raise NotImplementedError()

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
                logger.info('Stopped `%s` path lookup function for %s transfer observer `%s` (not found) (%s)',
                    path, self.observer_type_name, self.name, self.observer_type_impl)
                return

            if self.path_exists(path):

                if self.path_is_directory(path):
                    is_ok = True
                else:
                    # Indicate that there was an erorr with path
                    error_found = True

                    if idx == 1 or (idx % log_every == 0):
                        logger.warn('%s transfer path `%s` is not a directory (%s) (c:%s d:%s t:%s)',
                            self.observer_type_name_title, self.name, idx, utcnow() - start, self.observer_type_impl)
            else:
                # Indicate that there was an erorr with path
                error_found = True

                if idx == 1 or (idx % log_every == 0):
                    logger.warn('%s transfer path `%r` does not exist (%s) (c:%s d:%s t:%s)',
                        self.observer_type_name_title, path, self.name, idx, utcnow() - start, self.observer_type_impl)

            if is_ok:

                # Log only if had an error previously, otherwise it would emit too much to logs ..
                if error_found:
                    logger.info('%s file transfer path `%s` found successfully (%s) (c:%s d:%s t:%s)',
                        self.observer_type_name_title, path, self.name, idx, utcnow() - start, self.observer_type_impl)

                # .. and start the observer now.
                self.start(observer_start_args)

            else:
                sleep(5)

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
