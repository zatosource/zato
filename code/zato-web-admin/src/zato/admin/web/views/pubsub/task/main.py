# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web import from_utc_to_user
from zato.admin.web.views import Index as _Index
from zato.common.pubsub import pubsub_main_data
from zato.common.util import fs_safe_name
from zato.common.util.time_ import datetime_from_ms

# ################################################################################################################################

logger = logging.getLogger(__name__)

dict_name_to_url_name = {
    'subscriptions_by_topic': 'pubsub-task-main-dict-values-subscription',
    'subscriptions_by_sub_key': 'pubsub-task-main-dict-values-subscription',
    'sub_key_servers': 'pubsub-task-main-dict-values-sks',
    'endpoints': 'pubsub-task-main-dict-values-endpoints',
    'topics': 'pubsub-task-main-dict-values-topics',
    'sec_id_to_endpoint_id': 'pubsub-task-main-dict-values-endpoints',
    'ws_channel_id_to_endpoint_id': 'pubsub-task-main-dict-values-endpoints',
    'service_id_to_endpoint_id': 'pubsub-task-main-dict-values-endpoints',
    'topic_name_to_id': 'pubsub-task-main-dict-values-topics',
    'pubsub_tool_by_sub_key': 'pubsub-task-main-dict-values-pst',
    'pubsub_tools': 'pubsub-task-main-dict-values-pst',
    'endpoint_msg_counter': 'pubsub-task-main-dict-values-messages'
}

dict_name_to_template_name = {
    'subscriptions_by_topic': 'subscription',
    'subscriptions_by_sub_key': 'subscription',
    'sub_key_servers': 'sks',
    'endpoints': 'endpoints',
    'topics': 'topics',
    'sec_id_to_endpoint_id': 'endpoints',
    'ws_channel_id_to_endpoint_id': 'endpoints',
    'service_id_to_endpoint_id': 'endpoints',
    'topic_name_to_id': 'topics',
    'pubsub_tool_by_sub_key': 'pubsub-tools',
    'pubsub_tools': 'pubsub-tools',
    'endpoint_msg_counter': 'messages'
}

# ################################################################################################################################

class PubSubTool(object):
    def __init__(self):
        self.server_name = None
        self.server_pid = None
        self.server_api_address = None
        self.keep_running = None
        self.subscriptions_by_topic = None
        self.subscriptions_by_sub_key = None
        self.sub_key_servers = None
        self.endpoints = None
        self.topics = None
        self.sec_id_to_endpoint_id = None
        self.ws_channel_id_to_endpoint_id = None
        self.service_id_to_endpoint_id = None
        self.topic_name_to_id = None
        self.pub_buffer_gd = None
        self.pub_buffer_non_gd = None
        self.pubsub_tool_by_sub_key = None
        self.pubsub_tools = None
        self.sync_backlog = None
        self.msg_pub_counter = None
        self.has_meta_endpoint = None
        self.endpoint_meta_store_frequency = None
        self.endpoint_meta_data_len = None
        self.endpoint_meta_max_history = None
        self.data_prefix_len = None
        self.data_prefix_short_len = None

    def __repr__(self):
        attrs = {}
        for name in pubsub_main_data:
            value = getattr(self, name)
            if value:
                attrs[name] = value

        return '<{} at {} {}>'.format(self.__class__.__name__, hex(id(self)), attrs)

# ################################################################################################################################

class _PubSubDictKeys(object):
    def __init__(self):
        self.key = None
        self.key_len = None
        self.id_list = None

# ################################################################################################################################

class _SubscriptionDictKeys(_PubSubDictKeys):
    pass

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-task-main'
    template = 'zato/pubsub/task/main/index.html'
    service_name = 'pubsub.task.main.get-list'
    output_class = PubSubTool
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        output_optional = pubsub_main_data
        output_repeated = True

    def handle(self):
        return {}

# ################################################################################################################################

class _SubscriptionDict(_Index):
    method_allowed = 'GET'
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'dict_name', 'server_name', 'server_pid'
        output_repeated = True

    def handle(self):
        return {
            'dict_name': self.input.dict_name,
            'server_name': self.input.server_name,
            'server_pid': self.input.server_pid,
        }

    def get_initial_input(self):
        return {
            'dict_name': self.input.dict_name,
        }

# ################################################################################################################################

class SubscriptionDictKeys(_SubscriptionDict):
    url_name = 'pubsub-task-main-subscription-dict-keys'
    template = 'zato/pubsub/task/main/dict/keys.html'
    service_name = 'pubsub.task.main.get-dict-keys'
    output_class = _SubscriptionDictKeys

    class SimpleIO(_SubscriptionDict.SimpleIO):
        input_optional = 'key_url_name',
        output_required = 'key', 'key_len', 'id_list'

    def handle(self):
        out = super(SubscriptionDictKeys, self).handle()
        out['key_url_name'] = self.input.key_url_name
        out['values_url_name'] = dict_name_to_url_name[self.input.dict_name]
        return out

# ################################################################################################################################

class SubscriptionDictValues(_SubscriptionDict):
    url_name = 'pubsub-task-main-dict-values-subscription'
    service_name = 'pubsub.task.main.get-dict-values'
    output_class = _SubscriptionDictKeys

    class SimpleIO(_SubscriptionDict.SimpleIO):
        input_optional = 'key',
        output_required = 'sub_key',

    def handle(self):
        out = super(SubscriptionDictValues, self).handle()
        out['key'] = self.input.key
        return out

    def get_initial_input(self):
        out = super(SubscriptionDictValues, self).get_initial_input()
        out['sort_by'] = ['topic_name', 'creation_time', 'sub_key']
        return out

    def get_template_name(self):
        pattern = 'zato/pubsub/task/main/dict/values/{}.html'
        name = dict_name_to_template_name[self.input.dict_name]
        return pattern.format(name)

# ################################################################################################################################

'''
# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from operator import itemgetter

# Bunch
from bunch import bunchify

# Zato
from zato.common.exception import BadRequest
from zato.common.pubsub import pubsub_main_data
from zato.common.util.time_ import datetime_from_ms
from zato.server.pubsub import ToDictBase
from zato.server.service import AsIs, Int, List, ListOfDicts
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

len_keys = 'subscriptions_by_topic', 'subscriptions_by_sub_key', 'sub_key_servers', 'endpoints', 'topics', \
    'sec_id_to_endpoint_id', 'ws_channel_id_to_endpoint_id', 'service_id_to_endpoint_id', 'pub_buffer_gd', \
    'pub_buffer_non_gd', 'pubsub_tool_by_sub_key', 'pubsub_tools'

# ################################################################################################################################

class _TaskMainGetServerListSIO(AdminSIO):
    output_optional = pubsub_main_data
    skip_empty_keys = True

# ################################################################################################################################

class TaskMainGetServerList(AdminService):
    """ Per-server implementation of TaskMainGetList.
    """
    name = 'pubsub.task.main.get-server-list'

    SimpleIO = _TaskMainGetServerListSIO

    def handle(self):
        out = {
            'cluster_id': self.server.cluster_id,
            'server_name': self.server.name,
            'server_pid': self.server.pid,
            'server_api_address': '{}:{}'.format(self.server.preferred_address, self.server.port),
            'keep_running': self.pubsub.keep_running,
            'msg_pub_counter': self.pubsub.msg_pub_counter,
            'has_meta_endpoint': self.pubsub.has_meta_endpoint,
            'endpoint_meta_store_frequency': self.pubsub.endpoint_meta_store_frequency,
            'endpoint_meta_data_len': self.pubsub.endpoint_meta_data_len,
            'endpoint_meta_max_history': self.pubsub.endpoint_meta_max_history,
            'data_prefix_len': self.pubsub.data_prefix_len,
            'data_prefix_short_len': self.pubsub.data_prefix_short_len,
        }

        for key in len_keys:
            attr = getattr(self.pubsub, key)
            out[key] = len(attr)

        self.response.payload = out

# ################################################################################################################################

class TaskMainGetDict(AdminService):
    """ Returns a list of dictionaries keyed by attributes of PubSub, i.e. the input dictionary's name
    must be an attribute of PubSub.
    """
    name = '_pubsub.task.main.get-dict'

    class SimpleIO(GetListAdminSIO):
        input_required = 'dict_name'
        output_repeated = True
        skip_empty_keys = True

    _keys_allowed = 'subscriptions_by_topic', 'subscriptions_by_sub_key', 'sub_key_servers', 'endpoints', 'topics', \
        'sec_id_to_endpoint_id', 'ws_channel_id_to_endpoint_id', 'service_id_to_endpoint_id', 'topic_name_to_id', \
        'pubsub_tool_by_sub_key', 'pubsub_tools', 'endpoint_msg_counter'

    def validate_input(self):
        if self.request.input.dict_name not in self._keys_allowed:
            raise BadRequest(self.cid, 'Invalid value `{}`'.format(self.request.input.dict_name))

    def handle(self):
        attr = getattr(self.pubsub, self.request.input.dict_name) # type: dict
        self._handle_attr_call(attr)

    def _handle_attr_call(self, attr):
        raise NotImplementedError()

# ################################################################################################################################

class TaskMainGetDictKeys(TaskMainGetDict):
    """ Returns keys from the input PubSub dictionary.
    """
    name = 'pubsub.task.main.get-dict-keys'

    class SimpleIO(TaskMainGetDict.SimpleIO):
        output_optional = 'key', Int('key_len'), List('id_list')

    def _handle_attr_call(self, attr):

        key_len = 0
        out = []

        for key, values in attr.items():
            values = values or []
            values = values if isinstance(values, list) else [values]
            out.append({
                'key': key,
                'key_len': len(values),
                'id_list': sorted([elem.get_id() for elem in values])
            })

        self.response.payload[:] = sorted(out, key=itemgetter('key'))

# ################################################################################################################################

class TaskMainGetDictValues(TaskMainGetDict):
    """ Returns values from the input PubSub dictionary.
    """
    name = 'pubsub.task.main.get-dict-values'

    class SimpleIO(TaskMainGetDict.SimpleIO):
        output_optional = 'key', Int('key_len'), List('id_list')

    def _handle_attr_call(self, attr):
        self.response.payload[:] = []#attr.values()

# ################################################################################################################################

class TaskMainGetList(AdminService):
    """ Returns basic information about all the main PubSub objects of each server from the input cluster.
    """
    name = 'pubsub.task.main.get-list'

    class SimpleIO(_TaskMainGetServerListSIO, GetListAdminSIO):
        input_required = 'cluster_id'
        output_repeated = True

    def get_data(self):

        # Response to produce
        out = []

        info = self.servers.invoke_all(TaskMainGetServerList.name, timeout=10)
        info = bunchify(info)
        data = info[1]

        for server_name in data:
            server_info = data[server_name]
            if server_info.is_ok:
                server_data = server_info.server_data
                for pid in server_data:
                    pid_info = server_data[pid]
                    if pid_info.is_ok:
                        pid_response = pid_info.pid_data.response
                        out.append(pid_response.toDict())

        return out

    def handle(self):
        self.response.payload[:] = self.get_data()

# ################################################################################################################################
'''
