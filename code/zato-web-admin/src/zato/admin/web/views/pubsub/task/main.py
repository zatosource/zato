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

    def handle_return_data(self, return_data):

        print()
        print()

        print(111, return_data)

        print()

        print(222, return_data['items'])

        print()
        print()

        return return_data

        '''
        for item in return_data['items']:

            item.id = fs_safe_name('{}-{}'.format(item.name, item.pid))

            if item.last_gd_run:
                item.last_gd_run_utc = item.last_gd_run
                item.last_gd_run = from_utc_to_user(item.last_gd_run_utc + '+00:00', self.req.zato.user_profile)

            if item.last_task_run:
                item.last_task_run_utc = item.last_task_run
                item.last_task_run = from_utc_to_user(item.last_task_run_utc + '+00:00', self.req.zato.user_profile)

        return return_data
    '''

    def handle(self):
        return {}

# ################################################################################################################################
