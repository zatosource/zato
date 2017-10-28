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

# SQLAlchemy
from sqlalchemy import and_, exists

# Zato
from zato.common import CONTENT_TYPE, DATA_FORMAT, PUBSUB
from zato.common.exception import BadRequest, NotFound, Forbidden, TooManyRequests, ServiceUnavailable
from zato.common.odb.model import PubSubTopic, PubSubEndpoint, PubSubEndpointQueue, PubSubEndpointTopic, PubSubMessage
from zato.common.odb.query import query_wrapper
from zato.common.util import new_cid
from zato.server.service import AsIs, Int, Service
from zato.server.service.internal import AdminService, GetListAdminSIO

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
        input_optional = (Int('priority'), Int('expiration'), 'mime_type', AsIs('correl_id'), 'in_reply_to')
        output_optional = (AsIs('msg_id'),)
        response_elem = None

# ################################################################################################################################

    def handle_POST(self, _pri_min=_PRIORITY.MIN, _pri_max=_PRIORITY.MAX, _pri_def=_PRIORITY.DEFAULT, _JSON=_JSON,
        _new_cid=new_cid):

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

        cluster_id = self.server.cluster_id

        pub_msg_id = 'zpsm.%s' % _new_cid()
        pub_correl_id = input.get('correl_id')
        in_reply_to = input.get('in_reply_to')

        endpoint_id = pubsub.get_endpoint_id_by_sec_id(security_id)

        topic = pubsub.get_topic_by_name(topic_name)

        ps_msg = PubSubMessage()
        ps_msg.pub_msg_id = pub_msg_id
        ps_msg.creation_time = now
        ps_msg.data = data
        ps_msg.data_format = _JSON
        ps_msg.mime_type = mime_type
        ps_msg.size = len(data)
        ps_msg.priority = priority
        ps_msg.expiration = expiration
        ps_msg.expiration_time = expiration_time
        ps_msg.published_by_id = endpoint_id
        ps_msg.topic_id = topic.id
        ps_msg.cluster_id = cluster_id

        # Operate under a global lock for that topic to rule out any interference
        with self.lock('zato.pubsub.publish.%s' % topic_name):

            with closing(self.odb.session()) as session:

                # Get the topic object which must exist, hence .one() is used.
                ps_topic = session.query(PubSubTopic).\
                    filter(PubSubTopic.id==topic.id).\
                    filter(PubSubTopic.cluster_id==cluster_id).\
                    one()

                # Abort if max_depth is already reached
                if ps_topic.current_depth >= topic.max_depth:
                    raise ServiceUnavailable(self.cid, 'Max depth already reached for `{}`'.format(topic.name))

                # Update metadata if max_depth is not reached yet
                else:
                    ps_topic.current_depth = ps_topic.current_depth + 1
                    ps_topic.last_pub_time = now
                    session.add(ps_topic)

                # Update information when this endpoint last published to the topic
                ps_endpoint_topic = session.query(PubSubEndpointTopic).\
                    filter(PubSubEndpointTopic.endpoint_id==endpoint_id).\
                    filter(PubSubEndpointTopic.id==topic.id).\
                    filter(PubSubEndpointTopic.cluster_id==cluster_id).\
                    first()

                # Never published before - add a new row then
                if not ps_endpoint_topic:
                    ps_endpoint_topic = PubSubEndpointTopic()
                    ps_endpoint_topic.endpoint_id = endpoint_id
                    ps_endpoint_topic.topic_id = topic.id
                    ps_endpoint_topic.cluster_id = cluster_id

                # New row or not, we have an object to
                ps_endpoint_topic.last_pub_time = now
                ps_endpoint_topic.pub_msg_id = pub_msg_id
                ps_endpoint_topic.pub_correl_id = pub_correl_id
                ps_endpoint_topic.in_reply_to = in_reply_to

                session.add(ps_endpoint_topic)

                # Add the parent message with actual data
                session.add(ps_msg)

                # Enqueue a new message for all subscribers already known at the publication time
                for sub in subscriptions_by_topic:

                    queue_msg = PubSubEndpointQueue()
                    queue_msg.delivery_count = 0
                    queue_msg.msg = ps_msg
                    queue_msg.endpoint_id = endpoint_id
                    queue_msg.topic_id = topic.id
                    queue_msg.subscription_id = sub.id
                    queue_msg.cluster_id = cluster_id

                    session.add(queue_msg)

                session.commit()

        self.response.payload.msg_id = pub_msg_id

# ################################################################################################################################

class GetEndpointTopicList(Service):
    """ Returns all topics to which a given endpoint published at least once.
    """
    class SimpleIO:
        input_required = ('cluster_id', 'endpoint_id')
        output_required = ('topic_id', 'name', 'is_active', 'is_internal', 'max_depth')
        output_optional = ('last_pub_time', AsIs('last_msg_id'), AsIs('last_correl_id'), 'last_in_reply_to')
        output_repeated = True

    def handle(self):
        input = self.request.input
        pubsub = self.server.worker_store.pubsub

        if input.cluster_id != self.server.cluster_id:
            raise BadRequest(self.cid, 'Invalid cluster_id value')

        response = []

        with closing(self.odb.session()) as session:

            # Get last pub time for that specific endpoint to this very topic
            last_data = session.query(
                PubSubTopic.id.label('topic_id'),
                PubSubTopic.name, PubSubTopic.is_active,
                PubSubTopic.is_internal, PubSubTopic.name,
                PubSubTopic.max_depth,
                PubSubEndpointTopic.last_pub_time,
                PubSubEndpointTopic.pub_msg_id.label('last_msg_id'),
                PubSubEndpointTopic.pub_correl_id.label('last_correl_id'),
                PubSubEndpointTopic.in_reply_to.label('last_in_reply_to'),
                ).\
                filter(PubSubEndpointTopic.topic_id==PubSubTopic.id).\
                filter(PubSubEndpointTopic.endpoint_id==input.endpoint_id).\
                filter(PubSubEndpointTopic.cluster_id==self.server.cluster_id).\
                all()

            for item in last_data:
                item.last_pub_time = item.last_pub_time.isoformat()
                response.append(item)

        self.response.payload[:] = response

# ################################################################################################################################

