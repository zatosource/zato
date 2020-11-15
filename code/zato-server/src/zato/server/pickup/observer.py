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
import os
from traceback import format_exc

# gevent
from gevent import sleep

# inotify_simple
from inotify_simple import flags as inotify_flags, INotify

# Zato
from zato.common.util import spawn_greenlet

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class _InotifyEvent:
    __slots__ = 'src_path'

    def __init__(self, src_path):
        self.src_path = src_path

# ################################################################################################################################
# ################################################################################################################################

class FSOBserver:
    """ A file-system observer used on systems other than Linux.
    This is needed for gevent interoperability.
    """
    def __init__(self, timeout=0.25):
        self.timeout = timeout
        self.event_handler = None
        self.path = '<initial-fs-observer>'
        self.is_recursive = False

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

        inotify = INotify()
        inotify.add_watch(self.path, inotify_flags.CLOSE_WRITE)

        try:
            while True:

                try:
                    for event in inotify.read():
                        try:
                            src_path = os.path.normpath(os.path.join(self.path, event.name))
                            handler_func(_InotifyEvent(src_path))
                        except Exception:
                            logger.warn('Exception in inotify handler `%s`', format_exc())
                except Exception:
                    logger.warn('Exception in inotify.read() `%s`', format_exc())
                finally:
                    sleep(timeout)
        except Exception:
            logger.warn("Exception in inotify observer's main loop `%s`", format_exc())

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

    observer = FSOBserver()
    observer.schedule(event_handler, path, is_recursive)

    observer.start()
