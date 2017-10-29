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
     PubSubTopic, SecurityBase, Service as ODBService
from zato.common.odb.query import pubsub_messages_for_topic, pubsub_publishers_for_topic, pubsub_topic, pubsub_topic_list
from zato.server.service import AsIs
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
        output_required = ('name', 'is_active', 'is_internal', 'pattern_matched')
        output_optional = ('service_id', 'security_id', 'ws_channel_id', 'last_seen', 'last_pub_time', AsIs('last_msg_id'),
            AsIs('last_correl_id'), 'last_in_reply_to', 'service_name', 'sec_name', 'ws_channel_name')
        output_repeated = True

    def handle(self):
        response = []

        with closing(self.odb.session()) as session:

            # Get last pub time for that specific endpoint to this very topic
            last_data = pubsub_publishers_for_topic(session, self.server.cluster_id, self.request.input.topic_id).all()

            for item in last_data:
                item.last_seen = item.last_pub_time.isoformat()
                item.last_pub_time = item.last_pub_time.isoformat()
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
        return self._search(pubsub_messages_for_topic, session, self.server.cluster_id, self.request.input.topic_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

        for item in self.response.payload.zato_output:
            item.pub_time = item.pub_time.isoformat()
            item.ext_pub_time = item.ext_pub_time.isoformat() if item.ext_pub_time else ''

# ################################################################################################################################
