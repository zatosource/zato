# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK
from json import dumps, loads
from logging import getLogger
from threading import RLock
from uuid import uuid4

# Bunch
from bunch import bunchify

# gevent
from gevent import sleep, spawn

# Kombu
from kombu.connection import Connection as KombuAMQPConnection
from kombu.entity import PERSISTENT_DELIVERY_MODE, Exchange, Queue

# requests
import requests
from requests.auth import HTTPBasicAuth

# Zato
from zato.common.api import AMQP
from zato.common.broker_message import SERVICE
from zato.common.pubsub.util import get_broker_config
from zato.common.util.api import new_cid
from zato.server.connection.amqp_ import Consumer, get_connection_class, Producer
from zato.broker.message_handler import handle_broker_msg

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Dict
    from zato.common.typing_ import any_, anydict, anydictnone, callable_, dictlist, strlist, strnone
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class BrokerClient:

    def __init__(self, *, server:'ParallelServer | None'=None, **kwargs:'any_') -> 'None':

        self.server = server
        self.lock = RLock()
        self._callbacks = {}  # type: Dict[str, callable_]
        self.correlation_to_queue_map = {}  # Maps correlation IDs to queue names for timeout handling
        self.reply_consumers = {}  # Maps reply queue names to consumers
        self.reply_consumer_started = False
        self.consumer = None

        # This is the object whose on_broker_msg_ methods will be invoked for any messages taken off a queue
        self.context = kwargs.get('context') or self

        # Get broker configuration
        broker_config = get_broker_config()

        host, port = broker_config.address.split(':')
        port = int(port)

        # Common connection URL for both producer and consumer
        conn_url = f'{broker_config.protocol}://{broker_config.username}:{broker_config.password}@{host}:{port}/{broker_config.vhost}'

        # Base component name
        component_name = 'internal'

        # What queue to listen for messages from
        queue_name = kwargs.get('queue_name')

        # Connection class factory function
        def get_conn_class_func(suffix, is_tls):
            return get_connection_class(component_name, suffix, is_tls)

        # Shared configuration for both producer and consumer
        shared_config = {
            'is_active': True,
            'conn_url': conn_url,
            'host': host,
            'port': port,
            'vhost': broker_config.vhost,
            'username': broker_config.username,
            'password': broker_config.password,
            'get_conn_class_func': get_conn_class_func,
        }

        # Configure producer
        producer_config = bunchify(dict(shared_config, **{
            'name': f'{component_name}-producer',
            'frame_max': 128000,
            'heartbeat': 30,
            'pool_size': 10,
        }))

        self.producer = Producer(producer_config)

        # Configure consumer
        consumer_config = bunchify(dict(shared_config, **{
            'name': f'{component_name}-consumer',
            'queue': queue_name,
            'consumer_tag_prefix': 'zato-broker',
            'ack_mode': AMQP.ACK_MODE.ACK.id,
            'prefetch_count': 1,
            'conn_class': KombuAMQPConnection,
        }))

        self.consumer_config = consumer_config

        # For managing reply consumers
        self.reply_consumers = {}  # Maps reply queue names to consumers
        self.reply_consumer_started = False

# ################################################################################################################################

    def publish(self, msg:'anydict', *ignored_args:'any_', **kwargs:'any_') -> 'any_':
        """ Publishes a message to the AMQP broker.
        """
        msg = dumps(msg) # type: ignore

        exchange    = kwargs.get('exchange') or 'components'
        routing_key = kwargs.get('routing_key') or 'server'

        with self.producer.acquire() as client:
            client.publish(
                msg,
                exchange=exchange,
                routing_key=routing_key,
                content_type='application/json',
                delivery_mode=PERSISTENT_DELIVERY_MODE
            )

    invoke_async = publish

# ################################################################################################################################

    def publish_to_queue(self, queue_name:'str', msg:'any_', correlation_id:'str'='') -> 'None':
        """ Publishes a message directly to a specific queue.
        """
        logger.info(f'Publishing to queue `{queue_name}`, correlation_id:`{correlation_id}`')

        if not isinstance(msg, str):
            msg = dumps(msg)
            logger.debug(f'Converted message to string: {msg[:100]}...' if len(msg) > 100 else msg)

        # Prepare publish parameters
        publish_kwargs = {
            'exchange': '',  # Default exchange
            'routing_key': queue_name,  # Queue name as routing key
            'content_type': 'application/json',
            'delivery_mode': PERSISTENT_DELIVERY_MODE,
        }

        # Add correlation ID if provided
        if correlation_id:
            publish_kwargs['correlation_id'] = correlation_id

        # Publish the message
        with self.producer.acquire() as client:
            logger.debug(f'Producer connection acquired: {client}')
            _ = client.publish(msg, **publish_kwargs)

# ################################################################################################################################

    def _on_message(self, body:'any_', msg:'any_', name:'strnone'=None, config:'anydictnone'=None) -> 'None':
        """ Callback invoked when a message is received from the broker.
        The name and config parameters are required by the Consumer callback signature but not used.
        """
        try:
            # Parse message body
            if not isinstance(body, dict):
                body = loads(body)

            # Check if this is a reply to a previous request
            correlation_id = msg.properties.get('correlation_id')

            if correlation_id and correlation_id in self._callbacks:
                # Invoke callback registered for this correlation ID
                callback = self._callbacks.pop(correlation_id)
                callback(body)
            else:
                # Handle the message using the shared handler
                result = handle_broker_msg(body, self.context)

                # If the message was handled and needs a reply
                if result.was_handled and result.action_code == SERVICE.INVOKE.value:
                    if reply_to := body.get('reply_to'):
                        correlation_id = body.get('cid', '')
                        self.publish_to_queue(reply_to, result.response, correlation_id=correlation_id)

            # Always acknowledge the message
            msg.ack()

        except Exception as e:
            logger.warning(f'Error processing AMQP message: {e}')
            msg.ack()  # Still ack to avoid message queue buildup

# ################################################################################################################################

    def _on_reply(self, body:'any_', msg:'any_', name:'strnone'=None, config:'anydictnone'=None) -> 'None':
        """ Specific handler for replies to the temporary reply queue.
        The name and config parameters are required by the Consumer callback signature but not used.
        """
        if not isinstance(body, dict):
            body = loads(body)

        # Get correlation ID
        correlation_id = msg.properties.get('correlation_id')
        queue_name = config.queue if hasattr(config, 'queue') else None # type: ignore

        if correlation_id and correlation_id in self._callbacks:
            # Invoke callback registered for this correlation ID
            callback = self._callbacks.pop(correlation_id)

            # Clean up correlation to queue mapping
            with self.lock:
                _ = self.correlation_to_queue_map.pop(correlation_id, None)

            # Invoke the callback with the response
            callback(body)

            # Immediately delete the queue and clean up the consumer
            if queue_name:
                _ = spawn(self._cleanup_reply_consumer, queue_name)
        else:
            logger.warning(f'No callback found for correlation ID: {correlation_id}')

        # Always acknowledge the message
            msg.ack()

# ################################################################################################################################

    def _cleanup_reply_consumer(self, queue_name:'str', delay_seconds:'int'=0) -> 'None':
        """ Cleans up a reply consumer after waiting for specified delay.
        Explicitly deletes the queue after stopping the consumer.
        """
        try:
            # First, get the consumer (don't remove it yet to avoid race conditions)
            with self.lock:
                consumer = self.reply_consumers.get(queue_name)

            # If we have a consumer, properly disconnect it before deleting the queue
            if consumer:
                try:
                    # Stop the consumer's main loop first
                    consumer.stop()
                    logger.debug(f'Stopped consumer for {queue_name}')
                except Exception as e:
                    logger.warning(f'Error stopping consumer for {queue_name}: {str(e)}')

                # Wait a brief moment to ensure consumer loop has exited
                sleep(0.1) # type: ignore

                # Now remove it from the dictionary to avoid further references
                with self.lock:
                    _ = self.reply_consumers.pop(queue_name, None)

            # Finally, explicitly delete the queue using a fresh connection
            # This avoids using potentially cancelled channels
            try:
                with self.producer.acquire() as conn:
                    channel = conn.channel
                    if channel and channel.is_open:
                        channel.queue_delete(queue=queue_name)
                        logger.debug(f'Deleted queue: {queue_name}')
            except Exception as e:
                logger.warning(f'Error deleting queue {queue_name}: {str(e)}')

            logger.debug(f'Completed cleanup for queue: {queue_name}')
        except Exception as e:
            logger.warning(f'Error during cleanup for {queue_name}: {str(e)}')

# ################################################################################################################################

    def start_consumer(self) -> 'None':
        """ Starts the AMQP consumer in a background greenlet.
        """
        if not self.consumer:
            self.consumer = Consumer(self.consumer_config, self._on_message)
            _ = spawn(self.consumer.start)
            logger.info('Started broker consumer')

# ################################################################################################################################

    def stop_consumer(self) -> 'None':
        """ Stops the AMQP consumer.
        """
        if self.consumer:
            self.consumer.stop()
            self.consumer = None
            logger.info('Stopped broker consumer')

# ################################################################################################################################

    def _create_reply_consumer(self, queue_name:'str') -> 'Consumer':
        """ Creates a consumer for a specific reply queue.
        """
        # Set up configuration for a reply consumer
        reply_config = bunchify(dict(self.consumer_config, **{
            'name': f'reply-consumer-{queue_name[-8:]}',
            'queue': queue_name,
            'consumer_tag_prefix': 'zato-reply',
            'queue_opts': {
                'auto_delete': True,
                'durable': False,
            }
        }))

        # Create consumer for this specific reply queue
        consumer = Consumer(reply_config, self._on_reply)

        # Start the consumer in its own greenlet
        _ = spawn(consumer.start)

        # Track this consumer
        with self.lock:
            self.reply_consumers[queue_name] = consumer

        logger.debug(f'Started reply consumer for queue: {queue_name}')
        return consumer

# ################################################################################################################################

    def _create_reply_queue(self) -> 'str':
        """ Creates a unique name for a reply queue.
        The broker will create it on demand when the first message is sent there.
        """
        # Generate a unique queue name for this request
        unique_queue_name = f'zato-reply-{uuid4().hex}'
        logger.debug(f'Created unique reply queue name: {unique_queue_name}')
        return unique_queue_name

# ################################################################################################################################

    def invoke_with_callback(self, msg:'anydict', callback:'callable_') -> 'strnone':
        """ Publishes a message and registers a callback to be invoked when a reply is received.
        """
        # Generate a unique correlation ID for this request
        correlation_id = uuid4().hex

        # Create a unique reply queue name for this specific request
        reply_queue = self._create_reply_queue()

        # Create a consumer specifically for this reply queue
        _ = self._create_reply_consumer(reply_queue)

        # Store callback and correlation mapping
        with self.lock:
            self._callbacks[correlation_id] = callback
            self.correlation_to_queue_map[correlation_id] = reply_queue

            # Also store a copy of the callback under the msg cid value if present
            # This handles cases where the broker middleware changes the correlation ID
            if 'cid' in msg:
                cid = msg['cid']
                self._callbacks[cid] = callback
                self.correlation_to_queue_map[cid] = reply_queue

        # Include reply queue in message
        msg['reply_to'] = reply_queue

        # Set correlation ID in the business message ONLY, not in AMQP properties
        msg['cid'] = correlation_id

        # Convert message to JSON
        msg_str = dumps(msg) # type: ignore

        # Send message with the reply_to and correlation_id properties
        with self.producer.acquire() as client:
            client.publish(
                msg_str,
                exchange='components',
                routing_key='server',
                content_type='text/plain',
                delivery_mode=PERSISTENT_DELIVERY_MODE,
                reply_to=reply_queue
            )

        return correlation_id

# ################################################################################################################################

    def invoke_sync(
        self,
        service:'str',
        request:'anydictnone'=None,
        timeout:'int'=2,
        needs_root_elem:'bool'=False,
    ) -> 'any_':
        """ Synchronously invokes a service via the broker and waits for the response.
        """

        # Create response holder class without nonlocal keyword
        class ResponseHolder:
            def __init__(self):
                self.data = None
                self.ready = False
                self.error = None
                self.reply_queue_name = None
                self.cid = 'cid-not-set'
                self.service = 'service-not-set'

            def set_response(self, response):
                self.data = response
                self.ready = True
                logger.info(f'Rsp 🠈 {cid} - `{response}` from service `{self.service}``')

        # Initialize response holder
        response = ResponseHolder()

        # Generate a new CID for this request
        cid = new_cid()

        # Store service and CID in response holder for logging when response arrives
        response.service = service
        response.cid = cid

        # Prepare the message
        msg = {
            'action': SERVICE.INVOKE.value,
            'service': service,
            'payload': request or {},
            'cid': cid,
            'request_type': 'sync',
        }

        # Get correlation ID and create reply queue via invoke_with_callback
        correlation_id = self.invoke_with_callback(msg, response.set_response)

        # Store the reply queue name for possible cleanup in case of timeout
        with self.lock:
            if correlation_id in self.correlation_to_queue_map:
                response.reply_queue_name = self.correlation_to_queue_map.get(correlation_id)

        # Log service invocation with reply queue and CID in the same line
        reply_queue_info = f', reply-to: `{response.reply_queue_name}`' if response.reply_queue_name else ''
        logger.info(f'Req 🠊 {cid} - `{service}` with `{request}`{reply_queue_info}`')

        # Wait for the response
        wait_count = 0
        while not response.ready and wait_count < timeout:
            wait_count += 1
            sleep(1)

        # Handle timeout
        if not response.ready:

            # If timed out and we know the queue name, clean it up
            if response.reply_queue_name:

                logger.warning(f'Timeout reached - cleaning up reply queue {response.reply_queue_name}')
                self._cleanup_reply_consumer(response.reply_queue_name)

                # Also clean up the callback registration
                with self.lock:

                    if correlation_id in self._callbacks:
                        _ = self._callbacks.pop(correlation_id, None) # type: ignore

                    if correlation_id in self.correlation_to_queue_map:
                        _ = self.correlation_to_queue_map.pop(correlation_id, None)

            raise Exception(f'Timeout waiting for response from service `{service}` after {timeout} seconds')

        if not needs_root_elem:
            data = response.data
            data_keys = list(data.keys())
            root = data_keys[0]
            data = data[root]
        else:
            data = response.data

        return data

# ################################################################################################################################

    def get_connection(self) -> 'KombuAMQPConnection':
        """ Returns a new AMQP connection object using broker configuration parameters.
        """
        # Get broker configuration
        broker_config = get_broker_config()

        # Split host and port from address
        host, port = broker_config.address.split(':')
        port = int(port)

        # Create and return a new connection
        conn = KombuAMQPConnection(
            hostname=host,
            port=port,
            userid=broker_config.username,
            password=broker_config.password,
            virtual_host=broker_config.vhost,
            transport=broker_config.protocol,
        )

        return conn

# ################################################################################################################################

    def get_bindings(
        self,
        cid: 'str',
        exchange_name: 'str',
    ) -> 'dictlist':

        # Get binding information
        logger.info(f'[{cid}] Getting bindings for exchange={exchange_name}')

        # We'll store binding information here
        binding_info = []

        # Get broker configuration
        broker_config = get_broker_config()

        # Extract host and port information
        host, _ = broker_config.address.split(':')

        # Default management API port
        rabbitmq_api_port = 15672

        # The management API URL includes the vhost encoded as %2F for default vhost
        vhost_encoded = broker_config.vhost.replace('/', '%2F')

        # Construct the API URL for this exchange's bindings
        api_url = f'http://{host}:{rabbitmq_api_port}/api/exchanges/{vhost_encoded}/{exchange_name}/bindings/source'

        # Make the request to the RabbitMQ API
        response = requests.get(
            api_url,
            auth=HTTPBasicAuth(broker_config.username, broker_config.password),
            headers={'Content-Type': 'application/json'},
            timeout=5
        )

        if not response.status_code == OK:
            logger.warning(f'[{cid}] Failed to get bindings: API returned: {response.text}')

        else:

            # Parse bindings from response
            bindings_data = response.json()

            # Process each binding
            for binding in bindings_data:

                # Only include bindings to queues (not to other exchanges)
                if binding['destination_type'] == 'queue':
                    binding_info.append({
                        'queue': binding['destination'],
                        'routing_key': binding['routing_key'],
                        'exchange': binding['source'],
                        'arguments': binding.get('arguments') or {},
                        'vhost': binding['vhost'],
                    })

        return binding_info

# ################################################################################################################################

    def create_bindings(
        self,
        cid: 'str',
        sub_key: 'str',
        exchange_name: 'str',
        queue_name: 'str',
        routing_key: 'str',
        conn: 'Connection | None'=None,
    ) -> 'None':

        # Get broker connection from input or build a new one
        conn = conn or self.get_connection()

        # Create exchange and queue objects
        exchange = Exchange(exchange_name, type='topic', durable=True)
        queue = Queue(name=queue_name, exchange=exchange, routing_key=routing_key, durable=True)

        # Bind the queue to the exchange with the topic name as the routing key
        logger.info(f'[{cid}] [{sub_key}] Configuring bindings for exchange={exchange.name} -> queue={queue_name} (topic={routing_key})')

        _ = queue.maybe_bind(conn)
        _ = queue.declare()
        _ = queue.bind_to(exchange=exchange, routing_key=routing_key)

# ################################################################################################################################

    def delete_bindings(
        self,
        cid: 'str',
        sub_key: 'str',
        exchange_name: 'str',
        queue_name: 'str',
        routing_key: 'str',
        conn: 'Connection | None'=None,
    ) -> 'None':

        # Get broker connection from input or build a new one
        conn = conn or self.get_connection()

        # Create exchange and queue objects
        exchange = Exchange(exchange_name, type='topic', durable=True)

        # Unbind the queue from the exchange with the topic name as the routing key
        logger.info(f'[{cid}] [{sub_key}] Removing bindings for exchange={exchange.name} -> queue={queue_name} (topic={routing_key})')

        # Get a channel from the connection
        channel = conn.channel()

        # Unbind the queue from the exchange
        _ = channel.queue_unbind(
            queue=queue_name,
            exchange=exchange_name,
            routing_key=routing_key
        )

# ################################################################################################################################

    def update_bindings(
        self,
        cid: 'str',
        sub_key: 'str',
        exchange_name: 'str',
        queue_name: 'str',
        new_routing_key_list: 'strlist',
        conn: 'Connection | None'=None,
    ) -> 'None':

        # Get broker connection from input or build a new one
        conn = conn or self.get_connection()

        # Get current bindings for this exchange
        current_bindings = self.get_bindings(cid, exchange_name)

        # Extract current routing keys for this queue
        current_routing_keys = []
        for binding in current_bindings:
            if binding['queue'] == queue_name and binding['exchange'] == exchange_name:
                current_routing_keys.append(binding['routing_key'])

        # Convert lists to sets for comparison
        current_keys_set = set(current_routing_keys)
        new_keys_set = set(new_routing_key_list)

        # If sets are identical, do nothing
        if current_keys_set == new_keys_set:
            logger.info(f'[{cid}] [{sub_key}] Routing keys unchanged for exchange={exchange_name} -> queue={queue_name}')
            return

        logger.info(f'[{cid}] [{sub_key}] Current routing keys: {current_routing_keys}')
        logger.info(f'[{cid}] [{sub_key}] New routing keys: {new_routing_key_list}')

        # Find routing keys to add (in new list but not in current list)
        for routing_key in new_routing_key_list:
            if routing_key not in current_routing_keys:
                logger.info(f'[{cid}] [{sub_key}] Adding binding: {routing_key}')
                self.create_bindings(cid, sub_key, exchange_name, queue_name, routing_key, conn)

        # Find routing keys to remove (in current list but not in new list)
        for routing_key in current_routing_keys:
            if routing_key not in new_routing_key_list:
                logger.info(f'[{cid}] [{sub_key}] Removing binding: {routing_key}')
                self.delete_bindings(cid, sub_key, exchange_name, queue_name, routing_key, conn)

        logger.info(f'[{cid}] [{sub_key}] Updated bindings for exchange={exchange_name} -> queue={queue_name} -> {new_routing_key_list}')

# ################################################################################################################################
# ################################################################################################################################
