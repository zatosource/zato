# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import datetime
from logging import getLogger

# gevent
from gevent import sleep

# Zato
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
    observer_type = '<observer-type-not-set>'

    def __init__(self, manager, name, is_active, default_timeout):
        # type: (FileTransferAPI, str, bool, float) -> None
        self.manager = manager
        self.name = name
        self.is_active = is_active
        self.default_timeout = default_timeout
        self.event_handler = None
        self.path_list = ['<initial-observer>']
        self.is_recursive = False
        self.keep_running = True

# ################################################################################################################################

    def start(self, *args, **kwargs):
        if self.is_active:
            spawn_greenlet(self._start, *args, **kwargs)
        else:
            logger.info('Skipping an inactive file transfer channel `%s` (%s)', self.name, self.path)

# ################################################################################################################################

    def _start(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################

    def is_path_valid(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################

    def wait_for_path(self, path, observer, inotify, inotify_flags, inotify_lock, inotify_wd_to_path):
        # type: (str, BaseObserver, object, object, object, dict) -> None

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
                    path, self.name, observer.observer_type)
                return

            if os.path.exists(path):

                if os.path.isdir(path):
                    is_ok = True
                else:
                    # Indicate that there was an erorr with path
                    error_found = True

                    if idx == 1 or (idx % log_every == 0):
                        logger.warn('Local file transfer path `%s` is not a directory (%s) (c:%s d:%s t:%s)',
                            path, self.name, idx, utcnow() - start, observer.observer_type)
            else:
                # Indicate that there was an erorr with path
                error_found = True

                if idx == 1 or (idx % log_every == 0):
                    logger.warn('Local file transfer path `%r` does not exist (%s) (c:%s d:%s t:%s)',
                        path, self.name, idx, utcnow() - start, observer.observer_type)

            if is_ok:

                # Log only if had an error previously, otherwise it would emit too much to logs ..
                if error_found:
                    logger.info('Local file transfer path `%s` found successfully (%s) (c:%s d:%s t:%s)',
                        path, self.name, idx, utcnow() - start, observer.observer_type)

                # .. and start the observer now.
                observer.start(inotify, inotify_flags, inotify_lock, inotify_wd_to_path)

            else:
                sleep(5)

# ################################################################################################################################
# ################################################################################################################################

class BackgroundPathInspector:
    def __init__(self, path, observer, inotify=None, inotify_flags=None, inotify_lock=None, inotify_wd_to_path=None):
        # type: (str, BaseObserver, object, object, object, dict) -> None
        self.path = path
        self.observer = observer
        self.inotify = inotify
        self.inotify_flags = inotify_flags
        self.inotify_lock = inotify_lock
        self.inotify_wd_to_path = inotify_wd_to_path

    def start(self):
        spawn_greenlet(self.observer.wait_for_path, self.path, self.observer, self.inotify, self.inotify_flags,
            self.inotify_lock, self.inotify_wd_to_path)

# ################################################################################################################################
# ################################################################################################################################
