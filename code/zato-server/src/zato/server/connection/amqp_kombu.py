# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The producers and consumers of AMQP brokers, built on kombu, which an AMQP connector imports when it starts.

# stdlib
import sys
from datetime import timedelta
from logging import getLogger
from socket import error as socket_error
from ssl import SSLError
from traceback import format_exc, format_tb

# amqp
from amqp import spec
from amqp.exceptions import ConsumerCancelled

# gevent
from gevent import sleep

# Kombu
from kombu import Connection, Consumer as KombuConsumer, pools, Queue
from kombu.transport.pyamqp import Connection as PyAMQPConnection, SSLTransport, Transport

# Zato
from zato.common.api import AMQP, PubSub
from zato.common.typing_ import cast_
from zato.common.util.api import get_component_name, new_cid_queue_consumer, utcnow, wait_for_predicate
from zato.common.version import get_version
from zato.server.connection.amqp_ import is_tls_config

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from amqp.transport import TCPTransport
    from zato.common.ext.bunch import Bunch
    from kombu.connection import Connection as KombuAMQPConnection
    from kombu.messaging import Producer as KombuProducer
    from kombu.pools import ProducerPool as KombuProducerPool
    from kombu.transport.pyamqp import Message as KombuMessage
    from zato.common.typing_ import any_, anylist, anyset, anytuple, callable_, strdict
    anylist = anylist
    anyset = anyset
    kombu_conn_class = type[KombuAMQPConnection]

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

no_ack = {
    AMQP.ACK_MODE.ACK.id: False,
    AMQP.ACK_MODE.REJECT.id: True,
}

# ################################################################################################################################
# ################################################################################################################################

def get_connection_class(object_name:'str', suffix:'str', is_tls:'bool') -> 'kombu_conn_class':

    class _PyAMQPConnection(PyAMQPConnection):
        def __init__(_py_amqp_self, *args:'any_', **kwargs:'any_') -> 'None':
            version = get_version()
            kwargs['client_properties'] = {
                'zato.component': '{}/{}'.format(get_component_name('amqp-conn'), suffix),
                'zato.version': version,
                'zato.object.name': object_name,
            }
            super(_PyAMQPConnection, _py_amqp_self).__init__(*args, **kwargs)

    class _AMQPTLSTransport(SSLTransport):
        Connection = _PyAMQPConnection

    class _AMQPPlainTransport(Transport):
        Connection = _PyAMQPConnection

    if is_tls:
        transport_class = _AMQPTLSTransport
    else:
        transport_class = _AMQPPlainTransport

    class _AMQPConnection(Connection):
        def get_transport_cls(self):
            return transport_class

    return _AMQPConnection

# ################################################################################################################################

def _close_amqp_transport(connection:'PyAMQPConnection') -> 'None':
    """ Closes the underlying AMQP transport.
    """
    # Local variables
    transport:'TCPTransport | None' = connection._transport

    connection.is_closing = True

    # Send close method to broker
    argsig = 'BsBB'
    reply_code = 0
    reply_text = 'Normal shutdown'
    method_sig = (0, 0)

    try:
        _ = connection.send_method(
            spec.Connection.Close, argsig,
            (reply_code, reply_text, method_sig[0], method_sig[1]),
            wait=spec.Connection.CloseOk,
        )
    except(OSError, SSLError):
        pass

    # Close transport
    if transport:
        transport.close()

    # Close channels
    if connection.channels:
        channels:'anylist' = []

        for elem in connection.channels.values():
            if elem is not connection:
                channels.append(elem)

        for channel in channels:
            channel.collect()

    # Clear the client reference that kombu set when it established the connection
    amqp_connection = cast_('any_', connection)
    amqp_connection.client = None

    connection.is_closing = False

# ################################################################################################################################

def _do_close_connection(cid:'str', connection:'KombuAMQPConnection', max_wait_time:'int') -> 'None':
    """ Overridden from kombu.connection.Connection._do_close_self to handle repeated close attempts.
    """

    # Local aliases
    conn_as_uri = connection.as_uri()

    # When set to True, it will indicate that we managed to close the connection
    is_closed = False

    declared_entities = cast_('anyset', connection.declared_entities)
    declared_entities.clear()

    if connection._default_channel:
        connection.maybe_close_channel(connection._default_channel)

    if connection._connection:
        start_time = utcnow()
        until = start_time + timedelta(seconds=max_wait_time)
        attempt = 0

        logger.debug(f'Will retry until {until} (start is {start_time})')

        while not is_closed:
            attempt += 1
            try:
                _close_amqp_transport(connection._connection)
            except Exception as e:
                tb = ''.join(format_tb(sys.exc_info()[2]))
                tb += repr(e)
                logger.info(f'[{cid}], Could not close AMQP connection ({attempt} attempt so far) -> `{conn_as_uri}`, e:`{tb}`')
                sleep(1)
            else:

                # If we're here, it means there was no exception above, which means we really can indicate the connection is closed.
                is_closed = True
                connection._transport = None

        connection._connection = None

# ################################################################################################################################

def close_connection(cid:'str', connection:'KombuAMQPConnection', max_wait_time:'int'=100_00_000) -> 'None':
    """ Closes a Kombu connection.
    """

    # We always go here ..
    if True:
        connection.close()

    # .. this is left for debugging purposes.
    else:
        _do_close_connection(cid, connection, max_wait_time)
        connection._do_close_transport()
        connection._debug('closed')
        connection._closed = True

# ################################################################################################################################
# ################################################################################################################################

class Producer:
    """ Encapsulates information about producers used by outgoing AMQP connection to send messages to a broker.
    Each outgoing connection has one Producer object assigned.
    """
    def __init__(self, config:'Bunch') -> 'None':
        self.config = config
        self.name = self.config.name
        self.get_conn_class_func = config.get_conn_class_func
        self.name = config.name
        self.conn = self.get_conn_class_func('out/{}'.format(self.config.name), is_tls_config(self.config))(self.config.conn_url)

        # Kombu uses a global object to keep all connections in (pools.connections) but we cannot use it
        # because multiple channels or outgoing connections may be using the same definition,
        # thus we need to create a new connection group for each Producer object.

        connections = pools.register_group(pools.Connections(limit=5000)) # self.config.pool_size))

        class _Producers(pools.Producers):
            def create(
                self,
                connection:'PyAMQPConnection', # This is actually _PyAMQPConnection but we cannot use this type here
                limit:'int'
            ) -> 'KombuProducerPool':
                result = pools.ProducerPool(connections[connection], limit=limit)
                return result

        self.pool = _Producers(limit=self.config.pool_size + 1000)

    def acquire(self, *args:'any_', **kwargs:'any_') -> 'KombuProducer':
        producers = self.pool[self.conn]
        producer = producers.acquire(*args, **kwargs)
        return producer

    def stop(self):
        for pool in self.pool.values():
            pool.connections.force_close_all()

# ################################################################################################################################
# ################################################################################################################################

class Consumer:
    """ Consumes messages from AMQP queues. There is one Consumer object for each Zato AMQP channel.
    """
    def __init__(self, config:'Bunch', on_amqp_message:'callable_') -> 'None':

        # A single correlation ID for the while lifetime of this consumer, no matter how many it (re-)connects to the broker
        self.cid = new_cid_queue_consumer()

        # Public pub/sub queues require special configuration
        if config.queue.startswith('zpsk') or config.queue in {'server', 'pubsub', 'scheduler'}:
            queue_arguments={}
        else:
            queue_arguments = None

        queue = Queue(config.queue, queue_arguments=queue_arguments)

        self.config = config
        self.name = self.config.name
        self.queue = [queue]
        self.on_amqp_message = on_amqp_message
        self._keep_running = True

        self.is_stopped = True
        self.is_connected = False # Instance-level flag indicating whether we have an active connection now.
        self.timeout = config.get('consumer_drain_events_timeout') or PubSub.Timeout.Consumer

        # This is set to True the first time self.start is called.
        self.start_called = False

# ################################################################################################################################

    @property
    def keep_running(self) -> 'bool':
        return self._keep_running

    @keep_running.setter
    def keep_running(self, value:'bool') -> 'None':
        self._keep_running = value

# ################################################################################################################################

    def _on_amqp_message(self, body:'any_', msg:'KombuMessage') -> 'any_':

        try:
            return self.on_amqp_message(body, msg, self.name, self.config)
        except Exception:
            logger.warning(f'[{self.cid}] on-amqp-message error in channel `{self.name}` -> {format_exc()}')

# ################################################################################################################################

    def _get_consumer(
        self,
        always_log_when_connected:'bool'=False,
        _no_ack:'strdict'=no_ack,
        _gevent_sleep:'callable_'=sleep,
    ) -> 'KombuConsumer':
        """ Creates a new connection and consumer to an AMQP broker.
        """

        # Log what we're about to do
        logger.debug(f'[{self.cid}] Creating a new consumer -> {self.config.conn_url}')

        # We cannot assume that we will obtain the consumer right-away. For instance, the remote end
        # may be currently available when we are starting. It's OK to block indefinitely (or until self.keep_running is False)
        # because we run in our own greenlet.
        consumer = None
        err_conn_attempts = 0

        while not consumer:
            if not self.keep_running:
                break

            try:
                conn:'KombuAMQPConnection' = self.config.conn_class(self.config.conn_url)

                tag_prefix='{}/{}'.format(self.config.consumer_tag_prefix, get_component_name('amqp-consumer'))

                consumer = KombuConsumer(
                    conn,
                    queues=self.queue,
                    callbacks=[self._on_amqp_message],
                    no_ack=_no_ack[self.config.ack_mode],
                    tag_prefix=tag_prefix
                )
                _ = consumer.qos(prefetch_size=0, prefetch_count=self.config.prefetch_count, apply_global=False)
                consumer.consume()

            except Exception as e:
                e = e
                err_conn_attempts += 1
                noun = 'attempts' if err_conn_attempts > 1 else 'attempt'
                logger.info(
                    f'[{self.cid}] Could not create an AMQP consumer for channel `{self.name}` ' +
                    f'({err_conn_attempts} {noun} so far) for queue=`{self.config.queue}` -> ' +
                    f'`{self.config.conn_url}`, e:`{e}`'
                )

                # It's fine to sleep for a longer time because if this exception happens it means that we cannot connect
                # to the server at all, which will likely mean that it is down,
                if self.keep_running:
                    _gevent_sleep(2)

        has_errors = err_conn_attempts > 0

        if always_log_when_connected or has_errors:
            base_msg = f'[{self.cid}] Created an AMQP consumer for channel `{self.name}` -> queue=`{self.config.queue}` -> `{self.config.conn_url}`'
            if has_errors:
                noun = 'attempts' if err_conn_attempts > 1 else 'attempt'
                logger.info(f'{base_msg} after {err_conn_attempts} {noun}')
            else:
                logger.info(base_msg)

        out = cast_('KombuConsumer', consumer)
        return out

# ################################################################################################################################

    def start(self, conn_errors:'anytuple'=(socket_error, IOError, OSError), _gevent_sleep:'callable_'=sleep) -> 'None':
        """ Runs the AMQP consumer's mainloop.
        """

        # Local aliases.
        timeout = self.timeout

        # Indicate that we have been called ..
        self.start_called = True
        self.is_stopped = False

        try:

            # For type hints
            connection = cast_('KombuAMQPConnection', None)
            conn_as_uri:'str' = ''

            # .. try to connection initially ..
            consumer = self._get_consumer()

            # .. if we're here, it means we have connected ..
            self.is_connected = True

            # .. keep running until told not to ..
            while self.keep_running:

                try:

                    # .. we have a consumer so we can get its connection too ..
                    connection = cast_('KombuAMQPConnection', consumer.connection)

                    # .. it'll be an empty string the first time around (per what we assigned to it above) ..
                    conn_as_uri = conn_as_uri or connection.as_uri()

                    # .. keep consuming the events from our queue ..
                    while self.keep_running:
                        try:
                            connection.drain_events(timeout=self.timeout)
                        except TimeoutError as e:
                            # .. this is as expected and we can normally ignore it, because we just haven't received anything ..
                            # .. from the underlying TCP socket within timeout seconds, but if there's an errno to show, ..
                            # .. it means the connection really was broken, so we can log that ..
                            if e.errno:
                                logger.info(f'[{self.cid}] Timeout error in {conn_as_uri} -> {e}')
                        except ConsumerCancelled as e:
                            logger.info(f'[{self.cid}] Consumer cancelled, closing connection to `{conn_as_uri}` -> `{e.message}`')

                # .. we are here on exception other than timeouts, in which case we need to reconnect ..
                except Exception:
                    try:

                        # .. this flag is to ensure we don't log too much ..
                        had_log = False

                        # .. do we still have a connection object ..
                        if connection:

                            # .. if yes, first log what'we doing ..
                            logger.info(
                                f'[{self.cid}] Closing and reconnecting a lost connection for channel=`{self.name}` -> ' +
                                f'queue=`{self.config.queue}` -> `{conn_as_uri}` -> {format_exc()}'
                            )

                            # .. indicate we've already logged a message about it ..
                            had_log = True

                            # .. now close it ..
                            close_connection(self.cid, connection)

                        # .. log what we're about to do but only if we haven't logged anything earlier ..
                        if not had_log:
                            logger.info(
                                f'[{self.cid}] Reconnecting to queue={self.config.queue} -> ' +
                                f'`{format_exc()}` -> {conn_as_uri}'
                            )

                        # .. and connect again ..
                        consumer = self._get_consumer(always_log_when_connected=True)

                    except Exception:

                        # .. OK, we've lost the connection, set the flag to False and sleep for some time then ..
                        if not connection:
                            self.is_connected = False

                        # .. do sleep for a moment before reconnecting (remember, we are under a while self.keep_running loop)
                        if self.keep_running:
                            _gevent_sleep(timeout)

                    # .. we go here if we did reconnect ..
                    else:

                        # If there was not any exception but we did not have a previous connection it means that a previously
                        # established connection was broken so we need to recreate it.
                        # But, we do it only if we are still told to keep running.
                        if self.keep_running:
                            if not self.is_connected:
                                consumer = self._get_consumer()
                                self.is_connected = True

            # .. we go here when the main while self.keep_running loop finishes ..
            if connection:

                # .. log what we're about to do ..
                logger.debug(f'[{self.cid}] Closing connection for `{consumer}`')

                # .. and do close it ..
                close_connection(self.cid, connection)

            self.is_stopped = True # Set to True if we break out of the main loop.

        except Exception:
            logger.warning(f'[{self.cid}] Unrecoverable exception in consumer, e:`{format_exc()}`')

# ################################################################################################################################

    def stop(self):
        """ Stops the consumer and wait for the confirmation that it actually is not running anymore.
        """
        self.keep_running = False

        # Wait until actually stopped.
        if not self.is_stopped:

            # self.timeout is multiplied by 2 because it's used twice in the main loop in self.start
            # plus a bit of additional time is added.
            now = utcnow()
            delta = (self.timeout * 2) + 0.2
            until = now + timedelta(seconds=delta)

            while now < until:
                sleep(0.1)
                now = utcnow()
                if self.is_stopped:
                    return

            if not self.is_connected:
                return

            # If we get here it means that we did not stop in the time expected, raise an exception in that case.
            raise Exception(f'[{self.cid}] Consumer for channel `{self.name}` did not stop in the expected time of {delta}s.')

# ################################################################################################################################

    def _is_connected(self) -> 'bool':
        return self.is_connected

# ################################################################################################################################

    def wait_until_connected(self, timeout:'int'=1) -> 'bool':
        """ Waits until the consumer is connected or timeout is reached.
        """
        connected = wait_for_predicate(
            self._is_connected,
            timeout=timeout,
            interval=0.01,
            log_msg_details=f'consumer `{self.name}` to connect',
            needs_log=True,
        )

        return connected

# ################################################################################################################################
# ################################################################################################################################
