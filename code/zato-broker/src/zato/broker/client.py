# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import timedelta
from http.client import OK
from json import dumps, loads
from logging import getLogger
from threading import RLock
from traceback import format_exc

# Bunch
from bunch import bunchify

# gevent
from gevent import sleep, spawn

# Kombu
from kombu.entity import PERSISTENT_DELIVERY_MODE

# requests
import requests
from requests.auth import HTTPBasicAuth

# Zato
from zato.common.api import AMQP, PubSub
from zato.common.broker_message import SERVICE
from zato.common.pubsub.util import get_broker_config
from zato.common.util.api import new_cid_broker_client, new_cid_server, new_msg_id, utcnow
from zato.server.connection.amqp_ import Consumer, get_connection_class, Producer
from zato.broker.message_handler import handle_broker_msg
from zato.broker.amqp_layer import AMQP as _AMQP, BrokerConnection

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Dict
    from zato.common.typing_ import any_, anydict, anydictnone, callable_, dictlist, strlist, strnone
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

_default_priority = PubSub.Message.Priority_Default
_default_expiration = PubSub.Message.Default_Expiration

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class _InvokeWithCallbackCtx:
    producer: 'Producer'
    correlation_id: 'str'

# ################################################################################################################################
# ################################################################################################################################

class NoResponseReceivedException(Exception):
    pass

# ################################################################################################################################
# ################################################################################################################################

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
        self.consumer_drain_events_timeout = kwargs.get('consumer_drain_events_timeout')
        self._amqp = _AMQP()

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
            'conn_class': BrokerConnection,
            'consumer_drain_events_timeout': self.consumer_drain_events_timeout,
        }))

        self.consumer_config = consumer_config

        # For managing reply consumers
        self.reply_consumers = {}  # Maps reply queue names to consumers
        self.reply_consumer_started = False

# ################################################################################################################################

    def publish_to_pubsub(self, msg:'any_', *ignored_args:'any_', **kwargs:'any_') -> 'any_':

        self.publish(msg, routing_key='pubsub.publish.1')
        self.publish(msg, routing_key='pubsub.pull.1')

# ################################################################################################################################

    def publish(self, msg:'any_', *ignored_args:'any_', **kwargs:'any_') -> 'any_':
        """ Publishes a message to the AMQP broker.
        """

        # This will be True if we publish a message from a service's self.publish
        should_append_details:'bool' = bool(kwargs.get('should_append_details'))

        # If we need to append details, preprocess the message
        if should_append_details:

            # Get the current time
            now = utcnow()
            pub_time_iso = now.isoformat()
            recv_time_iso = pub_time_iso

            # Get topic name
            topic_name = kwargs.get('routing_key', '')

            # Get or generate msg_id
            msg_id = kwargs.get('msg_id') or new_msg_id()

            # Get or generate correlation_id
            correl_id = kwargs.get('cid', '') or new_cid_server()

            # Calculate expiration time
            expiration_seconds = _default_expiration
            expiration_time = now + timedelta(seconds=expiration_seconds)
            expiration_time_iso = expiration_time.isoformat()

            # Build the properly structured message
            msg = {
                'data': msg,
                'topic_name': topic_name,
                'msg_id': msg_id,
                'priority': _default_priority,
                'pub_time_iso': pub_time_iso,
                'recv_time_iso': recv_time_iso,
                'expiration': _default_expiration,
                'expiration_time_iso': expiration_time_iso,
                'correl_id': correl_id,
            }

        # We're given an already serialized message ..
        if isinstance(msg, str):

            # .. so we need to assume the defaults ..
            priority = _default_priority
            expiration = _default_expiration

        # .. otherwise, it's not serialized ..
        else:

            # .. we can try to extract the optional parameters ourselves ..
            priority = msg.get('priority') or _default_priority
            expiration = msg.get('expiration') or _default_expiration

            # .. and now we can serialize the message too ..
            msg = dumps(msg)

        exchange        = kwargs.get('exchange') or 'components'
        routing_key     = kwargs.get('routing_key') or 'server'
        mandatory       = kwargs.get('mandatory', True)
        publish_timeout = kwargs.get('publish_timeout', 30)

        with self.producer.acquire() as client:

            # Make sure we are connected ..
            _ = client.connection.ensure_connection() # type: ignore

            # Enable confirm mode on the channel
            client.channel.confirm_select()

            # .. and publish the message now.
            _ = client.publish(
                msg,
                exchange=exchange,
                routing_key=routing_key,
                content_type='application/json',
                delivery_mode=PERSISTENT_DELIVERY_MODE,
                retry=True,
                priority=priority,
                expiration=expiration,
                mandatory=mandatory,
                timeout=publish_timeout,
                confirm_timeout=3600 * 24,
                headers={
                    'zato_msg_id': new_msg_id(),
                    'zato_pub_time': utcnow().isoformat()
                }
            ) # type: ignore

    invoke_async = publish

# ################################################################################################################################

    def publish_to_queue(self, queue_name:'str', msg:'any_', correlation_id:'str'='') -> 'None':
        """ Publishes a message directly to a specific queue.
        """
        logger.debug(f'Pub to queue -> cid:`{correlation_id}` -> queue=`{queue_name}` -> msg:`{msg}`')

        if not isinstance(msg, str):
            msg = dumps(msg)
            logger.debug(f'Converted message to string: {msg[:100]}...' if len(msg) > 100 else msg)

        # Prepare publish parameters
        publish_kwargs = {
            'exchange': '',  # Default exchange
            'routing_key': queue_name,  # Queue name as routing key
            'content_type': 'application/json',
            'delivery_mode': PERSISTENT_DELIVERY_MODE,
            'headers': {'zato_pub_time': utcnow().isoformat()}
        }

        # Add correlation ID if provided
        if correlation_id:
            publish_kwargs['correlation_id'] = correlation_id

        # Publish the message
        with self.producer.acquire() as client:
            logger.debug(f'Producer connection acquired: {client}')
            # logger.warning('PUBLISH %s %s', msg, publish_kwargs)
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
                _ = spawn(self._cleanup_reply_consumer, correlation_id, queue_name)
        else:
            logger.warning(f'No callback found for correlation ID: {correlation_id}')

        # Always acknowledge the message
            msg.ack()

# ################################################################################################################################

    def _cleanup_reply_consumer(self, cid:'str', queue_name:'str', delay_seconds:'int'=0) -> 'None':
        """ Cleans up a reply consumer after waiting for specified delay.
        Explicitly deletes the queue after stopping the consumer.
        """
        try:
            with self.lock:
                # First, get the consumer (don't remove it yet to avoid race conditions)
                consumer = self.reply_consumers.get(queue_name)

                # If we have a consumer, properly disconnect it before deleting the queue
                if consumer:
                    try:
                        # Stop the consumer's main loop first
                        consumer.stop()
                        logger.debug(f'Stopped consumer for `{queue_name}`')
                    except Exception:
                        logger.warning(f'Error stopping consumer for `{queue_name}`: {format_exc()}')

                    # Wait a brief moment to ensure consumer loop has exited
                    sleep(0.1) # type: ignore

                    # Now remove it from the dictionary to avoid further references
                    _ = self.reply_consumers.pop(queue_name, None)

                # Delete the queue
                self.delete_queue(cid, queue_name)

                logger.debug(f'Completed cleanup for queue: {queue_name}')
        except Exception:
            logger.warning(f'Error during cleanup for `{queue_name}`: {format_exc()}')

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
        # Local variables
        connect_timeout = PubSub.Max_Retry_Time

        # Set up configuration for a reply consumer
        reply_config = bunchify(dict(self.consumer_config, **{
            'name': f'reply-consumer-{queue_name}',
            'queue': queue_name,
            'consumer_tag_prefix': PubSub.Prefix.Reply_Queue,
            'queue_opts': {
                'auto_delete': True,
                'durable': False,
            }
        }))

        # Create consumer for this specific reply queue
        consumer = Consumer(reply_config, self._on_reply)

        # Start the consumer in its own greenlet ..
        _ = spawn(consumer.start)

        # .. wait for it to connect ..
        connected = consumer.wait_until_connected(timeout=connect_timeout)

        if not connected:
            logger.error(f'Reply consumer for queue {queue_name} failed to connect within {connect_timeout}s')

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
        unique_queue_name = f'{PubSub.Prefix.Reply_Queue}-{new_cid_broker_client()}'
        logger.debug(f'Created unique reply queue name: {unique_queue_name}')
        return unique_queue_name

# ################################################################################################################################

    def _invoke_with_callback(self, msg:'anydict', callback:'callable_') -> '_InvokeWithCallbackCtx':
        """ Publishes a message and registers a callback to be invoked when a reply is received.
        """
        # Generate a unique correlation ID for this request
        correlation_id = new_cid_broker_client()

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

        # Extract the optional properties
        priority = msg.get('priority') or _default_priority
        expiration = msg.get('expiration') or _default_expiration

        with self.producer.acquire() as client:
            _ = client.publish(
                msg_str,
                exchange='components',
                routing_key='server',
                content_type='text/plain',
                delivery_mode=PERSISTENT_DELIVERY_MODE,
                reply_to=reply_queue,
                priority=priority,
                expiration=expiration,
            )

        ctx = _InvokeWithCallbackCtx()
        ctx.producer = client
        ctx.correlation_id = correlation_id

        return ctx

# ################################################################################################################################

    def _wait_for_response(
        self,
        ctx:'_InvokeWithCallbackCtx',
        response:'any_',
        timeout:'int | float',
        sleep_time:'float',
        cid:'str'
    ) -> 'None':
        """ Waits for a response from the broker within the specified timeout.
        """

        end_time = utcnow() + timedelta(seconds=timeout)

        # Get broker configuration for REST API access
        broker_config = get_broker_config()
        host, _ = broker_config.address.split(':')
        rabbitmq_api_port = 15672
        vhost_encoded = broker_config.vhost.replace('/', '%2F')

        while not response.ready and utcnow() < end_time:

            try:

                # Check if queue exists using RabbitMQ Management API
                api_url = f'http://{host}:{rabbitmq_api_port}/api/queues/{vhost_encoded}/{response.reply_queue_name}'

                response_api = requests.get(
                    api_url,
                    auth=HTTPBasicAuth(broker_config.username, broker_config.password),
                    headers={'Content-Type': 'application/json'},
                    timeout=1_000_000
                )

                if response_api.status_code != OK:
                    logger.info(f'[{cid}] AMQP queue no longer found `{response.reply_queue_name}`')
                    break

            except Exception:
                logger.info(f'[{cid}] AMQP queue check failed `{response.reply_queue_name}` -> {format_exc()}')
                break

            else:
                sleep(sleep_time)
                time_left = (end_time - utcnow()).total_seconds()
                msg = f'Still waiting - queue: {response.reply_queue_name}, time left: {time_left:.1f}s'
                logger.debug(msg)

# ################################################################################################################################

    def _invoke_sync(
        self,
        service:'str',
        request:'anydictnone'=None,
        timeout:'int | float'=PubSub.Timeout.Invoke_Sync,
        needs_root_elem:'bool'=False,
        cid:'str'='',
    ) -> 'any_':
        """ Synchronously invokes a service via the broker and waits for the response.
        """

        # For later use
        sleep_time = 0.05

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
                # reply_queue_info = f', reply-to: `{self.reply_queue_name}`' if self.reply_queue_name else ''
                # logger.info(f'Rsp 🠈 {cid} - `{self.service}` - `{response}`{reply_queue_info}')
                logger.info(f'Rsp 🠈 {cid} - `{self.service}`')

        # Initialize response holder
        response = ResponseHolder()

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

        # Get correlation ID and create reply queue via _invoke_with_callback
        ctx = self._invoke_with_callback(msg, response.set_response)

        # Store the reply queue name for possible cleanup in case of timeout
        with self.lock:
            if ctx.correlation_id in self.correlation_to_queue_map:
                response.reply_queue_name = self.correlation_to_queue_map.get(ctx.correlation_id)

        # Log service invocation with reply queue and CID in the same line
        reply_queue_info = f', reply-to: `{response.reply_queue_name}`' if response.reply_queue_name else ''
        logger.info(f'Req 🠊 {cid} - `{service}` - `{request}`{reply_queue_info}`')

        # Wait for response
        self._wait_for_response(ctx, response, timeout, sleep_time, cid)

        # .. handle timeouts and early exists (does not matter which one led us here)..
        if not response.ready:

            # .. if we know the queue name, clean it up ..
            if response.reply_queue_name:

                logger.info(f'No response - cleaning up reply queue {response.reply_queue_name}')
                self._cleanup_reply_consumer(ctx.correlation_id, response.reply_queue_name)

                # Also clean up the callback registration
                with self.lock:

                    if ctx.correlation_id in self._callbacks:
                        _ = self._callbacks.pop(ctx.correlation_id, None) # type: ignore

                    if ctx.correlation_id in self.correlation_to_queue_map:
                        _ = self.correlation_to_queue_map.pop(ctx.correlation_id, None)

            exc_msg = f'No response received from service `{service}`'
            raise NoResponseReceivedException(exc_msg)

        if not needs_root_elem:
            data = response.data
            data_keys = list(data.keys()) # type: ignore
            root = data_keys[0]
            data = data[root] # type: ignore
        else:
            data = response.data

        return data

# ################################################################################################################################

    def invoke_sync(self, *args:'any_', **kwargs:'any_') -> 'any_':

        # We'll keep pinging until we have this set
        response = None

        # First, ping the server to confirm it's up and running ..
        while not response:
            try:
                response = self._invoke_sync('demo.ping')
            except NoResponseReceivedException as e:
                logger.info('Timeout: %s', e)

        # .. now, we can invoke the actual service.
        return self._invoke_sync(*args, **kwargs)

# ################################################################################################################################

    def notify_pubsub_counterpart(self, cid:'str', action:'str', source_server_type:'str', **msg_data:'any_') -> 'None':
        """ Notify the counterpart pub/sub server about subscription changes.
        """
        counterpart = 'pull' if source_server_type == 'publish' else 'publish'
        queue_name = f'pubsub.{counterpart}.1'

        broker_msg = {
            'action': action,
            'cid': cid,
            **msg_data
        }

        self.publish_to_queue(queue_name, broker_msg, cid)
        logger.info(f'[{cid}] Notified counterpart server via queue `{queue_name}`')

# ################################################################################################################################

    def ping_connection(self) -> 'None':

        # Get broker configuration
        broker_config = get_broker_config()

        # .. extract its URL ..
        broker_url = broker_config.to_url()

        # .. log what we're doing ..
        logger.info('Broker connection ping: %s', broker_url)

        # .. build a new connection and ensure it exists ..
        _ = self.get_connection(broker_config, True)

        # .. if we're here, it means the connection is fine ..
        logger.info('Broker connection pinged OK: %s', broker_url)

# ################################################################################################################################

    def get_connection(self, *args, **kwargs):
        return self._amqp.get_connection(*args, **kwargs)

# ################################################################################################################################

    def get_queue_list(
        self,
        cid: 'str',
        prefix: 'str' = '',
        exclude_list: 'strlist | None' = None,
    ) -> 'dictlist':
        """ Get list of queues from RabbitMQ Management API.
        """
        exclude_list = exclude_list or []

        logger.debug(f'[{cid}] Getting queue list with prefix={prefix}, exclude_list={exclude_list}')

        # Get broker configuration
        broker_config = get_broker_config()

        # Extract host information
        host, _ = broker_config.address.split(':')

        # Default management API port
        rabbitmq_api_port = 15672

        # The management API URL includes the vhost encoded as %2F for default vhost
        vhost_encoded = broker_config.vhost.replace('/', '%2F')

        # Construct the API URL for queues
        api_url = f'http://{host}:{rabbitmq_api_port}/api/queues/{vhost_encoded}'

        # Make the request to the RabbitMQ API
        response = requests.get(
            api_url,
            auth=HTTPBasicAuth(broker_config.username, broker_config.password),
            headers={'Content-Type': 'application/json'},
            timeout=200_000
        )

        if not response.status_code == OK:
            msg = f'[{cid}] Failed to get queue list: API returned: {response.text}'
            raise Exception(msg)

        # Parse queues from response
        queues_data = response.json()
        filtered_queues = []

        for queue in queues_data:
            queue_name = queue['name']

            # Apply prefix filter if specified
            if prefix and not queue_name.startswith(prefix):
                continue

            # Apply exclude list filter
            should_exclude = False
            for exclude_prefix in exclude_list:
                if queue_name.startswith(exclude_prefix):
                    should_exclude = True
                    break

            if should_exclude:
                continue

            filtered_queues.append({
                'name': queue_name,
                'messages': queue.get('messages', 0),
                'consumers': queue.get('consumers', 0),
                'state': queue.get('state', 'unknown'),
                'vhost': queue.get('vhost', ''),
                'durable': queue.get('durable', False),
                'auto_delete': queue.get('auto_delete', False),
            })

        queue_count = len(filtered_queues)
        queue_text = 'queue' if queue_count == 1 else 'queues'
        logger.debug(f'[{cid}] Found {queue_count} {queue_text} matching criteria')
        return filtered_queues

# ################################################################################################################################

    def get_bindings(self, *args, **kwargs):
        return self._amqp.get_bindings(*args, **kwargs)

# ################################################################################################################################

    def create_bindings(self, *args, **kwargs):
        return self._amqp.create_bindings(*args, **kwargs)

# ################################################################################################################################

    def create_internal_queue(self, *args, **kwargs):
        return self._amqp.create_internal_queue(*args, **kwargs)

# ################################################################################################################################

    def delete_bindings(self, *args, **kwargs):
        return self._amqp.delete_bindings(*args, **kwargs)

# ################################################################################################################################

    def delete_queue(self, *args, **kwargs):
        return self._amqp.delete_queue(*args, **kwargs)

# ################################################################################################################################

    def update_bindings(self, *args, **kwargs):
        return self._amqp.update_bindings(*args, **kwargs)

# ################################################################################################################################

    def delete_topic(self, *args, **kwargs):
        return self._amqp.delete_topic(*args, **kwargs)

# ################################################################################################################################

    def get_bindings_by_queue(self, *args, **kwargs):
        return self._amqp.get_bindings_by_queue(*args, **kwargs)

# ################################################################################################################################

    def queue_has_bindings(self, *args, **kwargs):
        return self._amqp.queue_has_bindings(*args, **kwargs)

# ################################################################################################################################

    def get_bindings_by_routing_key(self, *args, **kwargs):
        return self._amqp.get_bindings_by_routing_key(*args, **kwargs)

# ################################################################################################################################

    def rename_topic(self, *args, **kwargs):
        return self._amqp.rename_topic(*args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_format)

    msg = '123'

    client = BrokerClient()
    client.publish(msg)

# ################################################################################################################################
# ################################################################################################################################
