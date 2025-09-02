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
from datetime import datetime
from json import loads
from http.client import OK
from logging import getLogger

# requests
import requests

# gunicorn
from gunicorn.app.base import BaseApplication

# werkzeug
from werkzeug.wrappers import Request

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.models import PubMessage
from zato.common.pubsub.models import APIResponse, BadRequestResponse, UnauthorizedResponse
from zato.common.pubsub.server.rest_base import BadRequestException, BaseRESTServer, UnauthorizedException
from zato.common.pubsub.util import set_time_since, validate_topic_name
from zato.common.util.api import as_bool, new_msg_id, utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, dictnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_needs_details = as_bool(os.environ.get('Zato_Needs_Details', False))

_min_priority = PubSub.Message.Priority_Min
_max_priority = PubSub.Message.Priority_Max
_default_priority = PubSub.Message.Priority_Default

_default_expiration = PubSub.Message.Default_Expiration

_max_messages_limit = 1000
_max_len_limit = PubSub.Message.Default_Max_Len
_default_max_messages = PubSub.Message.Default_Max_Messages

# ################################################################################################################################
# ################################################################################################################################

class PubSubRESTServer(BaseRESTServer):
    """ A REST server for pub/sub operations.
    """

# ################################################################################################################################
# ################################################################################################################################

#
# All the on_* methods are WSGI-level callbacks invoked by __call__
#

# ################################################################################################################################
# ################################################################################################################################

    def on_publish(self, cid:'str', environ:'anydict', start_response:'any_', topic_name:'str') -> 'APIResponse':
        """ Publish a message to a topic.
        """
        # Log what we're doing ..
        if _needs_details:
            logger.info(f'[{cid}] Processing publish request')

        # .. make sure the client is allowed to carry out this action ..
        username = self.authenticate(cid, environ)

        if _needs_details:
            logger.info(f'[{cid}] Authenticated user for messages/publish: `{username}`')

        # .. validate topic name ..
        validate_topic_name(topic_name)

        # .. check if user has permission to publish to this topic ..
        permission_result = self.backend.pattern_matcher.evaluate(username, topic_name, 'publish')
        if not permission_result.is_ok:
            logger.warning(f'[{cid}] User {username} denied publish access to topic {topic_name}: {permission_result.reason}')
            raise UnauthorizedException(cid, 'Permission denied')

        # .. build our representation of the request ..
        request = Request(environ)
        data = self._parse_json(cid, request)

        # .. make sure we actually did receive anything ..
        if not data:
            raise BadRequestException(cid, 'Input data missing')

        # .. now also make sure we did receive the business data ..
        msg_data = data.get('data')

        if msg_data is None:
            raise BadRequestException(cid, 'Message data missing')

        # .. get all the details from the message now that we know we have it ..
        ext_client_id = data.get('ext_client_id', '')
        priority = data.get('priority', _default_priority)
        expiration = data.get('expiration', _default_expiration)
        correl_id = data.get('correl_id', '') or cid
        in_reply_to=data.get('in_reply_to', '')

        # .. this is optional ..
        pub_time = data.get('pub_time', '')

        # .. make sure it's valid if given on input ..
        if pub_time:
            _ = datetime.fromisoformat(pub_time)

        # .. make sure the priority is valid ..
        if priority < _min_priority or priority > _max_priority:
            priority = _default_priority

        # .. make sure the expiration is valid ..
        expiration = round(expiration)
        if expiration < 1:
            expiration = 1

        # .. build a business message ..
        msg = PubMessage()
        msg.data = msg_data
        msg.priority = priority
        msg.expiration = expiration
        msg.correl_id = correl_id
        msg.ext_client_id = ext_client_id
        msg.pub_time = pub_time
        msg.in_reply_to = in_reply_to

        # .. let the backend handle it ..
        result = self.backend.publish_impl(cid, topic_name, msg, username, ext_client_id)

        # .. build our response ..
        response = APIResponse()
        response.is_ok = result.is_ok
        response.cid = cid
        response.msg_id = result.msg_id

        # .. and return it to the caller.
        return response

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
        rabbitmq_response = requests.post(api_url, json=payload, auth=self._broker_auth)

        if rabbitmq_response.status_code != OK:
            logger.error(f'[{cid}] RabbitMQ API error: {rabbitmq_response.status_code} - {rabbitmq_response.text}')
            return None

        return rabbitmq_response.json()

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
                payload = loads(payload_data)
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

    def _build_success_response(self, cid:'str', messages:'list', max_messages:'int', wrap_in_list:'bool') -> 'APIResponse':
        """ Create successful APIResponse with messages.
        """
        response = APIResponse()
        response.is_ok = True
        response.cid = cid
        response.data = None
        response.message_count = len(messages)

        # If max_messages is 1 and wrap_in_list is False, return single message format
        needs_single_message = max_messages == 1
        len_messages = len(messages)

        if needs_single_message and not wrap_in_list and len_messages == 1:
            message = messages[0]
            response.data = message['data']
            response.meta = message['meta']
        else:
            # Always wrap in list for max_messages > 1 or when wrap_in_list is True
            response.messages = messages

        return response

# ################################################################################################################################

    def _build_error_response(
        self,
        cid:'str',
        details:'str',
        *,
        response_class:'any_'=BadRequestResponse,
    ) -> 'BadRequestResponse | UnauthorizedResponse':
        """ Create error responses for various failure cases.
        """
        response = response_class()
        response.cid = cid
        response.details = details
        return response

# ################################################################################################################################

    def on_messages_get(self, cid:'str', environ:'anydict', start_response:'any_') -> 'APIResponse':
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

            #if _needs_details:
            logger.info(f'[{cid}] Retrieved {message_count} {message_word} for user `{username}` from queue `{sub_key}`')

            response = self._build_success_response(cid, messages, max_messages, wrap_in_list)
            return response

        except Exception as e:
            logger.error(f'[{cid}] Error retrieving messages: {e}')
            return self._build_error_response(cid, 'Internal error retrieving messages')

# ################################################################################################################################

    def on_subscribe(self, cid:'str', environ:'anydict', start_response:'any_', topic_name:'str') -> 'APIResponse':
        """ Handle subscription request.
        """
        # Log what we're doing ..
        logger.info(f'[{cid}] Processing subscribe request')

        # .. make sure the client is allowed to carry out this action ..
        username = self.authenticate(cid, environ)

        # .. validate topic name ..
        validate_topic_name(topic_name)

        # .. check if user has permission to subscribe to this topic ..
        permission_result = self.backend.pattern_matcher.evaluate(username, topic_name, 'subscribe')
        if not permission_result.is_ok:
            logger.warning(f'[{cid}] User {username} denied subscribe access to topic {topic_name}: {permission_result.reason}')
            raise UnauthorizedException(cid, 'Permission denied')

        # Subscribe to topic using backend
        result = self.backend.register_subscription(cid, topic_name, username=username, should_invoke_server=True)

        response = APIResponse()
        response.cid = cid
        response.is_ok = result.is_ok
        response.status = result.status
        return response

# ################################################################################################################################

    def on_unsubscribe(self, cid:'str', environ:'anydict', start_response:'any_', topic_name:'str') -> 'APIResponse':
        """ Handle unsubscribe request.
        """
        logger.info(f'[{cid}] Processing unsubscribe request')

        # .. make sure the client is allowed to carry out this action ..
        username = self.authenticate(cid, environ)

        # .. validate topic name ..
        validate_topic_name(topic_name)

        # .. check if user has permission to subscribe to this topic ..
        permission_result = self.backend.pattern_matcher.evaluate(username, topic_name, 'subscribe')
        if not permission_result.is_ok:
            logger.warning(f'[{cid}] User {username} denied subscribe access to topic {topic_name}: {permission_result.reason}')
            raise UnauthorizedException(cid, 'Permission denied')

        # Unsubscribe from topic using backend
        result = self.backend.unregister_subscription(cid, topic_name, username=username)

        response = APIResponse()
        response.is_ok = result.is_ok
        response.cid = cid

        return response

# ################################################################################################################################
# ################################################################################################################################

class GunicornApplication(BaseApplication):
    """ Gunicorn application wrapper for the PubSub REST API.
    """
    def __init__(self, app:'PubSubRESTServer', options:'dictnone'=None):
        self.options = options or {}
        self.options.setdefault('post_fork', self.on_post_fork)
        self.application = app
        super().__init__()

    def load_config(self):
        # Apply valid configuration options
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None: # type: ignore
                self.cfg.set(key.lower(), value) # type: ignore

    def load(self):
        return self.application

    def on_post_fork(self, server, worker):
        logger.info(f'Setting up PubSub REST server at {self.cfg.address}') # type: ignore
        self.application.init_broker_client()
        self.application.setup()

# ################################################################################################################################
# ################################################################################################################################
