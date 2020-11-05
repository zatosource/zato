# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import getLogger

# Zato
from zato.common.util.api import spawn_greenlet

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class BaseObserver:
    def __init__(self, name, is_active, default_timeout):
        # type: (str, bool, float) -> None
        self.name = name
        self.is_active = is_active
        self.default_timeout = default_timeout
        self.event_handler = None
        self.path = '<initial-local-observer>'
        self.is_recursive = False
        self.keep_running = True

    def start(self):
        if self.is_active:
            spawn_greenlet(self._start)
        else:
            logger.info('Skipping an inactive file transfer channel `%s` (%s)', self.name, self.path)

    def _start(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by subclasses')

# ################################################################################################################################
# ################################################################################################################################
