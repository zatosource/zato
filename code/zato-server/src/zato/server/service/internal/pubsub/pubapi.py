# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime

# rapidjson
from rapidjson import loads

# Zato
from zato.common import CONTENT_TYPE
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
        input_optional = (Bool('gd'),)
        response_elem = None

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

        return security_id

# ################################################################################################################################

class TopicService(PubSubService):
    """ Main service responsible for publications to a given topic. Handles security and distribution
    of messages to target queues.
    """
    class SimpleIO(PubSubService.SimpleIO):
        input_optional = PubSubService.SimpleIO.input_optional + (
            Int('priority'), Int('expiration'), 'mime_type', AsIs('correl_id'), 'in_reply_to', AsIs('ext_client_id'))
        output_optional = (AsIs('msg_id'),)

# ################################################################################################################################

    def handle_POST(self):

        # Check credentials first
        security_id = self._pubsub_check_credentials()

        # Regardless of mime-type, we always accept it in JSON payload
        try:
            data_parsed = loads(self.request.raw_request)
        except ValueError:
            raise BadRequest(self.cid, 'JSON input could not be parsed')
        else:
            data = self.request.raw_request

        # Ignore the header set by curl and similar tools
        mime_type = self.wsgi_environ.get('CONTENT_TYPE')
        mime_type = mime_type if mime_type != 'application/x-www-form-urlencoded' else CONTENT_TYPE.JSON

        input = self.request.input

        self.response.payload.msg_id = self.invoke('zato.pubsub.publish.publish', {
            'topic_name': input.topic_name,
            'mime_type': mime_type,
            'security_id': security_id,
            'data': data,
            'data_parsed': data_parsed,
            'priority': input.priority,
            'expiration': input.expiration,
            'correl_id': input.correl_id,
            'in_reply_to': input.in_reply_to,
            'ext_client_id': input.ext_client_id,
            'has_gd': input.gd,
        })['response']['msg_id']

# ################################################################################################################################

class SubscribeService(PubSubService):
    """ Service through which HTTP Basic Auth-using clients subscribe to topics.
    """
    class SimpleIO(PubSubService.SimpleIO):
        input_optional = PubSubService.SimpleIO.input_optional + ('deliver_to', 'delivery_format')
        output_optional = ('sub_key', Int('queue_depth'))

    def handle_POST(self, _new_cid=new_cid, _utcnow=datetime.utcnow):

        # Check credentials first
        security_id = self._pubsub_check_credentials()

        response = self.invoke('zato.pubsub.subscribe.subscribe-service-impl', {
            'topic_name': self.request.input.topic_name,
            'security_id': security_id,
            'has_gd': self.request.input.gd,
            'deliver_to': self.request.input.deliver_to,
            'delivery_format': self.request.input.delivery_format,
        })['response']

        self.response.payload.sub_key = response['sub_key']
        self.response.payload.queue_depth = response['queue_depth']

# ################################################################################################################################

    def handle_GET(self):
        pass

# ################################################################################################################################

class Hook1(AdminService):
    pass

# ################################################################################################################################

class Hook2(AdminService):
    pass

# ################################################################################################################################
