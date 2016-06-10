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

    class channel:
        zmq = 'channel ZeroMQ'

    class out:
        zmq = 'outgoing ZeroMQ'

class Inactive(Exception):
    pass

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class EventLogger(object):
    def __init__(self, enter_verb, exit_verb, enter_func, exit_func):

        self.enter_verb = enter_verb
        self.exit_verb = exit_verb

        self.enter_func = enter_func
        self.exit_func = exit_func

    def __enter__(self):
        self.enter_func(self.enter_verb)

    def __exit__(self, *args, **kwargs):
        self.exit_func(self.exit_verb)

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

    def _start_stop_logger(self, enter_verb, exit_verb):
        return EventLogger(enter_verb, exit_verb, self._debug_start_stop, self._info_start_stop)

    def _debug_start_stop(self, verb):
        logger.debug('%s %s connector `%s`', verb, self.type, self.name)

    def _info_start_stop(self, verb):
        logger.info('%s %s connector `%s`%s', verb, self.type, self.name, ' ({})'.format(
            self.log_details) if self.log_details else '')

# ################################################################################################################################

    def start(self, needs_log=True):
        with self._start_stop_logger('Starting',' Started'):
            self._start()

# ################################################################################################################################

    def stop(self):
        with self._start_stop_logger('Stopping',' Stopped'):
            self.keep_running = False
            self._stop()

# ################################################################################################################################

    def restart(self):
        """ Stops and starts the connector, must be called with self.lock held.
        """
        self.stop()
        self.start()

# ################################################################################################################################

    def edit(self, old_name, config):
        with self.lock:
            self._edit(old_name, config)
            self.restart()

# ################################################################################################################################

    def _edit(self, old_name, config):
        self.name = config.name
        self.config = config

# ################################################################################################################################

    def _stop(self):
        """ Can be, but does not have to, overwritten by subclasses to customize the behaviour.
        """

# ################################################################################################################################

class OutZMQSimple(Connector):
    """ An outgoing ZeroMQ connection of a type other than Majordomo (MDP).
    """
    def _start(self):
        self.log_details = '{} {}'.format(self.config.socket_type, self.config.address)
        self.ctx = zmq.Context()
        self.impl = self.ctx.socket(getattr(zmq, self.config.socket_type))
        self.conn = self
        self.impl.bind(self.config.address)

    def _send(self, msg, *args, **kwargs):
        self.impl.send(msg, *args, **kwargs)

    def _stop(self):
        self.impl.close(50) # TODO: Should be configurable

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

    def edit(self, old_name, config):
        with self.lock:
            self.connectors[old_name].edit(old_name, config)

    def delete(self, name):
        with self.lock:
            self.connectors[name].delete(config)
            del self.connectors[name]

    def start(self):
        with self.lock:
            for c in self.connectors.values():
                c.start()

# ################################################################################################################################
