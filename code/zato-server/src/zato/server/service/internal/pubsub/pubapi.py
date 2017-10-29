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
from zato.common.odb.model import PubSubTopic, PubSubEndpoint, PubSubEndpointQueue, PubSubEndpointTopic, PubSubMessage, \
     SecurityBase, Service as ODBService, ChannelWebSocket
from zato.common.odb.query import pubsub_message, query_wrapper
from zato.common.util import new_cid
from zato.server.pubsub import get_expiration, get_priority
from zato.server.service import AsIs, Bool, Int, Service
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################

_JSON = DATA_FORMAT.JSON

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
        input_optional = (Int('priority'), Int('expiration'), 'mime_type', AsIs('correl_id'), 'in_reply_to', Bool('gd'))
        output_optional = (AsIs('msg_id'),)
        response_elem = None

# ################################################################################################################################

    def handle_POST(self, _JSON=_JSON, _new_cid=new_cid, _utcnow=datetime.utcnow):
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
        pattern_matched = pubsub.is_allowed_pub_topic(topic_name, security_id=security_id)
        if not pattern_matched:
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

        priority = get_priority(self.cid, input)
        expiration = get_expiration(self.cid, input)

        # Construct the message object now that we have everything validated
        '''
        data_msg = DataMessage()
        data_msg.data = data
        data_msg.topic_name = topic_name
        data_msg.expiration = expiration
        data_msg.mime_type = mime_type
        data_msg.priority = priority
        '''

        try:
            topic = pubsub.get_topic_by_name(topic_name)
        except KeyError:
            raise NotFound(self.cid, 'No such topic `{}`'.format(topic_name))

        # Get all subscribers for that topic from local worker store
        subscriptions_by_topic = pubsub.get_subscriptions_by_topic(topic_name)

        now = _utcnow()
        expiration_time = now + timedelta(seconds=expiration) if expiration else None

        cluster_id = self.server.cluster_id

        pub_msg_id = 'zpsm%s' % _new_cid()
        pub_correl_id = input.get('correl_id')
        in_reply_to = input.get('in_reply_to')
        has_gd = input.gd if isinstance(input.gd, bool) else topic.has_gd

        endpoint_id = pubsub.get_endpoint_id_by_sec_id(security_id)

        ps_msg = PubSubMessage()
        ps_msg.pub_msg_id = pub_msg_id
        ps_msg.pub_correl_id = pub_correl_id
        ps_msg.in_reply_to = in_reply_to
        ps_msg.creation_time = now
        ps_msg.pattern_matched = pattern_matched
        ps_msg.data = data
        ps_msg.data_prefix = data[:2048]
        ps_msg.data_prefix_short = data[:64]
        ps_msg.data_format = _JSON
        ps_msg.mime_type = mime_type
        ps_msg.size = len(data)
        ps_msg.priority = priority
        ps_msg.expiration = expiration
        ps_msg.expiration_time = expiration_time
        ps_msg.published_by_id = endpoint_id
        ps_msg.topic_id = topic.id
        ps_msg.cluster_id = cluster_id
        ps_msg.has_gd = has_gd

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
                    filter(PubSubEndpointTopic.topic_id==topic.id).\
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
                ps_endpoint_topic.pattern_matched = pattern_matched

                session.add(ps_endpoint_topic)

                # Update metatadata for endpoint
                ps_endpoint = session.query(PubSubEndpoint).\
                    filter(PubSubEndpoint.id==endpoint_id).\
                    filter(PubSubEndpoint.cluster_id==cluster_id).\
                    one()

                ps_endpoint.last_seen = now
                ps_endpoint.last_pub_time = now

                session.add(ps_endpoint)

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
