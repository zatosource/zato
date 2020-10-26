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
from logging import getLogger

# gevent
from gevent import sleep

# Watchdog
from watchdog.events import FileCreatedEvent, FileModifiedEvent
from watchdog.utils.dirsnapshot import DirectorySnapshot, DirectorySnapshotDiff

# Zato
from zato.common.util.api import spawn_greenlet

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class LocalObserver:
    """ A local file-system observer.
    """
    def __init__(self, timeout=0.25):
        self.timeout = timeout
        self.event_handler = None
        self.path = '<initial-local-observer>'
        self.is_recursive = False
        self.keep_running = True

    def schedule(self, event_handler, path, recursive):
        self.event_handler = event_handler
        self.path = path
        self.is_recursive = recursive

    def start(self):
        spawn_greenlet(self._start)

    def _start(self):

        # Local aliases to avoid namespace lookups in self
        timeout = self.timeout
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
