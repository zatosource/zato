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
# orjson
import orjson
from http.client import OK
from logging import getLogger

# httpx
import httpx

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

# ################################################################################################################################
# ################################################################################################################################

class PubSubRESTServerPull(BaseRESTServer):
    """ A REST server for pub/sub message pulling operations.
    """
    server_type = 'pull'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client = self._create_client()

    def _create_client(self):
        """ Create httpx client with connection pooling.
        """
        limits = httpx.Limits(
            max_keepalive_connections=500,
            max_connections=500
        )
        return httpx.Client(
            limits=limits,
            auth=(self._broker_config.username, self._broker_config.password)
        )

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

    def _fetch_from_rabbitmq(self, cid:'str', api_url:'str', payload:'dict') -> 'list | None':
        """ Make HTTP request to RabbitMQ API.
        """
        rabbitmq_response = self._client.post(api_url, json=payload)

        if rabbitmq_response.status_code != OK:
            logger.error(f'[{cid}] RabbitMQ API error: {rabbitmq_response.status_code} - {rabbitmq_response.text}')
            return None

        return orjson.loads(rabbitmq_response.content)

# ################################################################################################################################

    def _transform_messages(self, messages_data:'list') -> 'list':
        """ Convert RabbitMQ format to Zato API format.
        """
        current_time = utcnow()
        messages = []

        for msg in messages_data:

            payload_data = msg.get('payload', '')

            # Parse the payload to extract the original data
            if isinstance(payload_data, str):
                payload = orjson.loads(payload_data)
            else:
                payload = payload_data

            actual_data = payload.get('data', payload_data)
            msg_id = payload.get('msg_id', '')
            priority = payload.get('priority', _default_priority)

            pub_time_iso = payload.get('pub_time_iso', '')
            pub_time_iso = pub_time_iso.replace('Z', '+00:00')

            recv_time_iso = payload.get('recv_time_iso', '')
            recv_time_iso = recv_time_iso.replace('Z', '+00:00')

            expiration = payload.get('expiration', _default_expiration)
            topic_name = payload.get('topic_name', '')
            expiration_time_iso = payload.get('expiration_time_iso', '')
            size = payload.get('size', len(str(actual_data).encode('utf-8')))

            # Disabled until it's added to publishers
            # headers = properties.get('headers', {})
            # properties = msg.get('properties', {})
            # mime_type = properties.get('content_type', 'application/json')
            # ext_pub_time_iso = headers.get('ext_pub_time_iso', '')

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

                # Disabled until it's added to publishers
                # 'mime_type': mime_type,
                # 'ext_pub_time_iso': ext_pub_time_iso,

                'pub_time_iso': pub_time_iso,
                'recv_time_iso': recv_time_iso,
                'expiration_time_iso': expiration_time_iso,
            }

            # .. this is optional ..
            if ext_client_id := payload.get('ext_client_id'):
                meta['ext_client_id'] = ext_client_id

            # .. so is this ..
            if in_reply_to := payload.get('in_reply_to'):
                meta['in_reply_to'] = in_reply_to

            # .. calculate and set time deltas ..
            set_time_since(meta, pub_time_iso, recv_time_iso, current_time)

            # .. create the message structure with meta and data ..
            message = {
                'meta': meta,
                'data': actual_data
            }

            # .. OK, the message is ready ..
            messages.append(message)

        # .. and now we can return them all.
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

    def on_messages_get(self, cid:'str', environ:'anydict', start_response:'any_') -> '_base_response':
        """ Get messages from the user's queue.
        """
        if _needs_details:
            logger.info(f'[{cid}] Processing messages/get request')

        username = self.authenticate(cid, environ)

        if _needs_details:
            logger.info(f'[{cid}] Authenticated user for messages/get: `{username}`')

        request = Request(environ)
        data = self._parse_json(cid, request)

        max_len, max_messages, wrap_in_list = self._validate_get_params(data)

        if _needs_details:
            logger.info(f'[{cid}] Validated params: max_len={max_len}, max_messages={max_messages}, wrap_in_list={wrap_in_list}')

        sub_key = self._find_user_sub_key(cid, username)

        if _needs_details:
            logger.info(f'[{cid}] Found sub_key: {sub_key}')

        if not sub_key:
            logger.info(f'[{cid}] No sub_key found, returning error response')
            return self._build_error_response(cid, 'No subscription found for user', response_class=UnauthorizedResponse)

        if _needs_details:
            logger.info(f'[{cid}] Found subscription: user={username}, sub_key={sub_key}')

        api_url, rabbitmq_payload = self._build_rabbitmq_request(sub_key, max_messages, max_len)

        try:
            messages_data = self._fetch_from_rabbitmq(cid, api_url, rabbitmq_payload)
            if messages_data is None:
                return self._build_error_response(cid, 'Subscription not found')

            messages = self._transform_messages(messages_data)

            message_count = len(messages)
            message_word = 'message' if message_count == 1 else 'messages'

            if _needs_details:
                logger.info(f'[{cid}] Retrieved {message_count} {message_word} for user `{username}` from queue `{sub_key}`')

            response = self._build_success_response(cid, messages, max_messages, wrap_in_list)
            return response

        except Exception as e:
            logger.error(f'[{cid}] Error retrieving messages: {e}')
            return self._build_error_response(cid, 'Internal error retrieving messages')
# ################################################################################################################################
# ################################################################################################################################
