# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from copy import deepcopy
from datetime import datetime
from logging import getLogger
from traceback import format_exc

# gevent
from gevent import sleep, spawn
from gevent.lock import RLock

# Zato
from zato.common.util.api import spawn_greenlet

# ################################################################################################################################

if 0:
    from typing import Any, Callable, Dict as dict_
    from zato.common.model.connector import ConnectorConfig

    Any = Any
    Callable = Callable
    ConnectorConfig = ConnectorConfig

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class connector_type:
    """ All types of ZeroMQ connections that we support.
    """
    class channel:
        zmq = 'ZeroMQ channel'

    class out:
        vault_conn = 'Vault connection'
        zmq = 'ZeroMQ outgoing'

    class duplex:
        amqp = 'AMQP'
        web_socket = 'WebSocket'
        zmq_v01 = 'ZeroMQ MDP v0.1'

class Inactive(Exception):
    pass

# ################################################################################################################################

class EventLogger:
    def __init__(self, enter_verb, exit_verb, enter_func, exit_func, predicate_func=None):

        self.enter_verb = enter_verb
        self.exit_verb = exit_verb

        self.enter_func = enter_func
        self.exit_func = exit_func
        self.predicate_func = predicate_func

    def __enter__(self):
        self.enter_func(self.enter_verb)

    def __exit__(self, *args, **kwargs):
        spawn_greenlet(self.exit_func, self.exit_verb, self.predicate_func)

# ################################################################################################################################

class Connector:
    """ A connector for long running background connections, such as WebSockets or AMQP. Includes means to run channels
    and outgoing connections.
    """

    # Whether that connector's start method should be called in its own greenlet
    start_in_greenlet = False

    def __init__(self, name, type, config, on_message_callback=None, auth_func=None, channels=None, outconns=None,
            parallel_server=None):
        # type: (str, str, ConnectorConfig, Callable, Callable, dict, dict, Callable) -> None
        self.name = name
        self.type = type
        self.config = config
        self.config.parallel_server = parallel_server
        self.on_message_callback = on_message_callback # Invoked by channels for each message received
        self.auth_func = auth_func # Invoked by channels that need to authenticate users

        # Service to invoke by channels for each message received
        self.service = getattr(config, 'service_name', None)

        self.channels = channels or {} # type: dict
        self.outconns = outconns or {} # type: dict

        self.id = self.config.id
        self.is_active = self.config.is_active # type: bool
        self.is_inactive = not self.is_active # type: bool
        self.is_connected = False

        self.keep_connecting = True
        self.keep_running = False
        self.lock = RLock()
        self.id_self = hex(id(self))

        # May be provided by subclasses
        self.conn = None

# ################################################################################################################################

    def get_log_details(self):
        """ Can be overridden in subclasses.
        """
        return ''

    _get_conn_string = get_prev_log_details = get_log_details

# ################################################################################################################################

    def _start_loop(self):
        """ Establishes a connection to the external resource in a loop that keeps running as long as self.is_connected is False.
        The flag must be set to True in a subclass's self._start method.
        """
        attempts = 0
        log_each = 10
        start = datetime.utcnow()

        if not self.is_active:
            logger.warning('Skipped creation of an inactive connection `%s` (%s)', self.name, self.type)
            return

        try:
            while self.keep_connecting:
                while not self.is_connected:
                    try:
                        self._start()
                    except Exception:

                        # Ok, we are not connected but it's possible that self.keep_connecting is already False,
                        # for instance, because someone deleted us even before we connected to the remote end.
                        # In this case, self.is_connected will never be True so we cannot loop indefinitely.
                        # Instead, we just need to return from the method to stop the connection attempts.
                        if not self.keep_connecting:
                            return

                        logger.warning('Caught %s exception `%s` (id:%s) (`%s` %s)',
                            self.type, format_exc(), self.id_self, self.name, self.get_log_details())
                        sleep(2)

                    # We go here if ._start did not set self.is_conneted to True.
                    # The if below is needed because we could have connected in between the sleep call and now.
                    if not self.is_connected:
                        attempts += 1
                        if attempts % log_each == 0:
                            logger.warning('Could not connect to %s (%s) after %s attempts, time spent so far: %s (id:%s)',
                                self.get_log_details(), self.name, attempts, datetime.utcnow() - start, self.id_self)

                # Ok, break from the outermost loop
                self.keep_connecting = False

            # Now that we are connected we can create all channels and outgoing connections depending on this connector.
            if self.channels:
                self.create_channels()

            if self.outconns:
                self.create_outconns()

        except KeyboardInterrupt:
            self.keep_connecting = False

# ################################################################################################################################

    def create_channels(self):
        pass

# ################################################################################################################################

    def create_outconns(self):
        pass

# ################################################################################################################################

    def create_channel(self, config):
        raise NotImplementedError('May be implemented in subclasses')

    def edit_channel(self, config):
        raise NotImplementedError('May be implemented in subclasses')

    def delete_channel(self, config):
        raise NotImplementedError('May be implemented in subclasses')

# ################################################################################################################################

    def create_outconn(self, config):
        raise NotImplementedError('May be implemented in subclasses')

    def edit_outconn(self, config):
        raise NotImplementedError('May be implemented in subclasses')

    def delete_outconn(self, config):
        raise NotImplementedError('May be implemented in subclasses')

# ################################################################################################################################

    def _start(self):
        raise NotImplementedError('Must be implemented in subclasses')

# ################################################################################################################################

    def _send(self):
        raise NotImplementedError('Must be implemented in subclasses')

# ################################################################################################################################

    def send(self, msg, *args, **kwargs):
        with self.lock:
            if self.is_inactive:
                raise Inactive('Connection `{}` is inactive ({})'.format(self.name, self.type))
            return self._send(msg, *args, **kwargs)

# ################################################################################################################################

    def _start_stop_logger(self, enter_verb, exit_verb, predicate_func=None):
        return EventLogger(enter_verb, exit_verb, self._info_start_stop, self._info_start_stop, predicate_func)

    def _info_start_stop(self, verb, predicate=None):
        log_details = self.get_prev_log_details() if 'Stop' in verb else self.get_log_details()

        # We cannot always log that the connector started or stopped because actions take place asynchronously,
        # in background. Thus we may receive a predicate function that will block until it is safe to emit a log entry.
        if verb == 'Started' and predicate:
            if not predicate():
                return

        if self.is_active:
            logger.info(
                '%s %s connector `%s` (id:%s) %s', verb, self.type, self.name, self.id_self,
                '({})'.format(log_details if log_details else self.get_log_details()))

# ################################################################################################################################

    def _wait_until_connected(self):
        """ Sleeps undefinitely until self.is_connected is True. Used as a predicate in self._start_stop_logger.
        Returns True if self.is_connected is True at the time of this method's completion. It may be False if we are
        told to stop connecting from layers above us.
        """
        while not self.is_connected:
            sleep(0.1)
            if not self.keep_connecting:
                return

        return True

# ################################################################################################################################

    def _spawn_start(self):
        spawn(self._start_loop).get()

# ################################################################################################################################

    def start(self, needs_log=True):
        if self.is_inactive:
            logger.info('Skipped creation of an inactive connector `%s` (%s)', self.name, self.type)
            return

        with self._start_stop_logger('Starting', 'Started', self._wait_until_connected):
            self.keep_running = True
            self.keep_connecting = True

            try:
                if self.start_in_greenlet:
                    spawn_greenlet(self._spawn_start, timeout=1)
                else:
                    self._start_loop()
            except Exception:
                logger.warning(format_exc())

# ################################################################################################################################

    def stop(self):
        with self._start_stop_logger('Stopping',' Stopped'):
            self._stop()
            self.keep_connecting = False # Set to False in case .stop is called before the connection was established
            self.keep_running = False

# ################################################################################################################################

    def _stop(self):
        """ Can be, but does not have to, overwritten by subclasses to customize the behaviour.
        """

# ################################################################################################################################

    def get_conn_report(self):
        raise NotImplementedError('Needs to be implemented by subclasses')

# ################################################################################################################################

class ConnectorStore:
    """ Base container for all connectors.
    """
    def __init__(self, type, connector_class, parallel_server=None):
        self.type = type
        self.connector_class = connector_class
        self.parallel_server = parallel_server
        self.connectors = {} # type: dict_[str, Connector]
        self.lock = RLock()

# ################################################################################################################################

    def _create(self, name, config, on_message_callback=None, auth_func=None, channels=None, outconns=None, needs_start=False):
        # type: (str, ConnectorConfig, Callable, Callable, dict, dict, bool)
        connector = self.connector_class(
            name, self.type, config, on_message_callback, auth_func, channels, outconns, self.parallel_server)
        self.connectors[name] = connector
        if needs_start:
            connector.start()

# ################################################################################################################################

    def create(self, name, config, on_message_callback=None, auth_func=None, channels=None, outconns=None, needs_start=False):
        # type: (str, ConnectorConfig, Callable, Callable, dict, dict, bool)
        with self.lock:
            self._create(name, config, on_message_callback, auth_func, channels, outconns, needs_start)

# ################################################################################################################################

    def _edit(self, old_name, config):
        # type: (str, ConnectorConfig)
        connector = self._delete(old_name)
        self._create(
            config.name, config, connector.on_message_callback, connector.auth_func, connector.channels,
            connector.outconns, True)

# ################################################################################################################################

    def edit(self, old_name, config, *ignored_args):
        # type: (str, Any)
        with self.lock:
            self._edit(old_name, config)

# ################################################################################################################################

    def _delete(self, name):
        # type: (str)
        connector = self.connectors[name]
        connector.stop()
        del self.connectors[name]
        return connector

# ################################################################################################################################

    def delete(self, name):
        # type: (str)
        with self.lock:
            self._delete(name)

# ################################################################################################################################

    def change_password(self, name, config):
        # type: (str, ConnectorConfig)
        with self.lock:
            new_config = deepcopy(self.connectors[name].config)
            new_config.password = config.password
            self._edit(new_config.name, new_config)

# ################################################################################################################################

    def create_channel(self, name, config):
        # type: (str, dict)
        with self.lock:
            self.connectors[name].create_channel(config)

# ################################################################################################################################

    def edit_channel(self, name, config):
        # type: (str, dict)
        with self.lock:
            self.connectors[name].edit_channel(config)

# ################################################################################################################################

    def delete_channel(self, name, config):
        # type: (str, dict)
        with self.lock:
            self.connectors[name].delete_channel(config)

# ################################################################################################################################

    def create_outconn(self, name, config):
        # type: (str, dict)
        with self.lock:
            self.connectors[name].create_outconn(config)

# ################################################################################################################################

    def edit_outconn(self, name, config):
        # type: (str, dict)
        with self.lock:
            self.connectors[name].edit_outconn(config)

# ################################################################################################################################

    def delete_outconn(self, name, config):
        # type: (str, dict)
        with self.lock:
            self.connectors[name].delete_outconn(config)

# ################################################################################################################################

    def start(self, name=None):
        # type: (str)
        with self.lock:
            for c in self.connectors.values():

                # Perhaps we want to start a single connector so we need to filter out the other ones
                if name and name != c.name:
                    continue

                c.start()

# ################################################################################################################################

    def invoke(self, name, *args, **kwargs):
        # type: (str, Any, Any)
        return self.connectors[name].invoke(*args, **kwargs)

# ################################################################################################################################

    def notify_pubsub_message(self, name, *args, **kwargs):
        # type: (str, Any, Any)
        return self.connectors[name].notify_pubsub_message(*args, **kwargs)

# ################################################################################################################################
