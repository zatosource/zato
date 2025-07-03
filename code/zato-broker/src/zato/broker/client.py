# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
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
from kombu.entity import PERSISTENT_DELIVERY_MODE

# Zato
from zato.common.api import AMQP
from zato.common.broker_message import SERVICE
from zato.common.pubsub.util import get_broker_config
from zato.common.util.api import new_cid
from zato.server.connection.amqp_ import Consumer, get_connection_class, Producer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Dict
    from zato.common.typing_ import any_, anydict, anydictnone, callable_, strnone
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class BrokerClient:

    def __init__(self, *, server:'ParallelServer | None'=None) -> 'None':

        self.server = server
        self.lock = RLock()
        self._callbacks = {}  # type: Dict[str, callable_]
        self.correlation_to_queue_map = {}  # Maps correlation IDs to queue names for timeout handling
        self.reply_consumers = {}  # Maps reply queue names to consumers
        self.reply_consumer_started = False
        self.consumer = None

        # Get broker configuration
        broker_config = get_broker_config()

        host, port = broker_config.address.split(':')
        port = int(port)

        # Common connection URL for both producer and consumer
        conn_url = f'{broker_config.protocol}://{broker_config.username}:{broker_config.password}@{host}:{port}/{broker_config.vhost}'

        # Base component name
        component_name = 'internal'

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
            'queue': 'server',
            'consumer_tag_prefix': 'zato-broker',
            'ack_mode': AMQP.ACK_MODE.ACK.id,
            'prefetch_count': 5,
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

        with self.producer.acquire() as client:
            client.publish(
                msg,
                exchange='components',
                routing_key='server',
                content_type='text/plain',
                delivery_mode=PERSISTENT_DELIVERY_MODE
            )

# ################################################################################################################################

    def publish_to_queue(self, queue_name:'str', msg:'any_', correlation_id:'str'='') -> 'None':
        """ Publishes a message directly to a specific queue.
        """
        if not isinstance(msg, str):
            msg = dumps(msg)

        # Prepare publish parameters
        publish_kwargs = {
            'exchange': '',  # Default exchange
            'routing_key': queue_name,  # Queue name as routing key
            'content_type': 'text/plain',
        }

        # Add correlation ID if provided
        if correlation_id:
            publish_kwargs['correlation_id'] = correlation_id

        # Publish the message
        with self.producer.acquire() as client:
            client.publish(msg, **publish_kwargs)

    invoke_async = publish

# ################################################################################################################################

    def _on_message(self, body:'any_', msg:'any_', name:'strnone'=None, config:'anydictnone'=None) -> 'None':
        """ Callback invoked when a message is received from the broker.
        The name and config parameters are required by the Consumer callback signature but not used.
        """
        try:
            # Parse message body
            message_data = loads(body)

            # Check if this is a reply to a previous request
            correlation_id = msg.properties.get('correlation_id')

            if correlation_id and correlation_id in self._callbacks:
                # Invoke callback registered for this correlation ID
                callback = self._callbacks.pop(correlation_id)
                callback(message_data)
            else:
                # Log the message if there's no handler
                logger.info(f'Received message with no handler: {message_data}')

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
        try:
            # Parse message body
            message_data = loads(body)

            # Get correlation ID
            correlation_id = msg.properties.get('correlation_id')
            # Get the queue name from config or properties
            queue_name = config.queue if hasattr(config, 'queue') else None # type: ignore

            if correlation_id and correlation_id in self._callbacks:
                # Invoke callback registered for this correlation ID
                callback = self._callbacks.pop(correlation_id)

                # Clean up correlation to queue mapping
                with self.lock:
                    self.correlation_to_queue_map.pop(correlation_id, None)

                # Invoke the callback with the response
                callback(message_data)

                # Immediately delete the queue and clean up the consumer
                if queue_name:
                    _ = spawn(self._cleanup_reply_consumer, queue_name)

            # Always acknowledge the message
            msg.ack()

        except Exception as e:
            logger.warning(f'Error processing reply message: {e}')
            msg.ack()

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
                sleep(0.1)

                # Now remove it from the dictionary to avoid further references
                with self.lock:
                    self.reply_consumers.pop(queue_name, None)

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
                'arguments': {'x-expires': 300000}  # 5 minutes expiry
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

        # Include reply queue in message
        msg['reply_to'] = reply_queue

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
                correlation_id=correlation_id,
                reply_to=reply_queue
            )

        return correlation_id

# ################################################################################################################################

    def invoke_sync(self, service:'str', request:'anydictnone'=None, timeout:'int'=2) -> 'any_':
        """ Synchronously invokes a service via the broker and waits for the response.
        """
        # Create response holder class without nonlocal keyword
        class ResponseHolder:
            def __init__(self):
                self.data = None
                self.ready = False
                self.error = None
                self.reply_queue_name = None

            def set_response(self, response):
                self.data = response
                self.ready = True
                # Queue deletion is handled in _on_reply when the reply is received

        # Initialize response holder
        response = ResponseHolder()

        # Prepare the message
        msg = {
            'action': SERVICE.INVOKE.value,
            'service': service,
            'payload': request or {},
            'cid': new_cid(),
            'request_type': 'sync',
        }

        logger.info(f'Invoking service `{service}` with `{request}`')
        correlation_id = self.invoke_with_callback(msg, response.set_response)

        # Store the reply queue name for possible cleanup in case of timeout
        with self.lock:
            if correlation_id in self.correlation_to_queue_map:
                response.reply_queue_name = self.correlation_to_queue_map.get(correlation_id)

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
                        self._callbacks.pop(correlation_id, None)
                    if correlation_id in self.correlation_to_queue_map:
                        self.correlation_to_queue_map.pop(correlation_id, None)

            raise Exception(f'Timeout waiting for response from service `{service}` after {timeout} seconds')

        logger.info(f'Received synchronous response from service `{service}`')
        return response.data

# ################################################################################################################################
# ################################################################################################################################
