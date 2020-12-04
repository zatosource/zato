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

if 0:
    from zato.server.file_transfer.snapshot import BaseSnapshotMaker

    BaseSnapshotMaker = BaseSnapshotMaker

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
    observer_type_impl = 'ftp-snapshot'
    observer_type_name = 'FTP'
    observer_type_name_title = observer_type_name

# ################################################################################################################################

    def path_exists(self, path, snapshot_maker):
        # type: (str, BaseSnapshotMaker) -> bool
        return snapshot_maker.file_client.path_exists(path)

# ################################################################################################################################

    def path_is_directory(self, path, snapshot_maker):
        # type: (str, BaseSnapshotMaker) -> bool
        raise NotImplementedError()

# ################################################################################################################################

    def is_path_valid(self, path):
        # type: (str) -> bool
        raise NotImplementedError()


# ################################################################################################################################

    def delete_file(self, path, snapshot_maker):
        """ Deletes a file pointed to by path.
        """
        # type: (str, BaseSnapshotMaker)
        snapshot_maker.file_client.delete_file(path)

# ################################################################################################################################
# ################################################################################################################################
