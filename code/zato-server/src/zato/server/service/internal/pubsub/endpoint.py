# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Python 2/3 compatibility
from six import add_metaclass

# stdlib
from contextlib import closing
from json import loads

# Zato
from zato.common import PUBSUB as COMMON_PUBSUB
from zato.common.broker_message import PUBSUB
from zato.common.exception import BadRequest, Conflict
from zato.common.odb.model import PubSubEndpoint, PubSubEndpointEnqueuedMessage, PubSubMessage, PubSubSubscription, PubSubTopic
from zato.common.odb.query import count, pubsub_endpoint, pubsub_endpoint_list, pubsub_endpoint_queue, \
     pubsub_messages_for_queue, server_by_id
from zato.common.odb.query.pubsub.endpoint import pubsub_endpoint_summary, pubsub_endpoint_summary_list
from zato.common.odb.query.pubsub.subscription import pubsub_subscription_list_by_endpoint_id
from zato.common.pubsub import msg_pub_attrs
from zato.common.util.pubsub import get_topic_sub_keys_from_sub_keys, make_short_msg_copy_from_msg
from zato.common.util.time_ import datetime_from_ms
from zato.server.service import AsIs, Bool, Int, List
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO
from zato.server.service.internal.pubsub import common_sub_data
from zato.server.service.internal.pubsub.search import NonGDSearchService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################

elem = 'pubsub_endpoint'
model = PubSubEndpoint
label = 'a pub/sub endpoint'
get_list_docs = 'pub/sub endpoints'
broker_message = PUBSUB
broker_message_prefix = 'ENDPOINT_'
list_func = pubsub_endpoint_list
skip_input_params = ['sub_key', 'is_sub_allowed']
output_optional_extra = ['ws_channel_name', 'sec_id', 'sec_type', 'sec_name', 'sub_key']

# ################################################################################################################################

msg_pub_attrs_sio = []

for name in msg_pub_attrs:
    if name in ('topic', 'is_in_sub_queue', 'position_in_group', 'group_id'):
        continue
    elif name.endswith('_id'):
        msg_pub_attrs_sio.append(AsIs(name))
    elif name in ('position_in_group', 'priority', 'size', 'delivery_count'):
        msg_pub_attrs_sio.append(Int(name))
    elif name.startswith(('has_', 'is_')):
        msg_pub_attrs_sio.append(Bool(name))
    else:
        msg_pub_attrs_sio.append(name)

# ################################################################################################################################

_meta_endpoint_key = COMMON_PUBSUB.REDIS.META_ENDPOINT_PUB_KEY

# ################################################################################################################################

_sub_skip_update = ('id', 'sub_id', 'sub_key', 'cluster_id', 'creation_time', 'current_depth', 'endpoint_id', 'endpoint_type',
    'last_interaction_time', 'staging_depth', 'sql_ws_client_id', 'topic_name', 'total_depth', 'web_socket',
    'out_rest_http_soap_id', 'out_soap_http_soap_id', 'out_http_soap_id')

# ################################################################################################################################

class _GetEndpointQueueMessagesSIO(GetListAdminSIO):
    input_required = ('cluster_id',)
    input_optional = GetListAdminSIO.input_optional + ('sub_id', 'sub_key')
    output_required = (AsIs('msg_id'), 'recv_time')
    output_optional = ('data_prefix_short', Int('delivery_count'), 'last_delivery_time', 'is_in_staging', 'queue_name',
        'endpoint_id', 'sub_key', 'published_by_id', 'published_by_name', 'server_name', 'server_pid')
    output_repeated = True

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

@add_metaclass(GetListMeta)
class GetList(AdminService):
    _filter_by = PubSubEndpoint.name,

# ################################################################################################################################

class Create(AdminService):
    """ Creates a new pub/sub endpoint.
    """
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

@add_metaclass(CreateEditMeta)
class Edit(AdminService):
    pass

# ################################################################################################################################

@add_metaclass(DeleteMeta)
class Delete(AdminService):
    pass

# ################################################################################################################################

class Get(AdminService):
    """ Returns details of a pub/sub endpoint.
    """
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
        output_required = ('topic_id', 'topic_name', 'pub_time', AsIs('pub_msg_id'), 'pub_pattern_matched', 'has_gd', 'data')
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

class GetEndpointQueueNonGDDepth(AdminService):
    """ Returns current depth of non-GD messages for input sub_key which must have a delivery task on current server.
    """
    class SimpleIO(AdminSIO):
        input_required = ('sub_key',)
        output_optional = (Int('current_depth_non_gd'),)

    def handle(self):
        pubsub_tool = self.pubsub.get_pubsub_tool_by_sub_key(self.request.input.sub_key)
        _, non_gd_depth = pubsub_tool.get_queue_depth(self.request.input.sub_key)
        self.response.payload.current_depth_non_gd = non_gd_depth

# ################################################################################################################################

class _GetEndpointQueue(AdminService):
    def _add_queue_depths(self, session, item):

        current_depth_gd_q = session.query(PubSubEndpointEnqueuedMessage.id).\
            filter(PubSubEndpointEnqueuedMessage.cluster_id==self.request.input.cluster_id).\
            filter(PubSubEndpointEnqueuedMessage.sub_key==item.sub_key).\
            filter(PubSubEndpointEnqueuedMessage.is_in_staging != True).\
            filter(PubSubEndpointEnqueuedMessage.delivery_status != COMMON_PUBSUB.DELIVERY_STATUS.DELIVERED)

        # This could be read from the SQL database ..
        item.current_depth_gd = count(session, current_depth_gd_q)

        # .. but non-GD depth needs to be collected from all the servers around. Note that the server may not be known
        # in case the subscriber is a WSX client. In this case, by definition, there will be no non-GD messages for that client.
        sk_server = self.pubsub.get_delivery_server_by_sub_key(item.sub_key)

        if sk_server:

            if sk_server.server_name == self.server.name and sk_server.server_pid == self.server.pid:
                pubsub_tool = self.pubsub.get_pubsub_tool_by_sub_key(item.sub_key)
                _, current_depth_non_gd = pubsub_tool.get_queue_depth(item.sub_key)
            else:
                response = self.servers[sk_server.server_name].invoke(GetEndpointQueueNonGDDepth.get_name(), {
                    'sub_key': item.sub_key,
                }, pid=sk_server.server_pid)
                inner_response = response['response']
                current_depth_non_gd = inner_response['current_depth_non_gd'] if inner_response else 0

        # No delivery server = there cannot be any non-GD messages waiting for that subscriber
        else:
            current_depth_non_gd = 0

        item.current_depth_non_gd = current_depth_non_gd

# ################################################################################################################################

class GetEndpointQueue(_GetEndpointQueue):
    """ Returns information describing an individual endpoint queue.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'id')
        output_optional = common_sub_data

    def handle(self):
        with closing(self.odb.session()) as session:
            item = pubsub_endpoint_queue(session, self.request.input.cluster_id, self.request.input.id)
            item.creation_time = datetime_from_ms(item.creation_time * 1000.0)
            if getattr(item, 'last_interaction_time', None):
                item.last_interaction_time = datetime_from_ms(item.last_interaction_time * 1000.0)
            self.response.payload = item
            self._add_queue_depths(session, self.response.payload)

# ################################################################################################################################

class GetEndpointQueueList(_GetEndpointQueue):
    """ Returns all queues to which a given endpoint is subscribed.
    """
    _filter_by = PubSubTopic.name, PubSubSubscription.sub_key

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

                if item.last_interaction_time:
                    item.last_interaction_time = datetime_from_ms(item.last_interaction_time * 1000.0)

                if item.last_interaction_details:
                    item.last_interaction_details = item.last_interaction_details.decode('utf8')

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

        # WebSockets clients dynamic attach to delivery servers hence the servers cannot be updated by users
        can_update_delivery_server = self.request.input.endpoint_type != COMMON_PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id

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

            if can_update_delivery_server:
                old_delivery_server_id = item.server_id
                new_delivery_server_id = self.request.input.server_id
                new_delivery_server_name = server_by_id(session, self.server.cluster_id, new_delivery_server_id).name

            for key, value in sorted(self.request.input.items()):
                if key not in _sub_skip_update:
                    if value is not None:
                        setattr(item, key, value)

            # This one we set manually based on logic at the top of the method
            item.out_http_soap_id = out_http_soap_id

            session.add(item)
            session.commit()

            self.response.payload.id = self.request.input.id
            self.response.payload.name = item.topic.name

            # Notify all processes, including our own, that this subscription's parameters have changed
            updated_params_msg = item.asdict()
            updated_params_msg['action'] = PUBSUB.SUBSCRIPTION_EDIT.value
            self.broker_client.publish(updated_params_msg)

            # We change the delivery server in background - note how we send name, not ID, on input.
            # This is because our invocation target will want to use self.servers[server_name].invoke(...)
            if can_update_delivery_server:
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
        input_required = ('cluster_id', 'sub_key')
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
                filter(PubSubEndpointEnqueuedMessage.sub_key==self.request.input.sub_key)

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

        with closing(self.odb.session()) as session:

            # First we need a list of topics to which sub_keys were related - required by broker messages.
            topic_sub_keys = get_topic_sub_keys_from_sub_keys(session, cluster_id, sub_key_list)

            # Remove the subscription object which in turn cascades and removes all dependant objects
            session.query(PubSubSubscription).\
                filter(PubSubSubscription.cluster_id==self.request.input.cluster_id).\
                filter(PubSubSubscription.sub_key.in_(sub_key_list)).\
                delete(synchronize_session=False)

            self.logger.info('Deleting subscriptions `%s`', topic_sub_keys)

            session.expire_all()
            session.commit()

        # Notify workers about deleted subscription(s)
        self.broker_client.publish({
            'topic_sub_keys': topic_sub_keys,
            'action': PUBSUB.SUBSCRIPTION_DELETE.value,
        })

# ################################################################################################################################

class _GetMessagesBase(object):
    def _get_sub_by_sub_input(self):
        if self.request.input.get('sub_id'):
            return self.pubsub.get_subscription_by_id(self.request.input.sub_id)
        elif self.request.input.get('sub_key'):
            return self.pubsub.get_subscription_by_sub_key(self.request.input.sub_key)
        else:
            raise Exception('Either sub_id or sub_key must be given on input')

# ################################################################################################################################

class GetEndpointQueueMessagesGD(AdminService, _GetMessagesBase):
    """ Returns a list of GD messages queued up for input subscription.
    """
    _filter_by = PubSubMessage.data_prefix,
    SimpleIO = _GetEndpointQueueMessagesSIO

    def get_data(self, session):
        sub = self._get_sub_by_sub_input()

        return self._search(
            pubsub_messages_for_queue, session, self.request.input.cluster_id, sub.sub_key, True, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

        for item in self.response.payload.zato_output:
            item.recv_time = datetime_from_ms(item.recv_time * 1000.0)
            item.published_by_name = self.pubsub.get_endpoint_by_id(item.published_by_id).name

# ################################################################################################################################

class GetServerEndpointQueueMessagesNonGD(AdminService):
    """ Returns a list of non-GD messages for an input queue by its sub_key which must exist on current server,
    i.e. current server must be the delivery server for this sub_key.
    """
    SimpleIO = _GetEndpointQueueMessagesSIO

    def handle(self):
        ps_tool = self.pubsub.get_pubsub_tool_by_sub_key(self.request.input.sub_key)
        messages = ps_tool.get_messages(self.request.input.sub_key, False)

        data_prefix_len = self.pubsub.data_prefix_len
        data_prefix_short_len = self.pubsub.data_prefix_short_len

        self.response.payload[:] = [
            make_short_msg_copy_from_msg(elem, data_prefix_len, data_prefix_short_len) for elem in messages]

        for elem in self.response.payload:
            elem['recv_time'] = datetime_from_ms(elem['recv_time'] * 1000.0)
            elem['published_by_name'] = self.pubsub.get_endpoint_by_id(elem['published_by_id']).name

# ################################################################################################################################

class GetEndpointQueueMessagesNonGD(NonGDSearchService, _GetMessagesBase):
    """ Returns a list of non-GD messages for an input queue by its sub_key.
    """
    SimpleIO = _GetEndpointQueueMessagesSIO

    def handle(self):
        sub = self._get_sub_by_sub_input()
        sk_server = self.pubsub.get_delivery_server_by_sub_key(sub.sub_key)

        if sk_server:
            response = self.servers[sk_server.server_name].invoke(GetServerEndpointQueueMessagesNonGD.get_name(), {
                'cluster_id': self.request.input.cluster_id,
                'sub_key': sub.sub_key,
            }, pid=sk_server.server_pid)

            if response:
                self.response.payload[:] = reversed(response['response'])

# ################################################################################################################################

class _GetEndpointSummaryBase(AdminService):
    """ Base class for services returning summaries about endpoints
    """
    class SimpleIO:
        input_required = ('cluster_id',)
        input_optional = ('topic_id',)
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
        result = self._search(pubsub_endpoint_summary_list, session, self.request.input.cluster_id,
            self.request.input.topic_id, False)

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

class GetServerDeliveryMessages(AdminService):
    """ Returns a list of messages to be delivered to input endpoint. The messages must exist on current server.
    """
    class SimpleIO(AdminSIO):
        input_required = ('sub_key',)
        output_optional = ('msg_list',)

    def handle(self):
        ps_tool = self.pubsub.get_pubsub_tool_by_sub_key(self.request.input.sub_key)
        self.response.payload.msg_list = ps_tool.pull_messages(self.request.input.sub_key)

# ################################################################################################################################

class GetDeliveryMessages(AdminService, _GetMessagesBase):
    """ Returns a list of messages to be delivered to input endpoint.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'sub_key')
        output_optional = msg_pub_attrs_sio
        output_repeated = True
        skip_empty_keys = True
        default_value = None

    def handle(self):
        sub = self._get_sub_by_sub_input()
        sk_server = self.pubsub.get_delivery_server_by_sub_key(sub.sub_key)

        if sk_server:
            response = self.servers[sk_server.server_name].invoke(GetServerDeliveryMessages.get_name(), {
                'sub_key': sub.sub_key,
            }, pid=sk_server.server_pid)

            if response:
                self.response.payload[:] = reversed(response['response']['msg_list'])
        else:
            self.logger.info('Could not find delivery server for sub_key:`%s`', sub.sub_key)

# ################################################################################################################################
