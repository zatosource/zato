# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from traceback import format_exc

# gevent
from gevent import sleep, spawn

# Kombu
from kombu import Connection, Consumer as _Consumer, pools, Queue
from kombu.mixins import ConsumerMixin
from kombu.transport.pyamqp import Connection as PyAMQPConnection, Transport

# Zato
from zato.common import AMQP, SECRET_SHADOW, version
from zato.common.util import get_component_name, spawn_greenlet
from zato.server.connection.connector import Connector, Inactive

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

_default_out_keys=('app_id', 'content_encoding', 'content_type', 'delivery_mode', 'expiration', 'priority', 'user_id')

# ################################################################################################################################

no_ack = {
    AMQP.ACK_MODE.ACK.id: False,
    AMQP.ACK_MODE.NO_ACK.id: True,
}

# ################################################################################################################################

class Consumer(object):
    """ Consumes messages from AMQP queues. There is one Consumer object for each Zato AMQP channel.
    """
    def __init__(self, config, on_message):
        # type: (dict, Callable)
        self.config = config
        self.queue = [Queue(self.config.queue)]
        self.on_message = [on_message]
        self.keep_running = True

    def _get_consumer(self, _no_ack=no_ack):
        """ Creates a new connection and consumer to an AMQP broker.
        """
        conn = self.config.conn_class(self.config.conn_url)
        consumer = _Consumer(conn, queues=self.queue, callbacks=self.on_message, no_ack=_no_ack[self.config.ack_mode],
            tag_prefix='{}/{}'.format(self.config.consumer_tag_prefix, get_component_name('amqp-consumer')))
        consumer.consume()
        return consumer

    def start(self):
        try:
            consumer = self._get_consumer()
            gevent_sleep = sleep
            has_conn = True
            timeout = self.config.heartbeat

            while self.keep_running:
                try:
                    consumer.connection.drain_events(timeout=timeout)
                except consumer.connection.connection_errors:
                    try:
                        consumer.connection.heartbeat_check()
                    except Exception, e:
                        logger.warn('Exception in heartbeat, e:`%s`', format_exc(e))
                        has_conn = False
                        gevent_sleep(timeout)
                    else:
                        # If there was not any exception but we did not have a previous connection
                        # it means that a previously established connection was broken so we need to recreate it.
                        # one 
                        if not has_conn:
                            consumer.connection.close()
                            consumer = self._get_consumer()
                            has_conn = True

        except Exception, e:
            logger.warn('Unrecoverable exception in consumer, e:`%s`', format_exc(e))

# ################################################################################################################################

class ConnectorAMQP(Connector):
    """ An AMQP connector under which channels or outgoing connections run.
    """
    start_in_greenlet = True

# ################################################################################################################################

    def _start(self):

        # Subclasses below are needed so as to be able to return per-greenlet/thread/process/definition
        # information in an AMQO connection's zato.* properties and, except for zato.version,
        # this information is not available on module level hence the classes are declared here,
        # in particular, we need access to self.config.name which is available only in run-time.

        class _PyAMQPConnection(PyAMQPConnection):
            def __init__(_py_amqp_self, *args, **kwargs):
                super(_PyAMQPConnection, _py_amqp_self).__init__(client_properties={
                    'zato.component':get_component_name('amqp-conn'),
                    'zato.version':version,
                    'zato.definition.name':self.config.name,
                }, *args, **kwargs)

        class _AMQPTransport(Transport):
            Connection = _PyAMQPConnection

        class _AMQPConnection(Connection):
            def get_transport_cls(self):
                return _AMQPTransport

        self._consumers = []
        self._producers = {}
        self._queue_name_to_consumer = {}

        self.config.conn_class = _AMQPConnection
        self.config.conn_url = self._get_conn_string()
        self.conn = self.config.conn_class(self.config.conn_url, frame_max=self.config.frame_max, heartbeat=self.config.heartbeat)
        self.conn.connect()
        self.is_connected = self.conn.connected

        # Close the connection object which was needed only to confirm that the remote end can be reached.
        # Then in run-time, when connections are needed by producers or consumers, they will be opened by kombu anyway.
        # In this manner we can at least know rightaway that something is wrong with the connection's definition
        # without having to wait for a producer/consumer to be first time used. Naturally, it is possible
        # that the connection will work now but then it won't when it's needed but this is unrelated to the fact
        # that if we can already report that the connection won't work now, then we should do it so that an error message
        # can be logged as early as possible.
        self.conn.close()

# ################################################################################################################################

    def on_message(self, body, msg):
        # type: (str, Any)
        """ Invoked each time a messages is taken off an AMQP queue.
        """
        msg.ack()

# ################################################################################################################################

    def _create_consumer(self, config):
        # type: (str)
        """ Creates an AMQP consumer for a specific queue and starts it.
        """
        consumer = Consumer(config, self.on_message)
        consumer.start()

# ################################################################################################################################

    def create_channels(self):
        """ Sets up AMQP consumers and producers.
        """
        for channel_name, config in self.channels.iteritems():
            config.conn_class = self.config.conn_class
            config.conn_url = self.config.conn_url
            config.heartbeat = self.config.heartbeat or 1 # We always require some heartbeat value
            logger.warn(config)

            for x in xrange(config.pool_size):
                spawn(self._create_consumer, config)

# ################################################################################################################################

    def create_outconns(self):
        """ Sets up AMQP producers for outgoing connections.
        """
        self._producers = pools.Producers(limit=self.config.pool_size)

# ################################################################################################################################

    def _stop(self):
        try:
            for pool in self._producers.values():
                pool.connections.force_close_all()
        except Exception, e:
            logger.warn(format_exc(e))

# ################################################################################################################################

    def _get_conn_string(self, needs_password=True):
        return 'amqp://{}:{}@{}:{}{}'.format(self.config.username, self.config.password if needs_password else SECRET_SHADOW,
            self.config.host, self.config.port, self.config.vhost)

# ################################################################################################################################

    def get_log_details(self):
        return self._get_conn_string(False)

# ################################################################################################################################

    def create_outconn(self, config):
        with self.lock:
            self.outconns[config.name] = config

    def edit_outconn(self, config):
        with self.lock:
            del self.outconns[config.old_name]
            self.outconns[config.name] = config

    def delete_outconn(self, config):
        with self.lock:
            del self.outconns[config.name]

# ################################################################################################################################

    def invoke(self, out_name, msg, exchange='/', routing_key=None, properties=None, headers=None,
            _default_out_keys=_default_out_keys, **kwargs):
        """ Synchronously publishes a message to an AMQP broker.
        """
        with self.lock:
            outconn_config = self.outconns[out_name]

        # Don't do anything if this connection is not active
        if not outconn_config['is_active']:
            raise Inactive('Connection is inactive `{}` ({})'.format(out_name, self._get_conn_string(False)))

        acquire_block = kwargs.pop('acquire_block', True)
        acquire_timeout = kwargs.pop('acquire_block', None)

        # Dictionary of kwargs is built based on user input falling back to the defaults
        # as specified in the outgoing connection's configuration.
        properties = properties or {}
        kwargs = {'exchange':exchange, 'routing_key':routing_key}

        for key in _default_out_keys:
            # The last 'or None' is needed because outconn_config[key] may return '' which is considered
            # to be a valid value by kombu/pyamqp but not by AMQP brokers. For instance with user_id=''
            # RabbitMQ will complain that this value is not the same as the one used to open the connection,
            # however, it will accept the message with user_id=None, thus it is added at the end.
            kwargs[key] = properties.pop(key, None) or outconn_config[key] or None

        # Merge in anything that is still left in user-defined properties.
        if properties:
            kwargs.update(properties)

        with self._producers[self.conn].acquire(acquire_block, acquire_timeout) as producer:
            return producer.publish(msg, headers=headers, **kwargs)

# ################################################################################################################################
