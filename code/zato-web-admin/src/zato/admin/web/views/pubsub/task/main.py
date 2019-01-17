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
        self.data = None

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

class SubscriptionsByTopic(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-task-main-dict-subscriptions-by-topic'
    template = 'zato/pubsub/task/main/dict/subscriptions-by-topic.html'
    service_name = 'pubsub.task.main.get-dict'
    output_class = _PubSubDict
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'dict_name', 'server_name', 'server_pid'
        output_required = 'key', 'data'
        output_repeated = True

    def get_initial_input(self):
        return {
            'key': self.input.dict_name,
            'sort_by': ['topic_name', 'creation_time', 'sub_key']
        }

    def handle(self):
        return {
            'cluster_id': self.input.cluster_id,
            'server_name': self.input.server_name,
            'server_pid': self.input.server_pid,
        }

    def on_before_append_item(self, item):
        data = item.data

        for elem in data:
            elem.id = fs_safe_name(elem.sub_key)
            elem.creation_time_utc = datetime_from_ms(elem.creation_time)
            elem.creation_time = from_utc_to_user(elem.creation_time_utc+'+00:00', self.req.zato.user_profile)

        return data

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
    name = 'pubsub.task.main.get-dict'

    class SimpleIO:
        input_required = 'dict_name', List('sort_by')
        output_optional = 'key', 'data'
        output_repeated = True

    _keys_allowed = 'subscriptions_by_topic', 'subscriptions_by_sub_key', 'sub_key_servers', 'endpoints', 'topics', \
        'sec_id_to_endpoint_id', 'ws_channel_id_to_endpoint_id', 'service_id_to_endpoint_id', 'topic_name_to_id', \
        'pubsub_tool_by_sub_key', 'pubsub_tools', 'endpoint_msg_counter'

    def handle(self):
        if self.request.input.dict_name not in self._keys_allowed:
            raise BadRequest(self.cid, 'Invalid value `{}`'.format(self.request.input.dict_name))

        attr = getattr(self.pubsub, self.request.input.dict_name)
        out = []

        for key, data in attr.items():
            if data and isinstance(data[0], ToDictBase):
                data = [elem.to_dict() for elem in data]
                data.sort(key=itemgetter(*self.request.input.sort_by))

            out.append({
                'key': key,
                'data': data
            })

        self.response.payload[:] = sorted(out, key=itemgetter('key'))

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
