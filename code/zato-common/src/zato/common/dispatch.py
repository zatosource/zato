# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# gevent
from gevent.lock import RLock

logger = getLogger(__name__)

# ################################################################################################################################

UPDATES = 'CREATE', 'EDIT', 'DELETE', 'CHANGE_PASSWORD'

class Dispatcher:

    def __init__(self):
        self.lock = RLock()
        self.listeners = {}

    def _listen(self, event, callback, **opaque):
        self.listeners.setdefault(event, []).append((callback, opaque))

    def listen(self, *args, **kwargs):
        with self.lock:
            self._listen(*args, **kwargs)

    def listen_for_updates(self, msg, callback, **opaque):
        with self.lock:
            for name, value in msg.items():
                for update in UPDATES:
                    if update in name:
                        self._listen(value.value, callback, **opaque)

    def unlisten(self, callback):
        """ Removes the callback from all the events it was registered for, e.g. when its owner is being replaced
        during a configuration reload.
        """
        with self.lock:
            for values in self.listeners.values():
                # Note that this needs an equality check, not an identity one, because bound methods
                # are created anew each time they are accessed, so 'is' would never match.
                values[:] = [(item_callback, opaque) for item_callback, opaque in values if item_callback != callback]

    def notify(self, event, ctx):
        with self.lock:
            for ev, values in self.listeners.items():
                if ev == event:
                    for callback, opaque in values:
                        callback(event, ctx, **opaque)

# A singleton used throughout the whole application.
dispatcher = Dispatcher()
