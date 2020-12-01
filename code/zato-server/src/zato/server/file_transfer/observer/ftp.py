# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from traceback import format_exc

# stdlib
import os
from logging import getLogger

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
# ################################################################################################################################

class FTPObserver(BaseObserver):
    """ An observer checking remote FTP directories.
    """
    observer_impl_type = 'ftp-snapshot'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._observe_func = self.observe_with_snapshots

# ################################################################################################################################

    def path_exists(self, path):
        return os.path.exists(path)

# ################################################################################################################################

    def path_is_directory(self, path):
        return os.path.isdir(path)

# ################################################################################################################################

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

    def _start(self, observer_start_args):
        for path in self.path_list: # type: str

            # Start only for paths that are valid - all invalid ones
            # are handled by a background path inspector.
            if self.is_path_valid(path):
                logger.info('Starting local file observer `%s` for `%s` (%s)', path, self.name, self.observer_impl_type)
                spawn_greenlet(self._observe_func, path, observer_start_args)
            else:
                logger.info('Skipping invalid path `%s` for `%s` (%s)', path, self.name, self.observer_impl_type)

# ################################################################################################################################

    def is_path_valid(self, path):
        # type: (str) -> bool
        return os.path.exists(path) and os.path.isdir(path)

# ################################################################################################################################
# ################################################################################################################################
