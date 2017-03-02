# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime, timedelta
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

class _AMQPProducers(object):
    """ Encapsulates information about producers used by outgoing AMQP connection to send messages to a broker.
    Each outgoing connection has one _AMQPProducers object assigned.
    """
    def __init__(self, config):
        # type: (dict)
        self.config = config
        self.name = self.config.name
        self.get_conn_class_func = config.get_conn_class_func
        self.name = config.name
        self.conn = self.get_conn_class_func(
            'out/{}'.format(self.config.name))(self.config.conn_url, frame_max=self.config.frame_max)

        # Kombu uses a global object to keep all connections in (pools.connections) but we cannot use it
        # because multiple channels or outgoing connections may be using the same definition,
        # thus we need to create a new connection group for each _AMQPProducers object.

        connections = pools.register_group(pools.Connections(limit=self.config.pool_size))

        class _Producers(pools.Producers):
            def create(self, connection, limit):
                return pools.ProducerPool(connections[connection], limit=limit)

        self.pool = _Producers(limit=self.config.pool_size)

    def acquire(self, *args, **kwargs):
        return self.pool[self.conn].acquire(*args, **kwargs)

    def stop(self):
        for pool in self.pool.itervalues():
            pool.connections.force_close_all()

# ################################################################################################################################

class Consumer(object):
    """ Consumes messages from AMQP queues. There is one Consumer object for each Zato AMQP channel.
    """
    def __init__(self, config, on_message):
        # type: (dict, Callable)
        self.config = config
        self.name = self.config.name
        self.queue = [Queue(self.config.queue)]
        self.on_message = [on_message]
        self.keep_running = True
        self.is_stopped = False
        self.timeout = 0.2

# ################################################################################################################################

    def _get_consumer(self, _no_ack=no_ack):
        """ Creates a new connection and consumer to an AMQP broker.
        """
        conn = self.config.conn_class(self.config.conn_url)
        consumer = _Consumer(conn, queues=self.queue, callbacks=self.on_message, no_ack=_no_ack[self.config.ack_mode],
            tag_prefix='{}/{}'.format(self.config.consumer_tag_prefix, get_component_name('amqp-consumer')))
        consumer.consume()
        return consumer

# ################################################################################################################################

    def start(self):
        try:
            consumer = self._get_consumer()
            gevent_sleep = sleep
            has_conn = True
            timeout = self.timeout

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

            consumer.connection.close()
            self.is_stopped = True # Set to True if we break out of the main loop.

        except Exception, e:
            logger.warn('Unrecoverable exception in consumer, e:`%s`', format_exc(e))

# ################################################################################################################################

    def stop(self):
        """ Stops the consumer and wait for the confirmation that it actually is not running anymore.
        """
        self.keep_running = False

        # Wait until actually stopped.
        if not self.is_stopped:

            # self.timeout is multiplied by 2 because it's used twice in the main loop in self.start
            # plus a bit of additional time is added.
            now = datetime.utcnow()
            delta = seconds=(self.timeout * 2) + 0.2
            until = now + timedelta(seconds=delta)

            while now < until:
                sleep(0.1)
                now = datetime.utcnow()
                if self.is_stopped:
                    return

            # If we get here it means that we did not stop in the time expected, raise an exception in that case.
            raise Exception('Consumer for channel `{}` did not stop in the expected time of {}s.'.format(
                self.name, delta))

# ################################################################################################################################

class ConnectorAMQP(Connector):
    """ An AMQP connector under which channels or outgoing connections run.
    """
    start_in_greenlet = True

# ################################################################################################################################

    def _get_conn_class(self, suffix):
        """ Subclasses below are needed so as to be able to return per-greenlet/thread/process/definition
        information in an AMQO connection's zato.* properties and, except for zato.version,
        this information is not available on module level hence the classes are declared here,
        in particular, we need access to self.config.name and suffix which are available only in run-time.
        """

        class _PyAMQPConnection(PyAMQPConnection):
            def __init__(_py_amqp_self, *args, **kwargs):
                super(_PyAMQPConnection, _py_amqp_self).__init__(client_properties={
                    'zato.component':'{}/{}'.format(get_component_name('amqp-conn'), suffix),
                    'zato.version':version,
                    'zato.definition.name':self.config.name,
                }, *args, **kwargs)

        class _AMQPTransport(Transport):
            Connection = _PyAMQPConnection

        class _AMQPConnection(Connection):
            def get_transport_cls(self):
                return _AMQPTransport

        return _AMQPConnection

# ################################################################################################################################

    def _start(self):
        self._consumers = {}
        self._producers = {}
        self.config.conn_url = self._get_conn_string()

        self.is_connected = True

        test_conn = self._get_conn_class('test-conn')(self.config.conn_url, frame_max=self.config.frame_max)
        test_conn.connect()
        self.is_connected = test_conn.connected

        # Close the connection object which was needed only to confirm that the remote end can be reached.
        # Then in run-time, when connections are needed by producers or consumers, they will be opened by kombu anyway.
        # In this manner we can at least know rightaway that something is wrong with the connection's definition
        # without having to wait for a producer/consumer to be first time used. Naturally, it is possible
        # that the connection will work now but then it won't when it's needed but this is unrelated to the fact
        # that if we can already report that the connection won't work now, then we should do it so that an error message
        # can be logged as early as possible.
        test_conn.close()

# ################################################################################################################################

    def _stop(self):
        self._stop_channels()
        self._stop_producers()

# ################################################################################################################################

    def on_message(self, body, msg):
        # type: (str, Any)
        """ Invoked each time a message is taken off an AMQP queue.
        """
        msg.ack()

# ################################################################################################################################

    def _get_conn_string(self, needs_password=True):
        return 'amqp://{}:{}@{}:{}{}'.format(self.config.username, self.config.password if needs_password else SECRET_SHADOW,
            self.config.host, self.config.port, self.config.vhost)

# ################################################################################################################################

    def get_log_details(self):
        return self._get_conn_string(False)

# ################################################################################################################################

    def _enrich_channel_config(self, config):
        config.conn_class = self._get_conn_class('channel/{}'.format(config.name))
        config.conn_url = self.config.conn_url

# ################################################################################################################################

    def create_channels(self):
        """ Sets up AMQP consumers for all channels.
        """
        for config in self.channels.itervalues():
            self._enrich_channel_config(config)

            for x in xrange(config.pool_size):
                spawn(self._create_consumer, config)

# ################################################################################################################################

    def create_outconns(self):
        """ Sets up AMQP producers for outgoing connections. Called when the connector starts up thus it only creates producers
        because self.outconns entries are already available.
        """
        with self.lock:
            for config in self.outconns.itervalues():
                self._create_producers(config)

# ################################################################################################################################

    def _create_consumer(self, config):
        # type: (str)
        """ Creates an AMQP consumer for a specific queue and starts it.
        """
        consumer = Consumer(config, self.on_message)
        self._consumers.setdefault(config.name, []).append(consumer)
        consumer.start()

# ################################################################################################################################

    def _create_producers(self, config):
        # type: (dict)
        """ Creates outgoing AMQP producers using kombu.
        """
        config.conn_url = self.config.conn_url
        config.frame_max = self.config.frame_max
        config.get_conn_class_func = self._get_conn_class
        self._producers[config.name] = _AMQPProducers(config)

# ################################################################################################################################

    def _stop_channels(self):
        for config in self.channels.values():
            self._delete_channel(config)

# ################################################################################################################################

    def _stop_producers(self):
        for producer in self._producers.itervalues():
            try:
                producer.stop()
            except Exception, e:
                logger.warn('Could not stop AMQP producer `%s`, e:`%s`', producer.name, format_exc(e))
            else:
                logger.info('Stopped producer for outconn `%s` in AMQP connector `%s`', producer.name, self.config.name)

# ################################################################################################################################

    def _create_channel(self, config):
        # type: (dict)
        """ Creates a channel. Must be called with self.lock held.
        """
        self.channels[config.name] = config
        self._enrich_channel_config(config)

        for x in xrange(config.pool_size):
            spawn(self._create_consumer, config)

# ################################################################################################################################

    def create_channel(self, config):
        """ Creates a channel.
        """
        with self.lock:
            self._create_channel(config)

        logger.info('Added channel `%s` to AMQP connector `%s`', config.name, self.config.name)

# ################################################################################################################################

    def edit_channel(self, config):
        # type: (dict)
        """ Obtains self.lock and updates a channel
        """
        with self.lock:
            self._delete_channel(config)
            self._create_channel(config)

        old_name = ' ({})'.format(config.old_name) if config.old_name != config.name else ''
        logger.info('Updated channel `%s`%s in AMQP connector `%s`', config.name, old_name, config.def_name)

# ################################################################################################################################

    def _delete_channel(self, config):
        # type: (dict)
        """ Deletes a channel. Must be called with self.lock held.
        """
        # Closing consumers may take time so we report the progress after about each 5% of consumers is closed,
        # or, if there are ten consumers or less, after each connection is closed.
        consumers = self._consumers[config.name]
        total = len(consumers)
        progress_after = int(round(total * 0.05)) if total > 10 else 1
        noun = 'consumer' if total == 1 else 'consumers'

        for idx, consumer in enumerate(consumers, 1):
            consumer.stop()
            if idx % progress_after == 0:
                if idx != total:
                    logger.info(
                        'Stopped %s/%s %s for channel `%s` in AMQP connector `%s`', idx, total, noun, config.name,
                        self.config.name)

        logger.info('Stopped %s/%s %s for channel `%s` in AMQP connector `%s`', total, total, noun, config.name, self.config.name)

        del self._consumers[config.name]
        del self.channels[config.name]

# ################################################################################################################################

    def delete_channel(self, config):
        # type: (dict)
        """ Obtains self.lock and deletes a channel.
        """
        with self.lock:
            self._delete_channel(config)

        logger.info('Deleted channel `%s` from AMQP connector `%s`', config.name, self.config.name)

# ################################################################################################################################

    def _create_outconn(self, config):
        # type: (dict)
        """ Creates an outgoing connection. Must be called with self.lock held.
        """
        self.outconns[config.name] = config
        self._create_producers(config)

# ################################################################################################################################

    def create_outconn(self, config):
        # type: (dict)
        """ Creates an outgoing connection.
        """
        with self.lock:
            self._create_outconn(config)

        logger.info('Added outconn `%s` to AMQP connector `%s`', config.name, self.config.name)

# ################################################################################################################################

    def edit_outconn(self, config):
        # type: (dict)
        """ Obtains self.lock and updates an outgoing connection.
        """
        with self.lock:
            self._delete_outconn(config)
            self._create_outconn(config)

        old_name = ' ({})'.format(config.old_name) if config.old_name != config.name else ''
        logger.info('Updated outconn `%s`%s in AMQP connector `%s`', config.name, old_name, config.def_name)

# ################################################################################################################################

    def _delete_outconn(self, config):
        # type: (dict)
        """ Deletes an outgoing connection. Must be called with self.lock held.
        """
        self._producers[config.name].stop()
        del self._producers[config.name]
        del self.outconns[config.name]

# ################################################################################################################################

    def delete_outconn(self, config):
        # type: (dict)
        """ Obtains self.lock and deletes an outgoing connection.
        """
        with self.lock:
            self._delete_outconn(config)

        logger.info('Deleted outconn `%s` from AMQP connector `%s`', config.name, self.config.name)

# ################################################################################################################################

    def invoke(self, out_name, msg, exchange='/', routing_key=None, properties=None, headers=None,
            _default_out_keys=_default_out_keys, **kwargs):
        # type: (str, str, str, str, dict, dict, Any, Any)
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

        with self._producers[out_name].acquire(acquire_block, acquire_timeout) as producer:
            return producer.publish(msg, headers=headers, **kwargs)

# ################################################################################################################################
