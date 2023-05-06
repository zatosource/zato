# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from dataclasses import dataclass

# gevent
from gevent import sleep

# Python 2/3 compatibility
from six import add_metaclass

# Zato
from zato.common.broker_message import PUBSUB as BROKER_MSG_PUBSUB
from zato.common.api import PUBSUB
from zato.common.odb.model import PubSubEndpointEnqueuedMessage, PubSubMessage, PubSubTopic
from zato.common.odb.query import pubsub_messages_for_topic, pubsub_publishers_for_topic, pubsub_topic, pubsub_topic_list
from zato.common.odb.query.pubsub.topic import get_gd_depth_topic, get_gd_depth_topic_list, get_topic_list_by_id_list, \
    get_topic_list_by_name_list, get_topic_list_by_name_pattern, get_topic_sub_count_list, get_topics_by_sub_keys
from zato.common.typing_ import anylist, cast_, intlistnone, intnone, strlistnone, strnone
from zato.common.util.api import ensure_pubsub_hook_is_valid
from zato.common.util.pubsub import get_last_pub_metadata
from zato.common.util.time_ import datetime_from_ms
from zato.server.connection.http_soap import BadRequest
from zato.server.service import AsIs, Bool, Int, List, Model, Opaque, Service
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO
from zato.server.service.internal.pubsub.search import NonGDSearchService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, stranydict, strlist
    Bunch = Bunch
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

topic_limit_fields = [Int('limit_retention'), Int('limit_message_expiry'), Int('limit_sub_inactivity')]

elem = 'pubsub_topic'
model = PubSubTopic
label = 'a pub/sub topic'
get_list_docs = 'pub/sub topics'
broker_message = BROKER_MSG_PUBSUB
broker_message_prefix = 'TOPIC_'
list_func = pubsub_topic_list
skip_input_params = ['cluster_id', 'is_internal', 'current_depth_gd', 'last_pub_time', 'last_pub_msg_id', 'last_endpoint_id',
    'last_endpoint_name']
input_optional_extra = ['needs_details', 'on_no_subs_pub', 'hook_service_name'] + topic_limit_fields
output_optional_extra = ['is_internal', Int('current_depth_gd'), Int('current_depth_non_gd'), 'last_pub_time',
    'hook_service_name', 'last_pub_time', AsIs('last_pub_msg_id'), 'last_endpoint_id', 'last_endpoint_name',
    Bool('last_pub_has_gd'), Opaque('last_pub_server_pid'), 'last_pub_server_name', 'on_no_subs_pub',
    Int('sub_count'),] + topic_limit_fields

# ################################################################################################################################

sub_broker_attrs = ('active_status', 'active_status', 'cluster_id', 'creation_time', 'endpoint_id', 'has_gd', 'id',
    'is_durable', 'is_internal', 'name', 'out_amqp_id', 'out_http_soap_id', 'sub_key', 'topic_id', 'ws_channel_id',
    'ws_sub_id', 'delivery_group_size')

# ################################################################################################################################

_meta_topic_key = PUBSUB.REDIS.META_TOPIC_LAST_KEY
_meta_endpoint_key = PUBSUB.REDIS.META_ENDPOINT_PUB_KEY

# ################################################################################################################################

def _format_meta_topic_key(cluster_id:'int', topic_id:'int') -> 'str':
    return _meta_topic_key % (cluster_id, topic_id)

# ################################################################################################################################

def broker_message_hook(
    self:'Service',
    input:'stranydict',
    instance:'PubSubTopic',
    attrs:'stranydict',
    service_type:'str'
) -> 'None':

    if service_type == 'create_edit':
        with closing(self.odb.session()) as session:
            topic = pubsub_topic(session, input['cluster_id'], instance.id)
            input['is_internal'] = topic.is_internal
            input['max_depth_gd'] = topic.max_depth_gd
            input['max_depth_non_gd'] = topic.max_depth_non_gd
            input['hook_service_id'] = topic.hook_service_id
            input['hook_service_name'] = topic.hook_service_name

# ################################################################################################################################

def _add_limits(item:'any_') -> 'None':
    item.limit_retention      = item.get('limit_retention')      or PUBSUB.DEFAULT.LimitTopicRetention
    item.limit_sub_inactivity = item.get('limit_sub_inactivity') or PUBSUB.DEFAULT.LimitMessageExpiry
    item.limit_message_expiry = item.get('limit_message_expiry') or PUBSUB.DEFAULT.LimitSubInactivity

# ################################################################################################################################

def response_hook(self:'Service', input:'stranydict', instance:'PubSubTopic', attrs:'stranydict', service_type:'str') -> 'None':

    if service_type == 'get_list':

        # Limit-related fields were introduced post-3.2 release which is why they may not exist
        for item in self.response.payload:
            _add_limits(item)

        # Details are needed when the main list of topics is requested. However, if only basic information
        # is needed, like a list of topic IDs and their names, we don't need to look up additional details.
        # The latter is the case of the message publication screen which simply needs a list of topic IDs/names.
        if input.get('needs_details', True):

            # Topics to look up data for
            topic_id_list = []

            # Collect all topic IDs whose depth need to be looked up
            for item in self.response.payload:
                topic_id_list.append(item.id)

            # .. query the database to find all the additional data for topics from the list ..
            with closing(self.odb.session()) as session:
                depth_by_topic = get_gd_depth_topic_list(session, input['cluster_id'], topic_id_list)
                sub_count_by_topic = get_topic_sub_count_list(session, input['cluster_id'], topic_id_list)

            # .. convert it all to a dict to make it easier to use it ..
            depth_by_topic = dict(depth_by_topic)
            sub_count_by_topic = dict(sub_count_by_topic)

            # .. look up last pub metadata among all the servers ..
            last_pub_by_topic = get_last_pub_metadata(self.server, topic_id_list) # type: dict

            # .. now, having collected all the details, go through all the topics again
            # .. and assign the metadata found.
            for item in self.response.payload:

                # .. assign additional data ..
                item.current_depth_gd = depth_by_topic.get(item.id) or 0
                item.sub_count = sub_count_by_topic.get(item.id) or 0

                # .. assign last usage metadata ..
                last_data = last_pub_by_topic.get(item.id)

                if last_data:
                    item.last_pub_time = last_data['pub_time']
                    item.last_pub_has_gd = last_data['has_gd']
                    item.last_pub_msg_id = last_data['pub_msg_id']
                    item.last_endpoint_id = last_data['endpoint_id']
                    item.last_endpoint_name = last_data['endpoint_name']
                    item.last_pub_server_pid = last_data.get('server_pid')
                    item.last_pub_server_name = last_data.get('server_name')

                    # PIDs are integers
                    if item.last_pub_server_pid:
                        item.last_pub_server_pid = int(item.last_pub_server_pid) # type: ignore

# ################################################################################################################################

def pre_opaque_attrs_hook(self:'Service', input:'stranydict', instance:'PubSubTopic', attrs:'stranydict') -> 'None':

    if not input.get('hook_service_name'):
        if input.get('hook_service_id'):
            hook_service_name = self.server.service_store.get_service_name_by_id(input['hook_service_id'])
            input['hook_service_name'] = hook_service_name

# ################################################################################################################################

def instance_hook(self:'Service', input:'stranydict', instance:'PubSubTopic', attrs:'stranydict') -> 'None':

    if attrs['is_create_edit']:

        # Populate a field that ODB requires even if it is reserved for future use
        instance.pub_buffer_size_gd = 0

        # Validate if broker hook actually exists
        ensure_pubsub_hook_is_valid(self, input, instance, attrs)

        # If input hook service is provided by its name,
        # turn it into a service ID and assign it to instance.
        hook_service_name = input.get('hook_service_name')
        if hook_service_name:
            hook_service_id = self.server.service_store.get_service_id_by_name(hook_service_name)
            instance.hook_service_id = hook_service_id

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DeleteTopicRequest(Model):
    id: intnone
    id_list: intlistnone
    name: strnone
    name_list: strlistnone
    pattern: strnone

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DeleteTopicResponse(Model):
    topics_deleted: anylist

# ################################################################################################################################
# ################################################################################################################################

@add_metaclass(GetListMeta)
class GetList(AdminService):
    _filter_by = PubSubTopic.name,

# ################################################################################################################################
# ################################################################################################################################

@add_metaclass(CreateEditMeta)
class Create(AdminService):
    pass

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

class DeleteTopics(Service):

    class SimpleIO:
        input = DeleteTopicRequest
        output = DeleteTopicResponse

    def _get_topic_data(self, query:'any_', condition:'any_') -> 'anylist':

        with closing(self.odb.session()) as session:
            topic_data = query(session, condition)

        topic_data = [dict(elem) for elem in topic_data]
        return topic_data

# ################################################################################################################################

    def _delete_topic_list(self, topic_id_list:'anylist') -> 'anylist':

        # Make sure we have a list of integers on input
        topic_id_list = [int(elem) for elem in topic_id_list]

        # We want to return a list of their IDs along with names so that the API users can easily understand what was deleted
        # which means that we need to construct the list upfront as otherwise, once we delete a topic,
        # such information will be no longer available.
        topic_data = self._get_topic_data(get_topic_list_by_id_list, topic_id_list)

        # Our response to produce
        out = []

        # A list of topic IDs that we were able to delete
        topics_deleted = []

        # Go through each of the input topic IDs ..
        for topic_id in topic_id_list:

            # .. invoke the service that will delete the topic ..
            try:
                self.invoke(Delete.get_name(), {
                    'id': topic_id
                })
                pass
            except Exception as e:
                self.logger.warn('Exception while deleting topic `%s` -> `%s`', topic_id, e)
            else:
                # If we are here, it means that the topic was deleted
                # in which case we add its ID for later use ..
                topics_deleted.append(topic_id)

                # .. sleep for a while in case to make sure there is no sudden surge of deletions ..
                sleep(0.05)

        # Go through each of the IDs given on input and return it on output too
        # as long as we actually did delete such a topic.
        for elem in topic_data:
            if elem['id'] in topics_deleted:
                out.append(elem)

        # Return the response to our caller
        return out

# ################################################################################################################################

    def _get_topic_id_list(self, query:'any_', condition:'any_') -> 'anylist':
        topic_data = self._get_topic_data(query, condition)
        out = [elem['id'] for elem in topic_data]
        return out

# ################################################################################################################################

    def handle(self) -> 'None':

        # Type checks
        topic_id_list:'anylist'

        # Local aliases
        input = self.request.input # type: DeleteTopicRequest

        # We can be given several types of input elements in the incoming request
        # and we always need to build a list of IDs out of them, unless we already
        # have a list of IDs on input.

        # This is a list - use it as-is
        if input.id_list:
            topic_id_list = input.id_list

        # It is an individual topic ID - we can turn it into a list as-is
        elif input.id:
            topic_id_list = [input.id]

        # It is an individual topic name - turn it into a list look it up in the database
        elif input.name:
            query = get_topic_list_by_name_list
            condition = [input.name]
            topic_id_list = self._get_topic_id_list(query, condition)

        # It is a list of names - look up topics matching them now
        elif input.name_list:
            query = get_topic_list_by_name_list
            condition = input.name_list
            topic_id_list = self._get_topic_id_list(query, condition)

        # This is a list of patterns but not necessarily full topic names as above
        elif input.pattern:
            query = get_topic_list_by_name_pattern
            condition = input.pattern
            topic_id_list = self._get_topic_id_list(query, condition)

        else:
            raise BadRequest(self.cid, 'No deletion criteria were given on input')

        # No matter how we arrived at this result, we have a list of topic IDs
        # and we can delete each of them now ..
        topics_deleted = self._delete_topic_list(topic_id_list)

        # .. now, we can produce a response for our caller ..
        response = DeleteTopicResponse()
        response.topics_deleted = topics_deleted

        # .. and return it on output
        self.response.payload = response

# ################################################################################################################################
# ################################################################################################################################

class Get(AdminService):
    """ Returns a pub/sub topic by its ID.
    """
    class SimpleIO:
        input_optional = 'cluster_id', AsIs('id'), 'name'
        output_optional = 'id', 'name', 'is_active', 'is_internal', 'has_gd', 'max_depth_gd', 'max_depth_non_gd', \
            'current_depth_gd', Int('limit_retention'), Int('limit_message_expiry'), Int('limit_sub_inactivity'), \
                'last_pub_time', 'on_no_subs_pub'

    def handle(self) -> 'None':

        # Local aliases
        cluster_id = self.request.input.get('cluster_id') or self.server.cluster_id
        topic_id   = self.request.input.id
        topic_name = self.request.input.name

        with closing(self.odb.session()) as session:
            topic = pubsub_topic(session, cluster_id, topic_id, topic_name) # type: PubSubTopic
            topic['current_depth_gd'] = get_gd_depth_topic(session, cluster_id, topic.id)

        # Now, we know that we have this object so we can just make use of its ID
        topic_id = topic.id

        last_data = get_last_pub_metadata(self.server, [topic_id])
        if last_data:
            topic['last_pub_time'] = last_data[int(topic_id)]['pub_time']

        # Limits were added post-3.2 release
        _add_limits(topic)

        self.response.payload = topic

# ################################################################################################################################
# ################################################################################################################################

class ClearTopicNonGD(AdminService):
    """ Clears a topic from all non-GD messages on current server.
    """
    class SimpleIO:
        input_required = ('topic_id',)
        output_optional = 'status'

    def handle(self) -> 'None':
        self.pubsub.sync_backlog.clear_topic(self.request.input.topic_id)
        self.response.payload.status = 'ok.{}.{}'.format(self.server.name, self.server.pid)

# ################################################################################################################################
# ################################################################################################################################

class Clear(AdminService):
    """ Clears a topic from GD and non-GD messages.
    """
    class SimpleIO:
        input_required = 'id'
        input_optional = 'cluster_id'

    def handle(self) -> 'None':

        # Local aliases
        cluster_id = self.request.input.get('cluster_id') or self.server.cluster_id
        topic_id = self.request.input.id

        with closing(self.odb.session()) as session:

            self.logger.info('Clearing topic `%s` (id:%s)', self.pubsub.get_topic_by_id(topic_id).name, topic_id)

            # Remove all GD messages
            _ = session.query(PubSubMessage).\
                filter(PubSubMessage.cluster_id==cluster_id).\
                filter(PubSubMessage.topic_id==topic_id).\
                delete()

            # Remove all references to topic messages from target queues
            _ = session.query(PubSubEndpointEnqueuedMessage).\
                filter(PubSubEndpointEnqueuedMessage.cluster_id==cluster_id).\
                filter(PubSubEndpointEnqueuedMessage.topic_id==topic_id).\
                delete()

            # Whatever happens with non-GD messsages we can at least delete the GD ones
            session.commit()

        # Delete non-GD messages for that topic on all servers
        _ = self.server.rpc.invoke_all(ClearTopicNonGD.get_name(), {
            'topic_id': topic_id,
        }, timeout=90)

# ################################################################################################################################
# ################################################################################################################################

class GetPublisherList(AdminService):
    """ Returns all publishers that sent at least one message to a given topic.
    """
    class SimpleIO:
        input_required = 'topic_id'
        input_optional = 'cluster_id'
        output_required = ('name', 'is_active', 'is_internal', 'pub_pattern_matched')
        output_optional = ('service_id', 'security_id', 'ws_channel_id', 'last_seen', 'last_pub_time', AsIs('last_msg_id'),
            AsIs('last_correl_id'), 'last_in_reply_to', 'service_name', 'sec_name', 'ws_channel_name', AsIs('ext_client_id'))
        output_repeated = True

    def handle(self) -> 'None':

        # Type checks
        item:'Bunch'

        # Local aliases
        cluster_id = self.request.input.get('cluster_id') or self.server.cluster_id

        response = []

        with closing(self.odb.session()) as session:

            # Get last pub time for that specific endpoint to this very topic
            last_data = pubsub_publishers_for_topic(session, cluster_id, self.request.input.topic_id).all()

            for item in last_data:
                item.last_seen = datetime_from_ms(cast_('float', item.last_seen))
                item.last_pub_time = datetime_from_ms(cast_('float', item.last_pub_time))
                response.append(item)

        self.response.payload[:] = response

# ################################################################################################################################
# ################################################################################################################################

class GetGDMessageList(AdminService):
    """ Returns all GD messages currently in a topic that have not been moved to subscriber queues yet.
    """
    _filter_by = PubSubMessage.data_prefix,

    class SimpleIO(GetListAdminSIO):
        input_required = 'topic_id'
        input_optional = GetListAdminSIO.input_optional + ('cluster_id', 'has_gd')
        output_required = (AsIs('msg_id'), 'pub_time', 'data_prefix_short', 'pub_pattern_matched')
        output_optional = (AsIs('correl_id'), 'in_reply_to', 'size', 'service_id', 'security_id', 'ws_channel_id',
            'service_name', 'sec_name', 'ws_channel_name', 'endpoint_id', 'endpoint_name', 'server_pid', 'server_name')
        output_repeated = True

# ################################################################################################################################

    def get_gd_data(self, session:'SASession') -> 'anylist':

        # Local aliases
        cluster_id = self.request.input.get('cluster_id') or self.server.cluster_id

        return self._search(
            pubsub_messages_for_topic, session, cluster_id, self.request.input.topic_id, False)

# ################################################################################################################################

    def handle(self) -> 'None':

        # Response to produce ..
        out = []

        # .. collect the data ..
        with closing(self.odb.session()) as session:
            data = self.get_gd_data(session)

        # .. use ISO timestamps ..
        for item in data:

            # .. work with dicts ..
            item = item._asdict()

            # .. convert to ISO ..
            pub_time = datetime_from_ms(item['pub_time'] * 1000.0)
            ext_pub_time = datetime_from_ms(item['ext_pub_time'] * 1000.0) if item['ext_pub_time'] else ''

            # .. assign it back ..
            item['pub_time'] = pub_time
            item['ext_pub_time'] = ext_pub_time

            # .. and add it to our response ..
            out.append(item)

        # .. which we can return now.
        self.response.payload[:] = out

# ################################################################################################################################
# ################################################################################################################################

class GetNonGDMessageList(NonGDSearchService):
    """ Returns all non-GD messages currently in a topic that have not been moved to subscriber queues yet.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'topic_id')
        input_optional = (Bool('paginate'), Int('cur_page'), 'query')
        output_required = (AsIs('_meta'),)
        output_optional = (AsIs('response'),)
        response_elem = None

# ################################################################################################################################

    def handle(self) -> 'None':

        # Local aliases
        topic_id = self.request.input.topic_id

        # Collects responses from all server processes
        reply = self.server.rpc.invoke_all('zato.pubsub.topic.get-server-message-list', {
            'topic_id': topic_id,
            'query': self.request.input.query,
        }, timeout=30)

        # Use a util function to produce a paginated response
        self.set_non_gd_msg_list_response(reply.data, self.request.input.cur_page)

# ################################################################################################################################
# ################################################################################################################################

class GetServerMessageList(AdminService):
    """ Returns a list of in-RAM messages matching input criteria from current server process.
    """
    class SimpleIO(AdminSIO):
        input_required = ('topic_id',)
        input_optional = ('cur_page', 'query', 'paginate')
        output_optional = (Opaque('data'),)

# ################################################################################################################################

    def handle(self) -> 'None':
        self.response.payload.data = self.pubsub.sync_backlog.get_messages_by_topic_id(
            self.request.input.topic_id, True, self.request.input.query)

# ################################################################################################################################
# ################################################################################################################################

class GetInRAMMessageList(AdminService):
    """ Returns all in-RAM messages matching input sub_keys. Messages, if there were any, are deleted from RAM.
    """
    class SimpleIO:
        input_required = List('sub_key_list')
        output_optional = List('messages')

    def handle(self) -> 'None':

        out = []
        topic_sub_keys = {}

        with closing(self.odb.session()) as session:
            for topic_id, sub_key in get_topics_by_sub_keys(session, self.server.cluster_id, self.request.input.sub_key_list):
                sub_keys = topic_sub_keys.setdefault(topic_id, [])
                sub_keys.append(sub_key)

        for topic_id, sub_keys in topic_sub_keys.items():

            # This is a dictionary of sub_key -> msg_id -> message data ..
            data = self.pubsub.sync_backlog.retrieve_messages_by_sub_keys(
                cast_('int', topic_id),
                cast_('strlist', sub_keys)
            )

            # .. which is why we can extend out directly - sub_keys are always unique
            out.extend(data)

        self.response.payload.messages = out

# ################################################################################################################################
# ################################################################################################################################

class GetNonGDDepth(AdminService):
    """ Returns depth of non-GD messages in the input topic on current server.
    """
    class SimpleIO:
        input_required = ('topic_name',)
        output_optional = (Int('depth'),)
        response_elem = None

    def handle(self) -> 'None':
        self.response.payload.depth = self.pubsub.get_non_gd_topic_depth(self.request.input.topic_name)

# ################################################################################################################################
# ################################################################################################################################

class CollectNonGDDepth(AdminService):
    """ Checks depth of non-GD messages for the input topic on all servers and returns a combined tally.
    """
    class SimpleIO:
        input_required = ('topic_name',)
        output_optional = (Int('current_depth_non_gd'),)

    def handle(self) -> 'None':

        reply = self.server.rpc.invoke_all('zato.pubsub.topic.get-non-gd-depth', {
            'topic_name':self.request.input.topic_name
            }, timeout=10)

        total = 0

        for response in reply.data:
            total += response['depth']

        self.response.payload.current_depth_non_gd = total

# ################################################################################################################################
# ################################################################################################################################

class GetTopicMetadata(AdminService):

    def handle(self) -> 'None':

        # All the topic IDs we need to find our in-RAM metadata for
        topic_id_list = self.request.raw_request['topic_id_list']

        # Construct keys to look up topic metadata for ..
        topic_key_list = (
            _format_meta_topic_key(self.server.cluster_id, topic_id) for topic_id in topic_id_list
        )

        # .. look up keys in RAM ..
        result = self.server.pub_sub_metadata.get_many(topic_key_list)

        self.logger.info('Returning topic metadata -> %s', result)

        if result:
            self.response.payload = result

# ################################################################################################################################
# ################################################################################################################################
