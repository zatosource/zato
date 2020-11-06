# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# gevent
from gevent.monkey import patch_all
patch_all()

# stdlib
import os
from datetime import datetime
from logging import getLogger

# gevent
from gevent import sleep

# Watchdog
from watchdog.events import FileCreatedEvent, FileModifiedEvent
from watchdog.utils.dirsnapshot import DirectorySnapshot, DirectorySnapshotDiff

# Zato
from .base import BaseObserver

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class LocalObserver(BaseObserver):
    """ A local file-system observer.
    """

    def schedule(self, event_handler, path, recursive):
        self.event_handler = event_handler
        self.path = path
        self.is_recursive = recursive

    def ensure_path_exists(self):

        # Local aliases
        timeout = self.default_timeout
        utcnow = datetime.utcnow

        # How many times we have tried to find the correct path and since when
        idx = 0
        start = utcnow()
        log_every = 10

        # A flag indicating if self.path currently exists
        is_ok = False

        # This becomes True only if we learn that there is something wrong with self.path
        error_found = False

        # Wait until the directory exists (possibly it does already but we do not know it yet)
        while not is_ok:

            idx += 1

            # Honour the main loop's status
            if not self.keep_running:
                return

            if os.path.exists(self.path):
                if os.path.isdir(self.path):
                    is_ok = True
                else:
                    # Indicate that there was an erorr with self.path
                    error_found = True

                    if idx == 1 or (idx % log_every == 0):
                        logger.warn('Local file transfer path `%s` is not a directory (%s) (c:% d:%s)',
                            self.path, self.name, idx, utcnow() - start)
            else:
                # Indicate that there was an erorr with self.path
                error_found = True

                if idx == 1 or (idx % log_every == 0):
                    logger.warn('Local file transfer path `%s` does not exist (%s) (c:%s d:%s)',
                        self.path, self.name, idx, utcnow() - start)

            if is_ok:

                # Log only if had an error previously, otherwise it would emit too much to logs
                if error_found:
                    logger.info('Local file transfer path `%s` found successfully (%s) (c:% d:%s)',
                        self.path, self.name, idx, utcnow() - start)
            else:
                sleep(6)

    def _start(self):

        # The local directory may not exist yet at the time when we are starting
        # and we possibly need to wait until it does.
        self.ensure_path_exists()

        # Local aliases to avoid namespace lookups in self
        timeout = self.default_timeout
        handler_func = self.event_handler.on_created
        path = self.path
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

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    from zato.server.pickup.api import PickupEventHandler

    manager = 111
    stanza  = 222
    config  = 333

    event_handler = PickupEventHandler(manager, stanza, config)
    path = '/tmp'
    is_recursive = False

    observer = LocalObserver()
    observer.schedule(event_handler, path, is_recursive)

    observer.start()
