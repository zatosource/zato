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

'''
# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# Bunch
from bunch import bunchify

# Zato
from zato.common.pubsub import pubsub_main_data
from zato.common.util.time_ import datetime_from_ms
from zato.server.service import AsIs, Int
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

'''
'server_name', 'server_pid', 'server_api_address', 'keep_running', 'subscriptions_by_topic', \
    'subscriptions_by_sub_key', 'sub_key_servers', 'endpoints', 'topics', 'sec_id_to_endpoint_id', \
    'ws_channel_id_to_endpoint_id', 'service_id_to_endpoint_id', 'topic_name_to_id', 'pub_buffer_gd', 'pub_buffer_non_gd', \
    'pubsub_tool_by_sub_key', 'pubsub_tools', 'sync_backlog', 'msg_pub_counter', 'has_meta_endpoint', \
    'endpoint_meta_store_frequency', 'endpoint_meta_data_len', 'endpoint_meta_max_history', 'data_prefix_len', \
    'data_prefix_short_len'
'''

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

        print(999, out)

        return out

    def handle(self):
        self.response.payload[:] = self.get_data()

# ################################################################################################################################

'''
