# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# gevent
from gevent.lock import RLock

class Dispatcher(object):

    def __init__(self):
        self.lock = RLock
        self.listeners = {}

    def listen(self, event, listener):
        with self.lock:
            self.listeners.setdefault(event, []).append(listener)

    def notify(self, event, opaque):
        with self.lock:
            for ev, listener in self.listeners.items():
                if ev == event:
                    listener.notify(event, opaque)

dispatcher = Dispatcher()
