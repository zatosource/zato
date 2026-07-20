# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from itertools import count
from time import monotonic

# gevent
from gevent import sleep
from gevent.pywsgi import WSGIServer

# Zato
from zato.common.api import PubSub
from zato.common.audit_log.api import AuditLog
from zato.common.ext.bunch import Bunch
from zato.common.typing_ import cast_
from zato.common.util.api import new_cid_server
from zato.server.base.config_manager import ConfigManager, _pubsub_amqp_bridge_service
from zato.server.connection.amqp_ import ConnectorAMQP
from zato.server.connection.connector import Connector_Type, ConnectorStore
from zato.server.service.internal.pubsub.topic import OnAMQPMessage

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strdict

# ################################################################################################################################
# ################################################################################################################################

# The credentials a private test broker accepts.
_default_username = 'guest'
_default_password = 'guest'

# How many producer connections an outgoing connection keeps in its pool.
_default_outconn_pool_size = 10

# How long to wait for a connector or a consumer to report itself connected, in seconds.
_connect_deadline_seconds = 10

# How often the connection wait checks the flags, in seconds.
_connect_poll_seconds = 0.05

# ################################################################################################################################
# ################################################################################################################################

# The REST push listener binds to any free local port.
_listen_address = ('127.0.0.1', 0)

# The status lines the listener can answer with.
_status_lines = {
    200: '200 OK',
    500: '500 Internal Server Error',
}

_response_headers = [('Content-Type', 'text/plain')]

# ################################################################################################################################
# ################################################################################################################################

class RESTPushListener:
    """ A local HTTP endpoint standing in for a subscriber's REST push URL - it records
    every request body and answers with a configurable status code so tests can make
    push deliveries succeed or fail at will.
    """

    def __init__(self) -> 'None':
        self.received:'anylist' = []
        self.status_code = 200
        self._server = WSGIServer(_listen_address, self._handle_request, log=None)

# ################################################################################################################################

    def start(self) -> 'None':
        self._server.start()

# ################################################################################################################################

    @property
    def url(self) -> 'str':
        out = f'http://127.0.0.1:{self._server.server_port}/push'
        return out

# ################################################################################################################################

    def _handle_request(self, environ:'anydict', start_response:'any_') -> 'anylist':
        body = environ['wsgi.input'].read()
        self.received.append(body)

        start_response(_status_lines[self.status_code], _response_headers)
        return [b'']

# ################################################################################################################################

    def stop(self) -> 'None':
        self._server.stop()

# ################################################################################################################################
# ################################################################################################################################

class _ServiceChannel:
    """ What the inbound delivery service reads from self.channel.
    """
    def __init__(self, name:'str') -> 'None':
        self.name = name

# ################################################################################################################################
# ################################################################################################################################

class _ServiceRequest:
    """ What the inbound delivery service reads from self.request.
    """
    def __init__(self, raw_request:'any_') -> 'None':
        self.raw_request = raw_request

# ################################################################################################################################
# ################################################################################################################################

class _ServiceStore:
    """ What PubSubFacade reads from self.server.service_store - no known services,
    so every published name is a topic.
    """
    def __init__(self) -> 'None':
        self.name_to_impl_name:'strdict' = {}

# ################################################################################################################################
# ################################################################################################################################

class _PubSubBackend:
    """ What the config manager methods read from self.server.pubsub_backend.
    """
    def __init__(self, audit_log:'AuditLog') -> 'None':
        self.audit_log = audit_log

# ################################################################################################################################
# ################################################################################################################################

class _Server:
    """ What the production code reads from self.server - the audit log holder,
    the recording target of service push deliveries, the config manager
    for services and the service store for the facade.
    """
    def __init__(self, config_manager:'any_', audit_log:'AuditLog') -> 'None':
        self.config_manager = config_manager
        self.pubsub_backend = _PubSubBackend(audit_log)
        self.service_store = _ServiceStore()
        self.service_invocations:'anylist' = []

# ################################################################################################################################

    def invoke(self, service_name:'str', request:'any_') -> 'None':
        """ What a service push delivery calls - the invocation is recorded for assertions.
        """
        self.service_invocations.append({
            'service_name': service_name,
            'request': request,
        })

# ################################################################################################################################
# ################################################################################################################################

class PubSubAMQPHarness:
    """ The real AMQP pub/sub production classes assembled without a server - a ConnectorStore
    of ConnectorAMQP connectors, the real ConfigManager publish, inbound delivery and channel
    override methods bound to this object, and a real AuditLog behind them.
    """

    # The real production methods under test, bound to this harness.
    get_pubsub_topic_backend = ConfigManager.get_pubsub_topic_backend
    pubsub_publish_to_amqp = ConfigManager.pubsub_publish_to_amqp
    get_pubsub_topic_by_amqp_channel = ConfigManager.get_pubsub_topic_by_amqp_channel
    pubsub_deliver_amqp_message = ConfigManager.pubsub_deliver_amqp_message
    _apply_amqp_channel_override = ConfigManager._apply_amqp_channel_override
    _remove_amqp_channel_override = ConfigManager._remove_amqp_channel_override
    amqp_invoke = ConfigManager.amqp_invoke

    def __init__(self, address:'str', server_name:'str') -> 'None':

        self.address = address
        self.username = _default_username
        self.password = _default_password

        # The registries the production methods above read.
        self._topic_backends:'anydict' = {}
        self._push_subs:'anydict' = {}

        # The real connector store, built the way a server builds it.
        self.amqp_api = ConnectorStore(Connector_Type.duplex.amqp, ConnectorAMQP)

        # The real audit log all publishes and deliveries write to.
        self.audit_log = AuditLog(server_name)

        # What the production code sees as the server.
        self.server = _Server(self, self.audit_log)

        # Invocations of channel services other than the inbound delivery service -
        # what arrives after a channel override was removed.
        self.channel_invocations:'anylist' = []

        # Config object identifiers, unique within this harness.
        self._id_counter = count(1)

# ################################################################################################################################

    def _build_connection_config(self, name:'str') -> 'Bunch':
        """ The connection part every connector config shares - what a broker
        definition contributes on a real server.
        """
        config = Bunch()
        config.name = name
        config.id = next(self._id_counter)
        config.is_active = True
        config.address = self.address
        config.username = self.username
        config.password = self.password

        return config

# ################################################################################################################################

    def create_outconn(self, name:'str') -> 'Bunch':
        """ Creates a connector and an outgoing connection under one name,
        the way on_config_event_OUTGOING_AMQP_CREATE does.
        """
        config = self._build_connection_config(name)
        config.pool_size = _default_outconn_pool_size

        # The message properties an outgoing connection can default for its publishes.
        config.app_id = ''
        config.content_encoding = ''
        config.content_type = ''
        config.delivery_mode = 2
        config.expiration = ''
        config.priority = 5
        config.user_id = ''

        self.amqp_api.create(name, config, self.on_message_callback, needs_start=True)
        self.amqp_api.create_outconn(name, config)

        self._wait_until_connected(name)
        return config

# ################################################################################################################################

    def create_channel(
        self,
        name:'str',
        queue:'str',
        service_name:'str',
        prefetch_count:'int'=0,
        drain_events_timeout:'float'=0.0,
    ) -> 'Bunch':
        """ Creates a connector and a channel under one name,
        the way on_config_event_CHANNEL_AMQP_CREATE does.
        """
        config = self._build_connection_config(name)
        config.queue = queue
        config.service_name = service_name
        config.consumer_tag_prefix = 'zato-test'
        config.ack_mode = 'ack'
        config.prefetch_count = prefetch_count
        config.data_format = ''
        config.pool_size = 1

        # Perf runs shorten the drain timeout so mass channel teardown stays quick.
        if drain_events_timeout:
            config.consumer_drain_events_timeout = drain_events_timeout

        self.amqp_api.create(name, config, self.on_message_callback, needs_start=True)
        self.amqp_api.create_channel(name, config)

        self._wait_until_connected(name)
        self._wait_until_consumers_connected(name)

        return config

# ################################################################################################################################

    def delete_channel(self, name:'str') -> 'None':
        """ Deletes a channel along with its connector.
        """
        connector = self.amqp_api.connectors[name]
        config = connector.channels[name]

        self.amqp_api.delete_channel(name, config)
        _ = self.amqp_api.delete(name)

# ################################################################################################################################

    def _wait_until_connected(self, name:'str') -> 'None':
        """ Waits until a connector reports itself connected - its start runs in a greenlet.
        """
        connector = self.amqp_api.connectors[name]
        deadline = monotonic() + _connect_deadline_seconds

        while not connector.is_connected:
            if monotonic() > deadline:
                raise Exception(f'Connector `{name}` did not connect within {_connect_deadline_seconds}s')
            sleep(_connect_poll_seconds)

# ################################################################################################################################

    def _wait_until_consumers_connected(self, name:'str') -> 'None':
        """ Waits until every consumer of a channel is connected - consumers also start
        in their own greenlets and populate the connector's registry as they do.
        """
        connector = self.amqp_api.connectors[name]
        deadline = monotonic() + _connect_deadline_seconds

        while True:

            # All the consumers exist and are connected - the channel is ready.
            consumers = connector._consumers.get(name)
            if consumers and all(consumer.is_connected for consumer in consumers):
                return

            if monotonic() > deadline:
                raise Exception(f'Consumers of channel `{name}` did not connect within {_connect_deadline_seconds}s')

            sleep(_connect_poll_seconds)

# ################################################################################################################################

    def register_amqp_topic(
        self,
        topic_name:'str',
        outconn_name:'str'='',
        exchange:'str'='',
        routing_key:'str'='',
        channel_name:'str'='',
    ) -> 'strdict':
        """ Registers an AMQP-backed topic the way the registry sync does on a real server,
        applying the channel override when the topic consumes from a channel.
        """
        backend_config = {
            'backend_type': PubSub.Backend_Type.AMQP,
            'amqp_outconn_name': outconn_name,
            'amqp_exchange': exchange,
            'amqp_routing_key': routing_key,
            'amqp_channel_name': channel_name,
            'original_service_name': '',
        }
        self._topic_backends[topic_name] = backend_config

        if channel_name:
            self._apply_amqp_channel_override(backend_config)

        return backend_config

# ################################################################################################################################

    def remove_amqp_topic(self, topic_name:'str') -> 'None':
        """ Removes an AMQP-backed topic the way a topic delete does, restoring
        the channel's own service when the topic consumed from a channel.
        """
        backend_config = self._topic_backends.pop(topic_name)

        if backend_config['amqp_channel_name']:
            self._remove_amqp_channel_override(backend_config)

# ################################################################################################################################

    def add_service_push_subscription(self, topic_name:'str', sub_key:'str', service_name:'str') -> 'None':
        """ Registers a push subscription whose deliveries invoke a service.
        """
        sub_config = {
            'topic_name': topic_name,
            'sub_key': sub_key,
            'push_type': PubSub.Push_Type.Service,
            'push_service_name': service_name,
        }
        self._push_subs.setdefault(sub_key, []).append(sub_config)

# ################################################################################################################################

    def add_rest_push_subscription(self, topic_name:'str', sub_key:'str', rest_push_url:'str') -> 'None':
        """ Registers a push subscription whose deliveries go to a REST endpoint.
        """
        sub_config = {
            'topic_name': topic_name,
            'sub_key': sub_key,
            'push_type': PubSub.Push_Type.REST,
            'rest_push_url': rest_push_url,
        }
        self._push_subs.setdefault(sub_key, []).append(sub_config)

# ################################################################################################################################

    def on_message_callback(self, service_name:'str', body:'any_', **kwargs:'any_') -> 'None':
        """ What channel consumers dispatch each consumed message to - the role
        ConfigManager.invoke plays on a real server. The pub/sub inbound delivery
        service runs for real, any other service has its invocation recorded.
        """
        zato_ctx = kwargs['zato_ctx']
        channel_item = zato_ctx['zato.channel_item']

        # The channel points at the pub/sub inbound delivery service, so the real
        # service class runs with the real config manager methods underneath it ..
        if service_name == _pubsub_amqp_bridge_service:

            service = OnAMQPMessage.__new__(OnAMQPMessage)
            service.channel = cast_('any_', _ServiceChannel(channel_item['name']))
            service.request = cast_('any_', _ServiceRequest(body))
            service.server = cast_('any_', self.server)
            service.cid = new_cid_server()

            # Exceptions propagate to the consumer, which requeues the message,
            # so the broker redelivers it - the production failure semantics.
            service.handle()

        # .. any other service is the channel's own one, running after
        # .. an override was removed - the invocation is recorded only.
        else:
            self.channel_invocations.append({
                'service_name': service_name,
                'channel_name': channel_item['name'],
                'body': body,
            })

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops every consumer and producer and closes all the connectors. Consumers get
        their stop flag ahead of the sequential per-channel waits, so they all wind down
        concurrently and the teardown stays quick even with many channels.
        """
        for connector in self.amqp_api.connectors.values():
            for consumers in connector._consumers.values():
                for consumer in consumers:
                    consumer.keep_running = False

        for name in list(self.amqp_api.connectors):
            _ = self.amqp_api.delete(name)

# ################################################################################################################################
# ################################################################################################################################
