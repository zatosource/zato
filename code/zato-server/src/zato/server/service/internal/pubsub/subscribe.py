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
from zato.common import PUBSUB
from zato.common.broker_message import PUBSUB as BROKER_MSG_PUBSUB
from zato.common.exception import BadRequest, NotFound, Forbidden, PubSubSubscriptionExists
from zato.common.odb.model import PubSubEndpointEnqueuedMessage, PubSubMessage, PubSubSubscription, WebSocketSubscription
from zato.common.pubsub import new_sub_key
from zato.common.time_util import utcnow_as_ms
from zato.server.service import AsIs, Bool, Int, Opaque
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

sub_broker_attrs = ('active_status', 'active_status', 'cluster_id', 'creation_time', 'endpoint_id', 'has_gd', 'id',
    'is_durable', 'is_internal', 'name', 'out_amqp_id', 'out_http_soap_id', 'sub_key', 'topic_id', 'ws_channel_id',
    'ws_sub_id', 'delivery_group_size')

# ################################################################################################################################

class SubscribeServiceImpl(AdminService):
    class SimpleIO(AdminSIO):
        input_required = ('topic_name',)
        input_optional = (Bool('gd'), 'deliver_to', 'delivery_format', 'security_id', 'ws_channel_id', 'ws_channel_name',
            AsIs('ws_pub_client_id'), 'sql_ws_client_id', 'deliver_by', 'is_internal', AsIs('ext_client_id'),
            'delivery_group_size', Opaque('web_socket'))
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

                    # This object will be transient - dropped each time a WSX disconnects
                    self.pubsub.add_ws_client_pubsub_keys(session, sql_ws_client_id, sub_key,
                        self.request.input.ws_channel_name, self.request.input.ws_pub_client_id)

                    # Let the WebSocket connection object know that it should handle this particular sub_key
                    self.request.input.web_socket.pubsub_tool.add_sub_key(sub_key)

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

                broker_input.action = BROKER_MSG_PUBSUB.SUBSCRIPTION_CREATE.value
                self.broker_client.publish(broker_input)

# ################################################################################################################################
