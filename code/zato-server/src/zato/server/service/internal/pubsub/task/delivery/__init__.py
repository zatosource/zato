# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from operator import itemgetter

# Zato
from zato.common.util.time_ import datetime_from_ms
from zato.server.service import AsIs, Int
from zato.server.service.internal import AdminService, GetListAdminSIO

# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, anytuple
    from zato.server.pubsub.delivery.task import DeliveryTask
    from zato.server.pubsub.delivery.tool import PubSubTool
    anytuple = anytuple
    DeliveryTask = DeliveryTask
    PubSubTool = PubSubTool

# ################################################################################################################################

class GetTaskSIO:
    output_required = ('server_name', 'server_pid', 'sub_key', 'topic_id', 'topic_name', 'is_active',
        'endpoint_id', 'endpoint_name', 'py_object', AsIs('python_id'), Int('len_messages'), Int('len_history'), Int('len_batches'),
        Int('len_delivered')) # type: anytuple
    output_optional = 'last_sync', 'last_sync_sk', 'last_iter_run', AsIs('ext_client_id') # type: anytuple
    output_elem = None
    response_elem = None

# ################################################################################################################################
# ################################################################################################################################

class GetServerDeliveryTaskList(AdminService):
    """ Returns all delivery tasks for a particular server process (must be invoked on the required one).
    """
    class SimpleIO(GetTaskSIO):
        output_repeated = True

    def get_data(self) -> 'anylist':

        out = [] # type: anylist

        for ps_tool in self.pubsub.pubsub_tools: # type: PubSubTool
            with ps_tool.lock:
                for _ignored_sub_key, task in ps_tool.delivery_tasks.items(): # type: (str, DeliveryTask)

                    last_sync = task.last_iter_run # ps_tool.last_gd_run
                    if last_sync:
                        last_sync = datetime_from_ms(last_sync * 1000)

                    if sub := self.pubsub.get_subscription_by_sub_key(task.sub_key):
                        endpoint_id = sub.endpoint_id
                        endpoint = self.pubsub.get_endpoint_by_id(endpoint_id)

                        out.append({
                            'server_name': ps_tool.server_name,
                            'server_pid': ps_tool.server_pid,
                            'endpoint_id': endpoint.id,
                            'endpoint_name': endpoint.name,
                            'py_object': task.py_object,
                            'python_id': task.python_id,
                            'sub_key': task.sub_key,
                            'topic_id': self.pubsub.get_topic_id_by_name(task.topic_name),
                            'topic_name': task.topic_name,
                            'is_active': task.keep_running,
                            'len_messages': len(task.delivery_list),
                            'len_history': len(task.delivery_list),
                            'last_sync': last_sync,
                            'last_iter_run': datetime_from_ms(task.last_iter_run * 1000),
                            'len_batches': task.len_batches,
                            'len_delivered': task.len_delivered,
                        })

        # Return the list of tasks sorted by sub_keys and their Python names
        return sorted(out, key=itemgetter('sub_key', 'py_object'))

    def handle(self):
        self.response.payload[:] = self.get_data()

# ################################################################################################################################
# ################################################################################################################################

class GetDeliveryTaskList(AdminService):
    """ Returns all delivery tasks for a particular server process (possibly a remote one).
    """
    class SimpleIO(GetListAdminSIO, GetTaskSIO):
        input_required = 'cluster_id', 'server_name', 'server_pid'

    def handle(self):

        invoker = self.server.rpc.get_invoker_by_server_name(self.request.input.server_name)
        self.response.payload[:] = invoker.invoke(GetServerDeliveryTaskList.get_name(), {
            'cluster_id': self.request.input.cluster_id,
        }, pid=self.request.input.server_pid)

# ################################################################################################################################
# ################################################################################################################################

class GetDeliveryTask(AdminService):
    """ Returns a particular delivery task by its Python object's ID.
    """
    class SimpleIO(GetTaskSIO):
        input_required = 'server_name', 'server_pid', AsIs('python_id')

    def handle(self):

        request = {
            'cluster_id': self.server.cluster_id,
            'server_name': self.request.input.server_name,
            'server_pid': self.request.input.server_pid,
        }

        invoker = self.server.rpc.get_invoker_by_server_name(self.request.input.server_name)
        response = invoker.invoke(GetDeliveryTaskList.get_name(), request)

        for item in response:
            if item['python_id'] == self.request.input.python_id:
                self.response.payload = item
                return

# ################################################################################################################################
# ################################################################################################################################
