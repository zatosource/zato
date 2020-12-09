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
from gevent import spawn
from gevent.lock import RLock

# Zato
from zato.common.util.api import spawn_greenlet

# ################################################################################################################################

logger = getLogger('zato')

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
    needs_self_client = False
    wrapper_type = '<undefined-Wrapper>'
    required_secret_attr = None
    required_secret_label = None
    build_if_not_active = False

    def __init__(self, config, server=None):
        # type: (Bunch, ParallelServer)
        self.config = config
        self.config.username_pretty = self.config.username or '(None)'
        self.server = server
        self._client = None
        self.delete_requested = False
        self.is_connected = False
        self.update_lock = RLock()

    @property
    def client(self):
        if not self._client:
            self.build_wrapper(False)
        return self._client

# ################################################################################################################################

    def build_wrapper(self, should_spawn=True):

        if not self.config.is_active:
            if not self.build_if_not_active:
                logger.info('Skipped building an inactive %s (%s)', self.wrapper_type, self.config.name)
                return

        if self.required_secret_attr:
            if not self.config[self.required_secret_attr]:
                logger.warn('Skipped building a %s without %s defined (%s)', self.wrapper_type,
                    self.required_secret_label, self.config.name)
                return

        # If we are to build the wrapper, it means that we are not connected at this time
        self.is_connected = False

        # Connection is active (config.is_active) so we can try to build it ..

        # .. in background ..
        if should_spawn:
            spawn(self._init)

        # .. or in a blocking manner
        else:
            self._init_impl()

# ################################################################################################################################

    def _init(self):
        # We use this double spawn method to be able to catch NotImplementedError immediately
        # in case subclasses do not implement self._init_impl.
        try:
            spawn_greenlet(self._init_impl, timeout=45)
        except Exception:
            logger.warn('Could not initialize %s `%s`, e:`%s`', self.wrapper_type, self.config.name, format_exc())

# ################################################################################################################################

    def _init_impl(self):
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
        if self.needs_self_client:
            if not self._client:
                return
            else:
                self._delete()
        else:
            self._delete()

# ################################################################################################################################

    def ping(self):
        if self.client:
            self._ping()

# ################################################################################################################################
# ################################################################################################################################
