# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from datetime import datetime, timedelta

# rapidjson
from rapidjson import dumps, loads

# Zato
from zato.common import CONTENT_TYPE, DATA_FORMAT, PUBSUB
from zato.common.exception import BadRequest, NotFound, Forbidden
from zato.common.odb.model import PubSubTopic, PubSubEndpoint, PubSubEndpointQueue, PubSubMessage
from zato.server.service import Int, Service

# ################################################################################################################################

_PRIORITY=PUBSUB.PRIORITY
_JSON=DATA_FORMAT.JSON

# ################################################################################################################################

def parse_basic_auth(auth, prefix = 'Basic '):
    if not auth.startswith(prefix):
        raise ValueError('Missing Basic Auth prefix')

    _, auth = auth.split(prefix)
    auth = auth.strip().decode('base64')

    return auth.split(':', 1)

# ################################################################################################################################
'''
class DataMessage(object):
    __slots__ = ('data', 'topic_name', 'expiration', 'mime_type', 'priority')

    def __init__(self, data=None, topic_name=None, expiration=None, mime_type=None, priority=None):
        self.data = data
        self.topic_name = topic_name
        self.expiration = expiration
        self.mime_type = mime_type
        self.priority = priority
'''

# ################################################################################################################################

class TopicService(Service):
    """ Main service responsible for publications to a given topic. Handles security and distribution
    of messages to target queues.
    """
    class SimpleIO:
        input_required = ('topic_name',)
        input_optional = (Int('priority'), Int('expiration'), 'mime_type')

# ################################################################################################################################

    def handle_POST(self, _pri_min=_PRIORITY.MIN, _pri_max=_PRIORITY.MAX, _pri_def=_PRIORITY.DEFAULT, _JSON=_JSON):

        # Check credentials first
        auth = self.wsgi_environ.get('HTTP_AUTHORIZATION')
        if not auth:
            raise Forbidden(self.cid)

        try:
            username, password = parse_basic_auth(auth)
        except ValueError:
            raise Forbidden(self.cid)

        worker_store = self.server.worker_store
        pubsub = worker_store.pubsub
        basic_auth = worker_store.request_dispatcher.url_data.basic_auth_config.itervalues()

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

        # Local alias
        input = self.request.input

        # Credentials are fine, now check whether that user has access to the topic given on input
        topic_name = input.topic_name

        # Confirm if this client may publish at all to the topic it chose
        if not pubsub.is_allowed_pub_topic(topic_name, security_id=security_id):
            raise Forbidden(self.cid)

        # Regardless of mime-type, we always accept it in JSON payload
        try:
            loads(self.request.raw_request)
        except ValueError:
            raise BadRequest(self.cid, 'JSON input could not be parsed')
        else:
            data = self.request.raw_request

        # Ignore the header set by curl and similar tools
        mime_type = self.wsgi_environ.get('CONTENT_TYPE')
        mime_type = mime_type if mime_type != 'application/x-www-form-urlencoded' else CONTENT_TYPE.JSON

        # Get and validate priority
        priority = input.get('priority')
        if priority:
            if priority < _pri_min or priority > _pri_max:
                raise BadRequest(self.cid, 'Priority `{}` outside of allowed range {}-{}'.format(priority, _pri_min, _pri_max))
        else:
            priority = _pri_def

        # Get and validate expiration
        expiration = input.get('expiration')
        if expiration is not None and expiration < 0:
            raise BadRequest(self.cid, 'Expiration `{}` must not be negative'.format(expiration))

        # Construct the message object now that we have everything validated
        '''
        data_msg = DataMessage()
        data_msg.data = data
        data_msg.topic_name = topic_name
        data_msg.expiration = expiration
        data_msg.mime_type = mime_type
        data_msg.priority = priority
        '''

        # Get all subscribers for that topic from local worker store
        subscriptions_by_topic = pubsub.get_subscriptions_by_topic(topic_name)

        now = datetime.utcnow()
        expiration_time = now + timedelta(seconds=expiration) if expiration else None

        endpoint_id = pubsub.get_endpoint_id_by_sec_id(security_id)
        topic_id = pubsub.get_topic_id_by_name(topic_name)

        ps_msg = PubSubMessage()
        ps_msg.creation_time = now
        ps_msg.data = data
        ps_msg.data_format = _JSON
        ps_msg.mime_type = mime_type
        ps_msg.size = len(data)
        ps_msg.priority = priority
        ps_msg.expiration = expiration
        ps_msg.expiration_time = expiration_time
        ps_msg.published_by_id = endpoint_id
        ps_msg.topic_id = topic_id
        ps_msg.cluster_id = self.server.cluster_id

        # Operate under a global lock for that topic to rule out any interference
        with self.lock('zato.pubsub.publish.{}'.format(topic_name)):

            with closing(self.odb.session()) as session:

                # Enqueue a new message for all subscribers already known at the publication time
                for sub in subscriptions_by_topic:

                    queue_msg = PubSubEndpointQueue()
                    queue_msg.delivery_count = 0
                    queue_msg.msg = ps_msg
                    queue_msg.endpoint_id = endpoint_id
                    queue_msg.topic_id = topic_id
                    queue_msg.subscription_id = sub.id
                    queue_msg.cluster_id = self.server.cluster_id

                    session.add(queue_msg)

                session.commit()

# ################################################################################################################################
