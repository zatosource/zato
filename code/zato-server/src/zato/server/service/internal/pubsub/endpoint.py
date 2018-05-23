# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from json import loads

# Zato
from zato.common import PUBSUB as COMMON_PUBSUB
from zato.common.broker_message import PUBSUB
from zato.common.exception import BadRequest, Conflict
from zato.common.odb.model import PubSubEndpoint, PubSubEndpointEnqueuedMessage, PubSubMessage, PubSubSubscription, PubSubTopic
from zato.common.odb.query import count, pubsub_endpoint, pubsub_endpoint_list, pubsub_endpoint_queue, \
     pubsub_endpoint_queue_list_by_sub_keys, pubsub_messages_for_queue, server_by_id
from zato.common.odb.query.pubsub.endpoint import pubsub_endpoint_summary, pubsub_endpoint_summary_list
from zato.common.odb.query.pubsub.subscription import pubsub_subscription_list_by_endpoint_id
from zato.common.util.time_ import datetime_from_ms
from zato.server.service import AsIs, Int, List
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO
from zato.server.service.internal.pubsub import common_sub_data
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

_meta_endpoint_key = COMMON_PUBSUB.REDIS.META_ENDPOINT_PUB_KEY

# ################################################################################################################################

_sub_skip_update = ('id', 'sub_id', 'sub_key', 'cluster_id', 'creation_time', 'current_depth', 'endpoint_id', 'endpoint_type',
    'last_interaction_time', 'staging_depth', 'sql_ws_client_id', 'topic_name', 'total_depth', 'web_socket',
    'out_rest_http_soap_id', 'out_soap_http_soap_id', 'out_http_soap_id')

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
        output_required = ('id', 'name', 'is_active', 'is_internal', 'role', 'endpoint_type')
        output_optional = ('tags', 'topic_patterns', 'pub_tag_patterns', 'message_tag_patterns',
            'security_id', 'ws_channel_id', 'sec_type', 'sec_name', 'ws_channel_name', 'sub_key')

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload = pubsub_endpoint(session, self.request.input.cluster_id, self.request.input.id)

# ################################################################################################################################

class GetTopicList(AdminService):
    """ Returns all topics to which a given endpoint published at least once.
    """

    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'endpoint_id')
        output_required = ('topic_id', 'topic_name', 'pub_time', AsIs('pub_msg_id'), 'pattern_matched', 'has_gd', 'data')
        output_optional = (AsIs('pub_correl_id'), 'in_reply_to', AsIs('ext_client_id'), 'ext_pub_time')
        output_repeated = True

# ################################################################################################################################

    def handle(self):
        out = self.kvdb.conn.get(_meta_endpoint_key % (self.request.input.cluster_id, self.request.input.endpoint_id))
        out = loads(out) if out else []

        for elem in out:
            elem['pub_time'] = datetime_from_ms(elem['pub_time'] * 1000.0)
            if elem['ext_pub_time']:
                elem['ext_pub_time'] = datetime_from_ms(elem['ext_pub_time'] * 1000.0)

        self.response.payload[:] = out

# ################################################################################################################################

class _GetEndpointQueue(AdminService):
    def _add_queue_depths(self, session, item):

        current_depth_gd_q = session.query(PubSubEndpointEnqueuedMessage.id).\
            filter(PubSubEndpointEnqueuedMessage.cluster_id==self.request.input.cluster_id).\
            filter(PubSubEndpointEnqueuedMessage.sub_key==item.sub_key).\
            filter(PubSubEndpointEnqueuedMessage.is_in_staging != True)

        item.current_depth_gd = count(session, current_depth_gd_q)

# ################################################################################################################################

class GetEndpointQueue(_GetEndpointQueue):
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'id')
        output_optional = common_sub_data

    def handle(self):
        with closing(self.odb.session()) as session:
            item = pubsub_endpoint_queue(session, self.request.input.cluster_id, self.request.input.id)

            self._add_queue_depths(session, item)
            item.creation_time = datetime_from_ms(item.creation_time)
            if item.last_interaction_time:
                item.last_interaction_time = datetime_from_ms(item.last_interaction_time)

            self.response.payload = item

# ################################################################################################################################

class GetEndpointQueueList(_GetEndpointQueue):
    """ Returns all queues to which a given endpoint is subscribed.
    """
    _filter_by = PubSubTopic.name,

    class SimpleIO(GetListAdminSIO):
        input_required = ('cluster_id', 'endpoint_id')
        output_optional = common_sub_data
        output_repeated = True
        request_elem = 'zato_pubsub_endpoint_get_endpoint_queue_list_request'
        response_elem = 'zato_pubsub_endpoint_get_endpoint_queue_list_response'

    def get_data(self, session):
        return self._search(pubsub_subscription_list_by_endpoint_id, session, self.request.input.cluster_id,
            self.request.input.endpoint_id, False)

    def handle(self):
        response = []

        with closing(self.odb.session()) as session:

            for item in self.get_data(session):

                self._add_queue_depths(session, item)
                item.creation_time = datetime_from_ms(item.creation_time * 1000.0)
                response.append(item)

        self.response.payload[:] = response

# ################################################################################################################################

class UpdateEndpointQueue(AdminService):
    """ Modifies selected subscription queue.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'id', 'sub_key', 'active_status')
        input_optional = common_sub_data
        output_required = ('id', 'name')

    def handle(self):

        # REST and SOAP outconn IDs have different input names but they both map
        # to the same SQL-level attribute. This means that at most one of them may be
        # provided on input. It's an error to provide both.
        out_rest_http_soap_id = self.request.input.get('out_rest_http_soap_id')
        out_soap_http_soap_id = self.request.input.get('out_soap_http_soap_id')

        if out_rest_http_soap_id and out_soap_http_soap_id:
            raise BadRequest(self.cid, 'Cannot provide both out_rest_http_soap_id and out_soap_http_soap_id on input')

        # We know we don't have both out_rest_http_soap_id and out_soap_http_soap_id on input
        # but we still need to find out if we have any at all.
        if out_rest_http_soap_id:
            out_http_soap_id = out_rest_http_soap_id
        elif out_soap_http_soap_id:
            out_http_soap_id = out_soap_http_soap_id
        else:
            out_http_soap_id = None

        with closing(self.odb.session()) as session:
            item = session.query(PubSubSubscription).\
                filter(PubSubSubscription.id==self.request.input.id).\
                filter(PubSubSubscription.cluster_id==self.request.input.cluster_id).\
                one()

            old_delivery_server_id = item.server_id
            new_delivery_server_id = self.request.input.server_id
            new_delivery_server_name = server_by_id(session, self.server.cluster_id, new_delivery_server_id).name

            for key, value in sorted(self.request.input.items()):
                if key not in _sub_skip_update:
                    setattr(item, key, value)

            # This one we set manually based on logic at the top of the method
            item.out_http_soap_id = out_http_soap_id

            session.add(item)
            session.commit()

            self.response.payload.id = self.request.input.id
            self.response.payload.name = item.topic.name

            # We change the delivery server in background - note how we send name, not ID, on input.
            # This is because our invocation target will want to use self.servers[server_name].invoke(...)
            if old_delivery_server_id != new_delivery_server_id:
                self.broker_client.publish({
                    'sub_key': self.request.input.sub_key,
                    'endpoint_type': item.endpoint.endpoint_type,
                    'old_delivery_server_id': old_delivery_server_id,
                    'new_delivery_server_name': new_delivery_server_name,
                    'action': PUBSUB.DELIVERY_SERVER_CHANGE.value,
                })

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

class GetEndpointQueueMessagesGD(AdminService):
    """ Returns a list of GD messages queued up for input subscription.
    """
    _filter_by = PubSubMessage.data_prefix,

    class SimpleIO(GetListAdminSIO):
        input_required = ('cluster_id', 'sub_id', 'has_gd')
        output_required = (AsIs('msg_id'), 'recv_time', 'data_prefix_short')
        output_optional = (Int('delivery_count'), 'last_delivery_time', 'is_in_staging', 'queue_name', 'endpoint_id')
        output_repeated = True

    def get_data(self, session):
        sub = self.pubsub.get_subscription_by_id(self.request.input.sub_id)
        return self._search(
            pubsub_messages_for_queue, session, self.request.input.cluster_id, sub.sub_key, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

        for item in self.response.payload.zato_output:
            item.recv_time = datetime_from_ms(item.recv_time * 1000.0)

# ################################################################################################################################

class GetEndpointQueueMessagesNonGD(AdminService):
    """ Returns a list of non-GD messages queued up for input subscription.
    """

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
            item = pubsub_endpoint_summary(session, self.server.cluster_id, self.request.input.endpoint_id)

            if item.last_seen:
                item.last_seen = datetime_from_ms(item.last_seen)

            if item.last_deliv_time:
                item.last_deliv_time = datetime_from_ms(item.last_deliv_time)

            self.response.payload = item

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

class GetTopicSubList(AdminService):
    """ Returns a list of topics to which a given endpoint has access for subscription,
    including both endpoints that it's already subscribed to or all the remaining ones
    the endpoint may be possible subscribe to.
    """
    class SimpleIO(AdminSIO):
        input_required = ('endpoint_id', 'cluster_id')
        input_optional = ('topic_filter_by',)
        output_optional = (List('topic_sub_list'),)

    def handle(self):

        # Local shortcuts
        endpoint_id = self.request.input.endpoint_id
        filter_by = self.request.input.topic_filter_by

        # Response to produce
        out = []

        # For all topics this endpoint may in theory subscribe to ..
        for topic in self.pubsub.get_sub_topics_for_endpoint(endpoint_id):

            if filter_by and (filter_by not in topic.name):
                continue

            # .. add each of them, along with information if the endpoint is already subscribed.
            out.append({
                'cluster_id': self.request.input.cluster_id,
                'endpoint_id': endpoint_id,
                'topic_id': topic.id,
                'topic_name': topic.name,
                'is_subscribed': self.pubsub.is_subscribed_to(endpoint_id, topic.name)
            })

        self.response.payload.topic_sub_list = out

# ################################################################################################################################
