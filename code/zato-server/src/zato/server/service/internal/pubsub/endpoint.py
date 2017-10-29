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
from zato.common.odb.model import PubSubEndpoint, PubSubEndpointTopic, PubSubTopic
from zato.common.odb.query import pubsub_endpoint, pubsub_endpoint_list
from zato.server.service import AsIs
from zato.server.service.internal import AdminService, AdminSIO
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################

elem = 'pubsub_endpoint'
model = PubSubEndpoint
label = 'a pub/sub endpoint'
broker_message = PUBSUB
broker_message_prefix = 'ENDPOINT_'
list_func = pubsub_endpoint_list
skip_input_params = ['is_internal']
output_optional_extra = ['ws_channel_name', 'hook_service_name', 'sec_id', 'sec_type', 'sec_name']

# ################################################################################################################################

def instance_hook(self, input, instance, attrs):
    # SQLite will not accept empty strings, must be None
    instance.last_seen = instance.last_seen or None
    instance.last_pub_time = instance.last_pub_time or None
    instance.last_sub_time = instance.last_sub_time or None
    instance.last_deliv_time = instance.last_deliv_time or None

def broker_message_hook(self, input, instance, attrs, service_type):
    if service_type == 'create_edit':
        with closing(self.odb.session()) as session:
            input.is_internal = pubsub_endpoint(session, input.cluster_id, instance.id).is_internal

# ################################################################################################################################

class GetList(AdminService):
    _filter_by = PubSubEndpoint.name,
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
        output_required = ('id', 'name', 'is_active', 'is_internal', 'role')
        output_optional = ('tags', 'topic_patterns', 'pub_tag_patterns', 'message_tag_patterns',
            'security_id', 'ws_channel_id', 'hook_service_id', 'sec_type', 'sec_name', 'ws_channel_name', 'hook_service_name')

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload = pubsub_endpoint(session, self.request.input.cluster_id, self.request.input.id)

# ################################################################################################################################

class GetTopicList(AdminService):
    """ Returns all topics to which a given endpoint published at least once.
    """
    class SimpleIO:
        input_required = ('cluster_id', 'endpoint_id')
        output_required = ('topic_id', 'name', 'is_active', 'is_internal', 'max_depth')
        output_optional = ('last_pub_time', AsIs('last_msg_id'), AsIs('last_correl_id'), 'last_in_reply_to')
        output_repeated = True

    def handle(self):
        input = self.request.input
        pubsub = self.server.worker_store.pubsub
        response = []

        with closing(self.odb.session()) as session:

            # Get last pub time for that specific endpoint to this very topic
            last_data = session.query(
                PubSubTopic.id.label('topic_id'),
                PubSubTopic.name, PubSubTopic.is_active,
                PubSubTopic.is_internal, PubSubTopic.name,
                PubSubTopic.max_depth,
                PubSubEndpointTopic.last_pub_time,
                PubSubEndpointTopic.pub_msg_id.label('last_msg_id'),
                PubSubEndpointTopic.pub_correl_id.label('last_correl_id'),
                PubSubEndpointTopic.in_reply_to.label('last_in_reply_to'),
                ).\
                filter(PubSubEndpointTopic.topic_id==PubSubTopic.id).\
                filter(PubSubEndpointTopic.endpoint_id==input.endpoint_id).\
                filter(PubSubEndpointTopic.cluster_id==self.server.cluster_id).\
                all()

            for item in last_data:
                item.last_pub_time = item.last_pub_time.isoformat()
                response.append(item)

        self.response.payload[:] = response

# ################################################################################################################################
