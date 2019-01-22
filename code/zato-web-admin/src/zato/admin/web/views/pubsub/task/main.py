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
from zato.common.pubsub import all_dict_keys, pubsub_main_data
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
    'endpoints': 'endpoint',
    'topics': 'topics',
    'sec_id_to_endpoint_id': 'endpoint',
    'ws_channel_id_to_endpoint_id': 'endpoint',
    'service_id_to_endpoint_id': 'endpoint',
    'topic_name_to_id': 'topic',
    'pubsub_tool_by_sub_key': 'pubsub-tool',
    'pubsub_tools': 'pubsub-tool',
    'endpoint_msg_counter': 'message'
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

class _SubscriptionDictKeys(object):
    def __init__(self):
        self.key = None
        self.key_len = None
        self.id_list = None

# ################################################################################################################################

class _DictValuesData(object):
    pass

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-task-main'
    template = 'zato/pubsub/task/main/index.html'
    service_name = 'zato.pubsub.task.main.get-list'
    output_class = PubSubTool
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        output_optional = pubsub_main_data
        output_repeated = True

    def handle(self):
        return {}

# ################################################################################################################################

class _DictView(_Index):
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

class SubscriptionDictKeys(_DictView):
    url_name = 'pubsub-task-main-subscription-dict-keys'
    template = 'zato/pubsub/task/main/dict/keys.html'
    service_name = 'zato.pubsub.task.main.get-dict-keys'
    output_class = _SubscriptionDictKeys

    class SimpleIO(_DictView.SimpleIO):
        input_optional = 'key_url_name',
        output_required = 'key', 'key_len', 'id_list', 'is_list'

    def handle(self):
        out = super(SubscriptionDictKeys, self).handle()
        out['key_url_name'] = self.input.key_url_name
        out['values_url_name'] = dict_name_to_url_name[self.input.dict_name]
        return out

# ################################################################################################################################

class DictValues(_DictView):
    service_name = 'zato.pubsub.task.main.get-dict-values'
    output_class = _DictValuesData
    _dict_sort_by = None

    class SimpleIO(_DictView.SimpleIO):
        input_optional = 'key',
        output_optional = all_dict_keys

    def handle(self):
        out = super(DictValues, self).handle()
        out['key'] = self.input.key
        return out

    def get_initial_input(self):
        out = super(DictValues, self).get_initial_input()
        if self._dict_sort_by:
            out['sort_by'] = self._dict_sort_by
        return out

    def on_before_append_item(self, item):
        creation_time = getattr(item, 'creation_time', None)
        if creation_time:
            if isinstance(creation_time, float):
                item.creation_time_utc = datetime_from_ms(item.creation_time)
            else:
                item.creation_time_utc = creation_time
            item.creation_time = from_utc_to_user(item.creation_time_utc+'+00:00', self.req.zato.user_profile)
        return item

    def get_template_name(self):
        pattern = 'zato/pubsub/task/main/dict/values/{}.html'
        name = dict_name_to_template_name[self.input.dict_name]
        return pattern.format(name)

# ################################################################################################################################

class DictValuesSubscription(DictValues):
    url_name = 'pubsub-task-main-dict-values-subscription'
    _dict_sort_by = ['creation_time']

# ################################################################################################################################

class DictValuesSubKeyServer(DictValues):
    url_name = 'pubsub-task-main-dict-values-sks'
    _dict_sort_by = ['creation_time']

# ################################################################################################################################

class DictValuesEndpoints(DictValues):
    url_name = 'pubsub-task-main-dict-values-endpoints'
    _dict_sort_by = ['endpoint_type', 'name']

# ################################################################################################################################
