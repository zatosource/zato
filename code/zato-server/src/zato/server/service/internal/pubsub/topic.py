# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# Zato
from zato.common.broker_message import PUBSUB as BROKER_MSG_PUBSUB
from zato.common.odb.model import PubSubEndpointEnqueuedMessage, PubSubMessage, PubSubTopic
from zato.common.odb.query import pubsub_messages_for_topic, pubsub_publishers_for_topic, pubsub_topic, pubsub_topic_list
from zato.common.odb.query_ps_topic import get_topics_by_sub_keys
from zato.common.time_util import datetime_from_ms
from zato.common.util import ensure_pubsub_hook_is_valid
from zato.server.service import AsIs, Dict, List
from zato.server.service.internal import AdminService, GetListAdminSIO
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################

elem = 'pubsub_topic'
model = PubSubTopic
label = 'a pub/sub topic'
broker_message = BROKER_MSG_PUBSUB
broker_message_prefix = 'TOPIC_'
list_func = pubsub_topic_list
skip_input_params = ['current_depth_gd', 'last_pub_time', 'is_internal']
output_optional_extra = ['current_depth_gd', 'last_pub_time', 'is_internal', 'hook_service_name']

# ################################################################################################################################

sub_broker_attrs = ('active_status', 'active_status', 'cluster_id', 'creation_time', 'endpoint_id', 'has_gd', 'id',
    'is_durable', 'is_internal', 'name', 'out_amqp_id', 'out_http_soap_id', 'sub_key', 'topic_id', 'ws_channel_id',
    'ws_sub_id', 'delivery_group_size')

# ################################################################################################################################

def broker_message_hook(self, input, instance, attrs, service_type):
    if service_type == 'create_edit':
        with closing(self.odb.session()) as session:
            topic = pubsub_topic(session, input.cluster_id, instance.id)
            input.is_internal = topic.is_internal
            input.hook_service_name = topic.hook_service_name

# ################################################################################################################################

def response_hook(service, input, instance, attrs, service_type):
    if service_type == 'get_list':
        for item in service.response.payload:
            if item.last_pub_time:
                item.last_pub_time = datetime_from_ms(item.last_pub_time)

# ################################################################################################################################

instance_hook = ensure_pubsub_hook_is_valid

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
        output_required = ('id', 'name', 'is_active', 'is_internal', 'has_gd', 'max_depth_gd', 'max_depth_non_gd',
            'current_depth_gd')
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
                topic.current_depth_gd = 0

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

class GetInRAMMessageList(AdminService):
    """ Returns all in-RAM messages matching input sub_keys. Messages, if there were any, are deleted from RAM.
    """
    class SimpleIO:
        input_required = (List('sub_key_list'),)
        output_optional = (Dict('messages'),)

    def handle(self):

        out = {}
        topic_sub_keys = {}

        with closing(self.odb.session()) as session:
            for topic_id, sub_key in get_topics_by_sub_keys(session, self.server.cluster_id, self.request.input.sub_key_list):
                sub_keys = topic_sub_keys.setdefault(topic_id, [])
                sub_keys.append(sub_key)

        for topic_id, sub_keys in topic_sub_keys.items():

            # This is a dictionary of sub_key -> msg_id -> message data ..
            data = self.pubsub.in_ram_backlog.retrieve_messages_by_sub_keys(topic_id, sub_keys)

            # .. which is why we can extend out directly - sub_keys are always unique
            out.update(data)

        self.response.payload.messages = out

# ################################################################################################################################
