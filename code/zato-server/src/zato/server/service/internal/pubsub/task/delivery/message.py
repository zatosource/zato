'''
# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from operator import itemgetter

# Zato
from zato.common.util.time_ import datetime_from_ms
from zato.server.service import AsIs, Int
from zato.server.service.internal import AdminService, GetListAdminSIO
from zato.server.service.internal.pubsub.task.delivery import GetTaskSIO

# ################################################################################################################################

# Type checking
if 0:
    from zato.server.pubsub.task import DeliveryTask, Message, PubSubTool

    DeliveryTask = DeliveryTask
    Message = Message
    PubSubTool = PubSubTool

# ################################################################################################################################
# ################################################################################################################################

class _GetMessageSIO(object):
    output_required = (AsIs('msg_id'),)
    response_elem = None

# ################################################################################################################################
# ################################################################################################################################

class GetDeliveryTask(AdminService):
    name = 'task2.get-delivery-task'

    class SimpleIO(GetTaskSIO):
        input_required = 'server_name', 'server_pid', AsIs('python_id')

    def handle(self):
        service_name = 'zato.pubsub.task.delivery.get-delivery-task-list'

        request = {
            'cluster_id': self.server.cluster_id,
            'server_name': self.request.input.server_name,
            'server_pid': self.request.input.server_pid,
        }

        response = self.servers[self.request.input.server_name].invoke(service_name, request)

        for item in response:
            if item['python_id'] == self.request.input.python_id:
                self.response.payload = item
                return

# ################################################################################################################################
# ################################################################################################################################

class GetServerDeliveryTaskMessageList(AdminService):
    """ Returns all in-flight messages tasks from a particular delivery task, which must exist on current server.
    """
    class SimpleIO(_GetMessageSIO):
        input_required = (AsIs('python_id'),)
        output_repeated = True

    def get_data(self):

        out = []

        self.logger.warn('EEE')


        for ps_tool in self.pubsub.pubsub_tools: # type: PubSubTool
            with ps_tool.lock:
                for sub_key, task in ps_tool.delivery_tasks.items(): # type: (str, DeliveryTask)

                    if task.python_id == self.request.input.python_id:

                        for msg in task.delivery_list: # type: Message
                            self.logger.warn('EEE %s', msg.asdict())

                    '''
                    last_sync = task.last_iter_run #ps_tool.last_gd_run
                    if last_sync:
                        last_sync = datetime_from_ms(last_sync * 1000)

                    endpoint_id = self.pubsub.get_subscription_by_sub_key(task.sub_key).endpoint_id
                    endpoint = self.pubsub.get_endpoint_by_id(endpoint_id)

                    out.append({
                        'server_name': ps_tool.server_name,
                        'server_pid': ps_tool.server_pid,
                        'endpoint_id': endpoint.id,
                        'endpoint_name': endpoint.name,
                        'py_object': task.py_object,
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
                    '''

        # Return the list of tasks sorted by sub_keys and their Python names
        return sorted(out, key=itemgetter('sub_key', 'py_object'))

    def handle(self):
        self.response.payload[:] = self.get_data()

# ################################################################################################################################
# ################################################################################################################################

class GetDeliveryTaskMessageList(AdminService):
    """ Returns all in-flight messages tasks from a particular delivery task.
    """
    name = 'pubsub.task.message.get-list2'

    class SimpleIO(GetListAdminSIO, _GetMessageSIO):
        input_optional = GetListAdminSIO.input_optional + (AsIs('python_id'),)
        input_required = 'cluster_id', 'server_name', 'server_pid'

    def handle(self):

        response = self.servers[self.request.input.server_name].invoke(GetServerDeliveryTaskMessageList.get_name(), {
            'cluster_id': self.request.input.cluster_id,
            'python_id': self.request.input.python_id,
        }, pid=self.request.input.server_pid)

        self.response.payload[:] = response

# ################################################################################################################################
# ################################################################################################################################
'''
