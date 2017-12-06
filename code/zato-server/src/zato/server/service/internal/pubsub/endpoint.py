# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# SQLAlchemy

# Zato
from zato.common import PUBSUB as COMMON_PUBSUB
from zato.common.broker_message import PUBSUB
from zato.common.exception import BadRequest, Conflict
from zato.common.odb.model import PubSubEndpoint, PubSubEndpointEnqueuedMessage, PubSubEndpointTopic, PubSubMessage, \
     PubSubSubscription, PubSubTopic
from zato.common.odb.query import count, pubsub_endpoint, pubsub_endpoint_list, pubsub_endpoint_queue, \
     pubsub_endpoint_queue_list, pubsub_endpoint_queue_list_by_sub_keys, pubsub_messages_for_queue
from zato.common.odb.query_ps_endpoint import pubsub_endpoint_summary, pubsub_endpoint_summary_list
from zato.common.time_util import datetime_from_ms
from zato.server.service import AsIs, Int, List
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################

elem = 'pubsub_endpoint'
model = PubSubEndpoint
label = 'a pub/sub endpoint'
broker_message = PUBSUB
broker_message_prefix = 'ENDPOINT_'
list_func = pubsub_endpoint_list
skip_input_params = ['sub_key', 'is_sub_allowed']
output_optional_extra = ['ws_channel_name', 'sec_id', 'sec_type', 'sec_name', 'sub_key']

# ################################################################################################################################

def instance_hook(self, input, instance, attrs):

    if attrs.is_delete:
        return

    # Don't use empty string with integer attributes, set them to None (NULL) instead
    if instance.service_id == '':
        instance.service_id = None

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
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'name', 'role', 'is_active', 'is_internal', 'endpoint_type')
        input_optional = ('topic_patterns', 'security_id', 'service_id', 'ws_channel_id')
        output_required = (AsIs('id'), 'name')
        request_elem = 'zato_pubsub_endpoint_create_request'
        response_elem = 'zato_pubsub_endpoint_create_response'

    def handle(self):
        input = self.request.input

        with closing(self.odb.session()) as session:

            existing_one = session.query(PubSubEndpoint.id).\
                filter(PubSubEndpoint.cluster_id==input.cluster_id).\
                filter(PubSubEndpoint.name==input.name).\
                first()

            if existing_one:
                raise Conflict(self.cid, 'Endpoint `{}` already exists'.format(input.name))

            endpoint = PubSubEndpoint()
            endpoint.cluster_id = input.cluster_id
            endpoint.name = input.name
            endpoint.is_active = input.is_active
            endpoint.is_internal = input.is_internal
            endpoint.endpoint_type = input.endpoint_type
            endpoint.role = input.role
            endpoint.topic_patterns = input.topic_patterns
            endpoint.security_id = input.security_id
            endpoint.service_id = input.service_id
            endpoint.ws_channel_id = input.ws_channel_id

            session.add(endpoint)
            session.commit()

            input.action = PUBSUB.ENDPOINT_CREATE.value
            input.id = endpoint.id
            self.broker_client.publish(input)

            self.response.payload.id = endpoint.id
            self.response.payload.name = self.request.input.name

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
            'security_id', 'ws_channel_id', 'sec_type', 'sec_name', 'ws_channel_name', 'sub_key')

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload = pubsub_endpoint(session, self.request.input.cluster_id, self.request.input.id)

# ################################################################################################################################

class GetTopicList(AdminService):
    """ Returns all topics to which a given endpoint published at least once.
    """
    class SimpleIO:
        input_required = ('cluster_id', 'endpoint_id')
        output_required = ('topic_id', 'name', 'is_active', 'is_internal', 'max_depth_gd', 'max_depth_non_gd')
        output_optional = ('last_pub_time', AsIs('last_msg_id'), AsIs('last_correl_id'), 'last_in_reply_to',
            AsIs('ext_client_id'))
        output_repeated = True

    def handle(self):
        input = self.request.input
        response = []

        with closing(self.odb.session()) as session:

            # Get last pub time for that specific endpoint to this very topic
            last_data = session.query(
                PubSubTopic.id.label('topic_id'),
                PubSubTopic.name, PubSubTopic.is_active,
                PubSubTopic.is_internal, PubSubTopic.name,
                PubSubTopic.max_depth_gd,
                PubSubTopic.max_depth_non_gd,
                PubSubEndpointTopic.last_pub_time,
                PubSubEndpointTopic.pub_msg_id.label('last_msg_id'),
                PubSubEndpointTopic.pub_correl_id.label('last_correl_id'),
                PubSubEndpointTopic.in_reply_to.label('last_in_reply_to'),
                PubSubEndpointTopic.ext_client_id,
                ).\
                filter(PubSubEndpointTopic.topic_id==PubSubTopic.id).\
                filter(PubSubEndpointTopic.endpoint_id==input.endpoint_id).\
                filter(PubSubEndpointTopic.cluster_id==self.request.input.cluster_id).\
                all()

            for item in last_data:
                item.last_pub_time = datetime_from_ms(item.last_pub_time)
                response.append(item)

        self.response.payload[:] = response

# ################################################################################################################################

class GetEndpointQueueList(AdminService):
    """ Returns all queues to which a given endpoint is subscribed.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'endpoint_id')
        output_required = ('sub_id', 'topic_id', 'topic_name', 'name', 'active_status', 'is_internal',
            'is_staging_enabled', 'creation_time', 'sub_key', 'has_gd', 'delivery_method',
            'delivery_data_format', 'endpoint_name', Int('total_depth'), Int('current_depth'), Int('staging_depth'))
        output_optional = ('delivery_endpoint', 'last_interaction_time', 'last_interaction_type', 'last_interaction_details',
            AsIs('ws_ext_client_id'))
        output_repeated = True

    def handle(self):
        response = []

        with closing(self.odb.session()) as session:

            queue_list = pubsub_endpoint_queue_list(session, self.request.input.cluster_id, self.request.input.endpoint_id).\
                all()

            for item in queue_list:

                total_q = session.query(PubSubEndpointEnqueuedMessage.id).\
                    filter(PubSubEndpointEnqueuedMessage.cluster_id==self.request.input.cluster_id).\
                    filter(PubSubEndpointEnqueuedMessage.subscription_id==item.sub_id)

                current_q = session.query(PubSubEndpointEnqueuedMessage.id).\
                    filter(PubSubEndpointEnqueuedMessage.cluster_id==self.request.input.cluster_id).\
                    filter(PubSubEndpointEnqueuedMessage.subscription_id==item.sub_id).\
                    filter(PubSubEndpointEnqueuedMessage.is_in_staging != True)

                staging_q = session.query(PubSubEndpointEnqueuedMessage.id).\
                    filter(PubSubEndpointEnqueuedMessage.cluster_id==self.request.input.cluster_id).\
                    filter(PubSubEndpointEnqueuedMessage.subscription_id==item.sub_id).\
                    filter(PubSubEndpointEnqueuedMessage.is_in_staging == True)

                total_depth = count(session, total_q)
                current_depth = count(session, current_q)
                staging_depth = count(session, staging_q)

                item.total_depth = total_depth
                item.current_depth = current_depth
                item.staging_depth = staging_depth

                item.creation_time = datetime_from_ms(item.creation_time)

                if item.last_interaction_time:
                    item.last_interaction_time = datetime_from_ms(item.last_interaction_time)
                response.append(item)

        self.response.payload[:] = response

# ################################################################################################################################

class UpdateEndpointQueue(AdminService):
    """ Modifies selected subscription queue.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'id', 'sub_key', 'active_status')
        input_optional = ('is_staging_enabled', 'has_gd')
        output_required = ('id', 'name')

    def handle(self):

        with closing(self.odb.session()) as session:
            item = session.query(PubSubSubscription).\
                filter(PubSubSubscription.id==self.request.input.id).\
                filter(PubSubSubscription.cluster_id==self.request.input.cluster_id).\
                one()

            item.sub_key = self.request.input.sub_key
            item.active_status = self.request.input.active_status
            item.is_staging_enabled = self.request.input.is_staging_enabled
            item.has_gd = self.request.input.has_gd

            session.add(item)
            session.commit()

            self.response.payload.id = self.request.input.id
            self.response.payload.name = item.topic.name

# ################################################################################################################################

class GetEndpointQueue(AdminService):
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'id')
        output_required = ('sub_id', 'topic_id', 'topic_name', 'name', 'active_status', 'is_internal',
            'is_staging_enabled', 'creation_time', 'sub_key', 'has_gd', 'delivery_method',
            'delivery_data_format', 'endpoint_id', 'endpoint_name')
        output_optional = ('delivery_endpoint', 'last_interaction_time', 'last_interaction_type', 'last_interaction_details',
            Int('total_depth'), Int('current_depth'), Int('staging_depth'), AsIs('ws_ext_client_id'))

    def handle(self):
        with closing(self.odb.session()) as session:
            item = pubsub_endpoint_queue(session, self.request.input.cluster_id, self.request.input.id)

            item.creation_time = datetime_from_ms(item.creation_time)
            if item.last_interaction_time:
                item.last_interaction_time = datetime_from_ms(item.last_interaction_time)

            self.response.payload = item

# ################################################################################################################################

class ClearEndpointQueue(AdminService):
    """ Clears messages from the queue given on input.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'id')
        input_optional = ('queue_type',)

    def handle(self, _queue_type=COMMON_PUBSUB.QUEUE_TYPE):

        # Make sure the (optional) queue type is one of allowed values
        queue_type = self.request.input.queue_type

        if queue_type:
            if queue_type not in _queue_type:
                raise BadRequest(self.cid, 'Invalid queue_type:`{}`'.format(queue_type))
            else:
                if queue_type == _queue_type.CURRENT:
                    is_in_staging = False
                elif queue_type == _queue_type.STAGING:
                    is_in_staging = True
        else:
            is_in_staging = None

        # Remove all references to the queue given on input
        with closing(self.odb.session()) as session:
            q = session.query(PubSubEndpointEnqueuedMessage).\
                filter(PubSubEndpointEnqueuedMessage.cluster_id==self.request.input.cluster_id).\
                filter(PubSubEndpointEnqueuedMessage.subscription_id==self.request.input.id)

            if is_in_staging is not None:
                q = q.filter(PubSubEndpointEnqueuedMessage.is_in_staging.is_(is_in_staging))
            q.delete()

            session.commit()

# ################################################################################################################################

class DeleteEndpointQueue(AdminService):
    """ Deletes input message queues for a subscriber based on sub_keys - including all messages
    and their parent subscription object.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id',)
        input_optional = ('sub_key', List('sub_key_list'))

    def handle(self):

        sub_key = self.request.input.sub_key
        sub_key_list = self.request.input.sub_key_list

        if not(sub_key or sub_key_list):
            raise BadRequest(self.cid, 'Exactly one of sub_key or sub_key_list is required')

        if sub_key and sub_key_list:
            raise BadRequest(self.cid, 'Cannot provide both sub_key and sub_key_list on input')

        if sub_key:
            sub_key_list = [sub_key] # Otherwise, we already had sub_key_list on input so 'else' is not needed

        cluster_id = self.request.input.cluster_id
        topic_sub_keys = {}

        with closing(self.odb.session()) as session:

            # First we need a list of topics to which sub_keys were related - required by broker messages.
            for item in pubsub_endpoint_queue_list_by_sub_keys(session, cluster_id, sub_key_list):
                sub_keys = topic_sub_keys.setdefault(item.topic_name, [])
                sub_keys.append(item.sub_key)

            # Remove the subscription object which in turn cascades and removes all dependant objects
            session.query(PubSubSubscription).\
                filter(PubSubSubscription.cluster_id==self.request.input.cluster_id).\
                filter(PubSubSubscription.sub_key.in_(sub_key_list)).\
                delete(synchronize_session=False)
            session.expire_all()

            session.commit()

        # Notify workers that this subscription needs to be deleted
        self.broker_client.publish({
            'topic_sub_keys': topic_sub_keys,
            'action': PUBSUB.SUBSCRIPTION_DELETE.value,
        })

# ################################################################################################################################

class GetEndpointQueueMessages(AdminService):
    _filter_by = PubSubMessage.data_prefix,

    class SimpleIO(GetListAdminSIO):
        input_required = ('cluster_id', 'sub_id')
        output_required = (AsIs('msg_id'), 'recv_time', 'data_prefix_short')
        output_optional = (Int('delivery_count'), 'last_delivery_time', 'is_in_staging', 'has_gd', 'queue_name', 'endpoint_id')
        output_repeated = True

    def get_data(self, session):
        return self._search(
            pubsub_messages_for_queue, session, self.request.input.cluster_id, self.request.input.sub_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

        for item in self.response.payload.zato_output:
            item.recv_time = datetime_from_ms(item.recv_time)
            item.last_delivery_time = datetime_from_ms(item.last_delivery_time) if item.last_delivery_time else ''

# ################################################################################################################################

class _GetEndpointSummaryBase(AdminService):
    """ Base class for services returning summaries about endpoints
    """
    class SimpleIO:
        input_required = ('cluster_id',)
        output_required = ('id', 'endpoint_name', 'endpoint_type', 'subscription_count', 'is_active', 'is_internal')
        output_optional = ('security_id', 'sec_type', 'sec_name', 'ws_channel_id', 'ws_channel_name',
            'service_id', 'service_name', 'last_seen', 'last_deliv_time', 'role')

# ################################################################################################################################

class GetEndpointSummary(_GetEndpointSummaryBase):
    """ Returns summarized information about a selected endpoint subscribed to topics.
    """
    class SimpleIO(_GetEndpointSummaryBase.SimpleIO):
        input_required = _GetEndpointSummaryBase.SimpleIO.input_required + ('endpoint_id',)
        request_elem = 'zato_pubsub_subscription_get_endpoint_summary_request'
        response_elem = 'zato_pubsub_subscription_get_endpoint_summary_response'

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload = pubsub_endpoint_summary(session, self.server.cluster_id, self.request.input.endpoint_id)

# ################################################################################################################################

class GetEndpointSummaryList(_GetEndpointSummaryBase):
    """ Returns summarized information about all endpoints subscribed to topics.
    """
    _filter_by = PubSubEndpoint.name,

    class SimpleIO(_GetEndpointSummaryBase.SimpleIO, GetListAdminSIO):
        request_elem = 'zato_pubsub_endpoint_get_endpoint_summary_list_request'
        response_elem = 'zato_pubsub_endpoint_get_endpoint_summary_list_response'

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
