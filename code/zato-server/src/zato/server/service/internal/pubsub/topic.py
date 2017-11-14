# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# Bunch
from bunch import Bunch

# SQLAlchemy
from sqlalchemy import and_, exists, insert
from sqlalchemy.sql import expression as expr, func

# Zato
from zato.common.broker_message import PUBSUB
from zato.common.exception import BadRequest, NotFound, Forbidden, PubSubSubscriptionExists
from zato.common.odb.model import PubSubEndpointEnqueuedMessage, PubSubMessage, PubSubSubscription, PubSubTopic, \
     WebSocketClientPubSubKeys, WebSocketSubscription
from zato.common.odb.query import pubsub_messages_for_topic, pubsub_publishers_for_topic, pubsub_topic, pubsub_topic_list
from zato.common.pubsub import new_sub_key
from zato.common.time_util import datetime_from_ms, utcnow_as_ms
from zato.server.service import AsIs, Bool, Int
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################

elem = 'pubsub_topic'
model = PubSubTopic
label = 'a pub/sub topic'
broker_message = PUBSUB
broker_message_prefix = 'TOPIC_'
list_func = pubsub_topic_list
skip_input_params = ['is_internal', 'last_pub_time', 'current_depth']
output_optional_extra = ['current_depth', 'last_pub_time', 'is_internal']

# ################################################################################################################################

sub_broker_attrs = ('active_status', 'active_status', 'cluster_id', 'creation_time', 'endpoint_id', 'has_gd', 'id',
    'is_durable', 'is_internal', 'name', 'out_amqp_id', 'out_http_soap_id', 'sub_key', 'topic_id', 'ws_channel_id',
    'ws_sub_id', 'delivery_group_size')

# ################################################################################################################################

def broker_message_hook(self, input, instance, attrs, service_type):
    if service_type == 'create_edit':
        with closing(self.odb.session()) as session:
            input.is_internal = pubsub_topic(session, input.cluster_id, instance.id).is_internal

# ################################################################################################################################

def response_hook(service, input, instance, attrs, service_type):
    if service_type == 'get_list':
        for item in service.response.payload:
            if item.last_pub_time:
                item.last_pub_time = datetime_from_ms(item.last_pub_time)

# ################################################################################################################################

class GetList(AdminService):
    _filter_by = PubSubTopic.name,
    __metaclass__ = GetListMeta

# ################################################################################################################################

class Create(AdminService):
    __metaclass__ = CreateEditMeta

# ################################################################################################################################

class Edit(AdminService):
    __metaclass__ = CreateEditMeta

# ################################################################################################################################

class Delete(AdminService):
    __metaclass__ = DeleteMeta

# ################################################################################################################################

class Get(AdminService):
    class SimpleIO:
        input_required = ('cluster_id', AsIs('id'))
        output_required = ('id', 'name', 'is_active', 'is_internal', 'has_gd', 'max_depth', 'current_depth')
        output_optional = ('last_pub_time',)

    def handle(self):
        with closing(self.odb.session()) as session:
            topic = pubsub_topic(session, self.request.input.cluster_id, self.request.input.id)

        if topic.last_pub_time:
            topic.last_pub_time = datetime_from_ms(topic.last_pub_time)

        self.response.payload = topic

# ################################################################################################################################

class Clear(AdminService):
    class SimpleIO:
        input_required = ('cluster_id', AsIs('id'))

    def handle(self):
        with closing(self.odb.session()) as session:

            topic = session.query(PubSubTopic).\
                filter(PubSubTopic.cluster_id==self.request.input.cluster_id).\
                filter(PubSubTopic.id==self.request.input.id).\
                one()

            with self.lock('zato.pubsub.publish.%s' % topic.name):

                # Set metadata for topic
                topic.current_depth = 0

                # Remove all messages
                session.query(PubSubMessage).\
                    filter(PubSubMessage.cluster_id==self.request.input.cluster_id).\
                    filter(PubSubMessage.topic_id==self.request.input.id).\
                    delete()

                # Remove all references to topic messages from target queues
                session.query(PubSubEndpointEnqueuedMessage).\
                    filter(PubSubEndpointEnqueuedMessage.cluster_id==self.request.input.cluster_id).\
                    filter(PubSubEndpointEnqueuedMessage.topic_id==self.request.input.id).\
                    delete()

                session.commit()

# ################################################################################################################################

class GetPublisherList(AdminService):
    """ Returns all publishers that sent at least one message to a given topic.
    """
    class SimpleIO:
        input_required = ('cluster_id', 'topic_id')
        output_required = ('name', 'is_active', 'is_internal', 'pattern_matched')
        output_optional = ('service_id', 'security_id', 'ws_channel_id', 'last_seen', 'last_pub_time', AsIs('last_msg_id'),
            AsIs('last_correl_id'), 'last_in_reply_to', 'service_name', 'sec_name', 'ws_channel_name', AsIs('ext_client_id'))
        output_repeated = True

    def handle(self):
        response = []

        with closing(self.odb.session()) as session:

            # Get last pub time for that specific endpoint to this very topic
            last_data = pubsub_publishers_for_topic(session, self.request.input.cluster_id, self.request.input.topic_id).all()

            for item in last_data:
                item.last_seen = datetime_from_ms(item.last_pub_time)
                item.last_pub_time = datetime_from_ms(item.last_pub_time)
                response.append(item)

        self.response.payload[:] = response

# ################################################################################################################################

class GetMessageList(AdminService):
    """ Returns all messages currently in a topic that have not been moved to subscriber queues yet.
    """
    _filter_by = PubSubMessage.data_prefix,

    class SimpleIO(GetListAdminSIO):
        input_required = ('cluster_id', 'topic_id')
        output_required = (AsIs('msg_id'), 'pub_time', 'data_prefix_short', 'pattern_matched')
        output_optional = (AsIs('correl_id'), 'in_reply_to', 'size', 'service_id', 'security_id', 'ws_channel_id', 'service_name',
            'sec_name', 'ws_channel_name', 'endpoint_id', 'endpoint_name')
        output_repeated = True

    def get_data(self, session):
        return self._search(
            pubsub_messages_for_topic, session, self.request.input.cluster_id, self.request.input.topic_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

        for item in self.response.payload.zato_output:
            item.pub_time = datetime_from_ms(item.pub_time)
            item.ext_pub_time = datetime_from_ms(item.ext_pub_time) if item.ext_pub_time else ''

# ################################################################################################################################

class SubscribeServiceImpl(AdminService):
    class SimpleIO(AdminSIO):
        input_required = ('topic_name',)
        input_optional = (Bool('gd'), 'deliver_to', 'delivery_format', 'security_id', 'ws_channel_id',
            'sql_ws_client_id', 'deliver_by', 'is_internal', AsIs('ext_client_id'), 'delivery_group_size')
        output_optional = ('sub_key', Int('queue_depth'))

# ################################################################################################################################

    def handle(self):

        input = self.request.input
        topic_name = self.request.input.topic_name
        pubsub = self.server.worker_store.pubsub

        security_id = input.security_id or None
        ws_channel_id = input.ws_channel_id or None
        sql_ws_client_id = input.sql_ws_client_id or None

        if ws_channel_id and (not sql_ws_client_id):
            raise BadRequest(self.cid, 'sql_ws_client_id must not be empty if ws_channel_id is given on input')

        if security_id:
            endpoint_id = pubsub.get_endpoint_id_by_sec_id(security_id)
        elif ws_channel_id:
            endpoint_id = pubsub.get_endpoint_id_by_ws_channel_id(ws_channel_id)
        else:
            raise NotImplementedError('To be implemented')

        # Confirm if this client may subscribe at all to the topic it chose
        kwargs = {'security_id':security_id} if security_id else {'ws_channel_id':ws_channel_id}
        pattern_matched = pubsub.is_allowed_sub_topic(topic_name, **kwargs)
        if not pattern_matched:
            raise Forbidden(self.cid)

        try:
            topic = pubsub.get_topic_by_name(topic_name)
        except KeyError:
            raise NotFound(self.cid, 'No such topic `{}`'.format(topic_name))

        has_gd = input.gd if isinstance(input.gd, bool) else topic.has_gd
        is_internal = input.is_internal or False

        delivery_data_format = input.delivery_format or None
        deliver_to = input.deliver_to or None
        deliver_by = input.deliver_by or 'priority,ext_pub_time,pub_time'
        delivery_group_size = input.delivery_group_size or 1

        if input.ws_channel_id:
            delivery_method = PUBSUB.DELIVERY_METHOD.WEB_SOCKET
        else:
            delivery_method = PUBSUB.DELIVERY_METHOD.NOTIFY if deliver_to else PUBSUB.DELIVERY_METHOD.PULL

        with self.lock('zato.pubsub.subscribe.%s.%s' % (topic_name, endpoint_id)):

            with closing(self.odb.session()) as session:

                # Non-WebSocket clients cannot subscribe to the same topic multiple times
                if not ws_channel_id:
                    sub_exists = session.query(exists().where(and_(
                        PubSubSubscription.endpoint_id==endpoint_id,
                            PubSubSubscription.topic_id==topic.id,
                            PubSubSubscription.cluster_id==self.server.cluster_id,
                            ))).\
                        scalar()

                    if sub_exists:
                        raise PubSubSubscriptionExists(self.cid, 'Subscription to topic `{}` already exists'.format(topic.name))

                now = utcnow_as_ms()
                sub_key = new_sub_key()

                # If we subscribe a WSX client, we need to create its accompanying SQL models
                if ws_channel_id:

                    # This object persists across multiple WSX connections
                    ws_sub = WebSocketSubscription()
                    ws_sub.is_internal = is_internal
                    ws_sub.sub_key = sub_key
                    ws_sub.ext_client_id = input.ext_client_id
                    ws_sub.channel_id = ws_channel_id
                    ws_sub.cluster_id = self.server.cluster_id
                    session.add(ws_sub)

                    # This object is transient - it will be dropped each time a WSX client disconnects
                    ws_sub_key = WebSocketClientPubSubKeys()
                    ws_sub_key.client_id = sql_ws_client_id
                    ws_sub_key.sub_key = sub_key
                    ws_sub_key.cluster_id = self.server.cluster_id
                    session.add(ws_sub_key)

                else:
                    ws_sub = None

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
                ps_sub.deliver_by = deliver_by
                ps_sub.delivery_group_size = delivery_group_size
                ps_sub.ws_channel_id = ws_channel_id
                ps_sub.ws_sub = ws_sub
                ps_sub.cluster_id = self.server.cluster_id

                session.add(ps_sub)
                session.flush() # Flush the session because we need the subscription's ID below in INSERT from SELECT

                # SELECT statement used by the INSERT below finds all messages for that topic
                # that haven't expired yet.
                select_messages = session.query(
                    PubSubMessage.pub_msg_id, PubSubMessage.topic_id,
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
                        PubSubEndpointEnqueuedMessage.pub_msg_id,
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

                # Notify workers of a new subscription
                broker_input = Bunch()
                broker_input.topic_name = topic.name

                for name in sub_broker_attrs:
                    broker_input[name] = getattr(ps_sub, name, None)

                broker_input.action = PUBSUB.SUBSCRIPTION_CREATE.value
                self.broker_client.publish(broker_input)
