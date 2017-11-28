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

# Zato
from zato.common import PUBSUB
from zato.common.broker_message import PUBSUB as BROKER_MSG_PUBSUB
from zato.common.exception import BadRequest, NotFound, Forbidden, PubSubSubscriptionExists
from zato.common.odb.model import PubSubEndpoint, PubSubSubscription
from zato.common.odb.query_ps_subscribe import add_subscription, add_wsx_subscription, has_subscription, \
     move_messages_to_sub_queue
from zato.common.odb.query_ps_subscription import pubsub_endpoint_summary_list
from zato.common.pubsub import new_sub_key
from zato.common.time_util import datetime_from_ms, utcnow_as_ms
from zato.server.service import AsIs, Bool, Int, Opaque
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################

sub_broker_attrs = ('active_status', 'active_status', 'cluster_id', 'creation_time', 'endpoint_id', 'has_gd', 'id',
    'is_durable', 'is_internal', 'name', 'out_amqp_id', 'out_http_soap_id', 'sub_key', 'topic_id', 'ws_channel_id',
    'ws_sub_id', 'delivery_group_size')

# ################################################################################################################################

class GetEndpointSummaryList(AdminService):
    """ Returns summarized information about endpoints subscribed to topics.
    """
    _filter_by = PubSubEndpoint.name,

    class SimpleIO(GetListAdminSIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'endpoint_name', 'endpoint_type', 'subscription_count', 'is_active', 'is_internal')
        output_optional = ('security_id', 'sec_type', 'sec_name', 'ws_channel_id', 'ws_channel_name',
            'service_id', 'service_name', 'last_seen', 'last_deliv_time', 'role')
        request_elem = 'zato_pubsub_subscription_get_endpoint_summary_list_request'
        response_elem = 'zato_pubsub_subscription_get_endpoint_summary_list_response'

    def get_data(self, session):
        result = self._search(pubsub_endpoint_summary_list, session, self.request.input.cluster_id, False)
        for item in result:

            if item.last_seen:
                item.last_seen = datetime_from_ms(item.last_seen)

            if item.last_deliv_time:
                item.last_deliv_time = datetime_from_ms(item.last_deliv_time)

        return result

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################

class SubscribeServiceImpl(AdminService):
    class SimpleIO(AdminSIO):
        input_required = ('topic_name',)
        input_optional = (Bool('gd'), 'deliver_to', 'delivery_format', 'security_id', 'ws_channel_id', 'ws_channel_name',
            AsIs('ws_pub_client_id'), 'sql_ws_client_id', 'deliver_by', 'is_internal', AsIs('ext_client_id'),
            'delivery_group_size', Opaque('web_socket'))
        output_optional = ('sub_key', Int('queue_depth'))

# ################################################################################################################################

    def get_pattern_matched(self, input, topic_name, ws_channel_id, sql_ws_client_id, security_id, endpoint_id):
        pubsub = self.server.worker_store.pubsub

        if ws_channel_id and (not sql_ws_client_id):
            raise BadRequest(self.cid, 'sql_ws_client_id must not be empty if ws_channel_id is given on input')

        # Confirm if this client may subscribe at all to the topic it chose
        kwargs = {'security_id':security_id} if security_id else {'ws_channel_id':ws_channel_id}
        pattern_matched = pubsub.is_allowed_sub_topic(topic_name, **kwargs)

        # Not allowed - raise an exception then
        if not pattern_matched:
            raise Forbidden(self.cid)

        # Alright, we can proceed
        else:
            return pattern_matched

# ################################################################################################################################

    def handle(self):

        input = self.request.input
        topic_name = self.request.input.topic_name
        pubsub = self.server.worker_store.pubsub
        ws_channel_id = input.ws_channel_id or None
        sql_ws_client_id = input.sql_ws_client_id or None
        security_id = input.security_id or None

        if security_id:
            endpoint_id = pubsub.get_endpoint_id_by_sec_id(security_id)
        elif ws_channel_id:
            endpoint_id = pubsub.get_endpoint_id_by_ws_channel_id(ws_channel_id)
        else:
            raise NotImplementedError('To be implemented')

        pattern_matched = self.get_pattern_matched(input, topic_name, ws_channel_id, sql_ws_client_id, security_id, endpoint_id)

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

        cluster_id = self.server.cluster_id

        with self.lock('zato.pubsub.subscribe.%s.%s' % (topic_name, endpoint_id)):

            with closing(self.odb.session()) as session:

                # Non-WebSocket clients cannot subscribe to the same topic multiple times
                if not ws_channel_id:
                    if has_subscription(session, cluster_id, topic.id, endpoint_id):
                        raise PubSubSubscriptionExists(self.cid, 'Subscription to topic `{}` already exists'.format(topic.name))

                now = utcnow_as_ms()
                sub_key = new_sub_key()

                # If we subscribe a WSX client, we need to create its accompanying SQL models
                if ws_channel_id:

                    # This object persists across multiple WSX connections
                    ws_sub = add_wsx_subscription(session, cluster_id, is_internal, sub_key, input.ext_client_id, ws_channel_id)

                    # This object will be transient - dropped each time a WSX disconnects
                    self.pubsub.add_ws_client_pubsub_keys(session, sql_ws_client_id, sub_key,
                        input.ws_channel_name, input.ws_pub_client_id)

                    # Let the WebSocket connection object know that it should handle this particular sub_key
                    input.web_socket.pubsub_tool.add_sub_key(sub_key)

                else:
                    ws_sub = None

                # Create a new subscription object
                ps_sub = add_subscription(session, cluster_id, PUBSUB.QUEUE_ACTIVE_STATUS.FULLY_ENABLED.id, False, now,
                    pattern_matched, sub_key, has_gd, topic.id, endpoint_id, delivery_method, delivery_data_format,
                    deliver_to, deliver_by, delivery_group_size, ws_channel_id, ws_sub)

                # Flush the session because we need the subscription's ID below in INSERT from SELECT
                session.flush()

                # Move all available messages to that subscriber's queue
                total_moved = move_messages_to_sub_queue(session, cluster_id, topic.id, endpoint_id, ps_sub.id, now)

                # Commit all changes
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
