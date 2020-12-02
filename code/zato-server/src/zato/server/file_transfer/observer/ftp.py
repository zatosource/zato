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
    observer_type_impl = 'ftp-snapshot'
    observer_type_name = 'FTP'
    observer_type_name_title = observer_type_name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self._observe_func = self.observe_with_snapshots

# ################################################################################################################################

    def path_exists(self, path):
        raise NotImplementedError()

# ################################################################################################################################

    def path_is_directory(self, path):
        raise NotImplementedError()

# ################################################################################################################################

    def is_path_valid(self, path):
        # type: (str) -> bool
        raise NotImplementedError()

# ################################################################################################################################
# ################################################################################################################################
