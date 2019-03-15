# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from traceback import format_exc

# gevent
from gevent.lock import RLock

# Zato
from zato.common.util import spawn_greenlet

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

# Type hints
import typing

if typing.TYPE_CHECKING:

    # Bunch
    from bunch import Bunch

    # Zato
    from zato.server.base.parallel import ParallelServer

    # For pyflakes
    Bunch = Bunch
    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

class Wrapper(object):
    """ Base class for non-queue based connections wrappers.
    """
    def __init__(self, config, server=None):
        # type: (Bunch, ParallelServer)
        self.config = config
        self.config.username_pretty = self.config.username or '(None)'
        self.server = server
        self.client = None
        self.delete_requested = False
        self.update_lock = RLock()

# ################################################################################################################################

    def build_wrapper(self):
        try:
            spawn_greenlet(self._init, timeout=2)
        except Exception:
            logger.warn('Could not initialize `%s` connection, e:`%s`', self.config.name, format_exc())

# ################################################################################################################################

    def _init(self):
        raise NotImplementedError('Must be implemented in subclasses (_init; {!r})'.format(self.config))

# ################################################################################################################################

    def _delete(self):
        raise NotImplementedError('Must be implemented in subclasses (_delete; {!r})'.format(self.config))

# ################################################################################################################################

    def _ping(self):
        # This is optional - not all connections can be pinged
        raise NotImplementedError('Can be implemented in subclasses (_ping; {!r})'.format(self.config))

# ################################################################################################################################

    def delete(self):
        if self.client:
            self._delete()

# ################################################################################################################################

    def ping(self):
        if self.client:
            self._ping()

# ################################################################################################################################
# ################################################################################################################################
