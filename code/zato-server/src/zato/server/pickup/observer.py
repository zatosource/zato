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
import logging

# gevent
from gevent import sleep

# Watchdog
from watchdog.utils.dirsnapshot import DirectorySnapshot, DirectorySnapshotDiff

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class FSOBserver:
    """ A file-system observer used on systems other than Linux.
    This is needed for gevent interoperability.
    """

    def watch(self):
        # type: () -> None

        dir_path = '/tmp'
        snapshot = DirectorySnapshot(dir_path, recursive=False)

        while True:
            new_snapshot = DirectorySnapshot(dir_path, recursive=False)
            diff = DirectorySnapshotDiff(snapshot, new_snapshot)

            print(111, diff.files_created, diff.files_modified, diff.files_moved)

            snapshot = DirectorySnapshot(dir_path, recursive=False)

            sleep(0.25)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    watcher = FSWatcher()
    watcher.watch()
