# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Must come first
from gevent import monkey;
_ = monkey.patch_all()

# stdlib
from http.client import OK
from logging import getLogger

# requests
import requests

# Zato
from zato.common.typing_ import any_, anydict

# gunicorn
from gunicorn.app.base import BaseApplication

# werkzeug
from werkzeug.wrappers import Request

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.models import PubMessage
from zato.common.pubsub.models import APIResponse, BadRequestResponse
from zato.common.pubsub.server.rest_base import BadRequestException, BaseRESTServer, UnauthorizedException

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dictnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_default_priority = PubSub.Message.Default_Priority
_default_expiration = PubSub.Message.Default_Expiration
_max_messages_limit = 1000
_max_len_limit = 5_000_000

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
        logger.info(f'[{cid}] Processing publish request')

        # .. make sure the client is allowed to carry out this action ..
        username = self.authenticate(cid, environ)

        # .. check if user has permission to publish to this topic ..
        permission_result = self.backend.pattern_matcher.evaluate(username, topic_name, 'publish')
        if not permission_result.is_ok:
            logger.warning(f'[{cid}] User {username} denied publish access to topic {topic_name}: {permission_result.reason}')
            raise UnauthorizedException(cid, f'No permission to publish to topic {topic_name}')

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

        # .. build a business message ..
        msg = PubMessage()
        msg.data = msg_data
        msg.priority = priority
        msg.expiration = expiration
        msg.correl_id = correl_id
        msg.ext_client_id = ext_client_id
        msg.in_reply_to = in_reply_to

        # .. let the backend handle it ..
        result = self.backend.publish_impl(cid, topic_name, msg, username, ext_client_id)

        # .. build our response ..
        response = APIResponse()
        response.is_ok = result.is_ok
        response.cid = cid

        # .. and return it to the caller.
        return response

# ################################################################################################################################

    def on_messages_get(self, cid:'str', environ:'anydict', start_response:'any_') -> 'APIResponse':
        """ Get messages from the user's queue.
        """
        # Authenticate the user
        username = self.authenticate(cid, environ)

        # Parse request data
        request = Request(environ)
        data = self._parse_json(cid, request)

        # Extract and validate parameters
        max_len = data.get('max_len', _max_len_limit)
        max_messages = data.get('max_messages', 1)

        # Enforce limits
        max_len = min(max_len, _max_len_limit)
        max_messages = min(max_messages, _max_messages_limit)

        # Find the user's subscription to get their sub_key (queue name)
        sub_key = None
        for subs_by_sec_name in self.subs_by_topic.values():
            if username in subs_by_sec_name:
                subscription = subs_by_sec_name[username]
                sub_key = subscription.sub_key
                break

        if not sub_key:
            logger.warning(f'[{cid}] No subscription found for user `{username}`')
            response = BadRequestResponse()
            response.cid = cid
            response.details = 'No subscription found for user'
            return response

        # Build RabbitMQ API URL
        api_url = f'{self._broker_api_base_url}/queues/{self._broker_config.vhost}/{sub_key}/get'

        # Prepare request payload for RabbitMQ
        rabbitmq_payload = {
            'count': max_messages,
            'ackmode': 'ack_requeue_false',  # Acknowledge and delete messages
            'encoding': 'auto',
            'truncate': max_len
        }

        try:
            # Make request to RabbitMQ
            rabbitmq_response = requests.post(api_url, json=rabbitmq_payload, auth=self._broker_auth)

            if rabbitmq_response.status_code != OK:
                logger.error(f'[{cid}] RabbitMQ API error: {rabbitmq_response.status_code} - {rabbitmq_response.text}')
                response = BadRequestResponse()
                response.cid = cid
                response.details = 'Failed to retrieve messages from queue'
                return response

            # Parse RabbitMQ response
            messages_data = rabbitmq_response.json()

            # Transform messages to our API format
            messages = []
            for msg in messages_data:
                # Extract message properties
                properties = msg.get('properties', {})
                headers = properties.get('headers', {})
                payload_data = msg.get('payload', '')

                # Calculate size
                if isinstance(payload_data, str):
                    size = len(payload_data.encode('utf-8'))
                else:
                    size = len(payload_data)

                # Build our message format according to Zato spec
                message = {
                    'data': payload_data,
                    'msg_id': properties.get('message_id', ''),
                    'correl_id': properties.get('correlation_id', ''),
                    'priority': properties.get('priority', _default_priority),
                    'mime_type': properties.get('content_type', 'application/json'),
                    'pub_time_iso': properties.get('timestamp', ''),
                    'recv_time_iso': properties.get('timestamp', ''),
                    'expiration': properties.get('expiration', _default_expiration),
                    'topic_name': headers.get('topic_name', ''),
                    'ext_client_id': headers.get('ext_client_id', ''),
                    'ext_pub_time_iso': headers.get('ext_pub_time_iso', ''),
                    'in_reply_to': '',
                    'expiration_time_iso': '',
                    'size': size,
                }
                messages.append(message)

            logger.info(f'[{cid}] Retrieved {len(messages)} messages for user `{username}` from queue `{sub_key}`')

            # Build success response
            response = APIResponse()
            response.is_ok = True
            response.cid = cid
            response.data = messages

            return response

        except Exception as e:
            logger.error(f'[{cid}] Error retrieving messages: {e}')
            response = BadRequestResponse()
            response.cid = cid
            response.details = 'Internal error retrieving messages'
            return response

# ################################################################################################################################

    def on_subscribe(self, cid:'str', environ:'anydict', start_response:'any_', topic_name:'str') -> 'APIResponse':
        """ Handle subscription request.
        """
        # Log what we're doing ..
        logger.info(f'[{cid}] Processing subscribe request')

        # .. make sure the client is allowed to carry out this action ..
        username = self.authenticate(cid, environ)

        # Subscribe to topic using backend
        result = self.backend.register_subscription(cid, topic_name, username)

        response = APIResponse()
        response.is_ok = result.is_ok
        response.cid = cid

        return response

# ################################################################################################################################

    def on_unsubscribe(self, cid:'str', environ:'anydict', start_response:'any_', topic_name:'str') -> 'APIResponse':
        """ Handle unsubscribe request.
        """
        # Log what we're doing ..
        logger.info(f'[{cid}] Processing unsubscribe request')

        # .. make sure the client is allowed to carry out this action ..
        username = self.authenticate(cid, environ)

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
        self.application.setup()

# ################################################################################################################################
# ################################################################################################################################
