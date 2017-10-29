# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# Zato
from zato.common.broker_message import PUBSUB
from zato.common.odb.model import ChannelWebSocket, PubSubEndpoint, PubSubEndpointTopic, PubSubEndpointQueue, PubSubMessage, \
     PubSubTopic, SecurityBase, Service
from zato.common.odb.query import pubsub_topic, pubsub_topic_list
from zato.server.service import AsIs
from zato.server.service.internal import AdminService, AdminSIO
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################

elem = 'pubsub_topic'
model = PubSubTopic
label = 'a pub/sub topic'
broker_message = PUBSUB
broker_message_prefix = 'TOPIC_'
list_func = pubsub_topic_list
skip_input_params = ['is_internal', 'last_pub_time', 'current_depth']
output_optional_extra = ['current_depth', 'last_pub_time']

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
                item.last_pub_time = item.last_pub_time.isoformat()

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
        output_required = ('id', 'name', 'is_active', 'is_internal', 'max_depth', 'current_depth')
        output_optional = ('last_pub_time',)

    def handle(self):
        with closing(self.odb.session()) as session:
            topic = pubsub_topic(session, self.request.input.cluster_id, self.request.input.id)

        topic.last_pub_time = topic.last_pub_time.isoformat()
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
                session.query(PubSubEndpointQueue).\
                    filter(PubSubEndpointQueue.cluster_id==self.request.input.cluster_id).\
                    filter(PubSubEndpointQueue.topic_id==self.request.input.id).\
                    delete()

                session.commit()

# ################################################################################################################################

class GetPublisherList(AdminService):
    """ Returns all publishers that sent at least one message to a given topic.
    """
    class SimpleIO:
        input_required = ('cluster_id', 'topic_id')
        output_required = ('name', 'is_active', 'is_internal')
        output_optional = ('service_id', 'security_id', 'ws_channel_id', 'last_seen', 'last_pub_time', AsIs('last_msg_id'),
            AsIs('last_correl_id'), 'last_in_reply_to', 'service_name', 'sec_name', 'ws_channel_name')
        output_repeated = True

    def handle(self):
        input = self.request.input
        pubsub = self.server.worker_store.pubsub
        response = []

        with closing(self.odb.session()) as session:

            # Get last pub time for that specific endpoint to this very topic
            last_data = session.query(
                PubSubEndpoint.service_id, PubSubEndpoint.security_id,
                PubSubEndpoint.ws_channel_id, PubSubEndpoint.name,
                PubSubEndpoint.is_active, PubSubEndpoint.is_internal,
                PubSubEndpoint.last_seen, PubSubEndpoint.last_pub_time,
                PubSubEndpointTopic.last_pub_time,
                PubSubEndpointTopic.pub_msg_id.label('last_msg_id'),
                PubSubEndpointTopic.pub_correl_id.label('last_correl_id'),
                PubSubEndpointTopic.in_reply_to.label('last_in_reply_to'),
                Service.name.label('service_name'),
                SecurityBase.name.label('sec_name'),
                ChannelWebSocket.name.label('ws_channel_name'),
                ).\
                outerjoin(Service, Service.id==PubSubEndpoint.service_id).\
                outerjoin(SecurityBase, SecurityBase.id==PubSubEndpoint.security_id).\
                outerjoin(ChannelWebSocket, ChannelWebSocket.id==PubSubEndpoint.ws_channel_id).\
                filter(PubSubEndpointTopic.topic_id==PubSubTopic.id).\
                filter(PubSubEndpointTopic.topic_id==input.topic_id).\
                filter(PubSubEndpointTopic.endpoint_id==PubSubEndpoint.id).\
                filter(PubSubEndpointTopic.cluster_id==self.server.cluster_id).\
                all()

            for item in last_data:
                item.last_seen = item.last_pub_time.isoformat()
                item.last_pub_time = item.last_pub_time.isoformat()
                response.append(item)

        self.response.payload[:] = response

# ################################################################################################################################
