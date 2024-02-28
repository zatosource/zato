# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from copy import deepcopy
from json import loads

# SQLAlchemy
from sqlalchemy import delete

# Zato
from zato.common.api import PUBSUB as COMMON_PUBSUB
from zato.common.broker_message import PUBSUB
from zato.common.exception import BadRequest, Conflict
from zato.common.odb.model import PubSubEndpoint, PubSubEndpointEnqueuedMessage, PubSubMessage, PubSubSubscription, PubSubTopic
from zato.common.odb.query import count, pubsub_endpoint, pubsub_endpoint_list, pubsub_endpoint_queue, \
     pubsub_messages_for_queue, pubsub_messages_for_queue_raw, server_by_id
from zato.common.odb.query.pubsub.endpoint import pubsub_endpoint_summary, pubsub_endpoint_summary_list
from zato.common.odb.query.pubsub.subscription import pubsub_subscription_list_by_endpoint_id
from zato.common.pubsub import ensure_subs_exist, msg_pub_attrs
from zato.common.simpleio_ import drop_sio_elems
from zato.common.typing_ import cast_
from zato.common.util.pubsub import get_endpoint_metadata, get_topic_sub_keys_from_sub_keys, make_short_msg_copy_from_msg
from zato.common.util.time_ import datetime_from_ms
from zato.server.service import AsIs, Bool, Int, List
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO
from zato.server.service.internal.pubsub import common_sub_data
from zato.server.service.internal.pubsub.search import NonGDSearchService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# Python 2/3 compatibility
from zato.common.py23_.past.builtins import unicode
from six import add_metaclass

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from sqlalchemy import Column
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anylist, intnone, strdict
    from zato.server.connection.server.rpc.invoker import PerPIDResponse, ServerInvocationResult
    from zato.server.pubsub.model import subnone
    from zato.server.service import Service
    Bunch   = Bunch
    Column = Column
    PerPIDResponse = PerPIDResponse
    ServerInvocationResult = ServerInvocationResult
    Service = Service
    subnone = subnone

# ################################################################################################################################
# ################################################################################################################################

elem = 'pubsub_endpoint'
model = PubSubEndpoint
label = 'a pub/sub endpoint'
get_list_docs = 'pub/sub endpoints'
broker_message = PUBSUB
broker_message_prefix = 'ENDPOINT_'
list_func = pubsub_endpoint_list
skip_input_params = ['sub_key', 'is_sub_allowed']
input_optional_extra = ['service_name']
output_optional_extra = ['service_name', 'ws_channel_name', 'sec_id', 'sec_type', 'sec_name', 'sub_key', 'endpoint_type_name']
delete_require_instance = False

SubTable = PubSubSubscription.__table__

# ################################################################################################################################

msg_pub_attrs_sio = []

for name in msg_pub_attrs:
    if name in ('topic', 'is_in_sub_queue', 'position_in_group', 'group_id'):
        continue
    elif name.endswith('_id'):
        msg_pub_attrs_sio.append(AsIs(name))
    elif name in ('position_in_group', 'priority', 'size', 'delivery_count', 'expiration'):
        msg_pub_attrs_sio.append(Int(name))
    elif name.startswith(('has_', 'is_')):
        msg_pub_attrs_sio.append(Bool(name))
    else:
        msg_pub_attrs_sio.append(name)

# ################################################################################################################################

_queue_type=COMMON_PUBSUB.QUEUE_TYPE
_meta_endpoint_key = COMMON_PUBSUB.REDIS.META_ENDPOINT_PUB_KEY

# ################################################################################################################################

_sub_skip_update = ('id', 'sub_id', 'sub_key', 'cluster_id', 'creation_time', 'current_depth', 'endpoint_id', 'endpoint_type',
    'last_interaction_time', 'staging_depth', 'sql_ws_client_id', 'topic_name', 'total_depth', 'web_socket',
    'out_rest_http_soap_id', 'out_soap_http_soap_id', 'out_http_soap_id')

# ################################################################################################################################
# ################################################################################################################################

class _GetEndpointQueueMessagesSIO(GetListAdminSIO):
    input_required = ('cluster_id',)
    input_optional = GetListAdminSIO.input_optional + ('sub_id', 'sub_key')
    output_required = (AsIs('msg_id'), 'recv_time')
    output_optional = ('data_prefix_short', Int('delivery_count'), 'last_delivery_time', 'is_in_staging', 'queue_name',
        'endpoint_id', 'sub_key', 'published_by_id', 'published_by_name', 'server_name', 'server_pid')
    output_repeated = True

# ################################################################################################################################
# ################################################################################################################################

def _get_security_id_from_input(self:'Service', input:'strdict') -> 'intnone':

    if input.get('security_name') == 'zato-no-security':
        return

    # If we have a security name on input, we need to turn it into its ID ..
    if security_name := input.get('security_name'):
        security_name = security_name.strip()
        security = self.server.worker_store.basic_auth_get(security_name)
        security = security['config']
        security_id:'int' = security['id']

    # .. otherwise, we use a service ID as it is.
    else:
        security_id = self.request.input.get('security_id')

    return security_id

# ################################################################################################################################
# ################################################################################################################################

def _get_service_id_from_input(self:'Service', input:'strdict') -> 'intnone':

    # If we have a service name on input, we need to turn it into its ID ..
    if service_name := input.get('service_name'):
        try:
            service_name = service_name.strip()
            service_id = self.server.service_store.get_service_id_by_name(service_name)
        except KeyError:
            return

    # .. otherwise, we use a service ID as it is.
    else:
        service_id = self.request.input.get('service_id')

    return service_id

# ################################################################################################################################
# ################################################################################################################################

def instance_hook(self:'Service', input:'strdict', instance:'PubSubEndpoint', attrs:'strdict') -> 'None':

    if attrs['is_delete']:
        return

    # These can be given as ID or name and we need to extract the correct values here
    service_id = _get_service_id_from_input(self, input)
    security_id = _get_security_id_from_input(self, input)

    instance.service_id = service_id
    instance.security_id = security_id

    # Don't use empty string with integer attributes, set them to None (NULL) instead
    if cast_('str', service_id) == '':
        instance.service_id = None

    if cast_('str', security_id) == '':
        instance.security_id = None

    # SQLite will not accept empty strings, must be None
    instance.last_seen = instance.last_seen or None
    instance.last_pub_time = instance.last_pub_time or None
    instance.last_sub_time = instance.last_sub_time or None
    instance.last_deliv_time = instance.last_deliv_time or None

# ################################################################################################################################

def response_hook(
    self:'Service',
    input:'any_',
    instance:'any_',
    attrs:'any_',
    service_type:'str',
) -> 'None':

    if service_type == 'create_edit':
        _ = self.pubsub.wait_for_endpoint(input['name'])

    elif service_type == 'get_list':

        # We are going to check topics for each of these endpoint IDs ..
        endpoint_id_list = []

        # .. go through every endpoint found ..
        for item in self.response.payload:

            # .. append its ID for later use ..
            endpoint_id_list.append(item.id)

        # .. we have all the IDs now and we can check their topics ..
        topic_service = 'zato.pubsub.subscription.get-list'
        topic_response = self.invoke(topic_service, endpoint_id_list=endpoint_id_list)

        # .. top-level response that we are returning ..
        response = self.response.payload.getvalue()
        response = loads(response)
        response = response['zato_pubsub_endpoint_get_list_response']

        # .. first, add the required key to all the endpoints ..
        for item in response:
            item['topic_list'] = []

        # .. now, go through the items once more and populate topics for each endpoint ..
        for item in response:
            for topic_dict in topic_response:
                if item['id'] == topic_dict['endpoint_id']:
                    topic_name = topic_dict['topic_name']
                    item['topic_list'].append(topic_name)

# ################################################################################################################################

def broker_message_hook(
    self:'Service',
    input:'strdict',
    instance:'PubSubEndpoint',
    attrs:'strdict',
    service_type:'str'
) -> 'None':
    if service_type == 'create_edit':
        with closing(self.odb.session()) as session:
            input['is_internal'] = pubsub_endpoint(session, input['cluster_id'], instance.id).is_internal

# ################################################################################################################################
# ################################################################################################################################

@add_metaclass(GetListMeta)
class GetList(AdminService):
    _filter_by = PubSubEndpoint.name,

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new pub/sub endpoint.
    """
    class SimpleIO(AdminSIO):
        input_required = ('name', 'role', 'is_active', 'is_internal', 'endpoint_type')
        input_optional = ('cluster_id', 'topic_patterns', 'security_id', 'security_name', 'service_id', 'service_name', \
            'ws_channel_id')
        output_required = (AsIs('id'), 'name')
        request_elem = 'zato_pubsub_endpoint_create_request'
        response_elem = 'zato_pubsub_endpoint_create_response'
        default_value = None

    def handle(self):

        input = self.request.input
        cluster_id = input.get('cluster_id') or self.server.cluster_id
        security_id = _get_security_id_from_input(self, self.request.input)
        service_id = _get_service_id_from_input(self, self.request.input)

        # If we had a name of a service on input but there is no ID for it, it means that that the name was invalid.
        if service_name := input.get('service_name'):
            if not service_id:
                raise BadRequest(self.cid, f'No such service -> {service_name}')

        # Services have a fixed role and patterns ..
        if input.endpoint_type == COMMON_PUBSUB.ENDPOINT_TYPE.SERVICE.id:
            role = COMMON_PUBSUB.ROLE.PUBLISHER_SUBSCRIBER.id
            topic_patterns = COMMON_PUBSUB.DEFAULT.Topic_Patterns_All
        else:
            role = input.role
            topic_patterns = input.topic_patterns

        # Populate it back so that we can reuse the same input object
        # when we publish a broker message.
        input.role = role
        input.topic_patterns = topic_patterns

        with closing(self.odb.session()) as session:

            existing_one = session.query(PubSubEndpoint.id).\
                filter(PubSubEndpoint.cluster_id==cluster_id).\
                filter(PubSubEndpoint.name==input.name).\
                first()

            # Names must be unique
            if existing_one:
                raise Conflict(self.cid, 'Endpoint `{}` already exists'.format(input.name))

            # Services cannot be assigned to more than one endpoint
            if service_id:
                try:
                    endpoint_id = self.pubsub.get_endpoint_id_by_service_id(service_id)
                except KeyError:
                    pass
                else:
                    endpoint = self.pubsub.get_endpoint_by_id(endpoint_id)
                    service_name = self.server.service_store.get_service_name_by_id(service_id)
                    msg = f'Service {service_name} is already assigned to endpoint {endpoint.name}'
                    raise Conflict(self.cid, msg)

            # Security definitions cannot be assigned to more than one endpoint
            if security_id:
                try:
                    endpoint_id = self.pubsub.get_endpoint_id_by_sec_id(security_id)
                except KeyError:
                    pass
                else:
                    endpoint = self.pubsub.get_endpoint_by_id(endpoint_id)
                    security = self.server.worker_store.basic_auth_get_by_id(security_id)
                    security_name:'str' = security['name']
                    msg = f'Security definition {security_name} is already assigned to endpoint {endpoint.name}'
                    raise Conflict(self.cid, msg)

            endpoint = PubSubEndpoint()
            endpoint.cluster_id = cluster_id # type: ignore
            endpoint.name = input.name
            endpoint.is_active = input.is_active
            endpoint.is_internal = input.is_internal
            endpoint.endpoint_type = input.endpoint_type
            endpoint.role = input.role
            endpoint.topic_patterns = input.topic_patterns
            endpoint.security_id = security_id
            endpoint.service_id = service_id
            endpoint.ws_channel_id = input.get('ws_channel_id')

            session.add(endpoint)
            session.commit()

            input.action = PUBSUB.ENDPOINT_CREATE.value
            input.id = endpoint.id
            self.broker_client.publish(input)

            self.response.payload.id = endpoint.id
            self.response.payload.name = self.request.input.name

        _ = self.pubsub.wait_for_endpoint(input.name)

# ################################################################################################################################
# ################################################################################################################################

@add_metaclass(CreateEditMeta)
class Edit(AdminService):
    pass

# ################################################################################################################################
# ################################################################################################################################

@add_metaclass(DeleteMeta)
class Delete(AdminService):
    pass

# ################################################################################################################################
# ################################################################################################################################

class Get(AdminService):
    """ Returns details of a pub/sub endpoint.
    """
    class SimpleIO:
        input_required = ('cluster_id', AsIs('id'))
        output_required = ('id', 'name', 'is_active', 'is_internal', 'role', 'endpoint_type')
        output_optional = ('tags', 'topic_patterns', 'pub_tag_patterns', 'message_tag_patterns',
            'security_id', 'ws_channel_id', 'sec_type', 'sec_name', 'ws_channel_name', 'sub_key',
            'service_id', 'service_name', AsIs('topic_list'))

    def handle(self):

        # Local variables
        cluster_id = self.request.input.cluster_id
        endpoint_id = self.request.input.id

        # Connect to the database ..
        with closing(self.odb.session()) as session:

            # .. get basic information about this endpoint ..
            self.response.payload = pubsub_endpoint(session, self.request.input.cluster_id, self.request.input.id)

            # .. get a list of topics this endpoint is subscribed to ..
            request = {'cluster_id':cluster_id, 'endpoint_id':endpoint_id, 'sql_session':session}

            topic_service = 'zato.pubsub.subscription.get-list'
            topic_list = self.invoke(topic_service, request)
            self.response.payload.topic_list = topic_list

# ################################################################################################################################
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
        self.response.payload[:] = get_endpoint_metadata(self.server, self.request.input.endpoint_id)

# ################################################################################################################################
# ################################################################################################################################

class GetEndpointQueueNonGDDepth(AdminService):
    """ Returns current depth of non-GD messages for input sub_key which must have a delivery task on current server.
    """
    class SimpleIO(AdminSIO):
        input_required = 'sub_key'
        output_optional = Int('current_depth_non_gd')

    def handle(self):
        if pubsub_tool := self.pubsub.get_pubsub_tool_by_sub_key(self.request.input.sub_key):
            _, non_gd_depth = pubsub_tool.get_queue_depth(self.request.input.sub_key)
            self.response.payload.current_depth_non_gd = non_gd_depth

# ################################################################################################################################
# ################################################################################################################################

class _GetEndpointQueue(AdminService):

    def _add_queue_depths(self, session:'SASession', item:'strdict') -> 'None':

        cluster_id = self.request.input.cluster_id
        sub_key = item['sub_key']

        current_depth_gd_q = pubsub_messages_for_queue_raw(session, cluster_id, sub_key, skip_delivered=True)

        # This could be read from the SQL database ..
        item['current_depth_gd'] = count(session, current_depth_gd_q)

        # .. but non-GD depth needs to be collected from all the servers around. Note that the server may not be known
        # in case the subscriber is a WSX client. In this case, by definition, there will be no non-GD messages for that client.
        sk_server = self.pubsub.get_delivery_server_by_sub_key(item['sub_key'])

        if sk_server:

            if sk_server.server_name == self.server.name and sk_server.server_pid == self.server.pid:
                if pubsub_tool := self.pubsub.get_pubsub_tool_by_sub_key(item['sub_key']):
                    _, current_depth_non_gd = pubsub_tool.get_queue_depth(item['sub_key'])
            else:

                # An invoker pointing to that server
                invoker   = self.server.rpc.get_invoker_by_server_name(sk_server.server_name)

                # The service we are invoking
                service_name = GetEndpointQueueNonGDDepth.get_name()

                # Inquire the server about our sub_key
                request = {
                    'sub_key': item['sub_key'],
                }

                # Keyword arguments point to a specific PID in that server
                kwargs = {
                    'pid': sk_server.server_pid
                }

                # Do invoke the server now
                response = invoker.invoke(service_name, request, **kwargs)

                self.logger.info('*' * 50)
                self.logger.warn('Invoker  -> %s', invoker)
                self.logger.warn('RESPONSE -> %s', response)
                self.logger.info('*' * 50)

                """
                '''

                pid_data = response['response']

                if pid_data:
                    pid_data = cast_('anydict', pid_data)
                    current_depth_non_gd = pid_data['current_depth_non_gd']
                else:
                    current_depth_non_gd = 0

        # No delivery server = there cannot be any non-GD messages waiting for that subscriber
        else:
            current_depth_non_gd = 0
            '''
            """

        # item['current_depth_non_gd'] = current_depth_non_gd
        item['current_depth_non_gd'] = 0

# ################################################################################################################################
# ################################################################################################################################

class GetEndpointQueue(_GetEndpointQueue):
    """ Returns information describing an individual endpoint queue.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'id')
        output_optional = common_sub_data

    def handle(self) -> 'None':
        with closing(self.odb.session()) as session:
            item = pubsub_endpoint_queue(session, self.request.input.cluster_id, self.request.input.id)
            item.creation_time = datetime_from_ms(item.creation_time * 1000.0)
            if getattr(item, 'last_interaction_time', None):
                item.last_interaction_time = datetime_from_ms(item.last_interaction_time * 1000.0)
            self.response.payload = item
            self._add_queue_depths(session, self.response.payload)

# ################################################################################################################################
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

    def get_data(self, session:'SASession') -> 'anylist':
        return self._search(pubsub_subscription_list_by_endpoint_id, session, self.request.input.cluster_id,
            self.request.input.endpoint_id, False)

    def handle(self) -> 'None':
        response = []
        with closing(self.odb.session()) as session:
            for item in self.get_data(session):

                item = item.get_value()

                self._add_queue_depths(session, item)
                item['creation_time'] = datetime_from_ms(item['creation_time'] * 1000.0)

                if item['last_interaction_time']:
                    item['last_interaction_time'] = datetime_from_ms(item['last_interaction_time'] * 1000.0)

                if item['last_interaction_details']:
                    if not isinstance(item['last_interaction_details'], unicode):
                        item['last_interaction_details'] = item['last_interaction_details'].decode('utf8')

                response.append(item)

        self.response.payload[:] = response

# ################################################################################################################################
# ################################################################################################################################

class UpdateEndpointQueue(AdminService):
    """ Modifies selected subscription queue.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'id', 'sub_key', 'active_status')
        input_optional = drop_sio_elems(common_sub_data, 'active_status', 'sub_key', 'creation_time', 'last_interaction_time')
        output_required = ('id', 'name')

    def handle(self) -> 'None':

        # REST and SOAP outconn IDs have different input names but they both map
        # to the same SQL-level attribute. This means that at most one of them may be
        # provided on input. It's an error to provide both.
        out_rest_http_soap_id = self.request.input.get('out_rest_http_soap_id')
        out_soap_http_soap_id = self.request.input.get('out_soap_http_soap_id')

        if out_rest_http_soap_id and out_soap_http_soap_id:
            raise BadRequest(self.cid, 'Cannot provide both out_rest_http_soap_id and out_soap_http_soap_id on input')

        should_update_delivery_server = self.request.input.endpoint_type not in {

            # WebSockets clients dynamically attach to delivery servers hence the servers cannot be updated by users
            COMMON_PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id,

            # Services are always invoked in the same server
            COMMON_PUBSUB.ENDPOINT_TYPE.SERVICE.id,
        }

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

            if should_update_delivery_server:
                old_delivery_server_id = item.server_id
                new_delivery_server_id = self.request.input.server_id
                if new_delivery_server_id:
                    new_delivery_server_name = server_by_id(session, self.server.cluster_id, new_delivery_server_id).name
                else:
                    new_delivery_server_name = None
            else:
                # These are added purely for static type hints
                old_delivery_server_id = -1
                new_delivery_server_id = -1
                new_delivery_server_name = 'new-delivery-server-name'

            for key, value in sorted(self.request.input.items()):
                if key not in _sub_skip_update:
                    if isinstance(value, bytes):
                        value = value.decode('utf8')
                    if value is not None:
                        setattr(item, key, value)

            # This one we set manually based on the logic at the top of the method
            item.out_http_soap_id = out_http_soap_id

            session.add(item)
            session.commit()

            self.response.payload.id = self.request.input.id
            self.response.payload.name = item.topic.name

            # Notify all processes, including our own, that this subscription's parameters have changed
            updated_params_msg:'strdict' = item.asdict()

            # Remove bytes objects from what we are about to publish - they had to be used
            # in SQL messages but not here.
            for key, value in deepcopy(updated_params_msg).items():
                if isinstance(value, bytes):
                    updated_params_msg[key] = value.decode('utf8')

            updated_params_msg['action'] = PUBSUB.SUBSCRIPTION_EDIT.value
            self.broker_client.publish(updated_params_msg)

            # We change the delivery server in background - note how we send name, not ID, on input.
            # This is because our invocation target will want to use
            # self.server.rpc.get_invoker_by_server_name(server_name).invoke(...)
            if should_update_delivery_server:
                if old_delivery_server_id != new_delivery_server_id:
                    self.broker_client.publish({
                        'sub_key': self.request.input.sub_key,
                        'endpoint_type': item.endpoint.endpoint_type,
                        'old_delivery_server_id': old_delivery_server_id,
                        'new_delivery_server_name': new_delivery_server_name,
                        'action': PUBSUB.DELIVERY_SERVER_CHANGE.value,
                    })

# ################################################################################################################################
# ################################################################################################################################

class ClearEndpointQueue(AdminService):
    """ Clears messages from the queue given on input.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'sub_key')
        input_optional = ('queue_type',)

    def handle(self) -> 'None':

        # Make sure the (optional) queue type is one of the allowed values
        if queue_type := self.request.input.queue_type:
            if queue_type not in _queue_type:
                raise BadRequest(self.cid, 'Invalid queue_type:`{}`'.format(queue_type))
            else:
                if queue_type == _queue_type.CURRENT:
                    is_in_staging = False
                elif queue_type == _queue_type.STAGING:
                    is_in_staging = True
                else:
                    is_in_staging = False
        else:
            is_in_staging = None

        # Remove all references to the queue given on input
        with closing(self.odb.session()) as session:
            q = session.query(PubSubEndpointEnqueuedMessage).\
                filter(PubSubEndpointEnqueuedMessage.cluster_id==self.request.input.cluster_id).\
                filter(PubSubEndpointEnqueuedMessage.sub_key==self.request.input.sub_key)

            if is_in_staging is not None:
                q = q.filter(cast_('Column', PubSubEndpointEnqueuedMessage.is_in_staging).is_(is_in_staging))
            _ = q.delete()

            session.commit()

        # Notify delivery tasks that
        self.broker_client.publish({
            'sub_key': self.request.input.sub_key,
            'action': PUBSUB.QUEUE_CLEAR.value,
        })

# ################################################################################################################################
# ################################################################################################################################

class DeleteEndpointQueue(AdminService):
    """ Deletes input message queues for a subscriber based on sub_keys - including all messages
    and their parent subscription object.
    """
    class SimpleIO(AdminSIO):
        input_optional = ('cluster_id', 'sub_key', List('sub_key_list'))

    def handle(self) -> 'None':

        sub_key = self.request.input.sub_key
        sub_key_list = self.request.input.sub_key_list

        if not(sub_key or sub_key_list):
            raise BadRequest(self.cid, 'Exactly one of sub_key or sub_key_list is required')

        if sub_key and sub_key_list:
            raise BadRequest(self.cid, 'Cannot provide both sub_key and sub_key_list on input')

        if sub_key:
            sub_key_list = [sub_key] # Otherwise, we already had sub_key_list on input so 'else' is not needed

        cluster_id = self.request.input.get('cluster_id') or self.server.cluster_id

        with closing(self.odb.session()) as session:

            # First we need a list of topics to which sub_keys were related - required by broker messages.
            topic_sub_keys = get_topic_sub_keys_from_sub_keys(session, cluster_id, sub_key_list)

            # .. log what we are about to do ..
            self.logger.info('Deleting subscriptions `%s`', topic_sub_keys)

            # .. delete all subscriptions from the sub_key list ..
            _:'any_' = session.execute(
                delete(SubTable).\
                where(
                    SubTable.c.sub_key.in_(sub_key_list),
                )
            )

            # .. and commit the changes permanently.
            session.commit()

        # Notify workers about deleted subscription(s)
        self.broker_client.publish({
            'topic_sub_keys': topic_sub_keys,
            'action': PUBSUB.SUBSCRIPTION_DELETE.value,
        })

# ################################################################################################################################
# ################################################################################################################################

class _GetMessagesBase:

    def _get_sub_by_sub_input(
        self:'Service', # type: ignore
        input:'Bunch'
    ) -> 'subnone':

        if input.get('sub_id'):
            return self.pubsub.get_subscription_by_id(input.sub_id)
        elif input.get('sub_key'):
            return self.pubsub.get_subscription_by_sub_key(input.sub_key)
        else:
            raise Exception('Either sub_id or sub_key must be given on input')

# ################################################################################################################################
# ################################################################################################################################

class GetEndpointQueueMessagesGD(AdminService, _GetMessagesBase):
    """ Returns a list of GD messages queued up for input subscription.
    """
    _filter_by = PubSubMessage.data_prefix,
    SimpleIO = _GetEndpointQueueMessagesSIO # type: ignore

    def get_data(self, session:'SASession') -> 'anylist':

        input = self.request.input
        sub = self._get_sub_by_sub_input(input)

        if not sub:
            self.logger.info('Could not find subscription by input `%s` (#1)', input)
            return []

        return self._search(
            pubsub_messages_for_queue, session, self.request.input.cluster_id, sub.sub_key, True, False)

    def handle(self) -> 'None':
        with closing(self.odb.session()) as session:
            self.response.payload[:] = [elem.get_value() for elem in self.get_data(session)]

        for item in self.response.payload:
            item['recv_time'] = datetime_from_ms(item['recv_time'] * 1000.0)
            item['published_by_name'] = self.pubsub.get_endpoint_by_id(item['published_by_id']).name

# ################################################################################################################################
# ################################################################################################################################

class GetServerEndpointQueueMessagesNonGD(AdminService):
    """ Returns a list of non-GD messages for an input queue by its sub_key which must exist on current server,
    i.e. current server must be the delivery server for this sub_key.
    """
    SimpleIO = _GetEndpointQueueMessagesSIO # type: ignore

    def handle(self) -> 'None':

        data_prefix_len = self.pubsub.data_prefix_len
        data_prefix_short_len = self.pubsub.data_prefix_short_len

        if ps_tool := self.pubsub.get_pubsub_tool_by_sub_key(self.request.input.sub_key):
            messages = ps_tool.get_messages(self.request.input.sub_key, False)

            self.response.payload[:] = [
                make_short_msg_copy_from_msg(elem, data_prefix_len, data_prefix_short_len) for elem in messages]

        for elem in self.response.payload:
            elem['recv_time'] = datetime_from_ms(elem['recv_time'] * 1000.0)
            elem['published_by_name'] = self.pubsub.get_endpoint_by_id(elem['published_by_id']).name

# ################################################################################################################################
# ################################################################################################################################

class GetEndpointQueueMessagesNonGD(NonGDSearchService, _GetMessagesBase):
    """ Returns a list of non-GD messages for an input queue by its sub_key.
    """
    SimpleIO = _GetEndpointQueueMessagesSIO # type: ignore

    def handle(self) -> 'None':

        input = self.request.input
        sub = self._get_sub_by_sub_input(input)

        if not sub:
            self.logger.info('Could not find subscription by input `%s` (#2)', input)
            return

        sk_server = self.pubsub.get_delivery_server_by_sub_key(sub.sub_key)

        if sk_server:
            invoker = self.server.rpc.get_invoker_by_server_name(sk_server.server_name)
            response = invoker.invoke(GetServerEndpointQueueMessagesNonGD.get_name(), {
                'cluster_id': self.request.input.cluster_id,
                'sub_key': sub.sub_key,
            }, pid=sk_server.server_pid)

            if response:
                self.response.payload[:] = reversed(response['response'])

# ################################################################################################################################
# ################################################################################################################################

class _GetEndpointSummaryBase(AdminService):
    """ Base class for services returning summaries about endpoints
    """
    class SimpleIO:
        input_required = ('cluster_id',)
        input_optional = ('topic_id',)
        output_required = ('id', 'endpoint_name', 'endpoint_type', 'subscription_count', 'is_active', 'is_internal')
        output_optional = ['security_id', 'sec_type', 'sec_name', 'ws_channel_id', 'ws_channel_name',
            'service_id', 'service_name', 'last_seen', 'last_deliv_time', 'role', 'endpoint_type_name'] + \
                drop_sio_elems(common_sub_data, 'endpoint_name', 'endpoint_type', 'is_internal')

# ################################################################################################################################
# ################################################################################################################################

class GetEndpointSummary(_GetEndpointSummaryBase):
    """ Returns summarized information about a selected endpoint subscribed to topics.
    """
    class SimpleIO(_GetEndpointSummaryBase.SimpleIO):
        input_required = _GetEndpointSummaryBase.SimpleIO.input_required + ('endpoint_id',)
        request_elem = 'zato_pubsub_subscription_get_endpoint_summary_request'
        response_elem = 'zato_pubsub_subscription_get_endpoint_summary_response'

    def handle(self) -> 'None':
        with closing(self.odb.session()) as session:
            item = pubsub_endpoint_summary(session, self.server.cluster_id, self.request.input.endpoint_id)

            item = item._asdict()

            if item['last_seen']:
                item['last_seen'] = datetime_from_ms(item['last_seen'])

            if item['last_deliv_time']:
                item['last_deliv_time'] = datetime_from_ms(item['last_deliv_time'])

            item['endpoint_type_name'] = COMMON_PUBSUB.ENDPOINT_TYPE.get_name_by_type(item['endpoint_type'])

            self.response.payload = item

# ################################################################################################################################
# ################################################################################################################################

class GetEndpointSummaryList(_GetEndpointSummaryBase):
    """ Returns summarized information about all endpoints subscribed to topics.
    """
    _filter_by = PubSubEndpoint.name,

    class SimpleIO(_GetEndpointSummaryBase.SimpleIO, GetListAdminSIO):
        request_elem = 'zato_pubsub_endpoint_get_endpoint_summary_list_request'
        response_elem = 'zato_pubsub_endpoint_get_endpoint_summary_list_response'

    def get_data(self, session:'SASession') -> 'anylist':

        # This will be a list of dictionaries that we return
        out = []

        # These are SQL rows
        result = self._search(pubsub_endpoint_summary_list, session, self.request.input.cluster_id,
            self.request.input.get('topic_id') or None, False)

        for item in result:

            item = item._asdict()

            if item['last_seen']:
                item['last_seen'] = datetime_from_ms(item['last_seen'])

            if item['last_deliv_time']:
                item['last_deliv_time'] = datetime_from_ms(item['last_deliv_time'])

            item['endpoint_type_name'] = COMMON_PUBSUB.ENDPOINT_TYPE.get_name_by_type(item['endpoint_type'])

            out.append(item)

        return out

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)

# ################################################################################################################################
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

    def handle(self) -> 'None':

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
# ################################################################################################################################

class GetServerDeliveryMessages(AdminService):
    """ Returns a list of messages to be delivered to input endpoint. The messages must exist on current server.
    """
    class SimpleIO(AdminSIO):
        input_required = 'sub_key'
        output_optional = List('msg_list')

    def handle(self) -> 'None':
        if ps_tool := self.pubsub.get_pubsub_tool_by_sub_key(self.request.input.sub_key):
            self.response.payload.msg_list = ps_tool.pull_messages(self.request.input.sub_key)

# ################################################################################################################################
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

    def handle(self) -> 'None':

        input = self.request.input
        sub = self._get_sub_by_sub_input(input)

        if not sub:
            self.logger.info('Could not find subscription by input `%s` (#3)', input)
            return

        sk_server = self.pubsub.get_delivery_server_by_sub_key(sub.sub_key)

        if sk_server:
            invoker = self.server.rpc.get_invoker_by_server_name(sk_server.server_name)
            response = invoker.invoke(GetServerDeliveryMessages.get_name(), {
                'sub_key': sub.sub_key,
            }, pid=sk_server.server_pid)

            if response:

                # It may be a dict on a successful invocation ..
                if isinstance(response, dict):
                    data = response         # type: ignore
                    data = data['response'] # type: ignore

                # .. otherwise, it may be an IPCResponse object.
                else:
                    data = response.data # type: ignore

                # Extract the actual list of messages ..
                data = cast_('strdict', data)
                msg_list = data['msg_list']
                msg_list = reversed(msg_list)
                msg_list = list(msg_list)

                # .. at this point the topic may have been already deleted ..
                try:
                    topic = self.pubsub.get_topic_by_sub_key(sub.sub_key)
                    topic_name = topic.name
                except KeyError:
                    self.logger.info('Could not find topic by sk `%s`', sub.sub_key)
                    topic_name = '(None)'

                # .. make sure that all of the sub_keys actually still exist ..
                with closing(self.odb.session()) as session:
                    msg_list = ensure_subs_exist(
                        session,
                        topic_name,
                        msg_list,
                        msg_list,
                        'returning to endpoint',
                        '<no-ctx-string>'
                    )

                self.response.payload[:] = msg_list
        else:
            self.logger.info('Could not find delivery server for sub_key:`%s`', sub.sub_key)

# ################################################################################################################################
# ################################################################################################################################

class GetEndpointMetadata(AdminService):
    """ An invoker making use of the API that Redis-based communication used to use.
    """
    def handle(self) -> 'None':

        # Local aliases
        endpoint_id = self.request.raw_request['endpoint_id']

        # Build a full key to look up data by ..
        endpoint_key = _meta_endpoint_key % (self.server.cluster_id, endpoint_id)

        # .. get the data ..
        topic_list = self.server.pub_sub_metadata.get(endpoint_key)

        # .. and return it to our caller.
        if topic_list:
            self.response.payload = {'topic_list': topic_list}

# ################################################################################################################################
# ################################################################################################################################
