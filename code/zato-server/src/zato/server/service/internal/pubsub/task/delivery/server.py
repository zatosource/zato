# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing

# Bunch
from bunch import bunchify

# Zato
from zato.common.odb.model import PubSubSubscription, Server, WebSocketClient, WebSocketClientPubSubKeys, WebSocketSubscription
from zato.common.util.time_ import datetime_from_ms
from zato.server.service import Int
from zato.server.service.internal import AdminService, GetListAdminSIO

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session
    from zato.common.typing_ import any_, anylist, anyset, anytuple
    any_ = any_
    anyset = anyset

# ################################################################################################################################
# ################################################################################################################################

_summary_delivery_server_sio = ('tasks', 'tasks_running', 'tasks_stopped', 'sub_keys', 'topics',
    'messages', 'messages_gd', 'messages_non_gd', Int('msg_handler_counter'), 'last_gd_run', 'last_task_run') # type: anytuple

# ################################################################################################################################
# ################################################################################################################################

def delivery_server_list(session:'Session', cluster_id:'int') -> 'anytuple':
    """ Returns a list of all servers (without PIDs) that are known to be delivery ones.
    """
    # WSX subscriptions first
    q_wsx = session.query(
        Server.id,
        Server.name,
        PubSubSubscription.sub_key
        ).\
        filter(PubSubSubscription.sub_key==WebSocketClientPubSubKeys.sub_key).\
        filter(WebSocketSubscription.sub_key==WebSocketClientPubSubKeys.sub_key).\
        filter(WebSocketClientPubSubKeys.client_id==WebSocketClient.id).\
        filter(WebSocketClient.server_id==Server.id).\
        filter(Server.cluster_id==cluster_id) # type: ignore

    # Non-WSX subscriptions now
    q_non_wsx = session.query(
        Server.id,
        Server.name,
        PubSubSubscription.sub_key
        )

    q_non_wsx = q_non_wsx.filter(Server.id==PubSubSubscription.server_id) # type: ignore
    q_non_wsx = q_non_wsx.filter(Server.cluster_id==cluster_id)           # type: ignore

    # Return a union of WSX and non-WSX related subscription servers
    return q_wsx.union(q_non_wsx).\
           all() # type: ignore

# ################################################################################################################################

class GetDetails(AdminService):
    """ Returns a summary of current activity for all delivery tasks on current PID (non-WSX clients only).
    """
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
        topics_seen = set() # type: anyset

        max_last_gd_run = 0
        max_last_task_run = 0

        for item in self.pubsub.pubsub_tools:

            total_tasks += len(item.delivery_tasks)
            total_sub_keys += len(item.sub_keys)

            item_last_gd_run = item.last_gd_run
            item_last_gd_run_values = item_last_gd_run.values() if item_last_gd_run else [] # type: any_
            max_item_last_gd_run = max(item_last_gd_run_values) if item_last_gd_run_values else 0 # type: int
            max_last_gd_run = max(max_last_gd_run, max_item_last_gd_run)

            for task in item.get_delivery_tasks():

                max_last_task_run = max(max_last_task_run, task.last_iter_run)
                topics_seen.add(task.topic_name)

                if task.is_running():
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

        if max_last_gd_run:
            max_last_gd_run = datetime_from_ms(max_last_gd_run * 1000)

        if max_last_task_run:
            max_last_task_run = datetime_from_ms(max_last_task_run * 1000)

        self.response.payload.last_gd_run = max_last_gd_run or ''
        self.response.payload.last_task_run = max_last_task_run or ''

# ################################################################################################################################

class GetList(AdminService):
    """ Returns all delivery servers defined for cluster.
    """
    class SimpleIO(GetListAdminSIO):
        input_required = ('cluster_id',)
        output_required = ('name', 'pid')
        output_optional = _summary_delivery_server_sio
        output_repeated = True
        output_elem = None

    def get_data(self) -> 'anylist':

        # Response to produce
        out = [] # type: anylist

        # All PIDs of all servers
        server_pids = {}

        with closing(self.odb.session()) as session:

            # Iterate over all servers and their sub_keys as they are known in ODB
            for _ignored_server_id, server_name, sub_key in delivery_server_list(session, self.request.input.cluster_id):

                # All PIDs of current server
                pids = server_pids.setdefault(server_name, set()) # type: anyset

                # Add a PID found for that server
                if sk_server := self.pubsub.get_sub_key_server(sub_key):
                    pids.add(sk_server.server_pid)

        # We can now iterate over the PIDs found and append an output row for each one.
        for server_name, pids in server_pids.items():

            for pid in pids:

                invoker = self.server.rpc.get_invoker_by_server_name(server_name)
                pid_response = bunchify(invoker.invoke(GetDetails.get_name(), pid=pid))

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
                    'msg_handler_counter': pid_response.get('msg_handler_counter'),
                    'last_gd_run': pid_response.last_gd_run,
                    'last_task_run': pid_response.last_task_run,
                })

                # OK, we can append data about this PID now
                out.append(pid_data)

        return out

    def handle(self):
        self.response.payload[:] = self.get_data()

# ################################################################################################################################
