# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# gevent
from gevent.lock import RLock

# PyZMQ
import zmq.green as zmq

class connector_type:
    class out:
        zmq = 'outgoing ZeroMQ'

class Inactive(Exception):
    pass

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class Connector(object):

    def __init__(self, name, type, config):
        self.name = name
        self.type = type
        self.config = config

        self.id = self.config.id
        self.is_active = self.config.is_active
        self.is_inactive = not self.is_active

        self.keep_running = False
        self.lock = RLock()

        # Must be provided by subclasses
        self.conn = None
        self.log_details = ''

# ################################################################################################################################

    def _start(self):
        raise NotImplementedError('Must be implemented in subclasses')

    _send = _start

# ################################################################################################################################

    def send(self, msg, *args, **kwargs):
        with self.lock:
            if self.is_inactive:
                raise Inactive('Connection `{}` is inactive ({})'.format(self.name, self.type))
            self._send(msg, *args, **kwargs)

# ################################################################################################################################

    def start(self):
        logger.debug('Starting %s connector `%s`', self.type, self.name)
        self._start()
        logger.info('Started %s connector `%s`%s', self.type, self.name, ' ({})'.format(
                    self.log_details) if self.log_details else '')

# ################################################################################################################################

    def stop(self):
        self.keep_running = False

# ################################################################################################################################

    def restart(self, lock=None):
        with lock or self.lock:
            self.stop()
            self.start()

# ################################################################################################################################

    def update(self, config):
        with self.lock as lock:
            self._update(config)
            self.restart(lock)

# ################################################################################################################################

    def _update(self, config):
        raise NotImplementedError()

# ################################################################################################################################

class OutZMQ(Connector):
    """ An outgoing ZeroMQ connection.
    """
    def _start(self):
        self.log_details = '{} {}'.format(self.config.socket_type, self.config.address)
        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(getattr(zmq, self.config.socket_type))
        self.conn = self.socket
        self.socket.bind(self.config.address)

    def _send(self, msg, *args, **kwargs):
        self.socket.send(msg, *args, **kwargs)

# ################################################################################################################################

class ConnectorStore(object):
    """ Base container for all connectors.
    """
    def __init__(self, type, connector_class):
        self.type = type
        self.connector_class = connector_class
        self.connectors = {}
        self.lock = RLock()

    def create(self, name, config):
        with self.lock:
            self.connectors[name] = self.connector_class(name, self.type, config)

    def update(self, old_name, config):
        with self.lock:
            self.connectors[old_name].update(config)

    def delete(self, name):
        with self.lock:
            self.connectors[name].delete(config)
            del self.connectors[name]

    def start(self):
        with self.lock:
            for c in self.connectors.values():
                c.start()
