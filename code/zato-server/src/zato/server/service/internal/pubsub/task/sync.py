# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from operator import itemgetter

# Zato
from zato.common.exception import BadRequest
from zato.common.json_internal import dumps
from zato.common.pubsub import all_dict_keys, pubsub_main_data
from zato.server.service import AsIs, Int, List
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

len_keys = 'subscriptions_by_topic', 'subscriptions_by_sub_key', 'sub_key_servers', \
    'pubsub_tool_by_sub_key', 'pubsub_tools'

# ################################################################################################################################

class _TaskSyncGetServerListSIO(AdminSIO):
    output_optional = pubsub_main_data
    skip_empty_keys = True

# ################################################################################################################################

class GetServerList(AdminService):
    """ Per-server implementation of TaskMainGetList.
    """
    SimpleIO = _TaskSyncGetServerListSIO

    def handle(self):
        out = {
            'cluster_id': self.server.cluster_id,
            'server_name': self.server.name,
            'server_pid': self.server.pid,
            'server_api_address': '{}:{}'.format(self.server.preferred_address, self.server.port),
            'msg_pub_counter': self.pubsub.msg_pub_counter,
            'has_meta_endpoint': self.pubsub.has_meta_endpoint,
            'endpoint_meta_store_frequency': self.pubsub.endpoint_meta_store_frequency,
            'endpoint_meta_data_len': self.pubsub.endpoint_meta_data_len,
            'endpoint_meta_max_history': self.pubsub.endpoint_meta_max_history,
            'data_prefix_len': self.pubsub.data_prefix_len,
            'data_prefix_short_len': self.pubsub.data_prefix_short_len,
            'endpoints': self.pubsub.endpoint_api.endpoints,
            'sec_id_to_endpoint_id': self.pubsub.endpoint_api.sec_id_to_endpoint_id,
            'ws_channel_id_to_endpoint_id': self.pubsub.endpoint_api.ws_channel_id_to_endpoint_id,
            'service_id_to_endpoint_id': self.pubsub.endpoint_api.service_id_to_endpoint_id,
            'topics': self.pubsub.topic_api.topics,
        }

        for key in len_keys:
            attr = getattr(self.pubsub, key)
            out[key] = len(attr)

        self.response.payload = out

# ################################################################################################################################

class GetDict(AdminService):
    """ Returns a list of dictionaries keyed by attributes of PubSub, i.e. the input dictionary's name
    must be an attribute of PubSub.
    """
    class SimpleIO(GetListAdminSIO):
        input_required = 'dict_name',
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

class GetDictKeys(GetDict):
    """ Returns keys from the input PubSub dictionary.
    """
    class SimpleIO(GetDict.SimpleIO):
        output_optional = 'key', Int('key_len'), List('id_list'), 'is_list'

    def _handle_attr_call(self, attr):
        out = []
        for key, values in attr.items():
            if isinstance(values, list):
                is_list = True
            else:
                is_list = False
                values = values or []
                values = values if isinstance(values, list) else [values]
            out.append({
                'key': key,
                'key_len': len(values),
                'id_list': sorted([elem.get_id() for elem in values]),
                'is_list': is_list,
            })

        self.response.payload[:] = sorted(out, key=itemgetter('key'))

# ################################################################################################################################

class GetDictValues(GetDict):
    """ Returns values from the input PubSub dictionary.
    """
    class SimpleIO(GetDict.SimpleIO):
        input_required = GetDict.SimpleIO.input_required + ('key', List('sort_by'))
        output_optional = all_dict_keys

    def _handle_attr_call(self, attr):

        key = self.request.input.key

        try:

            # This may be potentially an integer key that we received as string
            # so we need to try to convert it to one.
            try:
                key = int(key)
            except ValueError:
                pass # That is fine, it was not an integer

            values = attr[key]
        except KeyError:
            raise KeyError('No such key `{}` ({}) among `{}`'.format(key, type(key), sorted(attr.keys())))

        values = values if isinstance(values, list) else [values]
        out = [elem.to_dict() for elem in values]
        out.sort(key=itemgetter(*self.request.input.sort_by), reverse=True)

        for item in out:
            for key, value in item.items():
                if isinstance(value, datetime):
                    item[key] = value.isoformat()

        self.response.payload = dumps(out)

# ################################################################################################################################

class GetList(AdminService):
    """ Returns basic information about all the main PubSub objects of each server from the input cluster.
    """
    class SimpleIO(_TaskSyncGetServerListSIO, GetListAdminSIO):
        input_required = 'cluster_id'
        output_repeated = True

    def get_data(self):
        reply = self.server.rpc.invoke_all(GetServerList.get_name(), timeout=10)
        return reply.data

    def handle(self):
        self.response.payload[:] = self.get_data()

# ################################################################################################################################

class _GetEventList(AdminService):
    """ Returns a list of events for a particular topic.
    """
    class SimpleIO(GetListAdminSIO):
        input_required = 'cluster_id', 'server_name', 'server_pid'
        input_optional = GetListAdminSIO.input_optional + ('topic_name',)
        output_required = AsIs('log_id'), AsIs('event_id'), 'name', 'timestamp'
        output_optional = 'ctx'
        output_repeated = True
        response_elem = None

# ################################################################################################################################

class GetServerEventList(_GetEventList):
    """ Returns a list of events for a particular topic. Must be invoked on the same server the data is to be returned from.
    """
    def handle(self):

        # We always return PubSub's events ..
        event_list = self.pubsub.get_event_list()

        # .. and if requested, topic events are also included.
        if self.request.input.topic_name:
            topic_event_list = self.pubsub.get_topic_event_list(self.request.input.topic_name)
            event_list.extend(topic_event_list)

        # Sort the events if there are any to be returned
        if event_list:
            event_list.sort(key=itemgetter('timestamp', 'log_id', 'event_id'), reverse=True)

        self.response.payload[:] = event_list

# ################################################################################################################################

class GetEventList(_GetEventList):
    """ Returns a list of events for a particular topic. Must be invoked on the same server the data is to be returned from.
    """
    def handle(self):
        invoker = self.server.rpc.get_invoker_by_server_name(self.request.input.server_name)
        response = invoker.invoke(GetServerEventList.get_name(), self.request.input, pid=self.request.input.server_pid)
        self.response.payload[:] = response

# ################################################################################################################################
