# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from traceback import format_exc

# stdlib
import os
from logging import getLogger
from shutil import copy as shutil_copy

# Zato
from zato.common.api import FILE_TRANSFER
from .base import BaseObserver

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anytuple

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class LocalObserver(BaseObserver):
    """ A local file-system observer.
    """
    observer_type_name = 'local'
    observer_type_name_title = observer_type_name.title()
    should_wait_for_deleted_paths = True

    def __init__(self, *args:'any_', **kwargs:'any_') -> 'None':
        super().__init__(*args, **kwargs)

        # Always disregard inotify
        if False and self.manager.is_notify_preferred(self.channel_config):
            self.set_local_inotify_observer()
        else:
            self.set_local_snapshot_observer()

# ################################################################################################################################

    def set_local_inotify_observer(self):
        self.observer_type_impl = FILE_TRANSFER.SOURCE_TYPE_IMPL.LOCAL_INOTIFY
        self._observe_func = self.observe_with_inotify

# ################################################################################################################################

    def set_local_snapshot_observer(self):
        self.observer_type_impl = FILE_TRANSFER.SOURCE_TYPE_IMPL.LOCAL_SNAPSHOT
        self._observe_func = self.observe_with_snapshots

# ################################################################################################################################

    def path_exists(self, path:'str', _ignored_snapshot_maker:'any_'=None) -> 'bool':
        return os.path.exists(path)

# ################################################################################################################################

    def path_is_directory(self, path:'str', _ignored_snapshot_maker:'any_'=None) -> 'bool':
        return os.path.isdir(path)

# ################################################################################################################################

    def move_file(self, path_from:'str', path_to:'str', _ignored_event:'any_', _ignored_snapshot_maker:'any_') -> 'bool':
        """ Moves a file to a selected directory.
        """
        shutil_copy(path_from, path_to)

# ################################################################################################################################

    def delete_file(self, path:'str', _ignored_snapshot_maker:'any_') -> 'None':
        """ Deletes a file pointed to by path.
        """
        os.remove(path)

# ################################################################################################################################

    def observe_with_inotify(self, path:'str', observer_start_args:'anytuple') -> 'None':
        """ Local observer's main loop for Linux, uses inotify.
        """
        try:

            inotify, inotify_flags, lock_func, wd_to_path_map = observer_start_args

            # Create a new watch descriptor
            wd = inotify.add_watch(path, inotify_flags)

            # .. and map the input path to wd for use in higher-level layers.
            with lock_func:
                wd_to_path_map[wd] = path

        except Exception:
            logger.warning("Exception in inotify observer's main loop `%s`", format_exc())

# ################################################################################################################################

    def is_path_valid(self, path):
        # type: (str) -> bool
        return self.path_exists(path) and self.path_is_directory(path)

# ################################################################################################################################
# ################################################################################################################################
