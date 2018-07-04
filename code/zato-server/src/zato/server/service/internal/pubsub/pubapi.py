# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from traceback import format_exc

# rapidjson
from rapidjson import dumps, loads

# Zato
from zato.common import CONTENT_TYPE, PUBSUB
from zato.common.exception import BadRequest, Forbidden
from zato.common.util import new_cid
from zato.server.connection.web_socket import WebSocket
from zato.server.service import AsIs, Bool, Int, Service
from zato.server.service.internal import AdminService

# For pyflakes
WebSocket = WebSocket

# ################################################################################################################################

def parse_basic_auth(auth, prefix = 'Basic '):
    if not auth.startswith(prefix):
        raise ValueError('Missing Basic Auth prefix')

    _, auth = auth.split(prefix)
    auth = auth.strip().decode('base64')

    return auth.split(':', 1)

# ################################################################################################################################

class PubSubService(Service):
    class SimpleIO:
        input_required = ('topic_name',)
        response_elem = None
        skip_empty_keys = True
        default_value = None

# ################################################################################################################################

    def _pubsub_check_credentials(self):
        auth = self.wsgi_environ.get('HTTP_AUTHORIZATION')
        if not auth:
            raise Forbidden(self.cid)

        try:
            username, password = parse_basic_auth(auth)
        except ValueError:
            raise Forbidden(self.cid)

        basic_auth = self.server.worker_store.request_dispatcher.url_data.basic_auth_config.itervalues()

        for item in basic_auth:
            config = item['config']
            if config['is_active']:
                if config['username'] == username and config['password'] == password:
                    auth_ok = True
                    security_id = config['id']
                    break
                else:
                    auth_ok = False

        if not auth_ok:
            raise Forbidden(self.cid)

        try:
            endpoint_id = self.pubsub.get_endpoint_id_by_sec_id(security_id)
        except KeyError:
            self.logger.warn('Client credentials are valid but there is no pub/sub endpoint using them, sec_id:`%s`, e:`%s`',
                security_id, format_exc())
            raise Forbidden(self.cid)
        else:
            return endpoint_id

# ################################################################################################################################

class TopicService(PubSubService):
    """ Main service responsible for publications to and deliveries from a given topic. Handles security and distribution
    of messages to target queues or recipients.
    """
    class SimpleIO(PubSubService.SimpleIO):
        input_optional = ('data', AsIs('msg_id'), 'has_gd', Int('priority'),
            Int('expiration'), 'mime_type', AsIs('correl_id'), 'in_reply_to', AsIs('ext_client_id'), 'ext_pub_time',
            'sub_key')
        output_optional = (AsIs('msg_id'),)

# ################################################################################################################################

    def _publish(self, endpoint_id):
        """ POST /zato/pubsub/subscribe/topic/{topic_name} {"data":"my data", ...}
        """
        # Ignore the header set by curl and similar tools
        mime_type = self.wsgi_environ.get('CONTENT_TYPE')
        mime_type = mime_type if mime_type != 'application/x-www-form-urlencoded' else CONTENT_TYPE.JSON

        input = self.request.input

        ctx = {
            'mime_type': mime_type,
            'data': input.data,
            'priority': input.priority,
            'expiration': input.expiration,
            'correl_id': input.correl_id,
            'in_reply_to': input.in_reply_to,
            'ext_client_id': input.ext_client_id,
            'has_gd': input.has_gd or False,
            'endpoint_id': endpoint_id,
        }

        return self.pubsub.publish(input.topic_name, **ctx)

# ################################################################################################################################

    def _get_messages(self, ctx):
        """ POST /zato/pubsub/topic/{topic_name}?sub_key=...
        """
        return self.pubsub.get_messages(self.request.input.topic_name, self.request.input.sub_key)

# ################################################################################################################################

    def handle_POST(self):

        # Checks credentials and returns endpoint_id if valid
        endpoint_id = self._pubsub_check_credentials()

        # Both publish and get_messages are using POST but sub_key is absent in the latter.
        if self.request.input.sub_key:
            self.response.payload = dumps(self._get_messages(endpoint_id))
        else:
            self.response.payload.msg_id = self._publish(endpoint_id)

# ################################################################################################################################

class SubscribeService(PubSubService):
    """ Service through which REST clients subscribe to or unsubscribe from topics.
    """
    class SimpleIO(PubSubService.SimpleIO):
        input_optional = ('sub_key',)
        output_optional = ('sub_key', 'queue_depth')

# ################################################################################################################################

    def _check_sub_access(self, endpoint_id):

        # At this point we know that the credentials are valid and in principle, there is such an endpoint,
        # but we still don't know if it has permissions to subscribe to this topic and we don't want to reveal
        # information about what topics exist or not.
        try:
            topic = self.pubsub.get_topic_by_name(self.request.input.topic_name)
        except KeyError:
            self.logger.warn(format_exc())
            raise Forbidden(self.cid)

        # We know the topic exists but we also need to make sure the endpoint can subscribe to it
        if not self.pubsub.is_allowed_sub_topic_by_endpoint_id(topic.name, endpoint_id):
            endpoint = self.pubsub.get_endpoint_by_id(endpoint_id)
            self.logger.warn('Endpoint `%s` is not allowed to subscribe to `%s`', endpoint.name, self.request.input.topic_name)
            raise Forbidden(self.cid)

# ################################################################################################################################

    def handle_POST(self, _new_cid=new_cid, _utcnow=datetime.utcnow):

        # Checks credentials and returns endpoint_id if valid
        endpoint_id = self._pubsub_check_credentials()

        # Make sure this endpoint has correct subscribe permissions (patterns)
        self._check_sub_access(endpoint_id)

        response = self.invoke('zato.pubsub.subscription.subscribe-rest', {
            'topic_name': self.request.input.topic_name,
            'endpoint_id': endpoint_id,
            'delivery_batch_size': PUBSUB.DEFAULT.DELIVERY_BATCH_SIZE,
            'delivery_format': PUBSUB.DELIVERY_METHOD.PULL.id,
        })['response']

        self.response.payload.sub_key = response['sub_key']
        self.response.payload.queue_depth = response['queue_depth']

# ################################################################################################################################

    def handle_DELETE(self):

        # Local aliases
        topic_name = self.request.input.topic_name
        sub_key = self.request.input.sub_key

        # Checks credentials and returns endpoint_id if valid
        endpoint_id = self._pubsub_check_credentials()

        # To unsubscribe, we also need to have the right subscription permissions first (patterns) ..
        self._check_sub_access(endpoint_id)

        # .. also check that sub_key exists and that we are not using another endpoint's sub_key.
        try:
            sub = self.pubsub.get_subscription_by_sub_key(sub_key)
        except KeyError:
            self.logger.warn('Could not find subscription by sub_key:`%s`, endpoint:`%s`',
                sub_key, self.pubsub.get_endpoint_by_id(endpoint_id).name)
            raise Forbidden(self.cid)
        else:
            if sub.endpoint_id != endpoint_id:
                sub_endpoint = self.pubsub.get_endpoint_by_id(sub.endpoint_id)
                self_endpoint = self.pubsub.get_endpoint_by_id(endpoint_id)
                self.logger.warn('Endpoint `%s` cannot unsubscribe sk:`%s` (%s) created by `%s`',
                    self_endpoint.name, sub_key, self.pubsub.get_topic_by_sub_key(sub_key).name, sub_endpoint.name)
                raise Forbidden(self.cid)

        # We have all permissions checked now and can proceed to the actual call
        self.invoke('zato.pubsub.endpoint.delete-endpoint-queue', {
            'cluster_id': self.server.cluster_id,
            'sub_key': sub_key
        })

# ################################################################################################################################
