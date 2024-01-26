# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pylint: disable=attribute-defined-outside-init

# stdlib
from datetime import datetime, timedelta
from logging import getLogger
from socket import error as socket_error
from traceback import format_exc

# amqp
from amqp.exceptions import ConnectionError as AMQPConnectionError

# gevent
from gevent import sleep, spawn

# Kombu
from kombu import Connection, Consumer as _Consumer, pools, Queue
from kombu.transport.pyamqp import Connection as PyAMQPConnection, SSLTransport, Transport

# Python 2/3 compatibility
from zato.common.ext.future.utils import itervalues
from zato.common.py23_.past.builtins import xrange

# Zato
from zato.common.api import AMQP, CHANNEL, SECRET_SHADOW
from zato.common.version import get_version
from zato.common.util.api import get_component_name
from zato.server.connection.connector import Connector, Inactive

# ################################################################################################################################

if 0:
    from bunch import Bunch
    from typing import Any, Callable

    Any = Any
    Bunch = Bunch
    Callable = Callable

# ################################################################################################################################

version = get_version()
logger = getLogger(__name__)

# ################################################################################################################################

_default_out_keys=('app_id', 'content_encoding', 'content_type', 'delivery_mode', 'expiration', 'priority', 'user_id')

# ################################################################################################################################

no_ack = {
    AMQP.ACK_MODE.ACK.id: False,
    AMQP.ACK_MODE.REJECT.id: True,
}

# ################################################################################################################################

def _is_tls_config(config):
    # type: (Bunch) -> bool
    return config.conn_url.startswith('amqps://')

# ################################################################################################################################

class _AMQPMessage:
    __slots__ = ('body', 'impl')

    def __init__(self, body, impl):
        self.body = body
        self.impl = impl

# ################################################################################################################################

class _AMQPProducers:
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
            'out/{}'.format(self.config.name), _is_tls_config(self.config))(self.config.conn_url, frame_max=self.config.frame_max)

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
        for pool in itervalues(self.pool):
            pool.connections.force_close_all()

# ################################################################################################################################

class Consumer:
    """ Consumes messages from AMQP queues. There is one Consumer object for each Zato AMQP channel.
    """
    def __init__(self, config, on_amqp_message):
        # type: (dict, Callable)
        self.config = config
        self.name = self.config.name
        self.queue = [Queue(self.config.queue)]
        self.on_amqp_message = on_amqp_message
        self.keep_running = True
        self.is_stopped = False
        self.is_connected = False # Instance-level flag indicating whether we have an active connection now.
        self.timeout = 0.35

    def _on_amqp_message(self, body, msg):
        try:
            return self.on_amqp_message(body, msg, self.name, self.config)
        except Exception:
            logger.warning(format_exc())

# ################################################################################################################################

    def _get_consumer(self, _no_ack=no_ack, _gevent_sleep=sleep):
        """ Creates a new connection and consumer to an AMQP broker.
        """

        # We cannot assume that we will obtain the consumer right-away. For instance, the remote end
        # may be currently available when we are starting. It's OK to block indefinitely (or until self.keep_running is False)
        # because we run in our own greenlet.
        consumer = None
        err_conn_attempts = 0

        while not consumer:
            if not self.keep_running:
                break

            try:
                conn = self.config.conn_class(self.config.conn_url)
                consumer = _Consumer(conn, queues=self.queue, callbacks=[self._on_amqp_message],
                    no_ack=_no_ack[self.config.ack_mode], tag_prefix='{}/{}'.format(
                        self.config.consumer_tag_prefix, get_component_name('amqp-consumer')))
                consumer.qos(prefetch_size=0, prefetch_count=self.config.prefetch_count, apply_global=False)
                consumer.consume()
            except Exception:
                err_conn_attempts += 1
                noun = 'attempts' if err_conn_attempts > 1 else 'attempt'
                logger.info('Could not create an AMQP consumer for channel `%s` (%s %s so far), e:`%s`',
                    self.name, err_conn_attempts, noun, format_exc())

                # It's fine to sleep for a longer time because if this exception happens it means that we cannot connect
                # to the server at all, which will likely mean that it is down,
                if self.keep_running:
                    _gevent_sleep(2)

        if err_conn_attempts > 0:
            noun = 'attempts' if err_conn_attempts > 1 else 'attempt'
            logger.info('Created an AMQP consumer for channel `%s` after %s %s', self.name, err_conn_attempts, noun)

        return consumer

# ################################################################################################################################

    def start(self, conn_errors=(socket_error, IOError, OSError), _gevent_sleep=sleep):
        """ Runs the AMQP consumer's mainloop.
        """
        try:

            connection = None
            consumer = self._get_consumer()
            self.is_connected = True

            # Local aliases.
            timeout = self.timeout

            # Since heartbeats run frequently (self.timeout may be a fraction of a second), we don't want to log each
            # and every error. Instead we log errors each log_every times.
            hb_errors_so_far = 0
            log_every = 20

            while self.keep_running:
                try:

                    connection = consumer.connection

                    # Do not assume the consumer still has the connection, it may have been already closed, we don't know.
                    # Unfortunately, the only way to check it is to invoke the method and catch AttributeError
                    # if connection is already None.
                    try:
                        connection.drain_events(timeout=timeout)
                    except AttributeError:
                        consumer = self._get_consumer()

                # Special-case AMQP-level connection errors and recreate the connection if any is caught.
                except AMQPConnectionError:
                    logger.warning('Caught AMQP connection error in mainloop e:`%s`', format_exc())
                    if connection:
                        connection.close()
                        consumer = self._get_consumer()

                # Regular network-level errors - assume the AMQP connection is still fine and treat it
                # as an opportunity to perform the heartbeat.
                except conn_errors:

                    try:
                        connection.heartbeat_check()
                    except Exception:
                        hb_errors_so_far += 1
                        if hb_errors_so_far % log_every == 0:
                            logger.warning('Exception in heartbeat (%s so far), e:`%s`', hb_errors_so_far, format_exc())

                        # Ok, we've lost the connection, set the flag to False and sleep for some time then.
                        if not connection:
                            self.is_connected = False

                        if self.keep_running:
                            _gevent_sleep(timeout)
                    else:
                        # Reset heartbeat errors counter since we have apparently succeeded.
                        hb_errors_so_far = 0

                        # If there was not any exception but we did not have a previous connection it means that a previously
                        # established connection was broken so we need to recreate it.
                        # But, we do it only if we are still told to keep running.
                        if self.keep_running:
                            if not self.is_connected:
                                consumer = self._get_consumer()
                                self.is_connected = True

            if connection:
                logger.info('Closing connection for `%s`', consumer)
                connection.close()
            self.is_stopped = True # Set to True if we break out of the main loop.

        except Exception:
            logger.warning('Unrecoverable exception in consumer, e:`%s`', format_exc())

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
            delta = (self.timeout * 2) + 0.2
            until = now + timedelta(seconds=delta)

            while now < until:
                sleep(0.1)
                now = datetime.utcnow()
                if self.is_stopped:
                    return

            if not self.is_connected:
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

    def _get_conn_class(self, suffix, is_tls):
        """ Subclasses below are needed so as to be able to return per-greenlet/thread/process/definition
        information in an AMQP connection's zato.* properties and, except for zato.version,
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

        class _AMQPTransport(SSLTransport if is_tls else Transport):
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

        test_conn = self._get_conn_class('test-conn', _is_tls_config(self.config))(
            self.config.conn_url, frame_max=self.config.frame_max)
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
        self._stop_consumers()
        self._stop_producers()

# ################################################################################################################################

    def on_amqp_message(self, body, msg, channel_name, channel_config, _AMQPMessage=_AMQPMessage, _CHANNEL_AMQP=CHANNEL.AMQP,
        _RECEIVED='RECEIVED', _ZATO_ACK_MODE_ACK=AMQP.ACK_MODE.ACK.id):
        """ Invoked each time a message is taken off an AMQP queue.
        """
        self.on_message_callback(
            channel_config['service_name'], body, channel=_CHANNEL_AMQP,
            data_format=channel_config['data_format'],
            zato_ctx={'zato.channel_item': {  # noqa: JS101
                'id': channel_config.id,
                'name': channel_config.name,
                'is_internal': False,
                'amqp_msg': msg,
            }}) # noqa: JS101

        if msg._state == _RECEIVED:
            if channel_config['ack_mode'] == _ZATO_ACK_MODE_ACK:
                msg.ack()
            else:
                msg.reject()

# ################################################################################################################################

    def _get_conn_string(self, needs_password=True, _amqp_prefix=('amqp://', 'amqps://')):

        host = self.config.host
        for name in _amqp_prefix:
            if host.startswith(name):
                host = host.replace(name, '')
                prefix = name
                break
        else:
            prefix = 'amqp://'

        conn_string = '{}{}:{}@{}:{}/{}'.format(prefix, self.config.username,
            self.config.password if needs_password else SECRET_SHADOW, host, self.config.port, self.config.vhost)

        return conn_string

# ################################################################################################################################

    def get_log_details(self):
        return self._get_conn_string(False)

# ################################################################################################################################

    def _enrich_channel_config(self, config):
        config.conn_class = self._get_conn_class('channel/{}'.format(config.name), _is_tls_config(self.config))
        config.conn_url = self.config.conn_url

# ################################################################################################################################

    def create_channels(self):
        """ Sets up AMQP consumers for all channels.
        """
        for config in itervalues(self.channels):
            self._enrich_channel_config(config)

            for _x in xrange(config.pool_size):
                spawn(self._create_consumer, config)

# ################################################################################################################################

    def create_outconns(self):
        """ Sets up AMQP producers for outgoing connections. Called when the connector starts up thus it only creates producers
        because self.outconns entries are already available.
        """
        with self.lock:
            for config in itervalues(self.outconns):
                self._create_producers(config)

# ################################################################################################################################

    def _create_consumer(self, config):
        # type: (str)
        """ Creates an AMQP consumer for a specific queue and starts it.
        """
        consumer = Consumer(config, self.on_amqp_message)
        self._consumers.setdefault(config.name, []).append(consumer)

        if config.is_active:
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

    def _stop_consumers(self):
        for config in self.channels.values():
            self._delete_channel(config, False)

# ################################################################################################################################

    def _stop_producers(self):
        for producer in itervalues(self._producers):
            try:
                producer.stop()
            except Exception:
                logger.warning('Could not stop AMQP producer `%s`, e:`%s`', producer.name, format_exc())
            else:
                logger.info('Stopped producer for outconn `%s` in AMQP connector `%s`', producer.name, self.config.name)

# ################################################################################################################################

    def _create_channel(self, config):
        # type: (dict)
        """ Creates a channel. Must be called with self.lock held.
        """
        self.channels[config.name] = config
        self._enrich_channel_config(config)

        for _x in xrange(config.pool_size):
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

    def _delete_channel(self, config, delete_from_channels=True):
        # type: (dict)
        """ Deletes a channel. Must be called with self.lock held.
        """
        # Closing consumers may take time so we report the progress after about each 5% of consumers is closed,
        # or, if there are ten consumers or less, after each connection is closed.
        consumers = self._consumers.get(config.name)

        # There will be no consumer objects if pool_size is 0.
        if consumers:
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

            logger.info('Stopped %s/%s %s for channel `%s` in AMQP connector `%s`',
                total, total, noun, config.name, self.config.name)

            del self._consumers[config.name]

        # Note that we do not always delete from self.channels because they may be needed in our super-class,
        # in particular, in its self.edit method.
        if delete_from_channels:
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
        # It will be old_name if this is an edit and name if it a deletion.
        _name = config.get('old_name') or config.name

        self._producers[_name].stop()
        del self._producers[_name]
        del self.outconns[_name]

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
        kwargs = {'exchange':exchange, 'routing_key':routing_key, 'mandatory':kwargs.get('mandatory')}

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
