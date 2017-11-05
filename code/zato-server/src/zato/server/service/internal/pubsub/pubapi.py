# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from datetime import datetime, timedelta

# gevent
from gevent import spawn

# rapidjson
from rapidjson import dumps, loads

# SQLAlchemy
from sqlalchemy import and_, exists, insert, select, update
from sqlalchemy.sql import expression as expr, func

# Zato
from zato.common import CONTENT_TYPE, DATA_FORMAT, PUBSUB
from zato.common.exception import BadRequest, NotFound, Forbidden, TooManyRequests, ServiceUnavailable
from zato.common.odb.model import PubSubTopic, PubSubEndpoint, PubSubEndpointEnqueuedMessage, PubSubEndpointTopic, PubSubMessage, \
     PubSubSubscription, SecurityBase, Service as ODBService, ChannelWebSocket
from zato.common.odb.query import pubsub_message, pubsub_messages_for_queue, pubsub_queue_message, query_wrapper
from zato.common.pubsub import new_msg_id, new_sub_key
from zato.common.time_util import datetime_from_ms, datetime_to_ms, utcnow_as_ms
from zato.common.util import new_cid
from zato.server.pubsub import get_expiration, get_priority
from zato.server.service import AsIs, Bool, Int, Service
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

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

        self.response.payload.msg_id = self.invoke('zato.pubsub.message.publish', {
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

class SubscribeServiceImpl(AdminService):
    name = 'pubapi1.subscribe-service-impl'

    class SimpleIO(AdminSIO):
        input_required = ('topic_name',)
        input_optional = (Bool('gd'), 'deliver_to', 'delivery_format', 'security_id', 'ws_channel_id')
        output_optional = ('sub_key', Int('queue_depth'))

# ################################################################################################################################

    def handle(self):

        input = self.request.input
        topic_name = self.request.input.topic_name
        pubsub = self.server.worker_store.pubsub

        if input.security_id:
            endpoint_id = pubsub.get_endpoint_id_by_sec_id(input.security_id)
        elif input.ws_channel_id:
            endpoint_id = pubsub.get_endpoint_id_by_ws_channel_id(input.ws_channel_id)
        else:
            raise NotImplementedError('To be implemented')

        # Confirm if this client may subscribe at all to the topic it chose
        kwargs = {'security_id':input.security_id} if input.security_id else {'ws_channel_id':input.ws_channel_id}
        pattern_matched = pubsub.is_allowed_sub_topic(topic_name, **kwargs)
        if not pattern_matched:
            raise Forbidden(self.cid)

        try:
            topic = pubsub.get_topic_by_name(topic_name)
        except KeyError:
            raise NotFound(self.cid, 'No such topic `{}`'.format(topic_name))

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

                    now = utcnow_as_ms()
                    sub_key = new_sub_key()

                    # Create a new subscription object
                    ps_sub = PubSubSubscription()
                    ps_sub.active_status = PUBSUB.QUEUE_ACTIVE_STATUS.FULLY_ENABLED.id
                    ps_sub.is_internal = False
                    ps_sub.creation_time = now
                    ps_sub.pattern_matched = pattern_matched
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
                        expr.bindparam('creation_time', now),
                        expr.bindparam('delivery_count', 0),
                        expr.bindparam('endpoint_id', endpoint_id),
                        expr.bindparam('subscription_id', ps_sub.id),
                        expr.bindparam('has_gd', False),
                        expr.bindparam('is_in_staging', False),
                        expr.bindparam('cluster_id', self.server.cluster_id),
                        ).\
                        filter(PubSubMessage.topic_id==topic.id).\
                        filter(PubSubMessage.cluster_id==self.server.cluster_id).\
                        filter(PubSubMessage.expiration_time > now)

                    # INSERT references to topic's messages in the subscriber's queue.
                    insert_messages = insert(PubSubEndpointEnqueuedMessage).\
                        from_select((
                            PubSubEndpointEnqueuedMessage.msg_id,
                            PubSubEndpointEnqueuedMessage.topic_id,
                            expr.column('creation_time'),
                            expr.column('delivery_count'),
                            expr.column('endpoint_id'),
                            expr.column('subscription_id'),
                            expr.column('has_gd'),
                            expr.column('is_in_staging'),
                            expr.column('cluster_id'),
                            ), select_messages)

                    # Commit changes to subscriber's queue
                    session.execute(insert_messages)

                    # Get the number of messages moved to let the subscriber know
                    # how many there are available initially.
                    moved_q = session.query(PubSubEndpointEnqueuedMessage.id).\
                        filter(PubSubEndpointEnqueuedMessage.subscription_id==ps_sub.id).\
                        filter(PubSubEndpointEnqueuedMessage.cluster_id==self.server.cluster_id)

                    total_moved_q = moved_q.statement.with_only_columns([func.count()]).order_by(None)
                    total_moved = moved_q.session.execute(total_moved_q).scalar()

                    session.commit()

                    # Produce response
                    self.response.payload.sub_key = sub_key
                    self.response.payload.queue_depth = total_moved

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

        response = self.invoke('pubapi1.subscribe-service-impl', {
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
