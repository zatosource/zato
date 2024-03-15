'''
# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from operator import itemgetter

# Bunch
from bunch import Bunch

# Zato
from zato.common.util.time_ import datetime_from_ms
from zato.server.service import AsIs, Int
from zato.server.service.internal import AdminService, GetListAdminSIO
from zato.server.service.internal.pubsub.task.delivery import GetTaskSIO

# ################################################################################################################################

# Type checking
if 0:
    from zato.server.pubsub.delivery.task import DeliveryTask
    from zato.server.pubsub.delivery.tool import PubSubTool

    DeliveryTask = DeliveryTask
    Message = Message
    PubSubTool = PubSubTool

# ################################################################################################################################
# ################################################################################################################################

class _GetMessageSIO:
    output_required = (AsIs('msg_id'), 'published_by_id', Int('delivery_count'), 'recv_time')
    output_optional = (AsIs('ext_client_id'), 'data_prefix_short', 'published_by_name')
    response_elem = None

# ################################################################################################################################
# ################################################################################################################################

class GetServerDeliveryTaskMessageList(AdminService):
    """ Returns all in-flight messages tasks from a particular delivery task, which must exist on current server.
    """
    class SimpleIO(_GetMessageSIO):
        input_required = (AsIs('python_id'),)
        input_optional = (AsIs('msg_id'), 'needs_details')
        output_repeated = True

    def get_data(self):

        out = []
        msg_id = self.request.input.msg_id
        needs_details = self.request.input.needs_details

        # Get all pubsub tools ..
        for ps_tool in self.pubsub.pubsub_tools: # type: PubSubTool

            # Make sure nothing modifies any tool in the meantime
            with ps_tool.lock:

                # Get all tasks from current server ..
                for sub_key, task in ps_tool.delivery_tasks.items(): # type: (str, DeliveryTask)

                    # Find the one task required on input ..
                    if task.python_id == self.request.input.python_id:
                        for msg in task.delivery_list: # type: Message

                            # If only a single message is to be returned, check it here ..
                            if msg_id and msg_id != msg.msg_id:
                                continue

                            # A message to be produced
                            item = Bunch()
                            item.recv_time = datetime_from_ms(msg.recv_time * 1000)
                            item.msg_id = msg.pub_msg_id
                            item.published_by_id = msg.published_by_id
                            item.published_by_name = self.pubsub.get_endpoint_by_id(msg.published_by_id).name
                            item.ext_client_id = msg.ext_client_id
                            item.data_prefix_short = msg.data[:self.pubsub.data_prefix_short_len]
                            item.delivery_count = msg.delivery_count

                            # If details are needed, add them too ..
                            if needs_details:
                                pass

                            out.append(item)

        return out

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

        invoker = self.server.rpc.get_invoker_by_server_name(self.request.input.server_name)
        response = invoker.invoke(GetServerDeliveryTaskMessageList.get_name(), {
            'cluster_id': self.request.input.cluster_id,
            'python_id': self.request.input.python_id,
        }, pid=self.request.input.server_pid)

        self.response.payload[:] = response

# ################################################################################################################################
# ################################################################################################################################
'''
