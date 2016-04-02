# -*- coding: utf-8 -*-

"""
Copyright (C) 2015 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# gevent
from gevent.lock import RLock

# PyZMQ
import zmq.green as zmq

# ################################################################################################################################

class Connector(object):

    def __init__(self):
        self.keep_running = False
        self.lock = RLock()

        # Must be provided by subclasses
        self._start = None
        self._send = None
        self.conn = None

# ################################################################################################################################

    def init(self):
        raise NotImplementedError('Must be implemented in subclasses')

# ################################################################################################################################

    def send(self, msg):
        with self.lock:
            self._send(msg)

# ################################################################################################################################

    def stop(self):
        self.keep_running = False

# ################################################################################################################################

    def start(self):
        self._start()

# ################################################################################################################################

    def restart(self):
        with self.lock:
            self.stop()
            self.start()

# ################################################################################################################################


class OutZMQ(Connector):
    """ An outgoing ZeroMQ connection.
    """
    def _start(self):
        self.ctx = zmq.Context()
        self.conn = self.socket = self.ctx.socket(zmq.PUB)
        self.socket.bind('tcp://127.0.0.1:55111')

    def _send(self, msg):
        self.socket.send(msg)