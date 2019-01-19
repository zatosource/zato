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

class _PubSubDict(object):
    def __init__(self):
        self.key = None
        self.key_len = None
        self.id_list = None

# ################################################################################################################################

class _DictSubscriptionsBySubKey(_PubSubDict):
    pass

# ################################################################################################################################

class _DictSubscriptionsByTopic(_PubSubDict):
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

'''
class _DictView(_Index):
    method_allowed = 'GET'
    service_name = 'pubsub.task.main.get-dict'
    output_class = _PubSubDict
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'server_name', 'server_pid'
        output_required = 'key', 'data'
        output_repeated = True

    def handle(self):
        return {
            'cluster_id': self.input.cluster_id,
            'server_name': self.input.server_name,
            'server_pid': self.input.server_pid,
            'len_data': len(self.items),
        }

# ################################################################################################################################

class _BaseSubscription(_DictView):

    def on_before_append_item(self, item):

        data = item.data
        data = data if isinstance(data, list) else [data]

        for elem in data:
            elem.id = fs_safe_name(elem.sub_key)
            elem.creation_time_utc = datetime_from_ms(elem.creation_time)
            elem.creation_time = from_utc_to_user(elem.creation_time_utc+'+00:00', self.req.zato.user_profile)

        print()
        print()

        print(111, data)

        print()
        print()

        return data

# ################################################################################################################################
'''

class SubscriptionsByTopic(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-task-main-dict-subscriptions-by-topic'
    template = 'zato/pubsub/task/main/dict/subscriptions-by-topic.html'
    service_name = 'pubsub.task.main.get-dict-keys'
    output_class = _DictSubscriptionsByTopic
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'server_name', 'server_pid'
        output_required = 'key', 'key_len', 'id_list'
        output_repeated = True

    def handle(self):
        return {
            'server_name': self.input.server_name,
            'server_pid': self.input.server_pid,
        }

    def get_initial_input(self):
        return {
            'dict_name': 'subscriptions_by_topic',
            'sort_by': ['topic_name', 'creation_time', 'sub_key']
        }

'''
# ################################################################################################################################

class SubscriptionsBySubKey(_BaseSubscription):
    url_name = 'pubsub-task-main-dict-subscriptions-by-sub-key'
    template = 'zato/pubsub/task/main/dict/subscriptions-by-sub-key.html'

    def get_initial_input(self):
        return {
            'dict_name': 'subscriptions_by_sub_key',
            'sort_by': ['topic_name', 'creation_time', 'sub_key']
        }

# ################################################################################################################################
'''
