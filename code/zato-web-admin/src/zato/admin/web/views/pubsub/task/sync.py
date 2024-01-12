# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web import from_utc_to_user
from zato.admin.web.views import Index as _Index
from zato.common.pubsub import all_dict_keys, pubsub_main_data
from zato.common.util.event import Event
from zato.common.util.time_ import datetime_from_ms

# ################################################################################################################################

logger = logging.getLogger(__name__)

dict_name_to_url_name = {
    'subscriptions_by_topic': 'pubsub-task-sync-dict-values-subscriptions',
    'subscriptions_by_sub_key': 'pubsub-task-sync-dict-values-subscriptions',
    'sub_key_servers': 'pubsub-task-sync-dict-values-sks',
    'endpoints': 'pubsub-task-sync-dict-values-endpoints',
    'topics': 'pubsub-task-sync-dict-values-topics',
    'sec_id_to_endpoint_id': 'pubsub-task-sync-dict-values-endpoints',
    'ws_channel_id_to_endpoint_id': 'pubsub-task-sync-dict-values-endpoints',
    'service_id_to_endpoint_id': 'pubsub-task-sync-dict-values-endpoints',
    'topic_name_to_id': 'pubsub-task-sync-dict-values-topics',
    'pubsub_tool_by_sub_key': 'pubsub-task-sync-dict-values-pst',
    'pubsub_tools': 'pubsub-task-sync-dict-values-pst',
    'endpoint_msg_counter': 'pubsub-task-sync-dict-values-messages'
}

dict_name_to_template_name = {
    'subscriptions_by_topic': 'subscriptions',
    'subscriptions_by_sub_key': 'subscriptions',
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

time_keys = 'creation_time', 'last_synced', 'gd_pub_time_max'

# ################################################################################################################################

class PubSubTool:
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

class _SubscriptionDictKeys:
    def __init__(self):
        self.key = None
        self.key_len = None
        self.id_list = None

# ################################################################################################################################

class _DictValuesData:
    pass

# ################################################################################################################################

class _Event:
    pass

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-task-sync'
    template = 'zato/pubsub/task/sync/index.html'
    service_name = 'zato.pubsub.task.sync.get-list'
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
    url_name = 'pubsub-task-sync-subscription-dict-keys'
    template = 'zato/pubsub/task/sync/dict/keys.html'
    service_name = 'zato.pubsub.task.sync.get-dict-keys'
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
    service_name = 'zato.pubsub.task.sync.get-dict-values'
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
        for name in time_keys:
            raw_time_value = getattr(item, name, None)
            if raw_time_value:

                raw_key = '{}_raw'.format(name)
                utc_key = '{}_utc'.format(name)

                if isinstance(raw_time_value, float):
                    float_value = getattr(item, name)
                    float_as_dt = datetime_from_ms(float_value, False)

                    # The float value must have represented seconds rather than seconds
                    # so we need to retry after converting seconds to milliseconds.
                    # Year 2000 can be safely used because it will never be a correct value.
                    if float_as_dt.year < 2000:
                        float_value = float_value * 1000
                        float_as_dt = datetime_from_ms(float_value, False)

                    setattr(item, utc_key, float_as_dt.isoformat())
                else:
                    setattr(item, utc_key, raw_time_value)

                utc_value = getattr(item, utc_key)
                utc_value_user = from_utc_to_user(utc_value+'+00:00', self.req.zato.user_profile)

                setattr(item, raw_key, raw_time_value)
                setattr(item, name, utc_value_user)

        return item

    def get_template_name(self):
        pattern = 'zato/pubsub/task/sync/dict/values/{}.html'
        name = dict_name_to_template_name[self.input.dict_name]
        return pattern.format(name)

# ################################################################################################################################

class DictValuesSubscriptions(DictValues):
    url_name = 'pubsub-task-sync-dict-values-subscriptions'
    _dict_sort_by = ['creation_time']

# ################################################################################################################################

class DictValuesSubKeyServer(DictValues):
    url_name = 'pubsub-task-sync-dict-values-sks'
    _dict_sort_by = ['creation_time']

# ################################################################################################################################

class DictValuesEndpoints(DictValues):
    url_name = 'pubsub-task-sync-dict-values-endpoints'
    _dict_sort_by = ['endpoint_type', 'name']

# ################################################################################################################################

class DictValuesTopics(DictValues):
    url_name = 'pubsub-task-sync-dict-values-topics'
    _dict_sort_by = ['name']

# ################################################################################################################################

class EventList(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-task-event-list'
    template = 'zato/pubsub/task/sync/event/index.html'
    service_name = 'zato.pubsub.task.sync.get-event-list'
    output_class = _Event
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id', 'server_name', 'server_pid'
        output_optional = Event.__slots__
        output_repeated = True

    def handle(self):
        return {}

# ################################################################################################################################
