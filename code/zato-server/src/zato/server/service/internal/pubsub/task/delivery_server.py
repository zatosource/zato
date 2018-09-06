# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# Bunch
from bunch import bunchify

# Zato
from zato.common.odb.model import ChannelWebSocket, PubSubSubscription, Server, WebSocketClient, WebSocketClientPubSubKeys, \
     WebSocketSubscription
from zato.server.service import AsIs
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################

_summary_delivery_server_sio = ('tasks', 'tasks_running', 'tasks_stopped', 'sub_keys', 'topics',
    'messages', 'messages_gd', 'messages_non_gd', 'last_sync', 'last_delivery')

# ################################################################################################################################

def delivery_server_list_non_wsx(session, cluster_id):
    """ Returns a list of all servers (without PIDs) that are known to be delivery ones.
    """
    return session.query(
        Server.id,
        Server.name,
        PubSubSubscription.sub_key
        ).\
        filter(Server.id==PubSubSubscription.server_id).\
        filter(Server.cluster_id==cluster_id).\
        all()

# ################################################################################################################################

class GetDeliveryServerDetailsNonWSX(AdminService):
    """ Returns a summary of current activity for all delivery tasks on current PID (non-WSX clients only).
    """
    name = 'pubsub.task.get-delivery-server-details-non-wsx'

    class SimpleIO:
        output_optional = _summary_delivery_server_sio
        response_elem = None

    def handle(self):

        total_tasks = 0
        tasks_running = 0
        tasks_stopped = 0

        total_messages = 0
        messages_gd = 0
        messages_non_gd = 0

        total_sub_keys = 0
        topics_seen = set()

        max_last_sync = ''
        max_last_delivery = ''

        for item in self.pubsub.pubsub_tools:
            total_tasks += len(item.delivery_tasks)
            total_sub_keys += len(item.sub_keys)

            for task in item.get_delivery_tasks():
                topics_seen.add(task.topic_name)

                if task.keep_running:
                    tasks_running += 1
                else:
                    tasks_stopped += 1

                gd_depth, non_gd_depth = task.get_queue_depth()

                total_messages += gd_depth
                total_messages += non_gd_depth

                messages_gd += gd_depth
                messages_non_gd += non_gd_depth

        self.response.payload.tasks = total_tasks
        self.response.payload.tasks_running = tasks_running
        self.response.payload.tasks_stopped = tasks_stopped

        self.response.payload.messages = total_messages
        self.response.payload.messages_gd = messages_gd
        self.response.payload.messages_non_gd = messages_non_gd

        self.response.payload.topics = len(topics_seen)
        self.response.payload.sub_keys = total_sub_keys

        self.response.payload.last_sync = max_last_sync
        self.response.payload.last_delivery = max_last_delivery

# ################################################################################################################################

class DeliveryServerGetList(AdminService):
    """ Returns all delivery servers defined for cluster.
    """
    name = 'pubsub.task.delivery-server.get-list'

    class SimpleIO(GetListAdminSIO):
        input_required = ('cluster_id',)
        output_required = ('name', 'pid')
        output_optional = _summary_delivery_server_sio
        output_repeated = True
        output_elem = None

    def get_data(self):

        # Response to produce
        out = []

        # All PIDs of all servers
        server_pids = {}

        with closing(self.odb.session()) as session:

            # Iterate over all servers and their sub_keys as they are known in ODB
            for server_id, server_name, sub_key in delivery_server_list_non_wsx(session, self.request.input.cluster_id):

                # All PIDs of current server
                pids = server_pids.setdefault(server_name, set())

                # Add a PID found for that server
                pids.add(self.pubsub.get_sub_key_server(sub_key).server_pid)

            # We can now iterate over the PIDs found and append an output row for each one.
            for server_name, pids in server_pids.items():

                for pid in pids:

                    pid_response = bunchify(self.servers[server_name].invoke(GetDeliveryServerDetailsNonWSX.name, pid=pid))

                    # A summary of each PID's current pub/sub activities
                    pid_data = bunchify({
                        'name': server_name,
                        'pid': pid,
                        'tasks': pid_response.tasks,
                        'tasks_running': pid_response.tasks_running,
                        'tasks_stopped': pid_response.tasks_stopped,
                        'sub_keys': pid_response.sub_keys,
                        'topics': pid_response.topics,
                        'messages': pid_response.messages,
                        'messages_gd': pid_response.messages_gd,
                        'messages_non_gd': pid_response.messages_non_gd,
                        'last_sync': pid_response.last_sync,
                        'last_delivery': pid_response.last_delivery,
                    })

                # OK, we can append data about this PID now
                out.append(pid_data)

            return out

    def handle(self):
        self.response.payload[:] = self.get_data()

# ################################################################################################################################

class DeliveryTaskGetList(AdminService):
    """ Returns all delivery servers defined for cluster.
    """
    name = 'pubsub.task.get-list'

    class SimpleIO(GetListAdminSIO):
        input_required = ('cluster_id',)
        output_required = ('server_name', 'server_pid', AsIs('thread_id'), AsIs('object_id'),
            'sub_key', 'topic_id', 'topic_name', 'messages')
        output_optional = ('last_sync', 'last_delivery', AsIs('ext_client_id'))
        output_repeated = True
        output_elem = None

    def get_data(self):
        return [
            {'server_name':'ZZZ', 'server_pid':'1101',
             'thread_id':'DummyThread-183', 'object_id':'0x7f4ca83e68c0',
             'sub_key':'zpsk.wsx.32a358b555a4d2ec0f06b1cb', 'topic_id':1, 'topic_name':'/my/topic',
             'messages':39,
             'last_sync':'2018-09-03T10:49:00.431767', 'last_delivery':'2018-09-03T10:49:00.97212'
             },

            {'server_name':'QQQ', 'server_pid':'2341',
             'thread_id':'DummyThread-184', 'object_id':'0x7f4ca8380690',
             'sub_key':'zpsk.rest.bcb442f15ba7fa0765aa7d62', 'topic_id':1, 'topic_name':'/my/topic/2',
             'messages':1982,
             'last_sync':'2018-08-21T15:17:07.014784', 'last_delivery':'2018-08-30T11:19:45.09732',
             'ext_client_id':'RUID-3971'},
        ]

    def handle(self):
        self.response.payload[:] = self.get_data()

# ################################################################################################################################
