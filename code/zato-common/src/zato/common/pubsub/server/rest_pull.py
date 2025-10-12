# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Must come first
from gevent import monkey;
_ = monkey.patch_all()

# stdlib
import os
from queue import Queue, Empty
from threading import RLock
from traceback import format_exc

# orjson
from logging import getLogger

# Kombu
from kombu import Connection
from kombu.exceptions import OperationalError

# prometheus
from prometheus_client import Histogram

# werkzeug
from werkzeug.wrappers import Request

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.models import APIResponse, BadRequestResponse, UnauthorizedResponse, _base_response
from zato.common.pubsub.server.rest_base import BaseRESTServer
from zato.common.pubsub.util import set_time_since
from zato.common.util.api import as_bool, utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.models import Subscription
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_needs_details = as_bool(os.environ.get('Zato_Needs_Details', False))

_default_priority = PubSub.Message.Priority_Default
_default_expiration = PubSub.Message.Default_Expiration

_max_messages_limit = 1000
_max_len_limit = PubSub.Message.Default_Max_Len
_default_max_messages = PubSub.Message.Default_Max_Messages

# Metrics
conn_acquire_time = Histogram('zato_pubsub_connection_acquire_seconds', 'Time to acquire AMQP connection')
amqp_fetch_time = Histogram('zato_pubsub_amqp_fetch_seconds', 'AMQP fetch operation duration')
msg_transform_time = Histogram('zato_pubsub_transform_seconds', 'Message transformation time')
queue_op_time = Histogram('zato_pubsub_queue_op_seconds', 'Queue operation latency')
queue_setup_time = Histogram('zato_pubsub_queue_setup_seconds', 'SimpleQueue setup time')
auth_time = Histogram('zato_pubsub_auth_seconds', 'Authentication time')
json_parse_time = Histogram('zato_pubsub_json_parse_seconds', 'JSON parsing time')
sub_lookup_time = Histogram('zato_pubsub_sub_lookup_seconds', 'Subscription lookup time')
total_request_time = Histogram('zato_pubsub_total_request_seconds', 'Total request processing time')

# ################################################################################################################################
# ################################################################################################################################

class PubSubRESTServerPull(BaseRESTServer):
    """ A REST server for pub/sub message pulling operations.
    """
    server_type = 'pull'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Connection pool for AMQP connections
        self._connection_pool = Queue()
        self._pool_lock = RLock()
        self._pool_initialized = False

        # Initialize the connection pool
        self._init_connection_pool()

# ################################################################################################################################

    def _init_connection_pool(self) -> 'None':
        """ Initialize the AMQP connection pool.
        """
        with self._pool_lock:
            if self._pool_initialized:
                return

            # Create initial connections
            pool_size = 200
            for _ in range(pool_size):
                try:
                    connection = self._create_amqp_connection()
                    self._connection_pool.put(connection, block=False)
                except Exception as e:
                    logger.error(f'Failed to create AMQP connection for pool: {e}')

            self._pool_initialized = True
            logger.info(f'Initialized AMQP connection pool with {self._connection_pool.qsize()} connections')

# ################################################################################################################################

    def _create_amqp_connection(self) -> 'Connection':
        """ Create a new AMQP connection.
        """
        broker_url = f'{self._broker_config.protocol}://' + \
                     f'{self._broker_config.username}:{self._broker_config.password}@' + \
                     f'{self._broker_config.address}/{self._broker_config.vhost}'
        connection = Connection(broker_url)
        _ = connection.connect()
        return connection

# ################################################################################################################################

    def _get_connection(self) -> 'Connection':
        """ Get a connection from the pool or create a new one.
        """
        with conn_acquire_time.time():
            try:
                connection = self._connection_pool.get(block=False)
                # Test if connection is still alive
                if not connection.connected:
                    connection.connect()
                return connection
            except Empty:
                # Pool is empty, create a new connection and expand the pool
                connection = self._create_amqp_connection()
                self._connection_pool.put(connection, block=False)
                return connection

# ################################################################################################################################

    def _return_connection(self, connection: 'Connection') -> 'None':
        """ Return a connection to the pool.
        """
        try:
            if connection.connected:
                self._connection_pool.put(connection, block=False)
            else:
                # Connection is dead, don't return it to pool
                pass
        except Exception:
            # Pool is full or connection is bad, just ignore
            pass

# ################################################################################################################################

    def _validate_get_params(self, data:'dict') -> 'tuple[int, int, bool]':
        """ Extract and validate max_len/max_messages parameters.
        """
        max_len = data.get('max_len', _max_len_limit)
        max_messages = data.get('max_messages', _default_max_messages)
        wrap_in_list = as_bool(data.get('wrap_in_list', False))

        max_len = min(max_len, _max_len_limit)
        max_messages = min(max_messages, _max_messages_limit)

        return max_len, max_messages, wrap_in_list

# ################################################################################################################################

    def _find_user_sub_key(self, cid:'str', username:'str') -> 'str | None':
        """ Find user's subscription key from topics.
        """
        # Get sec_name from username
        config = self.get_user_config(username)
        sec_name = config['sec_name']

        for topic_name, subs_by_sec_name in self.backend.subs_by_topic.items():
            if sec_name in subs_by_sec_name:
                subscription = subs_by_sec_name[sec_name]

                if subscription is None:
                    msg = f'[{cid}] Malformed subscription data for user `{username}` in topic `{topic_name}`'
                    raise Exception(msg)

                return subscription.sub_key

        else:
            msg = f'[{cid}] No subscription found for user `{username}`'
            logger.warning(msg)
            return None

# ################################################################################################################################

    def _find_user_subscription(self, username:'str') -> 'Subscription | None':

        # Get sec_name from username
        config = self.get_user_config(username)
        sec_name = config['sec_name']

        for subscriptions in self.backend.subs_by_topic.values():
            sub = subscriptions.get(sec_name)

            if sub:
                return sub

        return None

# ################################################################################################################################

    def _build_rabbitmq_request(self, sub_key:'str', max_messages:'int', max_len:'int') -> 'tuple[str, dict]':
        """ Build RabbitMQ API URL and payload.
        """
        api_url = f'{self._broker_api_base_url}/queues/{self._broker_config.vhost}/{sub_key}/get'

        rabbitmq_payload = {
            'count': max_messages,
            'ackmode': 'ack_requeue_false',
            'encoding': 'auto',
            'truncate': max_len
        }

        return api_url, rabbitmq_payload

# ################################################################################################################################

    def _fetch_from_rabbitmq(self, cid:'str', queue_name:'str', max_messages:'int') -> 'list':
        """ Fetch messages from RabbitMQ queue using AMQP connection pool.
        """
        with amqp_fetch_time.time():
            connection = None
            messages = []

            try:
                connection = self._get_connection()

                if _needs_details:
                    logger.info(f'[{cid}] Got AMQP connection for queue: {queue_name}')

                # Access the queue using SimpleQueue
                try:
                    with queue_setup_time.time():
                        simple_queue = connection.SimpleQueue(queue_name)

                    with simple_queue:

                        messages_retrieved = 0

                        with queue_op_time.time():
                            while messages_retrieved < max_messages:
                                try:
                                    # Get messages without waiting for them if none is available
                                    message = simple_queue.get(block=False)

                                    if message is None:
                                        break

                                    messages.append(message.payload)
                                    messages_retrieved += 1

                                    # Acknowledge the message
                                    message.ack()

                                except Empty:
                                    break

                                except Exception as e:
                                    logger.error(f'[{cid}] Error getting message: {format_exc()}')
                                    break

                except Exception as queue_error:
                    logger.error(f'[{cid}] Error accessing queue {queue_name}: {queue_error}')
                    return []

                return messages

            except OperationalError as e:
                logger.error(f'[{cid}] AMQP operational error for queue {queue_name}: {e}')
                return []
            except Exception as e:
                logger.error(f'[{cid}] Error fetching messages from queue {queue_name}: {e}')
                return []
            finally:
                if connection:
                    self._return_connection(connection)

# ################################################################################################################################

    def _transform_messages(self, messages_data:'list') -> 'list':
        """ Convert AMQP message format to Zato API format.
        """
        with msg_transform_time.time():
            messages = []
            current_time = utcnow()

            for payload in messages_data:

                actual_data = payload.get('data', payload)
                msg_id = payload.get('msg_id', '')
                priority = payload.get('priority', _default_priority)

                recv_time_iso = payload.get('recv_time_iso', '')
                recv_time_iso = recv_time_iso.replace('Z', '+00:00')

                expiration = payload.get('expiration', _default_expiration)
                topic_name = payload.get('topic_name', '')
                size = payload.get('size', len(str(actual_data).encode('utf-8')))

                correl_id = payload.get('correl_id', '')
                ext_client_id = payload.get('ext_client_id', '')
                in_reply_to = payload.get('in_reply_to', '')

                # We want for the keys to be serialized in a specific order ..
                meta = {
                    'topic_name': topic_name,
                    'size': size,
                    'priority': priority,
                    'expiration': expiration,

                    'msg_id': msg_id,
                    'correl_id': correl_id,
                }

                if pub_time_iso := payload.get('pub_time_iso'):
                    pub_time_iso = pub_time_iso.replace('Z', '+00:00')
                    meta['pub_time_iso'] = pub_time_iso

                if recv_time_iso := payload.get('recv_time_iso'):
                    recv_time_iso = recv_time_iso.replace('Z', '+00:00')
                    meta['recv_time_iso'] = recv_time_iso

                if expiration_time_iso := payload.get('expiration_time_iso'):
                    meta['expiration_time_iso'] = expiration_time_iso

                # .. this is optional ..
                if ext_client_id := payload.get('ext_client_id'):
                    meta['ext_client_id'] = ext_client_id

                # .. so is this ..
                if in_reply_to := payload.get('in_reply_to'):
                    meta['in_reply_to'] = in_reply_to

                # .. calculate and set time deltas ..
                if pub_time_iso or recv_time_iso:
                    set_time_since(meta, pub_time_iso, recv_time_iso, current_time)

                # .. create the message structure with meta and data ..
                message = {
                    'meta': meta,
                    'data': actual_data
                }

                messages.append(message)

            return messages

# ################################################################################################################################

    def _build_success_response(self, cid:'str', messages:'list', max_messages:'int', wrap_in_list:'bool') -> '_base_response':
        """ Create successful APIResponse with messages.
        """
        response:'APIResponse' = {
            'is_ok': True,
            'cid': cid,
            'data': None,
            'message_count': len(messages)
        }

        # If max_messages is 1 and wrap_in_list is False, return single message format
        needs_single_message = max_messages == 1
        len_messages = len(messages)

        if needs_single_message and not wrap_in_list and len_messages == 1:
            message = messages[0]
            response['data'] = message['data']
            response['meta'] = message['meta']
        else:
            # Always wrap in list for max_messages > 1 or when wrap_in_list is True
            response['messages'] = messages

        return response

# ################################################################################################################################

    def _build_error_response(
        self,
        cid:'str',
        details:'str',
        *,
        response_class:'any_'=BadRequestResponse,
    ) -> '_base_response':
        """ Create error responses for various failure cases.
        """
        response:'_base_response' = {
            'is_ok': False,
            'cid': cid,
            'details': details
        }
        return response

# ################################################################################################################################

    def _on_messages_get(self, cid:'str', environ:'anydict', start_response:'any_') -> '_base_response':
        """ Get messages from the user's queue.
        """
        if _needs_details:
            logger.info(f'[{cid}] Processing messages/get request')

        with auth_time.time():
            username = self.authenticate(cid, environ)

        if _needs_details:
            logger.info(f'[{cid}] Authenticated user for messages/get: `{username}`')

        request = Request(environ)
        with json_parse_time.time():
            data = self._parse_json(cid, request)

        max_len, max_messages, wrap_in_list = self._validate_get_params(data)

        if _needs_details:
            logger.info(f'[{cid}] Validated params: max_len={max_len}, max_messages={max_messages}, wrap_in_list={wrap_in_list}')

        with sub_lookup_time.time():
            subscription = self._find_user_subscription(username)

        if not subscription:
            return self._build_error_response(cid, 'No subscription found for user', response_class=UnauthorizedResponse)

        if not subscription.is_delivery_active:
            return self._build_error_response(cid, 'Delivery disabled', response_class=UnauthorizedResponse)

        # OK, we're sure we have a subscription now and it's active
        sub_key = subscription.sub_key

        try:
            messages_data = self._fetch_from_rabbitmq(cid, sub_key, max_messages)
            messages = self._transform_messages(messages_data)

            message_count = len(messages)
            message_word = 'message' if message_count == 1 else 'messages'

            if _needs_details:
                logger.info(f'[{cid}] Retrieved {message_count} {message_word} for user `{username}` from queue `{sub_key}`')

            response = self._build_success_response(cid, messages, max_messages, wrap_in_list)
            return response

        except Exception:
            logger.error(f'[{cid}] Error retrieving messages: {format_exc()}')
            return self._build_error_response(cid, 'Internal error retrieving messages')

# ################################################################################################################################

    def on_messages_get(self, cid:'str', environ:'anydict', start_response:'any_') -> '_base_response':
        """ Get messages from the user's queue.
        """
        with total_request_time.time():
            return self._on_messages_get(cid, environ, start_response)
# ################################################################################################################################
# ################################################################################################################################
