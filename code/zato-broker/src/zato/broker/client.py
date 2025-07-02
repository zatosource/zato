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
from gevent import spawn

# Kombu
from kombu.connection import Connection as KombuAMQPConnection
from kombu.entity import PERSISTENT_DELIVERY_MODE

# Zato
from zato.common.api import AMQP
from zato.common.pubsub.util import get_broker_config
from zato.common.util.api import new_cid
from zato.server.connection.amqp_ import Consumer, get_connection_class, Producer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Dict
    from zato.common.typing_ import any_, anydict, callable_, strnone
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

        # Reply queue for responses
        self.reply_queue_name = f'zato-reply-{uuid4().hex[:8]}'
        self.reply_consumer = None
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

    invoke_async = publish

# ################################################################################################################################

    def _on_message(self, body:'any_', msg:'any_', name:'str'=None, config:'dict'=None) -> 'None':
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

    def _on_reply(self, body:'any_', msg:'any_', name:'str'=None, config:'dict'=None) -> 'None':
        """ Specific handler for replies to the temporary reply queue.
        The name and config parameters are required by the Consumer callback signature but not used.
        """
        try:
            # Parse message body
            message_data = loads(body)

            # Get correlation ID
            correlation_id = msg.properties.get('correlation_id')

            if correlation_id and correlation_id in self._callbacks:
                # Invoke callback registered for this correlation ID
                callback = self._callbacks.pop(correlation_id)
                callback(message_data)

            # Always acknowledge the message
            msg.ack()

        except Exception as e:
            logger.warning(f'Error processing reply message: {e}')
            msg.ack()

# ################################################################################################################################

    def start_consumer(self) -> 'None':
        """ Starts the AMQP consumer in a background greenlet.
        """
        if not self.consumer:
            self.consumer = Consumer(self.consumer_config, self._on_message)
            spawn(self.consumer.start)
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

    def _ensure_reply_consumer(self) -> 'None':
        """ Ensures the reply consumer is set up and running.
        """
        if self.reply_consumer_started:
            return

        # Create a config for the reply consumer
        reply_config = bunchify(dict(self.consumer_config, **{
            'name': f'reply-consumer',
            'queue': self.reply_queue_name,
            'consumer_tag_prefix': 'zato-reply',
        }))

        # Create a dedicated queue for replies
        conn = KombuAMQPConnection(reply_config.conn_url)
        channel = conn.channel()

        # Declare the reply queue (auto-delete when no longer used)
        channel.queue_declare(queue=self.reply_queue_name, auto_delete=True)
        conn.release()

        # Start the reply consumer
        self.reply_consumer = Consumer(reply_config, self._on_reply)
        spawn(self.reply_consumer.start)
        self.reply_consumer_started = True

        logger.info(f'Started reply consumer on queue: {self.reply_queue_name}')

# ################################################################################################################################

    def invoke_with_callback(self, msg:'anydict', callback:'callable_') -> 'strnone':
        """ Publishes a message and registers a callback to be invoked when a reply is received.
        Returns a correlation ID that can be used to track the request.
        """
        # Ensure we have a reply consumer running
        self._ensure_reply_consumer()

        # Generate a unique correlation ID for this request
        correlation_id = uuid4().hex

        # Register the callback
        with self.lock:
            self._callbacks[correlation_id] = callback

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
                reply_to=self.reply_queue_name
            )

        return correlation_id

# ################################################################################################################################

    def invoke_sync(self, service:'str', request:'anydict'=None, timeout:'int'=30) -> 'any_':
        """ Synchronously invokes a service via the broker and waits for the response.
        """

        class ResponseHolder:
            def __init__(self):
                self.data = None
                self.ready = False
                self.error = None

            def set_response(self, response):
                self.data = response
                self.ready = True

        # Initialize response holder
        response = ResponseHolder()

        # Prepare the message
        msg = {
            'service': service,
            'payload': request or {},
            'cid': new_cid(),
            'request_type': 'sync'
        }

        # Log the request
        logger.info(f'Invoking service `{service}` synchronously with `{request}`')

        # Send the request with callback
        self.invoke_with_callback(msg, response.set_response)

        # Wait for the response
        wait_count = 0
        while not response.ready and wait_count < timeout:
            wait_count += 1
            sleep(1)

        # Handle timeout
        if not response.ready:
            raise Exception(f'Timeout waiting for response from service `{service}` after {timeout} seconds')

        # Return the data
        logger.info(f'Received synchronous response from service `{service}`')
        return response.data

# ################################################################################################################################
# ################################################################################################################################
