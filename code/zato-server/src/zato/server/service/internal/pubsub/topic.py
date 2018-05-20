# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from operator import itemgetter

# Zato
from zato.common import PUBSUB as COMMON_PUBSUB, SEARCH
from zato.common.broker_message import PUBSUB as BROKER_MSG_PUBSUB
from zato.common.odb.model import PubSubEndpointEnqueuedMessage, PubSubMessage, PubSubTopic
from zato.common.odb.query import pubsub_messages_for_topic, pubsub_publishers_for_topic, pubsub_topic, pubsub_topic_list
from zato.common.odb.query.pubsub.topic import get_gd_depth_topic, get_topics_by_sub_keys
from zato.common.util import ensure_pubsub_hook_is_valid
from zato.common.util.time_ import datetime_from_ms
from zato.common.util.search import SearchResults
from zato.server.service import AsIs, Bool, Dict, Int, List, Opaque
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################

elem = 'pubsub_topic'
model = PubSubTopic
label = 'a pub/sub topic'
broker_message = BROKER_MSG_PUBSUB
broker_message_prefix = 'TOPIC_'
list_func = pubsub_topic_list
skip_input_params = ['is_internal', 'current_depth_gd', 'last_pub_time', 'last_pub_msg_id', 'last_endpoint_id',
    'last_endpoint_name']
input_optional_extra = ['needs_details']
output_optional_extra = ['is_internal', Int('current_depth_gd'), Int('current_depth_non_gd'), 'last_pub_time',
    'hook_service_name', 'last_pub_time', AsIs('last_pub_msg_id'), 'last_endpoint_id', 'last_endpoint_name']

# ################################################################################################################################

_page_size = SEARCH.ZATO.DEFAULTS.PAGE_SIZE.value

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

def get_last_pub_data(conn, cluster_id, topic_id, _topic_key=COMMON_PUBSUB.REDIS.META_TOPIC_LAST_KEY):
    last_data = conn.hgetall(_topic_key % (cluster_id, topic_id))
    if last_data:
        last_data['pub_time'] = datetime_from_ms(float(last_data['pub_time']) * 1000)
        return last_data

# ################################################################################################################################

def response_hook(self, input, instance, attrs, service_type):
    if service_type == 'get_list':

        # Details are needed when topics are in their own main screen but if only basic information
        # is needed, like a list of topic IDs and names, we don't need to look up additional details.
        # The latter is the case of the message publication screen which simply needs a list of topic IDs/names.
        if input.get('needs_details', True):

            with closing(self.odb.session()) as session:
                for item in self.response.payload:

                    # Checks current non-GD depth on all servers
                    item.current_depth_non_gd = self.invoke('zato.pubsub.topic.collect-non-gd-depth', {
                        'topic_name': item.name,
                    })['response']['current_depth_non_gd']

                    # Checks current GD depth in SQL
                    item.current_depth_gd = get_gd_depth_topic(session, input.cluster_id, item.id)

                    last_data = get_last_pub_data(self.kvdb.conn, self.server.cluster_id, item.id)
                    if last_data:
                        item.last_pub_time = last_data['pub_time']
                        item.last_pub_msg_id = last_data['pub_msg_id']
                        item.last_endpoint_id = last_data['endpoint_id']
                        item.last_endpoint_name = last_data['endpoint_name']

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
            topic = pubsub_topic(session, self.request.input.cluster_id, self.request.input.id)._asdict()
            topic['current_depth_gd'] = get_gd_depth_topic(session, self.request.input.cluster_id, self.request.input.id)

        last_data = get_last_pub_data(self.kvdb.conn, self.server.cluster_id, self.request.input.id)
        topic['last_pub_time'] = last_data['pub_time']

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

class GetGDMessageList(AdminService):
    """ Returns all GD messages currently in a topic that have not been moved to subscriber queues yet.
    """
    _filter_by = PubSubMessage.data_prefix,

    class SimpleIO(GetListAdminSIO):
        input_required = ('cluster_id', 'topic_id')
        input_optional = GetListAdminSIO.input_optional + ('has_gd',)
        output_required = (AsIs('msg_id'), 'pub_time', 'data_prefix_short', 'pattern_matched')
        output_optional = (AsIs('correl_id'), 'in_reply_to', 'size', 'service_id', 'security_id', 'ws_channel_id',
            'service_name', 'sec_name', 'ws_channel_name', 'endpoint_id', 'endpoint_name', 'server_pid', 'server_name')
        output_repeated = True

# ################################################################################################################################

    def get_gd_data(self, session):
        return self._search(
            pubsub_messages_for_topic, session, self.request.input.cluster_id, self.request.input.topic_id, False)

# ################################################################################################################################

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_gd_data(session)

        for item in self.response.payload.zato_output:
            item.pub_time = datetime_from_ms(item.pub_time * 1000.0)
            item.ext_pub_time = datetime_from_ms(item.ext_pub_time * 1000.0) if item.ext_pub_time else ''

# ################################################################################################################################

class GetNonGDMessageList(AdminService):
    """ Returns all non-GD messages currently in a topic that have not been moved to subscriber queues yet.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'topic_id')
        input_optional = (Bool('paginate'), Int('cur_page'), 'query')
        output_required = (AsIs('_meta'),)
        output_optional = (AsIs('response'),)
        response_elem = None

# ################################################################################################################################

    def handle(self, _sort_key=itemgetter('pub_time')):
        # Local aliases
        topic_id = self.request.input.topic_id
        paginate = self.request.input.paginate
        cur_page = self.request.input.cur_page
        cur_page = cur_page - 1 if cur_page else 0 # We index lists from 0

        # Response to produce
        msg_list = []

        # Collects responses from all server processes
        is_all_ok, all_data = self.servers.invoke_all('zato.pubsub.topic.get-server-message-list', {
            'topic_id': topic_id,
            'query': self.request.input.query,
        }, timeout=30)

        # Check if everything is OK on each level - overall, per server and then per process
        if is_all_ok:
            for server_name, server_data in all_data.iteritems():
                if server_data['is_ok']:
                    for server_pid, server_pid_data in server_data['server_data'].iteritems():
                        if server_pid_data['is_ok']:
                            pid_data = server_pid_data['pid_data']['response']['data']
                            msg_list.extend(pid_data)
                        else:
                            self.logger.warn('Caught an error (server_pid_data) %s', server_pid_data['error_info'])
                else:
                    self.logger.warn('Caught an error (server_data) %s', server_data['error_info'])

        else:
            self.logger.warn('Caught an error (all_data) %s', all_data)

        # Set it here because later on it may be shortened to the page_size of elements
        total = len(msg_list)

        # If we get here, we must have collected some data at all
        if msg_list:

            # Sort the output before it is returned - messages last published (youngest) come first
            msg_list.sort(key=_sort_key, reverse=True)

            # If pagination is requsted, return only the desired page
            if paginate:

                start = cur_page * _page_size
                end = start + _page_size

                msg_list = msg_list[start:end]

        for msg in msg_list:
            # Convert float timestamps in all the remaining messages to ISO-8601
            msg['pub_time'] = datetime_from_ms(msg['pub_time'] * 1000.0)
            if msg.get('expiration_time'):
                msg['expiration_time'] = datetime_from_ms(msg['expiration_time'] * 1000.0)

            # Return endpoint information in the same format GD messages are returned in
            msg['endpoint_id'] = msg.pop('published_by_id')
            msg['endpoint_name'] = self.pubsub.get_endpoint_by_id(msg['endpoint_id']).name

        search_results = SearchResults(None, None, None, total)
        search_results.set_data(cur_page, _page_size)

        # Actual data
        self.response.payload.response = msg_list

        # Search metadata
        self.response.payload._meta = search_results.to_dict()

# ################################################################################################################################

class GetServerMessageList(AdminService):
    """ Returns a list of in-RAM messages matching input criteria from current server process.
    """
    class SimpleIO(AdminSIO):
        input_required = ('topic_id',)
        input_optional = ('cur_page', 'query', 'paginate')
        output_optional = (Opaque('data'),)

# ################################################################################################################################

    def handle(self):
        self.response.payload.data = self.pubsub.sync_backlog.get_messages_by_topic_id(
            self.request.input.topic_id, True, self.request.input.query)

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
            data = self.pubsub.sync_backlog.retrieve_messages_by_sub_keys(topic_id, sub_keys)

            # .. which is why we can extend out directly - sub_keys are always unique
            out.update(data)

        self.response.payload.messages = out

# ################################################################################################################################

class GetNonGDDepth(AdminService):
    """ Returns depth of non-GD messages in the input topic on current server.
    """
    class SimpleIO:
        input_required = ('topic_name',)
        output_optional = (Int('depth'),)

    def handle(self):
        self.response.payload.depth = self.pubsub.get_non_gd_topic_depth(self.request.input.topic_name)

# ################################################################################################################################

class CollectNonGDDepth(AdminService):
    """ Checks depth of non-GD messages for the input topic on all servers and returns a combined tally.
    """
    class SimpleIO:
        input_required = ('topic_name',)
        output_optional = (Int('current_depth_non_gd'),)

    def handle(self):

        all_depth = self.servers.invoke_all('zato.pubsub.topic.get-non-gd-depth', {
            'topic_name':self.request.input.topic_name
            }, timeout=10)

        total = 0

        data = all_depth[1]
        for server_name in data:
            if data[server_name]['is_ok']:
                server_data = data[server_name]['server_data']
                for pid in server_data:
                    if server_data[pid]['is_ok']:
                        pid_data = server_data[pid]['pid_data']
                        total += pid_data['response']['depth']

        self.response.payload.current_depth_non_gd = total

# ################################################################################################################################
