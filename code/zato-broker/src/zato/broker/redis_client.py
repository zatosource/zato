# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import dataclass
from datetime import timedelta
from json import dumps, loads
from logging import getLogger
from threading import RLock
from traceback import format_exc

# gevent
from gevent import sleep, spawn

# redis
from redis import Redis
from redis.exceptions import ResponseError

# Zato
from zato.common.api import PubSub
from zato.common.broker_message import SERVICE
from zato.common.util.api import as_bool, new_cid_broker_client, new_cid_server, new_msg_id, utcnow
from zato.broker.message_handler import handle_broker_msg

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

_needs_details = as_bool(os.environ.get('Zato_Needs_Details', False))

_default_priority = PubSub.Message.Priority_Default
_default_expiration = PubSub.Message.Default_Expiration

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Channel_Prefix = 'zato:broker:channel:'
    Queue_Prefix = 'zato:broker:queue:'
    Reply_Prefix = 'zato:broker:reply:'
    Stream_Prefix = 'zato:broker:stream:'
    Consumer_Group = 'zato-broker'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class _InvokeWithCallbackCtx:
    correlation_id: 'str'
    reply_channel: 'str'

# ################################################################################################################################
# ################################################################################################################################

class NoResponseReceivedException(Exception):
    pass

# ################################################################################################################################
# ################################################################################################################################

class RedisBrokerClient:

    def __init__(self, *, server:'ParallelServer | None'=None, **kwargs:'any_') -> 'None':

        self.server = server
        self.lock = RLock()
        self._callbacks:'Dict[str, callable_]' = {}
        self.correlation_to_channel_map:'Dict[str, str]' = {}
        self._running = False
        self._consumer_greenlet = None

        # This is the object whose on_broker_msg_ methods will be invoked
        self.context = kwargs.get('context') or self

        # Get Redis connection from server or create new one
        if server and hasattr(server, 'kvdb') and server.kvdb:
            self.redis = server.kvdb.conn
        else:
            redis_host = os.environ.get('Zato_Redis_Host', 'localhost')
            redis_port = int(os.environ.get('Zato_Redis_Port', '6379'))
            redis_db = int(os.environ.get('Zato_Redis_DB', '0'))
            redis_password = os.environ.get('Zato_Redis_Password', None)
            self.redis = Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
                decode_responses=True
            )

        # Queue name for this consumer
        self.queue_name = kwargs.get('queue_name') or 'server'

        # Channel to subscribe to
        self.channel_name = f'{ModuleCtx.Channel_Prefix}{self.queue_name}'

        # Stream for persistent messages
        self.stream_name = f'{ModuleCtx.Stream_Prefix}{self.queue_name}'

        # Pubsub object for subscriptions
        self._pubsub = None

# ################################################################################################################################

    def publish_to_pubsub(self, msg:'any_', *ignored_args:'any_', **kwargs:'any_') -> 'any_':
        self.publish(msg, routing_key='pubsub.publish.1')
        self.publish(msg, routing_key='pubsub.pull.1')

# ################################################################################################################################

    def publish(self, msg:'any_', *ignored_args:'any_', **kwargs:'any_') -> 'any_':
        """ Publishes a message to Redis.
        """
        should_append_details:'bool' = bool(kwargs.get('should_append_details'))

        if should_append_details:
            now = utcnow()
            pub_time_iso = now.isoformat()
            topic_name = kwargs.get('routing_key', '')
            msg_id = kwargs.get('msg_id') or new_msg_id()
            correl_id = kwargs.get('cid', '') or new_cid_server()
            expiration_time = now + timedelta(seconds=_default_expiration)
            expiration_time_iso = expiration_time.isoformat()

            msg = {
                'data': msg,
                'topic_name': topic_name,
                'msg_id': msg_id,
                'priority': _default_priority,
                'pub_time_iso': pub_time_iso,
                'recv_time_iso': pub_time_iso,
                'expiration': _default_expiration,
                'expiration_time_iso': expiration_time_iso,
                'correl_id': correl_id,
            }

        if isinstance(msg, str):
            priority = _default_priority
            expiration = _default_expiration
        else:
            priority = msg.get('priority') or _default_priority
            expiration = msg.get('expiration') or _default_expiration
            msg = dumps(msg)

        routing_key = kwargs.get('routing_key') or 'server'
        channel = f'{ModuleCtx.Channel_Prefix}{routing_key}'

        # Publish to Redis channel
        _ = self.redis.publish(channel, msg)

        if _needs_details:
            logger.info(f'Published message to channel {channel}')

    invoke_async = publish

# ################################################################################################################################

    def publish_to_queue(self, queue_name:'str', msg:'any_', correlation_id:'str'='') -> 'None':
        """ Publishes a message to a specific Redis channel (simulating a queue).
        """
        if _needs_details:
            logger.info(f'[PUBLISH_TO_QUEUE] Starting -> cid:`{correlation_id}` -> queue=`{queue_name}`')

        if not isinstance(msg, str):
            msg = dumps(msg)

        # For reply queues, publish directly to the reply channel
        if queue_name.startswith(PubSub.Prefix.Reply_Queue):
            channel = f'{ModuleCtx.Reply_Prefix}{queue_name}'
        else:
            channel = f'{ModuleCtx.Queue_Prefix}{queue_name}'

        # Add correlation_id to message if provided
        if correlation_id:
            try:
                msg_dict = loads(msg)
                msg_dict['_correlation_id'] = correlation_id
                msg = dumps(msg_dict)
            except Exception:
                pass

        _ = self.redis.publish(channel, msg)

        if _needs_details:
            logger.info(f'[PUBLISH_TO_QUEUE] Published to channel {channel}')

# ################################################################################################################################

    def _on_message(self, message:'anydict') -> 'None':
        """ Callback invoked when a message is received.
        """
        try:
            if message['type'] != 'message':
                return

            data = message['data']
            channel = message['channel']

            if isinstance(data, bytes):
                data = data.decode('utf-8')

            body = loads(data)

            # Check for correlation ID
            correlation_id = body.pop('_correlation_id', None)

            if _needs_details:
                logger.info(f'[ON_MESSAGE] Received -> channel:`{channel}` -> correlation_id:`{correlation_id}`')

            if correlation_id and correlation_id in self._callbacks:
                callback = self._callbacks.pop(correlation_id)
                callback(body)
                if _needs_details:
                    logger.info(f'[ON_MESSAGE] Callback invoked for correlation_id:`{correlation_id}`')
            else:
                result = handle_broker_msg(body, self.context)

                if result.was_handled and result.action_code == SERVICE.INVOKE.value:
                    if reply_to := body.get('reply_to'):
                        cid = body.get('cid', '')
                        self.publish_to_queue(reply_to, result.response, correlation_id=cid)

        except Exception as e:
            logger.warning(f'Error processing Redis message: {e}')

# ################################################################################################################################

    def _on_reply(self, message:'anydict') -> 'None':
        """ Handler for reply messages.
        """
        try:
            if message['type'] != 'message':
                return

            data = message['data']

            if isinstance(data, bytes):
                data = data.decode('utf-8')

            body = loads(data)
            correlation_id = body.pop('_correlation_id', None)

            if correlation_id and correlation_id in self._callbacks:
                callback = self._callbacks.pop(correlation_id)

                with self.lock:
                    _ = self.correlation_to_channel_map.pop(correlation_id, None)

                callback(body)
            else:
                logger.warning(f'No callback found for correlation ID: {correlation_id}')

        except Exception as e:
            logger.warning(f'Error processing reply message: {e}')

# ################################################################################################################################

    def start_consumer(self) -> 'None':
        """ Starts the Redis consumer in a background greenlet.
        """
        if self._running:
            return

        self._running = True
        self._pubsub = self.redis.pubsub()

        # Subscribe to the main channel
        self._pubsub.subscribe(**{self.channel_name: self._on_message})

        def _consume():
            while self._running:
                try:
                    message = self._pubsub.get_message(timeout=1.0)
                    if message:
                        self._on_message(message)
                except Exception as e:
                    if self._running:
                        logger.warning(f'Error in consumer loop: {e}')
                    sleep(0.1)

        self._consumer_greenlet = spawn(_consume)
        logger.info('Started Redis broker consumer')

# ################################################################################################################################

    def stop_consumer(self) -> 'None':
        """ Stops the Redis consumer.
        """
        self._running = False

        if self._pubsub:
            try:
                self._pubsub.unsubscribe()
                self._pubsub.close()
            except Exception:
                pass
            self._pubsub = None

        if self._consumer_greenlet:
            self._consumer_greenlet.kill()
            self._consumer_greenlet = None

        logger.info('Stopped Redis broker consumer')

# ################################################################################################################################

    def _create_reply_channel(self) -> 'str':
        """ Creates a unique reply channel name.
        """
        unique_name = f'{PubSub.Prefix.Reply_Queue}-{new_cid_broker_client()}'
        return unique_name

# ################################################################################################################################

    def _subscribe_to_reply_channel(self, channel_name:'str', callback:'callable_') -> 'None':
        """ Subscribe to a reply channel.
        """
        full_channel = f'{ModuleCtx.Reply_Prefix}{channel_name}'

        # Create a dedicated pubsub for this reply
        reply_pubsub = self.redis.pubsub()
        reply_pubsub.subscribe(full_channel)

        def _wait_for_reply():
            while True:
                try:
                    message = reply_pubsub.get_message(timeout=1.0)
                    if message and message['type'] == 'message':
                        self._on_reply(message)
                        break
                except Exception:
                    break
            try:
                reply_pubsub.unsubscribe()
                reply_pubsub.close()
            except Exception:
                pass

        _ = spawn(_wait_for_reply)

# ################################################################################################################################

    def _invoke_with_callback(self, msg:'anydict', callback:'callable_') -> '_InvokeWithCallbackCtx':
        """ Publishes a message and registers a callback for the reply.
        """
        correlation_id = new_cid_broker_client()
        reply_channel = self._create_reply_channel()

        # Subscribe to reply channel before publishing
        self._subscribe_to_reply_channel(reply_channel, callback)

        with self.lock:
            self._callbacks[correlation_id] = callback
            self.correlation_to_channel_map[correlation_id] = reply_channel

            if 'cid' in msg:
                cid = msg['cid']
                self._callbacks[cid] = callback
                self.correlation_to_channel_map[cid] = reply_channel

        msg['reply_to'] = reply_channel
        msg['cid'] = correlation_id

        msg_str = dumps(msg)

        # Publish to the server channel
        channel = f'{ModuleCtx.Channel_Prefix}server'
        _ = self.redis.publish(channel, msg_str)

        ctx = _InvokeWithCallbackCtx()
        ctx.correlation_id = correlation_id
        ctx.reply_channel = reply_channel

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
        """ Waits for a response within the specified timeout.
        """
        end_time = utcnow() + timedelta(seconds=timeout)

        while not response.ready and utcnow() < end_time:
            sleep(sleep_time)
            time_left = (end_time - utcnow()).total_seconds()
            if _needs_details:
                logger.debug(f'Still waiting - channel: {ctx.reply_channel}, time left: {time_left:.1f}s')

# ################################################################################################################################

    def _invoke_sync(
        self,
        service:'str',
        request:'anydictnone'=None,
        timeout:'int | float'=PubSub.Timeout.Invoke_Sync,
        needs_root_elem:'bool'=False,
        cid:'str'='',
    ) -> 'any_':
        """ Synchronously invokes a service and waits for the response.
        """
        sleep_time = 0.05

        class ResponseHolder:
            def __init__(self):
                self.data = None
                self.ready = False
                self.error = None
                self.reply_channel = None
                self.cid = 'cid-not-set'
                self.service = 'service-not-set'

            def set_response(self, response):
                self.data = response
                self.ready = True
                logger.info(f'Rsp <- {self.cid} - `{self.service}`')

        response = ResponseHolder()
        response.service = service
        response.cid = cid

        msg = {
            'action': SERVICE.INVOKE.value,
            'service': service,
            'payload': request or {},
            'cid': cid,
            'request_type': 'sync',
        }

        ctx = self._invoke_with_callback(msg, response.set_response)
        response.reply_channel = ctx.reply_channel

        logger.info(f'Req -> {cid} - `{service}` - `{request}`')

        self._wait_for_response(ctx, response, timeout, sleep_time, cid)

        if not response.ready:
            with self.lock:
                _ = self._callbacks.pop(ctx.correlation_id, None)
                _ = self.correlation_to_channel_map.pop(ctx.correlation_id, None)

            raise NoResponseReceivedException(f'No response received from service `{service}`')

        if not needs_root_elem:
            data = response.data
            data_keys = list(data.keys())
            root = data_keys[0]
            data = data[root]
        else:
            data = response.data

        return data

# ################################################################################################################################

    def invoke_sync(self, *args:'any_', **kwargs:'any_') -> 'any_':
        response = None

        while not response:
            try:
                response = self._invoke_sync('demo.ping')
            except NoResponseReceivedException as e:
                logger.info('Timeout: %s', e)

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
        logger.info(f'[{cid}] Notified counterpart server via channel `{queue_name}`')

# ################################################################################################################################

    def ping_connection(self) -> 'None':
        """ Ping Redis to verify connection.
        """
        try:
            result = self.redis.ping()
            logger.info(f'Redis connection ping: OK (result={result})')
        except Exception as e:
            logger.error(f'Redis connection ping failed: {e}')
            raise

# ################################################################################################################################

    def create_internal_queue(self, queue_name:'str') -> 'None':
        """ No-op for Redis - channels are created on demand.
        """
        pass

# ################################################################################################################################

    def delete_queue(self, cid:'str', queue_name:'str') -> 'None':
        """ No-op for Redis - channels don't persist.
        """
        pass

# ################################################################################################################################

    def get_queue_list(
        self,
        cid:'str',
        prefix:'str'='',
        exclude_list:'strlist | None'=None,
    ) -> 'dictlist':
        """ Returns empty list - Redis pub/sub doesn't have persistent queues.
        """
        return []

# ################################################################################################################################

    def get_bindings(self, *args, **kwargs):
        return []

    def create_bindings(self, *args, **kwargs):
        pass

    def delete_bindings(self, *args, **kwargs):
        pass

    def update_bindings(self, *args, **kwargs):
        pass

    def delete_topic(self, *args, **kwargs):
        pass

    def get_bindings_by_queue(self, *args, **kwargs):
        return []

    def queue_has_bindings(self, *args, **kwargs):
        return False

    def get_bindings_by_routing_key(self, *args, **kwargs):
        return []

    def rename_topic(self, *args, **kwargs):
        pass

# ################################################################################################################################
# ################################################################################################################################
