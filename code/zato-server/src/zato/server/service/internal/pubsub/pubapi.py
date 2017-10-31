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
from sqlalchemy import and_, exists, insert, select
from sqlalchemy.sql import expression as expr, func

# Zato
from zato.common import CONTENT_TYPE, DATA_FORMAT, PUBSUB
from zato.common.exception import BadRequest, NotFound, Forbidden, TooManyRequests, ServiceUnavailable
from zato.common.odb.model import PubSubTopic, PubSubEndpoint, PubSubEndpointQueue, PubSubEndpointTopic, PubSubMessage, \
     PubSubSubscription, SecurityBase, Service as ODBService, ChannelWebSocket
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
            Int('priority'), Int('expiration'), 'mime_type', AsIs('correl_id'), 'in_reply_to', )
        output_optional = (AsIs('msg_id'),)

# ################################################################################################################################

    def handle_POST(self, _JSON=_JSON, _new_cid=new_cid, _utcnow=datetime.utcnow, _dt_max=datetime.max):

        # Check credentials first
        security_id = self._pubsub_check_credentials()

        # Local aliases
        input = self.request.input
        pubsub = self.server.worker_store.pubsub

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
        expiration_time = now + timedelta(seconds=expiration) if expiration else _dt_max

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

class SubscribeService(PubSubService):
    """ Service through which clients subscribe to topics.
    """
    class SimpleIO(PubSubService.SimpleIO):
        input_optional = PubSubService.SimpleIO.input_optional + ('sub_key', 'deliver_to', 'delivery_format')
        output_optional = ('sub_key', Int('msg_count'))

    def handle_POST(self, _new_cid=new_cid, _utcnow=datetime.utcnow):

        # Check credentials first
        security_id = self._pubsub_check_credentials()

        # Local aliases
        input = self.request.input
        pubsub = self.server.worker_store.pubsub

        '''
        # Confirm that input sub_key belongs to the endpoint given on input
        with closing(self.odb.session()) as session:
            ps_endpoint = session.query(PubSubEndpoint).\
                filter(PubSubEndpoint.security_id==security_id).\
                filter(PubSubEndpoint.sub_key==input.sub_key).\
                filter(PubSubEndpoint.cluster_id==self.server.cluster_id).\
                first()

            if not ps_endpoint:
                raise Forbidden(self.cid)
        '''

        # Credentials are fine, now check whether that user has access to the topic given on input
        topic_name = input.topic_name

        # Confirm if this client may subscribe at all to the topic it chose
        pattern_matched = pubsub.is_allowed_sub_topic(topic_name, security_id=security_id)
        if not pattern_matched:
            raise Forbidden(self.cid)

        try:
            topic = pubsub.get_topic_by_name(topic_name)
        except KeyError:
            raise NotFound(self.cid, 'No such topic `{}`'.format(topic_name))

        endpoint_id = pubsub.get_endpoint_id_by_sec_id(security_id)
        has_gd = input.gd if isinstance(input.gd, bool) else topic.has_gd
        delivery_data_format = input.delivery_format or None
        deliver_to = input.deliver_to or None
        delivery_method = PUBSUB.DELIVERY_METHOD.NOTIFY if deliver_to else PUBSUB.DELIVERY_METHOD.PULL

        with self.lock('zato.pubsub.subscribe.%s.%s' % (topic_name, endpoint_id)):

            # Check if such a subscription doesn't already exist

            with closing(self.odb.session()) as session:
                sub_exists = session.query(exists().where(and_(
                        PubSubSubscription.endpoint_id==endpoint_id,
                        PubSubSubscription.topic_id==topic.id,
                        PubSubSubscription.cluster_id==self.server.cluster_id,
                        ))).\
                    scalar()

                if sub_exists:
                    raise BadRequest(self.cid, 'Subscription to topic `{}` already exists'.format(topic.name))
                else:

                    now = _utcnow()
                    sub_key = 'zpsk{}'.format(_new_cid())

                    # Create a new subscription object
                    ps_sub = PubSubSubscription()
                    ps_sub.is_active = True
                    ps_sub.is_internal = False
                    ps_sub.creation_time = now
                    ps_sub.sub_key = sub_key
                    ps_sub.has_gd = has_gd
                    ps_sub.topic_id = topic.id
                    ps_sub.endpoint_id = endpoint_id
                    ps_sub.delivery_method = delivery_method
                    ps_sub.delivery_data_format = delivery_data_format
                    ps_sub.delivery_endpoint = deliver_to
                    ps_sub.cluster_id = self.server.cluster_id

                    session.add(ps_sub)
                    session.flush() # Flush the session because we need the subscription's ID below in INSERT from SELECT

                    # SELECT statement used by the INSERT below finds all messages for that topic
                    # that haven't expired yet.
                    select_messages = session.query(
                        PubSubMessage.id, PubSubMessage.topic_id,
                        expr.bindparam('delivery_count', 0),
                        expr.bindparam('endpoint_id', endpoint_id),
                        expr.bindparam('subscription_id', ps_sub.id),
                        expr.bindparam('cluster_id', self.server.cluster_id),
                        ).\
                        filter(PubSubMessage.topic_id==topic.id).\
                        filter(PubSubMessage.cluster_id==self.server.cluster_id).\
                        filter(PubSubMessage.expiration_time > now)

                    # INSERT references to topic's messages in the subscriber's queue.
                    insert_messages = insert(PubSubEndpointQueue).\
                        from_select((
                            PubSubEndpointQueue.msg_id,
                            PubSubEndpointQueue.topic_id,
                            expr.column('delivery_count'),
                            expr.column('endpoint_id'),
                            expr.column('subscription_id'),
                            expr.column('cluster_id'),
                    ), select_messages)

                    # Commit changes to subscriber's queue
                    session.execute(insert_messages)
                    session.commit()

                    # Get the number of messages moved to let the subscriber know
                    # how many there are available initially.
                    moved_q = session.query(PubSubEndpointQueue.id).\
                        filter(PubSubEndpointQueue.subscription_id==ps_sub.id).\
                        filter(PubSubEndpointQueue.cluster_id==self.server.cluster_id)

                    total_moved_q = moved_q.statement.with_only_columns([func.count()]).order_by(None)
                    total_moved = moved_q.session.execute(total_moved_q).scalar()

                    self.response.payload.sub_key = sub_key
                    self.response.payload.msg_count = total_moved

# ################################################################################################################################
