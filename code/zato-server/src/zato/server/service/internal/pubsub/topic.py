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
from zato.common.odb.model import PubSubEndpointQueue, PubSubMessage, PubSubTopic
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
