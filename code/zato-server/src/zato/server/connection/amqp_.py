# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from importlib import import_module
from logging import getLogger
from traceback import format_exc
from urllib.parse import unquote, urlparse

# gevent
from gevent import spawn

# Zato
from zato.common.api import AMQP, CHANNEL, SECRET_SHADOW
from zato.common.json_ import dumps
from zato.common.typing_ import cast_
from zato.common.util.api import new_cid_queue_consumer
from zato.common.worker_slot import is_config_process
from zato.server.connection.connector import Connector, Inactive

# Zato
from zato.input_output import ServiceInput

# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from kombu.connection import Connection as KombuAMQPConnection
    from zato.common.typing_ import any_, strdictnone, strtuple
    kombu_conn_class = type[KombuAMQPConnection]

# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################

class ModuleCtx:

    # The modules of the producers and consumers of each kind of broker, imported when a connector of that kind starts
    Kombu_Module = 'zato.server.connection.amqp_kombu'
    Azure_Module = 'zato.server.connection.amqp_azure'

# ################################################################################################################################

_default_out_keys=('app_id', 'content_encoding', 'content_type', 'delivery_mode', 'expiration', 'priority', 'user_id')

# ################################################################################################################################

# The delivery states of a message taken off a queue, the same names as kombu's
Message_State_Received = 'RECEIVED'
Message_State_Ack      = 'ACK'
Message_State_Rejected = 'REJECTED'
Message_State_Requeued = 'REQUEUED'

# ################################################################################################################################

def is_tls_config(config:'Bunch') -> 'bool':
    return config.conn_url.startswith('amqps://')

# ################################################################################################################################

def _add_auth_placeholders(address:'str') -> 'str':

    if '://' in address:
        protocol_part, server_part = address.split('://', 1)
        return f'{protocol_part}://' + '{username}:{password}@' + server_part
    else:
        return '{username}:{password}@' + address

# ################################################################################################################################

def get_conn_url(address:'str', username:'str', password:'str') -> 'str':
    """ The URL a connection to a broker is opened with - the address of a definition with its credentials in it.
    """
    conn_url = _add_auth_placeholders(address)
    out = conn_url.format(username=username, password=password)
    return out

# ################################################################################################################################

def get_connection_class(object_name:'str', suffix:'str', is_tls:'bool') -> 'kombu_conn_class':
    """ The class of the connections of kombu to an AMQP broker, from the module that imports kombu.
    """
    kombu_module = import_module(ModuleCtx.Kombu_Module)
    out = kombu_module.get_connection_class(object_name, suffix, is_tls)
    return out

# ################################################################################################################################

def _is_azure_service_bus(address:'str') -> 'bool':
    return 'servicebus.windows.net' in address

# ################################################################################################################################

# The scheme Azure Service Bus is reached over, used to complete an address given without one
_azure_scheme = 'amqps'

def _build_azure_conn_string(address:'str', username:'str', password:'str') -> 'str':

    # An address is given as host:port, the way the Dashboard and enmasse document it, or as a full amqps:// URL -
    # urlparse reads the host of a scheme-less address as its scheme, so such an address receives one first.
    if '://' not in address:
        address = f'{_azure_scheme}://{address}'

    parsed = urlparse(address)
    host = cast_('str', parsed.hostname)
    password_decoded = unquote(password)
    result = f'Endpoint=sb://{host}/;SharedAccessKeyName={username};SharedAccessKey={password_decoded}'
    return result

# ################################################################################################################################

class _AMQPMessage:
    __slots__ = ('body', 'impl')

    def __init__(self, body, impl):
        self.body = body
        self.impl = impl

# ################################################################################################################################

class ConnectorAMQP(Connector):
    """ An AMQP connector under which channels or outgoing connections run.
    """
    start_in_greenlet = True
    should_log_started_stopped = False

# ################################################################################################################################

    def _get_conn_class(self, suffix, is_tls):
        """ Returns a custom connection class for AMQP producers and consumers.
        Uses the top-level get_producer_class function to create the connection class.
        """
        return get_connection_class(self.config.name, suffix, is_tls)

# ################################################################################################################################

    def _start(self):
        self._consumers = {}
        self._producers = {}
        self.config.conn_url = self._get_conn_string()
        self.config.is_azure = _is_azure_service_bus(self.config.address)

        if self.config.is_azure:
            self.config.azure_conn_str = _build_azure_conn_string(
                self.config.address, self.config.username, self.config.password
            )
            self._start_azure()
        else:
            self._start_amqp()

    def _start_azure(self):

        # The connection string is validated here - an invalid one raises and the connector's loop retries after a pause.
        # Nothing is sent to the namespace yet, the producers and consumers connect on their own when they are used.
        azure_module = import_module(ModuleCtx.Azure_Module)
        azure_module.check_conn_str(self.config.azure_conn_str)
        self.is_connected = True

    def _start_amqp(self):

        # AMQP connectors start optimistically - channel consumers run their own reconnect loops
        # and producers connect when a message is published, so the connector reports itself
        # as connected and the test connection below only checks if the broker is reachable right now.
        self.is_connected = True

        # The connector itself has no consumer cid, so the test connection gets its own one for logging
        cid = new_cid_queue_consumer()

        test_conn:'KombuAMQPConnection' = self._get_conn_class('test-conn', is_tls_config(self.config))(self.config.conn_url)

        try:
            _ = test_conn.connect()
        except Exception as e:

            # An unreachable broker is not an error at this point - consumers and producers
            # will connect on their own once it becomes available.
            logger.info(f'[{cid}] AMQP broker not reachable now for connector `{self.name}` -> ' + \
                f'`{self.get_log_details()}` -> {e!r}')
        else:
            kombu_module = import_module(ModuleCtx.Kombu_Module)
            kombu_module.close_connection(cid, test_conn)

# ################################################################################################################################

    def _stop(self):
        self._stop_consumers()
        self._stop_producers()

# ################################################################################################################################

    def request_stop(self) -> 'None':
        """ Tells every consumer to stop without waiting for any of them, so that the consumers of many channels wind down
        in parallel and the subsequent stop finds them already finished.
        """
        for consumers in self._consumers.values():
            for consumer in consumers:
                consumer.keep_running = False

# ################################################################################################################################

    def on_amqp_message(self, body, msg, channel_name, channel_config, _AMQPMessage=_AMQPMessage, _CHANNEL_AMQP=CHANNEL.AMQP,
        _RECEIVED=Message_State_Received, _ZATO_ACK_MODE_ACK=AMQP.ACK_MODE.ACK.id):
        """ Invoked each time a message is taken off an AMQP queue.
        """
        try:
            self.on_message_callback(
                channel_config['service_name'],
                body,
                channel=_CHANNEL_AMQP,
                data_format=channel_config['data_format'],
                zato_ctx={'zato.channel_item': {  # noqa: JS101
                    'id': channel_config.id,
                    'name': channel_config.name,
                    'is_internal': False,
                    'amqp_msg': msg,
                }}) # noqa: JS101
        except Exception:
            # The service failed, reject the message and requeue it immediately so the broker
            # redelivers it right away instead of holding it until the connection is torn down.
            if msg._state == _RECEIVED:
                msg.requeue()
            raise
        else:
            if msg._state == _RECEIVED:
                if channel_config['ack_mode'] == _ZATO_ACK_MODE_ACK:
                    msg.ack()
                else:
                    msg.reject()

# ################################################################################################################################

    def _get_conn_string(self, needs_password:'bool'=True) -> 'str':

        if needs_password:
            password = self.config.password
        else:
            password = SECRET_SHADOW

        out = get_conn_url(self.config.address, self.config.username, password)
        return out

# ################################################################################################################################

    def get_log_details(self):
        return self._get_conn_string(False)

# ################################################################################################################################

    def _enrich_channel_config(self, config:'Bunch') -> 'None':
        config.conn_class = self._get_conn_class('channel/{}'.format(config.name), is_tls_config(self.config))
        config.conn_url = self.config.conn_url
        config.is_azure = self.config.is_azure
        config.azure_conn_str = getattr(self.config, 'azure_conn_str', None)

# ################################################################################################################################

    def create_channels(self):
        """ Sets up AMQP consumers for all channels.
        """
        for config in self.channels.values():
            self._enrich_channel_config(config)

            for _ in range(config.pool_size):
                _ = spawn(self._create_consumer, config)

# ################################################################################################################################

    def create_outconns(self):
        """ Sets up AMQP producers for outgoing connections. Called when the connector starts up thus it only creates producers
        because self.outconns entries are already available.
        """
        with self.lock:
            for config in self.outconns.values():
                self._create_producers(config)

# ################################################################################################################################

    def _create_consumer(self, config:'Bunch') -> 'None':
        """ Creates an AMQP consumer for a specific queue and starts it.
        """
        # The client library of the broker is imported with the first consumer of the process ..
        if config.is_azure:
            azure_module = import_module(ModuleCtx.Azure_Module)
            consumer_class = azure_module.AzureServiceBusConsumer
        else:
            kombu_module = import_module(ModuleCtx.Kombu_Module)
            consumer_class = kombu_module.Consumer

        # .. and the consumer is created.
        consumer = consumer_class(config, self.on_amqp_message)
        self._consumers.setdefault(config.name, []).append(consumer)

        # The config process of a server receives no messages, so its consumers stay as those of an inactive channel
        if config.is_active:
            if not is_config_process():
                _ = consumer.start()

# ################################################################################################################################

    def _create_producers(self, config:'Bunch') -> 'None':
        """ Creates outgoing AMQP producers.
        """
        config.conn_url = self.config.conn_url
        config.is_azure = self.config.is_azure
        config.azure_conn_str = getattr(self.config, 'azure_conn_str', None)
        config.get_conn_class_func = self._get_conn_class

        # The client library of the broker is imported with the first producer of the process.
        if config.is_azure:
            azure_module = import_module(ModuleCtx.Azure_Module)
            producer_class = azure_module.AzureServiceBusProducer
        else:
            kombu_module = import_module(ModuleCtx.Kombu_Module)
            producer_class = kombu_module.Producer

        self._producers[config.name] = producer_class(config)

# ################################################################################################################################

    def _stop_consumers(self):
        for config in self.channels.values():
            self._delete_channel(config, False)

# ################################################################################################################################

    def _stop_producers(self):
        for producer in self._producers.values():
            try:
                producer.stop()
            except Exception:
                logger.warning(f'Could not stop AMQP producer `{producer.name}`, e:`{format_exc()}`')
            else:
                logger.info(f'Stopped producer for outconn `{producer.name}` in AMQP connector `{self.config.name}`')

# ################################################################################################################################

    def _create_channel(self, config:'Bunch') -> 'None':
        """ Creates a channel. Must be called with self.lock held.
        """
        self.channels[config.name] = config
        self._enrich_channel_config(config)

        for _x in range(config.pool_size):
            _ = spawn(self._create_consumer, config)

# ################################################################################################################################

    def create_channel(self, config:'Bunch') -> 'None':
        """ Creates a channel.
        """
        with self.lock:
            self._create_channel(config)

        logger.info(f'Started AMQP channel `{config.name}` -> {self.get_log_details()}')

# ################################################################################################################################

    def _delete_channel(self, config, delete_from_channels=True):
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

            log_msg = f'Stopped {{idx}}/{total} {noun} for channel `{config.name}` in AMQP connector `{self.config.name}`'

            for idx, consumer in enumerate(consumers, 1):
                consumer.stop()
                if idx % progress_after == 0:
                    if idx != total:
                        logger.info(log_msg.format(idx=idx))

            logger.info(log_msg.format(idx=total))

            del self._consumers[config.name]

        # Note that we do not always delete from self.channels because they may be needed in our super-class,
        # in particular, in its self.edit method.
        if delete_from_channels:
            del self.channels[config.name]

# ################################################################################################################################

    def delete_channel(self, config:'Bunch') -> 'None':
        """ Obtains self.lock and deletes a channel.
        """
        with self.lock:
            self._delete_channel(config)

        logger.info(f'Deleted AMQP channel `{config.name}` -> `{self.get_log_details()}`')

# ################################################################################################################################

    def _create_outconn(self, config:'Bunch') -> 'None':
        """ Creates an outgoing connection. Must be called with self.lock held.
        """
        self.outconns[config.name] = config
        self._create_producers(config)

# ################################################################################################################################

    def create_outconn(self, config:'Bunch') -> 'None':
        """ Creates an outgoing connection.
        """
        with self.lock:
            self._create_outconn(config)

        logger.info(f'Added outconn `{config.name}` to AMQP connector `{self.config.name}`')

# ################################################################################################################################

    def _delete_outconn(self, config:'Bunch') -> 'None':
        """ Deletes an outgoing connection. Must be called with self.lock held.
        """

        # The producer is absent if it could not be created, in which case only the configuration is left to remove
        producer = self._producers.pop(config.name, None)

        if producer is not None:
            producer.stop()

        del self.outconns[config.name]

# ################################################################################################################################

    def delete_outconn(self, config:'Bunch') -> 'None':
        """ Obtains self.lock and deletes an outgoing connection.
        """
        with self.lock:
            self._delete_outconn(config)

        logger.info(f'Deleted outconn `{config.name}` from AMQP connector `{self.config.name}`')

# ################################################################################################################################

    def invoke(
        self,
        msg:'any_',
        exchange:'str'='/',
        routing_key:'str | None'=None,
        properties:'strdictnone'=None,
        headers:'strdictnone'=None,
        _default_out_keys:'strtuple'=_default_out_keys,
        **kwargs:'any_',
    ):
        """ Synchronously publishes a message to an AMQP broker. The message is text, bytes, a dict, a list
        or a service's input, the last three of which are serialized to JSON by kombu or, for Azure Service Bus, here.
        """
        out_name = self.config['name']
        with self.lock:
            outconn_config = self.outconns[out_name]

        # Don't do anything if this connection is not active
        if not outconn_config['is_active']:
            raise Inactive(f'Connection is inactive `{out_name}` ({self._get_conn_string(False)})')

        producer = self._producers[out_name]

        # A service's input is published as the dict of the fields it holds
        if isinstance(msg, ServiceInput):
            msg = msg.to_dict()

        # Azure Service Bus uses a simpler interface, its messages are text and the routing key names the queue
        if outconn_config.is_azure:
            if not routing_key:
                raise Exception(f'Publishing to Azure Service Bus through `{out_name}` requires a routing key naming the queue')
            if isinstance(msg, (dict, list)):
                msg = dumps(msg)
            return producer.publish(msg, routing_key)

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

        with producer.acquire(acquire_block, acquire_timeout) as kombu_producer:
            return kombu_producer.publish(msg, headers=headers, **kwargs)

# ################################################################################################################################

    def ping(self) -> 'None':
        """ Connects to the broker of the outgoing connection without publishing anything.
        """
        out_name = self.config['name']
        with self.lock:
            outconn_config = self.outconns[out_name]

        if not outconn_config['is_active']:
            raise Inactive(f'Connection is inactive `{out_name}` ({self._get_conn_string(False)})')

        producer = self._producers[out_name]
        producer.ping()

# ################################################################################################################################
