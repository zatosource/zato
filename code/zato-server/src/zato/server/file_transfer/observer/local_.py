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

class LocalObserver(BaseObserver):
    """ A local file-system observer.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if is_linux:
            self.observer_type = 'inotify'
            self._observe_func = self.observe_with_inotify
        else:
            self.observer_type = 'snapshot'
            self._observe_func = self.observe_with_snapshots

    def schedule(self, event_handler, path_list, recursive):
        # type: (object, list, bool) -> None
        self.event_handler = event_handler
        self.path_list = path_list
        self.is_recursive = recursive

# ################################################################################################################################

    def observe_with_inotify(self, path, observer_start_args):
        """ Local observer's main loop for Linux, uses inotify.
        """
        # type: (str, tuple) -> None
        try:

            inotify, inotify_flags, lock_func, wd_to_path_map = observer_start_args

            # Create a new watch descriptor
            wd = inotify.add_watch(path, inotify_flags)

            # .. and map the input path to wd for use in higher-level layers.
            with lock_func:
                wd_to_path_map[wd] = path

        except Exception:
            logger.warn("Exception in inotify observer's main loop `%s`", format_exc())

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
                logger.info('Starting local file observer `%s` for `%s` (%s)', path, self.name, self.observer_type)
                spawn_greenlet(self._observe_func, path, observer_start_args)
            else:
                logger.info('Skipping invalid path `%s` for `%s` (%s)', path, self.name, self.observer_type)

# ################################################################################################################################

    def is_path_valid(self, path):
        # type: (str) -> bool
        return os.path.exists(path) and os.path.isdir(path)

# ################################################################################################################################
# ################################################################################################################################
